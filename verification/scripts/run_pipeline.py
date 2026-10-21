"""Rerun the detection pipeline at the checked-out application commit, from the
seeded data in backend/data/raw/, and record stage timings and evaluation
figures. Run from backend/ with APP_ENV=development."""
import json
import platform
import sys
import time

import numpy as np

from scripts.init_db import init
from scripts.seed_data import seed
from app.database import SessionLocal
from app.ml import preprocessing, rules, graph_analysis, features, baseline, alerts, fraud_ring
from app.models.transaction import Transaction
from app.models.account import Account
from app.models.rule_hit import RuleHit

init()
seed()
db = SessionLocal()
timings = {}


def stage(name, fn, *a, **kw):
    t0 = time.perf_counter()
    out = fn(*a, **kw)
    timings[name] = round(time.perf_counter() - t0, 2)
    print(f"{name}: {timings[name]} s", flush=True)
    return out


stage("preprocessing_clean", preprocessing.clean, db)
stage("rules", rules.apply_rules, db)
stage("graph_analysis", graph_analysis.analyze, db)
stage("features", features.build_and_save, db)
ml = stage("ml_train", baseline.train_and_score, db)
stage("alerts", alerts.generate, db)
rings_out = stage("rings", fraud_ring.detect, db)
timings["pipeline_total"] = round(sum(timings.values()), 2)

# rule engine against transaction ground truth
flag = db.query(Transaction.status == "suspicious", Transaction.is_fraud).all()
tp = sum(1 for s, f in flag if s and f == 1)
fp = sum(1 for s, f in flag if s and f != 1)
fn_ = sum(1 for s, f in flag if not s and f == 1)
hits = {}
for (r,) in db.query(RuleHit.rule).all():
    hits[r] = hits.get(r, 0) + 1

rings = rings_out.get("rings", [])
members = [m for r in rings for m in r["member_ids"]]
fraud_acc = {u for (u,) in db.query(Account.account_uid).filter(Account.is_fraud == 1)}
sizes = sorted(r["size"] for r in rings)

out = {
    "python": platform.python_version(), "platform": platform.platform(),
    "timings_s": timings,
    "rule_engine": {"flagged": tp + fp, "tp": tp, "fp": fp, "fn": fn_,
                    "precision": round(tp / (tp + fp), 4), "recall": round(tp / (tp + fn_), 4),
                    "rule_hits_total": sum(hits.values()), "hits_per_rule": hits},
    "baseline": ml,
    "rings": {"count": len(rings), "members": len(members),
              "fraud_members": sum(1 for u in members if u in fraud_acc),
              "purity": round(sum(1 for u in members if u in fraud_acc) / max(len(members), 1), 4),
              "size_min": sizes[0] if sizes else None, "size_max": sizes[-1] if sizes else None,
              "size_median": float(np.median(sizes)) if sizes else None,
              "high_risk": sum(1 for r in rings if r.get("risk") == "High")},
}
json.dump(out, open(sys.argv[1], "w"), indent=2, default=str)
print(json.dumps(out, indent=2, default=str))
