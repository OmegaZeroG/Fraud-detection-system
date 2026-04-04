from fastapi import APIRouter, HTTPException
from app.schemas.predict import PredictRequest
from app.models.transaction import PredictResponse, ShapFactor
from app.core.model_loader import (
    lgbm, iso_forest, explainer,
    FEATURES, FEATURES_AUG, BEST_THRESHOLD
)
import numpy as np

router = APIRouter()

@router.post("/predict", response_model=PredictResponse)
def predict(request: PredictRequest):
    try:
        f = request.features

        feature_vector = [
            f.hour, f.day_of_week, f.is_odd_hour,
            f.amount_log, f.amount_z_score,
            f.new_device_flag, f.is_mobile,
            f.risky_email_domain, f.card_addr_mismatch,
            f.card_txn_count, f.failed_attempts_before_success,
            f.new_payee_flag, f.time_to_transfer_seconds,
            f.suspicious_sequence, f.country_encoded,
            f.password_changed_flag, f.vpn_flag
        ]

        X_base = np.array([feature_vector])

        # Layer 1 — Isolation Forest
        iso_score = float(-iso_forest.decision_function(X_base)[0])

        # Augment
        X_aug = np.append(X_base, [[iso_score]], axis=1)

        # Layer 2 — LightGBM
        fraud_prob = float(lgbm.predict_proba(X_aug)[0][1])

        # Risk level
        if fraud_prob >= BEST_THRESHOLD:
            risk_level = "HIGH"
            is_fraud = True
        elif fraud_prob >= BEST_THRESHOLD * 0.5:
            risk_level = "MEDIUM"
            is_fraud = False
        else:
            risk_level = "LOW"
            is_fraud = False

        # SHAP
        shap_values = explainer.shap_values(X_aug)
        sv = shap_values[1][0] if isinstance(shap_values, list) else shap_values[0]

        shap_factors = sorted(
            zip(FEATURES_AUG, sv.tolist()),
            key=lambda x: abs(x[1]),
            reverse=True
        )[:5]

        return PredictResponse(
            fraud_probability=round(fraud_prob, 4),
            iso_anomaly_score=round(iso_score, 4),
            risk_level=risk_level,
            is_fraud=is_fraud,
            threshold_used=BEST_THRESHOLD,
            shap_factors=[
                ShapFactor(feature=name, impact=round(val, 4))
                for name, val in shap_factors
            ]
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))