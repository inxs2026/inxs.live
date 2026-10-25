"""Read existing Woodbine handle datasets and saved standings without delivery side effects."""
import datetime as dt
import json
from pathlib import Path
import re
import subprocess
import threading
import math
from zoneinfo import ZoneInfo

HOME = Path.home()
RACING = HOME / '.openclaw/workspace/racing'
STANDINGS = HOME / '.hermes/profiles/trackdata-agent/cron/output'
PDF_CACHE = {}
LIVE_STANDINGS = Path('/tmp')
STANDINGS_LOCK = threading.Lock()
STANDINGS_CACHE = Path(__file__).resolve().parent / '.cache/standings'

def parse_live_standings(payload, kind):
    if payload.get('track') != 'WOODBINE' or payload.get('type') != kind or payload.get('year') != dt.datetime.now().year:
        raise ValueError('Standings track, type or year mismatch')
    rows = []
    names = set()
    for entry in payload.get('entries', []):
        name = str(entry.get('name') or '').strip()
        values = [str(entry.get(k, '')).replace(',', '').strip() for k in ('starts', 'first', 'second', 'third')]
        earnings = str(entry.get('earnings', '')).replace('$', '').replace(',', '').strip()
        if not name or name in names or not all(v.isdigit() for v in values) or not re.fullmatch(r'\d+(?:\.\d{1,2})?', earnings):
            raise ValueError('Incomplete standings row')
        starts, wins, second, third = map(int, values)
        if wins + second + third > starts:
            raise ValueError('Standings counts exceed starts')
        names.add(name)
        rows.append(dict(name=name, starts=starts, wins=wins, second=second, third=third,
                         earnings=float(earnings), winPct=100*wins/starts if starts else None,
                         itmPct=100*(wins+second+third)/starts if starts else None))
    if not rows:
        raise ValueError('No standings rows')
    return dict(rows=rows, dateRange=f"{payload['year']} Woodbine meet", coverageThrough=None,
                source='Scheduled Equibase Woodbine meet standings',
                sourceURL=f'https://www.equibase.com/stats/View.cfm?tf=meet&rbt=TB&tb={kind}',
                snapshot=True)

def attach_standings_pdf(data, kind):
    saved = dt.datetime.fromisoformat(data['savedAt'])
    day = saved.astimezone(ZoneInfo('America/Toronto')).strftime('%Y%m%d')
    paths = [LIVE_STANDINGS / f'standings_woodbine_weekend_{day}.pdf', LIVE_STANDINGS / f'standings_weekly_{day}.pdf']
    paths = sorted((p for p in paths if p.is_file() and p.stat().st_mtime >= saved.timestamp()), key=lambda p:p.stat().st_mtime, reverse=True)
    if paths and paths[0].read_bytes().startswith(b'%PDF-'):
        target = STANDINGS_CACHE / (kind + '.pdf')
        if not target.is_file() or paths[0].stat().st_mtime > target.stat().st_mtime:
            temporary = target.with_suffix('.pdf.tmp')
            temporary.write_bytes(paths[0].read_bytes())
            temporary.replace(target)
        data.update(document='/stats-document?report='+kind, documentLabel='Scheduled PDF (top 15)')
    return data


def live_standings(kind):
    with STANDINGS_LOCK:
        return _live_standings(kind)


def _live_standings(kind):
    cache = STANDINGS_CACHE / (kind + '.json')
    live = LIVE_STANDINGS / ('wo_' + kind + '.json')
    # Copy validated snapshots out of /tmp so they survive a reboot.
    old = json.loads(cache.read_text()) if cache.is_file() else None
    saved_ns = old.get('sourceMtimeNs', 0) if old else 0
    if live.is_file() and live.stat().st_mtime_ns > saved_ns:
        payload = json.loads(live.read_text())
        data = parse_live_standings(payload, kind)
        saved = dt.datetime.fromtimestamp(live.stat().st_mtime, dt.timezone.utc).isoformat()
        data.update(savedAt=saved, document=None, sourceMtimeNs=live.stat().st_mtime_ns)
        STANDINGS_CACHE.mkdir(parents=True, exist_ok=True)
        attach_standings_pdf(data, kind)
        temporary = cache.with_suffix('.tmp')
        temporary.write_text(json.dumps(data))
        temporary.replace(cache)
    if cache.is_file():
        data = json.loads(cache.read_text())
        if dt.datetime.fromisoformat(data['savedAt']).year != dt.datetime.now().year:
            raise ValueError('Cached standings belong to another year')
        before = json.dumps(data, sort_keys=True)
        attach_standings_pdf(data, kind)
        if json.dumps(data, sort_keys=True) != before:
            temporary = cache.with_suffix('.tmp')
            temporary.write_text(json.dumps(data))
            temporary.replace(cache)
        return data
    raise FileNotFoundError('Current standings snapshot is unavailable')

