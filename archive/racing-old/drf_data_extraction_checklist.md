# DRF Data Extraction Checklist
## Comprehensive Data Points for Racing Analysis

**Goal:** Extract EVERY valuable piece of information from the Daily Racing Form for complete handicapping analysis.

---

## BASIC HORSE INFORMATION

### Identity
- [ ] **Horse name**
- [ ] **Age** (3yo, 4yo, etc.)
- [ ] **Birth month** (Jan, Feb, Mar... shown as "3 (Jan)")
- [ ] **Sex** (colt, filly, gelding, mare)
- [ ] **Color** (bay, chestnut, dark bay/brown, gray)

### Breeding
- [ ] **Sire** (father) and stud fee
- [ ] **Dam** (mother) and her sire
- [ ] **Breeder** and location

### Connections
- [ ] **Owner**
- [ ] **Trainer** - name and stats (win %, starts-wins)
- [ ] **Jockey** - name and stats
- [ ] **Weight** carried
- [ ] **Medication** (Lasix: L, First Lasix: ÷)

---

## CAREER RECORD

### Overall Stats (from "Life" line)
- [ ] **Total starts**
- [ ] **Wins**
- [ ] **Places (2nd)**
- [ ] **Shows (3rd)**
- [ ] **Total career earnings**
- [ ] **Best Beyer Speed Figure** (career high)

### Calculate:
- [ ] **Average earnings per start** = Total earnings ÷ Total starts
- [ ] **Win percentage** = Wins ÷ Starts
- [ ] **In-the-money %** = (Wins + Places + Shows) ÷ Starts

### Current Year Stats
- [ ] **2026 record** (starts-wins-places-shows-earnings)
- [ ] **2025 record** (if available)

### Surface Breakdown
- [ ] **Dirt** (starts-wins-places-shows-earnings-best Beyer)
- [ ] **Turf** (starts-wins-places-shows-earnings-best Beyer)
- [ ] **Synthetic/Tapeta** (starts-wins-places-shows-earnings-best Beyer)
- [ ] **Wet tracks** (if separate line shown)

### Distance Record
- [ ] **At today's distance** (Dst line) - starts-wins-places-shows-earnings-best Beyer

---

## PAST PERFORMANCES (Last 10 races minimum)

For EACH race, extract:

### Race Conditions
- [ ] **Date** (e.g., 10â26 = October 10, 2026)
- [ ] **Track** (GP, WO, CD, etc.)
- [ ] **Surface** (fst, fm, gd, sly, ú = synthetic)
- [ ] **Distance** (6f, 1M, 1Â, etc.)
- [ ] **Track condition** (fast, good, sloppy, sealed)

### Fractional Times
- [ ] **Opening fraction** (e.g., 22¦ for first quarter)
- [ ] **Half-mile time** (e.g., :46)
- [ ] **3/4 mile time** (if applicable)
- [ ] **Final time** (e.g., 1:11§)

### Race Details
- [ ] **Race type** (Clm, Alw, Stakes, Md, etc.)
- [ ] **Class level** (claiming price, purse, stakes name)
- [ ] **Conditions** (N3L, N2X, etc.)

### Performance Data
- [ ] **Beyer Speed Figure** for that race
- [ ] **Post position**
- [ ] **Field size** (e.g., 3/6 = 3rd in 6-horse field)
- [ ] **Trip position calls:**
  - Start position
  - After 1st call
  - After 2nd call
  - Stretch call
  - Finish position
- [ ] **Beaten lengths** (e.g., 3§ = beaten 3.5 lengths)
- [ ] **Jockey** who rode
- [ ] **Weight carried**
- [ ] **Odds** (e.g., 4.50 = 9-2)

### RUNNING COMMENTS (Critical!)
- [ ] **Trip notes** - What happened during the race?
  - "Bumped start" = troubled start
  - "Saved ground" = rail trip
  - "Angled 4w" = moved wide
  - "Rallied" = closed late
  - "Weakened" = tired
  - "Eased" = pulled up, major concern!
  - "Fell" = fell during race (soundness red flag)
  - "Pulled up" = stopped before finish (injury concern)
  - "Blocked 5/16-1/16" = traffic trouble (excuse)
  - "Steadied" = checked by another horse
  - "Bore out/in" = lugged out or in
  - "No factor" = never competitive
  - "Passed tired horses" = late run against beaten horses (not impressive)

