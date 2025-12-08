"""
Download RoBERTa-large model for local use (Improved Version).

This script uses transformers' built-in caching to properly download
and cache the model for offline use with BERTScore.

Usage:
    python setup_roberta_v2.py
"""

import os
import sys
from pathlib import Path


def download_roberta_large():
    """Download RoBERTa-large using transformers' caching."""

    print("="*80)
    print("RoBERTa-Large Model Download (Using Transformers Cache)")
    print("="*80)
    print()

    # Set cache directory
    cache_dir = Path("model_cache")
    cache_dir.mkdir(exist_ok=True)

    print(f"Cache directory: {cache_dir.absolute()}")
    print()

    try:
        from transformers import AutoModel, AutoTokenizer

        print("Downloading RoBERTa-large model and tokenizer...")
        print("(This will download ~1.4GB, may take a few minutes)")
        print()

        # Download and cache model
        print("1. Downloading tokenizer...")
        tokenizer = AutoTokenizer.from_pretrained(
            "roberta-large",
            cache_dir=str(cache_dir)
        )
        print("   ✓ Tokenizer downloaded")

        # Download and cache model
        print("2. Downloading model weights...")
        model = AutoModel.from_pretrained(
            "roberta-large",
            cache_dir=str(cache_dir)
        )
        print("   ✓ Model downloaded")

        print()
        print("="*80)
        print("Download Complete!")
        print("="*80)
        print()
        print(f"Model cached in: {cache_dir.absolute()}")
        print()
        print("Next steps:")
        print("  1. Set TRANSFORMERS_CACHE environment variable")
        print(f"     export TRANSFORMERS_CACHE={cache_dir.absolute()}")
        print("  2. Or the code will set it automatically")
        print("  3. Run evaluation: python -m src.eval_runner")
        print()

        return True

    except Exception as e:
        print(f"\n✗ Download failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Main entry point."""
    try:
        from transformers import AutoModel, AutoTokenizer
    except ImportError:
        print("Error: transformers is not installed")
        print("Install with: pip install transformers")
        sys.exit(1)

    success = download_roberta_large()

    if not success:
        print("\n⚠ Download failed. Please check errors above.")
        sys.exit(1)

    sys.exit(0)


if __name__ == "__main__":
    main()
