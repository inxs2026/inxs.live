#!/usr/bin/env python3
"""
Racing Picks Pre-Check — tests EVERYTHING before the 11:45 AM cron fires.
Exits 0 if all clear, 1 if any check fails.
Prints a summary of pass/fail for each check.
"""
import os, sys, smtplib, socket, subprocess, glob, datetime
from pathlib import Path

WORKSPACE = Path.home() / ".openclaw/workspace"
TODAY = datetime.date.today()
MONTH = TODAY.strftime("%b%d").lower()       # e.g. "feb22"
YEAR  = TODAY.strftime("%Y-%m-%d")
PICKS_DIR = WORKSPACE / "racing/picks" / MONTH

TELEGRAM_TARGET = "1626341499"

failures = []
warnings = []

def ok(msg):    print(f"  ✅ {msg}")
def fail(msg):  print(f"  ❌ {msg}"); failures.append(msg)
def warn(msg):  print(f"  ⚠️  {msg}"); warnings.append(msg)

def alert_carlo(message):
    """Send alert to Carlo via Telegram."""
    subprocess.run([
        "openclaw", "message", "send",
        "--channel", "telegram",
        "--target", TELEGRAM_TARGET,
        "--message", message
    ], capture_output=True)


print(f"\n🏇 Racing Pre-Check — {TODAY.strftime('%A, %B %-d, %Y')}")
print("=" * 55)

# ── CHECK 1: Today's picks folder exists
print("\n[1] Picks folder")
if PICKS_DIR.exists():
    ok(f"Folder exists: racing/picks/{MONTH}/")
else:
    fail(f"Picks folder missing: racing/picks/{MONTH}/ — DRF not yet placed")

# ── CHECK 2: DRF PDF exists and is substantial
print("\n[2] DRF PDF file")
pdf_files = list(PICKS_DIR.glob("gulfstream_*.pdf")) if PICKS_DIR.exists() else []
if not pdf_files:
    fail(f"No DRF PDF found in racing/picks/{MONTH}/")
else:
    pdf = pdf_files[0]
    size_kb = pdf.stat().st_size / 1024
    if size_kb < 100:
        fail(f"DRF PDF suspiciously small ({size_kb:.0f} KB) — may be corrupt: {pdf.name}")
    else:
        ok(f"DRF PDF: {pdf.name} ({size_kb:.0f} KB)")

# ── CHECK 3: DRF TXT file exists and has content
print("\n[3] DRF TXT file")
txt_files = list(PICKS_DIR.glob("gulfstream_*.txt")) if PICKS_DIR.exists() else []
if not txt_files:
    warn(f"No DRF TXT found — PDF reader will be used directly")
else:
    txt = txt_files[0]
    lines = len(txt.read_text(errors='ignore').splitlines())
    if lines < 500:
        fail(f"DRF TXT too short ({lines} lines) — may be incomplete: {txt.name}")
    else:
        ok(f"DRF TXT: {txt.name} ({lines:,} lines)")

# ── CHECK 4: Methodology file exists and has content
print("\n[4] Methodology file")
meth = WORKSPACE / "racing/methodology/TOP-3-PICKS-METHODOLOGY.md"
if not meth.exists():
    fail("TOP-3-PICKS-METHODOLOGY.md missing from racing/methodology/")
else:
    size = meth.stat().st_size
    if size < 1000:
        fail(f"Methodology file suspiciously small ({size} bytes)")
    else:
        ok(f"TOP-3-PICKS-METHODOLOGY.md ({size:,} bytes)")

# ── CHECK 5: Email script exists
print("\n[5] Email script")
email_script = WORKSPACE / "scripts/send_email_pdf.py"
if not email_script.exists():
    fail("scripts/send_email_pdf.py missing")
else:
    ok("scripts/send_email_pdf.py found")

# ── CHECK 6: md_to_pdf.py exists and has dependencies
print("\n[6] PDF converter")
pdf_converter = WORKSPACE / "scripts/md_to_pdf.py"
if not pdf_converter.exists():
    fail("scripts/md_to_pdf.py missing")
