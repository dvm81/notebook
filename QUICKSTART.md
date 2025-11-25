# Quick Start Guide

## Installation (5 minutes)

```bash
# 1. Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Download NLTK data
python -c "import nltk; nltk.download('punkt'); nltk.download('punkt_tab')"
```

## Test with Sample Data

The project includes sample data for testing. Choose your approach:

### Option 1: Interactive Notebook (Recommended for Learning)

```bash
# Launch Jupyter notebook
jupyter notebook evaluation_demo.ipynb

# Follow the step-by-step walkthrough
# - See examples of each metric
# - Understand what scores mean
# - Visualize results
```

### Option 2: Command Line (Fast)

```bash
# Run the structure test first
python test_structure.py

# Run evaluation on sample data
python -m src.eval_runner

# Generate report
python -m src.report

# View the report
cat outputs/report.md
```

## Use Your Own Data

### Step 1: Prepare Your Data Files

#### 1.1 Create `data/input.jsonl`

Each line should be a JSON object:

```json
{
  "link": "https://example.com/article1",
  "document_title": "Your Article Title",
  "document_content": "Full source text here...",
  "metadata": {
    "author": "Author Name",
    "sector": "Technology",
    "date": "2024-01-15"
  },
  "uid": "unique-id-1",
  "write_id": "write-001",
  "notes": [],
  "expected_summary": "Reference/gold summary...",
  "agented_summary": "Model-generated summary to evaluate...",
  "export_timestamp": "2024-01-20T10:00:00Z"
}
```

#### 1.2 Create `data/persona_assignments.csv`

Map each summary to a persona:

```csv
write_id,persona_id
write-001,formal_analyst
write-002,casual_blogger
write-003,formal_analyst
```

#### 1.3 Create Persona Corpora

Create text files in `data/personas/` with 3-10 writing samples per persona:

**data/personas/formal_analyst.txt:**
```
Sample 1: The quarterly results demonstrate strong performance...

Sample 2: Analysis of market trends indicates...

Sample 3: Financial metrics reveal significant growth...
```

**data/personas/casual_blogger.txt:**
```
Sample 1: Wow, this quarter was amazing! Revenue is up...

Sample 2: Here's the cool thing about these trends...

Sample 3: Let me break down what's happening here...
```

### Step 2: Update Configuration

Edit `config.yaml` if needed to match your:
- Field names in JSON
- Persona file names
- Model preferences (BERTScore, BLEURT checkpoints)

### Step 3: Run Evaluation

```bash
# Run evaluation
python -m src.eval_runner --config config.yaml --data data/input.jsonl

# Generate report
python -m src.report

# Check outputs
ls outputs/
# You'll see:
# - per_item_metrics.csv (detailed metrics for each summary)
# - corpus_aggregates.json (aggregate statistics)
# - persona_centroids.json (cached stylometric profiles)
# - report.md (human-readable report)
```

## Understanding the Output

### per_item_metrics.csv

Contains all metrics for each evaluated summary:

| Column | Description |
|--------|-------------|
| `write_id`, `uid` | Identifiers |
| `persona_id` | Assigned persona |
| `rouge1_f`, `rouge2_f`, `rougeLsum_f` | ROUGE F1 scores |
| `rouge1_r`, `rougeLsum_r` | ROUGE recall scores |
| `bertscore_f1` | BERTScore F1 |
| `bleurt` | BLEURT score |
| `content_quality` | Composite content score (0-1) |
| `style_similarity` | Stylometric similarity to persona (0-1) |
| `compression_ratio` | Summary length / source length |

### corpus_aggregates.json

Statistics across all summaries:
- Overall means, medians, std devs
- Per-persona breakdowns
- Useful for comparing personas

### report.md

Human-readable markdown with:
- Summary tables
- Top/bottom performers
- Per-persona analysis

## Troubleshooting

### "Package not installed" errors

Make sure you activated the virtual environment:
```bash
source .venv/bin/activate
```

### BLEURT installation fails

BLEURT requires TensorFlow and can be tricky. Options:
1. Install TensorFlow first: `pip install tensorflow>=2.0.0`
2. Disable BLEURT in config.yaml: `use_bleurt: false`

### Out of memory with BERTScore

For large datasets:
1. Use smaller model in config: `bertscore_model: "roberta-base"`
2. Or disable: `use_bertscore: false`

### "No such file or directory" errors

Check your paths:
```bash
# Verify data files exist
ls data/input.jsonl
ls data/persona_assignments.csv
ls data/personas/

# Verify you're in the right directory
pwd  # Should end with /rogue
```

## Tips for Best Results

### Writing Good Persona Samples

- Include 5-10 samples per persona
- Make samples diverse but consistent in style
- Each sample should be 2-5 sentences
- Separate samples with blank lines

### Choosing Metrics

**For content accuracy focus:**
- Enable ROUGE, BERTScore, BLEURT
- Use `content_quality` as main metric

**For style matching focus:**
- Ensure good persona samples
- Check `style_similarity` scores
- Review per-persona breakdowns

### Interpreting Scores

**Content Quality (0-1):**
- 0.7+: Excellent summary
- 0.5-0.7: Good summary
- 0.3-0.5: Fair, needs improvement
- <0.3: Poor quality

**Style Similarity (0-1):**
- 0.8+: Excellent style match
- 0.6-0.8: Good style match
- 0.4-0.6: Moderate style match
- <0.4: Poor style match

## Next Steps

1. Read the full [README.md](README.md) for details
2. Review [claude.md](claude.md) for the complete specification
3. Customize `config.yaml` for your use case
4. Experiment with different metrics and personas

## Getting Help

If you encounter issues:
1. Run `python test_structure.py` to verify setup
2. Check that all data files are properly formatted
3. Review error messages carefully
4. Try running with sample data first to isolate the issue
