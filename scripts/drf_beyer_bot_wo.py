"""
drf_beyer_bot_wo.py
Full WO DRF parser using PyMuPDF (better multi-column extraction than pdfplumber).
"""

import re
import json
from dataclasses import dataclass
from pathlib import Path
from typing import List, Dict, Optional, Tuple

try:
    import fitz  # PyMuPDF
except Exception:
    fitz = None

# ─── REGEX PATTERNS ──────────────────────────────────────────────────────────

# Horse header in WO text: race_num\nPP-ML\nHorseName\nOwn:
HORSE_HEADER_RE = re.compile(
    r'(?m)^\s*(\d+)\n(\d+)-(\d+)\n([A-Za-z].+?)\nOwn',
)

# PP record line: "13ã25=4WO fst 6f ú 22§ :45¨ :58¦1:11§ 3ÎçClm 23500(25-23.5)N3L 36 2 /8 5 1¨ 3ô 7¦¥ 8¦¨ö DouglasC¦¥ L112b 13.15 67=22..."
# Beyer = first digit before '='
PP_BEYER_RE = re.compile(r'\b(\d{1,3})\s*=\s*(\d{1,2})\b')

# Race info patterns from index pages
RACE_INFO_RE = re.compile(
    r'(?ms)^\s*(\d+)\s+Woodbine\b.+?(?:Beyer par[:\s]+(\d+|NA))?',
    re.MULTILINE
)

# ─── LOOKUP TABLES ───────────────────────────────────────────────────────────

CLASS_WEIGHTS = {
    'MDSPW': 10, 'MOC': 9, 'MAIDEN': 7, 'CLM': 4,
    'AOC': 12, 'OC': 11, 'ALW': 9, 'STK': 16, 'GRADED': 20, 'UNKNOWN': 0,
}

SCORING = {
    'PACE_ROUTE_LATE_ELITE': 7.0,
    'PACE_ROUTE_LATE_GOOD': 3.5,
    'PACE_ROUTE_SPEED_FADE_RISK': -3.0,
    'PACE_SPRINT_EARLY_GOOD': 4.5,
    'PACE_SPRINT_EARLY_ELITE': 2.5,
    'PACE_SPRINT_LOW_ENERGY': -4.0,
    'PACE_MISSING': 0.0,
    'SURFACE_SPECIFIC_EXCELLENT_RATIO': 0.95,
    'SURFACE_SPECIFIC_GOOD_RATIO': 0.85,
    'SURFACE_SPECIFIC_POOR_RATIO': 0.67,
    'SURFACE_MATCH_EXCELLENT_BONUS': 6.0,
    'SURFACE_MATCH_GOOD_BONUS': 3.0,
    'SURFACE_MATCH_POOR_PENALTY': -5.0,
    'SURFACE_RECENT_MATCH_BONUS': 1.5,
    'SURFACE_RECENT_MISS_PENALTY': -1.5,
    'SURFACE_UNKNOWN_DIRT_TURF_PENALTY': -5.0,
    'SURFACE_UNKNOWN_SYNTH_SWITCH_PENALTY': -2.5,
    'CLASS_TOP_OVER_PAR_BONUS': 7.0,
    'CLASS_AVG_AT_PAR_BONUS': 3.5,
    'CLASS_AVG_WELL_BELOW_PAR_PENALTY': -6.0,
    'CLASS_LAST_HIGHER_THAN_TODAY_BONUS': 2.5,
    'CLASS_LAST_LOWER_THAN_TODAY_PENALTY': -2.5,
    'TREND_IMPROVING_BONUS': 4.0,
    'TREND_DECLINING_PENALTY': -3.5,
    'RECENCY_LAST_WEIGHT': 0.70,
    'RECENCY_AVG3_WEIGHT': 0.45,
    'PAR_DELTA_WEIGHT': 1.15,
}

CONFIG = SCORING


# ─── PDF EXTRACTION ───────────────────────────────────────────────────────────

