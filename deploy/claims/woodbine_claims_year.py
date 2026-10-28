#!/usr/bin/env python3
"""Daily claims above a complete current-year claims history. No publishing.

python woodbine_claims_year.py --through 2026-10-28 --output-dir reports
"""
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor, as_completed
from datetime import date, datetime, timezone
from decimal import Decimal
import argparse
import hashlib
import json
from pathlib import Path
import re
import sys
import urllib.request
from zoneinfo import ZoneInfo

from woodbine_claims import (CardError, PARSER_VERSION, claim_lines, html_report,
                            download_chart, markdown, parse_card)

RESULTS_CALENDAR = 'https://tvg.equibase.com/static/chart/pdf/WO-calendar.html'


def write_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix('.tmp')
    temp.write_text(json.dumps(data, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    temp.replace(path)


def load_calendar(path, year, through, offline=False):
    calendar = json.loads(path.read_text(encoding='utf-8'))
    if calendar.get('year') != year or calendar.get('track') != 'WO':
        raise CardError('Calendar track/year mismatch')
    dates = {date.fromisoformat(d) for d in calendar['dates']}
    if not dates or any(d.year != year for d in dates):
        raise CardError('Invalid calendar dates')
    if date.fromisoformat(calendar['coverage_end']) < through:
        raise CardError('Calendar does not cover the requested through date')
    result = dict(calendar)
    result['live_calendar_checked_at'] = None
    if not offline:
        request = urllib.request.Request(RESULTS_CALENDAR, headers={'User-Agent': 'WoodbineClaims/1.0'})
        with urllib.request.urlopen(request, timeout=45) as response:
            text = response.read(3_000_000).decode('utf-8')
        # Accept only full-card chart links for this track and year. Recent
        # make-up dates are discovered even if absent from the original schedule.
        for value in re.findall(r'WO(\d{6})CAN\.pdf', text):
            linked = datetime.strptime(value, '%m%d%y').date()
            if linked.year == year:
                dates.add(linked)
        if 'Woodbine Calendar' not in text:
            raise CardError('Official results calendar could not be verified')
        result['live_calendar_checked_at'] = datetime.now(timezone.utc).isoformat()
    result['dates'] = sorted(d.isoformat() for d in dates if d <= through)
    return result


def fetch_day(day, cache, refresh, offline):
    target = date.fromisoformat(day)
    path = cache / f'{day}.pdf'
    if offline:
        if not path.is_file() or not path.read_bytes().startswith(b'%PDF-'):
            raise CardError(f'Missing cached PDF: {day}')
    elif refresh or not path.is_file():
        temp = path.with_suffix('.download.pdf')
        download_chart(target, temp)
        temp.replace(path)
    return day


def parse_day(day, cache, expected_races):
    path = cache / f'{day}.pdf'
    result_path = cache / 'reports' / f'{day}.json'
    fingerprint = hashlib.sha256(path.read_bytes()).hexdigest()
    if result_path.is_file():
        saved = json.loads(result_path.read_text(encoding='utf-8'))
        if saved.get('source_sha256') == fingerprint and saved.get('parser_version') == PARSER_VERSION:
            if expected_races is None or len(saved.get('races_checked', [])) == expected_races:
                return saved
    result = parse_card(path, date.fromisoformat(day), expected_races)
    result['source'] = f"https://tvg.equibase.com/static/chart/pdf/WO{target_code(day)}CAN.pdf"
    result['checked_at'] = datetime.now(timezone.utc).isoformat()
    write_json(result_path, result)
    return result


def target_code(day):
    return date.fromisoformat(day).strftime('%m%d%y')


def aggregate(reports, expected_dates, through, year, errors):
    by_date = {r['date']: r for r in reports}
    if len(by_date) != len(reports):
        raise CardError('Duplicate daily reports')
    missing = sorted(set(expected_dates) - by_date.keys())
    claims = []
    for day in sorted(by_date, reverse=True):
        report = by_date[day]
        for c in sorted(report['claims'], key=lambda c: (c['race'], int(re.match(r'\d+', c['program_number']).group()))):
            claims.append(dict(c, date=day, source=report['source']))
    identities = [(c['date'], c['race'], c['program_number']) for c in claims]
    if len(identities) != len(set(identities)):
        raise CardError('Duplicate claims in annual report')
    completed = sorted(day for day, r in by_date.items() if r['status'] != 'cancelled')
    cancelled = sorted(day for day, r in by_date.items() if r['status'] == 'cancelled')
    if not completed:
        raise CardError('No completed cards verified')
    total = sum((Decimal(c['claim_price_cad']) for c in claims), Decimal(0))
    latest = completed[-1]
    return dict(track='Woodbine', year=year, requested_through=through.isoformat(),
                coverage_through=latest, coverage_start=completed[0],
                complete=not missing and not errors,
                checked_at=datetime.now(timezone.utc).isoformat(),
                completed_cards=len(completed), completed_races=sum(len(by_date[d]['completed_races']) for d in completed),
                cancelled_cards=cancelled, days_with_claims=sum(bool(by_date[d]['claims']) for d in completed),
                no_claims_dates=[d for d in completed if not by_date[d]['claims']],
                missing_dates=missing, errors=errors, total_claims=len(claims),
                total_claim_value_cad=f'{total:.2f}', claims=claims,
                daily=by_date[latest],
                cards=[{k: r[k] for k in ('date', 'status', 'races_checked', 'completed_races',
                                        'cancelled_races', 'source', 'source_sha256')}
                       for d, r in sorted(by_date.items())])


def combined_markdown(report):
    daily = markdown(report['daily']).splitlines()
    # Keep the accepted compact daily section first.
    daily[0] = f"# Woodbine Claims - Latest Completed Card: {report['daily']['date']}"
    lines = daily + ['', f"## All {report['year']} Claims", '',
        f"**{report['total_claims']} claims | C${Decimal(report['total_claim_value_cad']):,.0f} total**  ",
        f"{report['completed_cards']} completed cards checked, {report['coverage_start']} through {report['coverage_through']}.  ",
        'Newest date first; race numbers in order. All amounts CAD.', '']
    if not report['complete']:
        lines += ['**INCOMPLETE COVERAGE - this is not a complete year-to-date list.**',
                  'Unverified dates: ' + ', '.join(report['missing_dates']), '']
    previous = None
    for c in report['claims']:
        if c['date'] != previous:
            lines += [f"### {c['date']}", '']
            previous = c['date']
        lines += claim_lines(c)
    lines += ['Cancelled cards verified separately: ' + ', '.join(report['cancelled_cards']), '',
              'All source URLs and PDF hashes are retained in the accompanying JSON.', '']
    return '\n'.join(lines)


def main():
    today = datetime.now(ZoneInfo('America/Toronto')).date()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--year', type=int, default=today.year)
    parser.add_argument('--through', type=date.fromisoformat, default=today)
    parser.add_argument('--calendar', type=Path)
    parser.add_argument('--cache-dir', type=Path, default=Path('claims-cache'))
    parser.add_argument('--output-dir', type=Path, default=Path('reports'))
    parser.add_argument('--offline', action='store_true', help='Rebuild from saved PDFs without network access')
    parser.add_argument('--refresh-all', action='store_true', help='Refetch every chart to check historical corrections')
    args = parser.parse_args()
    try:
        if args.through.year != args.year or args.through > today:
            raise CardError('Through date must be in the requested year and cannot be in the future')
        path = args.calendar or Path(__file__).with_name(f'woodbine-{args.year}-calendar.json')
        calendar = load_calendar(path, args.year, args.through, args.offline)
        dates = calendar['dates']
        if not dates:
            raise CardError('No race dates are covered by this calendar yet')
        cache = args.cache_dir / str(args.year)
        cache.mkdir(parents=True, exist_ok=True)
        refresh = set(dates[-3:])  # Recheck recent results while reusing immutable historical PDFs.
        errors = []
        fetched = []
        with ThreadPoolExecutor(max_workers=4) as pool:
            tasks = {pool.submit(fetch_day, d, cache, args.refresh_all or d in refresh, args.offline): d for d in dates}
            for done, task in enumerate(as_completed(tasks), 1):
                try:
                    fetched.append(task.result())
                except Exception as error:
                    errors.append(dict(date=tasks[task], error=str(error)))
                if done % 10 == 0 or done == len(tasks):
                    print(f'Checked chart files: {done}/{len(tasks)}', flush=True)
        reports = []
        with ProcessPoolExecutor(max_workers=4) as pool:
            tasks = {pool.submit(parse_day, d, cache, calendar.get('race_counts', {}).get(d)): d for d in fetched}
            for done, task in enumerate(as_completed(tasks), 1):
                try:
                    reports.append(task.result())
                except Exception as error:
                    errors.append(dict(date=tasks[task], error=str(error)))
                if done % 10 == 0 or done == len(tasks):
                    print(f'Verified cards: {done}/{len(tasks)}', flush=True)
        annual = aggregate(reports, dates, args.through, args.year, errors)
        annual['calendar'] = calendar
        stem = args.output_dir / f'woodbine-claims-{args.year}-year-to-date'
        # Keep an incomplete run separate so it cannot replace the last complete report.
        if not annual['complete']:
            stem = stem.with_name(stem.name + '-INCOMPLETE')
        write_json(stem.with_suffix('.json'), annual)
        stem.with_suffix('.md').write_text(combined_markdown(annual), encoding='utf-8')
        stem.with_suffix('.html').write_text(html_report(annual), encoding='utf-8')
        print(f"{annual['total_claims']} claims, C${Decimal(annual['total_claim_value_cad']):,.0f}; "
              f"coverage through {annual['coverage_through']}; complete={annual['complete']}")
        if errors:
            for error in errors:
                print(error, file=sys.stderr)
            return 2
        return 0
    except (CardError, OSError, ValueError) as error:
        print(f'Annual claims could not be verified: {error}', file=sys.stderr)
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
