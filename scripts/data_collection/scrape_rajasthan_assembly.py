"""
Scraper for Rajasthan Legislative Assembly

Data source: https://assembly.rajasthan.gov.in/Containers/Members/Contacts.aspx
Multi-page member directory with detailed profile pages including family/children information in Hindi.

Output: Saves to data/rajasthan/rajasthan_assembly_current.json and .csv
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
from urllib.parse import urljoin, parse_qs, urlparse

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


class RajasthanAssemblyScraper:
    """Scraper for Rajasthan Assembly members data."""

    def __init__(self):
        self.base_url = "https://assembly.rajasthan.gov.in"
        self.members_url = f"{self.base_url}/Containers/Members/Contacts.aspx"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })

    def get_viewstate_data(self, soup):
        """Extract ASP.NET viewstate and validation data from the page."""
        viewstate = {}

        # Get all common ASP.NET hidden fields
        fields = ['__VIEWSTATE', '__VIEWSTATEGENERATOR', '__EVENTVALIDATION', '__EVENTTARGET', '__EVENTARGUMENT']

        for field in fields:
            element = soup.find('input', {'name': field})
            if element:
                viewstate[field] = element.get('value', '')

        return viewstate

    def fetch_members_list(self):
        """Fetch the list of all members from the main page."""

        logger.info(f"Fetching members list from {self.members_url}")

        try:
            response = self.session.get(self.members_url, timeout=30)

            if response.status_code != 200:
                logger.error(f"Failed to fetch members page: {response.status_code}")
                return []

            soup = BeautifulSoup(response.content, 'html.parser')

            members = []

            # Look for member data in the table
            # The page uses DataTables, so data might be in the HTML or loaded via AJAX

            # Find the main data table
            table = soup.find('table', {'id': re.compile(r'GridView|DataTable|gv.*Member', re.I)})

            if not table:
                # Try finding any table with member data
                tables = soup.find_all('table')
                for t in tables:
                    # Check if table has member-like data (names, phone numbers, etc.)
                    text = t.get_text()
                    if 'Mobile' in text or 'Email' in text or 'Constituency' in text:
                        table = t
                        break

            if table:
                logger.info("Found member table in HTML")
                members = self._parse_members_from_table(table, soup)
            else:
                logger.warning("Could not find member table, page might use AJAX")
                # Try to find JavaScript data or AJAX endpoints
                members = self._try_ajax_approach(soup)

            logger.info(f"Found {len(members)} members")
            return members

        except Exception as e:
            logger.error(f"Error fetching members list: {e}", exc_info=True)
            return []

    def _parse_members_from_table(self, table, soup):
        """Parse member data from HTML table."""

        members = []
        rows = table.find_all('tr')

        for row in rows[1:]:  # Skip header row
            cells = row.find_all(['td', 'th'])

            if len(cells) < 3:
                continue

            member_data = {}

            # Look for clickable member name
            name_link = row.find('a', id=re.compile(r'btnmember'))

            if name_link:
                member_data['name'] = name_link.get_text(strip=True)

                # Get the link - it should be a JavaScript postback
                href = name_link.get('href', '')

                if 'javascript:' in href.lower():
                    # Extract the parameter from JavaScript call
                    match = re.search(r"['\"]([^'\"]+)['\"]", href)
                    if match:
                        member_data['detail_link_type'] = 'postback'
                        member_data['detail_link_target'] = match.group(1)

            # Extract party
            party_span = row.find('span', id=re.compile(r'lblparty'))
            if party_span:
                member_data['party'] = party_span.get_text(strip=True)

            # Extract constituency
            constituency_span = row.find('span', id=re.compile(r'LblMemElectedArea'))
            if constituency_span:
                member_data['constituency'] = constituency_span.get_text(strip=True)

            # Extract mobile
            mobile_span = row.find('span', id=re.compile(r'lblmobile'))
            if mobile_span:
                member_data['mobile'] = mobile_span.get_text(strip=True)

            # Extract email
            email_span = row.find('span', id=re.compile(r'lblemail'))
            if email_span:
                email_text = email_span.get_text(strip=True)
                # Convert [at] and [dot] to actual symbols
                email_text = email_text.replace('[at]', '@').replace('[dot]', '.')
                member_data['email'] = email_text

            # Extract permanent address
            perm_add_parts = []
            for i in range(1, 4):
                addr_span = row.find('span', id=re.compile(rf'lbl_PemAdd{i}'))
                if addr_span:
                    addr_text = addr_span.get_text(strip=True)
                    if addr_text:
                        perm_add_parts.append(addr_text)

            if perm_add_parts:
                member_data['permanent_address'] = ', '.join(perm_add_parts)

            # Extract permanent phone
            perm_tel_span = row.find('span', id=re.compile(r'lblLocTel'))
            if perm_tel_span:
                member_data['permanent_phone'] = perm_tel_span.get_text(strip=True)

            # Extract local (Jaipur) address
            local_add_parts = []
            for i in range(1, 4):
                addr_span = row.find('span', id=re.compile(rf'lbl_LocAdd{i}'))
                if addr_span:
                    addr_text = addr_span.get_text(strip=True)
                    if addr_text:
                        local_add_parts.append(addr_text)

            if local_add_parts:
                member_data['local_address'] = ', '.join(local_add_parts)

            # Extract local phone
            local_tel_span = row.find('span', id=re.compile(r'lblPreTel'))
            if local_tel_span:
                member_data['local_phone'] = local_tel_span.get_text(strip=True)

            # Extract Vidhan Sabha term
            term_span = row.find('span', id=re.compile(r'LblHouseNo'))
            if term_span:
                member_data['vidhan_sabha_term'] = term_span.get_text(strip=True)

            # Extract member photo URL
            img = row.find('img', id=re.compile(r'ImgMember'))
            if img and img.get('src'):
                member_data['photo_url'] = urljoin(self.base_url, img.get('src'))

                # Extract member ID from photo URL if possible
                # Example: https://assembly.rajasthan.gov.in/HamareVidhayak/MLAPic/1745.jpg
                match = re.search(r'/MLAPic/(\d+)\.jpg', img.get('src'))
                if match:
                    member_data['member_id'] = match.group(1)

            if member_data.get('name'):
                members.append(member_data)

        return members

    def _try_ajax_approach(self, soup):
        """Try to find AJAX endpoints or embedded JSON data."""

        members = []

        # Look for embedded JSON in script tags
        scripts = soup.find_all('script')

        for script in scripts:
            script_text = script.get_text()

            # Look for JSON data
            if 'var memberData' in script_text or 'var data' in script_text:
                # Try to extract JSON
                try:
                    # This is a simplified approach - might need adjustment
                    json_match = re.search(r'var\s+\w+\s*=\s*(\[.*?\]);', script_text, re.DOTALL)
                    if json_match:
                        data = json.loads(json_match.group(1))
                        members = data
                        break
                except:
                    pass

        return members

    def fetch_member_details(self, member):
        """Fetch detailed information for a specific member."""

        logger.info(f"  Fetching details for: {member.get('name', 'Unknown')}")

        try:
            # Try multiple approaches to get member details

            # Approach 1: Try direct URL using member ID if available
            if member.get('member_id'):
                # Try different URL patterns that might work
                possible_urls = [
                    f"{self.base_url}/HamareVidhayak/MemberDetails.aspx?MemberID={member['member_id']}",
                    f"{self.base_url}/Containers/Members/MemberDetails.aspx?id={member['member_id']}",
                    f"{self.base_url}/HamareVidhayak/MemberProfile.aspx?id={member['member_id']}",
                ]

                for url in possible_urls:
                    try:
                        response = self.session.get(url, timeout=15, allow_redirects=True)
                        if response.status_code == 200 and len(response.content) > 1000:
                            # Looks like we got a valid page
                            logger.info(f"  Found details page at: {url}")
                            detail_soup = BeautifulSoup(response.content, 'html.parser')
                            details = self._parse_member_detail_page(detail_soup)

                            if details:  # If we got meaningful data
                                member.update(details)
                                time.sleep(0.5)
                                return member
                    except:
                        pass

            # Approach 2: ASP.NET postback (more complex, might not work without proper session)
            if member.get('detail_link_type') == 'postback':
                try:
                    # Get fresh viewstate
                    main_response = self.session.get(self.members_url, timeout=30)
                    main_soup = BeautifulSoup(main_response.content, 'html.parser')
                    viewstate = self.get_viewstate_data(main_soup)

                    # Perform postback
                    viewstate['__EVENTTARGET'] = member['detail_link_target']

                    response = self.session.post(self.members_url, data=viewstate, timeout=30)

                    if response.status_code == 200:
                        detail_soup = BeautifulSoup(response.content, 'html.parser')
                        details = self._parse_member_detail_page(detail_soup)

                        if details:
                            member.update(details)
                            time.sleep(0.5)
                            return member
                except Exception as e:
                    logger.debug(f"  Postback approach failed: {e}")

            # If no detail page found, just return member with existing data
            logger.debug(f"  No detail page found, using main page data only")
            time.sleep(0.3)
            return member

        except Exception as e:
            logger.error(f"  Error fetching details for {member.get('name')}: {e}")
            return member

    def _parse_member_detail_page(self, soup):
        """Parse detailed information from a member's profile page."""

        details = {}

        # Get all text content
        page_text = soup.get_text()

        # Look for specific fields
        # The page is in Hindi, so we need to look for both English and Hindi patterns

        # Extract all table rows if there's a detail table
        tables = soup.find_all('table')

        for table in tables:
            rows = table.find_all('tr')

            for row in rows:
                cells = row.find_all(['td', 'th'])

                if len(cells) >= 2:
                    label = cells[0].get_text(strip=True).lower()
                    value = cells[1].get_text(strip=True)

                    # Map common fields
                    if 'name' in label or 'नाम' in label:
                        details['full_name'] = value
                    elif 'constituency' in label or 'निर्वाचन क्षेत्र' in label:
                        details['constituency'] = value
                    elif 'party' in label or 'पार्टी' in label or 'दल' in label:
                        details['party'] = value
                    elif 'father' in label or 'पिता' in label:
                        details['father_name'] = value
                    elif 'mother' in label or 'माता' in label:
                        details['mother_name'] = value
                    elif 'spouse' in label or 'wife' in label or 'husband' in label or 'पत्नी' in label or 'पति' in label:
                        details['spouse_name'] = value
                    elif 'education' in label or 'शिक्षा' in label:
                        details['education'] = value
                    elif 'profession' in label or 'व्यवसाय' in label or 'पेशा' in label:
                        details['profession'] = value
                    elif 'birth' in label or 'जन्म' in label:
                        details['birth_info'] = value
                    elif 'address' in label or 'पता' in label:
                        if 'permanent' in label or 'स्थायी' in label:
                            details['permanent_address'] = value
                        elif 'local' in label or 'स्थानीय' in label:
                            details['local_address'] = value
                        else:
                            details['address'] = value
                    elif 'email' in label or 'ई-मेल' in label:
                        details['email'] = value
                    elif 'mobile' in label or 'phone' in label or 'मोबाइल' in label or 'फोन' in label:
                        details['phone'] = value
                    elif 'children' in label or 'child' in label or 'बच्चे' in label or 'संतान' in label:
                        details['children_info'] = value
                        # Try to parse children data
                        children_data = self._parse_children_info(value)
                        details.update(children_data)
                    elif 'son' in label or 'पुत्र' in label or 'बेटा' in label:
                        details['sons_info'] = value
                        # Try to extract count
                        son_count = self._extract_count(value)
                        if son_count is not None:
                            details['sons'] = son_count
                    elif 'daughter' in label or 'पुत्री' in label or 'बेटी' in label:
                        details['daughters_info'] = value
                        # Try to extract count
                        daughter_count = self._extract_count(value)
                        if daughter_count is not None:
                            details['daughters'] = daughter_count

        # Also try to extract from general page text if not found in tables
        if 'children_info' not in details:
            # Look for children patterns in the full text
            children_patterns = [
                r'(?:children|बच्चे|संतान)[:\s-]*([^\n]+)',
                r'(?:son|पुत्र|बेटा)[:\s-]*([^\n]+)',
                r'(?:daughter|पुत्री|बेटी)[:\s-]*([^\n]+)'
            ]

            for pattern in children_patterns:
                match = re.search(pattern, page_text, re.IGNORECASE)
                if match:
                    info = match.group(1).strip()
                    if 'son' in pattern or 'पुत्र' in pattern:
                        details['sons_info'] = info
                        count = self._extract_count(info)
                        if count is not None:
                            details['sons'] = count
                    elif 'daughter' in pattern or 'पुत्री' in pattern:
                        details['daughters_info'] = info
                        count = self._extract_count(info)
                        if count is not None:
                            details['daughters'] = count
                    else:
                        details['children_info'] = info

        return details

    def _parse_children_info(self, text):
        """Parse children information from text (may be in Hindi or English)."""

        data = {}

        if not text:
            return data

        # Try to extract counts
        # Look for patterns like "2 sons, 1 daughter" or "2 बेटे, 1 बेटी"

        # English patterns
        son_match = re.search(r'(\d+)\s*sons?', text, re.IGNORECASE)
        if son_match:
            data['sons'] = int(son_match.group(1))

        daughter_match = re.search(r'(\d+)\s*daughters?', text, re.IGNORECASE)
        if daughter_match:
            data['daughters'] = int(daughter_match.group(1))

        # Hindi patterns (using Devanagari script)
        son_hindi = re.search(r'(\d+)\s*(?:पुत्र|बेटे?|बेटा)', text)
        if son_hindi:
            data['sons'] = int(son_hindi.group(1))

        daughter_hindi = re.search(r'(\d+)\s*(?:पुत्री|बेटी)', text)
        if daughter_hindi:
            data['daughters'] = int(daughter_hindi.group(1))

        return data

    def _extract_count(self, text):
        """Extract a numeric count from text."""

        if not text:
            return None

        # Look for standalone numbers
        match = re.search(r'\b(\d+)\b', text)
        if match:
            return int(match.group(1))

        return None

    def scrape_all_members(self, test_mode=False, limit=None, skip_details=False):
        """Scrape all members from the Rajasthan Assembly website."""

        logger.info("Starting Rajasthan Assembly scraper...")
        logger.info("="*70)

        # Get member list
        members = self.fetch_members_list()

        if not members:
            logger.error("No members found!")
            return []

        # Apply limits if specified
        if test_mode:
            members = members[:5]
            logger.info(f"TEST MODE: Processing only {len(members)} members")
        elif limit:
            members = members[:limit]
            logger.info(f"LIMIT MODE: Processing only {len(members)} members")

        if skip_details:
            logger.info("SKIP_DETAILS mode: Will not fetch member detail pages")
            logger.info(f"\nCollected data for {len(members)} members from main page")
            return members

        logger.info(f"\nCollecting detailed data for {len(members)} members...")

        all_data = []

        for i, member in enumerate(members):
            logger.info(f"[{i+1}/{len(members)}] Processing {member.get('name', 'Unknown')}")

            # Fetch detailed information
            detailed_member = self.fetch_member_details(member)
            all_data.append(detailed_member)

            # Progress checkpoint every 25 members
            if (i + 1) % 25 == 0:
                logger.info(f"  Progress: {i+1}/{len(members)} members processed")

        logger.info(f"\nCollected data for {len(all_data)} members")
        return all_data


