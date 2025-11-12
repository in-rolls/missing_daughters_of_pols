"""
Test script to demonstrate data collection functionality.

This script tests the collection utilities and shows a working example
by fetching a small sample of data.

Usage:
    python test_collector.py
"""

import sys
from pathlib import Path
import json
import pandas as pd

# Add utilities to path
sys.path.append(str(Path(__file__).parent / 'utilities'))

from scraping_utils import (
    RateLimitedSession,
    validate_family_data,
    calculate_summary_stats,
    extract_children_from_text
)

def test_utilities():
    """Test utility functions."""
    print("=== Testing Utility Functions ===\n")

    # Test 1: Children extraction from text
    print("Test 1: Extracting children from text")
    test_texts = [
        "He has 2 sons and 1 daughter",
        "Family: 3 sons, 2 daughters",
        "Sons: 1, Daughters: 2",
        "One son and two daughters",
    ]

    for text in test_texts:
        result = extract_children_from_text(text)
        print(f"  '{text}' -> {result}")

    print()

    # Test 2: Data validation
    print("Test 2: Validating family data")
    test_record = {
        'names': 'Test Politician',
        'sons': '2',
        'daughters': 1,
        'party': 'TEST',
    }

    validated = validate_family_data(test_record)
    print(f"  Original: {test_record}")
    print(f"  Validated: {validated}")
    print()

    # Test 3: Summary statistics
    print("Test 3: Calculating summary statistics")
    sample_data = pd.DataFrame([
        {'names': 'Person A', 'sons': 2, 'daughters': 1},
        {'names': 'Person B', 'sons': 1, 'daughters': 2},
        {'names': 'Person C', 'sons': 3, 'daughters': 0},
        {'names': 'Person D', 'sons': 1, 'daughters': 1},
        {'names': 'Person E', 'sons': 0, 'daughters': 2},
    ])

    stats = calculate_summary_stats(sample_data)
    print("  Sample data statistics:")
    for key, value in stats.items():
        if isinstance(value, float):
            print(f"    {key}: {value:.3f}")
        else:
            print(f"    {key}: {value}")
    print()


def test_rajya_sabha_data():
    """Test parsing existing Rajya Sabha data."""
    print("=== Testing Rajya Sabha Data Parser ===\n")

    rs_data_dir = Path(__file__).parent.parent.parent / 'data'

    # Check if Rajya Sabha tar.gz exists
    rs_tar = rs_data_dir / 'rajya_sabha.tar.gz'

    if rs_tar.exists():
        print(f"Found Rajya Sabha data archive: {rs_tar}")
        print("To extract and analyze:")
        print(f"  cd {rs_data_dir}")
        print(f"  tar -xzf rajya_sabha.tar.gz")
        print()

        # Try to read a sample if extracted
        import tarfile
        import tempfile
        import os

        print("Extracting sample files from archive...")
        with tarfile.open(rs_tar, 'r:gz') as tar:
            members = tar.getmembers()[:5]  # Get first 5 files
            sample_data = []

            with tempfile.TemporaryDirectory() as tmpdir:
                for member in members:
                    if member.name.endswith('.json'):
                        tar.extract(member, tmpdir)
                        filepath = os.path.join(tmpdir, member.name)

                        with open(filepath, 'r') as f:
                            data = json.load(f)
                            sample_data.append(data)

            if sample_data:
                print(f"\nSample of {len(sample_data)} Rajya Sabha member records:")
                print("-" * 60)

                for i, record in enumerate(sample_data, 1):
                    print(f"\nRecord {i}:")
                    # Print relevant fields
                    for key in ['memberName', 'gender', 'party', 'state']:
                        if key in record:
                            value = record[key]
                            if isinstance(value, dict):
                                value = str(value)[:50] + '...' if len(str(value)) > 50 else value
                            print(f"  {key}: {value}")

                print("\n" + "-" * 60)
                print("\nNote: To analyze family data, you need to:")
                print("1. Extract all JSON files from the archive")
                print("2. Parse biographical text for children information")
                print("3. Create analysis script similar to Lok Sabha analysis")
                print()

    else:
        print(f"Rajya Sabha data not found at {rs_tar}")
        print()


def test_rate_limiter():
    """Test rate-limited session."""
    print("=== Testing Rate-Limited HTTP Session ===\n")

    session = RateLimitedSession(delay=0.5)

    # Test with a simple public API
    test_url = "https://api.github.com/zen"

    print(f"Making test request to: {test_url}")
    print("(This tests that HTTP requests work with rate limiting)")

    response = session.get(test_url)

    if response and response.status_code == 200:
        print(f"  ✓ Success! Status: {response.status_code}")
        print(f"  Response preview: {response.text[:100]}")
    else:
        print(f"  ✗ Request failed or no response")

    print()


def main():
    print("\n" + "=" * 70)
    print("DATA COLLECTION FRAMEWORK TEST")
    print("=" * 70 + "\n")

    # Run tests
    test_utilities()
    test_rate_limiter()
    test_rajya_sabha_data()

    print("=" * 70)
    print("NEXT STEPS:")
    print("=" * 70)
    print()
    print("1. Review the test results above")
    print()
    print("2. To collect new state data, use:")
    print("   cd state_assemblies/")
    print("   python collect_election_affidavits.py --state karnataka --year 2023")
    print()
    print("3. To extract data from PDFs (like UP data):")
    print("   cd pdf_extraction/")
    print("   python extract_biographical_data.py --input ../../../data/up/ --output ../../../data/up/extracted.csv")
    print()
    print("4. For comprehensive collection plan:")
    print("   See: data_collection/README.md")
    print()


if __name__ == '__main__':
    main()
