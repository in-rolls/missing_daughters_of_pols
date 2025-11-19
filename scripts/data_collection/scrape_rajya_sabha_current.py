"""
Scraper for Current Rajya Sabha Members using working NIC API

Collects sons/daughters data for all current RS members.
Uses the WORKING API: rsdoc.nic.in/Memberweb/GetCurrentMember_Biodata

Output: Saves to data/rajya_sabha/rs_current_TIMESTAMP.json
"""

import requests
import json
import pandas as pd
from pathlib import Path
from datetime import datetime
import time
import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


def parse_number_field(value):
    """Parse number fields from RS API (e.g., 'One', 'Two', '1', '2')"""
    if not value or value.strip() == '':
        return None

    # Number words to int
    number_map = {
        'zero': 0, 'one': 1, 'two': 2, 'three': 3, 'four': 4,
        'five': 5, 'six': 6, 'seven': 7, 'eight': 8, 'nine': 9, 'ten': 10
    }

    value_lower = value.lower().strip()

    # Try direct int conversion first
    try:
        return int(value_lower)
    except ValueError:
        pass

    # Try word to number
    if value_lower in number_map:
        return number_map[value_lower]

    return None


def collect_rajya_sabha_members(start_id=1, end_id=3000):
    """
    Collect RS members by iterating through member IDs.
    Current members will have valid data.
    """

    base_url = "https://rsdoc.nic.in/Memberweb/GetCurrentMember_Biodata"

    all_members = []
    successful = 0
    empty = 0
    errors = 0

    logger.info(f"Scraping Rajya Sabha members from ID {start_id} to {end_id}")
    logger.info("This will take a while... Progress updates every 100 IDs")

    for mpcode in range(start_id, end_id + 1):
        try:
            url = f"{base_url}?mpcode={mpcode}"
            response = requests.get(url, timeout=10)

            if response.status_code == 200:
                data = response.json()

                # Check if valid member data
                if data and len(data) > 0:
                    member = data[0]

                    # Check if current member
                    is_current = member.get('MP_CURRENT', False)

                    # Get name from MP_FNAME and MP_LNAME
                    fname = member.get('MP_FNAME', '').strip()
                    lname = member.get('MP_LNAME', '').strip()
                    full_name = f"{fname} {lname}".strip()

                    # Only process current members with valid names
                    if is_current and full_name:
                        # Extract family data
                        record = {
                            'mpcode': mpcode,
                            'name': full_name,
                            'party': member.get('PARTY_NAME', '').strip(),
                            'state': member.get('STATE_NAME', '').strip(),
                            'numberOfSons': parse_number_field(member.get('NO_SONS', '')),
                            'numberOfDaughters': parse_number_field(member.get('NO_DAUGHTER', '')),
                            'spouse': member.get('SPOUSE_NAME', '').strip(),
                            'qualification': member.get('QUALIFICATION', '').strip(),
                            'dateOfBirth': member.get('DATE_BIRTH', '').strip(),
                            'profession': member.get('prof1', '').strip(),
                        }
                        all_members.append(record)
                        successful += 1

                        if successful % 10 == 0:
                            logger.info(f"  Found {successful} members... (checking ID {mpcode})")
                else:
                    empty += 1
            else:
                errors += 1

            # Progress update
            if mpcode % 100 == 0:
                logger.info(f"Progress: Checked {mpcode}/{end_id} IDs | Found: {successful} | Empty: {empty} | Errors: {errors}")

            # Rate limiting
            time.sleep(0.5)

        except Exception as e:
            errors += 1
            if errors % 50 == 0:
                logger.warning(f"Errors so far: {errors} (latest at mpcode={mpcode})")
            continue

    logger.info(f"\nCollection complete!")
    logger.info(f"Total members found: {successful}")
    logger.info(f"Empty responses: {empty}")
    logger.info(f"Errors: {errors}")

    return all_members


def save_data(members, output_dir='../../data/rajya_sabha'):
    """Save collected data"""

    if not members:
        logger.error("No data to save")
        return None

    # Create output directory
    output_path = Path(__file__).parent / output_dir
    output_path.mkdir(parents=True, exist_ok=True)

    # Timestamp
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

    # Save as JSON
    json_file = output_path / f'rs_current_{timestamp}.json'
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump({'members': members, 'count': len(members)}, f, ensure_ascii=False, indent=2)

    logger.info(f"\nSaved JSON to: {json_file}")

    # Save as CSV
    df = pd.DataFrame(members)
    csv_file = output_path / f'rs_current_{timestamp}.csv'
    df.to_csv(csv_file, index=False)

    logger.info(f"Saved CSV to: {csv_file}")

    # Show sample
    print("\n" + "="*70)
    print("SAMPLE DATA (First 10 members)")
    print("="*70)
    print(df[['name', 'party', 'state', 'numberOfSons', 'numberOfDaughters']].head(10).to_string(index=False))
    print()

    # Statistics
    complete = df[(df['numberOfSons'].notna()) & (df['numberOfDaughters'].notna())]

    if len(complete) > 0:
        total_sons = complete['numberOfSons'].sum()
        total_daughters = complete['numberOfDaughters'].sum()
        total_children = total_sons + total_daughters

        print("STATISTICS")
        print("="*70)
        print(f"Total RS members found: {len(df)}")
        print(f"Members with family data: {len(complete)}")
        print(f"Total sons: {int(total_sons)}")
        print(f"Total daughters: {int(total_daughters)}")
        print(f"Total children: {int(total_children)}")

        if total_daughters > 0:
            sex_ratio = total_sons / total_daughters
            prop_daughters = total_daughters / total_children
            print(f"Sex ratio (sons/daughters): {sex_ratio:.3f}")
            print(f"Proportion daughters: {prop_daughters:.3f}")
        print()

    return csv_file


def main():
    import argparse
    parser = argparse.ArgumentParser(description='Scrape Rajya Sabha members')
    parser.add_argument('--start', type=int, default=1, help='Start ID (default: 1)')
    parser.add_argument('--end', type=int, default=3000, help='End ID (default: 3000)')
    parser.add_argument('--test', action='store_true', help='Test mode: only check first 500 IDs')
    args = parser.parse_args()

    if args.test:
        start_id, end_id = 1, 500
        logger.info("TEST MODE: Checking only first 500 IDs")
    else:
        start_id, end_id = args.start, args.end

    print("\n" + "="*70)
    print("RAJYA SABHA CURRENT MEMBERS SCRAPER")
    print("Using WORKING API: rsdoc.nic.in")
    print("="*70)
    print()

    # Collect data
    members = collect_rajya_sabha_members(start_id=start_id, end_id=end_id)

    if members:
        filepath = save_data(members)

        print("="*70)
        print("SUCCESS!")
        print("="*70)
        print(f"\nCollected {len(members)} Rajya Sabha members")
        print(f"Data saved to: {filepath}")
        print()
    else:
        print("No data collected")


if __name__ == '__main__':
    main()
