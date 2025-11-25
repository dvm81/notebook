# Evaluation Demo Notebook Guide

## Overview

`evaluation_demo.ipynb` is an interactive Jupyter notebook that walks through the entire evaluation strategy step-by-step, demonstrating each metric with concrete examples from the test data.

## What's Inside

### 1. **Setup & Data Loading**
- Load test articles and persona assignments
- Inspect sample data
- Understand the data structure

### 2. **ROUGE Metrics (Detailed)**
- **ROUGE-1**: Unigram overlap (word-level matching)
- **ROUGE-2**: Bigram overlap (phrase preservation)
- **ROUGE-L**: Longest common subsequence (structure similarity)
- Compare precision, recall, and F1 scores
- Visualize word-level overlap
- Compare multiple examples

### 3. **BERTScore**
- Semantic similarity using contextual embeddings
- Demonstrate advantage over ROUGE for paraphrasing
- Compare scores on example texts
- Show why BERTScore > ROUGE for synonyms

### 4. **BLEURT**
- Learned metric explanation
- Discussion of human correlation
- Notes on installation and usage

### 5. **Stylometric Features**
- Extract 10 stylometric features
- Show feature values for examples
- Build persona centroids
- Visualize persona characteristics

### 6. **Complete Evaluation**
- Run full evaluation on all 12 articles
- Generate results table
- Calculate summary statistics
- Show per-article scores

### 7. **Persona Comparison**
- Group results by persona
- Compare content quality across personas
- Analyze style fidelity by persona
- Visualizations (box plots, scatter plots)

### 8. **Summary & Insights**
- Key findings summary
- Best/worst performing articles
- Correlations between metrics
- Sector performance analysis
- Actionable recommendations

## How to Use

### Quick Start

```bash
# 1. Install dependencies (including Jupyter)
pip install -r requirements.txt

# 2. Download NLTK data
python -c "import nltk; nltk.download('punkt'); nltk.download('punkt_tab')"

# 3. Start Jupyter
jupyter notebook evaluation_demo.ipynb
```

### Run All Cells

In Jupyter, you can:
- **Cell → Run All** to execute the entire notebook
- Or run cells one-by-one to see each step

### Expected Runtime

- **Without BERTScore/BLEURT**: ~2-3 minutes
- **With BERTScore**: ~5-10 minutes (first run downloads models)
- **With BLEURT**: ~15-20 minutes (requires TensorFlow + large models)

For this demo, BERTScore is optional and BLEURT is skipped for speed.

## What You'll Learn

### Understanding Metrics

#### ROUGE (N-gram Overlap)
```
Reference: "The company reported strong revenue growth"
Generated: "The firm showed strong revenue growth"

ROUGE-1: 0.714 (5 of 7 words match)
ROUGE-2: 0.400 (2 of 5 bigrams match)
```

**Insight**: ROUGE captures word-level similarity but misses synonyms ("company"/"firm")

#### BERTScore (Semantic Similarity)
```
Reference: "The company reported strong revenue growth"
Generated: "The firm showed robust sales increases"

ROUGE-1: 0.143 (almost no word overlap)
BERTScore: 0.85+ (high semantic similarity)
```

**Insight**: BERTScore handles paraphrasing and synonyms

#### Stylometric Similarity
```
formal_analyst: Low exclamations, formal vocabulary, passive voice
enthusiast: High exclamations, superlatives, active voice
journalist: Balanced, neutral, structured

Summary style → Compare to persona centroids → Similarity score
```

**Insight**: Quantifies "writing style" objectively

## Interactive Exploration

### Modify Examples

Try changing examples to explore:

```python
# Use a different article
example = records[5]  # Change index

# Compare different personas
persona_examples = records[0:3]  # First 3

# Filter by sector
tech_articles = [r for r in records if r['metadata']['sector'] == 'Technology']
```

### Add Your Own Analysis

```python
# Add new cells to explore:

# 1. Compression ratio analysis
df_results['compression'].hist(bins=20)

# 2. Token length distributions
df_results.boxplot(column=['src_tokens', 'gen_tokens'])

# 3. Correlation matrix
df_results[['rouge1_f', 'rouge2_f', 'rougeLsum_f', 'style_sim']].corr()
```

## Visualizations Generated

The notebook creates several visualizations:

1. **ROUGE scores by persona** (box plot)
2. **Style similarity by persona** (box plot)
3. **Content quality vs style fidelity** (scatter plot)
4. **Compression ratio by persona** (box plot)

Saved to: `outputs/evaluation_visualization.png`

## Common Use Cases

### 1. Understanding Your Data

Run the notebook to:
- See actual metric values
- Understand score distributions
- Identify outliers
- Compare personas

### 2. Debugging Low Scores

If an article scores poorly:
```python
# Find the article
low_scorer = df_results[df_results['rougeLsum_f'] < 0.5]
print(low_scorer)

# Inspect it
rec = records[3]  # Example
print("Source:", rec['document_content'])
print("Reference:", rec['expected_summary'])
print("Generated:", rec['agented_summary'])
```

