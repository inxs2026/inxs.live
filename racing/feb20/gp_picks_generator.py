#!/usr/bin/env python3
"""
Gulfstream Park Top 3 Picks - February 20, 2026
Automated DRF analysis following the 9-step methodology
"""

import re
from typing import List, Dict, Optional
from collections import defaultdict

SCRATCHES = {
    2: ['Vacationer'],
    4: ['Ontheblink'],
    5: ['Conquering King', 'Brigade Commander', 'Dreams of Myfather'],
    7: ['Win Runner'],
    8: ["Denver's Alley"],
    9: ['Las Olas', 'Navy Cross'],
    10: ['Orquidea Real']
}

def extract_beyers_from_pp(lines: List[str]) -> List[int]:
    """Extract Beyer speed figures from past performance lines"""
    beyers = []
    for line in lines:
        # Beyer appears at start of race line
        match = re.match(r'^\s*(\d{1,3})\s+\d+\s*/\s*\d+', line)
        if match:
            fig = int(match.group(1))
            if 20 <= fig <= 120:  # Valid Beyer range
                beyers.append(fig)
        # Also check for -0 (no Beyer)
        elif re.match(r'^\s*-0\s+\d+\s*/\s*\d+', line):
            continue  # Skip, no Beyer
    return beyers

def calc_beyer_avg(beyers: List[int]) -> float:
    """Calculate average of last 3 Beyers"""
    if not beyers:
        return 0.0
    last_three = beyers[:3]
    return round(sum(last_three) / len(last_three), 1)

def parse_race_data(content: str, race_num: int) -> Dict:
    """Parse horses from a race section"""
    lines = content.split('\n')
    
    horses = {}
    current_horse = None
    collecting_pp = False
    pp_lines = []
    
    for i, line in enumerate(lines):
        # Detect horse entry: pattern like "130 - 1 Travieso" or "4 Turbo Fire"
        match = re.match(r'^(\d{1,3})\s*-\s*(\d+)\s+([A-Z][A-Za-z\s\']+)', line)
        if not match:
            match = re.match(r'^(\d+)\s+([A-Z][A-Za-z\s\']+)$', line)
            if match and i > 0:
                # Likely continuation, check if previous line has odds
                pass
        
        if match:
            # Save previous horse if exists
            if current_horse and pp_lines:
                beyers = extract_beyers_from_pp(pp_lines)
                horses[current_horse] = {
                    'beyers': beyers,
                    'beyer_avg': calc_beyer_avg(beyers),
                    'pp_lines': pp_lines
                }
            
            # Start new horse
            current_horse = match.group(2 if len(match.groups()) == 2 else 3).strip()
            pp_lines = []
            collecting_pp = True
        
        # Collect past performance lines (start with Beyer or -0)
        elif collecting_pp and (re.match(r'^\s*\d{1,3}\s+\d+\s*/\s*\d+', line) or 
                               re.match(r'^\s*-0\s+\d+\s*/\s*\d+', line)):
            pp_lines.append(line)
        
        # Stop collecting when we hit WORKS or TRAINER
        elif collecting_pp and ('WORKS:' in line or 'TRAINER:' in line):
            collecting_pp = False
    
    # Save last horse
    if current_horse and pp_lines:
        beyers = extract_beyers_from_pp(pp_lines)
        horses[current_horse] = {
            'beyers': beyers,
            'beyer_avg': calc_beyer_avg(beyers),
            'pp_lines': pp_lines
        }
    
    return horses

def analyze_race(race_num: int, horses: Dict) -> List[Dict]:
    """Rank horses by Beyer average and form"""
    # Filter out scratches
    scratched = SCRATCHES.get(race_num, [])
    active_horses = {name: data for name, data in horses.items() 
                    if name not in scratched}
    
    # Rank by Beyer average
    ranked = sorted(active_horses.items(), 
                   key=lambda x: x[1]['beyer_avg'], 
                   reverse=True)
    
    return ranked

def main():
    # Read DRF file
    with open('/home/damato/.openclaw/workspace/racing/feb20/drf_extracted.txt', 'r') as f:
        content = f.read()
    
    # Split into race sections (simplified - would need better parsing)
    # For now, let's manually analyze key races with the data we have
    
    print("GULFSTREAM PARK - FRIDAY, FEBRUARY 20, 2026")
    print("=" * 70)
    print()
    
    # Test parsing on Race 1
    race1_start = content.find("1 MILE (1:33) MAIDEN CLAIMING")
    race2_start = content.find("1Â MILES (Turf). (1:38) MAIDEN CLAIMING")
    
    if race1_start >= 0 and race2_start > race1_start:
        race1_content = content[race1_start:race2_start]
        horses_r1 = parse_race_data(race1_content, 1)
        
        print("RACE 1 - Maiden Claiming $12,500, 1 Mile")
        print("-" * 70)
        for name, data in horses_r1.items():
            print(f"{name}: Beyer Avg = {data['beyer_avg']} (from {data['beyers'][:3]})")
        print()

if __name__ == '__main__':
    main()
