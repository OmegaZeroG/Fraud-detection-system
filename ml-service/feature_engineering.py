import pandas as pd
import numpy as np
import os

def load_ieee(transaction_path, identity_path):
    print("📂 Loading IEEE-CIS dataset...")
    txn = pd.read_csv(transaction_path)
    idn = pd.read_csv(identity_path)
    
    # Merge on TransactionID
    df = txn.merge(idn, on="TransactionID", how="left")
    print(f"✅ IEEE-CIS loaded: {len(df)} rows")
    return df


def load_synthetic(synthetic_path):
    print("📂 Loading Synthetic Login dataset...")
    df = pd.read_csv(synthetic_path)
    print(f"✅ Synthetic loaded: {len(df)} rows")
    return df


def engineer_ieee_features(df):
    print("⚙️  Engineering IEEE-CIS features...")

    # --- Time features ---
    df['hour'] = (df['TransactionDT'] % 86400) // 3600
    df['day_of_week'] = (df['TransactionDT'] // 86400) % 7
    df['is_odd_hour'] = df['hour'].apply(lambda h: 1 if h < 6 or h >= 22 else 0)

    # --- Amount features ---
    df['amount_log'] = np.log1p(df['TransactionAmt'])
    user_avg = df.groupby('card1')['TransactionAmt'].transform('mean')
    user_std = df.groupby('card1')['TransactionAmt'].transform('std').fillna(1)
    df['amount_z_score'] = (df['TransactionAmt'] - user_avg) / (user_std + 1e-9)

    # --- Device / Identity flags ---
    df['new_device_flag'] = df['DeviceType'].isna().astype(int)
    df['is_mobile'] = (df['DeviceType'] == 'mobile').astype(int)

    # --- Email domain risk ---
    high_risk_domains = ['gmail.com', 'yahoo.com', 'hotmail.com']
    df['risky_email_domain'] = df['P_emaildomain'].apply(
        lambda x: 1 if str(x) in high_risk_domains else 0
    )

    # --- Card mismatch flags ---
    df['card_addr_mismatch'] = (df['card3'] != df['addr1']).astype(int)

    # --- Velocity: transaction count per card ---
    df['card_txn_count'] = df.groupby('card1')['TransactionID'].transform('count')

    # --- Failed attempts proxy (C columns are count features in IEEE) ---
    df['failed_attempts_before_success'] = df['C1'].fillna(0)

    # --- New payee proxy ---
    df['new_payee_flag'] = (df['R_emaildomain'] != df['P_emaildomain']).astype(int)

    # --- Select final features ---
    FEATURES = [
        'hour', 'day_of_week', 'is_odd_hour',
        'amount_log', 'amount_z_score',
        'new_device_flag', 'is_mobile',
        'risky_email_domain', 'card_addr_mismatch',
        'card_txn_count', 'failed_attempts_before_success',
        'new_payee_flag',
        'isFraud'  # label
    ]

    df = df[FEATURES].copy()
    df = df.rename(columns={'isFraud': 'is_fraud'})
    df = df.fillna(0)

    print(f"✅ IEEE features engineered: {df.shape}")
    return df


def engineer_synthetic_features(df):
    print("⚙️  Engineering Synthetic features...")

    # --- Amount z-score per user ---
    user_avg = df.groupby('user_id')['transaction_amount'].transform('mean')
    user_std = df.groupby('user_id')['transaction_amount'].transform('std').fillna(1)
    df['amount_z_score'] = (df['transaction_amount'] - user_avg) / (user_std + 1e-9)
    df['amount_log'] = np.log1p(df['transaction_amount'])

    # --- Suspicious sequence: new device + new payee + fast transfer ---
    df['suspicious_sequence'] = (
        (df['new_device_flag'] == 1) &
        (df['new_payee_flag'] == 1) &
        (df['time_to_transfer_seconds'] < 120)
    ).astype(int)

    # --- Country encoding ---
    df['country_encoded'] = pd.factorize(df['country'])[0]

    # --- Time features ---
    df['is_odd_hour'] = df['hour'].apply(lambda h: 1 if h < 6 or h >= 22 else 0)
    df['day_of_week'] = 0  # synthetic doesn't have date — default 0

    # --- Velocity proxy ---
    df['card_txn_count'] = df.groupby('user_id')['user_id'].transform('count')

    # --- Select final features (must match IEEE columns) ---
    FEATURES = [
        'hour', 'day_of_week', 'is_odd_hour',
        'amount_log', 'amount_z_score',
        'new_device_flag',
        'new_payee_flag', 'failed_attempts_before_success',
        'time_to_transfer_seconds', 'suspicious_sequence',
        'country_encoded', 'password_changed_flag', 'vpn_flag',
        'card_txn_count',
        'is_fraud'
    ]

    # Add missing IEEE columns as 0 so both datasets align
    for col in ['is_mobile', 'risky_email_domain', 'card_addr_mismatch']:
        df[col] = 0

    df = df[FEATURES + ['is_mobile', 'risky_email_domain', 'card_addr_mismatch']].copy()
    df = df.fillna(0)

    print(f"✅ Synthetic features engineered: {df.shape}")
    return df


def merge_datasets(ieee_df, synth_df):
    print("🔗 Merging datasets...")

    # Add missing columns to IEEE (ATO-specific ones)
    for col in ['time_to_transfer_seconds', 'suspicious_sequence',
                'country_encoded', 'password_changed_flag', 'vpn_flag']:
        if col not in ieee_df.columns:
            ieee_df[col] = 0

    # Combine
    combined = pd.concat([ieee_df, synth_df], ignore_index=True)
    combined = combined.fillna(0)

    print(f"✅ Combined dataset: {combined.shape}")
    print(f"📊 Fraud rate: {combined['is_fraud'].mean()*100:.3f}%")
    return combined


def run_pipeline(
    transaction_path=r"E:\Projects\Fraud-detection-system\dataset\raw\train_transaction.csv",
    identity_path=r"E:\Projects\Fraud-detection-system\dataset\raw\train_identity.csv",
    synthetic_path=r"E:\Projects\Fraud-detection-system\dataset\raw\synthetic_logins.csv",
    output_path=r"E:\Projects\Fraud-detection-system\dataset\processed\combined_features.csv"
):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    # Load
    ieee_raw = load_ieee(transaction_path, identity_path)
    synth_raw = load_synthetic(synthetic_path)

    # Engineer
    ieee_features = engineer_ieee_features(ieee_raw)
    synth_features = engineer_synthetic_features(synth_raw)

    # Merge
    final_df = merge_datasets(ieee_features, synth_features)

    # Save
    final_df.to_csv(output_path, index=False)
    print(f"💾 Saved to {output_path}")
    print(final_df.head())
    return final_df


if __name__ == "__main__":
    run_pipeline()