#!/usr/bin/env python3
"""
drf_beyer_unified.py
Handles BOTH Gulfstream Park (GP) and Woodbine (WO) DRF PDFs.
GP: single-line horse headers (PP ML HorseName Own:)
WO: multiline headers (race_num\nPP-ML\nHorseName\nOwn:)
"""

import re, json, tempfile
from pathlib import Path
from typing import List, Dict, Optional, Tuple

try:
    import fitz
except Exception:
    fitz = None

try:
    import pdfplumber
except Exception:
    pdfplumber = None

# ─── REGEX: GP FORMAT ───────────────────────────────────────────────────────────
GP_RACE_RE = re.compile(
    r'(?ms)^\s*(\d+)\s+Gulfstream Park\b(.*?)(?:Beyer\s*par[:\s]*(\d+|NA))?',
    re.I
)
GP_HORSE_RE = re.compile(r'(?m)^\s*(\d+)\s+([0-9]+(?:-[0-9]+(?:/[0-9]+)?)?)\s+(.+)$')
GP_PP_LINE_RE = re.compile(r'(?m)^\s*\d{1,2}[a-zA-Z]*\d{0,2}=\s*(\d+)\s+([A-Z]{2,4})\b.*?\s(\d{1,3})\b')

# ─── REGEX: WO FORMAT ─────────────────────────────────────────────────────────
# Horse header: race_num\nPP-ML\nHorseName\nOwn:
# PP on own line, then ML, then horse name
WO_HORSE_RE = re.compile(r'(?m)^\s*(\d+)\n(\d+)-(\d+)\n([A-Za-z].+?)\nOwn')
# PP lines: first digits before '=' are the Beyer
WO_BEYER_RE = re.compile(r'\b(\d{1,3})\s*=\s*(\d{1,2})\b')

# ─── REGEX: SHARED ────────────────────────────────────────────────────────────
PACE_RE = re.compile(r'TimeformUS Pace[:\s]+Early[:\s]+(\d+)\s+Late[:\s]+(\d+)', re.I)
WORKS_RE = re.compile(r'^(WORKS|TRAINER|Daily Racing Form|Copyright)', re.I)
SUMMARY_RE = re.compile(r'^(Life|20\d{2}|WO|GP|D\.Fst|Wet\d*|Synth\d*|Turf\d*|Dst\d*)', re.I)

CLASS_WEIGHTS = {
    'MDSPW': 10, 'MOC': 9, 'MAIDEN': 7, 'CLM': 4,
    'AOC': 12, 'OC': 11, 'ALW': 9, 'STK': 16,
    'GRADED': 20, 'UNKNOWN': 0,
}
SCORING = {
    'RECENCY_LAST_WEIGHT': 0.70,
    'RECENCY_AVG3_WEIGHT': 0.45,
    'PAR_DELTA_WEIGHT': 1.15,
    'TREND_IMPROVING_BONUS': 4.0,
    'TREND_DECLINING_PENALTY': -3.5,
    'PACE_SPRINT_EARLY_GOOD': 4.5,
    'PACE_MISSING': 0.0,
    'SURFACE_MATCH_EXCELLENT_BONUS': 6.0,
    'SURFACE_MATCH_GOOD_BONUS': 3.0,
    'SURFACE_MATCH_POOR_PENALTY': -5.0,
    'SURFACE_RECENT_MATCH_BONUS': 1.5,
    'SURFACE_RECENT_MISS_PENALTY': -1.5,
    'CLASS_TOP_OVER_PAR_BONUS': 7.0,
    'CLASS_AVG_AT_PAR_BONUS': 3.5,
    'CLASS_AVG_WELL_BELOW_PAR_PENALTY': -6.0,
}
CONFIG = SCORING

# ─── PDF EXTRACTION ─────────────────────────────────────────────────────────────

def extract_pdf_text(pdf_path: str) -> Tuple[str, List[str]]:
    """Extract raw text. Returns (all_text, list_of_page_texts)."""
    if fitz:
        doc = fitz.open(pdf_path)
        pages = [doc[p].get_text("text") for p in range(len(doc))]
        return '\n'.join(pages), pages
    elif pdfplumber:
        with pdfplumber.open(pdf_path) as pdf:
            pages = [p.extract_text() or '' for p in pdf.pages]
        return '\n'.join(pages), pages
    raise RuntimeError('Neither fitz nor pdfplumber available')


