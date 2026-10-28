#!/usr/bin/env python3
"""Extract a dated Woodbine claims report from Equibase's full-card chart PDF.

Requires pdfplumber. Downloads only public results; does not post or schedule.
Usage: python woodbine_claims.py --date 2026-10-25 --output-dir reports
Offline: add --pdf WO102526CAN.pdf
"""
from __future__ import annotations

import argparse
from datetime import date, datetime, timezone
from decimal import Decimal
import hashlib
from html import escape
import json
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import urllib.request

import pdfplumber

NO_CLAIMS = "No Claims on Todays Card"
PARSER_VERSION = 3
HEADER = re.compile(
    r"^W\s*O\s*O\s*D\s*B\s*I\s*N\s*E\s*-\s*"
    r"([A-Za-z]+\s+\d{1,2},\s+\d{4})\s*-\s*Race\s+(\d+)\s*$", re.M)


class CardError(ValueError):
    """Unavailable or unverified results must never become a no-claims report."""


def compact(value):
    return re.sub(r"\s+", " ", value).strip()


def horse_key(value):
    value = re.sub(r"\s*\([A-Za-z]{2,3}\)\s*$", "", value)
    return re.sub(r"[^a-z0-9]", "", value.lower())


def section(text, start, end):
    match = re.search(start + r"(.*?)" + end, text, re.S)
    if not match:
        raise CardError(f"Missing chart section: {start}")
    return match.group(1)


def connections(text, label, end):
    block = section(text, rf"\b{label}:\s*", end)
    found = {}
    for token in block.split(";"):
        token = compact(token)
        if not token:
            continue
        match = re.fullmatch(r"(\d+[A-Za-z]?)\s*-\s*(.+)", token)
        if not match:
            raise CardError(f"Unrecognized {label} entry: {token}")
        program, name = match.groups()
        if program in found:
            raise CardError(f"Duplicate program number in {label}: {program}")
        found[program] = name
    return found


def finish_positions(page):
    """Read the actual Fin column, excluding superscript beaten lengths.

    Reading row order or '11' as a finishing position confuses winners and
    beaten lengths, and can misreport double-digit finishes or dead heats.
    """
    words = page.extract_words(x_tolerance=1, y_tolerance=3)
    fin = next((w for w in words if w['text'] == 'Fin'), None)
    if fin is None:
        raise CardError("Official finish column not found")
    headers = [w for w in words if abs(w['top'] - fin['top']) < 1]
    pgm = next(w for w in headers if w['text'] == 'Pgm')
    horse = next(w for w in headers if w['text'] == 'Horse')
    odds = next(w for w in headers if w['text'] == 'Odds')
    stop = next(w['top'] for w in words
                if w['text'] == 'Fractional' and w['top'] > fin['bottom'])
    chars = [c for c in page.chars if fin['bottom'] < c['top'] < stop]
    pgm_chars = [c for c in chars if pgm['x0'] - 1 <= c['x0'] < horse['x0'] - 2
                 and not c['text'].isspace()]
    rows = {}
    for c in pgm_chars:
        rows.setdefault(round(c['top'], 1), []).append(c)
    result = {}
    for y, row in rows.items():
        program = ''.join(c['text'] for c in sorted(row, key=lambda c: c['x0']))
        if not re.fullmatch(r'\d+[A-Za-z]?', program):
            raise CardError(f"Unrecognized starter program: {program}")
        font_size = max(c['size'] for c in row)
        cell = [c for c in chars if fin['x0'] - 1 <= c['x0'] < odds['x0'] - 2
                and abs(c['top'] - y) < 0.7 and abs(c['size'] - font_size) < 0.2]
        value = compact(''.join(c['text'] for c in sorted(cell, key=lambda c: c['x0'])))
        if not value:
            raise CardError(f"Missing official finish for program {program}")
        result[program] = int(value) if value.isdigit() else value
    if not result:
        raise CardError("No official finishing positions found")
    return result


