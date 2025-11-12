# Quick Start Guide: Data Collection

This guide will help you start collecting data immediately.

## Setup (One-time)

```bash
cd scripts/data_collection
pip install -r requirements.txt
```

## Test the Framework

```bash
python test_collector.py
```

This will:
- Test utility functions
- Verify HTTP connectivity
- Show sample data from existing sources

## Collecting New Data

### Option 1: State Assembly Data (Recommended - Most Reliable)

Election affidavits are legally required and contain family information.

```bash
cd state_assemblies

# Collect from a single state
python collect_election_affidavits.py --state karnataka --year 2023

# Collect from multiple states
python collect_election_affidavits.py --state maharashtra --year 2019
python collect_election_affidavits.py --state "tamil nadu" --year 2021
python collect_election_affidavits.py --state gujarat --year 2022
```

**Output:** Creates CSV files in `data/<state_name>/` directory

**Data fields:**
- names, party, constituency, state, year
- sons, daughters, total_children, sex_ratio

### Option 2: Extract from Existing PDFs

If you already have PDF documents with biographical data:

```bash
cd pdf_extraction

# Extract from Uttar Pradesh PDFs
python extract_biographical_data.py --input ../../../data/up/ --output ../../../data/up/extracted.csv

# Extract from any PDF directory
python extract_biographical_data.py --input /path/to/pdfs/ --output /path/to/output.csv
```

### Option 3: Municipal Government Data

```bash
cd municipal_govt

python collect_municipal_data.py --city mumbai --output ../../../data/municipal/
```

**Note:** Municipal scripts need customization for each city's website.

## Priority Collection Order

For the quickest impact, collect in this order:

### Week 1: Large States (Tier 1)
```bash
python collect_election_affidavits.py --state maharashtra --year 2019
python collect_election_affidavits.py --state karnataka --year 2023
python collect_election_affidavits.py --state gujarat --year 2022
python collect_election_affidavits.py --state "tamil nadu" --year 2021
python collect_election_affidavits.py --state "west bengal" --year 2021
```

### Week 2: Medium States (Tier 2)
```bash
python collect_election_affidavits.py --state kerala --year 2021
python collect_election_affidavits.py --state punjab --year 2022
python collect_election_affidavits.py --state odisha --year 2019
python collect_election_affidavits.py --state haryana --year 2019
```

### Week 3: Extract from Existing PDFs
```bash
python extract_biographical_data.py --input ../../../data/up/ --output ../../../data/up/extracted.csv
```

## Monitoring Progress

The collection scripts:
- **Save checkpoints** every 10 records
- **Log progress** to console
- **Handle interruptions** gracefully (resume from checkpoint)
- **Rate limit** requests (1-2 seconds between requests)

## Analyzing Collected Data

Once you have CSV files, analyze with pandas:

```python
import pandas as pd
from utilities.scraping_utils import calculate_summary_stats

# Load data
df = pd.read_csv('../../../data/karnataka/karnataka_assembly_2023.csv')

# Calculate statistics
stats = calculate_summary_stats(df)
print(stats)

# Sex ratio
print(f"Sex Ratio: {stats['sex_ratio']:.2f}")
print(f"Proportion Daughters: {stats['proportion_daughters']:.3f}")
```

## Troubleshooting

### Problem: "No module named 'requests'"
**Solution:**
```bash
pip install -r requirements.txt
```

### Problem: Collection script finds no candidates
**Possible causes:**
1. MyNeta URL format has changed - verify at myneta.info
2. State name spelling - try variations (e.g., "tamilnadu" vs "tamil nadu")
3. Year is incorrect - check most recent election year

**Debug steps:**
- Visit the MyNeta URL directly in browser
- Check the script logs for HTTP errors
- Try a different state/year combination

### Problem: PDF extraction finds no data
**Possible causes:**
1. PDF is scanned image (not text-based)
2. PDF uses non-standard format
3. Text is in regional language

**Solutions:**
- For scanned PDFs: Use OCR (Tesseract)
- For regional languages: May need manual extraction or translation
- Check PDF structure: `pdfplumber` may work better than `PyPDF2`

## Data Quality Checks

After collection, validate:

```python
import pandas as pd

df = pd.read_csv('output.csv')

# Check completeness
print(f"Total records: {len(df)}")
print(f"Records with son/daughter data: {df[['sons', 'daughters']].notna().all(axis=1).sum()}")
print(f"Completeness: {df[['sons', 'daughters']].notna().all(axis=1).sum() / len(df) * 100:.1f}%")

# Check for anomalies
print("\nRecords with >10 children:")
print(df[(df['sons'] + df['daughters']) > 10][['names', 'sons', 'daughters']])
```

## Next Steps

1. ✅ Run `test_collector.py` to verify setup
2. ✅ Collect from 2-3 states to test workflow
3. ✅ Review data quality
4. ✅ Scale up to all states
5. ✅ Analyze combined dataset
6. ✅ Compare with existing Lok Sabha results

## Getting Help

- See `README.md` for comprehensive documentation
- Check scripts for inline comments
- Review existing analysis: `../../03_ls_daughters.ipynb`