def detect_format(text: str) -> str:
    """Detect GP vs WO format from text content."""
    if 'Gulfstream Park' in text or re.search(r'GP\b', text[:500]):
        return 'GP'
    if 'Woodbine' in text or 'Own:' in text:
        return 'WO'
    return 'UNKNOWN'


# ─── GP PARSING ───────────────────────────────────────────────────────────────

def gp_extract_race_blocks(text: str) -> List[Dict]:
    """Extract GP race sections."""
    blocks = []
    for m in GP_RACE_RE.finditer(text):
        race_num = int(m.group(1))
        par = m.group(3)
        par = None if par and par.upper() == 'NA' else int(par) if par and par.isdigit() else None
        header = m.group(2)
        start = m.start()
        end = m.end()
        # Next race start or end of text
        next_m = GP_RACE_RE.search(text, end)
        end = next_m.start() if next_m else len(text)
        blocks.append({
            'race_number': race_num,
            'header_block': header,
            'beyer_par': par,
            'text': text[start:end],
        })
    return blocks


def gp_split_horse_blocks(race_text: str) -> List[Dict]:
    """Split GP race text into horse blocks."""
    lines = race_text.splitlines()
    starts = []
    for idx, line in enumerate(lines):
        stripped = line.strip()
        m = GP_HORSE_RE.match(stripped)
        if m and any(k in m.group(3) for k in ['Own', 'Own:', 'TimeformUS Pace', 'Sire ']):
            starts.append((idx, m))
    
    horses = []
    for i, (idx, m) in enumerate(starts):
        end_idx = starts[i + 1][0] if i + 1 < len(starts) else len(lines)
        block_lines = lines[idx:end_idx]
        rest = m.group(3).strip()
        horse_name = re.split(r'\bOwn\b', rest, maxsplit=1, flags=re.I)[0].strip()
        horses.append({
            'pp': m.group(1).strip(),
            'ml': m.group(2).strip(),
            'horse_name': horse_name,
            'block_text': '\n'.join(block_lines),
        })
    return horses


def gp_extract_pps(horse_text: str) -> List[Dict]:
    """Extract Beyer figures from GP PP lines."""
    pps = []
    for line in horse_text.splitlines():
        s = line.strip()
        if not s or WORKS_RE.match(s) or SUMMARY_RE.match(s):
            continue
        if s.startswith(('TimeformUS Pace', 'Own ', 'Own:', 'Sire ', 'Dam', 'Br ', 'Tr ')):
            continue
        m = GP_PP_LINE_RE.search(s)
        if m:
            beyer = int(m.group(3)) if 1 <= int(m.group(3)) <= 130 else None
            if beyer:
                pps.append({'beyer': beyer, 'surface': None})
    return pps


def gp_extract_connections(horse_text: str) -> Dict[str, Optional[str]]:
    jockey = trainer = None
    # Trainer: Tr: Name
    tr_m = re.search(r'\bTr:\s*([A-Za-z][A-Za-z\s]+?)(?:\(|L|$)', horse_text, re.I)
    if tr_m:
        trainer = tr_m.group(1).strip().rstrip(')')
    # Jockey: ALL-CAPS initials + number
    jk_m = re.search(r'\b([A-Z][a-z]+\s+[A-Z])\s+(?:\(|L)', horse_text)
    if jk_m:
        jockey = jk_m.group(1).strip()
    return {'jockey': jockey, 'trainer': trainer}


# ─── WO PARSING ───────────────────────────────────────────────────────────────

