import sys, pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score
from xgboost import XGBClassifier
C=["total_sent","total_received","txn_count_sent","txn_count_received","unique_receivers","unique_senders","avg_sent_amount","avg_received_amount","max_sent_amount","max_received_amount","txn_per_active_day","in_degree","out_degree","degree_centrality","pagerank","in_cycle","community_size"]
df=pd.read_csv(sys.argv[1]); X=df[C].values; y=df["is_fraud"].values
Xtr,Xte,ytr,yte=train_test_split(X,y,test_size=0.25,stratify=y,random_state=42)
p,n=int(ytr.sum()),int(len(ytr)-ytr.sum())
for tm in ("hist","exact","approx"):
    m=XGBClassifier(n_estimators=300,max_depth=6,learning_rate=0.1,scale_pos_weight=n/max(p,1),eval_metric="logloss",random_state=42,n_jobs=-1,tree_method=tm).fit(Xtr,ytr)
    s=m.predict_proba(Xte)[:,1]; pr=(s>=0.5).astype(int)
    print(tm,[round(f(yte,pr),4) for f in (accuracy_score,precision_score,recall_score,f1_score)], round(roc_auc_score(yte,s),4), sorted(zip(m.feature_importances_.round(4),C),reverse=True)[:3])
