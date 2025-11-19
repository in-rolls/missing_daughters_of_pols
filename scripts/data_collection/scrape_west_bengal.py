"""
Working scraper for West Bengal 2021 Assembly Winners

This scrapes from MyNeta which has static HTML pages (not JavaScript-heavy).
Collects data for all 294 West Bengal MLAs elected in 2021.

Usage:
    python scrape_west_bengal.py
    python scrape_west_bengal.py --limit 10  # Test with first 10 only
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import re
import argparse
from pathlib import Path
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


class WestBengalScraper:
    """Scraper for West Bengal 2021 election data from MyNeta"""

    def __init__(self):
        self.base_url = "https://www.myneta.info/WestBengal2021"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })

    def get_winners_list(self):
        """Get list of all winners with their profile links"""
        url = f"{self.base_url}/index.php?action=show_winners&sort=default"

        logger.info(f"Fetching winners list from: {url}")

        try:
            response = self.session.get(url, timeout=15)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')

            # Find all candidate links
            candidates = []

            for link in soup.find_all('a', href=re.compile(r'candidate\.php\?candidate_id=')):
                href = link['href']
                candidate_id = re.search(r'candidate_id=(\d+)', href)

                if candidate_id:
                    candidates.append({
                        'name': link.text.strip(),
                        'candidate_id': candidate_id.group(1),
                        'url': f"{self.base_url}/{href}"
                    })

            # Deduplicate by candidate_id
            seen_ids = set()
            unique_candidates = []
            for c in candidates:
                if c['candidate_id'] not in seen_ids:
                    seen_ids.add(c['candidate_id'])
                    unique_candidates.append(c)

            logger.info(f"Found {len(unique_candidates)} winners")
            return unique_candidates

        except Exception as e:
            logger.error(f"Error fetching winners list: {e}")
            return []

    def scrape_candidate_profile(self, candidate):
        """Scrape individual candidate profile for family data"""

        logger.info(f"Scraping: {candidate['name']}")

        try:
            response = self.session.get(candidate['url'], timeout=15)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')

            record = {
                'name': candidate['name'],
                'candidate_id': candidate['candidate_id'],
                'state': 'West Bengal',
                'year': 2021
            }

            # Extract constituency and party from the page
            # Look for text like "Constituency: ALIPURDUARS" and "Party: BJP"
            page_text = soup.get_text()

            # Constituency
            constituency_match = re.search(r'Constituency[:\s]+([A-Z\s]+)', page_text, re.IGNORECASE)
            if constituency_match:
                record['constituency'] = constituency_match.group(1).strip()

            # Party
            party_match = re.search(r'Party[:\s]+([A-Z\(\)]+)', page_text, re.IGNORECASE)
            if party_match:
                record['party'] = party_match.group(1).strip()

            # Look for family information in tables
            # MyNeta affidavits have "Dependent1", "Dependent2", "Dependent3" columns

            # Method 1: Count non-nil dependents in the PAN table
            dependents_count = 0

            tables = soup.find_all('table')
            for table in tables:
                table_text = table.get_text().lower()

                # Look for tables with "dependent" mentions
                if 'dependent1' in table_text or 'dependent2' in table_text or 'dependent3' in table_text:
                    rows = table.find_all('tr')

                    for row in rows:
                        cells = row.find_all(['td', 'th'])
                        cell_texts = [c.get_text().strip().lower() for c in cells]

                        # Count if any dependent column has non-"nil" value
                        for i, cell in enumerate(cells):
                            cell_text = cell.get_text().strip().lower()

                            # Check if this is a dependent column with a non-nil value
                            if i >= 3:  # Dependent columns are usually after self, spouse, HUF
                                if cell_text and cell_text not in ['nil', '', 'n', 'no', '-', '0']:
                                    # This dependent has some value (asset, etc.)
                                    dependent_num = i - 2  # Rough estimate
                                    if dependent_num > 0 and dependent_num <= 3:
                                        dependents_count = max(dependents_count, dependent_num)

            # Method 2: Look for explicit spouse and dependent mentions in text
            spouse_match = re.search(r'spouse', page_text, re.IGNORECASE)
            has_spouse = spouse_match is not None

            # Try to find explicit family size mentions
            # Some affidavits mention "household members" or similar
            family_size_match = re.search(r'(\d+)\s+dependents?', page_text, re.IGNORECASE)
            if family_size_match:
                dependents_count = int(family_size_match.group(1))

            # Store what we found
            record['has_spouse'] = has_spouse
            record['dependents_count'] = dependents_count if dependents_count > 0 else None

            # Note: We can't definitively extract sons vs daughters from these affidavits
            # They only show "Dependent1", "Dependent2", etc. without gender
            record['sons'] = None  # Unknown from this source
            record['daughters'] = None  # Unknown from this source
            record['total_children_estimated'] = dependents_count if dependents_count > 0 else None

            # Add note about data limitation
            record['notes'] = 'Affidavit shows dependents but not gender breakdown'

            time.sleep(1.5)  # Rate limiting

            return record

        except Exception as e:
            logger.error(f"Error scraping {candidate['name']}: {e}")
            return {
                'name': candidate['name'],
                'candidate_id': candidate['candidate_id'],
                'state': 'West Bengal',
                'year': 2021,
                'error': str(e)
            }

    def scrape_all(self, limit=None):
        """Scrape all winners"""

        # Get winners list
        winners = self.get_winners_list()

        if not winners:
            logger.error("No winners found")
            return None

        if limit:
            winners = winners[:limit]
            logger.info(f"Limiting to first {limit} candidates for testing")

        # Scrape each winner
        data = []

        for i, winner in enumerate(winners):
            logger.info(f"Progress: {i+1}/{len(winners)}")
            record = self.scrape_candidate_profile(winner)
            data.append(record)

            # Save checkpoint every 20 records
            if (i + 1) % 20 == 0:
                logger.info(f"Checkpoint: Scraped {i+1} records")

        return data


def save_data(data, output_dir='../../data/west_bengal'):
    """Save collected data to CSV"""

    if not data:
        logger.error("No data to save")
        return None

    df = pd.DataFrame(data)

    # Create output directory
    output_path = Path(__file__).parent / output_dir
    output_path.mkdir(parents=True, exist_ok=True)

    # Generate filename
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f'west_bengal_assembly_2021_{timestamp}.csv'
    filepath = output_path / filename

    # Save
    df.to_csv(filepath, index=False)

    logger.info(f"\n{'='*70}")
    logger.info(f"DATA SAVED TO: {filepath}")
    logger.info(f"Total records: {len(df)}")
    logger.info(f"{'='*70}\n")

    # Show sample
    print("\nSAMPLE DATA (First 10 records):")
    print("-" * 70)
    display_cols = ['name']
    if 'party' in df.columns:
        display_cols.append('party')
    if 'constituency' in df.columns:
        display_cols.append('constituency')
    if 'dependents_count' in df.columns:
        display_cols.append('dependents_count')
    print(df[display_cols].head(10).to_string(index=False))
    print()

    # Statistics
    complete = df[df['dependents_count'].notna()]
    if len(complete) > 0:
        print(f"\nSTATISTICS:")
        print("-" * 70)
        print(f"MLAs with dependent data: {len(complete)}/{len(df)}")
        print(f"Average dependents: {complete['dependents_count'].mean():.2f}")
        print(f"Max dependents: {int(complete['dependents_count'].max())}")
        print()

    print(f"NOTE: This source (MyNeta affidavits) shows total dependents")
    print(f"but does NOT break down by gender (sons vs daughters).")
    print(f"For detailed family breakdown, need different sources (Wikipedia, news, etc.)")
    print()

    return filepath


def main():
    parser = argparse.ArgumentParser(
        description='Scrape West Bengal 2021 Assembly data from MyNeta'
    )
    parser.add_argument(
        '--limit',
        type=int,
        help='Limit number of candidates to scrape (for testing)'
    )

    args = parser.parse_args()

    print()
    print("=" * 70)
    print("WEST BENGAL 2021 ASSEMBLY DATA SCRAPER")
    print("Source: MyNeta (myneta.info/WestBengal2021)")
    print("=" * 70)
    print()

    scraper = WestBengalScraper()
    data = scraper.scrape_all(limit=args.limit)

    if data:
        filepath = save_data(data)

        print("=" * 70)
        print("SUCCESS!")
        print("=" * 70)
        print(f"\nData saved to: {filepath}")
        print("\nNext steps:")
        print("  1. Review the CSV file")
        print("  2. Run full scrape without --limit")
        print("  3. Enhance with Wikipedia data for sons/daughters breakdown")
        print()

    else:
        print("Failed to scrape data")


if __name__ == '__main__':
    main()
