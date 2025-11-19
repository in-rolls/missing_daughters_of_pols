"""
Scraper for Kerala Legislative Assembly

Data source: http://www.niyamasabha.org/codes/members.htm
Each member has a PDF with biographical data including children information.

Output: Saves to data/kerala/kerala_assembly_current.json and .csv
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd
import json
import time
import logging
from pathlib import Path
from datetime import datetime
import re

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


def get_member_links():
    """Get list of all current Kerala Assembly members and their profile links."""

    base_url = "http://www.niyamasabha.org"
    members_url = f"{base_url}/codes/members.htm"

    logger.info(f"Fetching members list from {members_url}")

    try:
        response = requests.get(members_url, timeout=15)

        if response.status_code != 200:
            logger.error(f"Failed to fetch members page: {response.status_code}")
            return []

        soup = BeautifulSoup(response.content, 'html.parser')

        members = []

        # Find all member profile PDF links
        # Pattern: 15kla/Members profile mal/*.pdf
        for link in soup.find_all('a', href=True):
            href = link.get('href', '')
            text = link.get_text(strip=True)

            # Look for member profile PDFs
            if 'Members%20profile%20mal' in href or 'Members profile mal' in href:
                # Build full URL
                if href.startswith('http'):
                    full_url = href
                else:
                    # Remove leading ../ if present
                    clean_href = href.lstrip('../')
                    full_url = f"{base_url}/codes/{clean_href}"

                # Extract member name from link text or filename
                member_name = text if text else href.split('/')[-1].replace('.pdf', '').replace('%20', ' ')

                members.append({
                    'name': member_name,
                    'pdf_url': full_url,
                    'state': 'Kerala'
                })

        logger.info(f"Found {len(members)} member profile PDFs")
        return members

    except Exception as e:
        logger.error(f"Error fetching members list: {e}")
        return []


def extract_children_from_pdf_url(pdf_url):
    """
    Extract children information from member PDF.
    Returns dict with name, sons, daughters.
    """

    logger.info(f"  Fetching PDF: {pdf_url}")

    try:
        # Download PDF
        response = requests.get(pdf_url, timeout=15)

        if response.status_code != 200:
            logger.warning(f"  Failed to download PDF: {response.status_code}")
            return None

        # For now, we'll extract text from PDF
        # Since PDF extraction has dependency issues, let's try a simpler approach:
        # Check if there's an HTML version or alternative format

        # Try to find HTML version by replacing .pdf with .html or similar
        html_url = pdf_url.replace('.pdf', '.html').replace('.PDF', '.html')

        try:
            html_response = requests.get(html_url, timeout=10)
            if html_response.status_code == 200:
                return extract_children_from_html(html_response.text)
        except:
            pass

        logger.warning(f"  PDF extraction not implemented yet (dependency issues)")
        return None

    except Exception as e:
        logger.error(f"  Error processing PDF: {e}")
        return None


def extract_children_from_html(html_text):
    """Extract children data from HTML text."""

    soup = BeautifulSoup(html_text, 'html.parser')
    text = soup.get_text()

    # Look for patterns like:
    # "Sons: 2" "Daughters: 1"
    # "Children: 2 sons, 1 daughter"
    # "Family: 2 sons and 1 daughter"

    data = {}

    # Try various patterns
    son_patterns = [
        r'sons?\s*[:\-]\s*(\d+)',
        r'(\d+)\s*sons?',
        r'male\s*child(?:ren)?\s*[:\-]\s*(\d+)',
    ]

    daughter_patterns = [
        r'daughters?\s*[:\-]\s*(\d+)',
        r'(\d+)\s*daughters?',
        r'female\s*child(?:ren)?\s*[:\-]\s*(\d+)',
    ]

    for pattern in son_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            data['sons'] = int(match.group(1))
            break

    for pattern in daughter_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            data['daughters'] = int(match.group(1))
            break

    return data if data else None


def scrape_kerala_members(test_mode=False):
    """Main scraping function."""

    logger.info("Starting Kerala Assembly scraper...")
    logger.info("="*70)

    # Get member links
    members = get_member_links()

    if not members:
        logger.error("No members found!")
        return []

    # Limit in test mode
    if test_mode:
        members = members[:10]
        logger.info(f"TEST MODE: Processing only {len(members)} members")

    logger.info(f"\nCollecting data for {len(members)} members...")

    # For now, just return the member data with PDF URLs
    # PDF extraction can be done separately
    all_data = []

    for i, member in enumerate(members):
        logger.info(f"  [{i+1}/{len(members)}] {member['name']}")

        all_data.append(member)

        # Note: PDF extraction would go here
        # Children data (sons/daughters) needs to be extracted from PDF

    logger.info(f"\nCollected {len(all_data)} members")
    logger.info("Note: PDF extraction not implemented. PDF URLs collected for manual processing.")
    return all_data


def save_data(data, output_dir='../../data/kerala'):
    """Save collected data."""

    if not data:
        logger.error("No data to save")
        return None

    # Create output directory
    output_path = Path(__file__).parent / output_dir
    output_path.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

    # Save JSON
    json_file = output_path / f'kerala_assembly_{timestamp}.json'
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump({'members': data, 'count': len(data)}, f, ensure_ascii=False, indent=2)

    logger.info(f"Saved JSON: {json_file}")

    # Save CSV
    df = pd.DataFrame(data)
    csv_file = output_path / f'kerala_assembly_{timestamp}.csv'
    df.to_csv(csv_file, index=False)

    logger.info(f"Saved CSV: {csv_file}")

    # Show sample
    print("\n" + "="*70)
    print("SAMPLE DATA")
    print("="*70)
    print(df.head(10).to_string(index=False))

    return csv_file


def main():
    import argparse

    parser = argparse.ArgumentParser(description='Scrape Kerala Assembly members')
    parser.add_argument('--test', action='store_true', help='Test mode (first 10 members only)')
    args = parser.parse_args()

    print("\n" + "="*70)
    print("KERALA LEGISLATIVE ASSEMBLY SCRAPER")
    print("="*70)
    print()

    data = scrape_kerala_members(test_mode=args.test)

    if data:
        save_data(data)
        print("\n✓ Scraping complete!")
    else:
        print("\n✗ No data collected")


if __name__ == '__main__':
    main()
