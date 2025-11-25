#!/usr/bin/env python
"""
Helper script to download BLEURT checkpoint.

BLEURT checkpoints are large (~400MB-1GB) and hosted on Google Cloud Storage.
This script helps download and set up the checkpoint for use.
"""

import os
import sys
import urllib.request
import zipfile
import tarfile
from pathlib import Path

CHECKPOINTS = {
    'BLEURT-20': {
        'url': 'https://storage.googleapis.com/bleurt-oss-21/BLEURT-20.zip',
        'size': '~1GB',
        'description': 'Full BLEURT-20 model (recommended for best performance)'
    },
    'BLEURT-20-D12': {
        'url': 'https://storage.googleapis.com/bleurt-oss-21/BLEURT-20-D12.zip',
        'size': '~500MB',
        'description': 'Medium-sized BLEURT-20 model (good balance)'
    },
    'BLEURT-20-D3': {
        'url': 'https://storage.googleapis.com/bleurt-oss-21/BLEURT-20-D3.zip',
        'size': '~300MB',
        'description': 'Smallest BLEURT-20 model (faster, slightly lower quality)'
    }
}

def download_checkpoint(checkpoint_name='BLEURT-20-D3', dest_dir='bleurt_checkpoints'):
    """Download a BLEURT checkpoint from Google Cloud Storage."""

    if checkpoint_name not in CHECKPOINTS:
        print(f"Error: Unknown checkpoint '{checkpoint_name}'")
        print(f"\nAvailable checkpoints:")
        for name, info in CHECKPOINTS.items():
            print(f"  - {name}: {info['description']} ({info['size']})")
        return False

    checkpoint_info = CHECKPOINTS[checkpoint_name]
    url = checkpoint_info['url']
    size = checkpoint_info['size']

    # Create destination directory
    dest_path = Path(dest_dir)
    dest_path.mkdir(exist_ok=True)

    checkpoint_dir = dest_path / checkpoint_name
    if checkpoint_dir.exists():
        print(f"✓ Checkpoint '{checkpoint_name}' already exists at {checkpoint_dir}")
        return True

    print(f"Downloading {checkpoint_name} checkpoint...")
    print(f"  Source: {url}")
    print(f"  Size: {size}")
    print(f"  Destination: {dest_path}")
    print()
    print("This may take several minutes depending on your connection speed...")
    print()

    # Download the file
    zip_path = dest_path / f"{checkpoint_name}.zip"

    try:
        def progress_hook(count, block_size, total_size):
            percent = int(count * block_size * 100 / total_size)
            sys.stdout.write(f"\rDownloading... {percent}%")
            sys.stdout.flush()

        urllib.request.urlretrieve(url, zip_path, progress_hook)
        print("\n✓ Download complete!")

        # Extract the zip file
        print(f"Extracting checkpoint...")
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(dest_path)

        print(f"✓ Checkpoint extracted to {checkpoint_dir}")

        # Clean up zip file
        zip_path.unlink()
        print(f"✓ Cleaned up temporary files")

        return True

    except Exception as e:
        print(f"\n✗ Error downloading checkpoint: {e}")
        print("\nTroubleshooting:")
        print("  1. Check your internet connection")
        print("  2. Ensure you have sufficient disk space")
        print("  3. Try a smaller checkpoint (BLEURT-20-D3)")
        print("  4. Download manually from: https://github.com/google-research/bleurt#checkpoints")
        return False

def verify_checkpoint(checkpoint_name='BLEURT-20-D3', dest_dir='bleurt_checkpoints'):
    """Verify that a checkpoint can be loaded."""

    checkpoint_path = Path(dest_dir) / checkpoint_name

    if not checkpoint_path.exists():
        print(f"✗ Checkpoint directory not found: {checkpoint_path}")
        return False

    print(f"Verifying checkpoint at {checkpoint_path}...")

    try:
        from bleurt import score
        scorer = score.BleurtScorer(str(checkpoint_path))

        # Test with a simple example
        references = ["This is a test sentence."]
        candidates = ["This is a test."]
        scores = scorer.score(references=references, candidates=candidates)

        print(f"✓ Checkpoint loaded successfully!")
        print(f"  Test score: {scores[0]:.4f}")
        return True

    except Exception as e:
        print(f"✗ Error loading checkpoint: {e}")
        return False

def main():
    """Main function."""

    print("="*80)
    print("BLEURT Checkpoint Setup")
    print("="*80)
    print()

    # Default to smallest checkpoint for demos
    checkpoint_name = 'BLEURT-20-D3'

    if len(sys.argv) > 1:
        checkpoint_name = sys.argv[1]

    print("Available checkpoints:")
    for name, info in CHECKPOINTS.items():
        marker = "→" if name == checkpoint_name else " "
        print(f"  {marker} {name}: {info['description']} ({info['size']})")
    print()
    print(f"Selected: {checkpoint_name}")
    print()

    # Download checkpoint
    success = download_checkpoint(checkpoint_name)

    if not success:
        print("\n✗ Failed to download checkpoint")
        return 1

    print()

    # Verify checkpoint
    success = verify_checkpoint(checkpoint_name)

    if not success:
        print("\n✗ Failed to verify checkpoint")
        return 1

    print()
    print("="*80)
    print("✓ BLEURT setup complete!")
    print("="*80)
    print()
    print(f"To use this checkpoint in your code:")
    print(f"  from bleurt import score")
    print(f"  scorer = score.BleurtScorer('bleurt_checkpoints/{checkpoint_name}')")
    print()
    print("To use in config.yaml:")
    print(f"  bleurt_checkpoint: 'bleurt_checkpoints/{checkpoint_name}'")
    print()

    return 0

if __name__ == '__main__':
    sys.exit(main())
