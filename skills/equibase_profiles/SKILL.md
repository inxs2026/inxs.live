# Equibase Horse Profiles — Charlie's Skill

Pull a complete profile for any horse: career stats, race history, workouts, connections, and stakes class.

**Built:** May 3, 2026 | **Location:** `skills/equibase_profiles/` | **Owner:** Charlie

---

## At a Glance

| What | Command |
|------|---------|
| Full profile + race history | `python3 skills/equibase_profiles/equibase_profile.py --horse "Awesome Bourbon"` |
| Last 5 races only | `python3 skills/equibase_profiles/equibase_profile.py --horse "Awesome Bourbon" --races 5` |
| JSON output | `python3 skills/equibase_profiles/equibase_profile.py --horse "Awesome Bourbon" --format json --output /tmp/horse.json` |
| One-line summary | `python3 skills/equibase_profiles/equibase_profile.py --horse "Awesome Bourbon" --format short` |

---

## Shell Usage

```bash
python3 skills/equibase_profiles/equibase_profile.py --horse "Awesome Bourbon"
python3 skills/equibase_profiles/equibase_profile.py --horse "Twist of Sugar" --races 10
python3 skills/equibase_profiles/equibase_profile.py --horse "Some Horse" --format json --output /tmp/horse.json
python3 skills/equibase_profiles/equibase_profile.py --horse "Some Horse" --visible   # debug Imperva blocks
```

### Arguments

| Arg | Default | Description |
|-----|---------|-------------|
| `--horse` | _(required)_ | Horse name to search |
| `--races` | _(all)_ | Limit race history to last N races |
| `--format` | `table` | Output format: `table`, `short`, or `json` |
| `--output` | _(none)_ | Write JSON to this path |
| `--visible` | _(false)_ | Show browser window for debugging |

---

## Python Usage (import)

```python
from skills.equibase_profiles.equibase_profile import get_profile, format_profile_table

# Get full profile data
data = get_profile("Awesome Bourbon")

# Print formatted table
print(format_profile_table(data))

# Access specific fields
print(data['career_stats']['earnings'])     # $304,944
print(data['career_stats']['best'])         # 108
print(data['trainer'])                       # Abraham R. Katryan
print(data['race_history'][0])              # Most recent race

# Look up a specific race
for race in data['race_history']:
    if race['track'] == 'Woodbine' and 'Gr. 2' in race['type']:
        print(race['date'], race['finish'], race['beyer'])
```

---

## Output Format (table)

```
🏇 Awesome Bourbon (KY)
   Foaled: TB, B, H, FOALED APRIL 21, 2020
   Breeding: NOT BOURBON - SEA THE AWESOME (IRE), BY SEA THE STARS (IRE)
   Trainer: Abraham R. Katryan | Jockey: Pietro Moran | Owner: Carlo D'Amato
   Best Class: Graded Stakes Placed

   Career: 21s 6W 72n 33n Best 108 — $304,944

   Race History (last 5 of 21):
   Date         Trk   Race  Fin   Byr     Type
   --------------------------------------------------------------------
   11/15/2025   Woodbine 10    #2     101     bet365 Kennedy Road Stakes (Gr. 2)
   9/28/2025    Woodbine 6     #1     108     Allowance Optional Claiming
   ...

   Workouts (3 recent):
   Apr 30 WO 5f 1:01.4 B

   Last Sale: Sold to Big Toe Stables
   Consignor: Santa Fe Thoroughbreds
```

---

## Output Format (JSON)

