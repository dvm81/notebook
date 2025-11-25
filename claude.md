
# Persona Summarization Evaluation — Plan (Using Your Exact JSON Schema)

This plan binds the evaluator to **your JSON schema** (from the screenshot) and specifies files, functions, and commands a coding agent can implement immediately.

We evaluate two pillars:
1) **Content Quality** — ROUGE‑1/2/Lsum + BERTScore + BLEURT.
2) **Style/Persona Fidelity** — Stylometric similarity to persona corpora (+ optional persona classifier).

---

## 0) Exact schema mapping

Each line in `data/input.jsonl` is a JSON object with **these fields** (as seen in your file):

```json
{
  "link": "https://...",
  "document_title": "string",
  "document_content": "long text",
  "metadata": {
    "author": "string",
    "sector": "string",
    "date": "YYYY-MM-DD"
  },
  "uid": "string",
  "write_id": "string",
  "notes": [],
  "expected_summary": "GOLD summary text",
  "agented_summary": "MODEL summary text to evaluate",
  "export_timestamp": "ISO8601"
}
```

> If additional keys like `project_name` or `tags` exist, they are passed through to the per‑item CSV for traceability but **not** required by metrics.

**Persona information:** Your JSON does **not** include `persona_id`. We will supply a separate file `data/persona_assignments.csv` (columns: `write_id,persona_id`) to tell the evaluator which persona each item should match. If a row is missing, the evaluator will set `persona_id = null` and skip style scoring for that item.

---

## 1) Repository layout

```
persona-eval/
├─ README.md
├─ requirements.txt
├─ config.yaml                               # copy of the exact template below
├─ data/
│  ├─ input.jsonl                            # your JSONL with the schema above
│  ├─ persona_assignments.csv                # write_id → persona_id mapping (required for style)
│  └─ personas/
│     ├─ alex.txt                            # 3–10 short samples per persona
│     └─ priya.txt
├─ src/
│  ├─ io_utils.py
│  ├─ text_utils.py
│  ├─ content_metrics.py
│  ├─ style_features.py
│  ├─ eval_runner.py
│  └─ report.py
└─ outputs/
   ├─ per_item_metrics.csv
   ├─ corpus_aggregates.json
   └─ report.md
```

---

## 2) Config (edit `config.yaml`)

```yaml
fields:
  source_text: "document_content"
  gold_summary: "expected_summary"
  model_summary: "agented_summary"

  # traceability / joins
  doc_title: "document_title"
  link: "link"
  author: "metadata.author"
  sector: "metadata.sector"
  report_date: "metadata.date"
  uid: "uid"
  write_id: "write_id"
  export_timestamp: "export_timestamp"
  notes: "notes"

# optional CSV mapping write_id → persona_id (string)
persona_assignments_csv: "data/persona_assignments.csv"

# persona corpora for style centroids
personas:
  alex: "data/personas/alex.txt"
  priya: "data/personas/priya.txt"

content:
  use_rouge: true
  rouge_variant: "rougeLsum"
  use_bertscore: true
  bertscore_model: "roberta-large"
  use_bleurt: true
  bleurt_checkpoint: "BLEURT-20-D12"

style:
  use_stylometric_similarity: true
  use_persona_classifier: false
  embedding_model: "all-MiniLM-L6-v2"
  rejection_threshold: 0.55
```

---

## 3) Implementation details

### 3.1 `io_utils.py`
- `load_jsonl(path)` — yields records.
- `get_field(obj, dotted_path, default=None)` — nested access (`"metadata.author"`).
- `load_persona_assignments(csv_path)` — returns `dict(write_id → persona_id)`.
- `record_to_example(rec, cfg, persona_map)` → returns tuple:
  `(source_text, gold, model, persona_id, trace_info)` where `persona_id = persona_map.get(write_id)`.

### 3.2 `content_metrics.py`
- Use `rouge-score` with `["rouge1","rouge2","rougeLsum"]`, `use_stemmer=True`.
- Use `bert-score` (`model_type=cfg.content.bertscore_model`, `rescale_with_baseline=True`).
- Use BLEURT (`bleurt_checkpoint=cfg.content.bleurt_checkpoint`). If multiple golds exist in future, use `max(score)`.
- Return per‑item dict with:
  `rouge1_f, rouge2_f, rougeLsum_f, rouge1_r, rougeLsum_r, bertscore_f1, bleurt, src_tokens, hyp_tokens, gold_tokens, compression_ratio`.

### 3.3 `style_features.py`
- Build **stylometric vectors** from persona corpora (function words, avg sentence length, type–token ratio, punctuation rates, pronoun rates, FK grade).
- Create a centroid per persona; cache to `outputs/persona_centroids.json`.
- For each item with `persona_id` present, compute `style_similarity ∈ [0,1]` (1 − JS‑divergence).
- If `persona_id` missing, set `style_similarity = null` and flag `style_skipped = 1`.

### 3.4 `eval_runner.py`
Flow:
1. Load config + persona assignments + persona centroids.
2. Stream records from `data/input.jsonl`.
3. For each record: extract fields per config; compute **content** and **style** metrics.
4. Write `outputs/per_item_metrics.csv` (columns below).
5. Aggregate means/medians/95% CIs overall and by persona → `outputs/corpus_aggregates.json`.
6. Build `outputs/report.md` with toplines and per‑persona tables.

CLI:
```bash
python -m src.eval_runner --config config.yaml --data data/input.jsonl --out outputs/per_item_metrics.csv
```

---

## 4) Output columns (per_item_metrics.csv)

Identifiers:
- `write_id`, `uid`, `persona_id`, `document_title`, `link`, `author`, `sector`, `report_date`, `export_timestamp`

Content:
- `rouge1_f`, `rouge2_f`, `rougeLsum_f`, `rouge1_r`, `rougeLsum_r`,
- `bertscore_f1`, `bleurt`,
- `src_tokens`, `hyp_tokens`, `gold_tokens`, `compression_ratio`

Style:
- `style_similarity` (nullable), `style_skipped` (0/1)

Composites:
- `content_quality = 0.4*rougeLsum_f + 0.3*bertscore_f1 + 0.3*bleurt`
- `style_fidelity = style_similarity` (or a weighted mix if you later add a classifier)

---

## 5) Commands

```bash
# 1) Install
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python -c "import nltk; nltk.download('punkt'); nltk.download('punkt_tab')"

# 2) Prepare config
cp persona_eval_config.exact.yaml config.yaml

# 3) Provide persona assignment mapping
# data/persona_assignments.csv with columns: write_id,persona_id

# 4) Run evaluation
python -m src.eval_runner --config config.yaml --data data/input.jsonl --out outputs/per_item_metrics.csv

# 5) Generate report
python -m src.report --metrics outputs/per_item_metrics.csv --out outputs/report.md
```

---

## 6) Acceptance criteria

- Pipeline runs on your JSONL and emits:
  `outputs/per_item_metrics.csv`, `outputs/corpus_aggregates.json`, `outputs/report.md`.
- Content metrics (ROUGE/BERTScore/BLEURT) computed for **all** items.
- Style metric computed for items with a persona in `persona_assignments.csv`.
- Reproducible via `config.yaml` without code edits.
