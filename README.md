# Summary Evaluation System

Simple evaluation system for financial/business summaries. Works directly with individual JSON files - no configuration needed.

## Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt
python -c "import nltk; nltk.download('punkt'); nltk.download('punkt_tab')"

# 2. Add your JSON files to data/
# Each file should contain one article with generated summary

# 3. Run evaluation
python -m src.eval_runner

# 4. Check results
cat outputs/per_item_metrics.csv
```

## Data Format

Put individual JSON files in the `data/` directory. Each file should have:

```json
{
  "link": "https://...",
  "document_title": "Article Title",
  "document_content": "Full article text...",
  "metadata": {
    "author": "Analyst Name",
    "sector": "Technology",
    "region": "North America",
    "date": "2025-11-24",
    "wire_id": "unique_id"
  },
  "expected_summary": "Reference summary...",
  "generated_summary": "AI-generated summary to evaluate...",
  "prompt_type": "Morning Summary Stock",
  "model_used": "gpt-4o",
  "export_timestamp": "2025-11-24T16:23:40.119022"
}
```

## What It Evaluates

### Content Quality
- **ROUGE scores** (1, 2, L) - word/phrase overlap with reference
- **BERTScore** - semantic similarity using roberta-large
- **Compression ratio** - summary length vs source

### Style Fidelity
- **10 stylometric features** - writing style analysis
- **Persona matching** - similarity to reference writing styles
- Automatically infers persona from:
  - `prompt_type` (e.g., "Research Note" → formal_analyst)
  - `author` role (e.g., "PhD, Economist" → formal_analyst)
  - Default: journalist style

### Personas

Three built-in writing styles:
- **formal_analyst** - Analytical, data-driven, formal language
- **journalist** - Clear, concise, news-style reporting
- **enthusiast** - Energetic, engaging, conversational

Add samples in `data/personas/*.txt` to customize.

## Outputs

After running evaluation:

```
outputs/
├── per_item_metrics.csv      # Detailed metrics for each summary
├── corpus_aggregates.json    # Statistics by persona, sector, model
└── persona_centroids.json    # Cached style profiles
```

### Per-Item Metrics CSV

Columns include:
- Identifiers: file, document_title, author, sector, date, wire_id
- Model info: prompt_type, model_used, persona
- ROUGE: rouge1_f, rouge2_f, rougeLsum_f (F1 scores)
- BERTScore: bertscore_f1
- Style: style_similarity
- Composite: content_quality (weighted ROUGE + BERTScore)
- **Overall: overall_quality (70% content + 30% style)**

### Aggregates JSON

Statistics grouped by:
- Overall (mean, median, std, min, max)
- By persona
- By sector
- By model

## Command Line Options

```bash
# Basic usage
python -m src.eval_runner

# Specify data directory
python -m src.eval_runner --data-dir /path/to/json/files

# Disable BERTScore (faster)
python -m src.eval_runner --no-bertscore

# Change BERTScore model
python -m src.eval_runner --bertscore-model distilbert-base-uncased

# Enable BLEURT (requires setup)
python -m src.eval_runner --use-bleurt
```

## Example Results

```
EVALUATION SUMMARY
==================
Total items evaluated: 9

Overall Metrics (mean):
  ROUGE-Lsum F1:     0.5469
  BERTScore F1:      0.4882
  Style Similarity:  0.8484
  Content Quality:   0.5152
  Overall Quality:   0.6152
                     (70% content + 30% style)

By Persona:
  formal_analyst:  9 items, overall=0.615, content=0.515, style=0.848
```

## How It Works

1. **Loads JSON files** from `data/` directory
2. **Infers persona** from metadata (prompt_type, author)
3. **Calculates metrics**:
   - ROUGE: n-gram overlap
   - BERTScore: semantic similarity
   - Style: feature extraction + Jensen-Shannon divergence
4. **Saves results** to CSV and JSON

## Project Structure

```
rogue/
├── data/                      # Your JSON files go here
│   ├── article1.json
│   ├── article2.json
│   └── personas/              # Style reference samples
│       ├── formal_analyst.txt
│       ├── journalist.txt
│       └── enthusiast.txt
├── src/
│   ├── io_utils.py           # Load JSON files
│   ├── content_metrics.py    # ROUGE, BERTScore
│   ├── style_features.py     # Stylometric analysis
│   ├── text_utils.py         # Text processing
│   └── eval_runner.py        # Main evaluation
├── outputs/                   # Results (auto-generated)
└── requirements.txt
```

## Customization

### Add Your Own Persona

1. Create `data/personas/your_persona.txt`
2. Add 5-10 writing samples (separated by blank lines)
3. Update persona inference in `src/io_utils.py:infer_persona()`

### Adjust Metrics

Edit `src/eval_runner.py` main():
- Disable BERTScore: `--no-bertscore`
- Change model: `--bertscore-model distilbert-base-uncased`
- Enable BLEURT: `--use-bleurt` (requires download)

## Dependencies

Core:
- rouge-score - ROUGE metrics
- bert-score - Semantic similarity
- transformers, torch - Model backends
- pandas, numpy - Data processing
- nltk, scipy - Text analysis
- huggingface_hub - Model downloads

Optional:
- bleurt - Human-correlated metric (large download)
- matplotlib - Visualization

## Local Model Setup (Optional)

Speed up evaluation by downloading RoBERTa-large once to local disk:

```bash
# Download model files (~1.4GB) to roberta-large/ directory
python setup_roberta.py

# Verify it works
python test_local_roberta.py

# Run evaluation (will use local model automatically)
python -m src.eval_runner
```

See [ROBERTA_LOCAL_SETUP.md](ROBERTA_LOCAL_SETUP.md) for details.

## Tips

### Good Summary Metrics
- **Overall Quality > 0.6**: Good overall summary (combined metric)
- **Overall Quality > 0.7**: Excellent overall summary
- ROUGE-Lsum F1 > 0.6: Good content coverage
- BERTScore F1 > 0.85: Strong semantic match
- Style similarity > 0.7: Good persona match
- Content quality > 0.6: Good content (weighted ROUGE + BERTScore)

### Troubleshooting

**No JSON files found:**
- Check files are in `data/` directory
- Ensure files end with `.json`
- Verify JSON is valid

**Persona mismatch:**
- Check `prompt_type` and `author` fields
- Update `infer_persona()` logic in `src/io_utils.py`
- Add more samples to `data/personas/`

**Slow evaluation:**
- Use smaller BERTScore model: `--bertscore-model distilbert-base-uncased`
- Disable BERTScore: `--no-bertscore`
- Process fewer files

## License

MIT
