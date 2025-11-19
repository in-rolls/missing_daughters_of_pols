# Working Data Collection Script

## Rajya Sabha Current Members Scraper

**File:** `scrape_rajya_sabha_current.py`

### What It Does

Collects family data (sons and daughters) for ALL current Rajya Sabha members using the official NIC API.

**Source:** `rsdoc.nic.in/Memberweb/GetCurrentMember_Biodata`

**Data Fields:**
- Name, Party, State
- Number of Sons (parsed from words like "One", "Two", etc.)
- Number of Daughters
- Spouse, DOB, Profession, Qualification

### Usage

```bash
cd scripts/data_collection

# Full collection (all current RS members)
python scrape_rajya_sabha_current.py

# Test mode (first 500 IDs only)
python scrape_rajya_sabha_current.py --test

# Custom range
python scrape_rajya_sabha_current.py --start 2000 --end 2600
```

### Output

- **JSON**: `data/rajya_sabha/rs_current_TIMESTAMP.json`
- **CSV**: `data/rajya_sabha/rs_current_TIMESTAMP.csv`

### Performance

- Checks 3000 IDs by default (to catch all possible members)
- 0.5s delay between requests (rate limiting)
- Takes ~25 minutes for full collection
- Shows progress every 100 IDs

### Why This Works

1. **Official API**: Uses government NIC API (stable, reliable)
2. **Current Members Only**: Filters for `MP_CURRENT = true`
3. **Sons/Daughters Data**: Has explicit fields for family breakdown
4. **No JavaScript**: Simple JSON API (no rendering needed)

## Next Steps

For Lok Sabha or State Assemblies, need to find similar working APIs or static HTML sources with sons/daughters breakdown (not just "dependents").
