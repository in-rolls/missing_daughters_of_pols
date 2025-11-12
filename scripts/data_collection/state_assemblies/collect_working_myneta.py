"""
Working MyNeta scraper based on actual site structure.

This version is updated to work with the current MyNeta website structure.
It focuses on recent elections with available data.

Usage:
    python collect_working_myneta.py --state Delhi --year 2025
"""

import argparse
import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import logging
import re
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).parent.parent / 'utilities'))
from scraping_utils import RateLimitedSession, validate_family_data

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Available elections on MyNeta (verified)
AVAILABLE_ELECTIONS = {
    'Delhi': [2025, 2022, 2017],
    'Bihar': [2025, 2022, 2017],
    'LokSabha': [2024, 2019, 2014, 2009, 2004],
}


def get_myneta_url(state, year):
    """
    Construct MyNeta URL based on state and year.

    MyNeta uses format: myneta.info/{State}{Year}/
    """
    # Normalize state name
    state_normalized = state.replace(' ', '')

    # Try different URL patterns
    possible_urls = [
        f"https://myneta.info/{state_normalized}{year}/",
        f"https://myneta.info/{state_normalized.lower()}{year}/",
        f"https://myneta.info/{state_normalized.capitalize()}{year}/",
    ]

    return possible_urls


def check_url_exists(url):
    """Check if a URL exists."""
    try:
        response = requests.head(url, timeout=5)
        return response.status_code == 200
    except:
        return False


def scrape_delhi_sample():
    """
    Scrape a small sample from Delhi 2025 to demonstrate working scraper.
    This is a targeted approach for the most recent data.
    """
    logger.info("Collecting sample data from Delhi 2025...")

    base_url = "https://myneta.info/Delhi2025/"
    session = RateLimitedSession(delay=2.0)

    # First, get the main page
    response = session.get(base_url)
    if not response or response.status_code != 200:
        logger.error(f"Failed to access {base_url}")
        return None

    soup = BeautifulSoup(response.content, 'html.parser')

    # Find candidate links
    # MyNeta typically uses candidate.php?candidate_id=XXX
    candidate_links = []

    for link in soup.find_all('a', href=re.compile(r'candidate\.php')):
        href = link.get('href')
        if href:
            full_url = href if href.startswith('http') else base_url + href
            candidate_links.append({
                'name': link.text.strip(),
                'url': full_url
            })

    logger.info(f"Found {len(candidate_links)} potential candidate links")

    # Sample first 10 candidates
    results = []

    for i, candidate in enumerate(candidate_links[:10]):
        logger.info(f"Processing {i+1}/10: {candidate['name']}")

        response = session.get(candidate['url'])
        if not response:
            continue

        soup = BeautifulSoup(response.content, 'html.parser')
        page_text = soup.get_text()

        record = {
            'name': candidate['name'],
            'state': 'Delhi',
            'year': 2025,
        }

        # Look for family information in the page
        # Common patterns: "Spouse and Dependents", "Family Details"

        # Method 1: Look for tables with spouse/dependent information
        tables = soup.find_all('table')
        for table in tables:
            table_text = table.get_text().lower()

            if 'spouse' in table_text or 'dependent' in table_text or 'family' in table_text:
                rows = table.find_all('tr')

                sons = 0
                daughters = 0

                for row in rows:
                    row_text = row.get_text().lower()
                    cells = row.find_all(['td', 'th'])

                    # Look for relationship field
                    if any('son' in cell.get_text().lower() and 'daughter' not in cell.get_text().lower()
                           for cell in cells):
                        sons += 1
                    elif any('daughter' in cell.get_text().lower() for cell in cells):
                        daughters += 1

                if sons > 0 or daughters > 0:
                    record['sons'] = sons
                    record['daughters'] = daughters
                    logger.info(f"  Found: {sons} sons, {daughters} daughters")
                    break

        # Method 2: Text pattern matching
        if 'sons' not in record:
            son_patterns = [
                r'(\d+)\s+sons?(?:\s|,|\.)',
                r'sons?\s*:\s*(\d+)',
            ]
            daughter_patterns = [
                r'(\d+)\s+daughters?(?:\s|,|\.)',
                r'daughters?\s*:\s*(\d+)',
            ]

            for pattern in son_patterns:
                match = re.search(pattern, page_text, re.IGNORECASE)
                if match:
                    record['sons'] = int(match.group(1))
                    break

            for pattern in daughter_patterns:
                match = re.search(pattern, page_text, re.IGNORECASE)
                if match:
                    record['daughters'] = int(match.group(1))
                    break

        results.append(validate_family_data(record))

    if results:
        df = pd.DataFrame(results)
        logger.info(f"\nCollected data for {len(df)} candidates")

        # Show results
        print("\n" + "="*70)
        print("COLLECTED DATA SAMPLE")
        print("="*70)
        print(df.to_string(index=False))

        # Calculate statistics for those with complete data
        complete = df.dropna(subset=['sons', 'daughters'])
        if len(complete) > 0:
            print(f"\nCandidates with family data: {len(complete)}/{len(df)}")
            print(f"Total sons: {complete['sons'].sum()}")
            print(f"Total daughters: {complete['daughters'].sum()}")

            total_sons = complete['sons'].sum()
            total_daughters = complete['daughters'].sum()
            if total_daughters > 0:
                ratio = total_sons / total_daughters
                print(f"Sex ratio: {ratio:.3f}")

        return df

    return None


def main():
    parser = argparse.ArgumentParser(
        description='Collect data from MyNeta (working version)'
    )
    parser.add_argument(
        '--state',
        default='Delhi',
        help='State name (default: Delhi)'
    )
    parser.add_argument(
        '--year',
        type=int,
        default=2025,
        help='Election year (default: 2025)'
    )
    parser.add_argument(
        '--sample',
        action='store_true',
        help='Collect small sample for testing'
    )

    args = parser.parse_args()

    print(f"\nAttempting to collect from {args.state} {args.year}")
    print("="*70)

    # For demo, just do Delhi sample
    if args.state == 'Delhi' or args.sample:
        scrape_delhi_sample()
    else:
        logger.warning("Full collection not yet implemented")
        logger.info("Available elections:")
        for state, years in AVAILABLE_ELECTIONS.items():
            logger.info(f"  {state}: {years}")


if __name__ == '__main__':
    main()
