"""
Extract biographical data (particularly children's gender information) from PDF documents.

This script handles various PDF formats commonly used by Indian state assemblies
for publishing member biographical information.

Requirements:
    pip install PyPDF2 pdfplumber pandas tabula-py

Usage:
    python extract_biographical_data.py --input path/to/pdf --output path/to/output.csv
    python extract_biographical_data.py --input ../../../data/up/ --output ../../../data/up/extracted.csv
"""

import argparse
import re
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any
import pandas as pd

try:
    import pdfplumber
except ImportError:
    print("Please install pdfplumber: pip install pdfplumber")
    exit(1)

import sys
sys.path.append(str(Path(__file__).parent.parent / 'utilities'))
from scraping_utils import extract_children_from_text, validate_family_data, calculate_summary_stats

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class BiographicalPDFExtractor:
    """
    Extract biographical data from PDF documents.
    """

    def __init__(self):
        self.patterns = {
            'name': [
                r'(?:Name|नाम|Shri|Smt\.?|Dr\.?|Prof\.?)\s*:?\s*([A-Za-z\s\.]+)',
                r'^([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s*$',
            ],
            'sons': [
                r'Sons?\s*:?\s*(\d+)',
                r'(\d+)\s+Sons?',
                r'पुत्र\s*:?\s*(\d+)',
            ],
            'daughters': [
                r'Daughters?\s*:?\s*(\d+)',
                r'(\d+)\s+Daughters?',
                r'पुत्री\s*:?\s*(\d+)',
            ],
            'children': [
                r'Children\s*:?\s*(\d+)',
                r'संतान\s*:?\s*(\d+)',
            ],
            'party': [
                r'Party\s*:?\s*([A-Za-z\(\)\s]+)',
                r'राजनीतिक\s+दल\s*:?\s*([^।\n]+)',
            ],
            'constituency': [
                r'Constituency\s*:?\s*([A-Za-z\s]+)',
                r'निर्वाचन\s+क्षेत्र\s*:?\s*([^।\n]+)',
            ]
        }

    def extract_from_text(self, text: str) -> Dict[str, Any]:
        """
        Extract biographical information from text.

        Args:
            text: Text extracted from PDF

        Returns:
            Dictionary with extracted information
        """
        result = {}

        # Extract using patterns
        for field, patterns in self.patterns.items():
            for pattern in patterns:
                match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
                if match:
                    result[field] = match.group(1).strip()
                    break

        # Use the utility function for more sophisticated extraction
        children_data = extract_children_from_text(text)
        if children_data['sons'] is not None:
            result['sons'] = children_data['sons']
        if children_data['daughters'] is not None:
            result['daughters'] = children_data['daughters']

        return result

    def extract_from_pdf(self, pdf_path: Path) -> List[Dict[str, Any]]:
        """
        Extract all biographical records from a PDF file.

        Args:
            pdf_path: Path to PDF file

        Returns:
            List of dictionaries with extracted data
        """
        logger.info(f"Processing {pdf_path}")
        records = []

        try:
            with pdfplumber.open(pdf_path) as pdf:
                for page_num, page in enumerate(pdf.pages, 1):
                    text = page.extract_text()
                    if not text:
                        continue

                    # Try to extract structured data from tables
                    tables = page.extract_tables()
                    if tables:
                        records.extend(self._extract_from_tables(tables))

                    # Also extract from plain text
                    # Split by common delimiters for individual member entries
                    sections = self._split_into_entries(text)
                    for section in sections:
                        data = self.extract_from_text(section)
                        if data:  # Only add if we extracted something
                            data['pdf_source'] = pdf_path.name
                            data['page'] = page_num
                            records.append(data)

        except Exception as e:
            logger.error(f"Error processing {pdf_path}: {e}")

        logger.info(f"Extracted {len(records)} records from {pdf_path}")
        return records

    def _extract_from_tables(self, tables: List[List[List[str]]]) -> List[Dict[str, Any]]:
        """
        Extract data from PDF tables.
        """
        records = []

        for table in tables:
            if not table or len(table) < 2:
                continue

            # Try to identify header row
            header = [cell.lower().strip() if cell else '' for cell in table[0]]

            # Map common column names
            col_map = {}
            for i, col in enumerate(header):
                if any(term in col for term in ['name', 'नाम']):
                    col_map['name'] = i
                elif any(term in col for term in ['son', 'पुत्र']):
                    col_map['sons'] = i
                elif any(term in col for term in ['daughter', 'पुत्री']):
                    col_map['daughters'] = i
                elif any(term in col for term in ['party', 'दल']):
                    col_map['party'] = i
                elif any(term in col for term in ['constituency', 'क्षेत्र']):
                    col_map['constituency'] = i

            # Extract data rows
            for row in table[1:]:
                if not row or len(row) == 0:
                    continue

                record = {}
                for field, idx in col_map.items():
                    if idx < len(row) and row[idx]:
                        value = row[idx].strip()
                        if field in ['sons', 'daughters']:
                            try:
                                record[field] = int(value)
                            except ValueError:
                                pass
                        else:
                            record[field] = value

                if record:
                    records.append(record)

        return records

    def _split_into_entries(self, text: str) -> List[str]:
        """
        Split text into individual member entries.

        Different formats use different delimiters:
        - Sequential numbering (1., 2., 3.)
        - Horizontal lines (----)
        - Page breaks
        """
        # Try splitting by numbered entries
        entries = re.split(r'\n\s*\d+\.\s+', text)

        # If that didn't work well, try other methods
        if len(entries) < 5:
            # Try splitting by multiple newlines
            entries = re.split(r'\n\s*\n\s*\n', text)

        return [entry.strip() for entry in entries if entry.strip()]