def wo_extract_horse_blocks(pages: List[str]) -> List[Dict]:
    """Extract WO horse blocks from all pages with true global PP assignment."""
    all_matches = []
    for page_num, page_text in enumerate(pages):
        if 'Own:' not in page_text:
            continue
        for m in WO_HORSE_RE.finditer(page_text):
            all_matches.append({
                'race_num': m.group(1),
                'pp_raw': m.group(3),  # raw PP from regex (not used)
                'ml': f"{m.group(2)}-{m.group(3)}",
                'horse_name': m.group(4).strip(),
                'page': page_num + 1,
                '_abs_pos': len(all_matches),
                'block_text': page_text[m.start():m.start() + 2000],
            })
    
    # Sort by absolute position
    all_matches.sort(key=lambda x: x['_abs_pos'])
    
    # Group by race and assign PP globally
    from collections import defaultdict
    race_groups = defaultdict(list)
    for h in all_matches:
        race_groups[int(h['race_num'])].append(h)
    
    result = []
    for rn, horses in race_groups.items():
        for pp_i, h in enumerate(horses, 1):
            result.append({
                'race_num': h['race_num'],
                'pp': str(pp_i),
                'ml': h['ml'],
                'horse_name': h['horse_name'],
                'block_text': h['block_text'],
            })
    return result


def wo_extract_pps(horse_text: str) -> List[Dict]:
    """Extract Beyer figures from WO PP lines."""
    pps = []
    for line in horse_text.splitlines():
        for m in WO_BEYER_RE.finditer(line):
            beyer = int(m.group(1))
            finish = int(m.group(2))
            if 1 <= beyer <= 130 and 1 <= finish <= 12:
                pps.append({'beyer': beyer, 'surface': None})
    return pps


def wo_extract_connections(horse_text: str) -> Dict[str, Optional[str]]:
    jockey = trainer = None
    tr_m = re.search(r'\bTr:\s*([A-Za-z][A-Za-z\s]+?)(?:\(|L|$)', horse_text, re.I)
    if tr_m:
        trainer = tr_m.group(1).strip().rstrip(')')
    jk_m = re.search(r'\b([A-Z][a-z]+\s+[A-Z])\s+(?:\(|L)', horse_text)
    if jk_m:
        jockey = jk_m.group(1).strip()
    return {'jockey': jockey, 'trainer': trainer}


# ─── SCORING (SHARED) ───────────────────────────────────────────────────────────

def score_beyers(pps: List[Dict]) -> Dict:
    vals = [p['beyer'] for p in pps if isinstance(p.get('beyer'), int)]
    if not vals:
        return {'last_beyer': None, 'best_last_3': None, 'avg_last_3': None,
                'top_beyer': None, 'history_count': 0}
    last3 = vals[:3]
    return {
        'last_beyer': vals[0],
        'best_last_3': max(last3),
        'avg_last_3': round(sum(last3) / len(last3), 1),
        'top_beyer': max(vals),
        'history_count': len(vals),
    }


def infer_race_surface(header: str) -> str:
    h = header.lower()
    if any(x in h for x in [' turf', 'turf.', ' fm ', 'firm', 'yl ', 'yielding']):
        return 'turf'
    if any(x in h for x in ['tapeta', 'synth', 'synthetic']):
        return 'synthetic'
    return 'dirt'


def infer_race_class(header: str) -> str:
    h = header.lower()
    if re.search(r'\bG[123]\b', header):
        return 'GRADED'
    if any(x in h for x in ['stk', 'stakes', 'hcp']):
        return 'STK'
    if 'aoc' in h:
        return 'AOC'
    if ' oc ' in f' {h} ':
        return 'OC'
    if ' alw ' in f' {h} ':
        return 'ALW'
    if any(x in h for x in ['clm', 'claiming']):
        return 'CLM'
    if 'md sp wt' in h:
        return 'MDSPW'
    if 'moc' in h:
        return 'MOC'
    if any(x in h for x in ['md', 'maiden']):
        return 'MAIDEN'
    return 'UNKNOWN'


# ─── ANALYZE ──────────────────────────────────────────────────────────────────

