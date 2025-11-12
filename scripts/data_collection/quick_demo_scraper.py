"""
Quick demonstration of data collection from a real source.

This fetches actual data from MyNeta to show the collection process.
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import re

def demo_collect_karnataka_sample():
    """
    Collect a small sample from Karnataka 2023 winners to demonstrate.
    """
    print("="*70)
    print("DEMO: Collecting Sample Data from Karnataka 2023 Elections")
    print("="*70)
    print()

    # MyNeta Karnataka 2023 winners page
    url = "https://myneta.info/karnataka2023/index.php?action=summary&subAction=winner_analyzed&sort=candidate"

    print(f"Fetching: {url}")
    response = requests.get(url)

    if response.status_code != 200:
        print(f"Failed to fetch data: {response.status_code}")
        return None

    soup = BeautifulSoup(response.content, 'html.parser')

    # Find the table with candidate data
    tables = soup.find_all('table')

    candidates = []
    for table in tables:
        rows = table.find_all('tr')

        for row in rows:
            cells = row.find_all('td')

            if len(cells) >= 3:
                # Look for candidate links
                links = row.find_all('a', href=re.compile(r'candidate\.php'))

                for link in links:
                    name = link.text.strip()
                    if name and len(name) > 3 and name != "Candidate":
                        # Get more details from the row
                        candidate_info = {
                            'name': name,
                            'url': 'https://myneta.info/karnataka2023/' + link['href']
                        }

                        # Try to get party and constituency from the row
                        if len(cells) > 1:
                            candidate_info['party'] = cells[1].text.strip() if len(cells) > 1 else None
                            candidate_info['constituency'] = cells[2].text.strip() if len(cells) > 2 else None

                        candidates.append(candidate_info)
                        break

    print(f"Found {len(candidates)} candidates")
    print()

    # Collect details from first 5 candidates as demo
    print("Collecting detailed information from first 5 candidates...")
    print()

    detailed_data = []

    for i, candidate in enumerate(candidates[:5]):
        print(f"{i+1}/5: {candidate['name']}")

        time.sleep(1)  # Rate limiting

        try:
            response = requests.get(candidate['url'])
            soup = BeautifulSoup(response.content, 'html.parser')

            # Extract family information from the page
            page_text = soup.get_text()

            record = {
                'name': candidate['name'],
                'party': candidate.get('party'),
                'constituency': candidate.get('constituency'),
                'state': 'Karnataka',
                'year': 2023
            }

            # Look for family information in tables
            tables = soup.find_all('table')

            for table in tables:
                table_text = table.get_text().lower()

                # Look for spouse and dependents section
                if 'spouse' in table_text or 'dependent' in table_text:
                    rows = table.find_all('tr')

                    sons = 0
                    daughters = 0

                    for row in rows:
                        row_text = row.get_text().lower()

                        # Count sons and daughters
                        if 'son' in row_text and 'daughter' not in row_text:
                            sons += 1
                        elif 'daughter' in row_text:
                            daughters += 1

                    if sons > 0 or daughters > 0:
                        record['sons'] = sons
                        record['daughters'] = daughters

            # If not found in tables, try text extraction
            if 'sons' not in record:
                # Look for patterns like "2 Sons" or "1 Daughter"
                son_match = re.search(r'(\d+)\s*sons?', page_text, re.IGNORECASE)
                daughter_match = re.search(r'(\d+)\s*daughters?', page_text, re.IGNORECASE)

                if son_match:
                    record['sons'] = int(son_match.group(1))
                if daughter_match:
                    record['daughters'] = int(daughter_match.group(1))

            detailed_data.append(record)

            # Show what we found
            if 'sons' in record or 'daughters' in record:
                print(f"   ✓ Found: {record.get('sons', 0)} sons, {record.get('daughters', 0)} daughters")
            else:
                print(f"   - No family data found")

        except Exception as e:
            print(f"   ✗ Error: {e}")

    print()
    print("="*70)
    print("SAMPLE DATA COLLECTED")
    print("="*70)

    if detailed_data:
        df = pd.DataFrame(detailed_data)
        print()
        print(df.to_string(index=False))
        print()

        # Calculate statistics for complete records
        complete = df.dropna(subset=['sons', 'daughters'])

        if len(complete) > 0:
            total_sons = complete['sons'].sum()
            total_daughters = complete['daughters'].sum()
            sex_ratio = total_sons / total_daughters if total_daughters > 0 else None

            print("STATISTICS (Complete records only):")
            print("-"*70)
            print(f"Candidates with family data: {len(complete)}/{len(df)}")
            print(f"Total sons: {int(total_sons)}")
            print(f"Total daughters: {int(total_daughters)}")
            if sex_ratio:
                print(f"Sex ratio: {sex_ratio:.2f}")
                print(f"Proportion daughters: {total_daughters/(total_sons+total_daughters):.3f}")
            print()

        return df

    else:
        print("No data collected")
        return None


if __name__ == '__main__':
    demo_collect_karnataka_sample()
