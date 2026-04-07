#!/usr/bin/env python3
"""
DRF PDF Parser - Gulfstream Park
Usage: python3 parse_drf.py <pdf_path>

Reliable approach:
1. Parse INDEX TO ENTRIES for horse->race mapping
2. Use "Post time:" lines to find race section boundaries
3. Within each race section, find each horse's Beyer figures directly
"""

import sys, re, subprocess, os

def extract_text(pdf_path):
    result = subprocess.run(['pdftotext', pdf_path, '-'], capture_output=True, text=True)
    return result.stdout

def parse_index(lines):
    """Return {horse_name: race_num} from INDEX TO ENTRIES."""
    horse_race = {}
    in_index = False
    for line in lines:
        s = line.strip()
        if 'INDEX TO ENTRIES' in s:
            in_index = True; continue
        if 'INDEX TO TRAINERS' in s:
            break
        if not in_index:
            continue
        m = re.match(r'^(.+?)\s*,\s*(\d+)$', s)
        if m:
            name = m.group(1).strip()
            race = int(m.group(2))
            if len(name) > 1:
                horse_race[name] = race
    return horse_race

def get_race_sections(lines):
    """Return list of (race_num, start_line, end_line) using Post time: markers."""
    posts = []
    for i, line in enumerate(lines):
        if 'Post time:' in line:
            posts.append(i)
    # Assign race numbers sequentially
    sections = []
    for idx, start in enumerate(posts):
        end = posts[idx+1] if idx+1 < len(posts) else len(lines)
        sections.append((idx+1, start, end))
    return sections

def parse_race_section(lines, start, end, horses_in_race):
    """Extract Beyers, PP, trainer for each horse within a race section."""
    block = lines[start:end]
    results = {}

    for horse in horses_in_race:
        results[horse] = {'pp': '?', 'trainer': '', 'jockey': '', 'beyers': [], 'comments': []}

    # Scan block for horse-specific data
    # Track which horse we're currently reading
    current_horse = None
    horse_names_lower = {h.lower(): h for h in horses_in_race}

    i = 0
    while i < len(block):
        s = block[i].strip()

        # Check if this line IS a horse name (exact match)
        if s.lower() in horse_names_lower:
            current_horse = horse_names_lower[s.lower()]
            i += 1
            continue

        # Check for "PP ML - ML HorseName" format e.g. "615 - 1 More Applause"
        m = re.match(r'^(\d{1,2})(\d+)\s*-\s*\d+\s+(.+)$', s)
        if m:
            pp = int(m.group(1))
            name_part = m.group(3).strip()
            for h in horses_in_race:
                if name_part.lower().startswith(h.lower()[:8]) or h.lower().startswith(name_part.lower()[:8]):
                    if 1 <= pp <= 14:
                        results[h]['pp'] = pp
                        current_horse = h
                    break

        # Check for "PP HorseName" format e.g. "2 Too Loose La Trek" or "3 Honor Her"
        m2 = re.match(r'^(\d{1,2})\s+([A-Z][A-Za-z0-9\s\'\(\)\*\-\.]+)$', s)
        if m2:
            pp = int(m2.group(1))
            name_part = m2.group(2).strip()
            if 1 <= pp <= 14:
                for h in horses_in_race:
                    if (name_part.lower() == h.lower() or
                        name_part.lower().startswith(h.lower()[:10]) or
                        h.lower().startswith(name_part.lower()[:10])):
                        results[h]['pp'] = pp
                        current_horse = h
                        break

        if current_horse is None:
            i += 1
            continue

        # Trainer
        if 'Tr:' in s and not results[current_horse]['trainer']:
            tm = re.search(r'Tr:\s*([A-Za-z][A-Za-z\s]+?)(?:\(|\d{2})', s)
            if tm:
                results[current_horse]['trainer'] = tm.group(1).strip()

        # Jockey
        if (re.match(r'^[A-Z][A-Z ]+[A-Z]\s+\(\d', s) and
            not results[current_horse]['jockey']):
            results[current_horse]['jockey'] = s.split('(')[0].strip()

        # Beyer figures
        for b, q in re.findall(r'\b([3-9][0-9]|1[0-1][0-9])=(\d{2})\b', s):
            results[current_horse]['beyers'].append(int(b))

        # Comments
        if re.search(r'\b(no factor|tired|weakened|no rally|drew clear|driving|gamely|'
                     r'one-paced|flattened|empty|outrun|trailed|off slow|'
                     r'bumped|checked|wide|pace|closed|rallied|bid|duel|'
                     r'no menace|no threat|fell back|gave way|lugged|bore)\b',
                     s, re.IGNORECASE):
            if 10 < len(s) < 100:
                results[current_horse]['comments'].append(s)

        i += 1

    # Clean up beyers
    for horse in results:
        seen, clean = set(), []
        for b in results[horse]['beyers']:
            if b not in seen and 30 <= b <= 119:
                seen.add(b); clean.append(b)
        results[horse]['beyers'] = clean[:5]

    return results

def beyer_str(beyers):
    b = beyers
    if len(b) >= 3:
        return f"Avg(3): {sum(b[:3])/3:.1f}  {b}"
    elif len(b) == 2:
        return f"Avg(2): {sum(b)/2:.1f}  {b}"
    elif len(b) == 1:
        return f"Only:   {b[0]}     {b}"
    return "DEBUT  []"

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 parse_drf.py <pdf_path>"); sys.exit(1)
    pdf_path = sys.argv[1]
    if not os.path.exists(pdf_path):
        print(f"Not found: {pdf_path}"); sys.exit(1)

    lines = extract_text(pdf_path).split('\n')
    print(f"Lines: {len(lines)}\n")

    horse_race = parse_index(lines)
    print(f"Index: {len(horse_race)} horses across races {sorted(set(horse_race.values()))}\n")

    sections = get_race_sections(lines)
    print(f"Race sections found: {len(sections)}\n")

    # Group horses by race
    races = {}
    for horse, rnum in horse_race.items():
        races.setdefault(rnum, []).append(horse)

    # Parse each race section
    for rnum, start, end in sections:
        horses_in_race = races.get(rnum, [])
        if not horses_in_race:
            continue

        race_data = parse_race_section(lines, start, end, horses_in_race)

        print(f"{'='*72}")
        print(f"  RACE {rnum}  —  {len(horses_in_race)} horses")
        print(f"{'='*72}")

        def sort_key(h):
            pp = race_data[h]['pp']
            return pp if isinstance(pp, int) else 99

        for horse in sorted(horses_in_race, key=sort_key):
            d = race_data[horse]
            pp = d['pp']
            tr = f"  [{d['trainer']}]" if d['trainer'] else ""
            print(f"  #{str(pp):>2}  {horse:<35} {beyer_str(d['beyers'])}{tr}")
        print()

if __name__ == '__main__':
    main()
