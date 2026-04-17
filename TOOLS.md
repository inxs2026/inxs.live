# TOOLS.md - Local Notes

Skills define _how_ tools work. This file is for _your_ specifics — the stuff that's unique to your setup.

## What Goes Here

Things like:

- Camera names and locations
- SSH hosts and aliases
- Preferred voices for TTS
- Speaker/room names
- Device nicknames
- Anything environment-specific

## Examples

```markdown
### Cameras

- living-room → Main area, 180° wide angle
- front-door → Entrance, motion-triggered

### SSH

- home-server → 192.168.1.100, user: admin
- umbrel-pi → 10.0.0.45, user: umbrel (credentials in config/pi_ssh.env)
  - Connects via: `sshpass -p 'damatopi' ssh -o StrictHostKeyChecking=no umbrel@10.0.0.45`
  - Full sudo access (passwordless sudo enabled Apr 7, 2026)

### TTS

- Preferred voice: "Nova" (warm, slightly British)
- Default speaker: Kitchen HomePod
```

## Why Separate?

Skills are shared. Your setup is yours. Keeping them apart means you can update skills without losing your notes, and share skills without leaking your infrastructure.

---

## 🏇 Horse Racing Analysis - Mandatory Files

When Carlo asks for race analysis, ALWAYS reference these files FIRST:

### **TOP 3 PICKS** (Betting Analysis)
- **File:** [[TOP-3-PICKS-METHODOLOGY.md]] ⭐ **OFFICIAL PROCESS**
- **When:** Analyzing races for betting picks
- **Process:**
  1. Calculate Beyer averages (last 3) for ALL contenders
  2. Analyze form, class, trainer/jockey angles, pace
  3. Rank by MOST positive factors
  4. Write 2-3 sentence explanation per pick
- **Rule:** "In Beyers We Trust" - Numbers + form, not hunches
- **System working well - follow it exactly!**

### **CLAIMING PROSPECTS** (Horses to Buy)
- **File:** [[racing/methodology/CLAIMING-PROSPECTS-CRITERIA.md]]  
- **When:** Identifying horses worth claiming (buying out of race)
- **Key:** Soundness FIRST (workout/race patterns), NOT purchase price!
- **Critical:** Claiming prospects ≠ betting picks

**RULE:** Read the appropriate methodology file BEFORE starting any racing analysis.

---

---

## 🌐 Web Projects

### inxs.live — Tools & Services Landing Page
- **Repo:** https://github.com/inxs2026/inxs.live.git
- **Hosting:** Vercel (auto-deploys on push to `main`)
- **Local files:** `tools/inxs-live/`
- **Stack:** Plain HTML/CSS/JS, no frameworks
- **Live tool:** PDF to Word → `pdf.inxs.live`
- **Future tools:** add as subdomains, add card to tools grid in `index.html`

### PDF to Word Converter
- **Repo:** https://github.com/inxs2026/PDFtoWord.git
- **Local files:** `tools/pdf2docx-web/`
- **Running:** systemd service `pdf2docx` on port 5050
- **Local URL:** http://10.0.0.49:5050
- **Public URL:** pdf.inxs.live (point subdomain to server)
- **Stack:** Flask + pdf2docx library

---

## 📦 Installed Libraries & Tools

### lucide-static (SVG Icons)
- **Installed:** `workspace/node_modules/lucide-static/`
- **Version:** ^0.577.0 (see `workspace/package.json`)
- **Usage:** Drop SVG icons inline — `node_modules/lucide-static/icons/<name>.svg`
- **Sprite:** `node_modules/lucide-static/sprite.svg`
- **When to use:** Any web project needing clean, consistent icons — no CDN needed

### pdf2docx (Python)
- **Installed:** system-wide (`--break-system-packages`)
- **Usage:** `python3 scripts/pdf_to_docx.py <input.pdf> [output.docx]`
- **Script:** `scripts/pdf_to_docx.py`

### Flask (Python)
- **Installed:** system-wide
- **Usage:** Web apps/APIs (used by PDF converter)

---

## 🔑 API Keys & Tokens

### GitHub PAT
- **Token file:** `config/github_token.txt` (chmod 600)
- **Scope:** repo
- **Accounts:** inxs2026
- **Usage:** `git remote set-url origin https://$(cat config/github_token.txt)@github.com/...`

---

## TTS (Text-to-Speech)

