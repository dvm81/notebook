# BLEURT Setup Guide

BLEURT is an **optional** metric that provides human-correlated quality scores. The evaluation system works perfectly without it, using ROUGE and BERTScore for content quality assessment.

## Why BLEURT is Optional

1. **Large Downloads**: Checkpoints are 300MB-1GB
2. **TensorFlow Dependency**: Requires TensorFlow 2.x which can have compatibility issues
3. **System Compatibility**: May not work on all macOS configurations (mutex errors)
4. **Slower Performance**: BLEURT is significantly slower than ROUGE/BERTScore

## When to Use BLEURT

BLEURT is valuable when:
- You need the highest correlation with human judgments
- You're evaluating for research/publication
- System compatibility is confirmed
- You have time for longer evaluation runs

## When to Skip BLEURT

You can safely skip BLEURT if:
- Quick evaluation iterations are needed
- ROUGE + BERTScore provide sufficient signal
- You encounter setup/compatibility issues
- Resource constraints (memory, disk space, time)

## Installation Status

✓ BLEURT package installed
✓ Checkpoint downloaded (BLEURT-20-D3, ~300MB)
⚠ System compatibility issue detected (macOS TensorFlow mutex error)

## Enabling BLEURT

If your system supports it, enable BLEURT in `config.yaml`:

```yaml
content:
  use_bleurt: true
  bleurt_checkpoint: "bleurt_checkpoints/BLEURT-20-D3"
```

## Downloading Checkpoints

Run the setup script to download BLEURT checkpoints:

```bash
# Download smallest checkpoint (recommended for demos)
python setup_bleurt.py

# Download specific checkpoint
python setup_bleurt.py BLEURT-20        # Full model (~1GB)
python setup_bleurt.py BLEURT-20-D12    # Medium (~500MB)
python setup_bleurt.py BLEURT-20-D3     # Small (~300MB)
```

## Troubleshooting

### TensorFlow Errors (mutex lock failed)

This is a known issue on some macOS systems with certain TensorFlow versions.

**Workaround:**
- Use Linux or Docker environment
- Skip BLEURT and rely on ROUGE + BERTScore
- Try older TensorFlow version: `pip install tensorflow==2.10.0`

### Checkpoint Download Fails

**Solutions:**
1. Check internet connection
2. Ensure 1GB+ free disk space
3. Try smaller checkpoint (BLEURT-20-D3)
4. Manual download from: https://github.com/google-research/bleurt#checkpoints

### Out of Memory

BLEURT uses significant memory during inference.

**Solutions:**
- Use smaller checkpoint (BLEURT-20-D3)
- Process fewer examples at once
- Close other applications
- Use machine with more RAM

## Alternative: Use Without BLEURT

The system provides excellent evaluation without BLEURT:

**Content Quality Metrics:**
- ✓ ROUGE-1, ROUGE-2, ROUGE-Lsum (n-gram overlap)
- ✓ BERTScore (semantic similarity)
- ✓ Token counts and compression ratios

**Style Fidelity Metrics:**
- ✓ Stylometric features (10 features)
- ✓ Persona similarity scores
- ✓ Jensen-Shannon divergence

These metrics are sufficient for most use cases!

## Performance Comparison

| Metric | Speed | Memory | Correlation with Humans |
|--------|-------|--------|------------------------|
| ROUGE | Fast | Low | Good (0.4-0.5) |
| BERTScore | Medium | Medium | Better (0.5-0.6) |
| BLEURT | Slow | High | Best (0.6-0.7) |

## Current Configuration

In `config.yaml`:
```yaml
use_bleurt: false  # Disabled due to system compatibility
```

To enable, change to:
```yaml
use_bleurt: true
```

And ensure checkpoint is downloaded and system is compatible.

## Testing BLEURT

After setup, test with:

```bash
source .venv/bin/activate
python -c "
from bleurt import score
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

scorer = score.BleurtScorer('bleurt_checkpoints/BLEURT-20-D3')
refs = ['This is a test.']
cands = ['This is a test.']
scores = scorer.score(references=refs, candidates=cands)
print(f'BLEURT score: {scores[0]:.4f}')
"
```

If this works without errors, you can enable BLEURT in the config!

## Summary

- **BLEURT is optional** - the system works great without it
- **Checkpoint downloaded** - ready to use if system is compatible
- **Current status** - disabled in config due to macOS compatibility issue
- **Recommendation** - use ROUGE + BERTScore for most use cases

For questions or issues, see:
- BLEURT GitHub: https://github.com/google-research/bleurt
- TensorFlow compatibility: https://www.tensorflow.org/install
