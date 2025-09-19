#!/usr/bin/env python3
"""
Professional Industry-Level PDF to JSON Converter using Unstructured

This script leverages the Unstructured library, an advanced open-source tool for ingesting and pre-processing unstructured documents, to convert PDFs into structured JSON format. It extracts text, tables, and images (treated as charts) while preserving page information and applying heuristics for section detection.

Schema:
- pages: List of page dictionaries
  - page_number: Integer page number
  - content: List of content dictionaries
    - type: 'paragraph', 'table', or 'chart'
    - section: Detected section (e.g., '1.1')
    - sub_section: Detected subsection
    - description: Descriptive text (e.g., for charts)
    - text: Extracted text (for paragraphs)
    - table_data: 2D list for table rows (for tables)

Dependencies:
- unstructured[all-docs] (pip install "unstructured[all-docs]")
- fitz (PyMuPDF) for page count
- tqdm for progress
- logging for detailed output

For optimal performance, use 'hi_res' strategy which requires additional dependencies like detectron2.
"""

import argparse
import json
import logging
import re
from collections import defaultdict
from io import StringIO
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import fitz  # PyMuPDF
import pandas as pd
from tqdm import tqdm
from unstructured.partition.pdf import partition_pdf

# -------------------------
# CONFIGURATION
# -------------------------
DEFAULT_STRATEGY = "hi_res"  # Alternatives: "fast", "ocr_only", "hi_res"
FALLBACK_STRATEGY = "fast"

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# -------------------------
# UTILITY FUNCTIONS
# -------------------------
def detect_section_subsection(text: str) -> Tuple[Optional[str], Optional[str]]:
    """
    Detects section and subsection from text using regex-based heuristics.

    Args:
        text (str): Input text to analyze.

    Returns:
        Tuple[Optional[str], Optional[str]]: Section and subsection.
    """
    if not text:
        return None, None
    section_pattern = r"^\d+(\.\d+)*\s+(.+)$"
    match = re.match(section_pattern, text.strip())
    if match:
        section, content = match.groups()
        return section, content
    return None, None


def parse_markdown_table(md_text: str) -> Optional[List[List[str]]]:
    """
    Parses a markdown table string into a 2D list of strings.

    Args:
        md_text (str): Markdown table text.

    Returns:
        Optional[List[List[str]]]: Table data as list of rows, or None if parsing fails.
    """
    try:
        # Use pandas to parse the markdown table
        df = pd.read_csv(StringIO(md_text), sep="|", skiprows=1, engine="python")
        df = df.applymap(lambda x: str(x).strip() if pd.notnull(x) else "")
        # Remove any empty columns caused by separators
        df = df.loc[:, ~df.columns.str.contains("^Unnamed")]
        return df.values.tolist()
    except Exception as e:
        logger.warning(f"Failed to parse markdown table: {e}")
        return None


def map_element_type(category: str) -> str:
    """
    Maps Unstructured element category to schema type.

    Args:
        category (str): Element category from Unstructured.

    Returns:
        str: 'paragraph', 'table', or 'chart'.
    """
    if category == "Table":
        return "table"
    elif category in ["Image", "FigureCaption"]:
        return "chart"
    else:
        return "paragraph"


# -------------------------
# MAIN PROCESSING FUNCTIONS
# -------------------------
def process_pdf(pdf_path: str, strategy: str = DEFAULT_STRATEGY) -> Dict:
    """
    Processes a PDF file using Unstructured to extract structured content into JSON format.

    Args:
        pdf_path (str): Path to the PDF file.
        strategy (str): Partitioning strategy ('hi_res', 'fast', etc.).

    Returns:
        Dict: Structured JSON data with pages and content.
    """
    pdf_file = Path(pdf_path)
    if not pdf_file.is_file():
        logger.error(f"PDF file not found: {pdf_path}")
        raise FileNotFoundError(f"PDF file not found: {pdf_path}")

    # Get total pages for progress
    doc = fitz.open(pdf_path)
    total_pages = len(doc)
    doc.close()

    logger.info(f"Processing PDF: {pdf_path} with strategy '{strategy}'")

    try:
        elements = partition_pdf(
            filename=str(pdf_file),
            strategy=strategy,
            languages=["eng"],  # Add more languages if needed
            infer_table_structure=True,  # For hi_res
        )
    except Exception as e:
        if strategy != FALLBACK_STRATEGY:
            logger.warning(f"Strategy '{strategy}' failed: {e}. Falling back to '{FALLBACK_STRATEGY}'.")
            elements = partition_pdf(
                filename=str(pdf_file),
                strategy=FALLBACK_STRATEGY,
                languages=["eng"],
            )
        else:
            raise

    # Group elements by page and build content
    pages: Dict[int, List[Dict]] = defaultdict(list)
    current_section: Optional[str] = None
    current_subsection: Optional[str] = None

    for el in tqdm(elements, total=len(elements), desc="Processing elements"):
        page_num = el.metadata.page_number
        el_type = map_element_type(el.category)
        text = el.text if el.text else ""
        section, subsection = detect_section_subsection(text)

        if el.category == "Title":
            current_section = section or text
            current_subsection = subsection

        content_item = {
            "type": el_type,
            "section": current_section,
            "sub_section": current_subsection,
            "description": None,
            "text": text if el_type != "table" else None,
            "table_data": None,
        }

        if el_type == "table":
            table_data = parse_markdown_table(text)
            content_item["table_data"] = table_data
            content_item["description"] = f"Table on page {page_num}"

        elif el_type == "chart":
            content_item["description"] = f"Chart/Image on page {page_num} (category: {el.category})"
            content_item["text"] = None  # Text might be caption

        elif section:
            content_item["description"] = "Section header"

        # Add coordinates if available
        if hasattr(el.metadata, "coordinates"):
            bbox = el.metadata.coordinates.points
            content_item["description"] = (content_item["description"] or "") + f" (bbox={bbox})"

        pages[page_num].append(content_item)

    # Sort pages and format result
    result = {
        "pages": [
            {"page_number": page_num, "content": content}
            for page_num, content in sorted(pages.items())
        ]
    }
    logger.info(f"Processed {len(result['pages'])} pages with {sum(len(c['content']) for c in result['pages'])} content items")
    return result


# -------------------------
# ENTRY POINT
# -------------------------
def main():
    """Main function to parse arguments and execute the PDF to JSON conversion."""
    parser = argparse.ArgumentParser(description="Convert PDF to structured JSON using Unstructured.")
    parser.add_argument("pdf_path", type=str, help="Path to the input PDF file")
    parser.add_argument("-o", "--output", type=str, default="output.json", help="Path to the output JSON file")
    parser.add_argument("-s", "--strategy", type=str, default=DEFAULT_STRATEGY, help="Unstructured partitioning strategy")
    args = parser.parse_args()

    try:
        structured_json = process_pdf(args.pdf_path, args.strategy)
        output_path = Path(args.output)
        with output_path.open("w", encoding="utf-8") as f:
            json.dump(structured_json, f, indent=4, ensure_ascii=False)
        logger.info(f"Successfully wrote JSON output to {output_path}")
    except Exception as e:
        logger.error(f"Failed to process PDF: {str(e)}")
        raise


if __name__ == "__main__":
    main()