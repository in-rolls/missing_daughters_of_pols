"""
Demonstrate the utility functions with real examples.
"""

import sys
from pathlib import Path
import pandas as pd

sys.path.append(str(Path(__file__).parent / 'utilities'))
from scraping_utils import (
    extract_children_from_text,
    validate_family_data,
    calculate_summary_stats,
    combine_and_deduplicate
)

def demo_text_extraction():
    """Show how text extraction works for various formats."""
    print("="*70)
    print("DEMO: EXTRACTING CHILDREN DATA FROM TEXT")
    print("="*70)
    print()

    # Real-world examples of how biographical data appears
    test_cases = [
        "Shri Ram Kumar has 2 sons and 1 daughter.",
        "Family: Wife, 3 sons, 2 daughters",
        "Sons: 2, Daughters: 1",
        "He has one son and two daughters",
        "Married with 4 children (2 sons, 2 daughters)",
        "पुत्र: 2, पुत्री: 1",  # Hindi
        "Blessed with 1 son and 1 daughter",
    ]

    print("Input Text → Extracted Data")
    print("-"*70)

    for text in test_cases:
        result = extract_children_from_text(text)
        sons = result['sons'] if result['sons'] is not None else '?'
        daughters = result['daughters'] if result['daughters'] is not None else '?'
        print(f"{text:<55} → S:{sons} D:{daughters}")

    print()


def demo_validation():
    """Show data validation and normalization."""
    print("="*70)
    print("DEMO: DATA VALIDATION & NORMALIZATION")
    print("="*70)
    print()

    # Examples of messy input data
    test_records = [
        {'names': 'Person A', 'sons': '2', 'daughters': '1'},  # String numbers
        {'names': 'Person B', 'sons': 1, 'daughters': 2},  # Integers
        {'names': 'Person C', 'sons': '', 'daughters': None},  # Missing data
        {'names': 'Person D', 'sons': 3, 'daughters': 0},  # Zero daughters
    ]

    print("BEFORE → AFTER VALIDATION")
    print("-"*70)

    for record in test_records:
        validated = validate_family_data(record)

        before = f"S:{record.get('sons')!r} D:{record.get('daughters')!r}"
        after_sons = validated.get('sons', 'None')
        after_daughters = validated.get('daughters', 'None')
        total = validated.get('total_children', '-')
        ratio = validated.get('sex_ratio', '-')

        if isinstance(ratio, float):
            ratio = f"{ratio:.2f}"

        print(f"{record['names']:<12} {before:<20} → S:{after_sons} D:{after_daughters} Total:{total} Ratio:{ratio}")

    print()


def demo_statistics():
    """Calculate and display statistics."""
    print("="*70)
    print("DEMO: STATISTICAL ANALYSIS")
    print("="*70)
    print()

    # Use real Delhi data
    delhi_path = Path(__file__).parent.parent.parent / 'data' / 'delhi' / 'delhi.csv'
    df = pd.read_csv(delhi_path)

    stats = calculate_summary_stats(df)

    print("COMPREHENSIVE STATISTICS:")
    print("-"*70)

    for key, value in stats.items():
        if isinstance(value, float):
            print(f"{key:<30}: {value:.3f}")
        else:
            print(f"{key:<30}: {value}")

    print()

    # Show distribution
    print("FAMILY SIZE DISTRIBUTION:")
    print("-"*70)

    complete = df.dropna(subset=['sons', 'daughters'])
    complete['total'] = complete['sons'] + complete['daughters']

    print(f"{'Size':>5} {'Count':>8} {'% of Total':>12}")
    print("-"*70)

    for size in range(0, 7):
        count = len(complete[complete['total'] == size])
        pct = count / len(complete) * 100 if len(complete) > 0 else 0
        if count > 0:
            print(f"{size:>5} {count:>8} {pct:>12.1f}%")

    print()


