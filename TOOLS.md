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
- **File:** `TOP-3-PICKS-METHODOLOGY.md` ⭐ **OFFICIAL PROCESS**
- **When:** Analyzing races for betting picks
- **Process:**
  1. Calculate Beyer averages (last 3) for ALL contenders
  2. Analyze form, class, trainer/jockey angles, pace
  3. Rank by MOST positive factors
  4. Write 2-3 sentence explanation per pick
- **Rule:** "In Beyers We Trust" - Numbers + form, not hunches
- **System working well - follow it exactly!**

### **CLAIMING PROSPECTS** (Horses to Buy)
- **File:** `CLAIMING-PROSPECTS-CRITERIA.md`  
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
- **Voice:** en-US-JennyNeural (friendly, considerate, comfort)
- **Auto mode:** off (text by default, voice on request only)
- **Note:** Matches Charlie's warm, empathetic female personality
- **Changed:** Feb 15, 2026 - installed edge-tts, fixed voice (SaraNeural didn't exist)

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
