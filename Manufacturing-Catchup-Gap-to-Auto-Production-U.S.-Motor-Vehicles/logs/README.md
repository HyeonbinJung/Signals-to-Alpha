# Execution evidence

- `analysis.log`: `OPENBLAS_NUM_THREADS=1 python run_analysis.py` full 1,000 block reorders, 2,000 bootstraps, 1,000 exposure perturbations, OOS robustness.
- `unit_tests.log`: `PYTHONPATH=. OPENBLAS_NUM_THREADS=1 python -m pytest -q tests`.
- `notebook.log`: `jupyter nbconvert --to notebook --execute --inplace research.ipynb`.
- `clean_*`: fresh copied study directory reproduction and checksums. Structural repository validator must be run against the complete GitHub repository, not this study folder alone.
