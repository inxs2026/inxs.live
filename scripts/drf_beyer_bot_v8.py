#!/usr/bin/env python3
"""
drf_beyer_bot_v8.py
Gulfstream Park DRF parser — pdfplumber-based.
"""

import re
import json
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import List, Dict, Optional, Tuple

try:
    import pdfplumber
except Exception:
    pdfplumber = None

# ─── REGEXES ────────────────────────────────────────────────────────────────

RACE_HEADER_RE = re.compile(
    r'(?ms)^\s*(\d+)\s+Gulfstream Park\b(.*?)(?:Beyer\s*par\s+(\d+|NA))',
    re.I
)
HORSE_HEADER_RE = re.compile(r'(?m)^\s*(\d+)\s+([0-9]+-[0-9]+(?:\/[0-9]+)?|[0-9]+)\s+(.+)$')
SUMMARY_LINE_RE = re.compile(r'^(Life|20\d{2}|GP|D\.Fst|Wet\d*|Synth\d*|Turf\d*|Dst\d*)\b')
WORKS_OR_TRAINER_RE = re.compile(r'^(WORKS|TRAINER|Daily Racing Form|Copyright)')
TIMEFORM_HEADER_RE = re.compile(r'TimeformUS Pace\s+Early\s+(\d{1,3})\s+Late\s+(\d{1,3})', re.I)
PACE_STYLE_RE = re.compile(r'\b(EP|E/P|P|S|LP)\b')
NUM_TOKEN_RE = re.compile(r'(?<!\d)(\d{1,3})(?!\d)')
CLAIMING_PRICE_RE = re.compile(r'(?<!\d)(\d{4,6})(?!\d)')
DATE_OPEN_RE = re.compile(r'^\d{1,4}[A-Za-z-]*\s+[A-Z]{2,4}\b')
JOCKEY_RE = re.compile(r'\b[A-Z][A-Za-z\'\-]+\s+[A-Z](?:\s+[A-Z])?\s+L?\d{2,3}[a-z]*\b')
CLASS_RE = re.compile(
    r'\b(?:\d?Md(?:\s+Sp\s+Wt)?|Md|Moc|Clm|OC|Alw|Hcp|Stk|Stake|Claiming|Allowance)\b',
    re.I
)
JOCKEY_LINE_RE = re.compile(
    r'\b([A-Z][A-Za-z\'\-]+\s+[A-Z](?:\s+[A-Z])?)\s+(\d+)\s+\d+\s+\d+\s+\d+\s+\.\d+'
)
TRAINER_RE = re.compile(r'\bTr\s+([^\d]+?)(?=\d{1,4}\s+\d|\bL\b|\bLife\b|\bBlinkers\b|$)')
OWNER_SPLIT_RE = re.compile(r'\bOwn:?\b', re.I)

SURFACE_GROUPS = {
    'dirt': {'fst', 'fast', 'my', 'muddy', 'sly', 'sloppy', 'gd', 'good'},
    'turf': {'fm', 'firm', 'yl', 'yielding'},
    'synthetic': {'tapeta', 'synth', 'synthetic'},
}

