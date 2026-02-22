#!/usr/bin/env python3
import re
from collections import defaultdict

# Read the extracted text
with open('gulfstream_feb19_extracted.txt', 'r', encoding='utf-8', errors='ignore') as f:
    content = f.read()

# Find race boundaries
race_markers = []
for match in re.finditer(r'Post time: (\d+:\d+ ET)', content):
    race_markers.append(match.start())

print(f"Found {len(race_markers)} races\n")

# Extract each race
for i, start_pos in enumerate(race_markers, 1):
    end_pos = race_markers[i] if i < len(race_markers) else len(content)
    race_text = content[start_pos:end_pos]
    
    # Extract race number and details
    race_lines = race_text.split('\n')[:15]
    
    print(f"=" * 80)
    print(f"RACE {i}")
    print(f"=" * 80)
    
    # Find race conditions
    for line in race_lines:
        if 'MILE' in line or 'Furlong' in line or 'FURLONGS' in line:
            print(f"Distance/Conditions: {line.strip()}")
            break
    
    # Find purse
    for line in race_lines:
        if 'Purse $' in line:
            print(f"Purse: {line.strip()[:100]}")
            break
    
    # Find race type
    for line in race_lines:
        if any(x in line for x in ['MAIDEN', 'CLAIMING', 'ALLOWANCE', 'STAKES', 'çMd', 'çCl', 'çAlw', 'çOC']):
            if 'Purse' not in line and len(line.strip()) > 5:
                print(f"Type: {line.strip()[:100]}")
                break
    
    # Count horses in field
    horse_count = race_text.count('\nOwn:')
    print(f"Field Size: {horse_count} horses")
    print()

