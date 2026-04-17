#!/usr/bin/env python3
"""
validate_drf_parse.py
Validates DRF parse output — missing races, blank names, bad ML, no Beyer history.
"""

import json, argparse, pathlib, sys

def validate(data: dict) -> list:
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
            import re
            if not re.fullmatch(r'[0-9]+(?:-[0-9]+(?:/[0-9]+)?)?', str(ml)):
                issues.append(f'Race {rn} {name}: unusual morning line {ml!r}')
            summary = h.get('beyer_summary', {})
            pps = h.get('pps', [])
            if not pps and summary.get('last_beyer') is None and summary.get('history_count', 0) == 0:
                issues.append(f'Race {rn} {name}: no Beyer history extracted')
    return issues


def validate_par(data: dict) -> list:
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


def main():
    if len(sys.argv) < 2:
        print('Usage: python validate_drf_parse.py <beyers.json>')
        sys.exit(1)
    path = pathlib.Path(sys.argv[1])
    data = json.loads(path.read_text(encoding='utf-8'))
    all_issues = validate(data) + validate_par(data)
    print(json.dumps({'issue_count': len(all_issues), 'issues': all_issues[:100]}, indent=2))
    return 0 if not all_issues else 2


if __name__ == '__main__':
    raise SystemExit(main())
