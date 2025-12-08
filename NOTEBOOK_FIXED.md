# evaluation_demo.ipynb - Fixed and Ready

## What Was Fixed

### 1. **Removed Duplicate Cells**
- Cell-9 was a duplicate with incorrect type (markdown instead of code)
- Deleted the duplicate, keeping the properly structured cell

### 2. **Fixed Cell Types**
- All code cells are now properly marked as `code` type
- All markdown cells are properly marked as `markdown` type

### 3. **Improved Local Model Detection**
- Now checks for both `model_cache/` (new preferred location) and `roberta-large/` (legacy)
- Sets both `TRANSFORMERS_CACHE` and `HF_HOME` environment variables
- Provides clear feedback about which cache is being used

### 4. **Updated Instructions**
- Intro cell now recommends `setup_roberta_v2.py` (improved version)
- Clear section headers for local model setup

## Current Notebook Structure

```
1. Introduction & Setup Instructions
2. Imports
3. Load Data
4. Examine One Example
5. ROUGE Metrics
6. BERTScore Section:
   - BERTScore intro (markdown)
   - Local Model Setup header (markdown)
   - Check for local model (code) ← FIXED
   - Calculate BERTScore (code)
7. Stylometric Analysis
8. Persona Similarity
9. Complete Evaluation
10. Results Summary
11. Visualization
12. Next Steps
```

## How to Use

### Option 1: With Local Model (Recommended)

```bash
# Step 1: Download local model (~1.4GB, one-time)
python setup_roberta_v2.py

# Step 2: Run notebook
jupyter notebook evaluation_demo.ipynb
```

When you run the "Local Model Setup" cell, you'll see:
```
✓ Using local RoBERTa model cache from: /path/to/rogue/model_cache
  This will speed up BERTScore evaluation and works offline.
```

### Option 2: Without Local Model

```bash
# Just run the notebook
jupyter notebook evaluation_demo.ipynb
```

When you run the "Local Model Setup" cell, you'll see:
```
ℹ Local RoBERTa model cache not found
  BERTScore will download from HuggingFace on first use.
  To download locally: run 'python setup_roberta_v2.py'
```

BERTScore will download the model automatically on first use (slower, requires internet).

## Expected Output

### Cell 1 (Imports)
```
✓ Imports successful
```

### Cell 3 (Load Data)
```
✓ Loaded 9 records

Personas: {'formal_analyst'}
Sectors: {'Automotive', 'Technology', 'Economics', 'Healthcare', ...}
```

### Cell 10 (Local Model Setup)
```
✓ Using local RoBERTa model cache from: /path/to/model_cache
  This will speed up BERTScore evaluation and works offline.
```

### Cell 11 (BERTScore)
```
Calculating BERTScore (may take a minute on first run)...

📊 BERTScore:
  Precision: 0.4458
  Recall:    0.4446
  F1:        0.4452

💡 BERTScore F1 of 0.4452 indicates fair semantic similarity
```

## Troubleshooting

### Issue: "Using local model" message but still downloads

**Solution:** Pull latest code and use `setup_roberta_v2.py`:
```bash
git pull origin main
python setup_roberta_v2.py
```

### Issue: ImportError for modules

**Solution:** Make sure you're in the right environment:
```bash
source .venv/bin/activate  # or activate your venv
pip install -r requirements.txt
```

### Issue: No JSON files found

**Solution:** Make sure you have data files:
```bash
ls data/*.json  # Should show 9 JSON files
```

### Issue: BERTScore fails

**Solution:** Check bert-score is installed:
```bash
pip install bert-score
```

## Performance Notes

**With Local Model:**
- First BERTScore calculation: ~10-30 seconds (model loads from disk)
- Subsequent calls: ~1-5 seconds per summary
- Works offline after initial setup

**Without Local Model:**
- First BERTScore calculation: 1-5 minutes (downloads ~1.4GB)
- Subsequent calls: ~1-5 seconds per summary
- Requires internet on first use

## Next Steps

1. ✅ **Notebook is ready to use**
2. Run through all cells to generate evaluation results
3. Check `outputs/evaluation_viz.png` for visualizations
4. Review detailed metrics in the Results Summary section

## Files You Can Commit

The fixed notebook is ready to commit:
```bash
git add evaluation_demo.ipynb
git commit -m "Fix evaluation_demo.ipynb - remove duplicates and improve model detection"
git push origin main
```

---

**Status:** ✅ Ready to use
**Tested:** Imports work, structure is correct
**Recommended:** Use with `setup_roberta_v2.py` for best experience
