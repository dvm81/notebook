"""
Test script to verify local RoBERTa-large model loading.
"""

import sys
from pathlib import Path
import bert_score


def test_local_model():
    """Test loading RoBERTa-large from local directory."""
    import os

    print("="*80)
    print("Testing Local RoBERTa-Large Model")
    print("="*80)
    print()

    # Check if local model exists
    local_model_path = Path("roberta-large")

    if not local_model_path.exists():
        print("✗ Local model directory not found")
        print("  Run: python setup_roberta.py")
        return False

    required_files = ["config.json", "merges.txt", "pytorch_model.bin", "vocab.json"]
    missing_files = [f for f in required_files if not (local_model_path / f).exists()]

    if missing_files:
        print(f"✗ Missing required files: {missing_files}")
        return False

    print("✓ Local model directory found")
    print(f"  Path: {local_model_path.absolute()}")
    print()

    # Set HF_HOME to use local directory
    os.environ['HF_HOME'] = str(local_model_path.parent.absolute())
    print(f"Set HF_HOME to: {os.environ['HF_HOME']}")
    print()

    # Test BERTScore with local model
    print("Testing BERTScore with model_type='roberta-large'...")
    print()

    reference = "The company reported strong quarterly earnings with revenue growth of 15%."
    hypothesis = "Quarterly results showed solid performance, with revenues up 15%."

    try:
        print("Computing BERTScore...")

        P, R, F1 = bert_score.score(
            [hypothesis],
            [reference],
            model_type='roberta-large',
            lang='en',
            rescale_with_baseline=True,
            verbose=False
        )

        print()
        print("✓ BERTScore calculation successful!")
        print()
        print(f"  Precision: {P.item():.4f}")
        print(f"  Recall:    {R.item():.4f}")
        print(f"  F1:        {F1.item():.4f}")
        print()

        return True

    except Exception as e:
        print(f"✗ BERTScore calculation failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Main entry point."""
    print()
    success = test_local_model()
    print()

    if success:
        print("="*80)
        print("✓ Local RoBERTa model is working correctly!")
        print("="*80)
        print()
        print("The evaluation system will now use the local model automatically.")
        print()
        sys.exit(0)
    else:
        print("="*80)
        print("✗ Local model test failed")
        print("="*80)
        sys.exit(1)


if __name__ == "__main__":
    main()
