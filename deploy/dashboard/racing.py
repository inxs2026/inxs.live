"""Read saved Woodbine selections and enrich them with dated TrackData updates."""
import concurrent.futures
from datetime import date, datetime, timezone
import json
import agco
import race_results
import race_schedule
from pathlib import Path
import re
import threading
import time
import urllib.parse
import urllib.request
from zoneinfo import ZoneInfo

HOME = Path.home()
HERMES = HOME / '.hermes/cache/wo-picks'
OPENCLAW = HOME / '.openclaw/workspace/racing'
CACHE = Path(__file__).resolve().parent / '.cache/racing'
API = 'https://api.trackdata.live/api'
LOCK = threading.Lock()
SNAPSHOTS = {}
BUSY = set()

def today():
    return datetime.now(ZoneInfo('America/Toronto')).date().isoformat()

def valid_date(value):
    if not isinstance(value, str) or not re.fullmatch(r'\d{4}-\d{2}-\d{2}', value):
        raise ValueError('Use a date in YYYY-MM-DD format')
    date.fromisoformat(value)
    return value

def available_dates():
    dates = {today()}
    for p in HERMES.glob('????-??-??/artifacts/picks-payload.json'):
        try:
            dates.add(valid_date(p.parent.parent.name))
        except ValueError:
            pass
    for p in OPENCLAW.glob('WO--??-??-????_smartpick.json'):
        try:
            dates.add(datetime.strptime(p.name[4:14], '%m-%d-%Y').date().isoformat())
        except ValueError:
            pass
    return sorted(dates, reverse=True)[:100]

def stamp(path):
    return datetime.fromtimestamp(path.stat().st_mtime, timezone.utc).isoformat()

def read_json(path):
    return json.loads(path.read_text())

def name_key(name):
    # Exact normalized name match only; country suffixes are not part of the horse name.
    return re.sub(r'[^a-z0-9]', '', re.sub(r'\s*\([^)]*\)\s*$', '', str(name)).lower())

def json_get(url):
    req = urllib.request.Request(url, headers={'User-Agent': 'LocalDashboard/1.0'})
    with urllib.request.urlopen(req, timeout=12) as response:
        return json.loads(response.read(2_000_000))

def get_updates(kind, target):
    formatted = date.fromisoformat(target).strftime('%m-%d-%Y')
    items = []
    page = 1
    while True:
        query = urllib.parse.urlencode(dict(view='all', track='WO', start_date=formatted, end_date=formatted, limit=100, page=page))
        result = json_get(API + '/' + kind + '?' + query)
        if not isinstance(result.get(kind), list) or result.get('meta', {}).get('fallback_applied'):
            raise ValueError('Unexpected source response')
        for row in result[kind]:
            if row.get('race_date') != target or row.get('track_code') != 'WO':
                raise ValueError('Source returned another race card')
            items.append(dict(race=row.get('race_number'), pp=str(row.get('program_number') or ''), name=row.get('horse_name') or '',
                              reason=row.get('description') or row.get('reason') or row.get('scratch_reason') or row.get('change_type') or 'Reported update',
                              type=row.get('change_type') or ('Scratch' if kind == 'scratches' else 'Change'),
                              updatedAt=row.get('change_time') or row.get('updated_at')))
        total = int(result.get('total_pages', 1))
        if page >= total:
            break
        if page >= 100:
            raise ValueError('Source pagination exceeded expected limit')
        page += 1
    return dict(items=items, checkedAt=datetime.now(timezone.utc).isoformat(), error=None)