def analyze_horse(h: Dict, race: Dict) -> Dict:
    block = h['block_text']
    
    if race.get('_format') == 'GP':
        pps = gp_extract_pps(block)
        conn = gp_extract_connections(block)
    else:
        pps = wo_extract_pps(block)
        conn = wo_extract_connections(block)
    
    pace_m = PACE_RE.search(block)
    pace = {'early': int(pace_m.group(1)) if pace_m else None,
            'late': int(pace_m.group(2)) if pace_m else None}
    
    summary = score_beyers(pps)
    
    # Basic scoring
    base = 0.0
    if summary['last_beyer']:
        base += summary['last_beyer'] * CONFIG['RECENCY_LAST_WEIGHT']
    if summary['avg_last_3']:
        base += summary['avg_last_3'] * CONFIG['RECENCY_AVG3_WEIGHT']
    
    par = race.get('beyer_par')
    if summary['last_beyer'] and par:
        base += (summary['last_beyer'] - par) * CONFIG['PAR_DELTA_WEIGHT']
    
    par_delta = (summary['last_beyer'] - par) if summary['last_beyer'] and par else None
    trend = 'mixed'
    if summary['history_count'] >= 3:
        v = [p['beyer'] for p in pps[:3] if isinstance(p.get('beyer'), int)]
        if len(v) >= 3:
            if v[0] > v[1] > v[2]:
                trend = 'improving'
                base += CONFIG['TREND_IMPROVING_BONUS']
            elif v[0] < v[1] < v[2]:
                trend = 'declining'
                base += CONFIG['TREND_DECLINING_PENALTY']
    
    # Surface adjustment
    surface = race.get('surface', 'dirt')
    recent_same = [p['beyer'] for p in pps[:5] if p.get('surface') == surface]
    surface_adj = 1.5 if recent_same else -1.5
    base += surface_adj
    
    # Value flag
    value_flag = ''
    try:
        ml = h['ml']
        ml_clean = ml.replace('/', '-')
        if '-' in ml_clean:
            left, right = ml_clean.split('-')[:2]
            odds_ratio = float(left) / float(right)
            if base >= 95 and odds_ratio <= 2.0:
                value_flag = 'logical favorite'
            elif base >= 85 and odds_ratio >= 4.0:
                value_flag = 'value'
    except Exception:
        pass
    
    return {
        'program_number': h['pp'],
        'horse_name': h['horse_name'],
        'morning_line': h['ml'],
        'jockey': conn.get('jockey'),
        'trainer': conn.get('trainer'),
        'timeform_pace': pace,
        'beyer_summary': summary,
        'par_delta': par_delta,
        'trend': trend,
        'pace_adjustment': CONFIG['PACE_SPRINT_EARLY_GOOD'] if pace['early'] and pace['early'] >= 85 else CONFIG['PACE_MISSING'],
        'surface_adjustment': surface_adj,
        'analysis_score': round(base, 1),
        'value_flag': value_flag,
        'status': 'ok' if summary['history_count'] else 'needs_review',
        'pps': pps,
    }


def analyze(text: str, pages: List[str], race_blocks: List[Dict], format: str) -> Dict:
    races_out = []
    for race in race_blocks:
        race['surface'] = infer_race_surface(race.get('header_block', ''))
        race['race_class'] = infer_race_class(race.get('header_block', ''))
        race['_format'] = format
        
        if format == 'GP':
            horse_blocks = gp_split_horse_blocks(race['text'])
        else:
            # WO: pass all pages to extract global PP positions
            horse_blocks = wo_extract_horse_blocks(pages)
            # Filter to just this race
            race_num = race['race_number']
            horse_blocks = [h for h in horse_blocks if int(h['race_num']) == race_num]
        
        analyzed = [analyze_horse(h, race) for h in horse_blocks]
        analyzed.sort(key=lambda x: x['analysis_score'], reverse=True)
        
        races_out.append({
            'race_number': race['race_number'],
            'beyer_par': race.get('beyer_par'),
            'surface': race.get('surface', 'dirt'),
            'race_class': race.get('race_class', 'UNKNOWN'),
            'header_block': race.get('header_block', ''),
            'horses': analyzed,
            'top_3': analyzed[:3],
        })
    
    races_out.sort(key=lambda x: x['race_number'])
    return {'races': races_out}


# ─── VALIDATORS ────────────────────────────────────────────────────────────────

def validate(data: Dict) -> List[str]:
    issues = []
    races = data.get('races', [])
    if not races:
        issues.append('No races found')
    for race in races:
        rn = race.get('race_number')
        horses = race.get('horses', [])
        if not horses:
            issues.append(f'Race {rn}: no horses parsed')
        for h in horses:
            name = h.get('horse_name', '')
            ml = h.get('morning_line', '')
            if not name:
                issues.append(f'Race {rn}: blank horse name')
            if not re.fullmatch(r'[0-9]+(?:-[0-9]+(?:/[0-9]+)?)?', str(ml)):
                issues.append(f'Race {rn} {name}: unusual morning line {ml!r}')
            s = h.get('beyer_summary', {})
            pps = h.get('pps', [])
            if not pps and s.get('last_beyer') is None:
                issues.append(f'Race {rn} {name}: no Beyer history extracted')
    return issues