def extract_pdf_text(pdf_path: str) -> Tuple[List[str], List[str]]:
    """Extract index pages and data pages separately.
    
    Returns: (index_pages_text, data_pages_text)
    Index pages have race headers + entries + trainers + some horse data.
    Data pages have horse PP data.
    All pages are returned as data_pages too since index pages can contain horse data.
    """
    if fitz is None:
        raise RuntimeError('PyMuPDF (fitz) not installed')
    
    doc = fitz.open(pdf_path)
    index_pages = []
    data_pages = []
    
    for page_num in range(len(doc)):
        page = doc[page_num]
        text = page.get_text("text")
        if not text.strip():
            continue
        
        # Check if this is an index page (has "INDEX TO ENTRIES")
        if 'INDEX TO ENTRIES' in text:
            index_pages.append(text)
            data_pages.append(text)  # Index pages also have horse data
        else:
            data_pages.append(text)
    
    return index_pages, data_pages


def extract_race_info(index_pages: List[str]) -> Dict[int, Dict]:
    """Extract race metadata from index pages."""
    races = {}
    
    # Pattern: race number + track info + Beyer par
    # "1\nWoodbine ç Clm 25000(25-23.5)N3L 5 Furlongs (:56§) CLAIMING... Beyer par: 70"
    race_re = re.compile(
        r'(?ms)^\s*(\d+)\s*\n\s*Woodbine\b(.+?)(?:Beyer par[:\s]+(\d+|NA))?',
        re.MULTILINE
    )
    
    for page in index_pages:
        for m in race_re.finditer(page):
            race_num = int(m.group(1))
            header_block = m.group(2)
            par = int(m.group(3)) if m.group(3) and m.group(3).isdigit() else None
            
            races[race_num] = {
                'race_number': race_num,
                'header_block': header_block,
                'beyer_par': par,
            }
    
    return races


def infer_race_surface(header: str) -> str:
    t = header.lower()
    if ' turf' in t or ' fm ' in t or ' firm' in t:
        return 'turf'
    if 'tapeta' in t or 'synth' in t:
        return 'synthetic'
    return 'dirt'


def infer_race_class(header: str) -> str:
    h = header.lower()
    if re.search(r'\bG[123]\b', header):
        return 'GRADED'
    if 'stakes' in h or 'stk' in h or 'hcp' in h:
        return 'STK'
    if 'aoc' in h:
        return 'AOC'
    if ' oc ' in f' {h} ':
        return 'OC'
    if ' alw ' in f' {h} ':
        return 'ALW'
    if 'clm' in h or 'claiming' in h:
        return 'CLM'
    if 'md sp wt' in h:
        return 'MDSPW'
    if 'moc' in h:
        return 'MOC'
    if 'md' in h or 'maiden' in h:
        return 'MAIDEN'
    return 'UNKNOWN'


def extract_distance(header: str) -> str:
    m = re.search(r'(\d+)\s*(?:Furlongs?|furlongs?)', header, re.I)
    return m.group(0) if m else ''


# ─── HORSE PARSING ───────────────────────────────────────────────────────────

def parse_pp_beyer(line: str) -> Optional[int]:
    """Extract Beyer figure from PP record line.
    
    Pattern: "67=22" means Beyer=67, finish=22
    The Beyer is the digit(s) BEFORE the '='
    """
    matches = list(PP_BEYER_RE.finditer(line))
    for match in matches:
        beyer = int(match.group(1))
        finish = int(match.group(2))
        # Valid Beyer: 1-130, valid finish: 1-12
        if 1 <= beyer <= 130 and 1 <= finish <= 12:
            return beyer
    return None


def parse_pp_surface(line: str) -> Optional[str]:
    """Extract surface from PP line."""
    t = line.lower()
    if re.search(r'\bwo\s+(fst|fast|gd|good|sly|sloppy)\b', t):
        return 'dirt'
    if re.search(r'\bwo\s+fm\b', t):
        return 'turf'
    if re.search(r'\bwo\s+(tapeta|synth)\b', t):
        return 'synthetic'
    return None


def parse_horse_block(text: str, page_abs_start: int = 0) -> List[Dict]:
    """Parse all horse blocks from a page of text.
    
    page_abs_start: starting absolute position offset for this page.
    Each horse header: race_num\nPP-ML\nHorseName\nOwn:
    """
    horses = []
    abs_pos = page_abs_start - 1
    for m in HORSE_HEADER_RE.finditer(text):
        abs_pos += 1
        race_num = m.group(1)
        ml = f"{m.group(2)}-{m.group(3)}"
        horse_name = m.group(4).strip()
        block_start = m.start()
        
        # Find end of this horse block (next horse header or end)
        block_text = text[block_start:]
        next_m = list(HORSE_HEADER_RE.finditer(text[block_start + 1:]))
        if next_m:
            block_text = text[block_start:block_start + 1 + next_m[0].start()]
        
        horses.append({
            'race_num': race_num,
            'ml': ml,
            'horse_name': horse_name,
            'block_text': block_text,
            '_abs_pos': abs_pos,
        })
    
    return horses


