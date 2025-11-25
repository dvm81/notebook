# Persona Summarization Evaluation System

A comprehensive evaluation framework for assessing persona-based summarization systems. This tool evaluates summaries on two key dimensions:

1. **Content Quality**: ROUGE, BERTScore, and BLEURT metrics
2. **Style/Persona Fidelity**: Stylometric similarity to persona writing styles

## Features

- **Content Metrics**:
  - ROUGE-1, ROUGE-2, ROUGE-Lsum (recall and F1)
  - BERTScore F1 (with baseline rescaling)
  - BLEURT scores
  - Compression ratio analysis

- **Style Metrics**:
  - Stylometric feature extraction (function words, sentence length, punctuation patterns, etc.)
  - Persona-specific centroid matching
  - Jensen-Shannon divergence-based similarity

- **Outputs**:
  - Per-item metrics CSV
  - Corpus-level aggregate statistics (JSON)
  - Markdown report with analysis and rankings

## Installation

```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Download NLTK data
python -c "import nltk; nltk.download('punkt'); nltk.download('punkt_tab')"
```

## Data Format

### Input JSONL (`data/input.jsonl`)

Each line should be a JSON object with the following schema:

```json
{
  "link": "https://...",
  "document_title": "string",
  "document_content": "long source text",
  "metadata": {
    "author": "string",
    "sector": "string",
    "date": "YYYY-MM-DD"
  },
  "uid": "string",
  "write_id": "string",
  "notes": [],
  "expected_summary": "gold/reference summary",
  "agented_summary": "model-generated summary to evaluate",
  "export_timestamp": "ISO8601"
}
```

### Persona Assignments (`data/persona_assignments.csv`)

CSV file mapping summaries to personas:

```csv
write_id,persona_id
write-001,alex
write-002,priya
```

### Persona Corpora (`data/personas/*.txt`)

Text files containing 3-10 writing samples for each persona, separated by double newlines:

```
Sample 1 text here...

Sample 2 text here...

Sample 3 text here...
```

## Configuration

Edit `config.yaml` to customize:

- Field mappings for your JSON schema
- Paths to persona files
- Which metrics to enable/disable
- Model checkpoints (BERTScore, BLEURT)

## Usage

### Interactive Notebook (Recommended for Learning)

Explore the evaluation metrics interactively with detailed explanations:

```bash
jupyter notebook evaluation_demo.ipynb
```

See [NOTEBOOK_GUIDE.md](NOTEBOOK_GUIDE.md) for details.

### Run Complete Evaluation (Command Line)

```bash
python -m src.eval_runner --config config.yaml --data data/input.jsonl --out outputs/per_item_metrics.csv
```

This will:
1. Load configuration and persona assignments
2. Build persona stylometric centroids
3. Process each record and calculate all metrics
4. Save per-item metrics to CSV
5. Generate aggregate statistics (JSON)
6. Print summary to console

### Generate Report

```bash
python -m src.report --metrics outputs/per_item_metrics.csv --out outputs/report.md
```

This creates a markdown report with:
- Overall statistics tables
- Per-persona breakdowns
- Top/bottom performing summaries
- Summary insights

## Output Files

After running the evaluation, you'll find:

- `outputs/per_item_metrics.csv`: All metrics for each evaluated summary
- `outputs/corpus_aggregates.json`: Mean, median, std dev for each metric
- `outputs/persona_centroids.json`: Cached stylometric centroids
- `outputs/report.md`: Human-readable markdown report

## Metrics Explanation

### Content Quality Score

Composite score calculated as:
```
content_quality = 0.4 * rougeLsum_f + 0.3 * bertscore_f1 + 0.3 * bleurt_normalized
```

### Style Similarity

Measures how closely the generated summary matches the target persona's writing style using:
- Function word frequencies
- Average sentence length
- Type-token ratio (vocabulary diversity)
- Punctuation patterns
- Pronoun usage
- Flesch-Kincaid grade level
- Average word length

Similarity is computed as `1 - JensenShannon_divergence` between feature distributions.

## Example Workflow

```bash
# 1. Set up environment
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python -c "import nltk; nltk.download('punkt'); nltk.download('punkt_tab')"

# 2. Prepare your data
# - Create data/input.jsonl with your summaries
# - Create data/persona_assignments.csv
# - Add persona writing samples to data/personas/

# 3. Run evaluation
python -m src.eval_runner --config config.yaml --data data/input.jsonl

# 4. Generate report
python -m src.report

# 5. View results
cat outputs/report.md
```

## Sample Data

The repository includes sample data for testing:
- 3 example summaries in `data/input.jsonl`
- 2 personas (alex, priya) with writing samples
- Persona assignments mapping summaries to personas

Run the evaluation on sample data to verify installation:

```bash
python -m src.eval_runner
python -m src.report
```

## Troubleshooting

### BLEURT Installation Issues

BLEURT requires TensorFlow and can be tricky to install. If you encounter issues:

1. Try installing TensorFlow separately first:
   ```bash
   pip install tensorflow>=2.0.0
   ```

2. If BLEURT still fails, you can disable it in `config.yaml`:
   ```yaml
   content:
     use_bleurt: false
   ```

### Memory Issues with BERTScore

For large datasets, BERTScore can consume significant memory. Consider:

- Processing in smaller batches
- Using a smaller model: change `roberta-large` to `roberta-base` in config.yaml
- Disabling if necessary: set `use_bertscore: false`

## License

MIT

## Citation

If you use this evaluation framework in your research, please cite:

```bibtex
@software{persona_eval_2024,
  title={Persona Summarization Evaluation System},
  year={2024},
  author={Your Name},
  version={1.0.0}
}
```
