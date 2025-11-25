"""
Report generation from evaluation metrics.
"""

import argparse
import json
import pandas as pd
from pathlib import Path
from typing import Dict, Any


def format_metric_table(metrics: Dict[str, Dict[str, float]], title: str) -> str:
    """
    Format metrics as a markdown table.

    Args:
        metrics: Dictionary of metric_name -> {mean, median, std, ...}
        title: Table title

    Returns:
        Markdown formatted table string
    """
    if not metrics:
        return f"### {title}\n\nNo data available.\n\n"

    lines = [f"### {title}\n"]
    lines.append("| Metric | Mean | Median | Std Dev | Min | Max | Count |")
    lines.append("|--------|------|--------|---------|-----|-----|-------|")

    for metric_name, stats in metrics.items():
        mean = stats.get('mean', 0)
        median = stats.get('median', 0)
        std = stats.get('std', 0)
        min_val = stats.get('min', 0)
        max_val = stats.get('max', 0)
        count = stats.get('count', 0)

        lines.append(
            f"| {metric_name} | {mean:.4f} | {median:.4f} | "
            f"{std:.4f} | {min_val:.4f} | {max_val:.4f} | {count} |"
        )

    lines.append("\n")
    return "\n".join(lines)


def generate_report(metrics_csv: str, aggregates_json: str, output_path: str):
    """
    Generate markdown report from evaluation results.

    Args:
        metrics_csv: Path to per_item_metrics.csv
        aggregates_json: Path to corpus_aggregates.json
        output_path: Path to output report.md
    """
    # Load data
    df = pd.read_csv(metrics_csv)
    with open(aggregates_json, 'r') as f:
        aggregates = json.load(f)

    # Start building report
    lines = []
    lines.append("# Persona Summarization Evaluation Report\n")
    lines.append(f"**Total Items Evaluated:** {len(df)}\n")

    # Overall statistics
    lines.append("## Overall Statistics\n")

    overall = aggregates.get('overall', {})

    # Content metrics
    content_metrics = {
        k: v for k, v in overall.items()
        if k in ['rouge1_f', 'rouge2_f', 'rougeLsum_f', 'rouge1_r', 'rougeLsum_r',
                 'bertscore_f1', 'bleurt', 'content_quality', 'compression_ratio']
    }
    lines.append(format_metric_table(content_metrics, "Content Quality Metrics"))

    # Style metrics
    style_metrics = {
        k: v for k, v in overall.items()
        if k in ['style_similarity', 'style_fidelity']
    }
    lines.append(format_metric_table(style_metrics, "Style Fidelity Metrics"))

    # Per-persona breakdown
    by_persona = aggregates.get('by_persona', {})
    if by_persona:
        lines.append("## Per-Persona Results\n")

        for persona_id, persona_metrics in by_persona.items():
            lines.append(f"### Persona: {persona_id}\n")

            # Filter content metrics
            persona_content = {
                k: v for k, v in persona_metrics.items()
                if k in ['rouge1_f', 'rouge2_f', 'rougeLsum_f', 'bertscore_f1',
                         'bleurt', 'content_quality']
            }

            # Filter style metrics
            persona_style = {
                k: v for k, v in persona_metrics.items()
                if k in ['style_similarity', 'style_fidelity']
            }

            if persona_content:
                lines.append("#### Content Metrics\n")
                lines.append("| Metric | Mean | Median | Std Dev | Count |")
                lines.append("|--------|------|--------|---------|-------|")
                for metric_name, stats in persona_content.items():
                    mean = stats.get('mean', 0)
                    median = stats.get('median', 0)
                    std = stats.get('std', 0)
                    count = stats.get('count', 0)
                    lines.append(f"| {metric_name} | {mean:.4f} | {median:.4f} | {std:.4f} | {count} |")
                lines.append("\n")

            if persona_style:
                lines.append("#### Style Metrics\n")
                lines.append("| Metric | Mean | Median | Std Dev | Count |")
                lines.append("|--------|------|--------|---------|-------|")
                for metric_name, stats in persona_style.items():
                    mean = stats.get('mean', 0)
                    median = stats.get('median', 0)
                    std = stats.get('std', 0)
                    count = stats.get('count', 0)
                    lines.append(f"| {metric_name} | {mean:.4f} | {median:.4f} | {std:.4f} | {count} |")
                lines.append("\n")

    # Top and bottom performers
    lines.append("## Performance Analysis\n")

    # Top 5 by content quality
    if 'content_quality' in df.columns:
        top_content = df.nlargest(5, 'content_quality')[
            ['write_id', 'document_title', 'content_quality', 'rougeLsum_f', 'bertscore_f1']
        ]
        lines.append("### Top 5 Summaries by Content Quality\n")
        lines.append(top_content.to_markdown(index=False))
        lines.append("\n")

        # Bottom 5 by content quality
        bottom_content = df.nsmallest(5, 'content_quality')[
            ['write_id', 'document_title', 'content_quality', 'rougeLsum_f', 'bertscore_f1']
        ]
        lines.append("### Bottom 5 Summaries by Content Quality\n")
        lines.append(bottom_content.to_markdown(index=False))
        lines.append("\n")

    # Style similarity analysis
    if 'style_similarity' in df.columns:
        df_with_style = df[df['style_similarity'].notna()]
        if len(df_with_style) > 0:
            top_style = df_with_style.nlargest(5, 'style_similarity')[
                ['write_id', 'document_title', 'persona_id', 'style_similarity']
            ]
            lines.append("### Top 5 Summaries by Style Similarity\n")
            lines.append(top_style.to_markdown(index=False))
            lines.append("\n")

            bottom_style = df_with_style.nsmallest(5, 'style_similarity')[
                ['write_id', 'document_title', 'persona_id', 'style_similarity']
            ]
            lines.append("### Bottom 5 Summaries by Style Similarity\n")
            lines.append(bottom_style.to_markdown(index=False))
            lines.append("\n")

    # Summary statistics
    lines.append("## Summary\n")
    lines.append(f"- **Items with style evaluation:** {df['style_skipped'].eq(0).sum()} / {len(df)}\n")
    lines.append(f"- **Items skipped for style:** {df['style_skipped'].eq(1).sum()}\n")

    if 'content_quality' in df.columns:
        avg_quality = df['content_quality'].mean()
        lines.append(f"- **Average content quality:** {avg_quality:.4f}\n")

    if 'style_similarity' in df.columns:
        avg_style = df['style_similarity'].mean()
        lines.append(f"- **Average style similarity:** {avg_style:.4f}\n")

    # Write report
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, 'w') as f:
        f.write('\n'.join(lines))

    print(f"Report generated: {output_path}")


def main():
    """Main report generation."""
    parser = argparse.ArgumentParser(description='Generate evaluation report')
    parser.add_argument('--metrics', default='outputs/per_item_metrics.csv',
                        help='Path to per-item metrics CSV')
    parser.add_argument('--aggregates', default='outputs/corpus_aggregates.json',
                        help='Path to aggregates JSON')
    parser.add_argument('--out', default='outputs/report.md',
                        help='Path to output report')
    args = parser.parse_args()

    generate_report(args.metrics, args.aggregates, args.out)


if __name__ == '__main__':
    main()