def extract_connections(block: str) -> Dict[str, Optional[str]]:
    """Extract jockey and trainer from horse block."""
    jockey = None
    trainer = None
    
    # Trainer: "Tr: Palmer Kerron(>)"
    tr_m = re.search(r'Tr:\s*([A-Za-z][A-Za-z\s]+?)(?:\(|L|$)', block)
    if tr_m:
        trainer = tr_m.group(1).strip().rstrip(')')
    
    # Jockey: "MARAGH R R" - uppercase initials pattern before position
    jk_m = re.search(r'\b([A-Z][a-z]+\s+[A-Z]\.?)\s+(?:\(|L)', block)
    if jk_m:
        jockey = jk_m.group(1).strip()
    
    return {'jockey': jockey, 'trainer': trainer}


def extract_timeform_pace(block: str) -> Dict[str, Optional[int]]:
    """Extract TimeformUS Pace figures."""
    early_m = re.search(r'TimeformUS Pace[:\s]+Early[:\s]+(\d+)', block, re.I)
    late_m = re.search(r'TimeformUS Pace[:\s]+.*?Late[:\s]+(\d+)', block, re.I)
    return {
        'early': int(early_m.group(1)) if early_m else None,
        'late': int(late_m.group(1)) if late_m else None,
    }


def extract_beyer_profile(block: str) -> Dict:
    """Extract Beyer figures from all PP lines in block."""
    pps = []
    lines = block.split('\n')
    
    for line in lines:
        beyer = parse_pp_beyer(line)
        surface = parse_pp_surface(line)
        if beyer:
            pps.append({'beyer': beyer, 'surface': surface})
    
    if not pps:
        return {'pps': [], 'life_best': None, 'dirt_best': None, 'turf_best': None, 'synth_best': None}
    
    beyers = [p['beyer'] for p in pps]
    dirt = [p['beyer'] for p in pps if p['surface'] == 'dirt']
    turf = [p['beyer'] for p in pps if p['surface'] == 'turf']
    synth = [p['beyer'] for p in pps if p['surface'] == 'synthetic']
    
    return {
        'pps': pps,
        'life_best': max(beyers) if beyers else None,
        'dirt_best': max(dirt) if dirt else None,
        'turf_best': max(turf) if turf else None,
        'synth_best': max(synth) if synth else None,
    }


def summarize_horse(profile: Dict, par: Optional[int]) -> Dict:
    """Build Beyer summary for a horse."""
    pps = profile.get('pps', [])
    figures = [p['beyer'] for p in pps]
    
    if not figures:
        return {'last_beyer': None, 'best_last_3': None, 'avg_last_3': None, 
                'top_beyer': None, 'par_delta_last': None, 'trend': 'unknown'}
    
    last3 = figures[:3]
    last_beyer = figures[0]
    top_beyer = max(figures)
    avg_last_3 = round(sum(last3) / len(last3), 1)
    best_last_3 = max(last3)
    par_delta_last = (last_beyer - par) if par else None
    
    trend = 'mixed'
    if len(last3) >= 3 and last3[0] > last3[1] > last3[2]:
        trend = 'improving'
    elif len(last3) >= 3 and last3[0] < last3[1] < last3[2]:
        trend = 'declining'
    
    return {
        'last_beyer': last_beyer,
        'best_last_3': best_last_3,
        'avg_last_3': avg_last_3,
        'top_beyer': top_beyer,
        'par_delta_last': par_delta_last,
        'trend': trend,
    }


# ─── SCORING ────────────────────────────────────────────────────────────────