def claimed_connections(page, count):
    """Read the two PDF columns separately so wrapped trainer names stay put."""
    words = page.extract_words(x_tolerance=1, y_tolerance=3)
    labels = []
    for i, word in enumerate(words):
        if word['text'] == 'Trainer:' and i and words[i-1]['text'] == 'New':
            start = words[i-1]
            owner = next((words[j-1] for j in range(i+1, len(words))
                          if words[j]['text'] == 'Owner:' and words[j-1]['text'] == 'New'
                          and abs(words[j]['top'] - word['top']) < 1), None)
            if owner is None:
                raise CardError('New-owner column not found')
            labels.append((start, owner))
    if len(labels) != count:
        raise CardError('Claim connections column count mismatch')
    result = []
    for i, (trainer, owner) in enumerate(labels):
        boundaries = [words[j]['top'] for j in range(len(words)-1)
                      if words[j]['top'] > trainer['top'] + 1
                      and (words[j]['text'], words[j+1]['text']) in
                      {('Voided', 'Claims:'), ('Claiming', 'Prices:'), ('Scratched', 'Horse(s):'), ('Total', 'WPS')}]
        if i+1 < len(labels):
            boundaries.append(labels[i+1][0]['top'])
        if not boundaries:
            raise CardError('Claims section ending not found')
        top, bottom = trainer['top'] - 0.5, min(boundaries) - 0.5
        trainer_text = page.crop((trainer['x0']-0.5, top, owner['x0']-1, bottom)).extract_text(x_tolerance=1) or ''
        owner_text = page.crop((owner['x0']-0.5, top, page.width, bottom)).extract_text(x_tolerance=1) or ''
        trainer_text = compact(re.sub(r'^New\s+Trainer:\s*', '', trainer_text))
        owner_text = compact(re.sub(r'^New\s+Owner:\s*', '', owner_text))
        if not trainer_text or not owner_text:
            raise CardError('Incomplete claimed connections')
        result.append((trainer_text, owner_text))
    return result


def parse_race(text, page, number):
    for required in ('Final Time:', 'Trainers:', 'Owners:', 'Footnotes', 'Copyright'):
        if required not in text:
            raise CardError(f"Race {number}: incomplete results ({required} missing)")
    marker = re.search(r'(\d+)\s+Claimed Horse\(s\):\s*', text)
    if not marker:
        if re.search(r'Claimed\s*Horse', text, re.I):
            raise CardError(f"Race {number}: unrecognized claims section")
        return []
    count = int(marker.group(1))
    block = section(text[marker.start():], r'\d+\s+Claimed Horse\(s\):\s*',
                    r'\n(?:Voided Claims:|Claiming Prices:|Scratched Horse\(s\):|Total WPS Pool:)')
    records = list(re.finditer(
        r'(.*?)\s+New Trainer:\s*(.*?)\s+New Owner:\s*(.*?)'
        r'(?=\n[^\n]+?\s+New Trainer:|\Z)', block, re.S))
    if len(records) != count:
        raise CardError(f"Race {number}: claims count mismatch ({count} vs {len(records)})")
    prices = section(text, r'\bClaiming Prices:\s*',
                     r'\n(?:Scratched Horse\(s\):|Total WPS Pool:)')
    price_map = {}
    for program, name, amount in re.findall(
            r'(\d+[A-Za-z]?)\s*-\s*(.*?)\s*:\s*\$([\d,]+(?:\.\d{2})?)\s*(?:;|$)',
            compact(prices)):
        key = horse_key(name)
        if key in price_map:
            raise CardError(f"Race {number}: ambiguous horse name: {name}")
        price_map[key] = (program, compact(name), Decimal(amount.replace(',', '')))
    old_trainers = connections(text, 'Trainers', r'\nOwners:')
    old_owners = connections(text, 'Owners', r'\nFootnotes')
    finishes = finish_positions(page)
    connection_rows = claimed_connections(page, count)
    claims = []
    for record, (new_trainer, new_owner) in zip(records, connection_rows):
        claimed = compact(record.group(1))
        if not all((claimed, new_trainer, new_owner)):
            raise CardError(f"Race {number}: missing new connections")
        if horse_key(claimed) not in price_map:
            raise CardError(f"Race {number}: cannot match claimed horse {claimed}")
        program, name, amount = price_map[horse_key(claimed)]
        if any(program not in mapping for mapping in (old_trainers, old_owners, finishes)):
            raise CardError(f"Race {number}: missing previous connections or finish for {name}")
        claims.append(dict(race=number, program_number=program, finish_position=finishes[program],
                           horse=name, claim_price_cad=str(amount.quantize(Decimal('0.01'))),
                           previous_owner=old_owners[program], previous_trainer=old_trainers[program],
                           new_owner=new_owner, new_trainer=new_trainer))
    return claims


