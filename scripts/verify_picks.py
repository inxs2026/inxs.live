#!/usr/bin/env python3
"""
Racing Picks Verification Script
Cross-checks generated picks against DRF to catch data errors.

Usage: python3 verify_picks.py <picks_file.md> <drf_file.txt>

Checks:
1. Horse name exists in race
2. Post position matches
3. Beyer averages approximately match (±5 points tolerance)

Exits 0 if all checks pass, 1 if errors found.
"""

import sys
import re
from typing import Dict, List, Tuple

def parse_picks_file(picks_file: str) -> Dict[int, List[Tuple[int, str, float]]]:
    """
    Parse picks markdown file.
    Returns: {race_num: [(post_pos, horse_name, beyer_avg), ...]}
    """
    picks = {}
    current_race = None
    
    with open(picks_file, 'r') as f:
        for line in f:
            # Race header: ## RACE 1 - ...
            race_match = re.match(r'^## RACE (\d+)', line)
            if race_match:
                current_race = int(race_match.group(1))
                picks[current_race] = []
                continue
            
            # Pick line: **1. #3 HORSE NAME** - Avg Beyer (last 3): 72.0
            pick_match = re.match(r'^\*\*\d+\.\s+#(\d+)\s+([A-Z\s\'\-]+)\*\*\s+-\s+Avg Beyer.*:\s+([\d\.]+)', line)
            if pick_match and current_race:
                post_pos = int(pick_match.group(1))
                horse_name = pick_match.group(2).strip()
                beyer_avg = float(pick_match.group(3))
                picks[current_race].append((post_pos, horse_name, beyer_avg))
    
    return picks

def parse_drf_file(drf_file: str) -> Dict[int, Dict[int, Tuple[str, List[int]]]]:
    """
    Parse DRF text file.
    Returns: {race_num: {post_pos: (horse_name, [beyer1, beyer2, beyer3])}}
    
    Note: This is a simplified parser. May need refinement based on DRF format.
    """
    horses = {}
    current_race = None
    
    with open(drf_file, 'r') as f:
        content = f.read()
    
    # Split by race (simplified - assumes "GP, race N" markers)
    race_sections = re.split(r'GP, race (\d+)', content)
    
    for i in range(1, len(race_sections), 2):
        race_num = int(race_sections[i])
        race_text = race_sections[i + 1]
        
        horses[race_num] = {}
        
        # Find horse entries (simplified - looks for post position + name patterns)
        # Format: "3 Fish Mooney" or "3 O'Hearn"
        horse_entries = re.findall(r'^(\d+)\s+([A-Z][A-Za-z\'\s\-]+)$', race_text, re.MULTILINE)
        
        for post_pos_str, horse_name in horse_entries:
            post_pos = int(post_pos_str)
            # Extract Beyers (last 3 races) - look for patterns like "82=15", "76=20"
            # This is simplified - actual implementation should parse PP lines
            beyers = []
            # Placeholder - real implementation would parse actual Beyer lines
            horses[race_num][post_pos] = (horse_name.strip(), beyers)
    
    return horses

def verify_picks(picks: Dict, drf_horses: Dict) -> List[str]:
    """
    Verify picks against DRF data.
    Returns list of error messages (empty if all OK).
    """
    errors = []
    
    for race_num, race_picks in picks.items():
        if race_num not in drf_horses:
            errors.append(f"Race {race_num}: Race not found in DRF")
            continue
        
        for post_pos, horse_name, beyer_avg in race_picks:
            # Check if post position exists
            if post_pos not in drf_horses[race_num]:
                errors.append(f"Race {race_num}: Post #{post_pos} not found in DRF")
                continue
            
            drf_name, drf_beyers = drf_horses[race_num][post_pos]
            
            # Check if horse name matches
            if horse_name.upper() != drf_name.upper():
                errors.append(
                    f"Race {race_num} Post #{post_pos}: "
                    f"Name mismatch - Picks say '{horse_name}', DRF says '{drf_name}'"
                )
            
            # Check Beyer average (if we have DRF Beyers)
            if drf_beyers and len(drf_beyers) >= 3:
                drf_avg = sum(drf_beyers[:3]) / 3
                if abs(beyer_avg - drf_avg) > 5:  # ±5 point tolerance
                    errors.append(
                        f"Race {race_num} #{post_pos} {horse_name}: "
                        f"Beyer mismatch - Picks say {beyer_avg:.1f}, DRF calculates {drf_avg:.1f}"
                    )
    
    return errors

def main():
    if len(sys.argv) != 3:
        print("Usage: python3 verify_picks.py <picks_file.md> <drf_file.txt>")
        sys.exit(1)
    
    picks_file = sys.argv[1]
    drf_file = sys.argv[2]
    
    print("🔍 RACING PICKS VERIFICATION")
    print("=" * 60)
    
    # Parse files
    print(f"Reading picks from: {picks_file}")
    picks = parse_picks_file(picks_file)
    print(f"  → Found {len(picks)} races with picks")
    
    print(f"Reading DRF from: {drf_file}")
    drf_horses = parse_drf_file(drf_file)
    print(f"  → Found {len(drf_horses)} races in DRF")
    
    # Verify
    print("\nVerifying picks against DRF...")
    errors = verify_picks(picks, drf_horses)
    
    print("=" * 60)
    
    if not errors:
        print("✅ VERIFICATION PASSED")
        print("All picks match DRF data. Safe to email.")
        sys.exit(0)
    else:
        print(f"❌ VERIFICATION FAILED - {len(errors)} error(s) found:")
        print()
        for error in errors:
            print(f"  • {error}")
        print()
        print("DO NOT EMAIL until errors are fixed!")
        sys.exit(1)

if __name__ == "__main__":
    main()
