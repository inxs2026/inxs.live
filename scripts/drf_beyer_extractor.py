#!/usr/bin/env python3
"""
drf_beyer_extractor.py
Carlo's extractor — WO + GP, pdfplumber, outputs CSV + JSON.
"""

import re, csv, json, argparse, pathlib

try:
    import pdfplumber
except Exception:
    pdfplumber = None

RACE_START_RE = re.compile(
    r'(?ms)^\s*(\d+)\s+(?:Woodbine|Gulfstream Park)\b(.*?)(?=\n\d+\s+(?:Woodbine|Gulfstream Park)\b|\Z)',
    re.I
)
HORSE_START_RE = re.compile(r'(?m)^\s*(\d+)\s+([0-9]+(?:-[0-9]+(?:/[0-9]+)?)?)\s+(.+)$')
PACE_RE = re.compile(r'TimeformUS Pace:\s*Early\s*(\d{1,3})\s*Late\s*(\d{1,3})', re.I)
WORKS_OR_TRAINER_RE = re.compile(
    r'^(WORKS|TRAINER|Daily Racing Form|Copyright|Previously trained by|Claimed from)',
    re.I
)
RESULT_LINE_RE = re.compile(
    r'(?m)^\s*\d{1,2}[a-zA-Z]*\d{0,2}=\s*\d+\s+([A-Z]{2,4})\b.*?\s(\d{1,3})\s+\d+\s+/\d+\s+',
    re.I
)
SUMMARY_LINE_RE = re.compile(
    r'^(Life|20\d{2}|WO|GP|D\.Fst|Wet\(?\d*\)?|Synth\(?\d*\)?|Turf\(?\d*\)?|Dst\(?\d*\)?|Previously trained by)',
    re.I
)
SURFACE_RE = re.compile(
    r'\b(fst|fast|fm|turf|gd|good|my|sly|sloppy|synth|synthetic)\b',
    re.I
)


def text_from_pdf(pdf_path: str) -> str:
    if pdfplumber is None:
        raise RuntimeError('pdfplumber is required')
    with pdfplumber.open(pdf_path) as pdf:
        return '\n'.join(page.extract_text() or '' for page in pdf.pages)


def normalize_text(text: str) -> str:
    text = text.replace('\r', '\n')
    text = re.sub(r'\n{3,}', '\n\n', text)
    text = re.sub(r'[ \t]{2,}', ' ', text)
    return text.strip()


def parse_entries(text: str) -> list:
    """Parse alphabetical index: HorseName,PP → (PP, HorseName)."""
    entries = []
    for m in re.finditer(r'(?m)^\s*(\d+)\s+([A-Za-z][A-Za-z0-9\'\-\. ]+?)\s*,\s*([1-9])\s*$', text):
        entries.append((int(m.group(3)), m.group(2).strip()))
    seen = set()
    out = []
    for e in entries:
        if e not in seen:
            seen.add(e)
            out.append(e)
    return out


def parse_pars(text: str) -> dict:
    """Extract Beyer pars per race."""
    pars = {}
    for m in re.finditer(r'(?m)^\s*(\d+)\s+Woodbine.*?Beyer par:?\s*(NA|\d+)', text, re.I):
        pars[int(m.group(1))] = None if m.group(2).upper() == 'NA' else int(m.group(2))
    return pars


def split_race_blocks(text: str) -> list:
    matches = list(RACE_START_RE.finditer(text))
    blocks = []
    for i, m in enumerate(matches):
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        blocks.append((int(m.group(1)), m.group(2).strip(), text[m.start():end]))
    return blocks


def split_horse_blocks(race_text: str) -> list:
    lines = race_text.splitlines()
    starts = []
    for idx, line in enumerate(lines):
        m = HORSE_START_RE.match(line.strip())
        if m and any(k in m.group(3) for k in ['Own', 'TimeformUS Pace', 'Beyer']):
            starts.append((idx, m))
    horses = []
    for i, (idx, m) in enumerate(starts):
        end = starts[i + 1][0] if i + 1 < len(starts) else len(lines)
        horses.append({
            'program_number': m.group(1),
            'morning_line': m.group(2),
            'horse_name': m.group(3).split(' Own ')[0].strip(),
            'text': '\n'.join(lines[idx:end]),
        })
    return horses


