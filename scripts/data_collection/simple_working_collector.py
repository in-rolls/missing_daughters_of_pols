"""
Simple working data collector for Indian politician family data.

This script collects data from a reliable, static source and saves it properly.
Focus: Get ONE source working end-to-end.
"""

import pandas as pd
import requests
from bs4 import BeautifulSoup
import time
import re
from pathlib import Path
from datetime import datetime


def collect_sample_data():
    """
    Collect sample data using a working approach.
    We'll scrape from Wikipedia pages which are static HTML and reliable.
    """
    print("=" * 70)
    print("SIMPLE DATA COLLECTOR - Collecting from reliable sources")
    print("=" * 70)
    print()

    # We'll start with a known working data source:
    # Individual politician Wikipedia pages for Karnataka 2023 CM and ministers

    # Known Karnataka 2023 cabinet members with Wikipedia pages
    known_politicians = [
        {
            'name': 'Siddaramaiah',
            'position': 'Chief Minister',
            'constituency': 'Varuna',
            'party': 'INC',
            'wikipedia': 'https://en.wikipedia.org/wiki/Siddaramaiah'
        },
        {
            'name': 'D. K. Shivakumar',
            'position': 'Deputy Chief Minister',
            'constituency': 'Kanakapura',
            'party': 'INC',
            'wikipedia': 'https://en.wikipedia.org/wiki/D._K._Shivakumar'
        },
        {
            'name': 'G. Parameshwara',
            'position': 'Minister',
            'constituency': 'Koratagere',
            'party': 'INC',
            'wikipedia': 'https://en.wikipedia.org/wiki/G._Parameshwara'
        },
        {
            'name': 'M. B. Patil',
            'position': 'Minister',
            'constituency': 'Babaleshwar',
            'party': 'INC',
            'wikipedia': 'https://en.wikipedia.org/wiki/M._B._Patil'
        },
        {
            'name': 'K. J. George',
            'position': 'Minister',
            'constituency': 'Sarvagnanagar',
            'party': 'INC',
            'wikipedia': 'https://en.wikipedia.org/wiki/K._J._George'
        },
    ]

    collected_data = []

    for i, politician in enumerate(known_politicians):
        print(f"[{i+1}/{len(known_politicians)}] {politician['name']}")

        try:
            # Fetch Wikipedia page with proper User-Agent
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            response = requests.get(politician['wikipedia'], headers=headers, timeout=10)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')
            page_text = soup.get_text().lower()

            # Look for family information
            record = {
                'name': politician['name'],
                'position': politician['position'],
                'constituency': politician['constituency'],
                'party': politician['party'],
                'state': 'Karnataka',
                'year': 2023,
                'source': 'Wikipedia'
            }

            # Try to extract children information from infobox
            infobox = soup.find('table', {'class': 'infobox'})

            sons = None
            daughters = None

            if infobox:
                # Look for "Children" row
                for row in infobox.find_all('tr'):
                    th = row.find('th')
                    if th and 'children' in th.get_text().lower():
                        td = row.find('td')
                        if td:
                            children_text = td.get_text().lower()

                            # Try to extract numbers
                            # Pattern: "2 sons and 1 daughter" or "3 (2 sons, 1 daughter)"
                            son_match = re.search(r'(\d+)\s*sons?', children_text)
                            daughter_match = re.search(r'(\d+)\s*daughters?', children_text)

                            if son_match:
                                sons = int(son_match.group(1))
                            if daughter_match:
                                daughters = int(daughter_match.group(1))

                            # Also try just counting mentions
                            if sons is None and daughters is None:
                                # Count total children if just a number
                                num_match = re.search(r'^(\d+)\s*(?:\(|$)', children_text)
                                if num_match:
                                    print(f"  Found {num_match.group(1)} children total (breakdown not specified)")

            # Also search in main text
            if sons is None or daughters is None:
                # Search in article text
                son_patterns = [
                    r'has\s+(\d+)\s+sons?',
                    r'(\d+)\s+sons?\s+(?:and|,)',
                    r'father\s+of\s+(\d+)\s+sons?',
                ]

                daughter_patterns = [
                    r'has\s+(\d+)\s+daughters?',
                    r'(\d+)\s+daughters?',
                    r'father\s+of\s+(\d+)\s+daughters?',
                ]

                for pattern in son_patterns:
                    if sons is None:
                        match = re.search(pattern, page_text)
                        if match:
                            sons = int(match.group(1))
                            break

                for pattern in daughter_patterns:
                    if daughters is None:
                        match = re.search(pattern, page_text)
                        if match:
                            daughters = int(match.group(1))
                            break

            record['sons'] = sons if sons is not None else 0
            record['daughters'] = daughters if daughters is not None else 0

            if sons is not None or daughters is not None:
                print(f"  ✓ Found: {record['sons']} sons, {record['daughters']} daughters")
            else:
                print(f"  - No family data found")

            collected_data.append(record)

            # Rate limiting
            time.sleep(2)

        except Exception as e:
            print(f"  ✗ Error: {e}")
            # Still add the record but without family data
            record = {
                'name': politician['name'],
                'position': politician['position'],
                'constituency': politician['constituency'],
                'party': politician['party'],
                'state': 'Karnataka',
                'year': 2023,
                'sons': None,
                'daughters': None,
                'source': 'Wikipedia',
                'error': str(e)
            }
            collected_data.append(record)

    print()
    print("=" * 70)
    print("DATA COLLECTED")
    print("=" * 70)
    print()

    return collected_data