### 3. Validating Personas

Check if personas are distinguishable:
```python
# Look at centroid differences
for persona, centroid in centroids.items():
    print(f"{persona}: exclamation_rate={centroid[5]:.4f}")

# If too similar, add more diverse samples
```

### 4. Presenting Results

The notebook outputs:
- Summary tables
- Statistics
- Visualizations
- Interpretations

Perfect for reports and presentations!

## Troubleshooting

### "Module not found" errors

```bash
# Install missing packages
pip install jupyter matplotlib seaborn tabulate
```

### BERTScore is slow

```python
# Use smaller model
model_type='distilbert-base-uncased'  # Instead of roberta-large

# Or skip BERTScore for quick runs
```

### Memory issues

```python
# Process fewer articles
records = records[:5]  # First 5 only

# Use smaller batch sizes
# Or run on CPU only
```

### Kernel crashes

```bash
# Increase memory limit
jupyter notebook --NotebookApp.max_buffer_size=1000000000

# Or restart kernel: Kernel → Restart & Clear Output
```

## Extending the Notebook

### Add New Metrics

```python
# Example: Add BLEU score
from nltk.translate.bleu_score import sentence_bleu

reference_tokens = reference.split()
generated_tokens = generated.split()
bleu = sentence_bleu([reference_tokens], generated_tokens)
```

### Add Custom Visualizations

```python
import matplotlib.pyplot as plt

# Histogram of ROUGE scores
plt.figure(figsize=(10, 6))
plt.hist(df_results['rougeLsum_f'], bins=20, edgecolor='black')
plt.xlabel('ROUGE-Lsum F1')
plt.ylabel('Frequency')
plt.title('Distribution of ROUGE-Lsum Scores')
plt.show()
```

### Export Results

```python
# Save to CSV
df_results.to_csv('outputs/notebook_results.csv', index=False)

# Save to Excel
df_results.to_excel('outputs/notebook_results.xlsx', index=False)

# Create custom report
with open('outputs/custom_report.txt', 'w') as f:
    f.write(f"Average ROUGE: {df_results['rougeLsum_f'].mean():.4f}\n")
    f.write(f"Average Style: {df_results['style_sim'].mean():.4f}\n")
```

## Comparison to Command-Line Evaluation

| Feature | Notebook | CLI (`eval_runner.py`) |
|---------|----------|------------------------|
| **Interactive** | ✓ Yes | ✗ No |
| **Visualizations** | ✓ Built-in | Manual |
| **Step-by-step** | ✓ Detailed | All at once |
| **Speed** | Slower (cell-by-cell) | Faster |
| **Customization** | ✓ Easy | Requires code edits |
| **BERTScore** | Optional (small model) | Full (large model) |
| **BLEURT** | Skipped for speed | Included |
| **Best for** | Learning, exploration | Production, batch |

## Recommended Workflow

1. **First time**: Run the notebook to understand metrics
2. **Development**: Use notebook to debug and explore
3. **Production**: Use CLI for full evaluation with all metrics
4. **Analysis**: Return to notebook for custom analysis

## Next Steps After Notebook

Once you understand the metrics:

1. **Run full evaluation**:
   ```bash
   python -m src.eval_runner
   ```

2. **Generate report**:
   ```bash
   python -m src.report
   ```

3. **Analyze production results**:
   - Open notebook
   - Load `outputs/per_item_metrics.csv`
   - Run custom analysis

## Tips for Best Results

### 1. Run in Order
Execute cells sequentially for correct dependencies

### 2. Restart Kernel When Needed
If strange results: **Kernel → Restart & Run All**

### 3. Save Often
Jupyter auto-saves, but manually save important modifications

### 4. Use Comments
Add notes about interesting findings:
```python
# TODO: Article 5 has unusually low ROUGE - investigate
# NOTE: Enthusiast persona shows higher style variation
```

### 5. Create Checkpoints
Save intermediate results:
```python
# After expensive computation
df_results.to_pickle('outputs/checkpoint.pkl')

# Reload later
df_results = pd.read_pickle('outputs/checkpoint.pkl')
```

## Learning Resources

### Understanding ROUGE
- [ROUGE Paper](https://aclanthology.org/W04-1013/)
- Focus on recall (what % of reference is covered)

### Understanding BERTScore
- [BERTScore Paper](https://arxiv.org/abs/1904.09675)
- Uses BERT embeddings for semantic similarity

### Understanding Stylometry
- Quantitative analysis of writing style
- Features: function words, punctuation, sentence length
- Jensen-Shannon divergence for distribution similarity

## Feedback & Contributions

Found issues or have improvements?
- Add cells with your analysis
- Save modified notebook
- Share insights with team

---

**Happy Exploring!** 🚀

The notebook is designed to be educational and interactive. Take your time with each section to fully understand how the evaluation works.
