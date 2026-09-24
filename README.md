# Simplified AP code package

This version is intentionally presentation-friendly.

The computational story has five stages:

1. validate the 16 Manual and WebMAUS files;
2. match Manual, MFA and WebMAUS words using lexical identity + order;
3. build the 3,676-row canonical evaluation table;
4. calculate understandable boundary-error measures;
5. compare the two aligners at recording level and inspect the largest errors.

Run:

```bash
python -m pytest -q
python scripts/run_evaluation.py --config config/config.yaml
```

The project rebuilds `data/derived/word_alignment_evaluation.csv` from the
TextGrids. It does not start from the previously generated research CSV.
