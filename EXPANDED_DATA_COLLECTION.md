# Expanded Data Collection Plan: Missing Daughters of Indian Politicians

## Overview

This document outlines the comprehensive data collection framework to expand the research from ~4,500 Lok Sabha children to **20,000+ children** across multiple levels of Indian government.

## Current Status

### ✅ Complete
- **Lok Sabha (12-17)**: 4,500+ children analyzed
- **Delhi Assembly**: 147 children analyzed (sex ratio: 1.19)
- **Framework**: Full data collection infrastructure built

### 📦 Ready to Analyze
- **Rajya Sabha**: ~2,000 records collected (archived)
- **Uttar Pradesh Assembly**: PDFs collected for 16th-18th sessions

### 🎯 Ready to Collect
- **26 State Assemblies**: Scripts ready, ~3,000-4,000 MLAs
- **Municipal Governments**: Framework ready for major cities

## New Data Collection Scripts

All scripts are organized in `/scripts/data_collection/`:

```
data_collection/
├── README.md                          # Comprehensive documentation
├── QUICKSTART.md                      # Get started in 5 minutes
├── DATA_SOURCES.md                    # All potential data sources
├── requirements.txt                   # Python dependencies
│
├── utilities/
│   └── scraping_utils.py             # Reusable functions
│
├── state_assemblies/
│   ├── collect_election_affidavits.py    # Main collector (MyNeta)
│   ├── collect_maharashtra.py            # State-specific template
│   └── collect_all_states_guide.sh       # Command reference
│
├── pdf_extraction/
│   └── extract_biographical_data.py      # Extract from PDFs
│
├── municipal_govt/
│   └── collect_municipal_data.py         # Municipal corporations
│
├── test_collector.py                 # Validate framework
├── demo_analysis.py                  # Sample analysis (Delhi)
└── collect_all_priority_states.py   # Orchestrate bulk collection
```

## Quick Start

### 1. Setup (5 minutes)
```bash
cd scripts/data_collection
pip install -r requirements.txt
python test_collector.py  # Validate setup
```

### 2. See Sample Analysis
```bash
python demo_analysis.py  # Analyzes existing Delhi data
```

**Output:**
```
Delhi MLAs (n=63):
- Sex Ratio: 1.19 (vs natural 1.05)
- Proportion Daughters: 0.456
- Estimated missing daughters: ~9
- HIGHER sex ratio than 17th Lok Sabha (1.14)
```

### 3. Collect New State Data
```bash
cd state_assemblies

# Single state
python collect_election_affidavits.py --state karnataka --year 2023

# Multiple states (orchestrated)
cd ..
python collect_all_priority_states.py --tier 1  # Large states first
```

## Data Sources by Priority

### Tier 1: State Assemblies (HIGHEST PRIORITY) ⭐⭐⭐⭐⭐

**Impact**: 3-4x current sample size
**Effort**: Low (scripts ready)
**Quality**: High (legally required affidavits)

**Method**: MyNeta affidavit data collection

**States to collect**:
1. Maharashtra (288 seats)
2. West Bengal (294 seats)
3. Tamil Nadu (234 seats)
4. Karnataka (224 seats)
5. Gujarat (182 seats)
6. Madhya Pradesh (230 seats)
7. Rajasthan (200 seats)
8. Bihar (243 seats)
9. Andhra Pradesh (175 seats)
10. Telangana (119 seats)
+ 19 more states

**Timeline**: 2-4 weeks (with rate limiting)

### Tier 2: Rajya Sabha Analysis ⭐⭐⭐⭐⭐

**Impact**: +2,000 records
**Effort**: Low (data already collected)
**Quality**: High

**Method**: Parse existing archive at `data/rajya_sabha.tar.gz`

**Timeline**: 1 week

### Tier 3: Uttar Pradesh PDFs ⭐⭐⭐⭐

**Impact**: +400-600 records (largest state)
**Effort**: Medium (extraction needed)
**Quality**: High

**Method**: PDF extraction (scripts ready, needs dependency fixes)

**Timeline**: 1 week

### Tier 4: Municipal Governments ⭐⭐⭐

**Impact**: +3,000-5,000 records
**Effort**: Medium-High (city-specific customization)
**Quality**: Variable

**Method**: Web scraping of municipal corporation websites

**Priority cities**: Mumbai, Delhi, Bangalore, Hyderabad, Chennai

**Timeline**: 4-6 weeks

### Tier 5: National Leaders ⭐⭐⭐

**Impact**: +500-1,000 high-profile cases
**Effort**: Medium
**Quality**: High (well-documented)

**Categories**:
- Union Cabinet Ministers (current + historical)
- Chief Ministers (all states)
- Governors

**Timeline**: 2-3 weeks

## Projected Dataset Growth