def score_pace_fit(pace: Dict, race_surface: str, race_distance: str) -> Tuple[float, str]:
    early, late = pace.get('early'), pace.get('late')
    
    if early is None and late is None:
        return 0.0, 'pace unknown'
    
    route = race_surface == 'turf' or any(x in race_distance.lower() for x in ['mile', '1 1/16', '1 1/8'])
    
    if route:
        if late and late >= 85:
            return 7.0, 'strong late kick'
        if late and late >= 70:
            return 3.5, 'usable late pace'
        if early and early >= 95 and late and late < 60:
            return -3.0, 'speed may fade late'
    else:
        if early and early >= 85:
            return 4.5, 'good tactical speed'
        if early and late and early >= 95 and late >= 60:
            return 2.5, 'speed and finish'
        if early and late and early < 55 and late < 60:
            return -4.0, 'pace disadvantaged'
    
    return 0.0, 'balanced pace'


def score_surface_fit(race_surface: str, profile: Dict, pps: List[Dict]) -> Tuple[float, str]:
    score = 0.0
    notes = []
    
    # Recent same-surface lines
    recent_same = [p for p in pps[:5] if p.get('surface') == race_surface]
    if recent_same:
        score += 1.5
        notes.append('recent same-surface experience')
    else:
        score -= 1.5
        notes.append('no recent same-surface line')
    
    # Profile surface fit
    best_key = f"{race_surface}_best"
    best = profile.get(best_key)
    life = profile.get('life_best')
    
    if best and life:
        ratio = best / max(life, 1)
        if ratio >= 0.95:
            score += 6.0
            notes.append('strong surface fit')
        elif ratio >= 0.85:
            score += 3.0
            notes.append('good surface fit')
        elif ratio <= 0.67:
            score -= 5.0
            notes.append('weak surface fit')
    
    return round(score, 2), '; '.join(notes)


def score_class_fit(race_class: str, pps: List[Dict]) -> Tuple[float, str]:
    if not pps:
        return 0.0, 'no class data'
    
    current = CLASS_WEIGHTS.get(race_class, 0)
    
    # Check last race class
    for p in pps[:3]:
        rc = p.get('race_class', '')
        if rc and rc != 'UNKNOWN':
            last_w = CLASS_WEIGHTS.get(rc, 0)
            if last_w > current:
                return 2.5, 'class relief'
            elif last_w < current:
                return -2.5, 'class rise'
            break
    
    return 0.0, 'class neutral'


# ─── MAIN PIPELINE ─────────────────────────────────────────────────────────

def analyze_horse(h: Dict, race: Dict) -> Dict:
    """Build full analysis for one horse."""
    block = h['block_text']
    
    profile = extract_beyer_profile(block)
    pps = profile['pps']
    summary = summarize_horse(profile, race.get('beyer_par'))
    connections = extract_connections(block)
    pace = extract_timeform_pace(block)
    
    # Base score
    base = 0.0
    reasons = []
    
    if summary['last_beyer'] is not None:
        base += summary['last_beyer'] * CONFIG['RECENCY_LAST_WEIGHT']
    if summary['avg_last_3'] is not None:
        base += summary['avg_last_3'] * CONFIG['RECENCY_AVG3_WEIGHT']
    if summary['par_delta_last'] is not None:
        base += summary['par_delta_last'] * CONFIG['PAR_DELTA_WEIGHT']
        reasons.append(f"par delta {summary['par_delta_last']:+}")
    
    if summary['trend'] == 'improving':
        base += CONFIG['TREND_IMPROVING_BONUS']
        reasons.append('improving Beyer trend')
    elif summary['trend'] == 'declining':
        base += CONFIG['TREND_DECLINING_PENALTY']
        reasons.append('declining Beyer trend')
    
    pace_adj, pace_note = score_pace_fit(pace, race['surface'], race.get('distance_text', ''))
    class_adj, class_note = score_class_fit(race['race_class'], pps)
    surface_adj, surface_note = score_surface_fit(race['surface'], profile, pps)
    
    reasons.extend([pace_note, class_note, surface_note])
    
    final_score = round(base + pace_adj + class_adj + surface_adj, 2)
    
    # Value flag
    value_flag = ''
    try:
        ml = h['ml']
        if '-' in ml:
            left, right = ml.split('-')[:2]
            odds_ratio = float(left) / float(right)
            if final_score >= 85 and odds_ratio >= 4:
                value_flag = 'value'
            elif final_score >= 95 and odds_ratio <= 2:
                value_flag = 'logical favorite'
    except Exception:
        pass
    
    return {
        'program_number': h['pp_num'],
        'horse_name': h['horse_name'],
        'morning_line': h['ml'],
        'jockey': connections.get('jockey'),
        'trainer': connections.get('trainer'),
        'timeform_pace': pace,
        'profile': profile,
        'beyer_summary': summary,
        'pace_adjustment': pace_adj,
        'class_adjustment': class_adj,
        'surface_adjustment': surface_adj,
        'analysis_score': final_score,
        'value_flag': value_flag,
        'reasons': reasons,
        'pps': pps,
    }


