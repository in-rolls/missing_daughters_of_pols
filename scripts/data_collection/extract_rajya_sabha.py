"""
Extract and analyze Rajya Sabha data from the existing archive.

This uses the rajya_sabha.tar.gz file that's already been collected.

Usage:
    python extract_rajya_sabha.py --output ../../data/rajya_sabha_analysis/
"""

import argparse
import tarfile
import json
import logging
from pathlib import Path
import pandas as pd
import tempfile
import re
import sys

sys.path.append(str(Path(__file__).parent / 'utilities'))
from scraping_utils import calculate_summary_stats, extract_children_from_text, validate_family_data

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def extract_rajya_sabha_archive():
    """
    Extract and analyze the Rajya Sabha archive.
    """
    logger.info("Extracting Rajya Sabha data archive...")

    archive_path = Path(__file__).parent.parent.parent / 'data' / 'rajya_sabha.tar.gz'

    if not archive_path.exists():
        logger.error(f"Archive not found: {archive_path}")
        return None

    records = []

    with tarfile.open(archive_path, 'r:gz') as tar:
        members = tar.getmembers()
        logger.info(f"Found {len(members)} files in archive")

        # Extract to temporary directory
        with tempfile.TemporaryDirectory() as tmpdir:
            logger.info("Extracting files...")
            tar.extractall(tmpdir)

            # Process each JSON file
            extracted_path = Path(tmpdir)
            json_files = list(extracted_path.rglob('*.json'))

            logger.info(f"Processing {len(json_files)} JSON files...")

            for i, json_file in enumerate(json_files):
                if (i + 1) % 100 == 0:
                    logger.info(f"  Processed {i+1}/{len(json_files)} files...")

                try:
                    with open(json_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)

                    record = extract_member_info(data)
                    if record:
                        records.append(record)

                except Exception as e:
                    logger.debug(f"Error processing {json_file}: {e}")
                    continue

    logger.info(f"Extracted {len(records)} member records")
    return records


def extract_member_info(data):
    """
    Extract relevant information from a Rajya Sabha member JSON record.

    The JSON files from rsdoc.nic.in use these field names:
    - MP_FNAME, MP_LNAME, MP_INIT for name
    - NO_SONS, NO_DAUGHTER for children
    - PARTY_NAME, STATE_NAME
    """
    # Handle list wrapper
    if isinstance(data, list) and len(data) > 0:
        data = data[0]

    if not data or not isinstance(data, dict):
        return None

    record = {}

    # Extract name
    init = (data.get('MP_INIT') or '').strip()
    fname = (data.get('MP_FNAME') or '').strip()
    lname = (data.get('MP_LNAME') or '').strip()

    name_parts = [p for p in [init, fname, lname] if p]
    if name_parts:
        record['name'] = ' '.join(name_parts)
    else:
        return None  # No name, skip

    # Extract other fields
    party = (data.get('PARTY_NAME') or '').strip()
    state = (data.get('STATE_NAME') or '').strip()

    if party:
        record['party'] = party
    if state:
        record['state'] = state

    # Extract family information - direct from NO_SONS and NO_DAUGHTER fields
    sons = data.get('NO_SONS')
    daughters = data.get('NO_DAUGHTER')

    # Convert to int (handles both numeric strings and text like "Two", "one")
    text_to_num = {
        'one': 1, 'two': 2, 'three': 3, 'four': 4, 'five': 5,
        'six': 6, 'seven': 7, 'eight': 8, 'nine': 9, 'ten': 10
    }

    if sons is not None and sons != '':
        try:
            # Try direct int conversion first
            record['sons'] = int(sons)
        except (ValueError, TypeError):
            # Try text to number conversion
            sons_lower = str(sons).strip().lower()
            if sons_lower in text_to_num:
                record['sons'] = text_to_num[sons_lower]

    if daughters is not None and daughters != '':
        try:
            # Try direct int conversion first
            record['daughters'] = int(daughters)
        except (ValueError, TypeError):
            # Try text to number conversion
            daughters_lower = str(daughters).strip().lower()
            if daughters_lower in text_to_num:
                record['daughters'] = text_to_num[daughters_lower]

    return validate_family_data(record)