| Data Source | Current | After Phase 1 | After Phase 2 |
|-------------|---------|---------------|---------------|
| Lok Sabha | 4,500 | 4,500 | 4,500 |
| Rajya Sabha | 0 | 2,000 | 2,000 |
| State Assemblies | 147 | 4,000 | 8,000 |
| Municipal | 0 | 0 | 3,000 |
| National Leaders | 0 | 0 | 500 |
| **TOTAL CHILDREN** | **4,647** | **10,500** | **18,000** |

## Research Questions Enabled by Expanded Data

### With State Assembly Data
1. **Regional variation**: Do states with higher population sex ratios also show higher politician sex ratios?
2. **State vs national**: Are state-level politicians different from national MPs?
3. **Policy impact**: Do states with stronger PCPNDT enforcement show different patterns?
4. **Party patterns**: Are party differences consistent across states?

### With Municipal Data
1. **Local vs state/national**: Does the pattern extend to local government?
2. **Urban patterns**: Different elite dynamics in metro cities?
3. **Power gradient**: Does sex ratio vary by level of political power?

### With Multiple Government Levels
1. **Comprehensive elite picture**: Across all political positions
2. **Historical trends**: Changes over time across different bodies
3. **Comparative analysis**: Politicians vs other elite groups

## Technical Features

### Robust Data Collection
- ✅ Rate limiting (1-2 second delays)
- ✅ Checkpoint/resume capability
- ✅ Error handling and logging
- ✅ Progress tracking
- ✅ Data validation

### Reusable Utilities
- ✅ `RateLimitedSession`: HTTP with retry logic
- ✅ `validate_family_data()`: Data normalization
- ✅ `calculate_summary_stats()`: Standard metrics
- ✅ `extract_children_from_text()`: Text parsing
- ✅ `DataCollector` base class: Common patterns

### Quality Assurance
- ✅ Test suite included
- ✅ Sample data validation
- ✅ Documentation for each script
- ✅ Error logging

## Implementation Timeline

### Week 1-2: Immediate Quick Wins
- [x] Build collection framework
- [x] Test on existing data (Delhi)
- [ ] Collect 5 large states
- [ ] Analyze Rajya Sabha data

**Deliverable**: 2x dataset size

### Week 3-4: Scale Up
- [ ] Collect remaining state assemblies
- [ ] Extract UP PDF data
- [ ] Initial analysis of state patterns

**Deliverable**: 3-4x dataset size, state-level analysis

### Week 5-8: Expand Scope
- [ ] Top 10 municipal corporations
- [ ] National leaders (Cabinet, CMs)
- [ ] Historical state assembly data

**Deliverable**: 5-6x dataset size, multi-level analysis

### Week 9-12: Comprehensive Analysis
- [ ] Complete all major data sources
- [ ] Comparative elite analysis
- [ ] Regional deep dives
- [ ] Publish extended findings

**Deliverable**: Comprehensive research paper

## Expected Outcomes

### Dataset Expansion
- From ~1,800 Lok Sabha MPs to **~5,000-10,000 politicians**
- From ~4,500 children to **~15,000-25,000 children**
- Coverage of **all 28 states + 8 UTs**

### New Analyses Possible
1. State-by-state breakdown
2. Urban vs rural politicians
3. Different government levels
4. Historical trends (2000-2024)
5. Party patterns across states

### Research Impact
- More robust statistical power
- Regional heterogeneity analysis
- Policy recommendation specificity
- Comparative elite studies

## Usage Examples

### Collect Single State
```bash
python state_assemblies/collect_election_affidavits.py \
  --state karnataka \
  --year 2023 \
  --output ../../data/
```

### Bulk Collection
```bash
python collect_all_priority_states.py --tier 1
```

### Analysis
```python
import pandas as pd
from utilities.scraping_utils import calculate_summary_stats

# Load collected data
df = pd.read_csv('data/karnataka/karnataka_assembly_2023.csv')

# Calculate statistics
stats = calculate_summary_stats(df)
print(f"Sex Ratio: {stats['sex_ratio']:.2f}")
print(f"Sample Size: {stats['n_politicians']} politicians")
```

## Documentation

- **`README.md`**: Comprehensive guide to all data sources
- **`QUICKSTART.md`**: Get started in 5 minutes
- **`DATA_SOURCES.md`**: All potential sources with feasibility analysis
- **Inline comments**: All scripts well-documented

## Next Steps

1. **Immediate**: Run `python test_collector.py` to validate setup
2. **Week 1**: Start collecting Tier 1 states
3. **Week 2**: Analyze Rajya Sabha data
4. **Week 3**: Scale up to all state assemblies
5. **Month 2**: Expand to municipal governments

## Contact & Contribution

This framework is designed to be:
- **Extensible**: Easy to add new data sources
- **Maintainable**: Clear code structure
- **Reusable**: Utility functions for common tasks
- **Documented**: Comprehensive guides

To add a new data source:
1. Create script in appropriate directory
2. Use utility functions from `scraping_utils.py`
3. Follow naming convention: `collect_[source].py`
4. Update this documentation

---

**Framework Version**: 1.0
**Last Updated**: 2025-11-12
**Status**: Ready for production use
