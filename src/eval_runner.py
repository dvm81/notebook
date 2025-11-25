"""
Main evaluation runner that orchestrates the entire pipeline.
"""

import argparse
import json
import yaml
import pandas as pd
from pathlib import Path
from typing import Dict, Any, List
from src.io_utils import load_jsonl, load_persona_assignments, record_to_example
from src.content_metrics import ContentMetricsCalculator
from src.style_features import StyleAnalyzer


def load_config(config_path: str) -> Dict[str, Any]:
    """
    Load YAML configuration file.

    Args:
        config_path: Path to config.yaml

    Returns:
        Configuration dictionary
    """
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)


def evaluate_single_item(
    source_text: str,
    gold_summary: str,
    model_summary: str,
    persona_id: str,
    trace_info: Dict[str, Any],
    content_calculator: ContentMetricsCalculator,
    style_analyzer: StyleAnalyzer
) -> Dict[str, Any]:
    """
    Evaluate a single summary item.

    Args:
        source_text: Source document
        gold_summary: Gold/reference summary
        model_summary: Model-generated summary
        persona_id: Persona ID (can be None)
        trace_info: Traceability information
        content_calculator: Content metrics calculator
        style_analyzer: Style analyzer

    Returns:
        Dictionary with all metrics and trace info
    """
    # Calculate content metrics
    content_metrics = content_calculator.calculate_all_metrics(
        source_text, gold_summary, model_summary
    )

    # Calculate style metrics
    style_metrics = style_analyzer.calculate_style_metrics(model_summary, persona_id)

    # Combine all metrics
    result = {
        **trace_info,
        'persona_id': persona_id,
        **content_metrics,
        **style_metrics
    }

    return result


def calculate_aggregates(results: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Calculate aggregate statistics across all results.

    Args:
        results: List of per-item metric dictionaries

    Returns:
        Dictionary with aggregate statistics
    """
    df = pd.DataFrame(results)

    # Metrics to aggregate
    content_metrics = [
        'rouge1_f', 'rouge2_f', 'rougeLsum_f',
        'rouge1_r', 'rougeLsum_r',
        'bertscore_f1', 'bleurt',
        'content_quality', 'compression_ratio'
    ]

    style_metrics = ['style_similarity', 'style_fidelity']

    aggregates = {
        'overall': {},
        'by_persona': {}
    }

    # Overall aggregates
    for metric in content_metrics:
        if metric in df.columns:
            values = df[metric].dropna()
            if len(values) > 0:
                aggregates['overall'][metric] = {
                    'mean': float(values.mean()),
                    'median': float(values.median()),
                    'std': float(values.std()),
                    'min': float(values.min()),
                    'max': float(values.max()),
                    'count': int(len(values))
                }

    for metric in style_metrics:
        if metric in df.columns:
            values = df[metric].dropna()
            if len(values) > 0:
                aggregates['overall'][metric] = {
                    'mean': float(values.mean()),
                    'median': float(values.median()),
                    'std': float(values.std()),
                    'min': float(values.min()),
                    'max': float(values.max()),
                    'count': int(len(values))
                }

    # Per-persona aggregates
    if 'persona_id' in df.columns:
        for persona_id in df['persona_id'].dropna().unique():
            persona_df = df[df['persona_id'] == persona_id]
            aggregates['by_persona'][persona_id] = {}

            for metric in content_metrics + style_metrics:
                if metric in persona_df.columns:
                    values = persona_df[metric].dropna()
                    if len(values) > 0:
                        aggregates['by_persona'][persona_id][metric] = {
                            'mean': float(values.mean()),
                            'median': float(values.median()),
                            'std': float(values.std()),
                            'count': int(len(values))
                        }

    return aggregates


def main():
    """Main evaluation pipeline."""
    parser = argparse.ArgumentParser(description='Evaluate persona summaries')
    parser.add_argument('--config', default='config.yaml', help='Path to config.yaml')
    parser.add_argument('--data', default='data/input.jsonl', help='Path to input JSONL')
    parser.add_argument('--out', default='outputs/per_item_metrics.csv',
                        help='Path to output CSV')
    args = parser.parse_args()

    # Load configuration
    print(f"Loading config from {args.config}...")
    config = load_config(args.config)

    # Load persona assignments
    persona_csv_path = config.get('persona_assignments_csv', 'data/persona_assignments.csv')
    print(f"Loading persona assignments from {persona_csv_path}...")
    persona_map = load_persona_assignments(persona_csv_path)
    print(f"Loaded {len(persona_map)} persona assignments")

    # Initialize calculators
    print("Initializing content metrics calculator...")
    content_calculator = ContentMetricsCalculator(config)

    print("Initializing style analyzer...")
    style_analyzer = StyleAnalyzer(config)

    # Build persona centroids
    print("Building persona centroids...")
    style_analyzer.build_persona_centroids()
    print(f"Built centroids for {len(style_analyzer.centroids)} personas")

    # Process each record
    print(f"Processing records from {args.data}...")
    results = []
    for i, record in enumerate(load_jsonl(args.data), 1):
        if i % 10 == 0:
            print(f"  Processed {i} records...")

        # Extract fields
        source_text, gold_summary, model_summary, persona_id, trace_info = \
            record_to_example(record, config, persona_map)

        # Evaluate
        item_result = evaluate_single_item(
            source_text, gold_summary, model_summary, persona_id,
            trace_info, content_calculator, style_analyzer
        )

        results.append(item_result)

    print(f"Processed {len(results)} total records")

    # Save per-item metrics to CSV
    print(f"Saving per-item metrics to {args.out}...")
    output_path = Path(args.out)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    df = pd.DataFrame(results)
    df.to_csv(output_path, index=False)
    print(f"Saved {len(df)} rows to {output_path}")

    # Calculate and save aggregates
    print("Calculating aggregate statistics...")
    aggregates = calculate_aggregates(results)

    aggregates_path = output_path.parent / 'corpus_aggregates.json'
    with open(aggregates_path, 'w') as f:
        json.dump(aggregates, f, indent=2)
    print(f"Saved aggregates to {aggregates_path}")

    # Print summary
    print("\n" + "=" * 60)
    print("EVALUATION SUMMARY")
    print("=" * 60)
    print(f"Total items evaluated: {len(results)}")
    print(f"\nOverall Content Quality (mean): {aggregates['overall'].get('content_quality', {}).get('mean', 'N/A')}")
    print(f"Overall ROUGE-Lsum F1 (mean): {aggregates['overall'].get('rougeLsum_f', {}).get('mean', 'N/A')}")
    print(f"Overall BERTScore F1 (mean): {aggregates['overall'].get('bertscore_f1', {}).get('mean', 'N/A')}")
    print(f"Overall Style Similarity (mean): {aggregates['overall'].get('style_similarity', {}).get('mean', 'N/A')}")

    if aggregates['by_persona']:
        print(f"\nPer-persona results:")
        for persona_id, metrics in aggregates['by_persona'].items():
            content_qual = metrics.get('content_quality', {}).get('mean', 'N/A')
            style_sim = metrics.get('style_similarity', {}).get('mean', 'N/A')
            print(f"  {persona_id}: content_quality={content_qual:.4f}, style_similarity={style_sim:.4f}"
                  if isinstance(content_qual, float) and isinstance(style_sim, float)
                  else f"  {persona_id}: metrics available")

    print("=" * 60)
    print("\nDone!")


if __name__ == '__main__':
    main()
