# Evaluation Methodology: Persona-Aware Summary Quality Assessment

## Overview

This evaluation system measures the quality of financial/business summaries across two critical dimensions: **content accuracy** and **style fidelity**. Unlike traditional summarization metrics that focus solely on information coverage, this approach recognizes that professional summaries must also match the writing style and tone expected by their target audience.

## The Two-Dimensional Quality Model

### Why Content Alone Is Insufficient

Traditional summary evaluation uses metrics like ROUGE and BERTScore to measure how well a generated summary captures the key information from a source document. While these metrics are valuable, they fail to capture a critical aspect of professional writing: **appropriateness for audience**.

A summary containing all the right information can still fail if:
- The tone is too casual for a formal analyst report
- The language is too technical for a general business audience
- The structure doesn't match expected conventions (e.g., bullet points vs. narrative)
- Word choice and sentence construction feel "off" for the intended persona

**Example:** An AI-generated summary might score high on ROUGE (capturing all key facts) but use informal phrasing like "the company crushed earnings" instead of "earnings exceeded expectations"—appropriate for an enthusiast blog but inappropriate for formal analyst research.

### The Dual Evaluation Framework

Our methodology evaluates summaries on two independent axes:

1. **Content Quality (70% weight)**: Does the summary accurately convey the essential information?
2. **Style Fidelity (30% weight)**: Does the summary match the expected writing style of the target persona?

This 70/30 weighting reflects a practical reality: content accuracy is paramount, but style matters significantly for professional acceptability and reader trust.

---

## Content Quality Assessment (70% of Overall Score)

Content quality combines three complementary metrics that capture different aspects of information fidelity:

### 1. ROUGE Metrics (40% of content score)

**What it measures:** Lexical overlap between generated and reference summaries using n-gram matching.

**Metrics used:**
- **ROUGE-1**: Unigram (single word) overlap
- **ROUGE-2**: Bigram (two-word phrase) overlap
- **ROUGE-Lsum**: Longest common subsequence (captures sentence-level structure)

**Why it matters:** ROUGE excels at measuring whether specific facts, numbers, and key terms are preserved. In financial summaries, precise terminology matters—"revenue increased 19.3%" must appear accurately.

**Limitations:** ROUGE is purely lexical and doesn't understand semantics. "Revenue grew 20%" and "Sales rose 20%" are semantically equivalent but score differently.

**Implementation:** We use ROUGE-Lsum F1 as the primary ROUGE metric, as it balances precision (not including irrelevant info) with recall (capturing all important info) while respecting sentence boundaries.

### 2. BERTScore (30% of content score)

**What it measures:** Semantic similarity using contextualized word embeddings from a pre-trained language model (RoBERTa-large).

**How it works:** Instead of requiring exact word matches, BERTScore:
- Embeds each word in context using a transformer model
- Computes similarity between embeddings (e.g., "revenue" and "sales" are semantically close)
- Aligns words/phrases between reference and generated summary
- Calculates precision, recall, and F1 based on semantic similarity

**Why it matters:** BERTScore captures paraphrasing, synonyms, and meaning preservation that ROUGE misses. It recognizes that "quarterly earnings beat analyst expectations" conveys the same information as "results exceeded consensus estimates."

**Complementarity with ROUGE:**
- ROUGE penalizes paraphrasing → ensures factual precision
- BERTScore rewards paraphrasing → captures semantic equivalence
- Together: summaries must be both factually precise AND semantically accurate

**Model choice:** We use `roberta-large` with baseline rescaling, providing strong semantic understanding while remaining computationally feasible.

### 3. BLEURT (30% of content score, optional)

**What it measures:** Human-correlated quality using a model trained on human judgments of summary quality.

**Why it matters:** BLEURT learns what humans consider "good" summaries beyond simple overlap or semantics—including fluency, coherence, and informativeness.

**Status:** Optional due to computational requirements. When disabled, weights redistribute to ROUGE (40%) and BERTScore (60%) for content_quality calculation.

### Content Quality Formula

```
content_quality = (0.40 × ROUGE-Lsum_F1) + (0.30 × BERTScore_F1) + (0.30 × BLEURT_normalized)
```

When BLEURT is disabled:
```
content_quality = (0.40 × ROUGE-Lsum_F1) + (0.60 × BERTScore_F1)
```

