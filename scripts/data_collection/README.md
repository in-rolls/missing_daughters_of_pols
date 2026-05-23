# Data Collection Scripts for Indian Politicians' Family Data

This directory contains organized scripts for collecting biographical data (particularly children's gender information) from various Indian political bodies.

## Directory Structure

```
data_collection/
├── utilities/           # Reusable utility functions
├── state_assemblies/    # Scripts for state legislative assembly data
├── pdf_extraction/      # Tools for extracting data from PDF documents
├── municipal_govt/      # Scripts for local government data
└── README.md           # This file
```

## Data Sources & Coverage

### ✅ Already Collected
- **Lok Sabha** (12th-17th): National Parliament lower house
- **Rajya Sabha**: National Parliament upper house
- **Delhi Legislative Assembly**: 7th Assembly
- **Uttar Pradesh Legislative Assembly**: 16th-18th Assemblies (PDFs need extraction)

### 🎯 Priority State Assemblies to Collect

#### Tier 1: Large States (High Priority)
1. **Maharashtra** - 288 seats
2. **West Bengal** - 294 seats
3. **Tamil Nadu** - 234 seats
4. **Karnataka** - 224 seats
5. **Gujarat** - 182 seats
6. **Madhya Pradesh** - 230 seats
7. **Rajasthan** - 200 seats
8. **Bihar** - 243 seats
9. **Andhra Pradesh** - 175 seats
10. **Telangana** - 119 seats

#### Tier 2: Medium States
11. **Odisha** - 147 seats
12. **Kerala** - 140 seats
13. **Punjab** - 117 seats
14. **Haryana** - 90 seats
15. **Jharkhand** - 81 seats
16. **Assam** - 126 seats
17. **Chhattisgarh** - 90 seats
18. **Uttarakhand** - 70 seats
19. **Himachal Pradesh** - 68 seats

#### Tier 3: Smaller States & UTs
20. **Jammu & Kashmir** - 89 seats (now UT with assembly)
21. **Goa** - 40 seats
22. **Manipur** - 60 seats
23. **Tripura** - 60 seats
24. **Meghalaya** - 60 seats
25. **Nagaland** - 60 seats
26. **Puducherry** - 30 seats
27. **Mizoram** - 40 seats
28. **Arunachal Pradesh** - 60 seats
29. **Sikkim** - 32 seats

### 📊 Additional Data Sources

#### National Level
- **Union Cabinet Ministers** - Current and historical
- **Chief Ministers** - All states, historical data
- **Governors** - Biographical data if available

#### Local Government (if feasible)
- **Municipal Corporation Mayors** - Major cities
- **District Panchayat Chiefs** - Selected districts
- **Municipal Councillors** - Metro cities (Mumbai, Delhi, Bangalore, etc.)

## Data Collection Strategy

### Primary Sources
1. **Official Assembly Websites** - Most authoritative
   - sansad.in (national)
   - State assembly websites
   - NIC (National Informatics Centre) portals

2. **Election Commission of India** - eci.gov.in
   - Affidavit data (candidates must declare family information)

3. **MyNeta/ADR** (Association for Democratic Reforms)
   - myneta.info - Comprehensive politician database
   - Often includes affidavit data

4. **Individual State Portals**
   - Maharashtra: https://www.mls.org.in/
   - Tamil Nadu: http://www.tn.gov.in/assembly
   - Karnataka: https://www.kla.kar.nic.in/
   - (See state-specific scripts for URLs)

### Data Fields to Collect
- Name
- Party affiliation
- Constituency
- Number of sons
- Number of daughters
- Total children
- Assembly/LS session number
- State
- Other demographic data (age, education) if available

## Usage

### 1. State Assembly Data Collection
```bash
# Collect data for a specific state
python state_assemblies/collect_[state_name].py

# Example:
python state_assemblies/collect_maharashtra.py
```

### 2. PDF Extraction
```bash
# Extract family data from assembly PDF documents
python pdf_extraction/extract_biographical_data.py --input path/to/pdf --output path/to/csv
```

### 3. Web Scraping with Rate Limiting
```python
from utilities.scraping_utils import RateLimitedSession

session = RateLimitedSession(delay=1.0)  # 1 second between requests
data = session.get(url)
```

## Best Practices

1. **Rate Limiting**: Always add delays between requests (1-2 seconds minimum)
2. **Data Validation**: Check for missing/malformed data
3. **Incremental Saving**: Save progress periodically to avoid data loss
4. **Error Logging**: Log failures for manual review
5. **Respect robots.txt**: Check website policies before scraping

## Notes

- Many state websites use regional languages; may need translation
- Some states have better data availability than others
- Election Commission affidavits are often the most reliable source
- Historical data may be harder to obtain for older assemblies
- Consider privacy/ethical implications when collecting family data

## Contributing

When adding new data sources:
1. Create a new script in the appropriate directory
2. Update this README with the source information
3. Use standard column names (names, sons, daughters, party, constituency, etc.)
4. Include error handling and logging
5. Document any data quirks or limitations