- **Provider:** Edge TTS (Microsoft neural voices, no API key needed)
- **Voice:** en-US-AvaNeural (Expressive, Caring, Pleasant, Friendly)
- **Voice rule:** When Carlo sends a voice note → reply in voice (Ava)
- **Note:** Matches Charlie's warm, empathetic female personality
- **Changed:** Apr 15, 2026 - switched from JennyNeural to AvaNeural (Carlo's pick)

---

## PDF Parsing

### Horse Vet/Expense Tracker
- **File:** `racing/D_Amato_Racing.xlsx`
- **Sheets:** WB-23 (work bills), Vet-23 Table (vet records), Reference (product lookup)
- **Usage:** Carlo can ask "what treatments did [horse] get" or "vet fees for [horse]"
- **Source:** Sent by Carlo Apr 9, 2026 — update monthly

### Post Position Colors — ALWAYS IMPORT, NEVER HARDCODE
- **File:** `scripts/pp_colors.py`
- **Usage:** `from scripts.pp_colors import PP_COLORS, PP_TEXT, pp_badge_style, pp_text_hex, pp_border_color`
- **All picks PDF scripts MUST import from here** — never hardcode PP colours again
- Covers PP #1–12 with correct bg + text colours (e.g. #6=black/yellow, #7=orange/black, #12=lime/black)

### pdfplumber DRF Parser ⭐ PRIMARY (updated April 13, 2026)
- **Script:** `scripts/drf_extract.py` — Coordinate-based extraction using pdfplumber
- **Key discovery:** Beyer digits are Bold, finish/field digits are Regular
- **Method:** Extract ONLY Bold digits before `/` to get Beyer
  - 1 Bold digit → single-digit Beyer (e.g., 9)
  - 2 Bold digits → 2-digit Beyer (e.g., 46)
  - 3 Bold digits → 3-digit Beyer (e.g., 107)
  - 4+ Bold digits → 2-digit Beyer with finish appended (e.g., 7710 → 77)
- **Why it works:** DRF Bold font distinguishes Beyer digits from finish/field, handles concatenated words
- **Usage:** `python3 scripts/drf_extract.py <pdf_path> [race_num]`
- **Output:** All races with horses sorted by PP. Includes trainer, jockey, Beyers[], avg_beyer_3, best_beyer
- **Note:** Only extracts Beyers now (no post/field). Workflow: DRF for Beyers, TrackData for PP verification.
- **Replaces:** The old `parse_drf.py` (LiteParse-based) for picks workflow

### LiteParse (backup, March 20, 2026)
- **CLI:** `lit parse <file.pdf> --format text`
- **Use:** Only if pdfplumber parser fails

### PP COLOURS — ALWAYS USE THIS FILE (updated April 3, 2026)
- **File:** `/home/damato/.hermes/skills/racing/saddlecloth.md` — SINGLE SOURCE OF TRUTH
- **Template:** `scripts/picks_pdf_template.py` — copy this for every new race day
- **NEVER hardcode PP colours** — always import from the saddlecloth file
- Key colours: #6=black bg/YELLOW text. #7=orange bg/black text. #12=lime green bg/black text
- **IMPORTANT:** This is the SADDLESOTH chart — different from old pp_colors.py!
- **ALWAYS visually verify the PDF** before sending — open it, check the badges look right

---

## Horse Racing Data

### TrackData.live MCP Server (mcporter) ⭐ PRIMARY
- **MCP URL:** https://mcp.trackdata.live/mcp
- **CLI:** `mcporter call trackdata.<tool>`
- **Config:** `/home/damato/.openclaw/workspace/config/mcporter.json`
- **Tools:**
  - `get_scratches` — today's scratches with horse names (on-demand when Carlo asks)
  - `get_changes` — change log (no horse names, limited use)
  - `get_todays_races` — today's full card (e.g. `track=GP`)
  - `get_race_details` — full entry details by key `GP-YYYYMMDD-RACENUM`
  - `get_horse_profile` — career stats + race history
  - `get_horses` — search by name
  - `get_past_races` — historical results
  - `get_claims` — claimed horses
  - `get_tracks` — all available track codes
- **Added:** February 21, 2026

### TrackData.live (Web - Fallback)
- **URL:** https://trackdata.live
- **Password:** damatopi
- **Purpose:** Web UI fallback if MCP server is down
- **Credentials stored:** `/home/damato/.openclaw/workspace/.trackdata_credentials`

---

Add whatever helps you do your job. This is your cheat sheet.

---

## 🐎 DRF Parsing Tools (Gulfstream + Woodbine)

**Location:** `scripts/` — all Python, no dependencies beyond pdfplumber

| File | Purpose | Best for |
|------|---------|----------|
| `drf_beyer_bot_v8.py` | Full scoring parser (GP) | Gulfstream Park PDFs |
| `drf_beyer_bot_wo.py` | WO parser (PyMuPDF) | Woodbine PDFs |
| `drf_beyer_unified.py` | Auto-detects GP or WO | Unknown format |
| `drf_beyer_extractor.py` | CSV + JSON export | Data analysis, archival |
| `validate_drf_parse.py` | Quality gate | Pre-flight check before picks |

**Usage:**
```bash
# GP — full scoring
python3 scripts/drf_beyer_bot_v8.py /path/to/GP_DRf.pdf

# WO — full scoring
python3 scripts/drf_beyer_bot_wo.py /path/to/WO_DRF.pdf

# Auto-detect (GP or WO)
python3 scripts/drf_beyer_unified.py /path/to/DRF.pdf

# Extract to CSV + JSON
python3 scripts/drf_beyer_extractor.py /path/to/DRF.pdf [output_dir]

# Validate parse quality
python3 scripts/validate_drf_parse.py output/beyers.json
```

**Workflow:**
1. Run `drf_beyer_extractor.py` → `output/beyers.json`
2. Run `validate_drf_parse.py` on the JSON
3. If clean → use `drf_beyer_unified.py` for analysis

---

## 📦 Dropbox

- **Access token:** stored in `config/dropbox_token.txt` (chmod 600)
- **App name:** OpenClaw-Charlie
- **Shared folder:** Carlo's Dropbox (`Carlo and Chi` folder confirmed accessible ✅)
- **Use:** Fetch DRF PDFs, share racing picks, exchange files
- **API:** Dropbox API v2
- **Test:** `curl -H "Authorization: Bearer $(cat config/dropbox_token.txt)" -H "Content-Type: application/json" "https://api.dropboxapi.com/2/files/list_folder" --data '{"path":""}'`

---

## 📄 PDF to Word Converter

**Script:** `scripts/pdf_to_docx.py`
**Library:** `pdf2docx` (installed system-wide)

**When Carlo says:** "convert X to Word / docx / Microsoft format" → run this script

```bash
python3 scripts/pdf_to_docx.py <input.pdf> [output.docx]
```

- Output defaults to same folder as input, same name, `.docx` extension
- Works on any PDF — picks, reports, documents, etc.
- Fast (~1 sec per 4 pages)
