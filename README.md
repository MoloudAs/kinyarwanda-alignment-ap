# A Reproducible Python Framework for Evaluating Kinyarwanda Forced Alignment

**Author:** Moloud Asakereh  
**Course:** Advanced Python for NLP  
**Institution:** Heinrich Heine University Düsseldorf (HHU)

## Project overview

This repository contains the Advanced Python (AP) implementation of a reproducible evaluation framework for **Kinyarwanda forced alignment**.

The project compares word-boundary timings from three annotation/alignment sources:

- **Manual reference annotations**
- **Montreal Forced Aligner (MFA)**
- **WebMAUS**

The underlying research workflow already existed as part of a larger forced-alignment study. The AP contribution is to turn the validated analysis logic into a small, modular, documented, testable, and reproducible Python project with:

- reusable Python modules;
- YAML configuration;
- a command-line entry point;
- automatic validation of expected data structure;
- reproducible result tables and figures;
- automated tests.

The project intentionally remains compact. It focuses on the Python techniques needed for the actual analysis rather than adding unrelated NLP or machine-learning libraries.

## Research objective

The main objective is to evaluate how closely automatically generated Kinyarwanda word boundaries match manual reference boundaries.

The computational questions are:

1. Can Manual, MFA, and WebMAUS word sequences be matched reliably using **lexical identity and sequence order**?
2. How large are the start- and end-boundary errors produced by MFA and WebMAUS relative to the manual reference?
3. How do the two aligners compare when the analysis is summarized at the **recording level**?
4. Which words and word boundaries show the largest alignment errors and therefore deserve qualitative inspection?

## Data

The evaluation dataset contains:

- **16 recordings**
- **3,676 manually annotated words**
- four anonymized manual annotators:
  - `Annotator_1`
  - `Annotator_2`
  - `Annotator_3`
  - `Annotator_4`

The relevant input directories are:

```text
data/
├── manual_reference/
└── webmaus/
```

The manual reference TextGrids also contain the MFA word tier used in the comparison. WebMAUS annotations are read from separate TextGrid files.

The repository configuration expects the following tiers:

- Manual reference: one tier beginning with `manual`
- MFA: `wordsMFA`
- WebMAUS: `ORT-MAU`

### Data access

The evaluation files are research data and are stored according to the permissions of the underlying project. They should not be assumed to be freely redistributable.

To run the project with authorized copies of the data, place the files under:

```text
data/manual_reference/
data/webmaus/
```

using the directory structure expected by `config/config.yaml`.

## Evaluation design

### 1. Conservative word normalization

Before matching labels across systems, word strings are normalized conservatively:

- Unicode is normalized with NFC;
- several apostrophe variants are mapped to the standard ASCII apostrophe;
- redundant whitespace is removed;
- comparison is case-insensitive using `casefold()`.

Accents, diacritics, and lexical content are preserved.

### 2. Lexical matching before timing comparison

Manual, MFA, and WebMAUS words are matched using:

- normalized lexical identity;
- sequence order.

**Timing information is not used to establish lexical correspondence.**

The complete manual word sequence must occur exactly once in the MFA and WebMAUS word sequences. If a unique match cannot be found, the program raises an error instead of silently forcing a correspondence.

### 3. Canonical word-level dataset

After lexical matching has been verified, the project creates one row per matched word.

The canonical table contains metadata and boundary times such as:

```text
filename
file_id
annotator
gender
recording_location
word_index
word
manual_start
manual_end
mfa_start
mfa_end
webmaus_start
webmaus_end
```

The expected canonical dataset contains exactly **3,676 rows from 16 recordings**.

### 4. Boundary-error measures

For each aligner:

```text
signed start error = automatic start - manual start
signed end error   = automatic end   - manual end
```

Errors are converted from seconds to milliseconds.

Absolute start and end errors are also calculated.

For each word:

```text
word MAE = (absolute start error + absolute end error) / 2
```

The project reports descriptive measures including:

- mean absolute error;
- median absolute error;
- start-boundary MAE;
- end-boundary MAE;
- percentage of word edges within 20 ms;
- percentage of word edges within 50 ms;
- percentage of word edges within 100 ms;
- percentage of complete words for which **both** boundaries fall within the same tolerance.

