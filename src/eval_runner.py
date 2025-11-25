"""
Main evaluation runner - works directly with JSON files (no YAML config needed).
"""

import argparse
import json
import pandas as pd
from pathlib import Path
from typing import Dict, Any, List

from src.io_utils import load_all_records
from src.content_metrics import ContentMetricsCalculator
from src.style_features import StyleAnalyzer
from src.text_utils import count_tokens


def evaluate_single_item(
    record: Dict[str, Any],
    content_calc: ContentMetricsCalculator,
    style_analyzer: StyleAnalyzer
) -> Dict[str, Any]:
    """
    Evaluate a single record.

    Args:
        record: Processed record with all fields
        content_calc: Content metrics calculator
        style_analyzer: Style analyzer

    Returns:
        Dictionary with all metrics
    """
    source_text = record['document_content']
    reference = record['expected_summary']
    generated = record['generated_summary']
    persona = record['persona']

    # Calculate content metrics
    content_metrics = content_calc.calculate_all_metrics(
        source_text=source_text,
        reference=reference,
        hypothesis=generated
    )

    # Calculate style similarity
    style_similarity = style_analyzer.calculate_style_similarity(generated, persona)

    # Calculate overall quality (combined metric)
    # Weighted combination: 70% content quality, 30% style fidelity
    content_quality = content_metrics.get('content_quality', 0.0)
    style_score = style_similarity if style_similarity is not None else 0.0
    overall_quality = (0.7 * content_quality) + (0.3 * style_score)

    # Combine all metrics
    result = {
        # Identifiers
        'file': record['_source_file'],
        'document_title': record['document_title'][:80],
        'link': record['link'],
        'author': record['author'],
        'sector': record['sector'],
        'region': record['region'],
        'date': record['date'],
        'wire_id': record['wire_id'],
        'prompt_type': record['prompt_type'],
        'model_used': record['model_used'],
        'persona': persona,

        # Content metrics
        **content_metrics,

        # Style metrics
        'style_similarity': style_similarity,

        # Combined overall quality
        'overall_quality': overall_quality,
    }

    return result


