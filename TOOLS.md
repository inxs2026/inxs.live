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

## ⚠️ Critical Path Rules (Etched in Stone)

### NEVER use /tmp for image tool files
**The image tool (and other tools) can only read from allowed directories.**
`/tmp` is NOT in the allowed file-read list.

**Rule:** Any time you convert a PDF to images using pdftoppm or similar, you MUST immediately copy to workspace:

```bash
pdftoppm -r 150 -png input.pdf /tmp/page  # output goes to /tmp/page-1.png etc.
cp /tmp/page-1.png /home/damato/.openclaw/workspace/tmp_page1.png  # ALWAYS copy first!
# THEN use /home/damato/.openclaw/workspace/tmp_page1.png in the image tool
```

**Why:** If the image tool tries to read `/tmp/page-1.png` directly → `Local media path is not under an allowed directory` → soft-lock. This is what killed the April 26 WO picks session.

**Allowed read directories:**
- `/home/damato/.openclaw/workspace/` (workspace tree)
- `/home/damato/.openclaw/media/` (media tree)
- Some skill directories

**Never:** `/tmp`, `$HOME`, paths outside the allowed tree.

### Context Overflow Guard
If the session is approaching 100K tokens, do NOT start heavy multi-step work:
- PDF parsing (multiple pages)
- Multi-image analysis (more than 3-4 images at once)
- Long model calls

**Early warning:** If heartbeat reports "⚠️ Session approaching context limit", stop and archive/reset before continuing.

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
- **Changed:** Apr 27, 2026 - emojis NOT spoken (paw print 🐾 is visual only, not read aloud)

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

### TrackData.live — DRF PDF Auto-Download (VERIFIED Apr 21, 2026) ⭐
**On race day, I can pull the DRF PDF directly from TrackData — no manual upload needed.**

**Steps:**
1. **Get track + date from Carlo** (e.g., "do WO races tomorrow")
2. **Download PDF:**
```bash
curl -s -L "https://api.trackdata.live/api/uploads/{TRACK}--{YYYY-MM-DD}.pdf" \
  -o racing/DRF/{TRACK}--{YYYY-MM-DD}.pdf
```
- URL format: `{TRACK}--{MM-DD-YYYY}.pdf` (e.g. `WO--04-19-2026.pdf`)
- Works for any track/date that's been uploaded (WO, GP, SA, AQU, KEE, TAM, etc.)
- Confirm upload exists first via: `mcporter call trackdata.get_recent_uploads --json '{"limit": 5}'`

3. **Extract Beyers:**
```bash
python3 scripts/drf_extract.py racing/DRF/{TRACK}--{YYYY-MM-DD}.pdf
```

4. **Build picks** per [[TOP-3-PICKS-METHODOLOGY.md]]

5. **Email to Carlo**

**Verification (Apr 21, 2026):**
- WO--04-19-2026.pdf → 715KB, 12 pages, 6 races, 40 horses ✅
- Extraction worked perfectly with `drf_extract.py` ✅
- Download URL: `https://api.trackdata.live/api/uploads/WO--04-19-2026.pdf`

**Note:** No API key or auth needed for download — it's publicly accessible once uploaded.

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

## WO DRF Beyer Extraction (VERIFIED Apr 19, 2026)

### Production Script
`racing/wo_beyer_extract.py` - extracts all Beyers from WO DRF PDF

### Key Fixes (Apr 19, 2026)
1. **Block boundaries**: Life 'L' at x=370-390 = horse block TOP
2. **Last horse**: use `life_ys[i+1] if i+1 < len else 800`
3. **avg3**: first 3 sorted by y ascending = most recent

### Verified 100% correct against image analysis
| Horse | Beyers | avg3 |
|-------|--------|------|
| Twist of Sugar | [37,33,45,45,65,66,57] | 38.3 |
| Vegas Road | [53] | 53.0 |
| Money Heist | [48,48] | 48.0 |
| Seeking Magic | [41,41,41,30,14,36,34,27,32] | 41.0 |
| Miss Soothsayer | [58,62,46,53,52,50,44] | 55.3 |

### Usage
```bash
python3 racing/wo_beyer_extract.py
# Outputs: racing/WO--04-19-2026_beyer_results.json
```


