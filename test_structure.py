"""
Quick test to validate project structure and basic functionality.
This test doesn't require heavy dependencies like BERTScore or BLEURT.
"""

import sys
from pathlib import Path

def test_imports():
    """Test that all modules can be imported."""
    print("Testing imports...")
    try:
        from src import io_utils, text_utils
        print("  ✓ Basic imports successful")
        return True
    except ImportError as e:
        print(f"  ✗ Import failed: {e}")
        return False

def test_file_structure():
    """Test that all required files exist."""
    print("\nTesting file structure...")
    required_files = [
        'config.yaml',
        'requirements.txt',
        'README.md',
        'data/input.jsonl',
        'data/persona_assignments.csv',
        'data/personas/formal_analyst.txt',
        'data/personas/enthusiast.txt',
        'data/personas/journalist.txt',
        'src/__init__.py',
        'src/io_utils.py',
        'src/text_utils.py',
        'src/content_metrics.py',
        'src/style_features.py',
        'src/eval_runner.py',
        'src/report.py'
    ]

    all_exist = True
    for file in required_files:
        if Path(file).exists():
            print(f"  ✓ {file}")
        else:
            print(f"  ✗ {file} - MISSING")
            all_exist = False

    return all_exist

def test_io_utils():
    """Test I/O utilities."""
    print("\nTesting I/O utilities...")
    try:
        from src.io_utils import load_jsonl, get_field, load_persona_assignments

        # Test load_jsonl
        records = list(load_jsonl('data/input.jsonl'))
        assert len(records) == 12, f"Expected 12 records, got {len(records)}"
        print(f"  ✓ Loaded {len(records)} records from JSONL")

        # Test get_field
        test_obj = {'metadata': {'author': 'Test Author'}}
        author = get_field(test_obj, 'metadata.author')
        assert author == 'Test Author', f"Expected 'Test Author', got {author}"
        print("  ✓ Nested field access works")

        # Test load_persona_assignments
        persona_map = load_persona_assignments('data/persona_assignments.csv')
        assert len(persona_map) == 12, f"Expected 12 assignments, got {len(persona_map)}"
        print(f"  ✓ Loaded {len(persona_map)} persona assignments")

        return True
    except Exception as e:
        print(f"  ✗ Test failed: {e}")
        return False

def test_text_utils():
    """Test text utilities."""
    print("\nTesting text utilities...")
    try:
        from src.text_utils import tokenize_sentences, tokenize_words, count_tokens

        test_text = "This is a test. It has two sentences."

        sentences = tokenize_sentences(test_text)
        assert len(sentences) == 2, f"Expected 2 sentences, got {len(sentences)}"
        print(f"  ✓ Sentence tokenization works ({len(sentences)} sentences)")

        words = tokenize_words(test_text)
        assert len(words) > 0, "Expected some words"
        print(f"  ✓ Word tokenization works ({len(words)} words)")

        token_count = count_tokens(test_text)
        assert token_count > 0, "Expected some tokens"
        print(f"  ✓ Token counting works ({token_count} tokens)")

        return True
    except Exception as e:
        print(f"  ✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_config_loading():
    """Test config loading."""
    print("\nTesting config loading...")
    try:
        import yaml

        with open('config.yaml', 'r') as f:
            config = yaml.safe_load(f)

        assert 'fields' in config, "Missing 'fields' in config"
        assert 'personas' in config, "Missing 'personas' in config"
        assert 'content' in config, "Missing 'content' in config"
        assert 'style' in config, "Missing 'style' in config"

        print("  ✓ Config structure is valid")
        print(f"  ✓ Found {len(config['personas'])} personas configured")

        return True
    except Exception as e:
        print(f"  ✗ Test failed: {e}")
        return False

def main():
    """Run all tests."""
    print("=" * 60)
    print("PERSONA SUMMARIZATION EVALUATION - STRUCTURE TEST")
    print("=" * 60)

    tests = [
        test_file_structure,
        test_config_loading,
        test_imports,
        test_io_utils,
        test_text_utils
    ]

    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"\n✗ Test crashed: {e}")
            import traceback
            traceback.print_exc()
            results.append(False)

    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    passed = sum(results)
    total = len(results)
    print(f"Passed: {passed}/{total}")

    if all(results):
        print("\n✓ All tests passed! Project structure is ready.")
        print("\nNext steps:")
        print("  1. Install dependencies: pip install -r requirements.txt")
        print("  2. Download NLTK data: python -c \"import nltk; nltk.download('punkt'); nltk.download('punkt_tab')\"")
        print("  3. Run evaluation: python -m src.eval_runner")
        return 0
    else:
        print("\n✗ Some tests failed. Please fix the issues above.")
        return 1

if __name__ == '__main__':
    sys.exit(main())
