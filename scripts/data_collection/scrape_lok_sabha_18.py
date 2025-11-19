"""
Scraper for 18th Lok Sabha (2024) Member Family Data

Collects sons and daughters data for all 543 MPs elected in 2024.
This is NEW data not yet in the repository (only has LS 12-17).

Usage:
    python scrape_lok_sabha_18.py
    python scrape_lok_sabha_18.py --limit 10  # Test with first 10 only
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd
import json
import time
import re
import argparse
from pathlib import Path
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


class LokSabha18Scraper:
    """Scraper for 18th Lok Sabha (2024) data"""

    def __init__(self):
        self.base_url = "https://sansad.in"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })

    def get_members_list(self):
        """Get list of all 18th LS members"""

        url = f"{self.base_url}/ls/members"

        logger.info(f"Fetching members list from: {url}")

        try:
            response = self.session.get(url, timeout=15)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')

            # Look for member links - typically in format /ls/members/biography/{id}
            members = []

            for link in soup.find_all('a', href=re.compile(r'/ls/members/biography/\d+')):
                href = link['href']
                member_id = re.search(r'/biography/(\d+)', href)

                if member_id:
                    members.append({
                        'name': link.text.strip(),
                        'member_id': member_id.group(1),
                        'url': f"{self.base_url}{href}" if not href.startswith('http') else href
                    })

            # Deduplicate
            seen_ids = set()
            unique_members = []
            for m in members:
                if m['member_id'] not in seen_ids:
                    seen_ids.add(m['member_id'])
                    unique_members.append(m)

            logger.info(f"Found {len(unique_members)} members")
            return unique_members

        except Exception as e:
            logger.error(f"Error fetching members list: {e}")
            return []

    def scrape_member_biodata(self, member):
        """Scrape individual member biodata for family information"""

        logger.info(f"Scraping: {member['name']} (ID: {member['member_id']})")

        try:
            response = self.session.get(member['url'], timeout=15)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')
            page_text = soup.get_text()

            record = {
                'name': member['name'],
                'member_id': member['member_id'],
                'lok_sabha': 18,
                'year': 2024
            }

            # Extract party, constituency from page
            # Look for patterns in the biodata

            # Constituency
            const_match = re.search(r'Constituency[:\s]+([A-Za-z\s\(\)]+)', page_text, re.IGNORECASE)
            if const_match:
                record['constituency'] = const_match.group(1).strip()

            # Party
            party_match = re.search(r'Party[:\s]+([A-Za-z\(\)\s]+)', page_text, re.IGNORECASE)
            if party_match:
                record['party'] = party_match.group(1).strip()

            # State
            state_match = re.search(r'State[:\s]+([A-Za-z\s]+)', page_text, re.IGNORECASE)
            if state_match:
                record['state'] = state_match.group(1).strip()

            # Look for family information
            # Pattern: "m. [spouse name], [year]: X s. and Y d."
            # Or: "X sons and Y daughters"

            sons = None
            daughters = None

            # Pattern 1: "2 s. and 3 d." format (common in official biographies)
            family_pattern1 = re.search(r'(\d+)\s*s\.\s*and\s*(\d+)\s*d\.', page_text, re.IGNORECASE)
            if family_pattern1:
                sons = int(family_pattern1.group(1))
                daughters = int(family_pattern1.group(2))

            # Pattern 2: "3 s." or "2 d." separately
            if sons is None:
                son_pattern = re.search(r'(\d+)\s*s\.(?:\s|;|,|$)', page_text, re.IGNORECASE)
                if son_pattern:
                    sons = int(son_pattern.group(1))

            if daughters is None:
                daughter_pattern = re.search(r'(\d+)\s*d\.(?:\s|;|,|$)', page_text, re.IGNORECASE)
                if daughter_pattern:
                    daughters = int(daughter_pattern.group(1))

            # Pattern 3: "2 sons and 3 daughters"
            if sons is None or daughters is None:
                sons_full = re.search(r'(\d+)\s+sons?(?:\s|,|\.)', page_text, re.IGNORECASE)
                daughters_full = re.search(r'(\d+)\s+daughters?(?:\s|,|\.)', page_text, re.IGNORECASE)

                if sons is None and sons_full:
                    sons = int(sons_full.group(1))
                if daughters is None and daughters_full:
                    daughters = int(daughters_full.group(1))

            record['numberOfSons'] = sons if sons is not None else 0
            record['numberOfDaughters'] = daughters if daughters is not None else 0

            if sons is not None or daughters is not None:
                logger.info(f"  ✓ Found: {record['numberOfSons']} sons, {record['numberOfDaughters']} daughters")
            else:
                logger.info(f"  - No family data found")

            time.sleep(2)  # Rate limiting

            return record

        except Exception as e:
            logger.error(f"Error scraping {member['name']}: {e}")
            return {
                'name': member['name'],
                'member_id': member['member_id'],
                'lok_sabha': 18,
                'year': 2024,
                'error': str(e)
            }

    def scrape_all(self, limit=None):
        """Scrape all members"""

        members = self.get_members_list()

        if not members:
            logger.error("No members found")
            return None

        if limit:
            members = members[:limit]
            logger.info(f"Limiting to first {limit} members for testing")

        data = []

        for i, member in enumerate(members):
            logger.info(f"Progress: {i+1}/{len(members)}")
            record = self.scrape_member_biodata(member)
            data.append(record)

            # Checkpoint every 50 records
            if (i + 1) % 50 == 0:
                logger.info(f"Checkpoint: Scraped {i+1} records")

        return data


def save_data(data, output_dir='../../data/lok_sabha'):
    """Save collected data to JSON (matching existing LS format)"""

    if not data:
        logger.error("No data to save")
        return None

    # Create output directory
    output_path = Path(__file__).parent / output_dir
    output_path.mkdir(parents=True, exist_ok=True)

    # Save as JSON (matching existing ls_12.json, ls_17.json format)
    filename = 'ls_18.json'
    filepath = output_path / filename

    # Wrap in structure similar to existing LS files
    output_data = {
        'metaDatasDto': {
            'currentPageNumber': 1,
            'perPageSize': len(data),
            'totalElements': len(data),
            'totalPages': 1
        },
        'membersDtoList': data
    }

    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)

    logger.info(f"\n{'='*70}")
    logger.info(f"DATA SAVED TO: {filepath}")
    logger.info(f"Total records: {len(data)}")
    logger.info(f"{'='*70}\n")

    # Also save as CSV for easy viewing
    df = pd.DataFrame(data)
    csv_filepath = output_path / 'ls_18.csv'
    df.to_csv(csv_filepath, index=False)
    logger.info(f"Also saved CSV to: {csv_filepath}\n")

    # Show sample
    print("\nSAMPLE DATA (First 10 members):")
    print("-" * 70)
    display_cols = ['name']
    if 'party' in df.columns:
        display_cols.append('party')
    if 'constituency' in df.columns:
        display_cols.append('constituency')
    display_cols.extend(['numberOfSons', 'numberOfDaughters'])
    print(df[display_cols].head(10).to_string(index=False))
    print()

    # Statistics
    complete = df[(df['numberOfSons'].notna()) & (df['numberOfDaughters'].notna())]
    if len(complete) > 0:
        total_sons = complete['numberOfSons'].sum()
        total_daughters = complete['numberOfDaughters'].sum()
        total_children = total_sons + total_daughters

        print(f"\nSTATISTICS:")
        print("-" * 70)
        print(f"MPs with family data: {len(complete)}/{len(df)}")
        print(f"Total sons: {int(total_sons)}")
        print(f"Total daughters: {int(total_daughters)}")
        print(f"Total children: {int(total_children)}")

        if total_daughters > 0:
            sex_ratio = total_sons / total_daughters
            prop_daughters = total_daughters / total_children
            print(f"Sex ratio (sons/daughters): {sex_ratio:.3f}")
            print(f"Proportion daughters: {prop_daughters:.3f}")
        print()

    return filepath


def main():
    parser = argparse.ArgumentParser(
        description='Scrape 18th Lok Sabha (2024) family data'
    )
    parser.add_argument(
        '--limit',
        type=int,
        help='Limit number of members to scrape (for testing)'
    )

    args = parser.parse_args()

    print()
    print("=" * 70)
    print("18TH LOK SABHA (2024) DATA SCRAPER")
    print("Source: sansad.in")
    print("Target: 543 MPs (NEW data not yet in repository)")
    print("=" * 70)
    print()

    scraper = LokSabha18Scraper()
    data = scraper.scrape_all(limit=args.limit)

    if data:
        filepath = save_data(data)

        print("=" * 70)
        print("SUCCESS!")
        print("=" * 70)
        print(f"\nData saved to: {filepath}")
        print("\nNext steps:")
        print("  1. Review the JSON/CSV files")
        print("  2. Run full scrape without --limit for all 543 MPs")
        print("  3. Combine with existing LS 12-17 data for analysis")
        print()

    else:
        print("Failed to scrape data")


if __name__ == '__main__':
    main()
