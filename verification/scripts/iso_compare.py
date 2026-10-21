"""Isolation Forest at commit 3800cc1 (contamination=y.mean()) versus the
training-only estimate (contamination=y_train.mean()), same features, split and seed."""
import json, sys, pandas as pd, sklearn
from sklearn.ensemble import IsolationForest
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score, confusion_matrix
C=["total_sent","total_received","txn_count_sent","txn_count_received","unique_receivers","unique_senders","avg_sent_amount","avg_received_amount","max_sent_amount","max_received_amount","txn_per_active_day","in_degree","out_degree","degree_centrality","pagerank","in_cycle","community_size"]
df=pd.read_csv(sys.argv[1]); X=df[C].values; y=df["is_fraud"].values
Xtr,Xte,ytr,yte=train_test_split(X,y,test_size=0.25,stratify=y,random_state=42)
out={"scikit_learn": sklearn.__version__}
for name,c in (("y_mean_as_committed",float(y.mean())),("y_train_mean_corrected",float(ytr.mean()))):
    iso=IsolationForest(n_estimators=200,contamination=c,random_state=42,n_jobs=-1).fit(Xtr)
    pr=(iso.predict(Xte)==-1).astype(int); s=-iso.score_samples(Xte)
    out[name]={"contamination":round(c,6),**{k:round(float(f(yte,pr)),4) for k,f in (("accuracy",accuracy_score),("precision",precision_score),("recall",recall_score),("f1",f1_score))},"roc_auc":round(float(roc_auc_score(yte,s)),4),"confusion_matrix_tn_fp_fn_tp":confusion_matrix(yte,pr).ravel().tolist(),"test_flagged":int(pr.sum())}
out["identical_predictions"]=out["y_mean_as_committed"]["confusion_matrix_tn_fp_fn_tp"]==out["y_train_mean_corrected"]["confusion_matrix_tn_fp_fn_tp"]
print(json.dumps(out,indent=2)); json.dump(out,open(sys.argv[2],"w"),indent=2)
