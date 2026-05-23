"""
Wikipedia scraper for Indian state assembly members and their family data.
Scrapes member lists and biographical pages to extract children information.
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd
import json
import time
import re
from pathlib import Path
import logging
from typing import Dict, List, Optional, Tuple
import sys

# Add utilities to path
sys.path.append(str(Path(__file__).parent.parent))
from utilities.scraping_utils import RateLimitedSession, extract_children_from_text

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class WikipediaAssemblyScraper:
    """Scraper for Indian state assembly Wikipedia pages."""

    # Wikipedia URLs for various state assemblies and legislative councils
    # These are for current/recent assemblies
    STATE_URLS = {
        'maharashtra_council': 'https://en.wikipedia.org/wiki/List_of_members_of_the_Maharashtra_Legislative_Council',
        'maharashtra_assembly': 'https://en.wikipedia.org/wiki/List_of_members_of_the_15th_Maharashtra_Legislative_Assembly',
        'karnataka_assembly': 'https://en.wikipedia.org/wiki/List_of_members_of_the_16th_Karnataka_Legislative_Assembly',
        'tamil_nadu_assembly': 'https://en.wikipedia.org/wiki/List_of_members_of_the_16th_Tamil_Nadu_Legislative_Assembly',
        'kerala_assembly': 'https://en.wikipedia.org/wiki/List_of_members_of_the_15th_Kerala_Legislative_Assembly',
        'uttar_pradesh_assembly': 'https://en.wikipedia.org/wiki/List_of_members_of_the_18th_Uttar_Pradesh_Legislative_Assembly',
        'west_bengal_assembly': 'https://en.wikipedia.org/wiki/List_of_members_of_the_17th_West_Bengal_Legislative_Assembly',
        'rajasthan_assembly': 'https://en.wikipedia.org/wiki/List_of_members_of_the_16th_Rajasthan_Legislative_Assembly',
        'madhya_pradesh_assembly': 'https://en.wikipedia.org/wiki/List_of_members_of_the_16th_Madhya_Pradesh_Legislative_Assembly',
        'telangana_assembly': 'https://en.wikipedia.org/wiki/List_of_members_of_the_3rd_Telangana_Legislative_Assembly',
        'punjab_assembly': 'https://en.wikipedia.org/wiki/List_of_members_of_the_16th_Punjab_Legislative_Assembly',
        'haryana_assembly': 'https://en.wikipedia.org/wiki/List_of_members_of_the_14th_Haryana_Legislative_Assembly',
        'bihar_assembly': 'https://en.wikipedia.org/wiki/List_of_members_of_the_17th_Bihar_Legislative_Assembly',
        'odisha_assembly': 'https://en.wikipedia.org/wiki/List_of_members_of_the_17th_Odisha_Legislative_Assembly',
        'assam_assembly': 'https://en.wikipedia.org/wiki/List_of_members_of_the_15th_Assam_Legislative_Assembly',
    }

    def __init__(self, output_dir: str = 'data/wikipedia_state_assemblies'):
        """
        Initialize scraper.

        Args:
            output_dir: Directory to save scraped data
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.session = RateLimitedSession(delay=1.0)
        self.base_url = 'https://en.wikipedia.org'

    def get_page(self, url: str) -> Optional[BeautifulSoup]:
        """
        Fetch and parse a Wikipedia page.

        Args:
            url: URL to fetch

        Returns:
            BeautifulSoup object or None if failed
        """
        headers = {
            'User-Agent': 'Mozilla/5.0 (compatible; ResearchBot/1.0; +https://github.com/in-rolls/missing_daughters_of_pols)'
        }

        response = self.session.get(url, headers=headers)
        if response and response.status_code == 200:
            return BeautifulSoup(response.content, 'lxml')
        else:
            logger.error(f"Failed to fetch {url}")
            return None

    def extract_member_links(self, soup: BeautifulSoup) -> List[Dict[str, str]]:
        """
        Extract member names and links from assembly list page.

        Args:
            soup: BeautifulSoup object of the list page

        Returns:
            List of dicts with 'name' and 'url' keys
        """
        members = []

        # Words that indicate non-person pages (parties, constituencies, etc.)
        exclude_keywords = [
            'assembly', 'constituency', 'party', 'lok_sabha', 'vidhan',
            'bjp', 'inc', 'congress', 'ncp', 'shiv_sena', 'shs', 'aap',
            'tmc', 'dmk', 'aiadmk', 'jd', 'bsp', 'sp', 'tdp', 'ysrcp',
            'list_of', 'category:', 'election', 'district', 'division'
        ]

        # Find all tables (member lists are usually in tables)
        tables = soup.find_all('table', class_='wikitable')

        for table in tables:
            rows = table.find_all('tr')
            for row in rows[1:]:  # Skip header row
                cells = row.find_all(['td', 'th'])

                # Look for links to member pages
                for cell in cells:
                    links = cell.find_all('a', href=True)
                    for link in links:
                        href = link.get('href', '')
                        # Filter for actual member pages (not red links, not external)
                        if href.startswith('/wiki/') and ':' not in href and 'redlink' not in link.get('class', []):
                            member_name = link.get_text(strip=True)
                            member_url = self.base_url + href

                            # Check if URL contains excluded keywords
                            href_lower = href.lower()
                            if any(keyword in href_lower for keyword in exclude_keywords):
                                continue

                            # Avoid duplicates and non-person pages
                            # Person names typically have multiple words or are at least 3 chars
                            if member_name and len(member_name) >= 3:
                                members.append({
                                    'name': member_name,
                                    'url': member_url
                                })

        # Remove duplicates based on URL
        seen_urls = set()
        unique_members = []
        for member in members:
            if member['url'] not in seen_urls:
                seen_urls.add(member['url'])
                unique_members.append(member)

        logger.info(f"Found {len(unique_members)} unique member links")
        return unique_members

    def extract_family_data_from_bio(self, soup: BeautifulSoup, member_name: str) -> Dict:
        """
        Extract family information from a member's biographical page.

        Args:
            soup: BeautifulSoup object of member's page
            member_name: Name of the member

        Returns:
            Dict with family information
        """
        data = {
            'name': member_name,
            'sons': None,
            'daughters': None,
            'spouse': None,
            'children_names': [],
            'raw_family_text': None
        }

        # Look for infobox (common structure for biographical pages)
        infobox = soup.find('table', class_='infobox')

        if infobox:
            rows = infobox.find_all('tr')
            for row in rows:
                header = row.find('th')
                if header:
                    header_text = header.get_text(strip=True).lower()

                    # Look for children/family related fields
                    if any(keyword in header_text for keyword in ['child', 'son', 'daughter', 'family']):
                        cell = row.find('td')
                        if cell:
                            family_text = cell.get_text(strip=True)
                            data['raw_family_text'] = family_text

                            # Extract structured data
                            children_info = extract_children_from_text(family_text)
                            data['sons'] = children_info.get('sons')
                            data['daughters'] = children_info.get('daughters')

                            # Try to extract individual child names
                            # Children are often listed with bullet points or line breaks
                            children_links = cell.find_all('a')
                            for link in children_links:
                                child_name = link.get_text(strip=True)
                                if child_name:
                                    data['children_names'].append(child_name)

                    # Look for spouse
                    if 'spouse' in header_text or 'partner' in header_text:
                        cell = row.find('td')
                        if cell:
                            data['spouse'] = cell.get_text(strip=True)

        # Also search in the article text for family information
        content = soup.find('div', class_='mw-parser-output')
        if content and not data['raw_family_text']:
            # Look for paragraphs mentioning family
            paragraphs = content.find_all('p')
            for p in paragraphs[:5]:  # Check first few paragraphs
                text = p.get_text()
                if any(keyword in text.lower() for keyword in ['son', 'daughter', 'child', 'married', 'wife', 'husband']):
                    data['raw_family_text'] = text
                    children_info = extract_children_from_text(text)
                    if children_info.get('sons') is not None or children_info.get('daughters') is not None:
                        data['sons'] = children_info.get('sons')
                        data['daughters'] = children_info.get('daughters')
                        break

        return data

    def scrape_state(self, state_key: str) -> pd.DataFrame:
        """
        Scrape a specific state assembly.

        Args:
            state_key: Key from STATE_URLS dict

        Returns:
            DataFrame with member family data
        """
        if state_key not in self.STATE_URLS:
            logger.error(f"Unknown state: {state_key}")
            return pd.DataFrame()

        url = self.STATE_URLS[state_key]
        logger.info(f"\nScraping {state_key} from {url}")

        # Get the list page
        soup = self.get_page(url)
        if not soup:
            return pd.DataFrame()

        # Extract member links
        members = self.extract_member_links(soup)
        logger.info(f"Found {len(members)} members for {state_key}")

        # Scrape each member's bio page
        results = []
        for i, member in enumerate(members[:100], 1):  # Limit to 100 per state for now
            logger.info(f"[{i}/{min(len(members), 100)}] Scraping {member['name']}")

            bio_soup = self.get_page(member['url'])
            if bio_soup:
                family_data = self.extract_family_data_from_bio(bio_soup, member['name'])
                family_data['url'] = member['url']
                family_data['state'] = state_key
                results.append(family_data)

            # Be respectful with rate limiting
            time.sleep(0.5)

        df = pd.DataFrame(results)

        # Save state-specific results
        output_file = self.output_dir / f'{state_key}.csv'
        df.to_csv(output_file, index=False)
        logger.info(f"Saved {len(df)} records to {output_file}")

        return df

    def scrape_all_states(self, states: Optional[List[str]] = None) -> pd.DataFrame:
        """
        Scrape multiple states.

        Args:
            states: List of state keys to scrape. If None, scrape all.

        Returns:
            Combined DataFrame with all results
        """
        if states is None:
            states = list(self.STATE_URLS.keys())

        all_results = []
        for state_key in states:
            df = self.scrape_state(state_key)
            if not df.empty:
                all_results.append(df)

        # Combine all results
        if all_results:
            combined_df = pd.concat(all_results, ignore_index=True)

            # Save combined results
            output_file = self.output_dir / 'all_states_combined.csv'
            combined_df.to_csv(output_file, index=False)
            logger.info(f"\nSaved combined results ({len(combined_df)} records) to {output_file}")

            # Generate summary statistics
            self.print_summary(combined_df)

            return combined_df

        return pd.DataFrame()

    def print_summary(self, df: pd.DataFrame):
        """Print summary statistics."""
        logger.info("\n" + "="*60)
        logger.info("SUMMARY STATISTICS")
        logger.info("="*60)

        logger.info(f"\nTotal members scraped: {len(df)}")
        logger.info(f"States covered: {df['state'].nunique()}")

        # Count records with family data
        has_sons = df['sons'].notna().sum()
        has_daughters = df['daughters'].notna().sum()
        has_any_children_data = ((df['sons'].notna()) | (df['daughters'].notna())).sum()

        logger.info(f"\nRecords with sons data: {has_sons}")
        logger.info(f"Records with daughters data: {has_daughters}")
        logger.info(f"Records with any children data: {has_any_children_data}")
        logger.info(f"Coverage: {has_any_children_data/len(df)*100:.1f}%")

        # Calculate sex ratio for records with complete data
        complete_data = df[(df['sons'].notna()) & (df['daughters'].notna())]
        if len(complete_data) > 0:
            total_sons = complete_data['sons'].sum()
            total_daughters = complete_data['daughters'].sum()
            if total_daughters > 0:
                sex_ratio = total_sons / total_daughters
                logger.info(f"\nRecords with complete data: {len(complete_data)}")
                logger.info(f"Total sons: {int(total_sons)}")
                logger.info(f"Total daughters: {int(total_daughters)}")
                logger.info(f"Sex ratio (sons/daughters): {sex_ratio:.2f}")

        # By state breakdown
        logger.info("\nBreakdown by state:")
        for state in df['state'].unique():
            state_df = df[df['state'] == state]
            state_complete = state_df[(state_df['sons'].notna()) & (state_df['daughters'].notna())]
            logger.info(f"  {state}: {len(state_df)} members, {len(state_complete)} with complete data")


def main():
    """Main function to run the scraper."""
    scraper = WikipediaAssemblyScraper()

    # Test on 5 states first
    test_states = [
        'maharashtra_council',
        'karnataka_assembly',
        'tamil_nadu_assembly',
        'kerala_assembly',
        'punjab_assembly'
    ]

    logger.info("Starting Wikipedia scrape for Indian state assemblies")
    logger.info(f"Testing on {len(test_states)} states: {', '.join(test_states)}")

    results = scraper.scrape_all_states(states=test_states)

    logger.info("\nScraping complete!")
    return results


if __name__ == '__main__':
    main()