```json
{
  "success": true,
  "name": "Awesome Bourbon",
  "registry": "KY",
  "foaled": "April 21, 2020",
  "sex": "H",
  "color": "B",
  "sire": "NOT BOURBON - SEA THE AWESOME (IRE), BY SEA THE STARS (IRE)",
  "trainer": "Abraham R. Katryan",
  "jockey": "Pietro Moran",
  "owner": "Carlo D'Amato",
  "career_stats": {
    "starts": "21", "wins": "6", "seconds": "7", "thirds": "3",
    "earnings": "$304,944", "best": "108"
  },
  "yearly_stats": [
    {"year": "2025", "starts": "10", "wins": "4", "seconds": "2", "thirds": "0", "earnings": "$163,681", "best": "108"},
    {"year": "2024", "starts": "4", "wins": "0", "seconds": "2", "thirds": "2", "earnings": "$30,073", "best": "104"}
  ],
  "race_history": [
    {
      "date": "11/15/2025", "track": "Woodbine", "race": "10",
      "type": "bet365 Kennedy Road Stakes (Gr. 2)",
      "finish": "2", "beyer": "101"
    }
  ],
  "workouts": ["Apr 30 WO 5f 1:01.4 B"],
  "stakes_class": "Graded Stakes Placed",
  "last_sale": {"sold_to": "Big Toe Stables", "consignor": "Santa Fe Thoroughbreds"},
  "url": "https://www.equibase.com/profiles/Results.cfm?type=Horse&refno=10795115&registry=T",
  "refno": "10795115"
}
```

---

## Data Returned

| Field | Description |
|-------|-------------|
| `name` | Horse name (may include registry in parentheses) |
| `registry` | State/country code: KY, NY, FL, etc. |
| `foaled` | Foaling date |
| `sex` / `color` | Sex (H=horse, M=mare, etc.) and color (B=bay, DK=dk bay, etc.) |
| `sire` | sire — dam line |
| `trainer` / `jockey` / `owner` | Current connections |
| `career_stats` | starts / wins / seconds / thirds / best Beyer / earnings |
| `yearly_stats` | Per-year breakdown |
| `race_history` | List of all races: date, track, race#, type, finish, beyer |
| `workouts` | Recent workouts (date, track, distance, time, etc.) |
| `stakes_class` | Best racing class achieved |
| `last_sale` | Most recent sale info |
| `url` | Direct Equibase profile URL |
| `refno` | Equibase internal horse ID |

---

## How It Works

1. **Navigate** → `equibase.com/premium/eqpHorseLookup.cfm?SAP=TN`
2. **Search** → fill horse name, press Enter
3. **Wait** → Equibase loads profile with Statistics tab showing
4. **Extract basic data** → name, connections, career/yearly stats from Statistics tab
5. **Click Results tab** → tab-separated race table loads: Track | Date | Race# | Type | Breed | Finish | Beyer
6. **Click Workouts tab** → workout entries

Each tab click triggers a dynamic page update — delays are built in to let the page render before scraping.

---

## Dependencies

Hermes venv Python (playwright already installed):
```
~/.hermes/hermes-agent/venv/bin/python
```

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| "Not a horse profile page" | Horse name not found, or Equibase returned a search results page instead |
| 0 races returned | Imperva may have blocked the Results tab click; try `--visible` to watch |
| Missing workouts | Workouts tab may be empty if horse has no recent works |
| Cookie modal blocks clicks | Script auto-removes `#uniccmp` element after each navigation step |
| "No search box found" | Equibase changed the search page URL or input selector |

---

## PDF Generator

```bash
python3 skills/equibase_profiles/equibase_profile_pdf.py --horse "Awesome Bourbon"
python3 skills/equibase_profiles/equibase_profile_pdf.py --horse "Awesome Bourbon" --races 10
python3 skills/equibase_profiles/equibase_profile_pdf.py --horse "Some Horse" --output /tmp/horse.pdf
```

**Output:** `horses/{HORSE}_profile_{YYYYMMDD}.pdf`

PDF includes: header with name/foaling/breeder, trainer-jockey-owner-breeder table, career stats box (starts/wins/seconds/thirds/best Beyer/earnings), full race history table (date/track/race/finish/beyer/type), workouts section, Equibase footer.

Arguments:
| Arg | Default | Description |
|-----|---------|-------------|
| `--horse` | _(required)_ | Horse name |
| `--races` | `20` | Max races in table |
| `--output` | _(auto)_ | Output path |

---

## Files

```
skills/equibase_profiles/
├── SKILL.md                   ← skill reference
├── equibase_profile.py        ← profile crawler (console)
└── equibase_profile_pdf.py    ← PDF generator
```
