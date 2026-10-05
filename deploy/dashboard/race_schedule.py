"""Approved race dates; unknown calendars never imply a non-racing day."""
import json
from pathlib import Path
from datetime import date
CALENDAR = Path(__file__).with_name('woodbine-calendar.json')

def build(target, has_card=False):
    selected = date.fromisoformat(target)
    result = dict(scheduled=None, nextRaceDate=None, source=None, asOf=None, sourceURL=None)
    try:
        data = json.loads(CALENDAR.read_text())
        dates = sorted(set(data['dates']))
        if len(dates) != 128 or any(date.fromisoformat(d).year != data['year'] for d in dates):
            raise ValueError('Invalid approved calendar')
        if selected.year == data['year']:
            result.update(scheduled=target in dates, nextRaceDate=next((d for d in dates if d > target), None),
                          source=data['source'], asOf=data['asOf'], sourceURL=data['sourceURL'])
    except (OSError, ValueError, KeyError, TypeError):
        pass
    # Real saved card evidence must not be hidden by a stale calendar.
    if has_card and result['scheduled'] is not True:
        result.update(scheduled=True, source='Saved race card', asOf=None, sourceURL=None)
    return result