def refresh(target, race_numbers):
    try:
        with LOCK:
            previous = SNAPSHOTS.get(target, {})
        snapshot = dict(previous)
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as pool:
            futures = {pool.submit(get_updates, kind, target): kind for kind in ('scratches', 'changes')}
            for future, kind in futures.items():
                try:
                    snapshot[kind] = future.result()
                except Exception:
                    snapshot[kind] = dict(previous.get(kind, dict(items=None, checkedAt=None)), error='TrackData is temporarily unavailable')
            details = dict(previous.get('details', {}))
            def detail(number):
                data = json_get(API + '/race-details/WO-' + target.replace('-', '') + '-' + str(number))
                race = data.get('race') or {}
                if race.get('race_date') != target or race.get('track_code') != 'WO':
                    raise ValueError('Race detail date/track mismatch')
                return dict(entries=[dict(name=e.get('horse_name', ''), pp=str(e.get('program_number') or ''), scratched=bool(e.get('scratched')))
                                     for e in data.get('entries', [])], postTime=race.get('post_time'), result=race_results.normalize(data, target, number), checkedAt=datetime.now(timezone.utc).isoformat())
            results = {pool.submit(detail, num): num for num in race_numbers}
            errors = []
            for future, num in results.items():
                try:
                    details[str(num)] = future.result()
                except Exception:
                    errors.append(num)
            snapshot['details'] = details
            snapshot['detailErrors'] = errors
        snapshot['attemptedAt'] = time.time()
        CACHE.mkdir(parents=True, exist_ok=True)
        p = CACHE / (target + '.json')
        temp = p.with_suffix('.tmp')
        temp.write_text(json.dumps(snapshot))
        temp.replace(p)
        with LOCK:
            SNAPSHOTS[target] = snapshot
    finally:
        with LOCK:
            BUSY.discard(target)

def enrichment(target, race_numbers, allow_refresh=True):
    with LOCK:
        if target not in SNAPSHOTS:
            try:
                SNAPSHOTS[target] = read_json(CACHE / (target + '.json'))
            except Exception:
                SNAPSHOTS[target] = {}
        snapshot = SNAPSHOTS[target]
        ttl = 300 if target == today() else 1800
        if allow_refresh and (time.time() - snapshot.get('attemptedAt', 0) > ttl or any(d.get('result', {}).get('payoutVersion') != 2 for d in snapshot.get('details', {}).values())) and target not in BUSY:
            BUSY.add(target)
            threading.Thread(target=refresh, args=(target, race_numbers), daemon=True).start()
        return dict(snapshot), target in BUSY

def document_path(agent, target):
    valid_date(target)
    if agent == 'hermes':
        path = Path('/tmp') / ('WO_' + target.replace('-', '') + '_Picks.pdf')
    elif agent == 'openclaw':
        path = OPENCLAW / ('WO--' + date.fromisoformat(target).strftime('%m-%d-%Y') + '_smartpick.pdf')
    else:
        raise ValueError('Unknown agent')
    return path if path.is_file() else None

def snapshot_scratches(payload):
    rows = []
    for number, race in payload.items():
        for s in race.get('scratches', []):
            rows.append(dict(race=int(number), pp=str(s.get('pp') or ''), name=s.get('name', ''), reason=s.get('reason') or 'Scratch', type='Scratch', updatedAt=None))
    return rows

def openclaw_rankings(race, mapping):
    horses = []
    for h in race.get('horses', []):
        pp = mapping.get(name_key(h.get('name')), '')
        # Never infer program numbers from array position.
        horses.append(dict(name=h.get('name') or 'Unknown horse', pp=str(pp), avg=h.get('avg3'), figures=h.get('e_values', [])[:3], note='', ppVerified=bool(pp)))
    horses.sort(key=lambda h: (not isinstance(h['avg'], (int, float)), -h['avg'] if isinstance(h['avg'], (int, float)) else 0))
    for i, h in enumerate(horses, 1):
        h['rank'] = i
    return horses

REVIEW_LABELS = {
    'no_beyer_markers_preserved': 'No-Beyer markers in the card',
    'missing_or_empty_beyer_data': 'Some runners have no usable Beyer data',
    'low_populated_beyer_coverage': 'Limited Beyer history in this race',
    'hybrid_parser_works_context_for_missing_vision_data': 'Workout context recorded for runners without Beyers',
    'fixed_beyer_column_low_active_coverage': 'Limited coverage from the DRF parser',
    'hybrid_parser_vision_disagreement': 'Recorded parser cross-check disagreement',
    'fixed_beyer_column_untrusted': 'DRF figure extraction needs review',
}