def valid_days(data):
    return [r for r in data['daily'] if r.get('status') != 'cancelled' and isinstance(r.get('handle_cad'), (int, float)) and r['handle_cad'] > 0]

def totals(rows):
    total = sum(r['handle_cad'] for r in rows)
    races = sum(r.get('races') or 0 for r in rows)
    return dict(handle=total, days=len(rows), races=races, average=total/len(rows) if rows else None)

def percent(current, prior):
    return (current/prior-1)*100 if prior else None

def handles():
    today=dt.datetime.now(ZoneInfo('America/Toronto')).date()
    year=today.year
    current_file=RACING/f'handles_{year}/handles.json'
    prior_file=RACING/f'handles_{year-1}/handles.json'
    def read_season(file,season):
        data=json.loads(file.read_text())
        if data.get('track')!='WO' or str(data.get('season'))!=str(season):raise ValueError('Handle dataset season or track mismatch')
        rows=[];seen=set()
        for row in data['daily']:
            date=dt.date.fromisoformat(row['date'])
            if date.year!=season or row['date'] in seen:raise ValueError('Invalid or duplicate handle date')
            seen.add(row['date'])
            if date>today or row.get('status')=='cancelled':continue
            value=row.get('handle_cad')
            if row.get('status') not in ('ok','verified_by_user','computed_per_race_html') or not isinstance(value,(int,float)) or isinstance(value,bool) or not math.isfinite(value) or value<=0:raise ValueError('A completed handle is unresolved')
            rows.append(row)
        return sorted(rows,key=lambda row:row['date'])
    # Never use the report export: a short-window PDF rebuild can overwrite it.
    b=read_season(current_file,year)
    a=read_season(prior_file,year-1)[:len(b)]
    if not b or len(a)!=len(b):raise ValueError('Comparison requires equal completed race-day counts')
    cutoff = max(r['date'] for r in b)
    current = totals(b)
    previous = totals(a)
    weekdays = []
    for number, label in [(3,'Thursday'),(4,'Friday'),(5,'Saturday'),(6,'Sunday')]:
        prior = totals([r for r in a if dt.date.fromisoformat(r['date']).weekday() == number])
        latest = totals([r for r in b if dt.date.fromisoformat(r['date']).weekday() == number])
        weekdays.append(dict(day=label, previous=prior, current=latest, averageChange=percent(latest['average'],prior['average']) if latest['average'] is not None else None))
    documents=[]
    if document_path('handle-daily').is_file():documents.append(dict(label=f'{year} daily handle PDF',key='handle-daily'))
    # Link an equal-day export only if its content matches the full live period.
    comparison_file=RACING/f'handles_{year-1}/comparison_{year-1}_vs_{year}.json'
    if comparison_file.is_file():
        try:
            saved=json.loads(comparison_file.read_text())
            if saved.get('year1_days')==a and saved.get('year2_days')==b and document_path('handle-yoy'):
                documents.insert(0,dict(label='Matching equal-race-days comparison PDF',key='handle-yoy'))
        except (ValueError,OSError):pass
    return dict(through=cutoff, priorThrough=max(r['date'] for r in a), current=current, previous=previous,currentYear=year,previousYear=year-1,
                change=percent(current['handle'],previous['handle']), weekdays=weekdays,
                source='Full daily handle datasets · matched completed race days',
                updatedAt=dt.datetime.fromtimestamp(current_file.stat().st_mtime,dt.timezone.utc).isoformat(),
                documents=documents)

def parse_standings(text):
    date_range = next((line.strip() for line in text.splitlines() if re.search(r'\w+ \d+\s*[–-]\s*\w+ \d+, \d{4}',line)), None)
    rows = []
    for line in text.splitlines():
        match = re.fullmatch(r'\s*(.+?)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+\$([\d,]+)\s*',line)
        if match:
            name, starts, wins, second, third, earnings = match.groups()
            starts, wins, second, third = map(int,(starts,wins,second,third))
            rows.append(dict(name=name,starts=starts,wins=wins,second=second,third=third,earnings=int(earnings.replace(',','')),
                             winPct=100*wins/starts if starts else None,itmPct=100*(wins+second+third)/starts if starts else None))
    if not rows or not date_range:
        raise ValueError('Saved standings format is unavailable')
    end = re.split(r'\s*[–-]\s*', date_range)[-1]
    through = dt.datetime.strptime(end, '%B %d, %Y').date().isoformat()
    return dict(dateRange=date_range, coverageThrough=through+'T12:00:00-04:00', rows=rows)