def calculate_aggregates(results: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Calculate aggregate statistics.

    Args:
        results: List of evaluation results

    Returns:
        Dictionary with aggregate statistics
    """
    df = pd.DataFrame(results)

    # Overall statistics
    numeric_cols = df.select_dtypes(include=['float64', 'int64']).columns
    overall_stats = df[numeric_cols].agg(['mean', 'median', 'std', 'min', 'max']).to_dict()

    # Per-persona statistics
    persona_stats = {}
    for persona in df['persona'].unique():
        persona_df = df[df['persona'] == persona]
        persona_stats[persona] = persona_df[numeric_cols].agg(['mean', 'median', 'std', 'count']).to_dict()

    # Per-sector statistics
    sector_stats = {}
    for sector in df['sector'].unique():
        if sector:  # Skip empty sectors
            sector_df = df[df['sector'] == sector]
            sector_stats[sector] = sector_df[numeric_cols].agg(['mean', 'count']).to_dict()

    # Per-model statistics
    model_stats = {}
    for model in df['model_used'].unique():
        if model:  # Skip empty models
            model_df = df[df['model_used'] == model]
            model_stats[model] = model_df[numeric_cols].agg(['mean', 'count']).to_dict()

    return {
        'overall': overall_stats,
        'by_persona': persona_stats,
        'by_sector': sector_stats,
        'by_model': model_stats,
        'total_items': len(results)
    }


def main():
    parser = argparse.ArgumentParser(
        description="Evaluate summaries from JSON files"
    )
    parser.add_argument(
        '--data-dir',
        type=str,
        default='data',
        help='Directory containing JSON files (default: data)'
    )
    parser.add_argument(
        '--output-dir',
        type=str,
        default='outputs',
        help='Output directory for results (default: outputs)'
    )
    parser.add_argument(
        '--use-bertscore',
        action='store_true',
        default=True,
        help='Use BERTScore (default: True)'
    )
    parser.add_argument(
        '--bertscore-model',
        type=str,
        default='roberta-large',
        help='BERTScore model (default: roberta-large)'
    )
    parser.add_argument(
        '--use-bleurt',
        action='store_true',
        default=False,
        help='Use BLEURT (default: False, requires setup)'
    )

    args = parser.parse_args()

    # Create output directory
    output_dir = Path(args.output_dir)
    output_dir.mkdir(exist_ok=True)

    print("="*80)
    print("PERSONA SUMMARIZATION EVALUATION")
    print("="*80)
    print()

    # Load all records
    print(f"Loading JSON files from {args.data_dir}...")
    records = load_all_records(args.data_dir)
    print(f"✓ Loaded {len(records)} records")
    print()

    # Show persona distribution
    persona_counts = {}
    for r in records:
        p = r['persona']
        persona_counts[p] = persona_counts.get(p, 0) + 1

    print("Persona distribution:")
    for persona, count in sorted(persona_counts.items()):
        print(f"  {persona:20s}: {count:2d} records")
    print()

    # Initialize calculators
    print("Initializing metrics calculators...")

    content_config = {
        'use_rouge': True,
        'use_bertscore': args.use_bertscore,
        'bertscore_model': args.bertscore_model,
        'use_bleurt': args.use_bleurt,
        'bleurt_checkpoint': 'bleurt_checkpoints/BLEURT-20-D3'
    }

    content_calculator = ContentMetricsCalculator({'content': content_config})

    # Set up persona paths
    persona_config = {
        'personas': {
            'formal_analyst': 'data/personas/formal_analyst.txt',
            'journalist': 'data/personas/journalist.txt',
            'enthusiast': 'data/personas/enthusiast.txt'
        }
    }
    style_analyzer = StyleAnalyzer(persona_config)

    # Build persona centroids
    print("Building persona centroids...")
    centroids = style_analyzer.build_persona_centroids()
    print(f"✓ Built centroids for {len(centroids)} personas")
    print()

    # Process each record
    print(f"Evaluating {len(records)} records...")
    print()
    results = []

    for i, record in enumerate(records, 1):
        title = record['document_title'][:50]
        print(f"  [{i}/{len(records)}] {title}...")

        result = evaluate_single_item(record, content_calculator, style_analyzer)
        results.append(result)

    print()
    print("✓ Evaluation complete!")
    print()

    # Save results
    output_csv = output_dir / 'per_item_metrics.csv'
    df = pd.DataFrame(results)
    df.to_csv(output_csv, index=False)
    print(f"✓ Saved per-item metrics to {output_csv}")

    # Calculate and save aggregates
    aggregates = calculate_aggregates(results)
    output_json = output_dir / 'corpus_aggregates.json'
    with open(output_json, 'w') as f:
        json.dump(aggregates, f, indent=2, default=str)
    print(f"✓ Saved aggregate statistics to {output_json}")

    # Print summary
    print()
    print("="*80)
    print("EVALUATION SUMMARY")
    print("="*80)
    print(f"Total items evaluated: {len(results)}")
    print()

    # Overall metrics
    print("Overall Metrics (mean):")
    if 'rougeLsum_f' in df.columns:
        print(f"  ROUGE-Lsum F1:     {df['rougeLsum_f'].mean():.4f}")
    if 'bertscore_f1' in df.columns and df['bertscore_f1'].notna().any():
        print(f"  BERTScore F1:      {df['bertscore_f1'].mean():.4f}")
    if 'bleurt' in df.columns and df['bleurt'].notna().any():
        print(f"  BLEURT:            {df['bleurt'].mean():.4f}")
    if 'style_similarity' in df.columns and df['style_similarity'].notna().any():
        print(f"  Style Similarity:  {df['style_similarity'].mean():.4f}")
    if 'content_quality' in df.columns:
        print(f"  Content Quality:   {df['content_quality'].mean():.4f}")
    if 'overall_quality' in df.columns:
        print(f"  Overall Quality:   {df['overall_quality'].mean():.4f}")
        print(f"                     (70% content + 30% style)")

    print()
    print("By Persona:")
    for persona in sorted(df['persona'].unique()):
        persona_df = df[df['persona'] == persona]
        style_val = persona_df['style_similarity'].mean() if persona_df['style_similarity'].notna().any() else 0.0
        overall_val = persona_df['overall_quality'].mean() if 'overall_quality' in persona_df.columns else 0.0
        print(f"  {persona:20s}: {len(persona_df):2d} items, "
              f"overall={overall_val:.3f}, "
              f"content={persona_df['content_quality'].mean():.3f}, "
              f"style={style_val:.3f}")

    print()
    print("="*80)
    print("Next steps:")
    print(f"  1. Review results in: {output_csv}")
    print(f"  2. Check aggregates in: {output_json}")
    print(f"  3. Generate report: python -m src.report")
    print("="*80)
    print()


if __name__ == '__main__':
    main()
