"""
I/O utilities for loading data and extracting fields based on config.
"""

import json
import csv
from pathlib import Path
from typing import Iterator, Dict, Any, Optional, Tuple


def load_jsonl(path: str) -> Iterator[Dict[str, Any]]:
    """
    Load JSONL file and yield records.

    Args:
        path: Path to JSONL file

    Yields:
        Dictionary records from the JSONL file
    """
    with open(path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line:
                yield json.loads(line)


def get_field(obj: Dict[str, Any], dotted_path: str, default: Any = None) -> Any:
    """
    Get nested field from object using dotted path notation.

    Args:
        obj: Dictionary object
        dotted_path: Path to field (e.g., "metadata.author")
        default: Default value if field not found

    Returns:
        Value at the specified path or default

    Examples:
        >>> obj = {"metadata": {"author": "John"}}
        >>> get_field(obj, "metadata.author")
        'John'
        >>> get_field(obj, "metadata.missing", "N/A")
        'N/A'
    """
    keys = dotted_path.split('.')
    current = obj

    for key in keys:
        if isinstance(current, dict) and key in current:
            current = current[key]
        else:
            return default

    return current


def load_persona_assignments(csv_path: str) -> Dict[str, str]:
    """
    Load persona assignments from CSV file.

    Args:
        csv_path: Path to CSV file with columns: write_id,persona_id

    Returns:
        Dictionary mapping write_id to persona_id
    """
    if not Path(csv_path).exists():
        return {}

    assignments = {}
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            write_id = row.get('write_id', '').strip()
            persona_id = row.get('persona_id', '').strip()
            if write_id and persona_id:
                assignments[write_id] = persona_id

    return assignments


def record_to_example(
    rec: Dict[str, Any],
    cfg: Dict[str, Any],
    persona_map: Dict[str, str]
) -> Tuple[str, str, str, Optional[str], Dict[str, Any]]:
    """
    Extract fields from record based on config.

    Args:
        rec: Record from JSONL
        cfg: Configuration dictionary with field mappings
        persona_map: Dictionary mapping write_id to persona_id

    Returns:
        Tuple of (source_text, gold_summary, model_summary, persona_id, trace_info)
    """
    fields = cfg.get('fields', {})

    source_text = get_field(rec, fields.get('source_text', 'document_content'), '')
    gold_summary = get_field(rec, fields.get('gold_summary', 'expected_summary'), '')
    model_summary = get_field(rec, fields.get('model_summary', 'agented_summary'), '')

    write_id = get_field(rec, fields.get('write_id', 'write_id'), '')
    persona_id = persona_map.get(write_id)

    # Extract trace information
    trace_info = {
        'write_id': write_id,
        'uid': get_field(rec, fields.get('uid', 'uid'), ''),
        'document_title': get_field(rec, fields.get('doc_title', 'document_title'), ''),
        'link': get_field(rec, fields.get('link', 'link'), ''),
        'author': get_field(rec, fields.get('author', 'metadata.author'), ''),
        'sector': get_field(rec, fields.get('sector', 'metadata.sector'), ''),
        'report_date': get_field(rec, fields.get('report_date', 'metadata.date'), ''),
        'export_timestamp': get_field(rec, fields.get('export_timestamp', 'export_timestamp'), ''),
        'notes': get_field(rec, fields.get('notes', 'notes'), [])
    }

    return source_text, gold_summary, model_summary, persona_id, trace_info
