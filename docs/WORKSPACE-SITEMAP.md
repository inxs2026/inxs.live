# Workspace Sitemap

**Purpose:** Quick reference for navigating the workspace. Read this to orient yourself when memory is fuzzy.

**Last updated:** April 7, 2026

---

## Workspace Root

**Path:** `~/.openclaw/workspace/`

### Core Files (born here, stay here)

- [[AGENTS.md]] — How I work, startup sequence, rules
- [[SOUL.md]] — My personality, communication style
- [[USER.md]] — Carlo's info, location, preferences
- [[MEMORY.md]] — Long-term curated memory
- [[IDENTITY.md]] — My name, avatar, persona
- [[HEARTBEAT.md]] — Quick health checks
- [[TOOLS.md]] — Tool configs, SSH hosts, API credentials
- [[TOP-3-PICKS-METHODOLOGY.md]] — Racing picks process

### Configuration

- [[config/pi_ssh.env]] — Umbrel Pi SSH credentials
- [[config/github_token.txt]] — GitHub PAT
- [[config/mcporter.json]] — TrackData MCP server config

---

## Folder Structure

### memory/

Daily logs and structured memory

- `YYYY-MM-DD.md` — Daily conversation logs
- [[memory/active-tasks.md]] — Current work in progress
- [[memory/lessons.md]] — Mistakes and learnings
- [[memory/projects.md]] — Long-term initiatives
- [[memory/reminders.md]] — Carlo's reminders
- [[memory/self-review.md]] — Periodic self-assessment

### scripts/

ALL executable scripts (33 files)

- [[scripts/morning_briefing_with_reminders.py]] — 7AM daily briefing
- [[scripts/stock_watchlist.py]] — 10AM + 3PM stock reports
- [[scripts/heartbeat_check.sh]] — Hourly health checks
- [[scripts/send_email_pdf.py]] — Email PDF attachments
- [[scripts/parse_drf.py]] — Parse DRF PDFs
- [[scripts/verify_picks.py]] — Verify picks before email
- [[scripts/pp_colors.py]] — Post position badge colors
- [[scripts/picks_pdf_template.py]] — Picks PDF template
- [[scripts/pdf_to_docx.py]] — PDF to Word converter
- [[scripts/track_results.py]] — Track racing results
- [[scripts/auto_cleanup.sh]] — Daily cleanup
- [[scripts/backup_charlie.sh]] — Workspace backup

### docs/

Documentation

- [[docs/CRON-JOBS.md]] — Cron job schedules
- [[docs/HEARTBEAT-GUIDE.md]] — Heartbeat documentation
- [[docs/VERIFICATION.md]] — Pre-delivery checks
- [[docs/WORKFLOWS.md]] — Standard operating procedures
- [[docs/SKILLS-GUIDE.md]] — Skill development
- [[docs/AUTONOMY-FRAMEWORK.md]] — Autonomy implementation
- [[docs/REMINDERS-GUIDE.md]] — How to set reminders
- [[docs/WORKSPACE-SITEMAP.md]] — This document
- [[docs/drf_guide/]] — DRF past performance reference images

### racing/

Horse racing analysis

**methodology/**
- [[TOP-3-PICKS-METHODOLOGY.md]] — Official picks process (required reading)
- [[racing/methodology/CLAIMING-PROSPECTS-CRITERIA.md]] — Horses to claim (buy)
- [[racing/methodology/TOP-3-PICKS-CRITERIA.md]] — Legacy criteria
- [[racing/methodology/rockyta_breeding_analysis.md]] — Breeding analysis
- [[racing/methodology/truenicks_checklist.md]] — Nickings checklist

**data/**
Historical race data (Feb 12, Apr 4-5, etc.)

### skills/

Workspace-local skills

- [[skills/gcalcli-calendar/]] — Google Calendar skill
- [[skills/mcporter/]] — TrackData MCP server skill
- [[skills/porteden-email/]] — Email skill
- [[skills/ralph-loops/]] — Ralph loops skill
- [[skills/regex-patterns/]] — Regex patterns skill

### tools/

Web projects and tools

- [[tools/inxs-live/]] — inxs.live landing page (Vercel)
- [[tools/pdf2docx-web/]] — PDF to Word web app (port 5050)
- [[tools/holographic-memory/]] — Experimental memory tool (not yet used)

### config/

Credentials and keys

- [[config/github_token.txt]] — GitHub PAT
- [[config/mcporter.json]] — TrackData MCP config
- [[config/pi_ssh.env]] — Umbrel Pi SSH credentials

### archive/

Old and superseded files

- [[archive/racing-scripts/]] — 50 old racing scripts and race data

---

## Key Paths for Tools

**TrackData MCP:** `mcporter call trackdata.<tool>`

**DRF Parser:** `python3 scripts/parse_drf.py <pdf>`

**Picks PDF Template:** `scripts/picks_pdf_template.py`

**PP Colors (source of truth):** `/home/damato/.hermes/skills/racing/saddlecloth.md`

**PP Colors (legacy):** `scripts/pp_colors.py`

**Email PDF:** `python3 scripts/send_email_pdf.py`

**Stock Watchlist:** `python3 scripts/stock_watchlist.py`

**Morning Briefing:** `python3 scripts/morning_briefing_with_reminders.py`

---

## Remote Systems

### Umbrel Pi (10.0.0.45)

- **SSH:** `umbrel@10.0.0.45` (password: damatopi)
- **Connection:** `sshpass -p 'damatopi' ssh -o StrictHostKeyChecking=no umbrel@10.0.0.45`
- **Credentials:** [[config/pi_ssh.env]]
- **What runs:** OpenClaw (me + Lexi), Bitcoin node, MeTube, Tor, I2P

---

## Quick Workflow References

### Racing Picks Workflow

1. DRF PDF arrives via Telegram
2. `python3 scripts/parse_drf.py <pdf>` — parse with litparse
3. Read [[TOP-3-PICKS-METHODOLOGY.md]] — follow the 10 steps
4. Verify with TrackData: `mcporter call trackdata.get_race_details`
5. Generate PDF from [[scripts/picks_pdf_template.py]]
6. Email: `python3 scripts/send_email_pdf.py`
7. Silent — no Telegram message after

### Morning Briefing (7AM daily)

Script: [[scripts/morning_briefing_with_reminders.py]]

Includes: reminders FIRST, weather, news, stocks

### Stock Reports (10AM + 3PM Mon-Fri)

Script: [[scripts/stock_watchlist.py]]

Full output — never summarize

---

## Workspace Health

| Check | Status |
|-------|--------|
| Core files in root | 8 files |
| Scripts | 33 scripts in scripts/ |
| Empty folders | None |
| Wikilinks | All key files cross-linked |
| Git status | Clean, committed |

---

## Related Documents

- [[MEMORY.md]] — Long-term curated memory
- [[memory/lessons.md]] — All lessons learned from mistakes
- [[memory/projects.md]] — Active and completed projects
- [[docs/WORKFLOWS.md]] — Standard operating procedures
- [[docs/CRON-JOBS.md]] — Scheduled autonomous tasks
- [[HEARTBEAT.md]] — Quick health checks (run hourly)
- [[TOOLS.md]] — Tool configs, credentials, SSH hosts

---

*This sitemap is my map of the workspace. If a file moves, update this document. Use wikilinks when referencing other files.*
