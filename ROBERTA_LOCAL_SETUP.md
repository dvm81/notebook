# Local RoBERTa-Large Model Setup

This guide explains how to use a local RoBERTa-large model for BERTScore evaluation, avoiding repeated downloads from HuggingFace.

## Overview

The evaluation system uses RoBERTa-large for BERTScore calculation. By default, it downloads the model from HuggingFace on first use. This setup allows you to download the model once and reuse it from local disk.

## Quick Start

### 1. Download Model Files

Run the download script to fetch the required model files:

```bash
python setup_roberta.py
```

This downloads 4 essential files (~1.4GB total) to the `roberta-large/` directory:
- `config.json` - Model configuration
- `merges.txt` - BPE tokenizer merges
- `pytorch_model.bin` - Model weights (~1.3GB)
- `vocab.json` - Tokenizer vocabulary

### 2. Verify Installation

Test that the local model works correctly:

```bash
python test_local_roberta.py
```

You should see:
```
✓ Local RoBERTa model is working correctly!
```

### 3. Run Evaluation

The evaluation system will automatically use the local model:

```bash
python -m src.eval_runner
```

You'll see a message confirming local model usage:
```
Using local RoBERTa-large model from: /path/to/rogue/roberta-large
```

## How It Works

The system automatically detects if `roberta-large/` directory exists with the required files. If found:

1. Sets `HF_HOME` environment variable to the project directory
2. Transformers library finds the model files locally
3. BERTScore uses the local model instead of downloading

If the directory doesn't exist, it falls back to downloading from HuggingFace.

## File Structure

```
rogue/
├── roberta-large/           # Local model directory
│   ├── config.json          # 482 bytes
│   ├── merges.txt           # 446 KB
│   ├── pytorch_model.bin    # 1.3 GB
│   └── vocab.json           # 878 KB
├── setup_roberta.py         # Download script
└── test_local_roberta.py    # Verification script
```

## Troubleshooting

### Model Not Found

If you see "BERTScore calculation failed" or downloading messages:

1. Verify files exist:
   ```bash
   ls -lh roberta-large/
   ```

2. Check all 4 files are present
3. Re-run download script if needed:
   ```bash
   python setup_roberta.py
   ```

### Download Fails

If `setup_roberta.py` fails:

1. Check internet connection
2. Verify `huggingface_hub` is installed:
   ```bash
   pip install huggingface_hub
   ```
3. Try downloading again

### Disk Space

The model requires ~1.4GB of disk space. Ensure you have sufficient space before downloading.

## Benefits

**Faster evaluation:**
- No download wait time on subsequent runs
- Model loads directly from disk

**Offline capability:**
- Run evaluations without internet (after initial download)
- Useful for air-gapped environments

**Reproducibility:**
- Same model version across runs
- No dependency on HuggingFace availability

**Network efficiency:**
- Download once, use many times
- Good for metered connections

## Removing Local Model

To use HuggingFace download instead:

```bash
rm -rf roberta-large/
```

The system will automatically fall back to downloading the model.

## Technical Details

### Environment Variables

The system sets `HF_HOME` to point to the project directory, allowing transformers to find the local model files.

### Model Loading

```python
# In content_metrics.py __init__()
local_model_path = Path("roberta-large")
if local_model_path.exists():
    os.environ['HF_HOME'] = str(local_model_path.parent.absolute())
```

### BERTScore Integration

BERTScore uses `model_type='roberta-large'` which transformers resolves to the local directory via `HF_HOME`.

## Dependencies

Required packages (already in `requirements.txt`):
- `transformers>=4.30.0` - Model loading
- `bert-score>=0.3.13` - BERTScore calculation
- `torch>=2.0.0` - Model execution
- `huggingface_hub>=0.19.0` - Download script

## FAQ

**Q: Do I need to download the model?**
A: No, it's optional. Without local files, the system downloads from HuggingFace automatically.

**Q: Can I delete the files after download?**
A: Yes, but you'll need to download again on next run or rely on HuggingFace.

**Q: Does this work with other models?**
A: This setup is specific to roberta-large. Other models would need similar setup scripts.

**Q: Will this slow down evaluation?**
A: No, loading from local disk is faster than downloading. After initial load, the model stays in memory.

**Q: What if I update requirements.txt?**
A: Local model setup is independent of package updates. It will continue working.

## See Also

- [Main README](README.md) - Overall project documentation
- [METHODOLOGY.md](METHODOLOGY.md) - Evaluation metrics explained
- [config.yaml](config.yaml) - Configuration file with BERTScore settings