def save_data(data, output_dir='../../data/karnataka'):
    """Save collected data to CSV."""

    # Create output directory
    output_path = Path(__file__).parent / output_dir
    output_path.mkdir(parents=True, exist_ok=True)

    # Convert to DataFrame
    df = pd.DataFrame(data)

    # Generate filename with timestamp
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f'karnataka_ministers_2023_{timestamp}.csv'
    filepath = output_path / filename

    # Save to CSV
    df.to_csv(filepath, index=False)

    print(f"✓ Data saved to: {filepath}")
    print(f"  Records: {len(df)}")

    # Show the data
    print()
    print("COLLECTED DATA:")
    print("-" * 70)
    print(df[['name', 'party', 'constituency', 'sons', 'daughters']].to_string(index=False))
    print()

    # Calculate statistics
    complete = df.dropna(subset=['sons', 'daughters'])
    if len(complete) > 0:
        total_sons = complete['sons'].sum()
        total_daughters = complete['daughters'].sum()
        total_children = total_sons + total_daughters

        print("STATISTICS:")
        print("-" * 70)
        print(f"Politicians with family data: {len(complete)}/{len(df)}")
        print(f"Total sons: {int(total_sons)}")
        print(f"Total daughters: {int(total_daughters)}")
        print(f"Total children: {int(total_children)}")

        if total_daughters > 0:
            sex_ratio = total_sons / total_daughters
            prop_daughters = total_daughters / total_children
            print(f"Sex ratio: {sex_ratio:.3f}")
            print(f"Proportion daughters: {prop_daughters:.3f}")
        print()

    return filepath


def main():
    print()
    print("=" * 70)
    print("SIMPLE WORKING DATA COLLECTOR")
    print("Collecting Karnataka 2023 Cabinet Ministers Data")
    print("=" * 70)
    print()

    # Collect data
    data = collect_sample_data()

    if data:
        # Save data
        filepath = save_data(data)

        print("=" * 70)
        print("SUCCESS!")
        print("=" * 70)
        print()
        print(f"Data successfully collected and saved to:")
        print(f"  {filepath}")
        print()
        print("Next steps:")
        print("  1. Review the CSV file")
        print("  2. Expand to more Karnataka MLAs")
        print("  3. Scale to other states")
        print()
    else:
        print("No data collected.")


if __name__ == '__main__':
    main()