## WO DRF Beyer Extraction - FINAL VERIFIED METHOD (Apr 19, 2026)

### Production Script
 - 100% verified correct

### Key Fixes (VERIFIED with Carlo)
1. **Block boundaries**: Life 'L' at x=370-390 = horse block TOP
2. **-0 pattern**: '-' at x=212.9 + '0' at x=216.6 = 0 Beyer (horse didn't earn figure)
3. **Normal pair**: digit at x=213.3 + digit at x=216.6 = 2-digit Beyer
4. **avg3**: average of most recent 3 = highest y values (end of sorted list)
5. **First pages**: {1, 2, 3, 5, 7, 9, 11} (includes Race 2's page)

### Verified Examples (Apr 19, 2026)
- Lady On the Nile: [0, 0, 37, 47, 47, 40, 64] → avg3=50.3
- Reload Baba: [25, 23, 26] → avg3=24.7
- Twist of Sugar: [37, 33, 45, 45, 65, 66, 57] → avg3=62.7

### Usage
python3 racing/wo_beyer_extract.py


## PRIMARY BeyEr Extraction: Image Tool (Apr 19, 2026) - CARLO ORDERED

### Carlo confirmed: image analysis is the ONLY reliable extraction method
pdfplumber had bugs for months - coords were wrong, -0 pattern missed.

### How It Works
1. Convert PDF: `pdftoppm -r 150 -png input.pdf page`
2. Analyze: Use `image` tool with detailed prompt
3. Parse: Extract horse names, Beyers[], avg3 from response

### Prompt Template
```
Look at this Woodbine DRF page. For EACH horse, list:
1. Horse name
2. ALL Beyer figures in order (most recent first)
3. avg3 = average of most recent 3

Format: HORSENAME: [beyer1, beyer2, ...] avg3=X.X
```

### Production Script
`racing/wo_beyer_extract_image.py` - documents workflow
`racing/wo_beyer_extract.py` - DEPRECATED, use image tool instead

## WO DRF Beyer Extraction - VERIFIED CORRECT (Apr 19, 2026)

### The Method (Verified with Carlo's bordered image)
1. Filter for **BOLD font** digits at x=213.3 (tens) and x=216.6 (units)
2. Pair digits within 3px y tolerance
3. Sort by y ascending - lowest y = top of page = most recent race
4. **FIRST 3 in sorted list = most recent 3 Beyers** (NOT last 3!)
5. avg3 = average of FIRST 3

### Key code:
```python
beyer_tens = [(c['top'], c['text']) for c in chars 
              if 'Bold' in str(c.get('fontname', '')) and 213 < c['x0'] < 214 and c['text'].isdigit()]
beyer_units = [(c['top'], c['text']) for c in chars 
               if 'Bold' in str(c.get('fontname', '')) and 216.5 < c['x0'] < 217.5 and c['text'].isdigit()]
# Pair, sort, avg3 of FIRST 3
```

### Verified against Carlo's bordered image (Nicki Is a Breeze):
- Extraction: [57, 59, 44, 58, 54, 54, 58, 43, 67, 59, 51, 55] ✓
- Carlo's box: [57, 59, 44] most recent → avg3 = 53.3 ✓

### Production script:
`racing/wo_beyer_extract.py` - UPDATE with BOLD filter + FIRST 3 logic

### CRITICAL REMINDERS
- Top of page = most recent race
- First 3 in y-sorted list = most recent 3 Beyers
- Life 'L' at x=370-390 = horse block top

## 📊 Equibase Standings — Charlie's Skill

**My own skill** (built May 3, 2026 — Carlo asked me to own it)

```bash
# Console standings
python3 skills/equibase_standings/equibase_crawl.py --track WO --type trainer

# PDF report (all 3 types)
python3 skills/equibase_standings/equibase_pdf.py --track WO
python3 skills/equibase_standings/equibase_pdf.py --track GP --types trainer jockey owner
```

- Wraps Hermes crawler via Hermes venv Python (same data, same Imperva handling)
- PDF output: `standings/{TRACK}_standings_{YYYYMMDD}.pdf`
- Skill file: `skills/equibase_standings/SKILL.md`
- Scripts: `skills/equibase_standings/equibase_crawl.py` + `equibase_pdf.py`
