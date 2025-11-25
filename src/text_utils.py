"""
Text processing utilities.
"""

import re
import string
from typing import List
import nltk


def ensure_nltk_data():
    """Download required NLTK data if not present."""
    try:
        nltk.data.find('tokenizers/punkt')
    except LookupError:
        nltk.download('punkt', quiet=True)

    try:
        nltk.data.find('tokenizers/punkt_tab')
    except LookupError:
        nltk.download('punkt_tab', quiet=True)


def tokenize_sentences(text: str) -> List[str]:
    """
    Tokenize text into sentences.

    Args:
        text: Input text

    Returns:
        List of sentences
    """
    ensure_nltk_data()
    return nltk.sent_tokenize(text)


def tokenize_words(text: str) -> List[str]:
    """
    Tokenize text into words.

    Args:
        text: Input text

    Returns:
        List of words
    """
    ensure_nltk_data()
    return nltk.word_tokenize(text)


def count_tokens(text: str) -> int:
    """
    Count number of tokens in text.

    Args:
        text: Input text

    Returns:
        Number of tokens
    """
    return len(tokenize_words(text))


def get_function_words() -> set:
    """
    Get set of common function words for stylometric analysis.

    Returns:
        Set of function words
    """
    return {
        'the', 'be', 'to', 'of', 'and', 'a', 'in', 'that', 'have', 'i',
        'it', 'for', 'not', 'on', 'with', 'he', 'as', 'you', 'do', 'at',
        'this', 'but', 'his', 'by', 'from', 'they', 'we', 'say', 'her', 'she',
        'or', 'an', 'will', 'my', 'one', 'all', 'would', 'there', 'their',
        'what', 'so', 'up', 'out', 'if', 'about', 'who', 'get', 'which', 'go',
        'me', 'when', 'make', 'can', 'like', 'time', 'no', 'just', 'him', 'know',
        'take', 'people', 'into', 'year', 'your', 'good', 'some', 'could', 'them',
        'see', 'other', 'than', 'then', 'now', 'look', 'only', 'come', 'its', 'over'
    }


def get_pronouns() -> set:
    """
    Get set of pronouns for stylometric analysis.

    Returns:
        Set of pronouns
    """
    return {
        'i', 'you', 'he', 'she', 'it', 'we', 'they',
        'me', 'him', 'her', 'us', 'them',
        'my', 'your', 'his', 'her', 'its', 'our', 'their',
        'mine', 'yours', 'hers', 'ours', 'theirs',
        'myself', 'yourself', 'himself', 'herself', 'itself', 'ourselves', 'themselves'
    }


def calculate_flesch_kincaid_grade(text: str) -> float:
    """
    Calculate Flesch-Kincaid grade level.

    Args:
        text: Input text

    Returns:
        Grade level score
    """
    sentences = tokenize_sentences(text)
    words = tokenize_words(text)

    if not sentences or not words:
        return 0.0

    # Count syllables (approximation)
    syllable_count = sum(_count_syllables(word) for word in words)

    num_sentences = len(sentences)
    num_words = len(words)

    if num_sentences == 0 or num_words == 0:
        return 0.0

    # FK grade formula
    grade = 0.39 * (num_words / num_sentences) + 11.8 * (syllable_count / num_words) - 15.59

    return max(0.0, grade)


def _count_syllables(word: str) -> int:
    """
    Count syllables in a word (approximation).

    Args:
        word: Input word

    Returns:
        Estimated syllable count
    """
    word = word.lower()
    vowels = 'aeiouy'
    syllable_count = 0
    previous_was_vowel = False

    for char in word:
        is_vowel = char in vowels
        if is_vowel and not previous_was_vowel:
            syllable_count += 1
        previous_was_vowel = is_vowel

    # Adjust for silent 'e'
    if word.endswith('e'):
        syllable_count -= 1

    # Ensure at least 1 syllable
    return max(1, syllable_count)


def get_punctuation_counts(text: str) -> dict:
    """
    Count different types of punctuation.

    Args:
        text: Input text

    Returns:
        Dictionary of punctuation counts
    """
    return {
        'comma': text.count(','),
        'period': text.count('.'),
        'semicolon': text.count(';'),
        'colon': text.count(':'),
        'exclamation': text.count('!'),
        'question': text.count('?'),
        'total': sum(1 for c in text if c in string.punctuation)
    }
