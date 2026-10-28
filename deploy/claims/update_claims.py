#!/usr/bin/env python3
"""Refresh claims and record success without replacing complete data on failure."""
from datetime import datetime, timezone
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path.home() / '.local/state/inxs-dashboard/claims'
STATUS = ROOT / 'refresh-status.json'


def write_status(data):
    ROOT.mkdir(parents=True, exist_ok=True)
    temp = STATUS.with_suffix('.tmp')
    temp.write_text(json.dumps(data, indent=2) + '\n', encoding='utf-8')
    temp.replace(STATUS)


def main():
    try:
        status = json.loads(STATUS.read_text(encoding='utf-8'))
    except (OSError, ValueError):
        status = {}
    status['last_attempt_at'] = datetime.now(timezone.utc).isoformat()
    status['running'] = True
    write_status(status)
    code = 1
    try:
        result = subprocess.run([sys.executable, str(Path(__file__).with_name('woodbine_claims_year.py')),
            '--cache-dir', str(ROOT / 'cache'), '--output-dir', str(ROOT / 'reports')],
            capture_output=True, text=True, timeout=900)
        code = result.returncode
        if result.stdout:
            print(result.stdout.strip())
        if result.stderr:
            print(result.stderr.strip(), file=sys.stderr)
    except (OSError, subprocess.TimeoutExpired) as error:
        print(type(error).__name__, file=sys.stderr)
    status['running'] = False
    status['error'] = code != 0
    if code == 0:
        status['last_success_at'] = datetime.now(timezone.utc).isoformat()
    write_status(status)
    return code


if __name__ == '__main__':
    raise SystemExit(main())
