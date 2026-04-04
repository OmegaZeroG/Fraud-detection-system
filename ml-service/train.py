import pandas as pd
import numpy as np
import pickle
import os
import lightgbm as lgb
from sklearn.ensemble import IsolationForest
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    average_precision_score,
    classification_report,
    roc_auc_score,
    confusion_matrix
)
from imblearn.over_sampling import SMOTE
import shap
import warnings
warnings.filterwarnings('ignore')

# ─── Paths ───────────────────────────────────────────────────────────────────
DATA_PATH    = r"E:\Projects\Fraud-detection-system\dataset\processed\combined_features.csv"
MODEL_DIR    = r"E:\Projects\Fraud-detection-system\ml-service\artifacts"
MODEL_PATH   = os.path.join(MODEL_DIR, "model.pkl")

os.makedirs(MODEL_DIR, exist_ok=True)

# ─── Features ────────────────────────────────────────────────────────────────
FEATURES = [
    'hour', 'day_of_week', 'is_odd_hour',
    'amount_log', 'amount_z_score',
    'new_device_flag', 'is_mobile',
    'risky_email_domain', 'card_addr_mismatch',
    'card_txn_count', 'failed_attempts_before_success',
    'new_payee_flag', 'time_to_transfer_seconds',
    'suspicious_sequence', 'country_encoded',
    'password_changed_flag', 'vpn_flag'
]

# ─── 1. Load Data ─────────────────────────────────────────────────────────────
print("📂 Loading combined dataset...")
df = pd.read_csv(DATA_PATH)
df = df.fillna(0)

X = df[FEATURES]
y = df['is_fraud']

print(f"✅ Data loaded: {X.shape}")
print(f"📊 Fraud rate: {y.mean()*100:.3f}%")

# ─── 2. Train / Test Split ────────────────────────────────────────────────────
X_train, X_test, y_train, y_test = train_test_split(
    X, y, stratify=y, test_size=0.2, random_state=42
)
print(f"✅ Train: {X_train.shape} | Test: {X_test.shape}")

# ─── 3. Layer 1 — Isolation Forest (Unsupervised) ────────────────────────────
print("\n🌲 Training Isolation Forest (Layer 1)...")
iso = IsolationForest(
    n_estimators=100,
    contamination=0.034,   # match fraud rate
    random_state=42,
    n_jobs=-1
)
iso.fit(X_train)

# Convert to 0-1 score (higher = more anomalous)
iso_train_score = -iso.decision_function(X_train)
iso_test_score  = -iso.decision_function(X_test)

print("✅ Isolation Forest trained")

# ─── 4. Add ISO score as feature for LightGBM ────────────────────────────────
X_train_aug = X_train.copy()
X_test_aug  = X_test.copy()
X_train_aug['iso_anomaly_score'] = iso_train_score
X_test_aug['iso_anomaly_score']  = iso_test_score

FEATURES_AUG = FEATURES + ['iso_anomaly_score']

# ─── 5. Handle Imbalance with SMOTE ──────────────────────────────────────────
print("\n⚖️  Applying SMOTE to balance classes...")
sm = SMOTE(random_state=42, k_neighbors=5)
X_res, y_res = sm.fit_resample(X_train_aug, y_train)
print(f"✅ After SMOTE — Fraud: {y_res.sum()} | Legit: {(y_res==0).sum()}")

# ─── 6. Layer 2 — LightGBM (Supervised) ──────────────────────────────────────
print("\n🚀 Training LightGBM (Layer 2)...")
lgbm = lgb.LGBMClassifier(
    n_estimators=500,
    learning_rate=0.05,
    max_depth=7,
    num_leaves=63,
    class_weight='balanced',
    subsample=0.8,
    colsample_bytree=0.8,
    random_state=42,
    n_jobs=-1,
    verbose=-1
)
lgbm.fit(
    X_res, y_res,
    eval_set=[(X_test_aug, y_test)],
    callbacks=[lgb.early_stopping(50, verbose=False),
               lgb.log_evaluation(100)]
)
print("✅ LightGBM trained")

# ─── 7. Evaluate ──────────────────────────────────────────────────────────────
print("\n📊 Evaluation Results:")
y_prob = lgbm.predict_proba(X_test_aug)[:, 1]
y_pred = (y_prob >= 0.5).astype(int)

print(f"   AUC-ROC  : {roc_auc_score(y_test, y_prob):.4f}")
print(f"   AUC-PR   : {average_precision_score(y_test, y_prob):.4f}")
print("\n" + classification_report(y_test, y_pred, target_names=['Legit', 'Fraud']))

cm = confusion_matrix(y_test, y_pred)
print(f"   Confusion Matrix:\n{cm}")
print(f"\n   ✅ Caught {cm[1][1]} frauds out of {cm[1][0]+cm[1][1]} total fraud cases")

# ─── 8. SHAP Explainer ────────────────────────────────────────────────────────
print("\n🔍 Building SHAP explainer...")
explainer = shap.TreeExplainer(lgbm)
print("✅ SHAP explainer ready")

# ─── 9. Find Best Threshold ───────────────────────────────────────────────────
print("\n🎯 Finding best threshold...")
thresholds = np.arange(0.1, 0.9, 0.05)
best_thresh = 0.5
best_f1 = 0

from sklearn.metrics import f1_score
for t in thresholds:
    preds = (y_prob >= t).astype(int)
    f1 = f1_score(y_test, preds)
    if f1 > best_f1:
        best_f1 = f1
        best_thresh = t

print(f"✅ Best threshold: {best_thresh:.2f} (F1: {best_f1:.4f})")

# ─── 10. Save Everything ─────────────────────────────────────────────────────
print("\n💾 Saving model bundle...")
bundle = {
    'lgbm': lgbm,
    'iso_forest': iso,
    'explainer': explainer,
    'features': FEATURES,
    'features_aug': FEATURES_AUG,
    'best_threshold': best_thresh,
    'fraud_rate': float(y.mean()),
}
pickle.dump(bundle, open(MODEL_PATH, 'wb'))
print(f"✅ Model saved to {MODEL_PATH}")
print("\n🎉 Training complete! Ready for api.py")