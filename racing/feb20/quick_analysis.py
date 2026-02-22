#!/usr/bin/env python3
"""Quick race-by-race analysis extraction"""

# Based on manual DRF review, compile all data systematically

races_data = {
    1: {  # Md Cl $12,500, 1M Dirt
        'horses': {
            'Lanum': {'beyers': [49], 'trainer': 'Pletcher 19%', 'jockey': 'Ortiz Jr 22%', 'notes': 'American Pharoah colt, MSW→MCL drop'},
            'Smash City': {'beyers': [49,50,36], 'notes': 'Best sustained figs'},
            'Turbo Fire': {'beyers': [49,26,54], 'notes': 'Inconsistent, one big race'},
            'Jeter': {'beyers': [25], 'trainer': 'Cox 26%', 'notes': '$300K Nyquist colt, MSW→MCL drop'},
            'Gigline': {'beyers': [24,41,31], 'notes': 'Lots of races, no win'},
            'It\'s the Stones': {'beyers': [], 'notes': 'First timer'},
            'Travieso': {'beyers': [25,37], 'notes': 'Slow figs'},
            'Roux Bucherro': {'beyers': [18,30], 'notes': 'Poor form'},
            'Holy Cow': {'beyers': [42,34,13], 'notes': 'Declining'},
            'Couches Burning': {'beyers': [], 'notes': 'First timer'}
        }
    },
    2: {  # Md Cl $35K, 1 1/8M Turf
        'scratched': ['Vacationer'],
        'horses': {
            'Rawayana': {'beyers': [53,60,52,59,50], 'notes': 'Adds blinkers, 55.0 avg last 3'},
            'Rudi': {'beyers': [55,56,48], 'notes': '53.0 avg, synthetic→turf'},
            'Fawcett': {'beyers': [], 'trainer': 'Walsh 18% debuts', 'notes': 'First timer, MCL debut angle'},
            'Win Street': {'beyers': [49,44,37], 'notes': '43.3 avg, Live Oak'},
            'Surfer\'s Joy': {'beyers': [32,30], 'notes': 'Poor figs'},
            'Lennie G': {'beyers': [26,43], 'trainer': 'Romans', 'notes': '34.5 avg'},
            'Unfair': {'beyers': [], 'notes': 'First timer'}
        }
    }
}

# Continue with races 3-10...
# (Would need to extract from DRF)

for race_num, data in races_data.items():
    print(f"\n=== RACE {race_num} ===")
    if 'scratched' in data:
        print(f"Scratched: {', '.join(data['scratched'])}")
    
    for horse, info in data['horses'].items():
        beyers = info['beyers']
        if beyers:
            last3 = beyers[:3]
            avg = round(sum(last3)/len(last3), 1) if last3 else 0
            print(f"{horse}: Beyer Avg {avg} from {beyers[:3]}")
        else:
            print(f"{horse}: First timer - {info.get('notes', '')}")
