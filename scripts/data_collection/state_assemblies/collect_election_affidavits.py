"""
Collect data from Election Commission affidavits via MyNeta.

This is often the most reliable source as candidates are legally required
to declare family information in their election affidavits.

MyNeta (myneta.info) aggregates and makes searchable all affidavit data
from the Election Commission of India.

Usage:
    python collect_election_affidavits.py --state maharashtra --year 2019
    python collect_election_affidavits.py --state "tamil nadu" --year 2021
"""

import argparse
import logging
from pathlib import Path
import pandas as pd
from bs4 import BeautifulSoup
import re
import sys

sys.path.append(str(Path(__file__).parent.parent / 'utilities'))
from scraping_utils import (
    RateLimitedSession,
    DataCollector,
    validate_family_data,
    extract_children_from_text
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AffidavitCollector(DataCollector):
    """
    Collect data from election affidavits via MyNeta.
    """

    def __init__(self, state: str, year: int, output_dir: str):
        super().__init__(output_dir, f'{state}_affidavits_{year}')
        self.state = state.lower().replace(' ', '')
        self.year = year
        self.base_url = f'https://myneta.info/{self.state}{year}/'

    def collect_candidate_list(self):
        """
        Get list of all candidates from MyNeta main page.
        """
        logger.info(f"Fetching candidate list for {self.state} {self.year}...")

        response = self.session.get(self.base_url)
        if not response or response.status_code != 200:
            logger.error(f"Failed to fetch {self.base_url}")
            return []

        soup = BeautifulSoup(response.content, 'html.parser')
        candidates = []

        # MyNeta typically has tables with candidate information
        # Look for tables with candidate details
        tables = soup.find_all('table')

        for table in tables:
            rows = table.find_all('tr')
            for row in rows[1:]:  # Skip header
                cells = row.find_all('td')
                if len(cells) >= 3:
                    # Typically: Name, Party, Constituency
                    name_cell = cells[0]
                    link = name_cell.find('a')

                    if link and 'href' in link.attrs:
                        candidate_info = {
                            'name': link.text.strip(),
                            'url': link['href'] if link['href'].startswith('http') else self.base_url + link['href'],
                            'party': cells[1].text.strip() if len(cells) > 1 else None,
                            'constituency': cells[2].text.strip() if len(cells) > 2 else None,
                        }
                        candidates.append(candidate_info)

        logger.info(f"Found {len(candidates)} candidates")
        return candidates

    def extract_family_info(self, candidate_url: str):
        """
        Extract family information from candidate affidavit page.
        """
        response = self.session.get(candidate_url)
        if not response or response.status_code != 200:
            return None

        soup = BeautifulSoup(response.content, 'html.parser')
        family_data = {}

        # Look for family information section
        # Common patterns in affidavits:
        # - Table with "Spouse and Dependents" information
        # - Sections labeled "Family Details"
        # - Tables showing children's names and relationships

        # Pattern 1: Look for tables with family/spouse information
        tables = soup.find_all('table')
        for table in tables:
            table_text = table.get_text().lower()
            if any(keyword in table_text for keyword in ['family', 'dependent', 'spouse', 'children']):
                # Count sons and daughters in the table
                rows = table.find_all('tr')
                sons = 0
                daughters = 0

                for row in rows:
                    row_text = row.get_text().lower()
                    if 'son' in row_text and 'daughter' not in row_text:
                        sons += 1
                    elif 'daughter' in row_text:
                        daughters += 1

                if sons > 0 or daughters > 0:
                    family_data['sons'] = sons
                    family_data['daughters'] = daughters

        # Pattern 2: Extract from general text
        page_text = soup.get_text()
        extracted = extract_children_from_text(page_text)

        if not family_data and (extracted['sons'] or extracted['daughters']):
            family_data = extracted

        # Look for explicit statements about children
        # e.g., "Number of children: 2 (1 son, 1 daughter)"
        children_pattern = r'number\s+of\s+children\s*:?\s*(\d+)'
        match = re.search(children_pattern, page_text, re.IGNORECASE)
        if match and not family_data:
            total_children = int(match.group(1))
            family_data['total_children'] = total_children

        return family_data

    def collect(self):
        """
        Main collection method.
        """
        # Get candidate list
        candidates = self.collect_candidate_list()

        if not candidates:
            logger.error("No candidates found. Check if the MyNeta URL is correct.")
            logger.info(f"Tried URL: {self.base_url}")
            logger.info("Please verify the state name and year are correct.")
            return None

        # Collect family data for each candidate
        results = []
        checkpoint_file = f'checkpoint_{self.state}_{self.year}.json'
        checkpoint = self.load_checkpoint(checkpoint_file)
        processed = checkpoint.get('processed', [])

        for i, candidate in enumerate(candidates):
            if candidate['name'] in processed:
                logger.info(f"Skipping already processed: {candidate['name']}")
                continue

            logger.info(f"Processing {i+1}/{len(candidates)}: {candidate['name']}")

            family_info = self.extract_family_info(candidate['url'])

            record = {
                'names': candidate['name'],
                'party': candidate.get('party'),
                'constituency': candidate.get('constituency'),
                'state': self.state.title(),
                'year': self.year,
            }

            if family_info:
                record.update(family_info)

            results.append(validate_family_data(record))

            # Update checkpoint every 10 records
            if (i + 1) % 10 == 0:
                processed.append(candidate['name'])
                checkpoint['processed'] = processed
                self.save_checkpoint(checkpoint, checkpoint_file)

        # Save final results
        if results:
            df = pd.DataFrame(results)
            output_file = f'{self.state}_assembly_{self.year}.csv'
            self.save_csv(df, output_file)
            logger.info(f"Saved data for {len(df)} candidates")

            # Print summary
            from scraping_utils import calculate_summary_stats
            stats = calculate_summary_stats(df)
            logger.info(f"Summary: {stats}")

            return df
        else:
            logger.warning("No data collected")
            return None


def main():
    parser = argparse.ArgumentParser(
        description='Collect data from election affidavits via MyNeta'
    )
    parser.add_argument(
        '--state',
        required=True,
        help='State name (e.g., "maharashtra", "tamil nadu")'
    )
    parser.add_argument(
        '--year',
        type=int,
        required=True,
        help='Election year (e.g., 2019, 2021)'
    )
    parser.add_argument(
        '--output',
        default='../../../data/',
        help='Output directory'
    )

    args = parser.parse_args()

    # Create state-specific output directory
    state_clean = args.state.lower().replace(' ', '_')
    output_dir = Path(args.output) / state_clean

    collector = AffidavitCollector(args.state, args.year, str(output_dir))
    collector.collect()


if __name__ == '__main__':
    main()
