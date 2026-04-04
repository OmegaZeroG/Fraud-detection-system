import pandas as pd
import numpy as np
import random
import os

random.seed(42)
np.random.seed(42)

def generate_login_events(n_users=500, n_events=50000):
    records = []

    # Each user has a normal behavior profile
    user_profiles = {
        uid: {
            'usual_hour': random.randint(8, 22),
            'usual_country': random.choice(['IN', 'US', 'UK', 'DE', 'AU']),
            'usual_device': f"device_{random.randint(1000, 8999)}",
            'avg_transfer_amount': random.uniform(100, 5000),
            'avg_transfer_delay': random.randint(300, 3600),
        }
        for uid in range(n_users)
    }

    for _ in range(n_events):
        uid = random.randint(0, n_users - 1)
        profile = user_profiles[uid]
        is_fraud = random.random() < 0.02  # 2% fraud rate — realistic ATO rate

        if is_fraud:
            # --- ATO attack pattern ---
            hour = random.choice([0, 1, 2, 3, 22, 23])             # odd hours
            country = random.choice(['RU', 'CN', 'NG', 'BR', 'KP']) # unusual country
            device = f"device_{random.randint(9000, 9999)}"          # new device
            failed_attempts = random.randint(3, 10)                  # brute force attempts
            new_payee_flag = 1                                        # new payee added
            time_to_transfer = random.randint(10, 180)               # very fast transfer
            amount = profile['avg_transfer_amount'] * random.uniform(3, 10)  # large amount
            password_changed = random.choice([0, 1])                 # may change password
            vpn_flag = random.choice([0, 1])                         # may use VPN
        else:
            # --- Normal user behavior ---
            hour = profile['usual_hour'] + random.randint(-2, 2)
            country = profile['usual_country']
            device = profile['usual_device']
            failed_attempts = random.randint(0, 1)
            new_payee_flag = random.choice([0, 0, 0, 1])            # rarely adds new payee
            time_to_transfer = profile['avg_transfer_delay'] + random.randint(-60, 60)
            amount = profile['avg_transfer_amount'] * random.uniform(0.5, 1.5)
            password_changed = 0
            vpn_flag = 0

        records.append({
            'user_id': uid,
            'hour': max(0, min(23, hour)),
            'country': country,
            'device_id': device,
            'new_device_flag': int(device != profile['usual_device']),
            'new_country_flag': int(country != profile['usual_country']),
            'new_payee_flag': new_payee_flag,
            'failed_attempts_before_success': failed_attempts,
            'time_to_transfer_seconds': max(1, time_to_transfer),
            'transaction_amount': round(amount, 2),
            'avg_user_amount': round(profile['avg_transfer_amount'], 2),
            'password_changed_flag': password_changed,
            'vpn_flag': vpn_flag,
            'is_fraud': int(is_fraud)
        })

    return pd.DataFrame(records)


if __name__ == "__main__":
    os.makedirs("../../dataset/raw", exist_ok=True)
    
    df = generate_login_events()
    
    output_path = "../../dataset/raw/synthetic_logins.csv"
    df.to_csv(output_path, index=False)
    
    print(f"✅ Generated {len(df)} records")
    print(f"📊 Fraud rate: {df['is_fraud'].mean()*100:.2f}%")
    print(f"📁 Saved to {output_path}")
    print(df.head())