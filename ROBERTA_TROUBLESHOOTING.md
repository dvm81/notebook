# RoBERTa Local Model Troubleshooting

## Issue: Model Still Downloads from HuggingFace Despite Local Setup

### Problem
Even after running `setup_roberta.py` and seeing the message "Using local RoBERTa-large model from...", BERTScore still tries to download from HuggingFace and may fail.

### Root Cause
The original `setup_roberta.py` downloads files to a simple `roberta-large/` directory, but transformers expects files in a specific cache structure. Setting `HF_HOME` alone isn't sufficient.

### Solution: Use Improved Setup Script

#### Option 1: Use setup_roberta_v2.py (Recommended)

This uses transformers' built-in caching mechanism:

```bash
# Download using proper transformers caching
python setup_roberta_v2.py
```

This creates a `model_cache/` directory with the proper structure that transformers expects.

#### Option 2: Keep Using Original Setup

If you already used `setup_roberta.py`, the code now sets **both** `TRANSFORMERS_CACHE` and `HF_HOME` environment variables, which should work better.

### How It Works Now

The updated code checks for models in this priority order:

1. **`model_cache/`** - Proper transformers cache (from `setup_roberta_v2.py`)
   - Sets `TRANSFORMERS_CACHE` and `HF_HOME`

2. **`roberta-large/`** - Legacy simple directory (from original `setup_roberta.py`)
   - Sets `TRANSFORMERS_CACHE` to the directory
   - Sets `HF_HOME` to the parent directory

3. **HuggingFace download** - Falls back if no local cache found

### Testing Your Setup

#### In Jupyter Notebook

Run the cell before BERTScore and you should see:

**With setup_roberta_v2.py:**
```
✓ Using local RoBERTa model cache from: /path/to/rogue/model_cache
  This will speed up BERTScore evaluation and works offline.
```

**With original setup_roberta.py:**
```
✓ Using local RoBERTa model from: /path/to/rogue/roberta-large
  Note: For better compatibility, run 'python setup_roberta_v2.py'
```

**No local cache:**
```
ℹ Local RoBERTa model cache not found
  BERTScore will download from HuggingFace on first use.
  To download locally: run 'python setup_roberta_v2.py'
```

#### In Python Scripts

Run `python -m src.eval_runner` and check the output for similar messages.

### Verification Test

Test if bert_score can find the local model:

```python
import os
from pathlib import Path

# Set up environment
model_cache = Path("model_cache")
if model_cache.exists():
    os.environ['TRANSFORMERS_CACHE'] = str(model_cache.absolute())
    os.environ['HF_HOME'] = str(model_cache.absolute())

# Try BERTScore
import bert_score

P, R, F1 = bert_score.score(
    ["Test sentence one."],
    ["Test sentence two."],
    model_type='roberta-large',
    lang='en',
    verbose=True  # Set to True to see loading messages
)

print(f"BERTScore F1: {F1.item():.4f}")
```

If it works without downloading, your local cache is properly configured!

### Migrating from Old to New Setup

If you used `setup_roberta.py` and want to switch to the improved version:

```bash
# Optional: Remove old directory (saves ~1.4GB)
rm -rf roberta-large/

# Download using new method
python setup_roberta_v2.py
```

The new setup will work better across different environments and is more compatible with transformers' expected cache structure.

### Environment Variables Explained

- **`TRANSFORMERS_CACHE`** - Where transformers looks for cached models
- **`HF_HOME`** - Base directory for all HuggingFace cache files
- **`HF_HUB_OFFLINE=1`** - (Optional) Prevents any internet access, forces offline mode

### Common Errors and Solutions

#### Error: "ConnectionError: Couldn't reach server"
**Cause:** Model not in cache, trying to download
**Solution:** Run `setup_roberta_v2.py` or check environment variables are set

#### Error: "OSError: Can't load config"
**Cause:** Wrong directory structure or missing files
**Solution:** Use `setup_roberta_v2.py` which creates proper structure

#### Error: "Model not found"
**Cause:** Environment variables not set in the current process
**Solution:** Make sure you run the setup cell **before** the BERTScore cell in notebooks

### Offline Usage

Once properly cached with `setup_roberta_v2.py`, you can work completely offline:

```bash
# Optional: Force offline mode
export HF_HUB_OFFLINE=1
export TRANSFORMERS_OFFLINE=1

# Run evaluation (will use cached model only)
python -m src.eval_runner
```

### File Sizes

- **setup_roberta.py**: ~1.4 GB in `roberta-large/`
- **setup_roberta_v2.py**: ~1.4 GB in `model_cache/` (proper cache structure)

Both download roughly the same amount of data, but v2 stores it in a more compatible format.

### Still Having Issues?

1. **Check Python environment**: Make sure you're using the same environment where packages are installed
2. **Check permissions**: Ensure you have write access to create `model_cache/` directory
3. **Check disk space**: Need ~2GB free space for model files
4. **Try verbose mode**: Set `verbose=True` in `bert_score.score()` to see what's happening
5. **Check transformers version**: `pip show transformers` (should be >=4.30.0)

### Contact/Issues

If problems persist, check:
- Transformers library version
- Bert-score library version
- Python version (3.8+ recommended)

Report issues at: https://github.com/dvm81/notebook/issues
