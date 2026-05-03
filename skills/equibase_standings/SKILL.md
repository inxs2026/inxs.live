# Equibase Standings Skill — Charlie's Edition

Pull jockey, trainer, and owner standings from Equibase meet pages and generate formatted PDF reports.

**Built:** May 3, 2026 | **Location:** `skills/equibase_standings/` | **Owner:** Charlie

---

## At a Glance

| What | Command | Output |
|------|---------|--------|
| Console standings | `python3 skills/equibase_standings/equibase_crawl.py --track WO --type trainer` | Formatted table to stdout |
| Single trainer lookup | Use `format_single_trainer()` in code | One trainer's full stats |
| PDF report | `python3 skills/equibase_standings/equibase_pdf.py --track WO` | `standings/WO_standings_YYYYMMDD.pdf` |

---

## Console Crawler — `equibase_crawl.py`

### Purpose
Pull the full Equibase standings table (or top N) for any track and type.

### Shell Usage
```bash
# Basic — WO trainers, top 25
python3 skills/equibase_standings/equibase_crawl.py --track WO --type trainer

# GP jockeys, top 10
python3 skills/equibase_standings/equibase_crawl.py --track GP --type jockey --top 10

# WO owners, save JSON
python3 skills/equibase_standings/equibase_crawl.py --track WO --type owner --output /tmp/wo_owner.json

# Debug visible browser (if Imperva blocking)
python3 skills/equibase_standings/equibase_crawl.py --track WO --type trainer --visible
```

### Python Usage (import)
```python
from skills.equibase_standings.equibase_crawl import get_standings, format_standings

# Fetch all 88 WO trainers
entries = get_standings("WO", "trainer", year=2026)

# Format as console table
text = format_standings("WO", "trainer", entries)
print(text)

# Look up a specific trainer
from skills.equibase_standings.equibase_crawl import format_single_trainer
print(format_single_trainer(entries, "Katryan"))
```

### Arguments
| Arg | Default | Description |
|-----|---------|-------------|
| `--track` | `WO` | Track code (see Track Codes below) |
| `--type` | `trainer` | Data type: `trainer`, `jockey`, `owner` |
| `--year` | `2026` | 4-digit year |
| `--top` | `25` | Number of entries in console output (max: 100) |
| `--output` | _(none)_ | Write JSON to this path (authoritative data) |
| `--visible` | _(false)_ | Show browser window for debugging |

### Console Output Format
```
🏇 WOODBINE — TRAINER STANDINGS  (as of 05/03/2026)
─────────────────────────────────────────────────────────────
Rk   Name                        St     St     1st   Win%   Earnings
─────────────────────────────────────────────────────────────
1    Mark E. Casse               24     --     5     21%    $254,649
2    Kevin Attard                10     --     2     20%    $120,485
...
─────────────────────────────────────────────────────────────
Total entries: 88
```
- Emoji differs by type: 🏇 trainer | 🧢 jockey | 💰 owner
- Trainer table shows an extra `St` (starters) column; jockey/owner omit it

### JSON Output Format
When `--output` is specified, writes:
```json
{
  "track": "WOODBINE",
  "type": "trainer",
  "year": 2026,
  "as_of": "05/03/2026",
  "entries": [
    {
      "rank": "1", "name": "Mark E. Casse", "starts": "24",
      "starters": "--", "first": "5", "second": "2", "third": "3",
      "earnings": "$254,649", "win_pct": "21%", "wps_pct": "42%",
      "per_start": "$10,610", "wps_per_start": "0.42"
    }
  ]
}
```
JSON is authoritative. Console table is for human reading only.

### Single Trainer Lookup
```python
from skills.equibase_standings.equibase_crawl import format_single_trainer

text = format_single_trainer(entries, "Abraham Katryan")
```
Output:
```
🏇 Abraham R. Katryan — WOODBINE Trainer Standings 2026

  Rank      #45
  Starts   4
  1st       0
  2nd       1
  3rd       1
  Win%      0%
  WPS%      50%
  Earnings  $6,489
```

---

## PDF Generator — `equibase_pdf.py`

### Purpose
Build a formatted landscape PDF combining trainer/jockey/owner standings for a single track. Suitable for sharing via email or Telegram.

### Shell Usage
```bash
# All 3 types, Woodbine (default)
python3 skills/equibase_standings/equibase_pdf.py --track WO

# Gulfstream, trainers only
python3 skills/equibase_standings/equibase_pdf.py --track GP --types trainer

# Trainer + jockey, specific year
python3 skills/equibase_standings/equibase_pdf.py --track WO --types trainer jockey --year 2025

# Custom output path
python3 skills/equibase_standings/equibase_pdf.py --track WO --output /path/to/my_report.pdf
```

