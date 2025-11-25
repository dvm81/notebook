# Test Data Overview

This document describes the realistic test data created for validating the evaluation system.

## Dataset Statistics

- **Total Articles**: 12
- **Sectors**: Technology (2), Healthcare (1), Finance (1), Environment (1), Sports (1), Automotive (1), Real Estate (1), Defense (1), Energy (1), Biotechnology (1), Retail (1)
- **Date Range**: November 2024
- **Personas**: 3 distinct writing styles

## Articles Summary

### 1. NVIDIA Q3 2024 Results (uid-tech-001)
- **Sector**: Technology
- **Persona**: formal_analyst
- **Topic**: Record revenue driven by AI chip demand
- **Key Points**: $18.1B revenue, Data Center dominance, 75% gross margin
- **Summary Quality**: Good - accurate and complete

### 2. FDA Alzheimer's Drug Approval (uid-health-001)
- **Sector**: Healthcare
- **Persona**: enthusiast
- **Topic**: Lecanemab approval for early Alzheimer's
- **Key Points**: 27% reduction in cognitive decline, $26,500 annual cost
- **Summary Quality**: Good - enthusiastic but accurate

### 3. Federal Reserve Interest Rates (uid-finance-001)
- **Sector**: Finance
- **Persona**: formal_analyst
- **Topic**: Fed holds rates steady at 5.25-5.50%
- **Key Points**: Data-dependent approach, no rate cuts soon
- **Summary Quality**: Excellent - precise and complete

### 4. Ocean Temperature Record (uid-env-001)
- **Sector**: Environment
- **Persona**: enthusiast
- **Topic**: 2024 ocean temperatures hit record highs
- **Key Points**: 14 zettajoules more heat, 73% coral bleaching
- **Summary Quality**: Good - energetic and informative

### 5. Google Quantum Breakthrough (uid-tech-002)
- **Sector**: Technology
- **Persona**: enthusiast
- **Topic**: Willow chip achieves error correction milestone
- **Key Points**: 105 qubits, exponential error reduction
- **Summary Quality**: Excellent - captures excitement and key facts

### 6. Premier League TV Deal (uid-sports-001)
- **Sector**: Sports
- **Persona**: journalist
- **Topic**: £6.7B domestic rights agreement
- **Key Points**: Sky/TNT/BBC split, revenue distribution
- **Summary Quality**: Good - professional and balanced

### 7. Toyota Solid-State Battery (uid-auto-001)
- **Sector**: Automotive
- **Persona**: enthusiast
- **Topic**: Claims 900-mile range by 2028
- **Key Points**: Dendrite formation solved, 1M mile lifespan
- **Summary Quality**: Good - enthusiastic with expert skepticism noted

### 8. Commercial Office Vacancies (uid-realestate-001)
- **Sector**: Real Estate
- **Persona**: journalist
- **Topic**: Vacancy rates hit 20-year highs
- **Key Points**: 19.6% average, remote work impact, conversions
- **Summary Quality**: Excellent - comprehensive coverage

### 9. U.S.-Japan Defense Alliance (uid-defense-001)
- **Sector**: Defense
- **Persona**: formal_analyst
- **Topic**: Joint command structure upgrade
- **Key Points**: Yokota Air Base HQ, 2% GDP defense spending
- **Summary Quality**: Good - formal and thorough

### 10. Offshore Wind Auction (uid-energy-001)
- **Sector**: Energy
- **Persona**: enthusiast
- **Topic**: Largest U.S. offshore wind lease auction
- **Key Points**: 488,000 acres, 5.6 GW capacity, March 2025
- **Summary Quality**: Good - energetic and detailed

### 11. CRISPR Gene Therapy Approval (uid-biotech-001)
- **Sector**: Biotechnology
- **Persona**: enthusiast
- **Topic**: First CRISPR therapy for sickle cell disease
- **Key Points**: 95% resolution of crises, $2.2M cost
- **Summary Quality**: Excellent - excitement balanced with facts

