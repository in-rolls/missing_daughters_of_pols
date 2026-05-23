"""
Extract children names from Kerala Assembly member PDFs.

The PDFs have biographical data with an English section listing children.
This script extracts the children's names for manual coding of sons/daughters.

Usage:
    python extract_kerala_children.py --input ../../data/kerala/kerala_assembly_20251119_052007.csv
"""

import pandas as pd
import requests
import re
import argparse
import logging
from pathlib import Path
from datetime import datetime
import time

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


def download_pdf(url, timeout=15):
    """Download PDF and return content."""
    try:
        response = requests.get(url, timeout=timeout)
        if response.status_code == 200:
            return response.content
        else:
            logger.warning(f"Failed to download: {response.status_code}")
            return None
    except Exception as e:
        logger.error(f"Error downloading PDF: {e}")
        return None


def extract_text_from_pdf_simple(pdf_content):
    """
    Extract text from PDF using pypdfium2.
    """
    try:
        import pypdfium2 as pdfium
        import io

        # Load PDF from bytes
        pdf = pdfium.PdfDocument(pdf_content)

        # Extract text from all pages
        text_parts = []
        for page_num in range(len(pdf)):
            page = pdf[page_num]
            textpage = page.get_textpage()
            text = textpage.get_text_range()
            text_parts.append(text)

        return '\n'.join(text_parts)

    except Exception as e:
        logger.error(f"Error extracting text from PDF: {e}")
        return ""


def extract_children_names(text):
    """
    Extract children names from PDF text.

    Kerala Assembly PDFs list children with honorifics like:
    - Master [Name] (for sons)
    - Smt. [Name] (for daughters/married women)
    - Kumari [Name] (for unmarried daughters)

    Also formats like "of Shri [father] and Smt. [mother] born at [place]"
    """

    children_names = []

    # Find all instances of children with honorifics
    # Pattern: Master/Smt./Kumari followed by name, then optional "of Shri..."
    pattern = r'(Master|Smt\.|Kumari|Shri)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)'

    matches = re.findall(pattern, text)

    for honorific, name in matches:
        # Clean up name
        name = name.strip()

        # Filter out common non-child names (parents)
        # If followed by "and Smt." it's usually parent names
        if name and len(name) > 1:
            children_names.append(f"{honorific} {name}")

    # Alternative: Look for explicit "Children:", "Son:", "Daughter:" sections
    children_section = re.search(r'(?:Children|Sons?|Daughters?)[:\s]+([^\n]+)', text, re.IGNORECASE)
    if children_section:
        section_text = children_section.group(1)
        # Split by commas
        for item in re.split(r'[,;]', section_text):
            item = item.strip()
            # Extract just the name part (remove "of Shri..." and other details)
            name_match = re.search(r'(Master|Smt\.|Kumari|Shri)?\s*([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)', item)
            if name_match:
                honorific = name_match.group(1) or ""
                name = name_match.group(2)
                if name:
                    full_name = f"{honorific} {name}".strip()
                    if full_name not in children_names:
                        children_names.append(full_name)

    # Remove duplicates while preserving order
    seen = set()
    unique_children = []
    for child in children_names:
        if child not in seen:
            seen.add(child)
            unique_children.append(child)

    return unique_children


def process_member(row, test_mode=False):
    """Process a single member's PDF to extract children names."""

    name = row['name']
    pdf_url = row['pdf_url']

    logger.info(f"Processing: {name[:50]}")

    if test_mode:
        # In test mode, just check if URL is accessible
        try:
            response = requests.head(pdf_url, timeout=5)
            if response.status_code == 200:
                logger.info(f"  ✓ PDF accessible")
                return "Test mode - PDF accessible"
            else:
                logger.warning(f"  ✗ PDF not accessible: {response.status_code}")
                return "Test mode - PDF not accessible"
        except Exception as e:
            logger.error(f"  Error: {e}")
            return "Test mode - Error"

    # Download PDF
    pdf_content = download_pdf(pdf_url)

    if not pdf_content:
        return None

    # Extract text
    text = extract_text_from_pdf_simple(pdf_content)

    if not text:
        logger.warning(f"  Could not extract text from PDF")
        return None

    # Extract children names
    children = extract_children_names(text)

    if children:
        logger.info(f"  Found {len(children)} children: {', '.join(children)}")
        return '; '.join(children)  # Use semicolon as separator
    else:
        logger.info(f"  No children found")
        return None


def main():
    parser = argparse.ArgumentParser(description='Extract children names from Kerala Assembly PDFs')
    parser.add_argument('--input', required=True, help='Input CSV file with PDF URLs')
    parser.add_argument('--output', help='Output CSV file (default: same as input with _with_children suffix)')
    parser.add_argument('--test', action='store_true', help='Test mode: process only first 5 members')
    parser.add_argument('--limit', type=int, help='Process only first N members')
    args = parser.parse_args()

    print("\n" + "="*70)
    print("KERALA ASSEMBLY - CHILDREN NAME EXTRACTION")
    print("="*70)
    print()

    # Load data
    logger.info(f"Loading data from {args.input}")
    df = pd.read_csv(args.input)

    logger.info(f"Total members: {len(df)}")

    # Limit if requested
    if args.test:
        df = df.head(5)
        logger.info("TEST MODE: Processing only first 5 members")
    elif args.limit:
        df = df.head(args.limit)
        logger.info(f"Processing only first {args.limit} members")

    # Process each member
    logger.info("\nExtracting children names...")
    logger.info("="*70)

    children_names = []

    for idx, row in df.iterrows():
        children = process_member(row, test_mode=args.test)
        children_names.append(children)

        # Rate limiting
        time.sleep(0.5)

        if (idx + 1) % 10 == 0:
            logger.info(f"Progress: {idx + 1}/{len(df)} members processed")

    # Add to dataframe
    df['children_names'] = children_names

    # Save
    if args.output:
        output_file = args.output
    else:
        input_path = Path(args.input)
        output_file = input_path.parent / f"{input_path.stem}_with_children{input_path.suffix}"

    df.to_csv(output_file, index=False)
    logger.info(f"\n✓ Saved to: {output_file}")

    # Statistics
    with_children = df['children_names'].notna().sum()
    logger.info(f"\nStatistics:")
    logger.info(f"  Total members: {len(df)}")
    logger.info(f"  With children data: {with_children} ({with_children/len(df)*100:.1f}%)")

    # Show sample
    print("\n" + "="*70)
    print("SAMPLE (first 10 with children)")
    print("="*70)
    sample = df[df['children_names'].notna()].head(10)
    for _, row in sample.iterrows():
        print(f"{row['name'][:40]:40} | {row['children_names']}")


if __name__ == '__main__':
    main()