### 5. Recording-level comparison

Word-level errors are aggregated to one MFA and one WebMAUS mean value per recording.

This gives **16 paired recording-level observations**.

The two aligners are compared with a **paired two-sided Wilcoxon signed-rank test**.

The project also reports:

- the mean and median recording-level difference;
- the number of recordings with lower MFA error;
- the number with lower WebMAUS error;
- ties.

### 6. Error inspection

Large errors are summarized at thresholds of:

```text
100 ms
250 ms
500 ms
```

The project also saves the words with the largest word-level errors for each aligner. These observations are retained for inspection; they are **not automatically excluded** from the evaluation.

## Project structure

```text
kinyarwanda-alignment-ap/
│
├── config/
│   └── config.yaml
│
├── data/
│   ├── manual_reference/
│   ├── webmaus/
│   └── derived/
│
├── results/
│   ├── figures/
│   └── tables/
│
├── scripts/
│   └── run_evaluation.py
│
├── src/
│   └── kinyarwanda_alignment/
│       ├── __init__.py
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
│
├── tests/
│   ├── test_config.py
│   ├── test_file_utils.py
│   ├── test_matching.py
│   ├── test_metrics.py
│   └── test_statistics.py
│
├── .gitignore
├── README.md
└── requirements.txt
```

## Module responsibilities

| Module | Responsibility |
| --- | --- |
| `config.py` | Load YAML configuration and resolve project-relative paths |
| `file_utils.py` | Extract filename metadata and normalize word labels |
| `textgrid_io.py` | Load TextGrids and validate/access required tiers |
| `matching.py` | Match word sequences by lexical identity and order |
| `dataset.py` | Build and validate the canonical word-level DataFrame |
| `metrics.py` | Calculate boundary errors, MAE, and tolerance summaries |
| `statistics.py` | Aggregate errors by recording and run the paired comparison |
| `diagnostics.py` | Summarize large errors and identify highest-error words |
| `plots.py` | Create diagnostic evaluation figures |
| `pipeline.py` | Coordinate the complete evaluation workflow |
| `scripts/run_evaluation.py` | Command-line entry point |

## Python environment

The project was developed and tested with:

```text
Python 3.11.8
```

A virtual environment is recommended.

### Create and activate a virtual environment

On macOS/Linux:

```bash
python3.11 -m venv .venv
source .venv/bin/activate
```

### Install dependencies

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

The main external packages used by the analysis include:

- pandas
- NumPy
- SciPy
- PyYAML
- TextGrid
- Matplotlib
- pytest

Exact package versions are recorded in `requirements.txt`.

## Configuration

The main configuration file is:

```text
config/config.yaml
```

The current configuration defines:

```yaml
project_root: .

inputs:
  manual_reference_dir: data/manual_reference
  webmaus_dir: data/webmaus

outputs:
  canonical_csv: data/derived/word_alignment_evaluation.csv
  tables_dir: results/tables
  figures_dir: results/figures

expected:
  evaluation_files: 16
  manual_words: 3676
  annotators:
    - Annotator_1
    - Annotator_2
    - Annotator_3
    - Annotator_4

analysis:
  top_error_words_per_aligner: 10
```

Relative paths are resolved automatically against the project root.

## Running the evaluation

From the repository root:

```bash
python scripts/run_evaluation.py --config config/config.yaml
```

The script is the main entry point for the project.

A successful run prints a summary similar to:

```text
========================================================================
KINYARWANDA ALIGNMENT EVALUATION: COMPLETE
========================================================================
Words: 3,676
Recordings: 16
Canonical CSV: .../data/derived/word_alignment_evaluation.csv
Tables: .../results/tables
Figures: .../results/figures

Interpretation: in-domain validation of the final Storyboard-adapted MFA system.
========================================================================
```

## Running the tests

Run the full test suite from the repository root:

```bash
python -m pytest -q
```

The current suite contains **10 tests** covering:

- filename metadata extraction;
- conservative word normalization;
- contiguous sequence matching;
- rejection of ambiguous sequence matches;
- boundary-error calculations;
- YAML configuration loading and path resolution;
- configuration validation;
- recording-level aggregation.

