"""
I/O utilities for loading data from individual JSON files.
"""

import json
from pathlib import Path
from typing import Iterator, Dict, Any, List


def load_json_files(data_dir: str = "data") -> Iterator[Dict[str, Any]]:
    """
    Load all JSON files from a directory.

    Args:
        data_dir: Directory containing JSON files

    Yields:
        Dictionary records from JSON files
    """
    data_path = Path(data_dir)

    if not data_path.exists():
        raise FileNotFoundError(f"Data directory not found: {data_dir}")

    json_files = sorted(data_path.glob("*.json"))

    if not json_files:
        raise FileNotFoundError(f"No JSON files found in {data_dir}")

    for json_file in json_files:
        with open(json_file, 'r', encoding='utf-8') as f:
            try:
                data = json.load(f)
                # Add filename for tracking
                data['_source_file'] = json_file.name
                yield data
            except json.JSONDecodeError as e:
                print(f"Warning: Failed to parse {json_file.name}: {e}")
                continue


def extract_fields(record: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extract all relevant fields from a record.

    Args:
        record: JSON record

    Returns:
        Dictionary with extracted fields
    """
    # Extract metadata
    metadata = record.get('metadata', {})

    return {
        # Core content
        'document_content': record.get('document_content', ''),
        'expected_summary': record.get('expected_summary', ''),
        'generated_summary': record.get('generated_summary', ''),

        # Metadata
        'document_title': record.get('document_title', ''),
        'link': record.get('link', ''),
        'author': metadata.get('author', ''),
        'sector': metadata.get('sector', ''),
        'region': metadata.get('region', ''),
        'date': metadata.get('date', ''),
        'wire_id': metadata.get('wire_id', ''),
        'subject_codes': metadata.get('subject_codes', []),

        # Model info
        'prompt_type': record.get('prompt_type', ''),
        'model_used': record.get('model_used', ''),
        'export_timestamp': record.get('export_timestamp', ''),

        # Tracking
        '_source_file': record.get('_source_file', ''),
    }


def infer_persona(record: Dict[str, Any]) -> str:
    """
    Infer persona from record metadata.

    Uses prompt_type, author role, and sector to determine writing style.

    Args:
        record: JSON record

    Returns:
        Persona ID (formal_analyst, journalist, or enthusiast)
    """
    prompt_type = record.get('prompt_type', '').lower()
    author = record.get('author', '').lower()
    sector = record.get('sector', '').lower()

    # Formal analyst style: research notes, detailed analysis
    if any(keyword in prompt_type for keyword in ['research', 'analyst', 'note']):
        return 'formal_analyst'

    if any(keyword in author for keyword in ['analyst', 'economist', 'strategist', 'phd', 'cfa']):
        return 'formal_analyst'

    # Journalist style: morning summaries, news-style
    if any(keyword in prompt_type for keyword in ['morning', 'summary', 'brief', 'update']):
        return 'journalist'

    # Enthusiast style: quick takes, highlights
    if any(keyword in prompt_type for keyword in ['quick', 'highlight', 'takeaway']):
        return 'enthusiast'

    # Default to journalist for financial/business content
    return 'journalist'


def load_all_records(data_dir: str = "data") -> List[Dict[str, Any]]:
    """
    Load and process all JSON files from directory.

    Args:
        data_dir: Directory containing JSON files

    Returns:
        List of processed records with extracted fields and inferred personas
    """
    records = []

    for raw_record in load_json_files(data_dir):
        # Extract all fields
        extracted = extract_fields(raw_record)

        # Infer persona
        extracted['persona'] = infer_persona(extracted)

        records.append(extracted)

    return records
