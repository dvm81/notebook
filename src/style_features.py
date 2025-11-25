"""
Style and persona fidelity metrics using stylometric features.
"""

import json
import numpy as np
from pathlib import Path
from typing import Dict, Any, Optional, List
from scipy.spatial.distance import jensenshannon
from src.text_utils import (
    tokenize_sentences,
    tokenize_words,
    get_function_words,
    get_pronouns,
    calculate_flesch_kincaid_grade,
    get_punctuation_counts
)


class StyleAnalyzer:
    """Analyze stylometric features and calculate persona similarity."""

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize style analyzer.

        Args:
            config: Configuration dictionary with style settings and persona paths
        """
        self.config = config
        self.style_config = config.get('style', {})
        self.personas = config.get('personas', {})
        self.centroids = {}
        self.function_words = get_function_words()
        self.pronouns = get_pronouns()

    def extract_stylometric_features(self, text: str) -> np.ndarray:
        """
        Extract stylometric feature vector from text.

        Features:
        - Function word rates (normalized frequencies)
        - Average sentence length
        - Type-token ratio
        - Punctuation rates
        - Pronoun rate
        - Flesch-Kincaid grade

        Args:
            text: Input text

        Returns:
            Feature vector as numpy array
        """
        if not text.strip():
            return np.zeros(10)

        # Tokenize
        sentences = tokenize_sentences(text)
        words = tokenize_words(text)
        words_lower = [w.lower() for w in words]

        if not words:
            return np.zeros(10)

        # Feature 1: Function word rate
        function_word_count = sum(1 for w in words_lower if w in self.function_words)
        function_word_rate = function_word_count / len(words)

        # Feature 2: Average sentence length
        avg_sentence_length = len(words) / len(sentences) if sentences else 0

        # Feature 3: Type-token ratio (vocabulary diversity)
        type_token_ratio = len(set(words_lower)) / len(words) if words else 0

        # Feature 4-7: Punctuation rates
        punct_counts = get_punctuation_counts(text)
        total_chars = len(text)
        comma_rate = punct_counts['comma'] / total_chars if total_chars > 0 else 0
        period_rate = punct_counts['period'] / total_chars if total_chars > 0 else 0
        exclamation_rate = punct_counts['exclamation'] / total_chars if total_chars > 0 else 0
        question_rate = punct_counts['question'] / total_chars if total_chars > 0 else 0

        # Feature 8: Pronoun rate
        pronoun_count = sum(1 for w in words_lower if w in self.pronouns)
        pronoun_rate = pronoun_count / len(words)

        # Feature 9: Flesch-Kincaid grade
        fk_grade = calculate_flesch_kincaid_grade(text)
        fk_grade_normalized = min(fk_grade / 20.0, 1.0)  # Normalize to 0-1

        # Feature 10: Average word length
        avg_word_length = sum(len(w) for w in words) / len(words)
        avg_word_length_normalized = min(avg_word_length / 10.0, 1.0)

        features = np.array([
            function_word_rate,
            avg_sentence_length / 50.0,  # Normalize (assume max 50 words/sentence)
            type_token_ratio,
            comma_rate * 100,  # Scale up
            period_rate * 100,
            exclamation_rate * 100,
            question_rate * 100,
            pronoun_rate,
            fk_grade_normalized,
            avg_word_length_normalized
        ])

        return features

    def build_persona_centroids(self, force_rebuild: bool = False) -> Dict[str, np.ndarray]:
        """
        Build stylometric centroids for each persona from their corpus files.

        Args:
            force_rebuild: If True, rebuild even if cache exists

        Returns:
            Dictionary mapping persona_id to centroid vector
        """
        cache_path = Path('outputs/persona_centroids.json')

        # Try to load from cache
        if not force_rebuild and cache_path.exists():
            with open(cache_path, 'r') as f:
                cached = json.load(f)
                self.centroids = {k: np.array(v) for k, v in cached.items()}
                return self.centroids

        centroids = {}

        for persona_id, corpus_path in self.personas.items():
            if not Path(corpus_path).exists():
                print(f"Warning: Persona corpus not found: {corpus_path}")
                continue

            # Load persona corpus
            with open(corpus_path, 'r', encoding='utf-8') as f:
                corpus_text = f.read()

            # Split into samples (assume samples separated by double newlines)
            samples = [s.strip() for s in corpus_text.split('\n\n') if s.strip()]

            if not samples:
                print(f"Warning: No samples found for persona {persona_id}")
                continue

            # Extract features from each sample
            feature_vectors = []
            for sample in samples:
                features = self.extract_stylometric_features(sample)
                feature_vectors.append(features)

            # Calculate centroid (mean of all samples)
            centroid = np.mean(feature_vectors, axis=0)
            centroids[persona_id] = centroid

        # Cache centroids
        cache_path.parent.mkdir(parents=True, exist_ok=True)
        with open(cache_path, 'w') as f:
            json.dump({k: v.tolist() for k, v in centroids.items()}, f, indent=2)

        self.centroids = centroids
        return centroids

    def calculate_style_similarity(
        self,
        text: str,
        persona_id: Optional[str]
    ) -> Optional[float]:
        """
        Calculate stylometric similarity between text and persona centroid.

        Uses 1 - Jensen-Shannon divergence as similarity measure.

        Args:
            text: Text to analyze
            persona_id: Target persona ID

        Returns:
            Similarity score in [0, 1] or None if persona not available
        """
        if not self.style_config.get('use_stylometric_similarity', True):
            return None

        if persona_id is None:
            return None

        # Ensure centroids are built
        if not self.centroids:
            self.build_persona_centroids()

        if persona_id not in self.centroids:
            print(f"Warning: No centroid for persona {persona_id}")
            return None

        # Extract features from text
        text_features = self.extract_stylometric_features(text)
        persona_centroid = self.centroids[persona_id]

        # Normalize features to probability distributions (add small epsilon to avoid zeros)
        epsilon = 1e-10
        text_dist = text_features + epsilon
        text_dist = text_dist / text_dist.sum()

        centroid_dist = persona_centroid + epsilon
        centroid_dist = centroid_dist / centroid_dist.sum()

        # Calculate Jensen-Shannon divergence
        js_divergence = jensenshannon(text_dist, centroid_dist)

        # Convert to similarity (1 - divergence)
        # JS divergence is in [0, 1] for probability distributions
        similarity = 1.0 - js_divergence

        return float(similarity)

    def calculate_style_metrics(
        self,
        hypothesis: str,
        persona_id: Optional[str]
    ) -> Dict[str, Any]:
        """
        Calculate all style metrics for a summary.

        Args:
            hypothesis: Generated summary
            persona_id: Target persona ID

        Returns:
            Dictionary with style metrics
        """
        style_similarity = self.calculate_style_similarity(hypothesis, persona_id)
        style_skipped = 1 if (persona_id is None or style_similarity is None) else 0

        return {
            'style_similarity': style_similarity,
            'style_skipped': style_skipped,
            'style_fidelity': style_similarity  # Alias for composite metric
        }