### Calculate for Each Race:
- [ ] **Actual finishing time** (if beaten):
  - Winner's time + (beaten lengths ÷ 2.5) = horse's time
  - Example: Winner 1:10.0, beaten 2.5L → 1:11.0

---

## WORKOUT INFORMATION

For each workout:
- [ ] **Date** (e.g., â 24 GP = January 24 at Gulfstream)
- [ ] **Track**
- [ ] **Distance** (3f, 4f, 5f)
- [ ] **Surface** (fst, gd, fm, ú = synthetic)
- [ ] **Time**
- [ ] **Quality rating:**
  - **B** = Breezing (standard)
  - **Bg** = Breezing with good energy
  - **H** = Handily (working hard)
  - **g** = With company (working with another horse)
  - **d** = From gate
- [ ] **Ranking** (e.g., 5/21 = 5th fastest of 21 horses that day)

### Workout Pattern Analysis:
- [ ] **Regularity** - How often? (every 5-7 days = good)
- [ ] **Recent** - When was last work? (within 7-10 days of race = ready)
- [ ] **Quality** - Bullet works (1/X = fastest that day)?
- [ ] **Progression** - Times getting faster?
- [ ] **Gaps** - Any long breaks? (red flag for soundness)

---

## TRAINER/JOCKEY STATS

### Trainer Patterns (shown at bottom of PP)
- [ ] **Overall win %**
- [ ] **Specific conditions:**
  - Maiden claims (MdnClm)
  - First-time Lasix (1stLasix)
  - Turf/Synth switches
  - Sprint to route (Sprint/Route)
  - Off 31-60 days layoff
  - Routes
  - Claims
  - Stakes
- [ ] **Track-specific** (e.g., "2025-26 GP")
- [ ] **Jockey/Trainer combo** (J/T stats)

### Jockey Stats
- [ ] **Overall record** (starts-wins-places-shows-win%)
- [ ] **2025 record**
- [ ] **Mount changes** (who rode last time vs today?)

---

## CLAIMING/OWNERSHIP HISTORY

### Claiming Activity
- [ ] **Claimed from** - who, for how much, when
- [ ] **Voided claims** - (v) symbol = major red flag!
- [ ] **Claiming price today** vs last race
- [ ] **Trainer after claim** - new connections

### Equipment Changes
- [ ] **Blinkers** - ON/OFF
- [ ] **First-time equipment** - blinkers, visor, etc.

---

## CLASS ANALYSIS

### Class Level Comparison
- [ ] **Today's class** (purse, claiming price, conditions)
- [ ] **Last 3 races class levels**
- [ ] **Pattern:**
  - Rising in class?
  - Dropping in class? (competitive drop vs stagnant drop)
  - Same level?

### Class Drop Quality
- [ ] **Competitive at higher class?** (4th-5th finishes = good)
- [ ] **Stagnant dropper?** (same poor results despite drops = bad)
- [ ] **Strategic big drop?** (confidence builder)
- [ ] **Gradual decline?** (getting worse each race)

---

## SOUNDNESS INDICATORS (For Claiming Races)

### Racing Frequency
- [ ] **Starts per year**
  - 10+ races/year = sound
  - 5-6 races/year = questionable
  - <5 races/year = red flag
- [ ] **Missing seasons** - gaps of 6-12+ months?
- [ ] **Earnings per start** (calculated above)

### Red Flags in Comments
- [ ] **"Eased"** - pulled up before finish
- [ ] **"Fell"** - fell during race
- [ ] **"Pulled up"** - stopped racing
- [ ] **"Lame"** - obvious injury
- [ ] **Voided claims (v)**

### Workout Soundness
- [ ] **Consistent spacing** (5-7 days apart)
- [ ] **No long gaps** between works
- [ ] **Regular pattern** leading to race

---

## SPEED FIGURE ANALYSIS

### Beyer Comparison
- [ ] **Horse's best Beyer**
- [ ] **Recent Beyers** (last 3 races)
- [ ] **Beyer at today's distance/surface**
- [ ] **Comparison to field:**
  - Who has highest Beyer?
  - Where does this horse rank?
  - Beyer progression (improving or declining?)

### Time Analysis
- [ ] **Fastest time at today's exact distance/surface**
- [ ] **How many times run at this distance?**
- [ ] **Recent times** (within 6 months?)
- [ ] **Time trend** (getting faster or slower?)