def validate_pars(data: Dict) -> List[str]:
    issues = []
    for race in data.get('races', []):
        par = race.get('beyer_par')
        if par is None:
            continue
        tops = []
        for h in race.get('horses', []):
            s = h.get('beyer_summary', {})
            for key in ('last_beyer', 'best_last_3'):
                v = s.get(key)
                if isinstance(v, (int, float)):
                    tops.append(v)
        if tops:
            top = max(tops)
            if top > par + 40:
                issues.append(f"Race {race.get('race_number')}: top Beyer {top} far above par {par}")
            if top < par - 35:
                issues.append(f"Race {race.get('race_number')}: top Beyer {top} far below par {par}")
    return issues


# ─── RENDER ───────────────────────────────────────────────────────────────────

def render_telegram_summary(data: Dict) -> str:
    parts = []
    for race in data.get('races', []):
        lines = [f"🏇 Race {race['race_number']} | Par {race['beyer_par']} | {race['surface']} | {race['race_class']}"]
        for i, h in enumerate(race.get('top_3', []), 1):
            s = h['beyer_summary']
            tf = h['timeform_pace']
            flag = f" | {h['value_flag'].upper()}" if h['value_flag'] else ''
            conn = f" | J:{h['jockey'] or '?'} T:{h['trainer'] or '?'}"
            lines.append(
                f"{i}. #{h['program_number']} {h['horse_name']} ({h['morning_line']}) | "
                f"Score {h['analysis_score']} | Last {s['last_beyer']} | Avg3 {s['avg_last_3']} | "
                f"E/L {tf.get('early','?')}/{tf.get('late','?')} | "
                f"Pace {h['pace_adjustment']:+.1f} | Surf {h['surface_adjustment']:+.1f}{flag}{conn}"
            )
            reasons = [r for r in [f"par delta {h['par_delta']:+}" if h['par_delta'] else None,
                                   f"improving" if h['trend'] == 'improving' else None,
                                   f"declining" if h['trend'] == 'declining' else None,
                                   f"needs_review" if h['status'] == 'needs_review' else None] if r]
            if reasons:
                lines.append(f" Notes: {', '.join(reasons)}")
        parts.append('\n'.join(lines))
    return '\n\n'.join(parts) if parts else 'No races parsed.'


# ─── MAIN ────────────────────────────────────────────────────────────────────────

def analyze_drf(pdf_path: str) -> Dict:
    all_text, pages = extract_pdf_text(pdf_path)
    fmt = detect_format(all_text)
    
    if fmt == 'GP':
        race_blocks = gp_extract_race_blocks(all_text)
    else:
        # For WO, build race blocks from race number headers
        race_blocks = []
        for m in re.finditer(r'(?m)^\s*(\d+)\s*\n\s*Woodbine\b', all_text):
            race_num = int(m.group(1))
            start = m.start()
            next_m = re.search(r'(?m)^\s*\d+\s*\n\s*Woodbine\b', all_text[start + 1:])
            end = start + 1 + next_m.start() if next_m else len(all_text)
            par_m = re.search(r'Beyer\s*par[:\s]*(\d+|NA)', all_text[start:end], re.I)
            par = None
            if par_m:
                par_str = par_m.group(1)
                par = None if par_str.upper() == 'NA' else int(par_str)
            race_blocks.append({
                'race_number': race_num,
                'header_block': all_text[start:end][:200],
                'beyer_par': par,
                'text': all_text[start:end],
            })
    
    return analyze(all_text, pages, race_blocks, fmt)


if __name__ == '__main__':
    import sys
    if len(sys.argv) < 2:
        print('Usage: python drf_beyer_unified.py <pdf_path>')
        sys.exit(1)
    
    result = analyze_drf(sys.argv[1])
    all_issues = validate(result) + validate_pars(result)
    if all_issues:
        print('⚠️ VALIDATION ISSUES:', ', '.join(all_issues), '\n')
    print(render_telegram_summary(result))
    print('\n--- JSON ---\n')
    print(json.dumps(result, indent=2, default=str))
