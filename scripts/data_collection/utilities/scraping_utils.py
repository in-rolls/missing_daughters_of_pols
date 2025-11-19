"""
Utility functions for web scraping political data.
Includes rate limiting, error handling, and common patterns.
"""

import requests
import time
import logging
from typing import Optional, Dict, Any
import json
from pathlib import Path
import pandas as pd

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class RateLimitedSession:
    """
    A requests session wrapper that enforces rate limiting
    and provides retry logic with exponential backoff.
    """

    def __init__(self, delay: float = 1.0, max_retries: int = 3):
        """
        Args:
            delay: Minimum seconds between requests
            max_retries: Maximum number of retry attempts
        """
        self.session = requests.Session()
        self.delay = delay
        self.max_retries = max_retries
        self.last_request_time = 0

    def get(self, url: str, **kwargs) -> Optional[requests.Response]:
        """
        Make a GET request with rate limiting and retry logic.

        Args:
            url: URL to fetch
            **kwargs: Additional arguments to pass to requests.get()

        Returns:
            Response object or None if all retries failed
        """
        # Enforce rate limiting
        elapsed = time.time() - self.last_request_time
        if elapsed < self.delay:
            time.sleep(self.delay - elapsed)

        # Retry logic
        for attempt in range(self.max_retries):
            try:
                response = self.session.get(url, **kwargs)
                self.last_request_time = time.time()

                if response.status_code == 200:
                    return response
                elif response.status_code == 429:  # Too many requests
                    wait_time = 2 ** attempt * 5  # Exponential backoff
                    logger.warning(f"Rate limited. Waiting {wait_time}s before retry...")
                    time.sleep(wait_time)
                else:
                    logger.warning(f"Request failed with status {response.status_code}: {url}")
                    return response

            except requests.RequestException as e:
                logger.error(f"Request error (attempt {attempt + 1}/{self.max_retries}): {e}")
                if attempt < self.max_retries - 1:
                    time.sleep(2 ** attempt)  # Exponential backoff

        logger.error(f"All retry attempts failed for: {url}")
        return None

    def post(self, url: str, **kwargs) -> Optional[requests.Response]:
        """
        Make a POST request with rate limiting and retry logic.
        """
        elapsed = time.time() - self.last_request_time
        if elapsed < self.delay:
            time.sleep(self.delay - elapsed)

        for attempt in range(self.max_retries):
            try:
                response = self.session.post(url, **kwargs)
                self.last_request_time = time.time()

                if response.status_code == 200:
                    return response
                else:
                    logger.warning(f"POST request failed with status {response.status_code}: {url}")
                    return response

            except requests.RequestException as e:
                logger.error(f"POST request error (attempt {attempt + 1}/{self.max_retries}): {e}")
                if attempt < self.max_retries - 1:
                    time.sleep(2 ** attempt)

        logger.error(f"All retry attempts failed for POST: {url}")
        return None


class DataCollector:
    """
    Base class for collecting biographical data from political bodies.
    Provides common functionality for data collection, validation, and storage.
    """

    def __init__(self, output_dir: str, name: str):
        """
        Args:
            output_dir: Directory to save collected data
            name: Name of the data source (e.g., 'maharashtra_assembly')
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.name = name
        self.session = RateLimitedSession()
        self.data = []

    def save_json(self, data: Any, filename: str):
        """Save data as JSON."""
        filepath = self.output_dir / filename
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        logger.info(f"Saved JSON to {filepath}")

    def save_csv(self, df: pd.DataFrame, filename: str):
        """Save DataFrame as CSV."""
        filepath = self.output_dir / filename
        df.to_csv(filepath, index=False, encoding='utf-8')
        logger.info(f"Saved CSV to {filepath}")

    def load_checkpoint(self, checkpoint_file: str) -> Dict:
        """Load checkpoint data to resume collection."""
        filepath = self.output_dir / checkpoint_file
        if filepath.exists():
            with open(filepath, 'r') as f:
                return json.load(f)
        return {}

    def save_checkpoint(self, checkpoint_data: Dict, checkpoint_file: str):
        """Save checkpoint to allow resuming collection."""
        self.save_json(checkpoint_data, checkpoint_file)


def validate_family_data(record: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate and normalize family data fields.

    Args:
        record: Dictionary with family information

    Returns:
        Validated and normalized record
    """
    validated = record.copy()

    # Normalize son/daughter fields
    for field in ['sons', 'daughters']:
        if field in validated:
            val = validated[field]
            if val is None or val == '':
                validated[field] = None
            elif isinstance(val, str):
                try:
                    validated[field] = int(val)
                except ValueError:
                    logger.warning(f"Invalid {field} value: {val}")
                    validated[field] = None
            elif not isinstance(val, int):
                validated[field] = None

    # Calculate total if both present
    if validated.get('sons') is not None and validated.get('daughters') is not None:
        validated['total_children'] = validated['sons'] + validated['daughters']

    # Calculate sex ratio if both present and daughters > 0
    if (validated.get('sons') is not None and
        validated.get('daughters') is not None and
        validated.get('daughters') > 0):
        validated['sex_ratio'] = validated['sons'] / validated['daughters']

    return validated


