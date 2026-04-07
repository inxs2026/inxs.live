# Workspace Sitemap

**Purpose:** Quick reference for navigating the workspace. Read this to orient yourself when memory is fuzzy.

**Last updated:** April 7, 2026

---

## 🏠 WORKSPACE ROOT (`~/.openclaw/workspace/`)

### Core Files (born here, stay here)
| File | Purpose |
|------|---------|
| `AGENTS.md` | How I work, startup sequence, rules |
| `SOUL.md` | My personality, communication style |
| `USER.md` | Carlo's info, location, preferences |
| `MEMORY.md` | Long-term curated memory |
| `IDENTITY.md` | My name, avatar, persona |
| `HEARTBEAT.md` | Quick health checks |
| `TOOLS.md` | Tool configs, SSH hosts, API credentials |
| `TOP-3-PICKS-METHODOLOGY.md` | Racing picks process |

### Configuration
| File | Purpose |
|------|---------|
| `config/pi_ssh.env` | Umbrel Pi SSH credentials |
| `config/github_token.txt` | GitHub PAT |
| `config/mcporter.json` | TrackData MCP server config |

---

## 📁 FOLDER STRUCTURE

```
~/.openclaw/workspace/
│
├── memory/                    ← Daily logs + structured memory
│   ├── YYYY-MM-DD.md          ← Daily conversation logs
│   ├── active-tasks.md        ← Current work in progress
│   ├── lessons.md             ← Mistakes and learnings
│   ├── projects.md            ← Long-term initiatives
│   ├── reminders.md           ← Carlo's reminders
│   └── self-review.md         ← Periodic self-assessment
│
├── scripts/                   ← ALL executable scripts (33 files)
│   ├── morning_briefing_with_reminders.py   ← 7AM daily briefing
│   ├── stock_watchlist.py                    ← 10AM + 3PM stock reports
│   ├── heartbeat_check.sh                    ← Hourly health checks
│   ├── send_email_pdf.py                     ← Email PDF attachments
│   ├── parse_drf.py                          ← Parse DRF PDFs
│   ├── verify_picks.py                       ← Verify picks before email
│   ├── pp_colors.py                          ← Post position badge colors
│   ├── picks_pdf_template.py                 ← Picks PDF template
│   ├── pdf_to_docx.py                       ← PDF to Word converter
│   ├── track_results.py                      ← Track racing results
│   ├── auto_cleanup.sh                      ← Daily cleanup
│   ├── backup_charlie.sh                    ← Workspace backup
│   └── [24 other scripts]                   ← One-offs and utilities
│
├── docs/                     ← Documentation
│   ├── CRON-JOBS.md          ← Cron job schedules
│   ├── HEARTBEAT-GUIDE.md    ← Heartbeat documentation
│   ├── VERIFICATION.md       ← Pre-delivery checks
│   ├── WORKFLOWS.md         ← Standard operating procedures
│   ├── SKILLS-GUIDE.md       ← Skill development
│   ├── AUTONOMY-FRAMEWORK.md ← Autonomy implementation
│   ├── WORKSPACE-ORGANIZATION.md ← This document
│   ├── REMINDERS-GUIDE.md    ← How to set reminders
│   └── drf_guide/            ← DRF past performance reference images
│
├── racing/                   ← Horse racing analysis
│   ├── methodology/
│   │   ├── TOP-3-PICKS-METHODOLOGY.md   ← Official picks process ⭐
│   │   ├── CLAIMING-PROSPECTS-CRITERIA.md ← Horses to claim (buy)
│   │   ├── TOP-3-PICKS-CRITERIA.md     ← Legacy criteria file
│   │   ├── rockyta_breeding_analysis.md ← Breeding analysis
│   │   └── truenicks_checklist.md       ← Nickings checklist
│   └── data/                  ← Historical race data
│       ├── 2026-02-12_GP_performance.json
│       ├── 2026-02-12_GP_picks.json
│       ├── 2026-02-12_GP_results.json
│       ├── gulfstream_feb14_COMPLETE_36_PICKS.md
│       ├── gulfstream_feb14_2026_results.md
│       ├── GP-Apr04-2026-parse.txt
│       ├── GP-Apr05-2026-parse.txt
│       ├── GP_Picks_Apr04_2026.pdf
│       └── GP_Picks_Apr05_2026.pdf
│
├── skills/                   ← Workspace-local skills
│   ├── gcalcli-calendar/     ← Google Calendar skill
│   ├── mcporter/             ← TrackData MCP server skill
│   ├── porteden-email/       ← Email skill
│   ├── ralph-loops/          ← Ralph loops skill
│   └── regex-patterns/        ← Regex patterns skill
│
├── tools/                    ← Web projects + tools
│   ├── inxs-live/            ← inxs.live landing page (Vercel)
│   ├── pdf2docx-web/         ← PDF to Word web app (port 5050)
│   └── holographic-memory/    ← Experimental memory tool (not yet used)
│
├── config/                   ← Credentials + keys
│   ├── github_token.txt      ← GitHub PAT
│   ├── mcporter.json         ← TrackData MCP config
│   └── pi_ssh.env            ← Umbrel Pi SSH credentials
│
├── archive/                  ← Old/superseded files (kept for reference)
│   ├── racing-scripts/       ← 50 old racing scripts + race data
│   ├── generate_picks_mar20.py
│   ├── gen_picks_mar7.py
│   ├── gulfstream_feb15_2026_COMPLETE_ANALYSIS.html
│   └── postposition_preview.pdf
│
├── node_modules/             ← npm packages (lucide-static)
├── package.json              ← npm config (for lucide-static)
└── .git/                    ← Git repository (local)
```