def extract_timeform_pace(text: str) -> dict:
    m = PACE_RE.search(text)
    return {'early': int(m.group(1)) if m else None, 'late': int(m.group(2)) if m else None}


def extract_pp_lines(text: str) -> list:
    out = []
    for line in text.splitlines():
        s = line.strip()
        if not s or WORKS_OR_TRAINER_RE.match(s) or SUMMARY_LINE_RE.match(s):
            continue
        if re.match(r'^\d{1,2}', s) and re.search(r'\b\d{2,4}\b', s):
            out.append(s)
    return out


def parse_result_line(line: str) -> dict:
    toks = line.split()
    if len(toks) < 8:
        return None
    track = None
    for t in toks:
        if t in {'WO', 'GP', 'FE', 'TP', 'MVR', 'CT', 'Tam', 'Aqu', 'CD', 'Sar', 'Bel', 'Kee', 'Ind', 'Mnr', 'Lrl'}:
            track = t
            break
    nums = [int(x) for x in re.findall(r'(?<![:$])\b\d{1,3}\b', line)]
    beyer = None
    for n in nums:
        if 0 <= n <= 120 and n not in {1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12}:
            beyer = n
            break
    return {'track': track, 'beyer': beyer, 'raw_line': line}


def score_beyers(pps: list) -> dict:
    from statistics import mean
    vals = [p['beyer'] for p in pps if isinstance(p.get('beyer'), int)]
    if not vals:
        return {'last_beyer': None, 'best_last_3': None, 'avg_last_3': None, 'history_count': 0}
    last3 = vals[:3]
    return {
        'last_beyer': vals[0],
        'best_last_3': max(last3),
        'avg_last_3': round(mean(last3), 1),
        'history_count': len(vals),
    }


def analyze(text: str) -> dict:
    text = normalize_text(text)
    pars = parse_pars(text)
    races = []
    for race_no, title, race_text in split_race_blocks(text):
        horses = []
        for hb in split_horse_blocks(race_text):
            pps = [parse_result_line(l) for l in extract_pp_lines(hb['text'])]
            pps = [p for p in pps if p]
            summary = score_beyers(pps)
            pace = extract_timeform_pace(hb['text'])
            horses.append({
                'program_number': hb['program_number'],
                'horse_name': hb['horse_name'],
                'morning_line': hb['morning_line'],
                'timeform_pace': pace,
                'pps': pps,
                'beyer_summary': summary,
                'race_number': race_no,
                'race_title': title,
                'race_beyer_par': pars.get(race_no),
                'status': 'ok' if summary['history_count'] else 'needs_review',
            })
        races.append({
            'race_number': race_no,
            'title': title,
            'beyer_par': pars.get(race_no),
            'horses': horses,
        })
    return {'races': races}


def write_outputs(data: dict, outdir: str = 'output') -> list:
    outdir = pathlib.Path(outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    rows = []
    for race in data['races']:
        for h in race['horses']:
            s = h['beyer_summary']
            rows.append({
                'race': race['race_number'],
                'horse': h['horse_name'],
                'ml': h['morning_line'],
                'last_beyer': s['last_beyer'],
                'best_last_3': s['best_last_3'],
                'avg_last_3': s['avg_last_3'],
                'history_count': s['history_count'],
                'status': h['status'],
            })
    with open(outdir / 'beyers.csv', 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=rows[0].keys() if rows else [
            'race', 'horse', 'ml', 'last_beyer', 'best_last_3', 'avg_last_3', 'history_count', 'status'
        ])
        w.writeheader()
        w.writerows(rows)
    (outdir / 'beyers.json').write_text(json.dumps(data, indent=2, default=str), encoding='utf-8')
    return rows


if __name__ == '__main__':
    import sys
    path = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else None
    if not path:
        print('Usage: python drf_beyer_extractor.py <pdf_path> [output_dir]')
        sys.exit(1)
    outdir = sys.argv[2] if len(sys.argv) > 2 else 'output'
    txt = text_from_pdf(str(path)) if path.suffix.lower() == '.pdf' else path.read_text(encoding='utf-8', errors='ignore')
    data = analyze(txt)
    rows = write_outputs(data, outdir)
    print(f"Wrote {len(rows)} horses to {outdir}/beyers.csv and {outdir}/beyers.json")
    print(json.dumps(data, indent=2, default=str)[:5000])
