# Quick Fix for Local RoBERTa Model Issue

## Your Problem
On another machine, even though you see "Using local RoBERTa-large model from...", bert_score.score() still returns an error trying to access HuggingFace.

## Quick Solution

### Step 1: Use the Improved Setup Script

On your other machine, run:

```bash
cd /path/to/rogue
python setup_roberta_v2.py
```

This will download the model to `model_cache/` directory with proper transformers cache structure (~1.4GB).

### Step 2: Update Your Repository

Pull the latest changes:

```bash
git pull origin main
```

This includes:
- Updated `setup_roberta_v2.py` (improved download script)
- Updated `src/content_metrics.py` (checks `TRANSFORMERS_CACHE` variable)
- Updated notebook cells (checks both `model_cache/` and `roberta-large/`)

### Step 3: Test It Works

Run this quick test:

```python
import os
from pathlib import Path

# Should find the model cache
model_cache = Path("model_cache")
if model_cache.exists():
    os.environ['TRANSFORMERS_CACHE'] = str(model_cache.absolute())
    os.environ['HF_HOME'] = str(model_cache.absolute())
    print(f"✓ Cache found: {model_cache.absolute()}")

# Test BERTScore
import bert_score

P, R, F1 = bert_score.score(
    ["The company reported strong earnings."],
    ["Earnings were strong for the company."],
    model_type='roberta-large',
    lang='en',
    verbose=False
)

print(f"✓ BERTScore works! F1: {F1.item():.4f}")
```

If this runs **without downloading anything**, you're good to go!

## Why This Works Better

**Problem with Original Approach:**
- `setup_roberta.py` downloaded files to simple directory
- Transformers expects specific nested cache structure
- Setting `HF_HOME` alone wasn't enough

**Why New Approach Works:**
- `setup_roberta_v2.py` uses transformers' own caching mechanism
- Creates proper cache structure automatically
- Sets both `TRANSFORMERS_CACHE` and `HF_HOME`
- Works reliably across different environments

## Alternative: Manual Environment Setup

If you can't run the new script, manually set environment variables:

```bash
export TRANSFORMERS_CACHE=/path/to/rogue/model_cache
export HF_HOME=/path/to/rogue/model_cache
```

Or in Python (before importing bert_score):

```python
import os
os.environ['TRANSFORMERS_CACHE'] = '/path/to/rogue/model_cache'
os.environ['HF_HOME'] = '/path/to/rogue/model_cache'
```

## Checklist

- [ ] Pulled latest code: `git pull origin main`
- [ ] Ran new setup: `python setup_roberta_v2.py`
- [ ] Verified `model_cache/` directory exists
- [ ] Tested with quick test script above
- [ ] Ran notebook - no HuggingFace download during BERTScore

## Next Steps

Once this works, you can:

1. **Remove old cache** (optional, saves ~1.4GB):
   ```bash
   rm -rf roberta-large/
   ```

2. **Run evaluation**:
   ```bash
   python -m src.eval_runner
   ```

3. **Use notebooks** - they'll automatically detect and use `model_cache/`

---

**Still stuck?** Check `ROBERTA_TROUBLESHOOTING.md` for detailed debugging steps.