---

## 🔑 KEY PATHS FOR TOOLS

| Tool / Skill | Path |
|---------------|------|
| **TrackData MCP** | `mcporter call trackdata.<tool>` |
| **DRF Parser** | `python3 scripts/parse_drf.py <pdf>` |
| **Picks PDF Template** | `scripts/picks_pdf_template.py` |
| **PP Colors (source of truth)** | `/home/damato/.hermes/skills/racing/saddlecloth.md` |
| **PP Colors (legacy)** | `scripts/pp_colors.py` |
| **Email PDF** | `python3 scripts/send_email_pdf.py <email> <subject> <body> <pdf>` |
| **Stock Watchlist** | `python3 scripts/stock_watchlist.py` |
| **Morning Briefing** | `python3 scripts/morning_briefing_with_reminders.py` |

---

## 🖥️ REMOTE SYSTEMS

### Umbrel Pi (10.0.0.45)
- **SSH:** `umbrel@10.0.0.45` (password: damatopi)
- **Connection:** `sshpass -p 'damatopi' ssh -o StrictHostKeyChecking=no umbrel@10.0.0.45`
- **Credentials:** `config/pi_ssh.env`
- **What runs:** OpenClaw (me + Lexi), Bitcoin node, MeTube, Tor, I2P

---

## ⚡ QUICK WORKFLOW REFERENCES

### Racing Picks Workflow
1. DRF PDF arrives via Telegram
2. `python3 scripts/parse_drf.py <pdf>` — parse with litparse
3. Read `TOP-3-PICKS-METHODOLOGY.md` — follow the 10 steps
4. Verify with TrackData: `mcporter call trackdata.get_race_details`
5. Generate PDF from template
6. Email: `python3 scripts/send_email_pdf.py`
7. Silent — no Telegram message after

### Morning Briefing (7AM daily)
- Script: `scripts/morning_briefing_with_reminders.py`
- Includes: reminders FIRST, weather, news, stocks

### Stock Reports (10AM + 3PM Mon-Fri)
- Script: `scripts/stock_watchlist.py`
- Full output — never summarize

---

## 📊 WORKSPACE HEALTH

| Check | Status |
|-------|--------|
| Core files in root | ✅ 8 files |
| Scripts | ✅ 33 scripts in `scripts/` |
| Empty folders | ✅ None |
| Wikilinks | ✅ All key files cross-linked |
| Git status | ✅ Clean, committed |

---

*This sitemap is my map of the workspace. If a file moves, update this document.*