def parse_card(pdf_path, target, expected_races=None):
    blocks = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text(x_tolerance=1, y_tolerance=3) or ''
            match = HEADER.search(text)
            if match:
                chart_date = datetime.strptime(compact(match.group(1)), '%B %d, %Y').date()
                if chart_date != target:
                    raise CardError(f"Chart date {chart_date} does not match requested date {target}")
                blocks.append(dict(number=int(match.group(2)), page=page, text=text))
            elif blocks:
                blocks[-1]['text'] += '\n' + text
            elif text.strip():
                raise CardError("Not a recognized Woodbine results chart")
        if not blocks:
            raise CardError("No Woodbine races found")
        numbers = [b['number'] for b in blocks]
        if numbers != list(range(1, max(numbers) + 1)):
            raise CardError(f"Missing, duplicate or out-of-order race charts: {numbers}")
        if expected_races is not None and len(numbers) != expected_races:
            raise CardError(f"Expected {expected_races} races, found {len(numbers)}")
        cancelled = [b['number'] for b in blocks if re.search(r'^Cancelled\s*-\s*\S', b['text'], re.M)]
        all_cancelled = len(cancelled) == len(blocks)
        if all_cancelled and expected_races is None:
            raise CardError('Cancelled card requires an independently supplied scheduled race count')
        for block in blocks:
            if block['number'] in cancelled and 'Copyright' not in block['text']:
                raise CardError('Incomplete cancellation chart')
        if not all_cancelled and expected_races is None and not re.search(r'Total Attendance:\s*.*?Handle:\s*\$', blocks[-1]['text']):
            raise CardError("Full-card closing attendance/handle marker missing; cannot confirm coverage")
        claims = [claim for block in blocks
                  if block['number'] not in cancelled
                  for claim in parse_race(block['text'], block['page'], block['number'])]
    keys = [(c['race'], c['program_number']) for c in claims]
    if len(set(keys)) != len(keys):
        raise CardError("Duplicate claims detected")
    total = sum((Decimal(c['claim_price_cad']) for c in claims), Decimal(0))
    return dict(track='Woodbine', date=target.isoformat(), currency='CAD', races_checked=numbers,
                completed_races=[n for n in numbers if n not in cancelled], cancelled_races=cancelled,
                parser_version=PARSER_VERSION,
                status='cancelled' if all_cancelled else 'claims_found' if claims else 'no_claims', claims=claims,
                total_claims=len(claims), total_claim_value_cad=f'{total:.2f}',
                message='Card cancelled - no races run' if all_cancelled else f'{len(claims)} claimed horses' if claims else NO_CLAIMS,
                source_sha256=hashlib.sha256(Path(pdf_path).read_bytes()).hexdigest())


def download_chart(target, destination):
    filename = 'WO' + target.strftime('%m%d%y') + 'CAN.pdf'
    errors = []
    for host in ('tvg.equibase.com', 'www.equibase.com'):
        url = f'https://{host}/static/chart/pdf/{filename}'
        try:
            request = urllib.request.Request(url, headers={'User-Agent': 'WoodbineClaims/1.0'})
            with urllib.request.urlopen(request, timeout=45) as response:
                content = response.read(30_000_001)
            if len(content) > 30_000_000 or not content.startswith(b'%PDF-'):
                raise CardError('Response is not an acceptable PDF')
            destination.write_bytes(content)
            return url
        except (OSError, CardError) as error:
            errors.append(f'{host}: {error}')
        # Some Windows HTTP clients receive challenge pages; curl is a standard
        # fallback. Certificate verification remains enabled and HTML is rejected.
        try:
            process = subprocess.run(['curl', '--fail', '--silent', '--show-error',
                '--location', '--max-time', '45', '--output', str(destination), url],
                capture_output=True, text=True, timeout=50)
            if process.returncode == 0 and destination.read_bytes().startswith(b'%PDF-'):
                return url
        except (OSError, subprocess.TimeoutExpired):
            pass
    raise CardError('Could not retrieve official full-card chart. Supply --pdf. ' + '; '.join(errors))


def display_trainer(value):
    if ',' in value:
        surname, given = value.rsplit(',', 1)
        return compact(f'{given} {surname}')
    return value


def claim_lines(claim):
    """Two wrapping rows, shared by the daily and annual sections."""
    c = claim
    return [
        f"**Race {c['race']} - {c['horse']}** | Previous owner: {c['previous_owner']}; trainer: {display_trainer(c['previous_trainer'])}  ",
        f"**Finish: {c['finish_position']} | Claim: C${Decimal(c['claim_price_cad']):,.0f}** | New owner: {c['new_owner']}; trainer: {c['new_trainer']}",
        '',
    ]


def claim_html(c):
    def safe(value):
        return escape(str(value))
    return (
        '<article class="claim">'
        f'<p class="previous"><strong class="horse">Race {safe(c["race"])} - {safe(c["horse"])}</strong>'
        f' &middot; Previous owner: {safe(c["previous_owner"])}; trainer: {safe(display_trainer(c["previous_trainer"]))}</p>'
        f'<p class="new"><strong>Finish: {safe(c["finish_position"])} &middot; Claim: '
        f'C${Decimal(c["claim_price_cad"]):,.0f}</strong>'
        f' &middot; New owner: {safe(c["new_owner"])}; trainer: {safe(c["new_trainer"])}</p>'
        '</article>')


