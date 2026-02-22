#!/usr/bin/env python3
"""
DRF PDF Parser - Extracts structured past performance data
Uses pdfplumber for reliable Beyer figure extraction

Usage:
    python3 parse_drf.py <drf_pdf_file>
    python3 parse_drf.py <drf_pdf_file> --race 3
    python3 parse_drf.py <drf_pdf_file> --json
"""
import pdfplumber
import re
import sys
import json
from pathlib import Path

# ── Regex patterns ───────────────────────────────────────────────────────────
POST_TIME  = re.compile(r'Posttime:', re.IGNORECASE)
BEYER_PAR  = re.compile(r'Beyerpar:\s*(\d+|NA)', re.IGNORECASE)
BEYER_FIG  = re.compile(r'(\d{2,3})=\d{2}')
PP_DATE    = re.compile(r'^\d{1,2}[åæçèÝáâãäòÁÂÃÄßàÜÛÞ]')
STANDALONE = re.compile(r'^\s*(\d{1,2})\s*$')
HORSE_LINE = re.compile(
    r'^([A-Z][A-Za-z\'\*\/\(\)\s]+?)\s+'
    r'(?:B\.|Ch\.|Gr/ro\.|Dk\.b|Ro\.|Blk\.|Gy\.)[a-z]\.'
)
TRAINER_RE = re.compile(r'Tr:\s*([A-Z][^(]+?)\s*\(')


def parse_pdf(pdf_path, target_race=None):
    """Parse a DRF PDF and return structured race/horse data."""
    pdf_path = Path(pdf_path)
    if not pdf_path.exists():
        print(f"❌ File not found: {pdf_path}", file=sys.stderr)
        sys.exit(1)

    races = {}
    current_race = 0
    current_horse = None
    pending_pp = None

    with pdfplumber.open(str(pdf_path)) as pdf:
        for page in pdf.pages:
            lines = (page.extract_text() or "").split('\n')
            for line in lines:
                s = line.strip()
                if not s:
                    pending_pp = None
                    continue

                # ── New race: "Posttime:12:20ET" appears once per race
                if POST_TIME.search(s):
                    current_race += 1
                    races[current_race] = {'race': current_race, 'par': None, 'horses': []}
                    current_horse = None
                    pending_pp = None
                    continue

                if current_race == 0:
                    continue

                # ── Beyer par for the race
                m = BEYER_PAR.search(s)
                if m and races[current_race]['par'] is None:
                    v = m.group(1)
                    races[current_race]['par'] = int(v) if v != 'NA' else None

                # ── Standalone number = post position
                m = STANDALONE.match(s)
                if m:
                    pending_pp = int(m.group(1))
                    continue

                # ── Horse name line (follows a PP number)
                if pending_pp is not None:
                    hm = HORSE_LINE.match(s)
                    if hm:
                        name = hm.group(1).strip().rstrip('* ')
                        current_horse = {
                            'pp': pending_pp, 'name': name,
                            'trainer': None, 'beyers': [],
                            'pp_lines': []
                        }
                        races[current_race]['horses'].append(current_horse)
                    pending_pp = None

                # ── Trainer
                if current_horse and 'Tr:' in s:
                    tm = TRAINER_RE.search(s)
                    if tm:
                        current_horse['trainer'] = tm.group(1).strip()

                # ── Past performance line with Beyer
                if current_horse and PP_DATE.match(s):
                    bm = BEYER_FIG.search(s)
                    if bm:
                        current_horse['beyers'].append(int(bm.group(1)))
                        current_horse['pp_lines'].append(s[:130])

    # ── Compute Beyer averages (last 3, most recent first)
    for race_data in races.values():
        for horse in race_data['horses']:
            b = horse['beyers'][:3]
            horse['beyer_avg']  = round(sum(b) / len(b), 1) if b else None
            horse['beyer_last'] = b[0] if b else None
            horse['beyer_trend'] = (
                '📈' if len(b) >= 2 and b[0] > b[1] else
                '📉' if len(b) >= 2 and b[0] < b[1] else '➡️'
            )

    if target_race:
        return {target_race: races.get(target_race, {'race': target_race, 'horses': [], 'par': None})}
    return races


def print_summary(races):
    total_h = sum(len(r['horses']) for r in races.values())
    print(f"Races: {len(races)}  |  Horses: {total_h}")

    for rn in sorted(races):
        r = races[rn]
        par = r['par']
        horses = r['horses']
        print(f"\n{'='*62}")
        print(f"RACE {rn}  |  Beyer Par: {par if par else 'N/A'}")
        print(f"{'='*62}")
        if not horses:
            print("  (no horses parsed)")
            continue

        with_data = sorted([h for h in horses if h['beyer_avg']], key=lambda x: -x['beyer_avg'])
        no_data   = [h for h in horses if not h['beyer_avg']]

        for h in with_data:
            b3 = ', '.join(str(x) for x in h['beyers'][:3])
            tr = f"  [{h['trainer']}]" if h['trainer'] else ''
            print(f"  #{h['pp']:2} {h['name']:<28}  Avg:{h['beyer_avg']:6.1f}  [{b3}] {h['beyer_trend']}{tr}")
        for h in no_data:
            print(f"  #{h['pp']:2} {h['name']:<28}  Avg:   N/A  (debut/no figures)")


def main():
    args = sys.argv[1:]
    if not args or '-h' in args or '--help' in args:
        print(__doc__)
        sys.exit(0)

    pdf_path = args[0]
    as_json  = '--json' in args
    race_arg = None
    if '--race' in args:
        idx = args.index('--race')
        try:
            race_arg = int(args[idx + 1])
        except (IndexError, ValueError):
            print("Error: --race requires a number", file=sys.stderr)
            sys.exit(1)

    races = parse_pdf(pdf_path, race_arg)

    if as_json:
        # Remove raw pp_lines from JSON output for cleanliness
        for r in races.values():
            for h in r['horses']:
                h.pop('pp_lines', None)
        print(json.dumps(races, indent=2))
    else:
        print_summary(races)


if __name__ == '__main__':
    main()
