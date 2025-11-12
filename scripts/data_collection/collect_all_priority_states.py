"""
Master script to collect data from all priority states.

This script orchestrates collection from multiple states, with proper
error handling, progress tracking, and checkpoint management.

Usage:
    # Collect from all Tier 1 states
    python collect_all_priority_states.py --tier 1

    # Collect from all states
    python collect_all_priority_states.py --tier all

    # Resume from checkpoint
    python collect_all_priority_states.py --tier 1 --resume
"""

import argparse
import logging
import json
from pathlib import Path
import sys
from datetime import datetime

sys.path.append(str(Path(__file__).parent / 'utilities'))
sys.path.append(str(Path(__file__).parent / 'state_assemblies'))

from scraping_utils import RateLimitedSession

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# State priority tiers with most recent election years
STATES_TIER_1 = [
    ('maharashtra', 2019),
    ('west bengal', 2021),
    ('tamil nadu', 2021),
    ('karnataka', 2023),
    ('gujarat', 2022),
    ('madhya pradesh', 2023),
    ('rajasthan', 2023),
    ('bihar', 2020),
    ('andhra pradesh', 2019),
    ('telangana', 2023),
]

STATES_TIER_2 = [
    ('odisha', 2019),
    ('kerala', 2021),
    ('punjab', 2022),
    ('haryana', 2019),
    ('jharkhand', 2019),
    ('assam', 2021),
    ('chhattisgarh', 2023),
    ('uttarakhand', 2022),
    ('himachal pradesh', 2022),
]

STATES_TIER_3 = [
    ('goa', 2022),
    ('manipur', 2022),
    ('tripura', 2023),
    ('meghalaya', 2023),
    ('nagaland', 2023),
    ('mizoram', 2023),
    ('arunachal pradesh', 2019),
    ('sikkim', 2019),
]


class MasterCollector:
    """
    Orchestrate data collection from multiple states.
    """

    def __init__(self, output_dir: str, checkpoint_file: str = 'collection_progress.json'):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.checkpoint_file = self.output_dir / checkpoint_file
        self.progress = self._load_progress()

    def _load_progress(self):
        """Load collection progress from checkpoint."""
        if self.checkpoint_file.exists():
            with open(self.checkpoint_file, 'r') as f:
                return json.load(f)
        return {'completed': [], 'failed': [], 'last_updated': None}

    def _save_progress(self):
        """Save collection progress."""
        self.progress['last_updated'] = datetime.now().isoformat()
        with open(self.checkpoint_file, 'w') as f:
            json.dump(self.progress, f, indent=2)

    def collect_state(self, state: str, year: int):
        """
        Collect data for a single state.

        Args:
            state: State name
            year: Election year

        Returns:
            bool: True if successful, False otherwise
        """
        logger.info(f"\n{'='*70}")
        logger.info(f"Collecting: {state.upper()} ({year})")
        logger.info(f"{'='*70}")

        state_key = f"{state}_{year}"

        # Check if already completed
        if state_key in self.progress['completed']:
            logger.info(f"Already completed: {state} ({year}). Skipping...")
            return True

        # Import and run the collector
        try:
            from collect_election_affidavits import AffidavitCollector

            state_output_dir = self.output_dir / state.replace(' ', '_')
            collector = AffidavitCollector(state, year, str(state_output_dir))

            result = collector.collect()

            if result is not None and len(result) > 0:
                logger.info(f"✓ Successfully collected {len(result)} records from {state}")
                self.progress['completed'].append(state_key)
                self._save_progress()
                return True
            else:
                logger.warning(f"✗ No data collected from {state}")
                self.progress['failed'].append({
                    'state': state_key,
                    'reason': 'No data returned',
                    'timestamp': datetime.now().isoformat()
                })
                self._save_progress()
                return False

        except Exception as e:
            logger.error(f"✗ Error collecting from {state}: {e}")
            self.progress['failed'].append({
                'state': state_key,
                'reason': str(e),
                'timestamp': datetime.now().isoformat()
            })
            self._save_progress()
            return False

    def collect_tier(self, tier: int):
        """
        Collect data from all states in a tier.

        Args:
            tier: Tier number (1, 2, or 3)
        """
        if tier == 1:
            states = STATES_TIER_1
            tier_name = "Tier 1: Large States"
        elif tier == 2:
            states = STATES_TIER_2
            tier_name = "Tier 2: Medium States"
        elif tier == 3:
            states = STATES_TIER_3
            tier_name = "Tier 3: Smaller States"
        else:
            raise ValueError(f"Invalid tier: {tier}")

        logger.info(f"\n{'='*70}")
        logger.info(f"COLLECTING {tier_name.upper()}")
        logger.info(f"Total states: {len(states)}")
        logger.info(f"{'='*70}\n")

        successful = 0
        failed = 0

        for i, (state, year) in enumerate(states, 1):
            logger.info(f"\nProgress: {i}/{len(states)} states")

            if self.collect_state(state, year):
                successful += 1
            else:
                failed += 1

        # Print summary
        logger.info(f"\n{'='*70}")
        logger.info(f"TIER {tier} COLLECTION SUMMARY")
        logger.info(f"{'='*70}")
        logger.info(f"Successful: {successful}/{len(states)}")
        logger.info(f"Failed: {failed}/{len(states)}")
        logger.info(f"{'='*70}\n")

    def collect_all(self):
        """Collect from all states across all tiers."""
        logger.info("\n" + "="*70)
        logger.info("COLLECTING FROM ALL STATES")
        logger.info("="*70 + "\n")

        for tier in [1, 2, 3]:
            self.collect_tier(tier)

        # Final summary
        self.print_final_summary()

    def print_final_summary(self):
        """Print final collection summary."""
        completed = len(self.progress['completed'])
        failed = len(self.progress['failed'])
        total = completed + failed

        logger.info("\n" + "="*70)
        logger.info("FINAL COLLECTION SUMMARY")
        logger.info("="*70)
        logger.info(f"Total states attempted: {total}")
        logger.info(f"Successfully collected: {completed}")
        logger.info(f"Failed: {failed}")

        if failed > 0:
            logger.info("\nFailed states:")
            for failure in self.progress['failed']:
                logger.info(f"  - {failure['state']}: {failure['reason']}")

        logger.info(f"\nData saved to: {self.output_dir}")
        logger.info(f"Progress checkpoint: {self.checkpoint_file}")
        logger.info("="*70 + "\n")


def main():
    parser = argparse.ArgumentParser(
        description='Collect data from multiple state assemblies'
    )
    parser.add_argument(
        '--tier',
        choices=['1', '2', '3', 'all'],
        required=True,
        help='Which tier of states to collect (1=large, 2=medium, 3=small, all=everything)'
    )
    parser.add_argument(
        '--output',
        default='../../data/',
        help='Base output directory for all data'
    )
    parser.add_argument(
        '--resume',
        action='store_true',
        help='Resume from checkpoint (skip already completed states)'
    )

    args = parser.parse_args()

    # Create master collector
    collector = MasterCollector(args.output)

    # Print current progress if resuming
    if args.resume and collector.progress['completed']:
        logger.info("\nResuming from checkpoint...")
        logger.info(f"Already completed: {len(collector.progress['completed'])} states")

    # Collect based on tier
    if args.tier == 'all':
        collector.collect_all()
    else:
        collector.collect_tier(int(args.tier))


if __name__ == '__main__':
    main()