## Outputs

### Canonical dataset

```text
data/derived/word_alignment_evaluation.csv
```

This file is rebuilt from the TextGrid inputs by the pipeline. The analysis does **not** begin from a previously generated research CSV.

### Result tables

The pipeline writes tables to:

```text
results/tables/
```

including:

```text
overall_edge_summary.csv
word_tolerance_summary.csv
recording_level_summary.csv
recording_level_test.json
large_error_summary.csv
top_error_words.csv
```

### Figures

The pipeline writes figures to:

```text
results/figures/
```

including:

```text
cumulative_word_edge_error.pdf
paired_recording_mae.pdf
```

The first figure shows the cumulative distribution of absolute word-edge errors.

The second shows paired MFA and WebMAUS mean errors for each recording.

## Main results

For the 16-recording evaluation set, the analysis contains **3,676 matched words**.

The overall mean absolute word-boundary error is approximately:

| Aligner | Mean absolute error |
| --- | ---: |
| MFA | 53.82 ms |
| WebMAUS | 96.78 ms |

At the recording level, MFA has the lower mean error in **13 of the 16 recordings**.

Using equal weighting of recordings, the mean recording-level errors are approximately:

| Aligner | Recording-level mean |
| --- | ---: |
| MFA | 53.30 ms |
| WebMAUS | 94.29 ms |

The paired two-sided Wilcoxon signed-rank comparison gives:

```text
W = 8
p < .001
```

These values describe this evaluation dataset and should not be interpreted as a general benchmark for all Kinyarwanda speech or all forced-alignment conditions.

## Interpretation and limitations

This analysis is an **in-domain validation** of the final Storyboard-adapted MFA system.

Important limitations are:

- the 16 evaluation recordings were part of the corpus used during acoustic-model adaptation, so the results do not represent fully unseen-data generalization;
- the four manual annotators worked on different recordings, so this evaluation does not provide an inter-annotator agreement estimate;
- phone-level boundaries are not formally evaluated in this AP pipeline;
- large errors are inspected but not automatically removed;
- conclusions are specific to the data, models, and annotation setup used here.

## Reproducibility safeguards

The project includes several checks intended to prevent silent processing errors:

- the expected number of recordings can be checked from the YAML configuration;
- the expected number of matched words can be checked;
- annotator folder names are validated;
- required TextGrid tiers are checked;
- word sequences must match uniquely;
- lexical correspondence is established before timing comparison;
- missing boundary values are rejected;
- intervals with `start > end` are rejected;
- duplicate `file_id + word_index` rows are rejected;
- word indices must be continuous within each recording;
- filename-derived metadata are checked for missing values;
- automated tests cover key transformations.

## Advanced Python course techniques used

The project applies course concepts where they are useful to the task, including:

- modular functions with clear responsibilities;
- docstrings;
- type hints;
- custom exceptions;
- regular expressions for filename metadata;
- comprehensions;
- iteration over structured data;
- dictionaries and sets;
- YAML configuration files;
- command-line arguments with `argparse`;
- `pathlib.Path` for file handling;
- pandas DataFrames;
- NumPy numerical operations;
- virtual environments and dependency management;
- automated tests with pytest;
- Git/GitHub project organization.

The project does not add unrelated libraries or programming patterns solely to demonstrate them.

## Project context and contribution

This repository was implemented by **Moloud Asakereh** as an AP project for **Advanced Python for NLP at HHU Düsseldorf**.

The underlying forced-alignment study is part of a broader collaborative research project. For the AP, the main contribution is the independent Python implementation and refactoring of the evaluation workflow into a reproducible software structure.

The manual annotators are anonymized in the repository as `Annotator_1` to `Annotator_4`.

## Repository access

The repository may remain private while research data or project materials are access-restricted. If the repository is submitted privately for course assessment, access should be granted to the relevant course instructors.

## Citation and research use

If this repository is reused for research, the underlying data sources, forced-alignment systems, and associated research outputs should be cited as appropriate. This README documents the computational AP implementation; the accompanying written report provides the fuller academic context and references.
