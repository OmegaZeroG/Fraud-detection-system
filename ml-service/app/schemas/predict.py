from pydantic import BaseModel

class TransactionFeatures(BaseModel):
    hour: float = 0
    day_of_week: float = 0
    is_odd_hour: float = 0
    amount_log: float = 0
    amount_z_score: float = 0
    new_device_flag: float = 0
    is_mobile: float = 0
    risky_email_domain: float = 0
    card_addr_mismatch: float = 0
    card_txn_count: float = 1
    failed_attempts_before_success: float = 0
    new_payee_flag: float = 0
    time_to_transfer_seconds: float = 600
    suspicious_sequence: float = 0
    country_encoded: float = 0
    password_changed_flag: float = 0
    vpn_flag: float = 0

class PredictRequest(BaseModel):
    features: TransactionFeatures