def process_directory(input_path: Path, output_path: Path):
    """
    Process all PDFs in a directory.
    """
    extractor = BiographicalPDFExtractor()
    all_records = []

    pdf_files = list(input_path.glob('*.pdf'))
    logger.info(f"Found {len(pdf_files)} PDF files")

    for pdf_file in pdf_files:
        records = extractor.extract_from_pdf(pdf_file)
        all_records.extend(records)

    if all_records:
        # Convert to DataFrame
        df = pd.DataFrame(all_records)

        # Validate data
        validated_records = [validate_family_data(record) for record in all_records]
        df = pd.DataFrame(validated_records)

        # Remove duplicates based on name
        if 'name' in df.columns:
            df = df.drop_duplicates(subset=['name'], keep='first')

        # Save to CSV
        df.to_csv(output_path, index=False)
        logger.info(f"Saved {len(df)} records to {output_path}")

        # Print summary statistics if we have complete data
        if 'sons' in df.columns and 'daughters' in df.columns:
            stats = calculate_summary_stats(df)
            logger.info(f"Summary statistics: {stats}")

    else:
        logger.warning("No records extracted from PDFs")


def main():
    parser = argparse.ArgumentParser(
        description='Extract biographical data from PDF documents'
    )
    parser.add_argument(
        '--input',
        required=True,
        help='Path to PDF file or directory containing PDFs'
    )
    parser.add_argument(
        '--output',
        required=True,
        help='Path to output CSV file'
    )

    args = parser.parse_args()

    input_path = Path(args.input)
    output_path = Path(args.output)

    if not input_path.exists():
        logger.error(f"Input path does not exist: {input_path}")
        return

    # Create output directory if needed
    output_path.parent.mkdir(parents=True, exist_ok=True)

    if input_path.is_dir():
        process_directory(input_path, output_path)
    else:
        extractor = BiographicalPDFExtractor()
        records = extractor.extract_from_pdf(input_path)

        if records:
            validated_records = [validate_family_data(record) for record in records]
            df = pd.DataFrame(validated_records)
            df.to_csv(output_path, index=False)
            logger.info(f"Saved {len(df)} records to {output_path}")

            if 'sons' in df.columns and 'daughters' in df.columns:
                stats = calculate_summary_stats(df)
                logger.info(f"Summary statistics: {stats}")
        else:
            logger.warning("No records extracted")


if __name__ == '__main__':
    main()
