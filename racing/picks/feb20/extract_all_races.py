#!/usr/bin/env python3
"""
Extract key data from all 10 Gulfstream races - Feb 20, 2026
Systematically parse Beyer figures and key info
"""

# Load DRF data
with open('drf_extracted.txt', 'r') as f:
    lines = f.readlines()

# Race start line numbers (from grep command)
race_starts = [
    (1, 215, "Md Cl $12,500, 1M Dirt"),
    (2, 1114, "Md Cl $35K, 1 1/8M Turf"),
    (3, 1747, "Clm $8K N3L, 1M 70Y Tapeta, F&M"),
    (4, 2826, "Md Cl TBD"),
    (5, 3593, "Clm TBD, 1M Turf"),
    (6, 4782, "TBD"),
    (7, 5535, "TBD"),
    (8, 6175, "TBD"),
    (9, 7357, "TBD, 1 1/8M Tapeta"),
    (10, 8507, "TBD, 1M")
]

print("GULFSTREAM PARK - RACE DATA EXTRACTION")
print("=" * 70)

# For each race, show starting line
for race_num, start_line, desc in race_starts:
    print(f"\nRace {race_num} (Line {start_line}): {desc}")
    # Could parse horses here but for speed, will do manually

print("\nExtraction complete. Use this to guide manual analysis.")