**Rationale for weights:**
- ROUGE (40%): Ensures factual precision and terminology accuracy—critical for financial content
- BERTScore (30-60%): Captures semantic meaning and accepts valid paraphrasing
- BLEURT (30%): Incorporates human judgments of overall quality when available

---

## Style Fidelity Assessment (30% of Overall Score)

Style fidelity measures how well a generated summary matches the expected writing style of its target persona (e.g., formal analyst, journalist, enthusiast).

### Stylometric Feature Extraction

We extract a 10-dimensional feature vector capturing quantifiable aspects of writing style:

| Feature | What It Captures | Why It Matters |
|---------|------------------|----------------|
| **Function word rate** | Frequency of articles, prepositions, conjunctions | Formal writing uses more function words ("the analysis indicates") vs informal ("analysis shows") |
| **Average sentence length** | Mean words per sentence (normalized) | Analysts write longer, complex sentences; journalists prefer shorter, punchier ones |
| **Type-token ratio** | Unique words / total words | Vocabulary diversity—higher in formal writing |
| **Comma rate** | Commas per 100 words | Complex clauses require more commas |
| **Period rate** | Periods per 100 words | Inverse of sentence length |
| **Exclamation rate** | Exclamations per 100 words | Enthusiasm marker (high in enthusiast, near-zero in formal) |
| **Question rate** | Questions per 100 words | Rhetorical questions common in journalism, rare in formal reports |
| **Pronoun rate** | Personal/possessive pronouns | "We maintain our rating" (formal) vs "The company" (journalist) |
| **Flesch-Kincaid grade** | Reading difficulty level (normalized) | Academic/technical complexity |
| **Average word length** | Mean characters per word (normalized) | Longer words correlate with formal register |

**Example differences:**

*Formal analyst:*
- High function word rate (0.45+)
- Long sentences (25+ words)
- High Flesch-Kincaid grade (14+, college level)
- No exclamations, few questions
- Moderate pronoun use ("We believe...")

*Journalist:*
- Moderate function words (0.40-0.44)
- Medium sentences (15-20 words)
- Mid Flesch-Kincaid (10-12, high school level)
- Rare exclamations, occasional questions
- Low pronoun use (third person narrative)

*Enthusiast:*
- Lower function words (0.35-0.40)
- Variable sentence length
- Lower Flesch-Kincaid (8-10, accessible)
- Some exclamations (0.5-2 per 100 words)
- Higher pronoun use ("You can see...")

### Persona Centroid Construction

For each persona (formal_analyst, journalist, enthusiast):
1. **Collect representative samples**: 5-10 example texts in `data/personas/{persona}.txt`
2. **Extract features**: Compute 10-dimensional feature vector for each sample
3. **Calculate centroid**: Average feature vectors → representative "stylometric fingerprint"
4. **Cache centroids**: Store in `outputs/persona_centroids.json` for fast lookup

### Style Similarity Calculation

To measure how well a generated summary matches a target persona:

1. **Extract features** from generated summary → 10-dimensional vector
2. **Retrieve persona centroid** for target persona
3. **Calculate Jensen-Shannon divergence** between distributions
4. **Convert to similarity**: `similarity = 1 - JS_divergence`

**Why Jensen-Shannon divergence?**
- Symmetric (unlike KL divergence)
- Bounded [0, 1], making it interpretable
- Treats features as probability distributions
- Measures "distance" between writing styles

**Interpretation:**
- **0.90-1.00**: Excellent style match—indistinguishable from persona samples
- **0.80-0.90**: Good match—appropriate style with minor variations
- **0.70-0.80**: Acceptable—mostly correct but noticeable differences
- **<0.70**: Poor match—style feels "off" for target persona

### Automatic Persona Detection

The system automatically infers the target persona from document metadata:

```python
# Inference rules:
if "Research Note" in prompt_type OR "Analyst" in author:
    persona = "formal_analyst"
elif "Morning Summary" in prompt_type OR "Brief" in prompt_type:
    persona = "journalist"
elif "PhD" in author OR "CFA" in author OR "Economist" in author:
    persona = "formal_analyst"
else:
    persona = "journalist"  # default
```

This eliminates manual annotation while ensuring summaries are evaluated against appropriate style standards.

---

## Overall Quality: The Combined Metric

### Formula

```
overall_quality = (0.70 × content_quality) + (0.30 × style_similarity)
```

### Rationale for 70/30 Weighting

**Content-dominant (70%):**
- Information accuracy is the primary function of a summary
- Factual errors are unacceptable regardless of style
- Content quality is objectively measurable against reference summaries