def build(target=None, offline=False):
    target = valid_date(target or today())
    dates = available_dates()
    if target not in dates:
        raise ValueError('No saved race card for this date')
    hpath = HERMES / target / 'artifacts/picks-payload.json'
    opath = OPENCLAW / ('WO--' + date.fromisoformat(target).strftime('%m-%d-%Y') + '_smartpick.json')
    errors = []
    hp, op, state, audits, reviews = {}, {}, {}, [], []
    for name, path in [('Hermes', hpath), ('OpenClaw', opath)]:
        try:
            value = read_json(path)
            if name == 'Hermes':
                if not isinstance(value, dict) or not all(str(k).isdigit() and isinstance(v, dict) for k, v in value.items()):
                    raise ValueError('Invalid Hermes payload')
                hp = value
            else:
                if value.get('date') != target or value.get('track') != 'WO':
                    raise ValueError('Invalid OpenClaw card date')
                op = value
        except FileNotFoundError:
            pass
        except Exception:
            errors.append(name + ' saved picks could not be read')
    for name, filename in [('state', HERMES / target / 'state.json'), ('audit', hpath.parent / 'race-audit-summary.json'), ('review', hpath.parent / 'manual-review.json')]:
        try:
            d = read_json(filename)
            if name == 'state': state = d
            elif name == 'audit': audits = d
            elif name == 'review': reviews = d.get('items', [])
        except Exception:
            pass
    oraces = {str(r['race']): r for r in op.get('races', [])}
    numbers = sorted({int(n) for n in hp} | {int(n) for n in oraces})
    schedule = race_schedule.build(target, bool(numbers))
    snapshot, refreshing = ({}, False) if schedule['scheduled'] is False else (enrichment(target, numbers, allow_refresh=False) if offline else enrichment(target, numbers))
    scratch_feed = snapshot.get('scratches', {})
    live_scratches = scratch_feed.get('items')
    scratches = live_scratches if live_scratches is not None else snapshot_scratches(hp)
    scratch_source = 'TrackData' if live_scratches is not None else 'Hermes generation snapshot' if hp else 'Unavailable'
    scratch_time = scratch_feed.get('checkedAt') if live_scratches is not None else stamp(hpath) if hpath.exists() else None
    changes_feed = snapshot.get('changes', {})
    changes = changes_feed.get('items')
    if changes is None:
        changes = [dict(race=int(n), pp='', name=c.get('horse', ''), reason=c.get('change', ''), type='Change', updatedAt=None)
                   for n, r in hp.items() for c in r.get('changes', []) if not str(c.get('change', '')).lower().startswith('scratch')]
    else:
        changes = [c for c in changes if c.get('type', '').lower() != 'scratch']
    cards = []
    for number in numbers:
        key = str(number)
        hr, other = hp.get(key, {}), oraces.get(key, {})
        mapping = {}
        cached_details = {}
        try:
            cached_details = read_json(hpath.parent / 'race-details' / f'race-{number:02d}.json')
            mapping.update({name_key(e.get('horse_name')): str(e.get('program_number') or '') for e in cached_details.get('entries', [])})
        except Exception:
            pass
        for h in state.get('race_results', {}).get(key, {}).get('horses', {}).values():
            mapping.setdefault(name_key(h.get('name')), str(h.get('pp') or ''))
        live_detail = snapshot.get('details', {}).get(key, {})
        for e in live_detail.get('entries', []):
            mapping[name_key(e.get('name'))] = str(e.get('pp') or '')
        hs = [dict(rank=i, name=p.get('name') or 'Unknown horse', pp=str(p.get('pp') or ''), avg=p.get('avg'),
                   figures=p.get('last3') or [], note=p.get('note') or '', ppVerified=bool(p.get('pp'))) for i, p in enumerate(hr.get('picks', []), 1)]
        os = openclaw_rankings(other, mapping)
        rs = [s for s in scratches if str(s.get('race')) == key]
        for h in hs + os:
            h['scratched'] = any((h['pp'] and h['pp'] == str(s.get('pp'))) or name_key(h['name']) == name_key(s.get('name')) for s in rs)
            if not h['scratched']:
                h['scratched'] = any(e.get('scratched') and name_key(h['name']) == name_key(e.get('name')) for e in live_detail.get('entries', []))
        official_pp = str(other.get('equibase_pick_pp') or '')
        official = next((h for h in os if h['pp'] == official_pp), None) if official_pp else None
        audit = next((a for a in audits if str(a.get('race_number')) == key), {})
        race_reviews = [dict(title=REVIEW_LABELS.get(r.get('reason'), str(r.get('reason', 'Review note')).replace('_', ' ').capitalize()),
                             reason=r.get('reason'), horses=[h.get('name') if isinstance(h, dict) else str(h) for h in r.get('horses', [])],
                             missing=bool(r.get('reason') in ('missing_or_empty_beyer_data', 'low_populated_beyer_coverage')))
                        for r in reviews if str(r.get('race_number')) == key]
        result = dict(live_detail.get('result') or dict(complete=False, entries=[], status='unavailable', chart=None))
        result['checkedAt'] = live_detail.get('checkedAt')
        result['cached'] = number in snapshot.get('detailErrors', [])
        for h in hs + os:
            finish = race_results.match(h, result['entries'], name_key) if result['complete'] else None
            h['finish'] = finish['finish'] if finish and not finish['scratched'] else None
        cards.append(dict(result=result, number=number, conditions=hr.get('cond') or other.get('race_type') or cached_details.get('race', {}).get('race_type') or '',
                          distance=hr.get('dist') or cached_details.get('race', {}).get('distance') or '', surface=hr.get('surface') or '',
                          postTime=live_detail.get('postTime') or cached_details.get('race', {}).get('post_time'),
                          hermes=hs, openclaw=os, official=dict(pp=official_pp, name=official['name'] if official else None, scratched=official['scratched'] if official else False) if official_pp else None,
                          equibaseURL=other.get('url'), scratches=rs, reviews=race_reviews,
                          audit=dict(source=audit.get('beyer_source'), runnersWithFigures=audit.get('fixed_column_active_horses_with_beyers'), runners=audit.get('active_entries'), untrusted=bool(audit.get('fixed_column_untrusted')))))
    sources = []
    for agent, path, present, label, method in [
        ('Hermes', hpath, bool(hp), 'DRF Beyer top-three', 'Saved ranking by the average of the latest three DRF Beyer slots. Missing, zero and -0 figures are excluded from the average. Numeric ties use the lower program number. Scratches known at generation are excluded. Recorded parser provenance and data-quality notes are shown per race when available.'),
        ('OpenClaw', opath, bool(op), 'Equibase E-speed rankings', 'Saved Equibase E-speed figures, ranked by their latest-three average, excluding 999 placeholder values. This is the sorting rule used by the OpenClaw report, not an AI prediction. Equibase’s own SmartPick is a separate informational selection and does not change the E-speed order.')]:
        doc = document_path(agent.lower(), target)
        sources.append(dict(agent=agent, label=label, method=method, available=present, savedAt=stamp(path) if present else None,
                            file=path.name if present else None, document='/racing-document?agent=' + agent.lower() + '&date=' + target if doc else None))
    return dict(comparison=race_results.comparison(cards, target, {s['agent'].lower():s['savedAt'] for s in sources}, name_key), date=target, today=today(), dates=dates, schedule=schedule, races=cards, sources=sources, errors=errors, refreshing=refreshing, agco=None if offline else agco.build(target),
                scratches=dict(items=scratches, source=scratch_source, checkedAt=scratch_time, error=scratch_feed.get('error'),
                               historical=target != today(), snapshot=live_scratches is None, available=live_scratches is not None or bool(hp)),
                changes=dict(items=changes, source='TrackData' if changes_feed.get('items') is not None else 'Hermes generation snapshot', checkedAt=changes_feed.get('checkedAt'), error=changes_feed.get('error')),
                updatedAt=datetime.now(timezone.utc).isoformat())
