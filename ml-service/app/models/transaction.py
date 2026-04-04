from pydantic import BaseModel
from typing import List

class ShapFactor(BaseModel):
    feature: str
    impact: float

class PredictResponse(BaseModel):
    fraud_probability: float
    iso_anomaly_score: float
    risk_level: str        # LOW / MEDIUM / HIGH
    is_fraud: bool
    threshold_used: float
    shap_factors: List[ShapFactor]