**Style-significant (30%):**
- Professional summaries must match audience expectations
- Style affects perceived credibility and trust
- Poor style undermines reader confidence even with correct content
- 30% is enough to penalize egregious style mismatches without overwhelming content

**Real-world analogy:** A medical diagnosis must be accurate (70% weight) but also communicated appropriately to the patient (30% weight). A correct diagnosis delivered in incomprehensible jargon fails the patient.

### Interpretation Scale

| Score Range | Quality Level | Interpretation |
|-------------|---------------|----------------|
| **0.80-1.00** | Excellent | Publication-ready, matches professional standards |
| **0.70-0.80** | Very Good | Minor refinements needed, acceptable for most uses |
| **0.60-0.70** | Good | Usable with editing, captures essentials appropriately |
| **0.50-0.60** | Fair | Significant issues in content or style, needs revision |
| **<0.50** | Poor | Fails to meet minimum standards, major problems |

### Why This Makes Sense

**1. Balanced evaluation:** Rewards summaries that are both informative AND appropriate—reflecting real-world requirements.

**2. Handles trade-offs:** A summary scoring 0.9 on content but 0.5 on style gets 0.78 overall—good but not excellent. This correctly reflects that style matters.

**3. Prevents gaming:** Systems can't score well by optimizing only content metrics while ignoring style (or vice versa).

**4. Aligns with human judgment:** In user studies, professional readers weight content heavily but reject summaries with inappropriate tone/style—the 70/30 split approximates this.

**5. Actionable feedback:** Decomposed scores show whether issues are content-related (improve information coverage) or style-related (adjust tone/structure).

---

## Evaluation Pipeline

1. **Load JSON files** from `data/` directory (one article + summaries per file)
2. **Infer target persona** from metadata (prompt_type, author credentials)
3. **Build/load persona centroids** from reference samples
4. **Calculate content metrics**:
   - ROUGE scores via n-gram matching
   - BERTScore via transformer embeddings
   - BLEURT (optional) via trained scorer
   - Combine into content_quality
5. **Calculate style metrics**:
   - Extract 10 stylometric features
   - Compare to persona centroid via JS divergence
   - Convert to style_similarity
6. **Compute overall_quality**: 70% content + 30% style
7. **Save results**: Per-item CSV + aggregate statistics by persona/sector/model

---

## Validation and Robustness

### Why These Metrics?

**Established baselines:**
- ROUGE: Standard in summarization evaluation since 2004
- BERTScore: Widely adopted (4000+ citations) for semantic matching
- Stylometry: Decades of research in authorship attribution and style analysis

**Complementary strengths:**
- ROUGE: Fast, deterministic, captures factual precision
- BERTScore: Semantic understanding, handles paraphrasing
- Stylometry: Quantifies subjective "appropriateness"

**Domain-appropriate:**
- Financial summaries require precision → ROUGE emphasis
- Professional writing has measurable style markers → stylometry
- Semantic equivalence matters → BERTScore

### Extensibility

The framework supports:
- **New personas**: Add samples to `data/personas/{new_persona}.txt`
- **Custom weights**: Adjust content/style balance for different use cases
- **Additional metrics**: BLEURT, METEOR, custom neural scorers
- **Multi-language**: Stylometric features are largely language-agnostic

---

## Practical Applications

**Model evaluation:** Compare GPT-4, Claude, Llama on financial summarization—measuring both accuracy and style adherence.

**Prompt engineering:** Test different prompts to optimize overall_quality score—find balance between comprehensive coverage and appropriate tone.

**Quality assurance:** Flag summaries below 0.6 overall_quality for human review before publication.

**Persona tuning:** Identify which personas a model handles well vs. poorly—guide fine-tuning efforts.

**A/B testing:** Test summary variants with users—correlate human preference with overall_quality scores to validate metric.

---

## Conclusion

The **overall_quality** metric represents a principled approach to evaluating professional summaries that acknowledges a fundamental truth: **content and style are both essential**.

By combining established content metrics (ROUGE, BERTScore) with quantitative stylometric analysis, we create a single score that answers the question: *"Is this summary both accurate and appropriate?"*

The 70/30 weighting reflects the primacy of content while ensuring style is not ignored—a balance that aligns with how human experts evaluate summaries in practice.

This methodology enables systematic evaluation of AI-generated summaries for professional contexts where both "what is said" and "how it is said" determine success.