def demo_combine():
    """Show how to combine multiple datasets."""
    print("="*70)
    print("DEMO: COMBINING MULTIPLE STATE DATASETS")
    print("="*70)
    print()

    # Simulate having collected from multiple states
    state1 = pd.DataFrame([
        {'names': 'MLA A', 'sons': 2, 'daughters': 1, 'state': 'State1'},
        {'names': 'MLA B', 'sons': 1, 'daughters': 2, 'state': 'State1'},
        {'names': 'MLA A', 'sons': 2, 'daughters': 1, 'state': 'State1'},  # Duplicate
    ])

    state2 = pd.DataFrame([
        {'names': 'MLA C', 'sons': 3, 'daughters': 0, 'state': 'State2'},
        {'names': 'MLA D', 'sons': 1, 'daughters': 1, 'state': 'State2'},
    ])

    state3 = pd.DataFrame([
        {'names': 'MLA E', 'sons': 0, 'daughters': 2, 'state': 'State3'},
    ])

    print("Dataset 1 (State1): 3 records (1 duplicate)")
    print("Dataset 2 (State2): 2 records")
    print("Dataset 3 (State3): 1 record")
    print()

    combined = combine_and_deduplicate([state1, state2, state3], key_columns=['names'])

    print(f"COMBINED DATASET: {len(combined)} unique records")
    print("-"*70)
    print(combined.to_string(index=False))
    print()

    # Calculate combined statistics
    stats = calculate_summary_stats(combined)
    print(f"Combined sex ratio: {stats['sex_ratio']:.3f}")
    print(f"Combined proportion daughters: {stats['proportion_daughters']:.3f}")
    print()


def demo_real_world_workflow():
    """Show a complete real-world workflow."""
    print("="*70)
    print("DEMO: COMPLETE ANALYSIS WORKFLOW")
    print("="*70)
    print()

    # Load Delhi data
    delhi_path = Path(__file__).parent.parent.parent / 'data' / 'delhi' / 'delhi.csv'
    delhi_df = pd.read_csv(delhi_path)

    print("STEP 1: Load data")
    print(f"  Loaded {len(delhi_df)} records from Delhi Assembly")
    print()

    print("STEP 2: Data quality check")
    complete = delhi_df.dropna(subset=['sons', 'daughters'])
    print(f"  Complete records: {len(complete)}/{len(delhi_df)} ({len(complete)/len(delhi_df)*100:.1f}%)")
    print()

    print("STEP 3: Calculate statistics")
    stats = calculate_summary_stats(delhi_df)
    print(f"  Sex ratio: {stats['sex_ratio']:.3f}")
    print(f"  Proportion daughters: {stats['proportion_daughters']:.3f}")
    print()

    print("STEP 4: Statistical significance test")
    natural_ratio = 1.05
    observed_ratio = stats['sex_ratio']
    difference = observed_ratio - natural_ratio

    print(f"  Natural sex ratio: {natural_ratio}")
    print(f"  Observed sex ratio: {observed_ratio:.3f}")
    print(f"  Difference: {difference:.3f}")

    if difference > 0.05:
        print(f"  ⚠️  SIGNIFICANT: Sex ratio is notably higher than natural")
    else:
        print(f"  ✓ Sex ratio within expected range")

    print()

    print("STEP 5: Calculate missing daughters")
    expected_daughters = stats['total_children'] * (1 / (1 + natural_ratio))
    actual_daughters = stats['total_daughters']
    missing = expected_daughters - actual_daughters

    print(f"  Expected daughters (natural): {expected_daughters:.1f}")
    print(f"  Actual daughters: {actual_daughters}")
    print(f"  Missing daughters: ~{int(missing)}")
    print()

    print("STEP 6: Top politicians by family size")
    print("-"*70)
    complete['total'] = complete['sons'] + complete['daughters']
    top10 = complete.nlargest(5, 'total')[['names', 'sons', 'daughters', 'total']]
    print(top10.to_string(index=False))
    print()


def main():
    print("\n" + "="*70)
    print("DATA COLLECTION UTILITIES - COMPREHENSIVE DEMO")
    print("="*70 + "\n")

    demo_text_extraction()
    demo_validation()
    demo_statistics()
    demo_combine()
    demo_real_world_workflow()

    print("="*70)
    print("SUMMARY")
    print("="*70)
    print()
    print("The utility functions provide:")
    print("  ✓ Text parsing for various formats")
    print("  ✓ Data validation and normalization")
    print("  ✓ Statistical calculations")
    print("  ✓ Dataset combination and deduplication")
    print("  ✓ Complete analysis workflows")
    print()
    print("These functions are reusable across all data sources!")
    print()


if __name__ == '__main__':
    main()