def html_report(report):
    """Standalone, wrapping report; also supplies reusable markup for the future page."""
    annual = 'daily' in report
    daily = report['daily'] if annual else report
    title = f'Woodbine Claims - {daily["date"]}'
    content = [f'<h1>{escape(title)}</h1>',
        f'<p class="meta">{len(daily["races_checked"])} races checked. All amounts in Canadian dollars.</p>',
        '<section aria-label="Latest completed card">']
    content += [claim_html(c) for c in daily['claims']]
    if not daily['claims']:
        content.append(f'<p>{escape(daily.get("message", NO_CLAIMS))}</p>')
    content += [f'<p class="total">{daily["total_claims"]} claims | C${Decimal(daily["total_claim_value_cad"]):,.0f} total</p>', '</section>']
    if annual:
        content += [f'<section aria-label="All current-year claims"><h2>All {report["year"]} Claims</h2>',
            f'<p class="total">{report["total_claims"]} claims | C${Decimal(report["total_claim_value_cad"]):,.0f} total</p>',
            f'<p class="meta">{report["completed_cards"]} completed cards checked, {report["coverage_start"]} through {report["coverage_through"]}.<br>'
            'Newest date first; race numbers in order. All amounts CAD.</p>']
        if not report['complete']:
            content.append('<p class="previous"><strong>INCOMPLETE COVERAGE</strong> - unverified dates: '
                           + escape(', '.join(report['missing_dates'])) + '</p>')
        previous_date = None
        for c in report['claims']:
            if c['date'] != previous_date:
                content.append(f'<h3>{escape(c["date"])}</h3>')
                previous_date = c['date']
            content.append(claim_html(c))
        content.append('</section>')
    content.append('<footer>Previous owner/trainer in red. New owner/trainer in green. '
                   'Labels also identify each line.<br>Sources and verification details are retained in the accompanying JSON.</footer>')
    return ('<!doctype html><html lang="en"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width,initial-scale=1">'
        f'<title>{escape(title)}</title><style>'
        ':root{color-scheme:dark}*{box-sizing:border-box}'
        'body{margin:0;background:#191919;color:#f5f5f5;font:14px/1.5 Arial,sans-serif}'
        'main{max-width:1200px;margin:auto;padding:18px 20px;overflow-wrap:anywhere}'
        'h1{font-size:22px;margin:0 0 8px}h2{font-size:21px;margin:24px 0 10px}'
        'h3{font-size:16px;margin:18px 0 8px}.claim{margin:0 0 10px}.claim p{margin:0}'
        '.previous{color:#ff858c}.new{color:#78e6a2}.horse{color:#75baff}.meta{margin:0 0 12px}'
        '.total{font-weight:bold;margin:8px 0 4px}footer{font-size:12px;color:#bbb;margin-top:24px}'
        '@media(max-width:600px){main{padding:14px 12px}body{font-size:13px}}'
        '</style></head><body><main>' + '\n'.join(content) + '</main></body></html>')


def markdown(report):
    lines = [f"# Woodbine Claims - {report['date']}", '',
             f"Verified results: {len(report['races_checked'])} races. All amounts in Canadian dollars.", '']
    if not report['claims']:
        lines += [report.get('message', NO_CLAIMS), '']
    else:
        for c in report['claims']:
            lines += claim_lines(c)
        lines += ['', f"Total: {report['total_claims']} claims, C${Decimal(report['total_claim_value_cad']):,.0f}.", '']
    lines += [f"Source: {report.get('source', 'Supplied official chart PDF')}", '',
              'Previous connections are the owner and trainer listed for that race, before the claim.', '']
    return '\n'.join(lines)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--date', required=True, type=date.fromisoformat, help='YYYY-MM-DD')
    parser.add_argument('--pdf', type=Path, help='Previously downloaded official full-card chart')
    parser.add_argument('--expected-races', type=int, help='Optional additional card-count check')
    parser.add_argument('--output-dir', type=Path, default=Path('reports'))
    args = parser.parse_args()
    try:
        with tempfile.TemporaryDirectory(prefix='woodbine-claims-') as temp:
            pdf_path = args.pdf or Path(temp) / 'chart.pdf'
            source = str(args.pdf.resolve()) if args.pdf else download_chart(args.date, pdf_path)
            report = parse_card(pdf_path, args.date, args.expected_races)
            report.update(source=source, checked_at=datetime.now(timezone.utc).isoformat())
            args.output_dir.mkdir(parents=True, exist_ok=True)
            stem = args.output_dir / f'woodbine-claims-{args.date}'
            stem.with_suffix('.json').write_text(json.dumps(report, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
            rendered = markdown(report)
            stem.with_suffix('.md').write_text(rendered, encoding='utf-8')
            stem.with_suffix('.html').write_text(html_report(report), encoding='utf-8')
            print(rendered)
    except (CardError, OSError, StopIteration, ValueError) as error:
        print(f'Results could not be verified: {error}. No no-claims report was issued.', file=sys.stderr)
        return 2
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
