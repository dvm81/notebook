"""
Content quality metrics: ROUGE, BERTScore, and BLEURT.
"""

from typing import Dict, Any, Optional
from pathlib import Path
from rouge_score import rouge_scorer
from src.text_utils import count_tokens


class ContentMetricsCalculator:
    """Calculate content quality metrics for summaries."""

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize metrics calculator.

        Args:
            config: Configuration dictionary with content metrics settings
        """
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
        self._bertscore_model = None  # Lazy load
        self._bertscore_tokenizer = None  # Lazy load

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

    def _load_bertscore_model(self):
        """Lazy load BERTScore model and tokenizer from local directory."""
        if self._bertscore_model is not None:
            return self._bertscore_model, self._bertscore_tokenizer

        try:
            from transformers import AutoModel, AutoTokenizer

            # Try to load from local directory first (using configured model name)
            model_dir = Path(self.bertscore_model)

            if model_dir.exists() and (model_dir / "config.json").exists():
                print(f"Loading BERTScore model from local directory: {model_dir}")
                self._bertscore_tokenizer = AutoTokenizer.from_pretrained(
                    str(model_dir),
                    local_files_only=True
                )
                self._bertscore_model = AutoModel.from_pretrained(
                    str(model_dir),
                    local_files_only=True
                )
            else:
                print(f"Loading BERTScore model from HuggingFace: {self.bertscore_model}")
                self._bertscore_tokenizer = AutoTokenizer.from_pretrained(self.bertscore_model)
                self._bertscore_model = AutoModel.from_pretrained(self.bertscore_model)

            # Move to eval mode
            self._bertscore_model.eval()

            return self._bertscore_model, self._bertscore_tokenizer

        except Exception as e:
            print(f"Warning: Failed to load BERTScore model: {e}")
            self._bertscore_model = False
            self._bertscore_tokenizer = False
            return None, None

    def calculate_bertscore(
        self,
        reference: str,
        hypothesis: str
    ) -> Optional[float]:
        """
        Calculate BERTScore manually using transformers.

        Computes BERTScore by:
        1. Loading model from local roberta-large/ directory if available
        2. Computing embeddings for reference and hypothesis
        3. Computing greedy token-level matching with cosine similarity
        4. Returning F1 score

        Args:
            reference: Gold summary
            hypothesis: Generated summary

        Returns:
            BERTScore F1 or None if disabled
        """
        if not self.content_config.get('use_bertscore', True):
            return None

        try:
            import torch
            import torch.nn.functional as F

            # Load model and tokenizer
            model, tokenizer = self._load_bertscore_model()

            if model is None or tokenizer is None:
                return None

            # Tokenize
            ref_tokens = tokenizer(reference, return_tensors="pt", padding=True, truncation=True, max_length=512)
            hyp_tokens = tokenizer(hypothesis, return_tensors="pt", padding=True, truncation=True, max_length=512)

            # Get embeddings
            with torch.no_grad():
                ref_outputs = model(**ref_tokens)
                hyp_outputs = model(**hyp_tokens)

            # Get last hidden states
            ref_embeds = ref_outputs.last_hidden_state[0]  # [seq_len, hidden_dim]
            hyp_embeds = hyp_outputs.last_hidden_state[0]

            # Remove CLS and SEP tokens (first and last)
            ref_embeds = ref_embeds[1:-1]
            hyp_embeds = hyp_embeds[1:-1]

            # Normalize embeddings
            ref_embeds = F.normalize(ref_embeds, p=2, dim=1)
            hyp_embeds = F.normalize(hyp_embeds, p=2, dim=1)

            # Compute cosine similarity matrix
            sim_matrix = torch.mm(hyp_embeds, ref_embeds.t())  # [hyp_len, ref_len]

            # Precision: for each hypothesis token, find max similarity with reference
            precision = sim_matrix.max(dim=1)[0].mean().item()

            # Recall: for each reference token, find max similarity with hypothesis
            recall = sim_matrix.max(dim=0)[0].mean().item()

            # F1
            if precision + recall > 0:
                f1 = 2 * (precision * recall) / (precision + recall)
            else:
                f1 = 0.0

            return f1

        except Exception as e:
            print(f"Warning: BERTScore calculation failed: {e}")
            import traceback
            traceback.print_exc()
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
