# Projects

**Purpose:** Long-term initiatives, ongoing work, future ideas

---

## Active Projects

### Racing Analytics Suite
**Status:** In progress  
**Started:** February 12, 2026  
**Goal:** Build custom tools for tracking picks performance, trainer patterns, and ROI

**Components:**
- ✅ `racing/` folder structure
- ✅ [[scripts/verify_picks.py]] - compare picks vs actual results
- ⏳ Daily report generator (planned)
- ⏳ Trainer database (planned)
- ⏳ Data extractor for DRF results (planned)

**Files:**
- `/home/damato/.openclaw/workspace/racing/`
- [[TOP-3-PICKS-METHODOLOGY.md]]

**Next Steps:**
1. Track today's Gulfstream results (after races complete)
2. Build daily report generator
3. Populate trainer stats from recent races

---

## Completed Projects

### Session Hygiene Monitoring
**Completed:** February 14, 2026  
**Goal:** Monitor session size and prevent performance issues  
**Result:** [[scripts/check_session_hygiene.sh]] script created (2MB warn, 5MB alert)

### Structured Memory System
**Completed:** February 14, 2026  
**Goal:** Split memory into organized files instead of dumping everything into [[MEMORY.md]]  
**Result:** Created [[memory/active-tasks.md]], [[memory/lessons.md]], [[memory/self-review.md]], [[memory/projects.md]]

### Crash Recovery Protocol
**Completed:** February 14, 2026  
**Goal:** Resume work autonomously after crashes/restarts  
**Result:** Updated [[AGENTS.md]] to read [[memory/active-tasks.md]] first on startup

### Skills Enhancement Framework
**Completed:** February 14, 2026  
**Goal:** Add "Use when / Don't use when" to skills to prevent wrong selection  
**Result:** Created [[docs/SKILLS-GUIDE.md]], updated regex-patterns skill

### Self-Verification System
**Completed:** February 14, 2026  
**Goal:** Catch errors before delivery - "build ≠ review"  
**Result:** Created [[docs/VERIFICATION.md]] with quick & deep checks

### Cron Jobs for Autonomous Operation
**Completed:** February 14, 2026  
**Goal:** Scheduled work in isolated sessions  
**Result:** 3 cron jobs created:
- Daily Racing Results (8 PM) - tracks performance, announces results
- Weekly Self-Review (Sunday 8 PM) - analyzes my week, delivers summary
- Daily Storage Cleanup (midnight) - maintenance, alerts only if issues

See [[docs/CRON-JOBS.md]] for full cron job documentation.

### Heartbeat Optimization
**Completed:** February 14, 2026  
**Goal:** Fast health checks (<30 sec), no heavy work  
**Result:** 
- Rewrote [[HEARTBEAT.md]] with 5 quick checks
- Created [[scripts/heartbeat_check.sh]] script (session, tasks, workspace, cron health, racing)
- Created [[docs/HEARTBEAT-GUIDE.md]] documentation
- Heavy work moved to cron jobs

### TrackData.live Integration
**Completed:** February 9, 2026  
**Goal:** Access horse racing data tool  
**Result:** Credentials stored in [[TOOLS.md]], can access via [[mcporter]] skill

### Backup & Storage Cleanup
**Completed:** February 14, 2026  
**Goal:** Free up workspace storage, add pCloud capacity  
**Result:** 138 MB freed, auto-cleanup scripts created, 4GB pCloud added

### SSH Access to Umbrel Pi
**Completed:** April 7, 2026  
**Goal:** SSH into Carlo's Umbrel Pi without needing Carlo to run commands  
**Result:** 
- SSH connection established: `umbrel@10.0.0.45`
- Credentials stored in [[config/pi_ssh.env]]
- Full sudo access granted
- Can now diagnose and fix OpenClaw on the Pi directly

---

## Future Ideas

### Email Monitoring
- Check inbox periodically for important messages
- Auto-categorize racing results, personal email, etc.
- Integrate with heartbeat checks

### Proactive Calendar Integration
- Check upcoming events
- Remind Carlo of important dates
- Suggest prep work for scheduled items

### Voice Storytelling
- Use `sag` (ElevenLabs TTS) for movie summaries, stories
- More engaging than text walls

### Performance Tracking Dashboard
- Visualize racing picks ROI
- Track trainer/jockey performance over time
- Generate weekly/monthly reports

---

## Project Template

```markdown
### [Project Name]
**Status:** planning | in-progress | on-hold | completed
**Started:** YYYY-MM-DD
**Goal:** One-line description
**Components:**
- [ ] Component 1
- [ ] Component 2
**Files:** List relevant files/directories
**Next Steps:**
1. Step 1
2. Step 2
```
