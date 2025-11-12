"""
Demonstration script showing how to analyze collected data.

This analyzes the existing Delhi assembly data to show:
1. How to load collected data
2. How to calculate statistics
3. How to compare with Lok Sabha results
"""

import pandas as pd
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent / 'utilities'))
from scraping_utils import calculate_summary_stats

def analyze_delhi():
    """Analyze Delhi Assembly data."""
    print("="*70)
    print("DELHI LEGISLATIVE ASSEMBLY ANALYSIS")
    print("="*70)
    print()

    # Load Delhi data
    delhi_path = Path(__file__).parent.parent.parent / 'data' / 'delhi' / 'delhi.csv'

    if not delhi_path.exists():
        print(f"Error: Delhi data not found at {delhi_path}")
        return

    df = pd.read_csv(delhi_path)

    print(f"Total MLAs in dataset: {len(df)}")
    print()

    # Filter to complete records
    complete_df = df.dropna(subset=['sons', 'daughters'])
    print(f"MLAs with complete family data: {len(complete_df)}")
    print()

    # Calculate statistics
    stats = calculate_summary_stats(df)

    print("SUMMARY STATISTICS")
    print("-" * 70)
    print(f"Total Sons: {stats['total_sons']}")
    print(f"Total Daughters: {stats['total_daughters']}")
    print(f"Total Children: {stats['total_children']}")
    print()
    print(f"Sex Ratio (sons/daughters): {stats['sex_ratio']:.2f}")
    print(f"Proportion of Daughters: {stats['proportion_daughters']:.3f}")
    print()
    print(f"Mean Sons per MLA: {stats['mean_sons']:.2f}")
    print(f"Mean Daughters per MLA: {stats['mean_daughters']:.2f}")
    print(f"Mean Total Children: {stats['mean_total_children']:.2f}")
    print()

    # Compare with natural sex ratio
    natural_ratio = 1.05
    print("COMPARISON WITH NATURAL SEX RATIO")
    print("-" * 70)
    print(f"Natural sex ratio: {natural_ratio:.2f}")
    print(f"Delhi MLAs sex ratio: {stats['sex_ratio']:.2f}")
    print(f"Difference: {stats['sex_ratio'] - natural_ratio:.2f}")
    print()

    if stats['sex_ratio'] > natural_ratio:
        excess = stats['sex_ratio'] - natural_ratio
        missing_daughters = int(stats['total_sons'] / stats['sex_ratio'] * excess)
        print(f"⚠️  Sex ratio is HIGHER than natural ratio")
        print(f"Estimated missing daughters: ~{missing_daughters}")
    else:
        print("✓ Sex ratio is within normal range")

    print()

    # Show top 10 members by family size
    print("TOP 10 MLAs BY FAMILY SIZE")
    print("-" * 70)
    df_sorted = complete_df.copy()
    df_sorted['total'] = df_sorted['sons'] + df_sorted['daughters']
    df_sorted = df_sorted.sort_values('total', ascending=False).head(10)

    print(f"{'Name':<30} {'Sons':>5} {'Daughters':>10} {'Total':>7}")
    print("-" * 70)
    for _, row in df_sorted.iterrows():
        print(f"{row['names']:<30} {int(row['sons']):>5} {int(row['daughters']):>10} {int(row['total']):>7}")

    print()

    # Distribution by family size
    print("DISTRIBUTION BY FAMILY SIZE")
    print("-" * 70)
    df_analysis = complete_df.copy()
    df_analysis['total'] = df_analysis['sons'] + df_analysis['daughters']

    for size in range(1, 7):
        subset = df_analysis[df_analysis['total'] == size]
        if len(subset) > 0:
            prop_daughters = subset['daughters'].sum() / (subset['sons'].sum() + subset['daughters'].sum())
            print(f"{size} children: {len(subset):>3} MLAs, Prop. daughters: {prop_daughters:.3f}")

    print()


def compare_with_lok_sabha():
    """Compare Delhi results with Lok Sabha results from the README."""
    print("="*70)
    print("COMPARISON WITH LOK SABHA")
    print("="*70)
    print()

    # Lok Sabha statistics from the README
    lok_sabha_17_ratio = 1.14
    lok_sabha_17_prop = 0.44
    lok_sabha_overall_ratio = 1.085

    # Delhi statistics
    delhi_path = Path(__file__).parent.parent.parent / 'data' / 'delhi' / 'delhi.csv'
    delhi_df = pd.read_csv(delhi_path)
    delhi_stats = calculate_summary_stats(delhi_df)

    print(f"{'Metric':<40} {'17th Lok Sabha':>15} {'Delhi Assembly':>15}")
    print("-" * 70)
    print(f"{'Sex Ratio':<40} {lok_sabha_17_ratio:>15.2f} {delhi_stats['sex_ratio']:>15.2f}")
    print(f"{'Proportion Daughters':<40} {lok_sabha_17_prop:>15.2f} {delhi_stats['proportion_daughters']:>15.2f}")
    print()

    print("INTERPRETATION")
    print("-" * 70)
    if delhi_stats['sex_ratio'] > lok_sabha_17_ratio:
        print("Delhi MLAs have HIGHER sex ratio than 17th Lok Sabha")
        print("(more skewed towards sons)")
    else:
        print("Delhi MLAs have LOWER sex ratio than 17th Lok Sabha")
        print("(less skewed towards sons)")

    print()
    print(f"Overall Lok Sabha (12-17): {lok_sabha_overall_ratio:.2f}")
    print(f"Delhi Assembly: {delhi_stats['sex_ratio']:.2f}")
    print()


def main():
    """Run all analyses."""
    print("\n" + "="*70)
    print("DATA COLLECTION FRAMEWORK - SAMPLE ANALYSIS")
    print("="*70 + "\n")

    analyze_delhi()
    compare_with_lok_sabha()

    print("="*70)
    print("NEXT STEPS")
    print("="*70)
    print()
    print("1. Collect more state assemblies to expand the dataset")
    print("2. Analyze patterns across states")
    print("3. Compare with state-level sex ratio at birth data")
    print("4. Investigate party-wise differences")
    print()
    print("Use the collection scripts in:")
    print("  state_assemblies/collect_election_affidavits.py")
    print()


if __name__ == '__main__':
    main()