def save_data(data, output_dir='../../data/rajasthan'):
    """Save collected data to JSON and CSV files."""

    if not data:
        logger.error("No data to save")
        return None

    # Create output directory
    output_path = Path(__file__).parent / output_dir
    output_path.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

    # Save JSON
    json_file = output_path / f'rajasthan_assembly_{timestamp}.json'
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump({
            'source': 'Rajasthan Legislative Assembly',
            'url': 'https://assembly.rajasthan.gov.in/Containers/Members/Contacts.aspx',
            'scraped_at': datetime.now().isoformat(),
            'count': len(data),
            'members': data
        }, f, ensure_ascii=False, indent=2)

    logger.info(f"Saved JSON: {json_file}")

    # Save CSV
    df = pd.DataFrame(data)
    csv_file = output_path / f'rajasthan_assembly_{timestamp}.csv'
    df.to_csv(csv_file, index=False, encoding='utf-8')

    logger.info(f"Saved CSV: {csv_file}")

    # Show summary
    print("\n" + "="*70)
    print("SCRAPING SUMMARY")
    print("="*70)
    print(f"Total members: {len(data)}")

    if 'sons' in df.columns and 'daughters' in df.columns:
        with_children_data = df.dropna(subset=['sons', 'daughters'])
        print(f"Members with children data: {len(with_children_data)}")

        if len(with_children_data) > 0:
            total_sons = with_children_data['sons'].sum()
            total_daughters = with_children_data['daughters'].sum()
            print(f"Total sons: {int(total_sons)}")
            print(f"Total daughters: {int(total_daughters)}")
            print(f"Sex ratio: {total_sons/total_daughters:.2f}" if total_daughters > 0 else "Sex ratio: N/A")

    # Show sample
    print("\n" + "="*70)
    print("SAMPLE DATA (first 5 members)")
    print("="*70)

    # Select interesting columns for display
    display_cols = []
    for col in ['name', 'full_name', 'constituency', 'party', 'sons', 'daughters', 'children_info']:
        if col in df.columns:
            display_cols.append(col)

    if display_cols:
        print(df[display_cols].head().to_string(index=False))
    else:
        print(df.head().to_string(index=False))

    return csv_file


def main():
    import argparse

    parser = argparse.ArgumentParser(description='Scrape Rajasthan Assembly members')
    parser.add_argument('--test', action='store_true', help='Test mode (first 5 members only)')
    parser.add_argument('--limit', type=int, help='Limit number of members to scrape')
    parser.add_argument('--skip-details', action='store_true', help='Skip fetching detail pages (faster, main page data only)')
    args = parser.parse_args()

    print("\n" + "="*70)
    print("RAJASTHAN LEGISLATIVE ASSEMBLY SCRAPER")
    print("="*70)
    print()

    scraper = RajasthanAssemblyScraper()
    data = scraper.scrape_all_members(test_mode=args.test, limit=args.limit, skip_details=args.skip_details)

    if data:
        save_data(data)
        print("\n✓ Scraping complete!")
    else:
        print("\n✗ No data collected")


if __name__ == '__main__':
    main()
