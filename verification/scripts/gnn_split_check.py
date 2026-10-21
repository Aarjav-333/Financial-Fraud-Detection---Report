"""Recompute the synthetic GNN split exactly as app/ml/gnn.py does (numpy only)."""
import hashlib, json, sys, numpy as np, pandas as pd
df = pd.read_csv(sys.argv[1]); y = df["is_fraud"].to_numpy(dtype=np.int64)
rng = np.random.default_rng(42); idx = np.arange(len(y)); test = []
for label in (0, 1):
    li = rng.permutation(idx[y == label]); test.append(li[: int(len(li) * 0.25)])
test_idx = np.concatenate(test); mask = np.zeros(len(y), bool); mask[test_idx] = True
train_idx = np.where(~mask)[0]
rng2 = np.random.default_rng(43); val = []
for label in (0, 1):
    nodes = train_idx[y[train_idx] == label]; val.append(rng2.permutation(nodes)[: int(round(len(nodes) * 0.15))])
val_idx = np.sort(np.concatenate(val)); tr = np.setdiff1d(train_idx, val_idx)
out = {"train": len(tr), "validation": len(val_idx), "test": len(test_idx),
       "test_positives": int(y[test_idx].sum()), "test_negatives": int(len(test_idx) - y[test_idx].sum()),
       "test_split_id": hashlib.sha256(np.sort(test_idx.astype(np.int64)).tobytes()).hexdigest()[:16]}
print(json.dumps(out)); json.dump(out, open(sys.argv[2], "w"), indent=2)