---

## BREEDING ANALYSIS (When Relevant)

### Sire Information
- [ ] **Sire name** and stud fee
- [ ] **Sire's specialty** (dirt, turf, sprinter, router)
- [ ] **Sire's progeny success**

### Dam Information
- [ ] **Dam name**
- [ ] **Dam's sire** (broodmare sire)
- [ ] **Surface preference** indicated by breeding

### Surface Compatibility
- [ ] **Wrong surface = opportunity?** (bred for turf running on dirt, etc.)
- [ ] **First-time surface switch** with good breeding

---

## SPECIAL SITUATIONS

### First-Time Starters (Maidens with no races)
- [ ] **Birth month** (Jan/Feb = may be more developed)
- [ ] **Workout pattern** (regular? quality?)
- [ ] **Debut timing** (early season vs late season)
- [ ] **Trainer maiden stats**

### Return from Layoff
- [ ] **Length of layoff** (days since last race)
- [ ] **Reason for layoff** (if known)
- [ ] **Workout pattern during layoff**
- [ ] **Trainer layoff stats** (31-60 days, 61-180 days)

### Equipment/Medication Changes
- [ ] **Blinkers ON/OFF** (trainer stats for this)
- [ ] **First-time Lasix** (÷ symbol, trainer stats)
- [ ] **Gelding surgery** ("first start since gelding")

---

## PACE ANALYSIS

### Early Pace
- [ ] **TimeformUS Early pace figure** (if shown)
- [ ] **Historical running style:**
  - Front-runner? (leads early)
  - Presser? (close to pace)
  - Mid-pack? (waits)
  - Closer? (comes from behind)

### Late Pace
- [ ] **TimeformUS Late pace figure**
- [ ] **Finishing ability** from comments

### Today's Race Setup
- [ ] **How many speed horses?**
- [ ] **Likely pace scenario** (fast, moderate, slow)
- [ ] **Does this horse benefit?**

---

## DISTANCE SUITABILITY

### Experience at Today's Distance
- [ ] **Ever run this distance?**
- [ ] **Success at this distance?**
- [ ] **Stretching out** (going longer)?
- [ ] **Cutting back** (going shorter)?

### Distance Pattern
- [ ] **Best at what distance?**
- [ ] **Fade at shorter = won't handle longer**
- [ ] **Strong finishes = handles stretch out?**

---

## TRACK/SURFACE COMPATIBILITY

### Today's Surface
- [ ] **Dirt, Turf, or Synthetic?**
- [ ] **Record on this surface**
- [ ] **First time on this surface?**
- [ ] **Breeding suitable for surface?**

### Track-Specific Record
- [ ] **Record at today's track** (GP, WO, etc.)
- [ ] **Familiarity with track**

---

## VALUE OPPORTUNITIES

### Arbitrage Plays
- [ ] **Wrong surface** (bred for turf on dirt = cheap buy?)
- [ ] **Class drop** to reset confidence
- [ ] **Trainer pattern** (strategic placement)

### Overlooked Positives
- [ ] **Traffic trouble last out** (excuse in comments)
- [ ] **Bad post position** last time
- [ ] **Equipment change** addressing issue
- [ ] **Jockey upgrade**

---

## FINAL CHECKLIST SUMMARY

Before making a pick, have you extracted:

✅ **Basic info** - age, birth month, connections  
✅ **Career record** - earnings, win %, earnings/start  
✅ **Past performances** - dates, conditions, times, Beyers, comments  
✅ **Workouts** - pattern, quality, recency  
✅ **Trainer/jockey stats** - relevant conditions  
✅ **Class analysis** - where coming from vs where going  
✅ **Soundness** - frequency, gaps, red flags (for claiming)  
✅ **Speed figures** - Beyers, times at distance  
✅ **Running style** - pace preference  
✅ **Distance/surface fit** - experience and success  
✅ **Comments** - trip notes, excuses, trouble  

**Goal:** Use ALL available data from DRF + other tools (Equibase, TrackData.live, historical forms) to build the MOST COMPLETE picture possible.

---

*Created: February 10, 2026*  
*Purpose: Systematic extraction of all DRF data points for comprehensive handicapping*  
*Use with: Equibase entries, TrackData.live results, Woodbine historical forms*
