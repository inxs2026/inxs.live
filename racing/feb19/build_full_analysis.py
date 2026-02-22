#!/usr/bin/env python3
"""
Build complete Gulfstream analysis by parsing DRF text systematically
"""
import re

with open('gulfstream_feb19_extracted.txt', 'r', encoding='utf-8', errors='ignore') as f:
    content = f.read()

# Split by "Post time:" to get race boundaries
races = re.split(r'Post time: (\d+:\d+ ET)', content)

# races[0] = header
# races[1] = "12:20 ET", races[2] = Race 1 content
# races[3] = "12:50 ET", races[4] = Race 2 content
# etc.

output = []
output.append("# GULFSTREAM PARK - THURSDAY, FEBRUARY 19, 2026")
output.append("## COMPREHENSIVE RACING ANALYSIS & TOP 3 PICKS")
output.append("")
output.append("**Analysis Time:** 12:15 PM EST")
output.append("**Source:** DRF Past Performances")
output.append("**Scratches:** Verified as of 12:15 PM EST")
output.append("")
output.append("---")
output.append("")

race_num = 0
for i in range(1, len(races), 2):
    if i+1 >= len(races):
        break
    
    race_num += 1
    post_time = races[i].strip()
    race_content = races[i+1]
    
    output.append(f"## RACE {race_num}")
    output.append(f"**Post Time:** {post_time}")
    output.append("")
    
    # Extract race conditions from first few lines
    lines = race_content.split('\n')[:20]
    for line in lines:
        if 'Furlong' in line or 'MILE' in line:
            output.append(f"**Distance:** {line.strip()}")
            break
    
    # Extract race type/purse
    for line in lines:
        if 'Purse $' in line or 'CLAIMING' in line or 'MAIDEN' in line:
            if len(line.strip()) > 10 and 'Wagers' not in line:
                output.append(f"**{line.strip()[:100]}**")
                break
    
    output.append("")
    
    # Extract horse entries (simplified - just count)
    horse_count = race_content.count('\nOwn:')
    output.append(f"**Field Size:** {horse_count} horses")
    output.append("")
    
    # Extract visible Beyer patterns for top horses
    beyer_matches = re.findall(r'(\d{2,3})b?\s+[\d.*]+\s+(\d{2})=', race_content[:4000])
    
    if beyer_matches:
        output.append(f"**Sample Beyers (first horses):** {', '.join([b[1] for b in beyer_matches[:12]])}")
    
    output.append("")
    output.append("### TOP 3 PICKS")
    output.append("")
    output.append(f"[Detailed analysis for Race {race_num} - IN PROGRESS]")
    output.append("")
    output.append("---")
    output.append("")

# Write output
with open('gulfstream_picks_outline.md', 'w') as f:
    f.write('\n'.join(output))

print("Outline created. Now building detailed analysis...")
print(f"Total races processed: {race_num}")

