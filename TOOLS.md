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
  - `get_scratches` — today's scratches with horse names (use this for STEP 0!)
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
