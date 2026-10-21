# Verification record

Evidence behind Section 7.2.7 (Reproducibility) of the report. Everything here
was produced on 21 October 2026 from a fresh clone of the application
repository at commit `3800cc143f3a7d35ca668f6d220b96d19a49ca65`
(<https://github.com/Aarjav-333/fraud-detection-graphml/commit/3800cc1>).

## What was run

| Step | Script | Output |
|---|---|---|
| Seed an empty database from `backend/data/raw/` and run cleaning, rules, graph analysis, features, classical models, alerts and rings, timing each stage | `scripts/run_pipeline.py` | `results/run_A_sklearn152_pipeline.json`, `results/run_B_latest_pipeline.json` |
| Isolation Forest with `contamination=y.mean()` (as committed) versus `y_train.mean()` (training-only) on the same split | `scripts/iso_compare.py` | `results/run_*_isolation_forest_contamination.json` |
| Recompute the synthetic GNN split exactly as `app/ml/gnn.py` does (numpy only) | `scripts/gnn_split_check.py` | `results/gnn_split_check.json` |
| XGBoost across releases 2.0.3–3.2.0 and tree methods | `scripts/xgb_version_check.py`, `scripts/xgb_tree_methods.py` | `results/xgboost_reproduction.txt` |
| Test suite (`pytest -q -rs`) | — | `results/pytest_3800cc1.txt` |

Run A used scikit-learn 1.5.2 / XGBoost 2.1.4 / pandas 2.2.3 / NumPy 2.0.2 /
SciPy 1.14.1 / NetworkX 3.4.2; run B used the then-current releases. Full
package lists are in `environment/`. Both ran on Python 3.11.17, Linux, 4 vCPU,
no GPU (`environment/platform.txt`).

## Findings

- Rule engine, Random Forest (run A), Isolation Forest, fraud rings, dataset
  populations, classical split and GNN split identifier `4f01af3d7815646e`
  reproduce the report exactly.
- XGBoost gives F1 0.831 (report: 0.825) under every release tried; the cause
  could not be established.
- `contamination=y.mean()` and `y_train.mean()` give identical predictions
  (confusion matrix 654 / 185 / 182 / 229). The application repository still
  uses `y.mean()` at every commit, including `3800cc1`.
- GCN / GraphSAGE results were **not** re-run: PyTorch could not be installed
  in the verification container (its package host was blocked by the network
  policy). Their figures rest on the author's local result files.
- Pipeline wall-clock time: 18.7 s (run A) and 16.9 s (run B), single runs.

## Re-running

From a clone of the application repository at `3800cc1`, in `backend/`, with
the requirements installed and `APP_ENV=development`:

```bash
cp /path/to/verification/scripts/run_pipeline.py .
python run_pipeline.py out.json             # seeds ./fraud_detection.db first
python /path/to/verification/scripts/iso_compare.py data/processed/features.csv iso.json
python /path/to/verification/scripts/gnn_split_check.py data/processed/features.csv split.json
```

`run_pipeline.py` re-seeds the database it finds, so run it in a scratch
checkout, never against a working database.