### 12. Walmart Automation (uid-retail-001)
- **Sector**: Retail
- **Persona**: journalist
- **Topic**: 65% of stores to use AI by 2026
- **Key Points**: $9B investment, 20% cost reduction, retraining
- **Summary Quality**: Good - balanced reporting

## Persona Characteristics

### formal_analyst
- **Style**: Corporate, data-driven, precise
- **Tone**: Professional, measured, objective
- **Characteristics**:
  - Uses specific numerical data
  - Formal vocabulary (e.g., "consensus estimates", "sequential growth")
  - Passive voice and third-person
  - No exclamation points or emotional language
  - Technical terminology
- **Example Phrases**: "demonstrated substantial revenue growth", "attributable to favorable product mix", "contingent upon continued adoption"

### enthusiast
- **Style**: Energetic, conversational, excited
- **Tone**: Informal, engaging, passionate
- **Characteristics**:
  - Frequent exclamation points
  - Superlatives (incredible, huge, massive, amazing)
  - Direct address to reader
  - Colloquial language
  - Emotional reactions
- **Example Phrases**: "This is absolutely incredible!", "We're talking about", "Get this:", "That's insane!", "Mind-blowing fact:"

### journalist
- **Style**: Balanced, informative, professional
- **Tone**: Neutral, factual, clear
- **Characteristics**:
  - Inverted pyramid structure
  - Attribution of sources
  - Balanced presentation
  - Clear, concise sentences
  - Professional but accessible
- **Example Phrases**: "announced plans to", "according to", "representing a", "The agreement includes", "experts note that"

## Expected Evaluation Results

### Content Quality Expectations

Articles should show:
- **High ROUGE scores** (0.6-0.8): Summaries capture key facts accurately
- **High BERTScore** (0.85-0.95): Semantic similarity is strong
- **Varied BLEURT scores** (0.3-0.7): Some summaries more polished than others

### Style Similarity Expectations

- **formal_analyst summaries**: Should match formal_analyst persona well (0.7-0.9)
- **enthusiast summaries**: Should match enthusiast persona well (0.7-0.9)
- **journalist summaries**: Should match journalist persona well (0.7-0.9)

### Quality Variations

The dataset includes summaries with varying quality levels:

1. **Excellent matches**: Articles 3, 5, 8, 11
   - High content quality
   - Strong style fidelity
   - Comprehensive coverage

2. **Good matches**: Articles 1, 2, 4, 6, 7, 9, 10, 12
   - Good content quality
   - Good style match
   - Minor omissions acceptable

3. **Subtle issues**: None intentionally added
   - All summaries are accurate
   - No hallucinations present
   - Style matches persona assignments

## Testing the System

To evaluate the test data:

```bash
# Run evaluation
python -m src.eval_runner

# Generate report
python -m src.report

# Check outputs
cat outputs/report.md
head -n 20 outputs/per_item_metrics.csv
```

## Expected Insights

After evaluation, you should see:

1. **Overall high content quality** (avg 0.65-0.75)
2. **Strong style fidelity** for matched personas (avg 0.70-0.85)
3. **Per-persona consistency** in writing patterns
4. **Sector diversity** showing system handles various domains
5. **Compression ratios** varying by content type

## Use Cases Demonstrated

This test data demonstrates the system's ability to:

1. ✓ Handle diverse content domains
2. ✓ Distinguish between writing styles
3. ✓ Evaluate factual accuracy
4. ✓ Measure stylometric similarity
5. ✓ Process realistic article lengths (300-600 words)
6. ✓ Work with professional-quality summaries
7. ✓ Generate meaningful comparative metrics
8. ✓ Support per-persona analysis

## Data Quality Notes

- All articles are realistic and fact-based (though example URLs)
- Summaries maintain factual accuracy (no hallucinations)
- Personas show clear stylistic differences
- Metadata is complete and properly formatted
- JSON structure matches specification exactly
