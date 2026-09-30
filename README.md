# A Reproducible Python Framework for Evaluating Kinyarwanda Forced Alignment

This repository contains the reproducible Python implementation used for the word-level evaluation of Kinyarwanda forced alignment in the study **Developing and Validating a Kinyarwanda Forced-Alignment Resource for Phonetic Research**.

The analysis compares word boundaries produced by the **Montreal Forced Aligner (MFA)** and **WebMAUS** against manually annotated reference boundaries. The repository provides the code, configuration, evaluation data, tests, derived tables, and figures required to reproduce the reported evaluation.

## Evaluation data

The evaluation dataset contains:

- 16 recordings
- 3,676 manually annotated words
- 7,352 word boundaries per automatic aligner
- four anonymized annotators (`Annotator_1`–`Annotator_4`)
- Manual, MFA, and WebMAUS word boundaries

The manual-reference TextGrids also contain the MFA word tier. WebMAUS alignments are stored in separate TextGrid files.

The evaluation is **in-domain**: the 16 recordings were part of the target corpus used during MFA adaptation.

## Evaluation approach

Words are matched across the manual reference, MFA, and WebMAUS using:

1. normalized lexical identity, and
2. sequence order.

Boundary timing is **not** used to establish word correspondence. Timing is compared only after the lexical sequences have been matched.

For every matched word, the pipeline calculates:

- signed start-boundary error
- signed end-boundary error
- absolute start-boundary error
- absolute end-boundary error
- mean absolute word-boundary error
- percentages of boundaries within 20, 50, and 100 ms
- percentages of words with both boundaries within the same thresholds
- recording-level mean absolute error

The main inferential comparison is performed at the **recording level**, using 16 paired MFA–WebMAUS observations.

## Repository structure

```text
kinyarwanda-alignment/
├── config/
│   └── config.yaml
├── data/
│   ├── manual_reference/
│   ├── webmaus/
│   └── derived/
├── results/
│   ├── figures/
│   └── tables/
├── scripts/
│   └── run_evaluation.py
├── src/
│   └── kinyarwanda_alignment/
│       ├── config.py
│       ├── dataset.py
│       ├── diagnostics.py
│       ├── file_utils.py
│       ├── matching.py
│       ├── metrics.py
│       ├── pipeline.py
│       ├── plots.py
│       ├── statistics.py
│       └── textgrid_io.py
├── tests/
├── README.md
└── requirements.txt
```

### Main modules

- `config.py` — loads the YAML configuration and resolves project-relative paths.
- `file_utils.py` — handles filename metadata and conservative word normalization.
- `textgrid_io.py` — loads TextGrid files and validates required tiers.
- `matching.py` — matches the manual word sequence to MFA and WebMAUS by lexical identity and order.
- `dataset.py` — builds and validates the canonical word-level evaluation DataFrame.
- `metrics.py` — calculates boundary-error measures and tolerance summaries.
- `statistics.py` — creates recording-level summaries and performs the paired two-sided Wilcoxon signed-rank test.
- `diagnostics.py` — summarizes large errors and extracts the largest-error words for inspection.
- `plots.py` — creates the evaluation figures.
- `pipeline.py` — coordinates the complete analysis workflow.

The workflow can be summarized as:

```text
TextGrid inputs
    ↓
tier validation
    ↓
word normalization and sequence matching
    ↓
canonical word-level dataset
    ↓
boundary-error calculation
    ↓
descriptive summaries
    ↓
recording-level paired comparison
    ↓
diagnostics, tables, and figures
```

## Setup

The analysis was developed with **Python 3.11.8**.

Create and activate a virtual environment:

```bash
python3.11 -m venv .venv
source .venv/bin/activate
```

Install the required packages:

```bash
pip install -r requirements.txt
```

The main external packages used are pandas, NumPy, SciPy, PyYAML, TextGrid, Matplotlib, and pytest.

## Running the analysis

From the repository root, run:

```bash
python scripts/run_evaluation.py --config config/config.yaml
```

The pipeline rebuilds the canonical evaluation dataset from the TextGrid inputs and writes the derived tables and figures to the configured output directories.

## Tests

Run the test suite with:

```bash
python -m pytest -q
```

The current suite contains 10 focused tests covering filename parsing, word normalization, sequence matching, boundary-error calculation, configuration handling, and recording-level aggregation.

## Outputs

The canonical word-level dataset is written to:

```text
data/derived/word_alignment_evaluation.csv
```

Summary tables are written to:

```text
results/tables/
```

Figures are written to:

```text
results/figures/
```

The generated result files include recording-level summaries, tolerance summaries, large-error diagnostics, the paired statistical test, and evaluation figures.

## Main evaluation results

Across 3,676 matched words:

| Aligner | Mean absolute word-boundary error | Median absolute error | Boundaries within 50 ms |
| --- | ---: | ---: | ---: |
| MFA | 53.82 ms | 22.81 ms | 70.96% |
| WebMAUS | 96.78 ms | 43.26 ms | 55.52% |

At the recording level:

- MFA had the lower mean error in 13 of 16 recordings.
- Mean recording-level MAE was 53.30 ms for MFA and 94.29 ms for WebMAUS.
- The mean paired difference (WebMAUS − MFA) was 40.99 ms.
- The paired two-sided Wilcoxon signed-rank test gave `W = 8, p < .001`.

These results compare the complete alignment configurations used in this evaluation.

## Scope and limitations

This evaluation is limited to **word boundaries**. Phone tiers may be present in the alignment output, but they are not formally evaluated here.

The evaluation is also **in-domain**: the 16 recordings were part of the corpus used during MFA adaptation. The results therefore should not be interpreted as performance on completely unseen Kinyarwanda speech.

The four manual annotators worked on different recordings, so inter-annotator agreement cannot be estimated from this evaluation.

Large alignment errors are retained in the analysis and reported for inspection rather than being automatically removed.

## Reproducibility

The repository is organized so that the analysis can be rerun from the TextGrid inputs using project-relative paths, a YAML configuration file, a pinned `requirements.txt`, a single command-line entry point, explicit validation checks, automated tests, and deterministic output locations.

This makes the repository an executable record of the evaluation analysis used in the study.

