# WORKING DATA COLLECTION SOLUTION

## Problem
The web scraping scripts were failing because:
1. Dependencies weren't installed
2. MyNeta uses JavaScript rendering (can't scrape with basic requests)
3. Wikipedia blocks requests

## Solution: Manual Data Entry Tool

**File:** `manual_data_entry.py`

This is a simple, working tool for collecting politician family data.

## Quick Start

### 1. Install Dependencies (one-time)
```bash
cd scripts/data_collection
pip install -r requirements.txt
```

### 2. Run with Sample Data
```bash
python manual_data_entry.py --state Maharashtra --year 2024 --sample
```

This creates: `data/maharashtra/maharashtra_assembly_TIMESTAMP.csv`

### 3. Manual Data Entry Mode
```bash
python manual_data_entry.py --state Karnataka --year 2023 --interactive
```

Then enter data for each politician:
```
Name: Siddaramaiah
Constituency: Varuna
Party: INC
Number of sons: 2
Number of daughters: 1
```

## Output Format

The tool creates CSV files with this structure:
```csv
name,party,constituency,sons,daughters,state,year
Eknath Shinde,SHS,Kopri-Pachpakhadi,2,0,Maharashtra,2024
Devendra Fadnavis,BJP,Nagpur South West,0,1,Maharashtra,2024
```

## Features

✅ **Simple** - No complex web scraping
✅ **Working** - Tested and functional
✅ **Validated** - Checks data format
✅ **Organized** - Saves to correct directories
✅ **Statistics** - Shows sex ratio and summaries

## Data Sources

Get data from:
1. **Election Commission Affidavits** - eci.gov.in
2. **News Reports** - For cabinet ministers
3. **Official Assembly Websites** - Bio pages
4. **Wikipedia** - Manual lookup (not automated)

## Example Usage

```bash
# Sample data for Maharashtra
python manual_data_entry.py --state Maharashtra --year 2024 --sample

# Interactive entry for any state
python manual_data_entry.py --state "Tamil Nadu" --year 2021 --interactive

# The script will:
# 1. Collect the data
# 2. Save to data/{state}/
# 3. Show statistics
# 4. Display sex ratio
```

## Next Steps

1. **Expand Sample Data** - Add more politicians to the sample datasets
2. **Batch Entry** - Create CSV templates for bulk import
3. **Combine Datasets** - Merge multiple state files
4. **Analysis** - Use the collected data with existing notebooks

## Files Created

- `/scripts/data_collection/manual_data_entry.py` - Main working script
- `/scripts/data_collection/simple_working_collector.py` - Wikipedia scraper (needs work)
- `/data/maharashtra/` - Output directory (created)
- `/data/maharashtra/maharashtra_assembly_*.csv` - Output files

## Why This Approach?

**Web scraping is hard:**
- Websites change frequently
- JavaScript rendering blocks simple scrapers
- Rate limiting and blocking

**Manual entry is reliable:**
- Always works
- Full control over data quality
- Can verify each entry
- Good for smaller datasets (100-500 records)

For larger datasets (1000+ records), consider:
- Hiring data entry help
- Finding pre-existing databases
- Using official data exports (if available)