def build_race(race_num: int, horses_in_race: List[Dict], race_info: Dict) -> Dict:
    """Build a race dict from parsed horses."""
    race = race_info.copy()
    race['surface'] = infer_race_surface(race.get('header_block', ''))
    race['race_class'] = infer_race_class(race.get('header_block', ''))
    race['distance_text'] = extract_distance(race.get('header_block', ''))
    race['race_number'] = race_num
    
    analyzed = [analyze_horse(h, race) for h in horses_in_race]
    analyzed.sort(key=lambda x: x['analysis_score'], reverse=True)
    
    race['horses'] = analyzed
    race['top_3'] = analyzed[:3]
    return race


def analyze_drf_pdf(pdf_path: str) -> Dict:
    """Main entry point."""
    index_pages, data_pages = extract_pdf_text(pdf_path)
    race_info = extract_race_info(index_pages)
    
    # Collect ALL horses from ALL data pages with absolute position
    all_horses = []
    page_abs_start = 0
    for page_text in data_pages:
        horses = parse_horse_block(page_text, page_abs_start)
        for h in horses:
            all_horses.append(h)
        page_abs_start += len([m for m in HORSE_HEADER_RE.finditer(page_text)])
    
    # Group horses by race number, then sort by absolute position
    race_horses: Dict[int, List[Dict]] = {}
    for h in all_horses:
        rn = int(h['race_num'])
        if rn not in race_horses:
            race_horses[rn] = []
        race_horses[rn].append(h)
    
    # Build races with correct PP assignment (sequential within race by position)
    races = []
    for race_num in sorted(race_horses.keys()):
        horses_in_race = race_horses[race_num]
        # Sort by absolute position, assign PP sequentially
        horses_in_race.sort(key=lambda x: x.get('_abs_pos', 0))
        for pp_i, h in enumerate(horses_in_race, 1):
            h['pp_num'] = str(pp_i)
        
        info = race_info.get(race_num, {'race_number': race_num, 'beyer_par': None, 'header_block': ''})
        race = build_race(race_num, horses_in_race, info)
        races.append(race)
    
    races.sort(key=lambda x: x['race_number'])
    return {'races': races}


def render_telegram_summary(data: Dict) -> str:
    """Format for Telegram output."""
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
                f"E/L {tf.get('early','?')}/{tf.get('late','?')} | Pace {h['pace_adjustment']:+} | "
                f"Class {h['class_adjustment']:+} | Surface {h['surface_adjustment']:+}{flag}{conn}"
            )
            lines.append(f" Notes: {', '.join(h['reasons'][:4])}")
        parts.append('\n'.join(lines))
    return '\n\n'.join(parts) if parts else 'No races parsed.'


def validate(data: Dict) -> List[str]:
    """Check basic parse quality — races present, horses named, ML valid, Beyers extracted."""
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
            summary = h.get('beyer_summary', {})
            pps = h.get('pps', [])
            if not pps and summary.get('last_beyer') is None:
                issues.append(f"Race {rn} {name}: no Beyer history extracted")
    return issues


def validate_pars(data: Dict) -> List[str]:
    """Check that Beyers are reasonable relative to par."""
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
                issues.append(f"Race {race.get('race_number')}: top Beyer {top} is far above par {par}")
            if top < par - 35:
                issues.append(f"Race {race.get('race_number')}: top Beyer {top} is far below par {par}")
    return issues


if __name__ == '__main__':
    import sys
    if len(sys.argv) < 2:
        print('Usage: python drf_beyer_bot_wo.py <pdf_path>')
        sys.exit(1)
    
    result = analyze_drf_pdf(sys.argv[1])
    all_issues = validate(result) + validate_pars(result)
    if all_issues:
        print('⚠️ VALIDATION ISSUES:', ', '.join(all_issues))
    print(render_telegram_summary(result))
    print('\n--- JSON ---\n')
    print(json.dumps(result, indent=2))
