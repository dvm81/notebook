"""
Content quality metrics: ROUGE, BERTScore, and BLEURT.
"""

from typing import Dict, Any, Optional
from pathlib import Path
from rouge_score import rouge_scorer
import bert_score
from src.text_utils import count_tokens


class ContentMetricsCalculator:
    """Calculate content quality metrics for summaries."""

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize metrics calculator.

        Args:
            config: Configuration dictionary with content metrics settings
        """
        import os

        self.config = config
        self.content_config = config.get('content', {})

        # Initialize ROUGE
        if self.content_config.get('use_rouge', True):
            rouge_types = ['rouge1', 'rouge2', 'rougeLsum']
            self.rouge_scorer = rouge_scorer.RougeScorer(rouge_types, use_stemmer=True)
        else:
            self.rouge_scorer = None

        # BERTScore model configuration
        self.bertscore_model = self.content_config.get('bertscore_model', 'roberta-large')

        # Set up local model cache for transformers if it exists
        model_cache_dir = Path("model_cache")
        roberta_legacy_dir = Path("roberta-large")

        if model_cache_dir.exists() and list(model_cache_dir.glob("**/config.json")):
            # Use new model_cache directory (from setup_roberta_v2.py)
            os.environ['TRANSFORMERS_CACHE'] = str(model_cache_dir.absolute())
            os.environ['HF_HOME'] = str(model_cache_dir.absolute())
            print(f"Using local RoBERTa model cache from: {model_cache_dir.absolute()}")
        elif roberta_legacy_dir.exists() and (roberta_legacy_dir / "config.json").exists():
            # Use legacy roberta-large directory (from old setup_roberta.py)
            os.environ['TRANSFORMERS_CACHE'] = str(roberta_legacy_dir.absolute())
            os.environ['HF_HOME'] = str(roberta_legacy_dir.parent.absolute())
            print(f"Using local RoBERTa-large model from: {roberta_legacy_dir.absolute()}")

        # BLEURT checkpoint
        self.bleurt_checkpoint = self.content_config.get('bleurt_checkpoint', 'BLEURT-20-D12')
        self.bleurt_scorer = None  # Lazy load

    def _init_bleurt(self):
        """Lazy initialization of BLEURT scorer."""
        if self.bleurt_scorer is None and self.content_config.get('use_bleurt', True):
            try:
                from bleurt import score
                self.bleurt_scorer = score.BleurtScorer(self.bleurt_checkpoint)
            except Exception as e:
                print(f"Warning: BLEURT initialization failed: {e}")
                self.bleurt_scorer = False

    def calculate_rouge(
        self,
        reference: str,
        hypothesis: str
    ) -> Dict[str, float]:
        """
        Calculate ROUGE scores.

        Args:
            reference: Gold summary
            hypothesis: Generated summary

        Returns:
            Dictionary with ROUGE scores
        """
        if not self.rouge_scorer:
            return {}

        scores = self.rouge_scorer.score(reference, hypothesis)

        return {
            'rouge1_f': scores['rouge1'].fmeasure,
            'rouge2_f': scores['rouge2'].fmeasure,
            'rougeLsum_f': scores['rougeLsum'].fmeasure,
            'rouge1_r': scores['rouge1'].recall,
            'rouge2_r': scores['rouge2'].recall,
            'rougeLsum_r': scores['rougeLsum'].recall,
        }

    def calculate_bertscore(
        self,
        reference: str,
        hypothesis: str
    ) -> Optional[float]:
        """
        Calculate BERTScore.

        Will use local RoBERTa-large model if roberta-large/ directory exists,
        otherwise downloads from HuggingFace.

        Args:
            reference: Gold summary
            hypothesis: Generated summary

        Returns:
            BERTScore F1 or None if disabled
        """
        if not self.content_config.get('use_bertscore', True):
            return None

        try:
            P, R, F1 = bert_score.score(
                [hypothesis],
                [reference],
                model_type=self.bertscore_model,
                lang='en',
                rescale_with_baseline=True,
                verbose=False
            )
            return F1.item()
        except Exception as e:
            print(f"Warning: BERTScore calculation failed: {e}")
            return None

    def calculate_bleurt(
        self,
        reference: str,
        hypothesis: str
    ) -> Optional[float]:
        """
        Calculate BLEURT score.

        Args:
            reference: Gold summary
            hypothesis: Generated summary

        Returns:
            BLEURT score or None if disabled/failed
        """
        if not self.content_config.get('use_bleurt', True):
            return None

        self._init_bleurt()

        if not self.bleurt_scorer:
            return None

        try:
            scores = self.bleurt_scorer.score(
                references=[reference],
                candidates=[hypothesis]
            )
            return scores[0]
        except Exception as e:
            print(f"Warning: BLEURT calculation failed: {e}")
            return None

    def calculate_all_metrics(
        self,
        source_text: str,
        reference: str,
        hypothesis: str
    ) -> Dict[str, Any]:
        """
        Calculate all content metrics for a single example.

        Args:
            source_text: Source document
            reference: Gold summary
            hypothesis: Generated summary

        Returns:
            Dictionary with all metrics
        """
        metrics = {}

        # ROUGE
        rouge_scores = self.calculate_rouge(reference, hypothesis)
        metrics.update(rouge_scores)

        # BERTScore
        bertscore_f1 = self.calculate_bertscore(reference, hypothesis)
        metrics['bertscore_f1'] = bertscore_f1

        # BLEURT
        bleurt_score = self.calculate_bleurt(reference, hypothesis)
        metrics['bleurt'] = bleurt_score

        # Token counts and compression ratio
        src_tokens = count_tokens(source_text)
        hyp_tokens = count_tokens(hypothesis)
        gold_tokens = count_tokens(reference)

        metrics['src_tokens'] = src_tokens
        metrics['hyp_tokens'] = hyp_tokens
        metrics['gold_tokens'] = gold_tokens
        metrics['compression_ratio'] = hyp_tokens / src_tokens if src_tokens > 0 else 0.0

        # Composite score
        rougeLsum_f = metrics.get('rougeLsum_f', 0.0)
        bertscore = bertscore_f1 if bertscore_f1 is not None else 0.0
        bleurt = bleurt_score if bleurt_score is not None else 0.0

        # Normalize BLEURT to 0-1 range (BLEURT typically ranges from -1 to 1)
        bleurt_normalized = (bleurt + 1) / 2 if bleurt is not None else 0.0

        metrics['content_quality'] = (
            0.4 * rougeLsum_f +
            0.3 * bertscore +
            0.3 * bleurt_normalized
        )

        return metrics