def extract_children_from_text(text: str) -> Dict[str, Optional[int]]:
    """
    Extract number of sons and daughters from biographical text.

    Looks for patterns like:
    - "2 sons and 1 daughter"
    - "Son: 2, Daughter: 1"
    - "3 sons, 2 daughters"
    - "1 son", "2 daughters"

    Args:
        text: Biographical text

    Returns:
        Dictionary with 'sons' and 'daughters' counts
    """
    import re

    result = {'sons': None, 'daughters': None}

    if not text:
        return result

    text = text.lower()

    # Pattern 1: "N son(s)" - match word boundaries to avoid false matches
    son_match = re.search(r'(\d+)\s*sons?\b', text)
    if son_match:
        result['sons'] = int(son_match.group(1))

    # Pattern 2: "N daughter(s)" - match word boundaries
    daughter_match = re.search(r'(\d+)\s*daughters?\b', text)
    if daughter_match:
        result['daughters'] = int(daughter_match.group(1))

    # Pattern 3: "Son: N" or "Son(s): N"
    son_colon = re.search(r'sons?:\s*(\d+)', text)
    if son_colon:
        result['sons'] = int(son_colon.group(1))

    # Pattern 4: "Daughter: N" or "Daughter(s): N"
    daughter_colon = re.search(r'daughters?:\s*(\d+)', text)
    if daughter_colon:
        result['daughters'] = int(daughter_colon.group(1))

    # Pattern 5: "son and daughter" (implies 1 of each)
    if 'son and daughter' in text and result['sons'] is None and result['daughters'] is None:
        # Check if there's a number before "son"
        one_each = re.search(r'\b(?:has\s+)?(?:a\s+)?son\s+and\s+(?:a\s+)?daughter\b', text)
        if one_each:
            result['sons'] = 1
            result['daughters'] = 1

    return result


def combine_and_deduplicate(dataframes: list, key_columns: list = ['names']) -> pd.DataFrame:
    """
    Combine multiple dataframes and remove duplicates.

    Args:
        dataframes: List of DataFrames to combine
        key_columns: Columns to use for identifying duplicates

    Returns:
        Combined DataFrame with duplicates removed
    """
    if not dataframes:
        return pd.DataFrame()

    combined = pd.concat(dataframes, ignore_index=True)

    # Remove exact duplicates
    combined = combined.drop_duplicates()

    # Remove duplicates based on key columns, keeping first occurrence
    combined = combined.drop_duplicates(subset=key_columns, keep='first')

    logger.info(f"Combined {len(dataframes)} dataframes into {len(combined)} records")

    return combined


def calculate_summary_stats(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Calculate summary statistics for family data.

    Args:
        df: DataFrame with 'sons' and 'daughters' columns

    Returns:
        Dictionary with summary statistics
    """
    # Filter to records with complete data
    complete_data = df.dropna(subset=['sons', 'daughters'])

    if len(complete_data) == 0:
        return {'error': 'No complete records found'}

    total_sons = complete_data['sons'].sum()
    total_daughters = complete_data['daughters'].sum()
    total_children = total_sons + total_daughters

    stats = {
        'n_politicians': len(complete_data),
        'total_sons': int(total_sons),
        'total_daughters': int(total_daughters),
        'total_children': int(total_children),
        'sex_ratio': total_sons / total_daughters if total_daughters > 0 else None,
        'mean_sons': complete_data['sons'].mean(),
        'mean_daughters': complete_data['daughters'].mean(),
        'mean_total_children': (complete_data['sons'] + complete_data['daughters']).mean(),
        'proportion_daughters': total_daughters / total_children if total_children > 0 else None
    }

    return stats