def standings(kind):
    try:
        return live_standings(kind)
    except (OSError, ValueError, KeyError, TypeError):
        cache = STANDINGS_CACHE / (kind + '.json')
        if cache.is_file():
            data = json.loads(cache.read_text())
            data['refreshError'] = 'Latest source could not be validated; showing the last saved snapshot.'
            return data
    # Legacy output is a clearly dated fallback, never labelled as current.
    file = STANDINGS/f'woodbine_{kind}_standings.pdf'
    stamp = file.stat().st_mtime_ns
    cached = PDF_CACHE.get(kind)
    if not cached or cached[0] != stamp:
        text = subprocess.run(['pdftotext','-layout',str(file),'-'],capture_output=True,text=True,timeout=10,check=True).stdout
        data = parse_standings(text)
        data.update(source='Saved Equibase Woodbine meet standings', savedAt=dt.datetime.fromtimestamp(file.stat().st_mtime,dt.timezone.utc).isoformat(),
                    document='/stats-document?report='+kind,
                    sourceURL=f'https://www.equibase.com/static/statistics/tracks/WO-CAN-{kind.title()}.html')
        PDF_CACHE[kind] = (stamp,data)
    return PDF_CACHE[kind][1]

def owners_document():
    files = sorted((HOME/'.openclaw/workspace').glob('WO_Owners_by_Year_2015-????.pdf'))
    return files[-1] if files else None

def parse_owners(text):
    rows = []
    for line in text.splitlines():
        match = re.fullmatch(r'\s*(20\d{2})\s*(?:¹)?\s+([\d,]+)\s+([\d,]+)\s+([\d,]+)\s+([\d,]+)\s+([\d,]+)\s+([\d,]+)\s*',line)
        if match:
            values = [int(v.replace(',','')) for v in match.groups()]
            rows.append(dict(zip(('year','owners','races','winners','twoPlus','fivePlus','tenPlus'),values)))
    coverage = re.search(r'(20\d{2}) partial\s*[—–-]\s*through ([A-Za-z]+ \d+)',text)
    generated = re.search(r'Generated (\d{4}-\d{2}-\d{2})',text)
    if not rows or not coverage or not generated:
        raise ValueError('Owner report format is unavailable')
    return dict(rows=rows,partialYear=int(coverage[1]),through=coverage[2],generated=generated[1])

def owners():
    file = owners_document()
    if file is None:
        raise ValueError('No owner report available')
    stamp = (str(file),file.stat().st_mtime_ns)
    cached = PDF_CACHE.get('owners')
    if not cached or cached[0] != stamp:
        text = subprocess.run(['pdftotext','-layout',str(file),'-'],capture_output=True,text=True,timeout=10,check=True).stdout
        data = parse_owners(text)
        data.update(document='/stats-document?report=owners',source='Equibase Leaders by Track · Owner Standings')
        PDF_CACHE['owners'] = (stamp,data)
    return PDF_CACHE['owners'][1]

def build():
    data = {}
    for key, reader in [('handle',handles),('owners',owners),('jockey',lambda:standings('jockey')),('trainer',lambda:standings('trainer'))]:
        try:
            data[key] = reader()
        except (OSError, ValueError, KeyError, subprocess.SubprocessError):
            data[key] = dict(error='Saved statistics are temporarily unavailable.')
    return data

def document_path(key):
    if key == 'owners':
        return owners_document()
    if key in ('jockey','trainer'):
        cache = STANDINGS_CACHE / (key + '.json')
        if cache.is_file():
            data = live_standings(key)
            if data.get('document'):
                return STANDINGS_CACHE / (key + '.pdf')
            return None
        return STANDINGS/f'woodbine_{key}_standings.pdf'
    if key == 'handle-daily':
        year=dt.datetime.now(ZoneInfo('America/Toronto')).year
        return RACING/f'handles_{year}/Woodbine_{year}_Daily_Handle.pdf'
    if key == 'handle-yoy':
        year=dt.datetime.now(ZoneInfo('America/Toronto')).year
        files = sorted((RACING/f'handles_{year-1}').glob(f'Woodbine_{year-1}_vs_{year}_{year}YTD_????-??-??.pdf'))
        return files[-1] if files else None
    raise ValueError('Invalid report')