### Python Usage (import)
```python
from skills.equibase_standings.equibase_pdf import build_pdf, fetch_standings

# Fetch data
trainers = fetch_standings("WO", "trainer")
jockeys = fetch_standings("WO", "jockey")
owners = fetch_standings("WO", "owner")

# Build PDF
build_pdf(
    track_code="WO",
    track_name="WOODBINE",
    location="Toronto, Ontario",
    data_by_type={'trainer': trainers, 'jockey': jockeys, 'owner': owners},
    output_path="standings/WO_standings_20260503.pdf"
)
```

### Arguments
| Arg | Default | Description |
|-----|---------|-------------|
| `--track` | `WO` | Track code (see Track Codes below) |
| `--types` | `trainer jockey owner` | Space-separated types to include |
| `--year` | `2026` | 4-digit year |
| `--output` | _(auto)_ | `standings/{TRACK}_standings_{YYYYMMDD}.pdf` |

### PDF Output Location
```
standings/{TRACK}_standings_{YYYYMMDD}.pdf
e.g.  standings/WO_standings_20260503.pdf
```

### PDF Design
- **Size:** Landscape Letter (11 × 8.5 in)
- **Colors:** WO = navy `#1a3a5c` | GP = forest green `#1a4a2e` | Other = gray
- **Structure:** One section per data type (trainer / jockey / owner)
- **Rows:** Top 25 entries per section, alternating white/light-gray shading
- **Footer:** "Data © Equibase Company LLC | Generated {date} by Charlie"

---

## Track Codes

| Code | Track Name | Location |
|------|-----------|----------|
| `WO` | Woodbine | Toronto, Ontario |
| `GP` | Gulfstream Park | Hallandale Beach, FL |
| `CD` | Churchill Downs | Louisville, KY |
| `SA` | Santa Anita Park | Arcadia, CA |
| `DMR` | Del Mar | Del Mar, CA |
| `BEL` | Belmont Park | Elmont, NY |
| `SAR` | Saratoga | Saratoga Springs, NY |
| `KEE` | Keeneland | Lexington, KY |
| `AQU` | Aqueduct | Queens, NY |
| `TAM` | Tampa Bay Downs | Tampa, FL |
| `OP` | Oaklawn Park | Hot Springs, AR |
| `GG` | Golden Gate Fields | Berkeley, CA |

---

## Data Types

| Type | Code | Extra Columns | Emoji |
|------|------|--------------|-------|
| Trainer standings | `trainer` | Starters | 🏇 |
| Jockey standings | `jockey` | — | 🧢 |
| Owner standings | `owner` | — | 💰 |

---

## Output Fields (all data types)

| Field | Description |
|-------|-------------|
| `rank` | Numeric rank |
| `name` | Full name |
| `starts` | Total race starts |
| `starters` | Number of starters (trainer only; `--` for jockey/owner) |
| `first` | Wins (1st place) |
| `second` | Seconds (2nd place) |
| `third` | Thirds (3rd place) |
| `earnings` | Total purse earnings (e.g. `$254,649`) |
| `win_pct` | Win percentage (e.g. `21%`) |
| `wps_pct` | Win-place-show percentage (e.g. `42%`) |
| `per_start` | Earnings per start |
| `wps_per_start` | WPS per start |

---

## Dependencies

Underlies both scripts — calls Hermes venv Python:
```
~/.hermes/hermes-agent/venv/bin/python /home/damato/equibase_standings_crawler.py
~/.hermes/hermes-agent/venv/bin/python /home/damato/generate_standings_pdf.py
```

Hermes venv already has: `playwright`, `reportlab`

---

## How It Works

1. **Launch Playwright** → navigates to `equibase.com/stats/View.cfm`
2. **Select track** → dropdown `selAvailTracks`
3. **Select meet year** → dropdown `selAvailRaceMeets` (matches `04/{YY}` pattern)
4. **Wait for Imperva** → anti-bot interstitial (up to 45s)
5. **Extract table** → header-indexed lookup (different column sets for trainer/jockey/owner)
6. **Return data** → JSON (authoritative) + formatted console output

---

## Troubleshooting

| Problem | Likely Cause | Fix |
|---------|-------------|-----|
| Imperva interstitial never clears | Anti-bot triggered | Wait 5 min, re-run with `--visible` |
| 0 entries extracted | DOM change or Imperva block | Check Equibase manually; re-run |
| Module not found | Wrong Python | Use Hermes venv path (default in scripts) |
| PDF build fails | Missing data or reportlab error | Check stderr; try `--types trainer` only |
| Stale JSON | Previous run's file left in /tmp | Always use fresh output path or `--output` |

---

## Files

```
skills/equibase_standings/
├── SKILL.md              ← skill definition
├── equibase_crawl.py    ← console crawler + formatting
└── equibase_pdf.py      ← PDF generator

workspace/
└── standings/           ← auto-generated PDF output directory
    └── WO_standings_20260503.pdf
```
