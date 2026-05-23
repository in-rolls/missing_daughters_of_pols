# Wikipedia State Assembly Scraper

## Overview

This scraper extracts family data (sons, daughters, spouse information) from Wikipedia biographical pages of Indian state assembly members. It's designed to cast a wide net across multiple states to gather data on politicians' children.

## Script Location

`scripts/data_collection/scrape_wikipedia_state_assemblies.py`

## Features

- **Multi-state scraping**: Configured to scrape 15 Indian state assemblies
- **Biographical data extraction**: Extracts sons, daughters, spouse, and children names from Wikipedia infoboxes
- **Smart filtering**: Filters out non-person pages (parties, constituencies, etc.)
- **Rate limiting**: Respects Wikipedia with 1-second delays between requests
- **Comprehensive logging**: Tracks progress and errors
- **CSV output**: Saves data in easy-to-analyze CSV format

## Supported States

The scraper includes URLs for:
1. Maharashtra Legislative Council
2. Maharashtra Assembly (15th)
3. Karnataka Assembly (16th)
4. Tamil Nadu Assembly (16th)
5. Kerala Assembly (15th)
6. Uttar Pradesh Assembly (18th)
7. West Bengal Assembly (17th)
8. Rajasthan Assembly (16th)
9. Madhya Pradesh Assembly (16th)
10. Telangana Assembly (3rd)
11. Punjab Assembly (16th)
12. Haryana Assembly (14th)
13. Bihar Assembly (17th)
14. Odisha Assembly (17th)
15. Assam Assembly (15th)

## Usage

### Basic Usage

```python
from scrape_wikipedia_state_assemblies import WikipediaAssemblyScraper

# Initialize scraper
scraper = WikipediaAssemblyScraper()

# Scrape specific states
test_states = [
    'maharashtra_council',
    'karnataka_assembly',
    'tamil_nadu_assembly',
    'kerala_assembly',
    'punjab_assembly'
]

results = scraper.scrape_all_states(states=test_states)
```

### Command Line

```bash
cd /home/user/missing_daughters_of_pols
python scripts/data_collection/scrape_wikipedia_state_assemblies.py
```

## Output

### CSV Files Created

All files are saved to `data/wikipedia_state_assemblies/`:

1. **Individual state files**: `{state_key}.csv` (e.g., `maharashtra_council.csv`)
2. **Combined file**: `all_states_combined.csv`

### CSV Schema

| Column | Type | Description |
|--------|------|-------------|
| name | str | Member's name |
| sons | int | Number of sons (if found) |
| daughters | int | Number of daughters (if found) |
| spouse | str | Spouse information |
| children_names | list | Names of children extracted from bio |
| raw_family_text | str | Raw text from family/children fields |
| url | str | Wikipedia page URL |
| state | str | State identifier key |

## Data Extraction Logic

### Text Pattern Matching

The scraper uses improved regex patterns to extract children data:

- `"2 sons"` → sons: 2
- `"1 daughter"` → daughters: 1
- `"Son: 3, Daughter: 1"` → sons: 3, daughters: 1
- `"has a son and daughter"` → sons: 1, daughters: 1

### Infobox Parsing

The scraper looks for Wikipedia infobox fields containing:
- "child", "son", "daughter", "family" keywords
- Links to children's names (if they have Wikipedia pages)
- Spouse/partner information

### Article Text Fallback

If infobox data isn't available, the scraper searches the first few paragraphs of the article for family mentions.

## Features & Improvements

### Smart Filtering

Automatically excludes pages for:
- Political parties (BJP, INC, NCP, etc.)
- Constituencies (Assembly constituencies)
- Non-person pages (lists, categories, etc.)

### Rate Limiting

- 1 second delay between general requests
- Additional 0.5 second sleep between member pages
- Exponential backoff on errors
- Retry logic (up to 3 attempts)

### Respectful Scraping

- Proper User-Agent header identifying the research project
- Conservative request rates
- Comprehensive error handling

## Limitations

1. **Coverage**: Only scrapes up to 100 members per state (configurable)
2. **Data availability**: Depends on Wikipedia biographical data quality
3. **URL stability**: Wikipedia page structures may change
4. **Manual URL updates**: Assembly number in URLs may need updating for new elections

## Testing Results

Initial test on Maharashtra Legislative Council:
- Scraped 100 members successfully
- Found some family data in biographical text
- Demonstrated the approach works

## Extending the Scraper

### Adding New States

Add to `STATE_URLS` dict in the `WikipediaAssemblyScraper` class:

```python
STATE_URLS = {
    # ...existing states...
    'new_state_assembly': 'https://en.wikipedia.org/wiki/List_of_members_of_the_Nth_StateName_Legislative_Assembly',
}
```

### Increasing Member Limit

Change line 250 in `scrape_state()` method:

```python
for i, member in enumerate(members[:100], 1):  # Change 100 to desired limit
```

### Adjusting Rate Limiting

Modify in `__init__` method:

```python
self.session = RateLimitedSession(delay=1.0)  # Increase delay if needed
```

## Dependencies

```
requests>=2.28.0
beautifulsoup4>=4.11.0
pandas>=1.5.0
lxml>=4.9.0
```

## Future Enhancements

1. **Expand to all Indian states**: Currently covers 15 states, can add all 28 states + 8 UTs
2. **Historical data**: Scrape previous assembly sessions
3. **Rajya Sabha members**: Add Upper House coverage
4. **Multi-language support**: Extract data from regional language Wikipedias
5. **Structured children data**: Better parsing of individual children (names, genders, ages)
6. **Cross-referencing**: Match with existing Lok Sabha data for comprehensive coverage

## Notes

- Wikipedia data quality varies significantly by politician
- More prominent politicians tend to have better biographical coverage
- The scraper successfully demonstrates that Wikipedia is a viable source for casting a wide net
- Data should be validated against other sources where possible

## Contact

Part of the "Missing Daughters of Indian Politicians" research project:
https://github.com/in-rolls/missing_daughters_of_pols