CLASS_WEIGHTS = {
    'MDSPW': 10, 'MOC': 9, 'MAIDEN': 7, 'CLM': 4,
    'AOC': 12, 'OC': 11, 'ALW': 9, 'STK': 16,
    'GRADED': 20, 'UNKNOWN': 0,
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


@dataclass
class ScoringConfig:
    values: Dict[str, float]

    def __getitem__(self, key: str) -> float:
        return self.values[key]

    def get(self, key: str, default: float = 0.0) -> float:
        return self.values.get(key, default)


CONFIG = ScoringConfig(values=SCORING)


# ─── PDF / TEXT EXTRACTION ─────────────────────────────────────────────────

def extract_text_from_pdf(pdf_path: str) -> str:
    if pdfplumber is None:
        raise RuntimeError('pdfplumber not installed.')
    texts = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            texts.append(page.extract_text() or '')
    return '\n'.join(texts)


def normalize_text(text: str) -> str:
    text = text.replace('\r', '\n')
    text = text.replace('Beyer par:', 'Beyer par ')
    text = re.sub(r'\n{3,}', '\n\n', text)
    text = re.sub(r'[ \t]{2,}', ' ', text)
    return text


# ─── RACE / HORSE BLOCK PARSING ─────────────────────────────────────────

def infer_race_surface(race_text: str) -> str:
    head = ' '.join(race_text.splitlines()[:12]).lower()
    if ' turf' in head or 'turf.' in head or ' fm ' in head:
        return 'turf'
    if 'tapeta' in head or 'synth' in head or 'synthetic' in head:
        return 'synthetic'
    return 'dirt'


def extract_distance_text(race_text: str) -> str:
    head = ' '.join(race_text.splitlines()[:8])
    m = re.search(r'\b(\d+\s*(?:MILES?|miles?|f|F|1/16|1/8|1 1/16|1 1/8))\b', head)
    return m.group(1) if m else head


def infer_race_class(race_text: str) -> str:
    head = ' '.join(race_text.splitlines()[:12])
    h = head.lower()
    if re.search(r'\bG[123]\b', head):
        return 'GRADED'
    if 'stk' in h or 'stakes' in h or 'hcp' in h:
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


def find_race_sections(text: str) -> List[Dict]:
    matches = list(RACE_HEADER_RE.finditer(text))
    sections = []
    for i, m in enumerate(matches):
        start = m.start()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        par_raw = m.group(3)
        section_text = text[start:end]
        sections.append({
            'race_number': int(m.group(1)),
            'track_line': m.group(2).strip(),
            'beyer_par': int(par_raw) if str(par_raw).isdigit() else None,
            'surface': infer_race_surface(section_text),
            'race_class': infer_race_class(section_text),
            'distance_text': extract_distance_text(section_text),
            'text': section_text,
        })
    return sections


def _looks_like_horse_header(line: str) -> Optional[re.Match]:
    m = HORSE_HEADER_RE.match(line.strip())
    if not m:
        return None
    rest = m.group(3)
    if 'Own' in rest or 'TimeformUS Pace' in rest:
        return m
    return None


def split_horse_blocks(race_text: str) -> List[Dict]:
    lines = race_text.splitlines()
    starts = []
    for idx, line in enumerate(lines):
        m = _looks_like_horse_header(line)
        if m:
            starts.append((idx, m))

    horses = []
    for i, (idx, m) in enumerate(starts):
        end_idx = starts[i + 1][0] if i + 1 < len(starts) else len(lines)
        block_lines = lines[idx:end_idx]
        full_header = block_lines[0].strip()
        rest = m.group(3).strip()
        owner_split = OWNER_SPLIT_RE.split(rest, maxsplit=1)
        horse_name = owner_split[0].strip()
        horses.append({
            'program_number': m.group(1).strip(),
            'morning_line': m.group(2).strip(),
            'horse_name': horse_name,
            'header_line': full_header,
            'text': '\n'.join(block_lines),
        })
    return horses


# ─── PP LINE PARSING ────────────────────────────────────────────────────

def extract_timeform_pace(horse_text: str) -> Dict[str, Optional[int]]:
    early = late = None
    style = None
    m = TIMEFORM_HEADER_RE.search(horse_text)
    if m:
        early, late = int(m.group(1)), int(m.group(2))
    style_m = PACE_STYLE_RE.search(horse_text)
    if style_m:
        style = style_m.group(1).upper()
    return {'early': early, 'late': late, 'style': style}


def extract_connections(horse_text: str, header_line: str) -> Dict[str, Optional[str]]:
    jockey = None
    trainer = None
    jm = JOCKEY_LINE_RE.search(header_line)
    if jm:
        jockey = jm.group(1).strip()
    tm = TRAINER_RE.search(horse_text)
    if tm:
        trainer = tm.group(1).strip()
    return {'jockey': jockey, 'trainer': trainer}


def extract_profile_beyers(horse_text: str, pps: Optional[List[Dict]] = None) -> Dict:
    out = {
        'life_best': None, 'dirt_best': None, 'wet_best': None,
        'synth_best': None, 'turf_best': None, 'dst_best': None, 'line_top': None,
    }
    for line in horse_text.splitlines():
        s = line.strip()
        if not s:
            continue
        if s.startswith('Life '):
            vals = [int(x) for x in NUM_TOKEN_RE.findall(s) if 0 <= int(x) <= 130]
            if vals:
                out['life_best'] = max(vals)
        elif s.startswith('D.Fst'):
            vals = [int(x) for x in NUM_TOKEN_RE.findall(s) if 0 <= int(x) <= 130]
            if vals:
                out['dirt_best'] = max(vals)
        elif s.startswith('Wet'):
            vals = [int(x) for x in NUM_TOKEN_RE.findall(s) if 0 <= int(x) <= 130]
            if vals:
                out['wet_best'] = max(vals)
        elif s.startswith('Synth'):
            vals = [int(x) for x in NUM_TOKEN_RE.findall(s) if 0 <= int(x) <= 130]
            if vals:
                out['synth_best'] = max(vals)
        elif s.startswith('Turf'):
            vals = [int(x) for x in NUM_TOKEN_RE.findall(s) if 0 <= int(x) <= 130]
            if vals:
                out['turf_best'] = max(vals)
        elif s.startswith('Dst'):
            vals = [int(x) for x in NUM_TOKEN_RE.findall(s) if 0 <= int(x) <= 130]
            if vals:
                out['dst_best'] = max(vals)

    if pps:
        beyers = [p['beyer'] for p in pps if isinstance(p.get('beyer'), int)]
        if beyers:
            out['line_top'] = max(beyers)
        if out['life_best'] is None or out['line_top'] > out['life_best']:
            out['life_best'] = out['line_top']
        dirt = [p['beyer'] for p in pps if p.get('surface') == 'dirt' and isinstance(p.get('beyer'), int)]
        turf = [p['beyer'] for p in pps if p.get('surface') == 'turf' and isinstance(p.get('beyer'), int)]
        synth = [p['beyer'] for p in pps if p.get('surface') == 'synthetic' and isinstance(p.get('beyer'), int)]
        if dirt:
            out['dirt_best'] = max([v for v in [out['dirt_best'], max(dirt)] if v is not None])
        if turf:
            out['turf_best'] = max([v for v in [out['turf_best'], max(turf)] if v is not None])
        if synth:
            out['synth_best'] = max([v for v in [out['synth_best'], max(synth)] if v is not None])
    return out


def extract_pp_lines(horse_text: str) -> List[str]:
    lines = []
    for raw in horse_text.splitlines():
        line = raw.strip()
        if not line:
            continue
        if WORKS_OR_TRAINER_RE.search(line):
            break
        if SUMMARY_LINE_RE.match(line):
            continue
        if line.startswith(('TimeformUS Pace', 'Own ', 'Own:', 'Sire ', 'Sire:', 'Dam', 'Br ', 'Br:', 'Tr ', 'Tr:')):
            continue
        if DATE_OPEN_RE.match(line):
            lines.append(line)
    return lines


def parse_track(line: str) -> Optional[str]:
    m = re.search(r'\b\d{1,4}[A-Za-z-]*\s+([A-Z]{2,4})\b', line)
    return m.group(1) if m else None


def parse_surface(line: str) -> Optional[str]:
    tokens = set(re.findall(r'[A-Za-z]+', line.lower()))
    for surface, aliases in SURFACE_GROUPS.items():
        if aliases & tokens:
            return surface
    return None


def parse_race_class_from_line(line: str) -> str:
    l = line.lower()
    if re.search(r'\bG[123]\b', line):
        return 'GRADED'
    if 'stk' in l or 'stakes' in l or 'hcp' in l:
        return 'STK'
    if 'aoc' in l:
        return 'AOC'
    if ' oc ' in f' {l} ':
        return 'OC'
    if ' alw ' in f' {l} ':
        return 'ALW'
    if 'clm' in l:
        return 'CLM'
    if 'md sp wt' in l:
        return 'MDSPW'
    if 'moc' in l:
        return 'MOC'
    if 'md' in l or 'mdn' in l:
        return 'MAIDEN'
    return 'UNKNOWN'


def parse_claiming_level(line: str) -> Optional[int]:
    l = line.lower()
    if 'clm' not in l and 'claim' not in l and 'md ' not in l and 'moc' not in l:
        return None
    nums = [int(x) for x in CLAIMING_PRICE_RE.findall(line)]
    plausible = [n for n in nums if 5000 <= n <= 500000]
    return plausible[0] if plausible else None


def normalize_fused_numbers(text: str) -> str:
    text = re.sub(r'(\d{5})(\d{2}-\d{2})', r'\1 \2', text)
    text = re.sub(r'\b(\d{2})(\d{3})(?=\s+\d?Md\b)', r'\1 \2', text)
    text = re.sub(r'\b(\d{2})(\d{3})(\d{3})(?=\s+Md\b)', r'\1 \2 \3', text)
    text = re.sub(r'(\b\d{4,6})(\d{2}-\d{2}\b)', r'\1 \2', text)
    return text


def trim_to_pre_jockey(text: str) -> str:
    m = JOCKEY_RE.search(text)
    return text[:m.start()].strip() if m else text


def after_class_tokens(text: str) -> List[str]:
    m = CLASS_RE.search(text)
    if not m:
        return []
    return text[m.end():].strip().split()


def is_purse_token(tok: str) -> bool:
    return bool(re.fullmatch(r'\d{4,6}|\d{2,3}k|\d{2,3}-\d{2,3}', tok, re.I))


def is_pos_token(tok: str) -> bool:
    return bool(re.fullmatch(r'\d{1,2}', tok)) and 1 <= int(tok) <= 12


def _cut_comment_tail(line: str) -> str:
    parts = re.split(r'(?<=[A-Za-z])\s{1,}[A-Z][a-z]', line, maxsplit=1)
    if len(parts) > 1:
        return parts[0].strip()
    return line


def parse_beyer_from_line(line: str) -> Optional[int]:
    text = normalize_fused_numbers(line)
    text = trim_to_pre_jockey(text)
    toks = after_class_tokens(text)
    if not toks:
        return None
    toks = [t for t in toks if not re.fullmatch(r'\d{1,2}[/-]\d{1,2}', t)]
    i = 0
    while i < len(toks) and is_purse_token(toks[i]):
        i += 1
    toks = toks[i:]
    if not toks:
        return None
    for idx, tok in enumerate(toks):
        if not re.fullmatch(r'\d{1,3}', tok):
            continue
        val = int(tok)
        if not (0 <= val <= 110):
            continue
        following = toks[idx+1:idx+8]
        pos_count = sum(1 for x in following if is_pos_token(x))
        if pos_count >= 3:
            return val
    for tok in toks:
        if re.fullmatch(r'\d{1,3}', tok):
            val = int(tok)
            if 0 <= val <= 110:
                return val
    return None


def parse_pp_record(line: str) -> Dict:
    return {
        'date_token': line.split()[0] if line.split() else '',
        'track': parse_track(line),
        'surface': parse_surface(line),
        'race_class': parse_race_class_from_line(line),
        'claiming_level': parse_claiming_level(line),
        'beyer': parse_beyer_from_line(line),
        'raw_line': line,
    }


# ─── SCORING ─────────────────────────────────────────────────────────────

def is_route_context(race_surface: str, race_distance_text: str) -> bool:
    t = race_distance_text.lower()
    return race_surface == 'turf' or any(x in t for x in ['1 mile', '1 1/16', '1 1/8', '1 miles', 'mile'])


def score_pace_fit(pace: Dict, race_surface: str, race_distance_text: str = '') -> Tuple[float, str]:
    early, late, style = pace.get('early'), pace.get('late'), pace.get('style')
    if early is None or late is None:
        if style in {'EP', 'E/P'}:
            return 1.0, 'pace style only: tactical speed'
        if style == 'LP':
            return 1.0, 'pace style only: late runner'
        return CONFIG['PACE_MISSING'], 'pace unknown'

    score = 0.0
    notes = []
    route = is_route_context(race_surface, race_distance_text)

    if route:
        if late >= 85:
            score += CONFIG['PACE_ROUTE_LATE_ELITE']
            notes.append('strong late kick')
        elif late >= 70:
            score += CONFIG['PACE_ROUTE_LATE_GOOD']
            notes.append('usable late pace')
        if early >= 95 and late < 60:
            score += CONFIG['PACE_ROUTE_SPEED_FADE_RISK']
            notes.append('speed may fade late')
    else:
        if early >= 85:
            score += CONFIG['PACE_SPRINT_EARLY_GOOD']
            notes.append('good tactical speed')
        if early >= 95 and late >= 60:
            score += CONFIG['PACE_SPRINT_EARLY_ELITE']
            notes.append('speed and finish')
        if early < 55 and late < 60:
            score += CONFIG['PACE_SPRINT_LOW_ENERGY']
            notes.append('pace disadvantaged')

    if not notes:
        notes.append('balanced pace')
    return round(score, 2), '; '.join(notes)


def surface_switch_penalty(race_surface: str, profile: Dict) -> float:
    dirt = profile.get('dirt_best')
    turf = profile.get('turf_best')
    synth = profile.get('synth_best')

    if race_surface == 'dirt' and dirt is None:
        if turf is not None and synth is None:
            return CONFIG['SURFACE_UNKNOWN_DIRT_TURF_PENALTY']
        if synth is not None:
            return CONFIG['SURFACE_UNKNOWN_SYNTH_SWITCH_PENALTY']
    if race_surface == 'turf' and turf is None:
        if dirt is not None and synth is None:
            return CONFIG['SURFACE_UNKNOWN_DIRT_TURF_PENALTY']
        if synth is not None:
            return CONFIG['SURFACE_UNKNOWN_SYNTH_SWITCH_PENALTY']
    if race_surface == 'synthetic' and synth is None:
        if dirt is not None or turf is not None:
            return CONFIG['SURFACE_UNKNOWN_SYNTH_SWITCH_PENALTY']
    return 0.0


def score_surface_fit(race_surface: str, profile: Dict, pps: List[Dict]) -> Tuple[float, str]:
    specific = {
        'dirt': profile.get('dirt_best'),
        'turf': profile.get('turf_best'),
        'synthetic': profile.get('synth_best'),
    }.get(race_surface)
    top = profile.get('life_best') or profile.get('line_top') or 0
    recent_same = [p['beyer'] for p in pps[:5] if p.get('surface') == race_surface and isinstance(p.get('beyer'), int)]

    score = 0.0
    notes = []

    if specific is not None and top:
        ratio = specific / max(top, 1)
        if ratio >= CONFIG['SURFACE_SPECIFIC_EXCELLENT_RATIO']:
            score += CONFIG['SURFACE_MATCH_EXCELLENT_BONUS']
            notes.append('strong surface fit')
        elif ratio >= CONFIG['SURFACE_SPECIFIC_GOOD_RATIO']:
            score += CONFIG['SURFACE_MATCH_GOOD_BONUS']
            notes.append('good surface fit')
        elif ratio <= CONFIG['SURFACE_SPECIFIC_POOR_RATIO']:
            score += CONFIG['SURFACE_MATCH_POOR_PENALTY']
            notes.append('weak surface fit')
        else:
            notes.append('surface fit neutral')
    else:
        pen = surface_switch_penalty(race_surface, profile)
        score += pen
        notes.append('surface evidence missing' if pen == 0 else 'surface switch penalty')

    if recent_same:
        score += CONFIG['SURFACE_RECENT_MATCH_BONUS']
        notes.append('recent same-surface experience')
    else:
        score += CONFIG['SURFACE_RECENT_MISS_PENALTY']
        notes.append('no recent same-surface line')

    return round(score, 2), '; '.join(notes)


def score_class_fit(current_class: str, current_par: Optional[int], pps: List[Dict]) -> Tuple[float, str]:
    recent = [p for p in pps[:5] if isinstance(p.get('beyer'), int)]
    if not recent:
        return 0.0, 'no class data'

    score = 0.0
    notes = []
    avg_recent = sum(p['beyer'] for p in recent) / len(recent)
    top_recent = max(p['beyer'] for p in recent)

    if current_par is not None:
        if top_recent >= current_par + 5:
            score += CONFIG['CLASS_TOP_OVER_PAR_BONUS']
            notes.append('back class over par')
        elif avg_recent >= current_par:
            score += CONFIG['CLASS_AVG_AT_PAR_BONUS']
            notes.append('class competitive')
        elif avg_recent <= current_par - 10:
            score += CONFIG['CLASS_AVG_WELL_BELOW_PAR_PENALTY']
            notes.append('below par class')
        else:
            notes.append('class neutral')
    else:
        notes.append('no par available')

    current_weight = CLASS_WEIGHTS.get(current_class, 0)
    last_class = recent[0].get('race_class', 'UNKNOWN')
    last_weight = CLASS_WEIGHTS.get(last_class, 0)

    if last_weight > current_weight:
        score += CONFIG['CLASS_LAST_HIGHER_THAN_TODAY_BONUS']
        notes.append('class relief')
    elif last_weight < current_weight:
        score += CONFIG['CLASS_LAST_LOWER_THAN_TODAY_PENALTY']
        notes.append('class rise')
    else:
        notes.append('same class level')

    return round(score, 2), '; '.join(notes)


def summarize_horse(pps: List[Dict], beyer_par: Optional[int]) -> Dict:
    figures = [p['beyer'] for p in pps if isinstance(p.get('beyer'), int)]
    if not figures:
        return {
            'last_beyer': None, 'best_last_3': None, 'avg_last_3': None,
            'top_beyer': None, 'par_delta_last': None, 'trend': 'unknown',
        }

    last3 = figures[:3]
    last_beyer = figures[0]
    top_beyer = max(figures)
    avg_last_3 = round(sum(last3) / len(last3), 1)
    best_last_3 = max(last3)
    par_delta_last = (last_beyer - beyer_par) if beyer_par is not None else None

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


def build_horse_analysis(hb: Dict, race: Dict) -> Dict:
    horse_text = hb['text']
    pp_lines = extract_pp_lines(horse_text)
    pps = [parse_pp_record(line) for line in pp_lines]
    pace = extract_timeform_pace(horse_text)
    profile = extract_profile_beyers(horse_text, pps)
    summary = summarize_horse(pps, race['beyer_par'])
    connections = extract_connections(horse_text, hb['header_line'])

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
    class_adj, class_note = score_class_fit(race['race_class'], race['beyer_par'], pps)
    surface_adj, surface_note = score_surface_fit(race['surface'], profile, pps)
    reasons.extend([pace_note, class_note, surface_note])

    final_score = round((base or 0) + (pace_adj or 0) + (class_adj or 0) + (surface_adj or 0), 2)

    value_flag = ''
    ml = hb['morning_line']
    try:
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
        'program_number': hb['program_number'],
        'horse_name': hb['horse_name'],
        'morning_line': hb['morning_line'],
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


# ─── VALIDATORS ────────────────────────────────────────────────────────────

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
            pps = h.get('pps', [])
            if not pps and h.get('beyer_summary', {}).get('last_beyer') is None:
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


# ─── ANALYZE ─────────────────────────────────────────────────────────────

def analyze_drf_text(text: str) -> Dict:
    text = normalize_text(text)
    races = []
    for race in find_race_sections(text):
        horses = [build_horse_analysis(hb, race) for hb in split_horse_blocks(race['text'])]
        horses.sort(key=lambda x: x['analysis_score'], reverse=True)
        races.append({
            'race_number': race['race_number'],
            'beyer_par': race['beyer_par'],
            'surface': race['surface'],
            'race_class': race['race_class'],
            'distance_text': race.get('distance_text', ''),
            'horses': horses,
            'top_3': horses[:3],
        })
    return {'races': races, 'scoring_constants': CONFIG.values}


def analyze_drf_pdf(pdf_path: str) -> Dict:
    return analyze_drf_text(extract_text_from_pdf(pdf_path))


# ─── RENDER ──────────────────────────────────────────────────────────────

def render_telegram_summary(data: Dict) -> str:
    parts = []
    for race in data.get('races', []):
        lines = [f"🏇 Race {race['race_number']} | Par {race['beyer_par']} | {race['surface']} | {race['race_class']}"]
        for i, h in enumerate(race.get('top_3', []), 1):
            s = h['beyer_summary']
            tf = h['timeform_pace']
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


def handle_drf_input(file_bytes: bytes = None, text_input: str = None) -> str:
    if text_input:
        return render_telegram_summary(analyze_drf_text(text_input))
    if file_bytes:
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp:
            tmp.write(file_bytes)
            path = tmp.name
            return render_telegram_summary(analyze_drf_pdf(path))
    return 'No DRF input provided.'


if __name__ == '__main__':
    import sys
    if len(sys.argv) < 2:
        print('Usage: python drf_beyer_bot_v8.py <drf.pdf or textfile.txt>')
        sys.exit(1)
    path = Path(sys.argv[1])
    if path.suffix.lower() == '.pdf':
        result = analyze_drf_pdf(str(path))
    else:
        result = analyze_drf_text(path.read_text(encoding='utf-8', errors='ignore'))
    issues = validate(result) + validate_pars(result)
    if issues:
        print('⚠️ VALIDATION ISSUES:', ', '.join(issues), '\n')
    print(render_telegram_summary(result))
    print('\n--- JSON ---\n')
    print(json.dumps(result, indent=2))
