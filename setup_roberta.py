"""
Download RoBERTa-large model files for local use.

This script downloads only the essential model files needed for BERTScore
evaluation, avoiding repeated downloads during evaluation runs.

Files downloaded:
- config.json (model configuration)
- merges.txt (BPE merges for tokenizer)
- pytorch_model.bin (model weights)
- vocab.json (tokenizer vocabulary)

Usage:
    python setup_roberta.py
"""

import os
import sys
from pathlib import Path
from huggingface_hub import hf_hub_download


def download_roberta_large():
    """Download RoBERTa-large model files to local directory."""

    model_name = "roberta-large"
    local_dir = Path("roberta-large")

    print("="*80)
    print("RoBERTa-Large Model Download")
    print("="*80)
    print()
    print(f"Downloading RoBERTa-large model files to: {local_dir.absolute()}")
    print()

    # Create directory
    local_dir.mkdir(exist_ok=True)

    # Files to download
    files_to_download = [
        "config.json",
        "merges.txt",
        "pytorch_model.bin",
        "vocab.json"
    ]

    print("Files to download:")
    for f in files_to_download:
        print(f"  - {f}")
    print()

    # Download each file
    for filename in files_to_download:
        print(f"Downloading {filename}...", end=" ", flush=True)

        try:
            # Download from Hugging Face Hub
            downloaded_path = hf_hub_download(
                repo_id=model_name,
                filename=filename,
                cache_dir=None,
                local_dir=local_dir,
                local_dir_use_symlinks=False
            )
            print("✓")

        except Exception as e:
            print(f"✗")
            print(f"Error downloading {filename}: {e}")
            return False

    print()
    print("="*80)
    print("Download Complete!")
    print("="*80)
    print()
    print(f"Model files saved to: {local_dir.absolute()}")
    print()

    # Verify all files exist
    missing_files = []
    for filename in files_to_download:
        if not (local_dir / filename).exists():
            missing_files.append(filename)

    if missing_files:
        print("⚠ Warning: Some files are missing:")
        for f in missing_files:
            print(f"  - {f}")
        return False

    print("All files downloaded successfully!")
    print()
    print("Next steps:")
    print("  1. The code will automatically use the local model")
    print("  2. Run evaluation: python -m src.eval_runner")
    print()

    return True


def main():
    """Main entry point."""
    try:
        # Check if huggingface_hub is installed
        import huggingface_hub
    except ImportError:
        print("Error: huggingface_hub is not installed")
        print("Install with: pip install huggingface_hub")
        sys.exit(1)

    success = download_roberta_large()

    if not success:
        print("\n⚠ Download failed. Please check errors above.")
        sys.exit(1)

    sys.exit(0)


if __name__ == "__main__":
    main()
