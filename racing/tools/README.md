# Racing Tools - Custom Analytics Suite

**Built:** February 12, 2026  
**Purpose:** Track picks performance, analyze trainer patterns, generate reports

## Tools

### 1. Results Tracker (`scripts/track_results.py`)
- Compare picks vs actual race results
- Calculate win %, board %, ROI
- Store historical performance data

### 2. Daily Report Generator (`scripts/daily_report.py`)
- Automated daily recap of picks vs results
- Performance metrics (winners, exactas, trifectas)
- Trend analysis (improving/declining)

### 3. Trainer Database (`scripts/trainer_stats.py`)
- Track trainer win %
- Identify hot/cold trainers
- Surface preference, distance patterns

### 4. Data Extractor (`scripts/extract_data.py`)
- Parse DRF race results
- Extract Beyers, comments, fractional times
- Convert to structured JSON/CSV

## Data Structure

```
racing-tools/
├── data/
│   ├── picks/              # Our daily picks
│   ├── results/            # Actual race results
│   ├── trainers/           # Trainer statistics
│   └── performance/        # Performance metrics
├── reports/                # Generated reports
└── scripts/                # Python tools
```

## Usage

### Track Today's Results
```bash
python3 racing-tools/scripts/track_results.py --date 2026-02-12 --track GP
```

### Generate Daily Report
```bash
python3 racing-tools/scripts/daily_report.py
```

### Update Trainer Stats
```bash
python3 racing-tools/scripts/trainer_stats.py --add "Brad Cox" --win-pct 32 --surface dirt
```

---

**Philosophy:** Simple, reliable, racing-focused. No external dependencies beyond Python standard library.
