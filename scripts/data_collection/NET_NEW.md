# Net New Data Collection Capabilities

## What's NEW (Beyond existing RS/LS scrapers)

### 🎯 PRIMARY VALUE: State Assembly Collection

**28 State Assemblies = ~4,000 MLAs = 3-4x your current dataset**

Scripts:
- `state_assemblies/collect_election_affidavits.py` - Generic collector for any state
- `state_assemblies/collect_all_priority_states.py` - Bulk orchestration
- `state_assemblies/collect_all_states_guide.sh` - Quick reference

**Quick Start:**
```bash
cd scripts/data_collection/state_assemblies
python collect_election_affidavits.py --state karnataka --year 2023
```

**Collect all Tier 1 states:**
```bash
python collect_all_priority_states.py --tier 1
```

### 🔧 Reusable Utilities

`utilities/scraping_utils.py` - Import in ANY scraper:
- `RateLimitedSession` - HTTP with retry & rate limiting
- `validate_family_data()` - Normalize data
- `calculate_summary_stats()` - Standard metrics
- `extract_children_from_text()` - Parse biographical text
- `DataCollector` - Base class for collectors

### 📄 PDF Extraction

`pdf_extraction/extract_biographical_data.py` - Extract from UP PDFs you already have

**Usage:**
```bash
python extract_biographical_data.py --input ../../../data/up/ --output ../../../data/up/extracted.csv
```

### 🏛️ Municipal Government Framework

`municipal_govt/collect_municipal_data.py` - Template for 40+ cities

### 📊 Data Sources Roadmap

`DATA_SOURCES.md` - Comprehensive list of 50+ potential sources, prioritized by:
- Sample size
- Data availability
- Collection difficulty
- Research impact

## Impact

| Data Source | Current | After Collection | Growth |
|-------------|---------|------------------|--------|
| Lok Sabha | 1,785 MPs | 1,785 | - |
| Rajya Sabha | (archived) | (archived) | - |
| State Assemblies | 147 (Delhi only) | ~4,000 MLAs | **27x** |
| Municipal | 0 | ~3,000 | **NEW** |
| **TOTAL** | **~1,900** | **~8,900** | **4.7x** |

## Priority Actions (By Impact)

1. **Collect Tier 1 States** (Week 1)
   - 10 largest states
   - ~1,500 MLAs
   - 80% of state-level data

2. **Extract UP PDFs** (Week 1)
   - PDFs already collected
   - ~400 MLAs
   - Largest state

3. **Collect Tier 2 States** (Week 2-3)
   - Medium states
   - ~1,500 more MLAs

4. **Municipal Governments** (Month 2)
   - Top 10 cities
   - ~1,000 corporators
   - Different socioeconomic profile

## What You Already Have (Not Duplicating)

✅ Lok Sabha scraper (`03_ls_daughters.ipynb`)
✅ Rajya Sabha scraper (`01_get_rs_data.ipynb`)
✅ Rajya Sabha analysis (`02_rs_parse_analyse.ipynb`)
✅ Delhi Assembly data (`delhi.ipynb`)

## Bottom Line

**Net new capability: Collect 28 state assemblies + 40 municipal corporations**

**Dataset growth: 1,900 → 8,900 politicians (4.7x)**

**Time to collect Tier 1 states: ~1 week (scripts ready)**