def analyze_rajya_sabha_data(records):
    """
    Analyze the extracted Rajya Sabha data.
    """
    if not records:
        logger.error("No records to analyze")
        return

    df = pd.DataFrame(records)

    print("\n" + "="*70)
    print("RAJYA SABHA DATA ANALYSIS")
    print("="*70)
    print()

    print(f"Total members: {len(df)}")

    # Check data completeness
    complete = df.dropna(subset=['sons', 'daughters'])
    print(f"Members with family data: {len(complete)} ({len(complete)/len(df)*100:.1f}%)")
    print()

    if len(complete) > 0:
        print("SAMPLE DATA (First 10 with family information):")
        print("-"*70)
        print(complete[['name', 'sons', 'daughters', 'party', 'state']].head(10).to_string(index=False))
        print()

        # Calculate statistics
        stats = calculate_summary_stats(df)

        print("STATISTICS:")
        print("-"*70)
        print(f"Members with family data: {stats['n_politicians']}")
        print(f"Total sons: {stats['total_sons']}")
        print(f"Total daughters: {stats['total_daughters']}")
        print(f"Total children: {stats['total_children']}")
        print()
        print(f"Sex ratio: {stats['sex_ratio']:.3f}")
        print(f"Proportion daughters: {stats['proportion_daughters']:.3f}")
        print(f"Mean children per member: {stats['mean_total_children']:.2f}")
        print()

        # Compare with natural
        print("COMPARISON WITH NATURAL SEX RATIO:")
        print("-"*70)
        print(f"Natural sex ratio: 1.05")
        print(f"Rajya Sabha sex ratio: {stats['sex_ratio']:.3f}")
        print(f"Difference: {stats['sex_ratio'] - 1.05:.3f}")
        print()

        if stats['sex_ratio'] > 1.05:
            expected_daughters = stats['total_children'] * 0.488
            missing = expected_daughters - stats['total_daughters']
            print(f"Expected daughters (natural): {expected_daughters:.1f}")
            print(f"Actual daughters: {stats['total_daughters']}")
            print(f"Missing daughters: ~{int(missing)}")
            print()

        # Party-wise analysis if enough data
        if 'party' in complete.columns and len(complete) > 50:
            print("PARTY-WISE ANALYSIS (Parties with 10+ members):")
            print("-"*70)

            party_groups = complete.groupby('party')
            party_stats = []

            for party, group in party_groups:
                if len(group) >= 10:
                    total_sons = group['sons'].sum()
                    total_daughters = group['daughters'].sum()
                    ratio = total_sons / total_daughters if total_daughters > 0 else None

                    party_stats.append({
                        'Party': party,
                        'Members': len(group),
                        'Sons': int(total_sons),
                        'Daughters': int(total_daughters),
                        'Ratio': f"{ratio:.2f}" if ratio else '-'
                    })

            if party_stats:
                party_df = pd.DataFrame(party_stats).sort_values('Ratio', ascending=False)
                print(party_df.to_string(index=False))
                print()

    else:
        print("⚠️  No family data found in the records")
        print()
        print("Sample of available fields:")
        print(df.head(5).to_string())
        print()
        print("This may mean:")
        print("1. Family data is in different fields than expected")
        print("2. The JSON structure needs manual inspection")
        print("3. Data may need to be extracted from PDF/HTML files")

    return df


def main():
    parser = argparse.ArgumentParser(
        description='Extract and analyze Rajya Sabha data from archive'
    )
    parser.add_argument(
        '--output',
        default='../../data/rajya_sabha_analysis/',
        help='Output directory for analysis'
    )

    args = parser.parse_args()

    # Extract data
    records = extract_rajya_sabha_archive()

    if records:
        # Analyze
        df = analyze_rajya_sabha_data(records)

        # Save to CSV
        output_dir = Path(args.output)
        output_dir.mkdir(parents=True, exist_ok=True)

        output_file = output_dir / 'rajya_sabha_extracted.csv'
        df.to_csv(output_file, index=False)
        logger.info(f"Saved data to {output_file}")
    else:
        logger.error("No data extracted")


if __name__ == '__main__':
    main()
