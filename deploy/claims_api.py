"""Serve only the last complete Woodbine claims snapshot; no write side effects."""
from datetime import datetime, timezone
from decimal import Decimal
import json
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path.home() / '.local/state/inxs-dashboard/claims'


def read_report():
    year = datetime.now(ZoneInfo('America/Toronto')).year
    path = ROOT / 'reports' / f'woodbine-claims-{year}-year-to-date.json'
    data = json.loads(path.read_text(encoding='utf-8'))
    if (data.get('year') != year or data.get('track') != 'Woodbine'
            or data.get('complete') is not True or data.get('missing_dates') or data.get('errors')):
        raise ValueError('Claims snapshot is not a verified current-year report')
    claims = data.get('claims')
    if not isinstance(claims, list) or data.get('total_claims') != len(claims):
        raise ValueError('Claims count mismatch')
    total = sum((Decimal(c['claim_price_cad']) for c in claims), Decimal(0))
    if total != Decimal(data['total_claim_value_cad']):
        raise ValueError('Claims total mismatch')
    if data.get('daily', {}).get('date') != data.get('coverage_through'):
        raise ValueError('Daily claims date mismatch')
    try:
        status = json.loads((ROOT / 'refresh-status.json').read_text(encoding='utf-8'))
    except (OSError, ValueError):
        status = {}
    checked = status.get('last_success_at') or data.get('checked_at')
    # Off-days are expected. Compare the successful check to the most recent
    # scheduled update, not a fixed age that would flag Monday-Wednesday stale.
    from datetime import timedelta
    now = datetime.now(ZoneInfo('America/Toronto'))
    scheduled = []
    for ago in range(8):
        day = now.date() - timedelta(days=ago)
        if day.weekday() not in (3, 4, 5, 6):
            continue
        for hour in range(15, 25):
            tick = datetime.combine(day, datetime.min.time(), ZoneInfo('America/Toronto')) + timedelta(hours=hour)
            if tick <= now - timedelta(minutes=20):
                scheduled.append(tick)
    latest_due = max(scheduled) if scheduled else None
    try:
        overdue = latest_due is not None and datetime.fromisoformat(checked) < latest_due
    except (TypeError, ValueError):
        overdue = True
    data['refresh'] = dict(
        last_checked_at=checked, last_attempt_at=status.get('last_attempt_at'),
        schedule='Hourly Thursday-Sunday, 3 pm through midnight (Toronto)',
        stale=bool(status.get('error')) or overdue,
        error='Latest refresh could not be verified; showing the last complete report.' if status.get('error') else None)
    return data