else:
    ok("scripts/md_to_pdf.py found")
    # Test reportlab import
    result = subprocess.run(
        [sys.executable, "-c", "import reportlab, markdown2; print('ok')"],
        capture_output=True, text=True
    )
    if "ok" in result.stdout:
        ok("reportlab + markdown2 available")
    else:
        warn("reportlab/markdown2 not installed — md_to_pdf.py will auto-install on first run")

# ── CHECK 7: Gmail SMTP connectivity (actual test)
print("\n[7] Gmail SMTP connection")
FROM_EMAIL   = "charliethebot1@gmail.com"
APP_PASSWORD = "mbxaezedvcxcjopi"
try:
    server = smtplib.SMTP("smtp.gmail.com", 587, timeout=10)
    server.starttls()
    server.login(FROM_EMAIL, APP_PASSWORD)
    server.quit()
    ok("Gmail SMTP login successful")
except smtplib.SMTPAuthenticationError:
    fail("Gmail SMTP auth failed — app password may be expired or revoked")
except (socket.timeout, ConnectionRefusedError, OSError) as e:
    fail(f"Gmail SMTP unreachable: {e}")
except Exception as e:
    fail(f"Gmail SMTP error: {e}")

# ── CHECK 8: Equibase scraper (primary scratches) + TrackData MCP (backup)
print("\n[8] Equibase scraper (primary scratches)")
scraper = WORKSPACE / "scripts/equibase_scraper.py"
venv_python = Path.home() / "scraping_env/bin/python3"
equibase_ok = False
if not scraper.exists():
    fail("scripts/equibase_scraper.py missing")
elif not venv_python.exists():
    fail("scraping_env not found — run: python3 -m venv ~/scraping_env && ~/scraping_env/bin/pip install 'scrapling[all]'")
else:
    result = subprocess.run(
        [str(venv_python), str(scraper)],
        capture_output=True, text=True, timeout=60,
        cwd=str(WORKSPACE)
    )
    if result.returncode == 0 and "Done!" in result.stdout:
        import re
        m = re.search(r'(\d+) scratches', result.stdout)
        count = m.group(1) if m else "0"
        ok(f"Equibase scraper ran — {count} scratch(es), entries + scratches.txt saved")
        equibase_ok = True
    else:
        warn(f"Equibase scraper failed — trying TrackData MCP as backup")

if not equibase_ok:
    print("\n[8b] TrackData MCP (backup scratches)")
    result = subprocess.run(
        ["mcporter", "call", "trackdata.get_scratches"],
        capture_output=True, text=True, timeout=15
    )
    if result.returncode == 0:
        try:
            import json
            data = json.loads(result.stdout)
            count = data.get("count", 0)
            ok(f"TrackData MCP live — {count} scratch(es) so far today")
        except Exception:
            ok("TrackData MCP reachable (could not parse response)")
    else:
        fail("Both Equibase scraper AND TrackData MCP failed — scratches unknown!")

# ── CHECK 9: No stale picks already exist for today
print("\n[9] Stale picks check")
stale = list(PICKS_DIR.glob("*picks*.md")) if PICKS_DIR.exists() else []
stale += list(PICKS_DIR.glob("*picks*.pdf")) if PICKS_DIR.exists() else []
if stale:
    warn(f"{len(stale)} picks file(s) already exist from earlier run: {[f.name for f in stale]}")
else:
    ok("No stale picks files")

# ── RESULT ──────────────────────────────────────────────────────────────────
print("\n" + "=" * 55)
if not failures:
    print(f"✅ ALL CHECKS PASSED — Ready for 11:45 AM picks")
    if warnings:
        for w in warnings:
            print(f"   ⚠️  {w}")
    sys.exit(0)
else:
    msg_lines = [f"🚨 Racing Pre-Check FAILED — {TODAY.strftime('%b %-d')}"]
    for f in failures:
        msg_lines.append(f"❌ {f}")
    if warnings:
        for w in warnings:
            msg_lines.append(f"⚠️ {w}")
    msg_lines.append("Picks cron will still run at 11:45 AM — manual fix needed NOW.")
    full_msg = "\n".join(msg_lines)
    print(full_msg)
    alert_carlo(full_msg)
    sys.exit(1)
