import pandas as pd
import numpy as np
import random
import os
from datetime import datetime, timedelta

random.seed(42)
np.random.seed(42)

# ─── Constants ────────────────────────────────────────────────────────────────
LEGIT_COUNTRIES  = ['IN', 'US', 'UK', 'DE', 'AU', 'CA', 'FR', 'JP']
ATTACK_COUNTRIES = ['RU', 'CN', 'NG', 'BR', 'KP', 'RO', 'UA', 'VN']
MULE_ACCOUNTS    = [f"mule_{i}" for i in range(50)]   # fixed mule pool
PROXY_IPS        = [f"proxy_{i}" for i in range(200)] # residential proxy pool

def generate_user_profiles(n_users=1000):
    return {
        uid: {
            'usual_hour':        random.randint(8, 22),
            'usual_country':     random.choice(LEGIT_COUNTRIES),
            'usual_device':      f"device_{random.randint(1000, 8999)}",
            'usual_ip_prefix':   f"192.168.{random.randint(0,255)}",
            'avg_amount':        random.uniform(100, 5000),
            'avg_delay':         random.randint(300, 3600),
            'account_age_days':  random.randint(30, 1800),
            'usual_typing_wpm':  random.randint(40, 100),
        }
        for uid in range(n_users)
    }


def generate_normal_event(uid, profile, day_offset):
    hour = profile['usual_hour'] + random.randint(-2, 2)
    return {
        'user_id':                       uid,
        'hour':                          max(0, min(23, hour)),
        'day_of_week':                   day_offset % 7,
        'country':                       profile['usual_country'],
        'device_id':                     profile['usual_device'],
        'new_device_flag':               0,
        'new_country_flag':              0,
        'new_payee_flag':                random.choice([0, 0, 0, 1]),
        'failed_attempts_before_success': random.randint(0, 1),
        'time_to_transfer_seconds':      profile['avg_delay'] + random.randint(-60, 60),
        'transaction_amount':            profile['avg_amount'] * random.uniform(0.5, 1.5),
        'avg_user_amount':               profile['avg_amount'],
        'password_changed_flag':         0,
        'vpn_flag':                      0,
        'account_age_days':              profile['account_age_days'],
        'warmup_phase_flag':             0,
        'campaign_flag':                 0,
        'mule_account_flag':             0,
        'typing_speed_anomaly':          0,
        'geo_velocity_kmh':              random.uniform(0, 50),
        'proxy_flag':                    0,
        'receiving_account':             f"legit_{random.randint(1,5000)}",
        'session_duration_seconds':      random.randint(120, 1800),
        'pages_visited':                 random.randint(3, 20),
        'is_fraud':                      0,
        'fraud_type':                    'none'
    }


# ─── Attack Pattern 1: Classic ATO ────────────────────────────────────────────
def generate_classic_ato(uid, profile, day_offset):
    hour = random.choice([0, 1, 2, 3, 22, 23])
    return {
        'user_id':                       uid,
        'hour':                          hour,
        'day_of_week':                   day_offset % 7,
        'country':                       random.choice(ATTACK_COUNTRIES),
        'device_id':                     f"device_{random.randint(9000,9999)}",
        'new_device_flag':               1,
        'new_country_flag':              1,
        'new_payee_flag':                1,
        'failed_attempts_before_success': random.randint(3, 10),
        'time_to_transfer_seconds':      random.randint(10, 120),
        'transaction_amount':            profile['avg_amount'] * random.uniform(4, 10),
        'avg_user_amount':               profile['avg_amount'],
        'password_changed_flag':         1,
        'vpn_flag':                      random.choice([0, 1]),
        'account_age_days':              profile['account_age_days'],
        'warmup_phase_flag':             0,
        'campaign_flag':                 0,
        'mule_account_flag':             1,
        'typing_speed_anomaly':          1,
        'geo_velocity_kmh':              random.uniform(800, 5000),
        'proxy_flag':                    0,
        'receiving_account':             random.choice(MULE_ACCOUNTS),
        'session_duration_seconds':      random.randint(30, 180),
        'pages_visited':                 random.randint(1, 4),
        'is_fraud':                      1,
        'fraud_type':                    'classic_ato'
    }


# ─── Attack Pattern 2: Warmup ATO (sophisticated) ─────────────────────────────
def generate_warmup_ato(uid, profile, day_offset, phase):
    """
    Attacker logs in normally for days 1-3 (warmup),
    then strikes on day 4+
    """
    is_strike = phase == 'strike'

    if not is_strike:
        # Warmup phase — looks almost normal but slight anomalies
        hour = profile['usual_hour'] + random.randint(-1, 1)
        return {
            'user_id':                       uid,
            'hour':                          max(0, min(23, hour)),
            'day_of_week':                   day_offset % 7,
            'country':                       profile['usual_country'],
            'device_id':                     f"device_{random.randint(8000,8999)}",  # slightly new
            'new_device_flag':               1,
            'new_country_flag':              0,
            'new_payee_flag':                0,
            'failed_attempts_before_success': random.randint(0, 2),
            'time_to_transfer_seconds':      profile['avg_delay'],
            'transaction_amount':            profile['avg_amount'] * random.uniform(0.8, 1.2),
            'avg_user_amount':               profile['avg_amount'],
            'password_changed_flag':         0,
            'vpn_flag':                      0,
            'account_age_days':              profile['account_age_days'],
            'warmup_phase_flag':             1,
            'campaign_flag':                 0,
            'mule_account_flag':             0,
            'typing_speed_anomaly':          random.choice([0, 1]),
            'geo_velocity_kmh':              random.uniform(0, 100),
            'proxy_flag':                    1,
            'receiving_account':             f"legit_{random.randint(1,5000)}",
            'session_duration_seconds':      random.randint(60, 300),
            'pages_visited':                 random.randint(2, 8),
            'is_fraud':                      0,  # warmup itself not flagged
            'fraud_type':                    'warmup_phase'
        }
    else:
        # Strike phase
        return {
            'user_id':                       uid,
            'hour':                          random.randint(0, 6),
            'day_of_week':                   day_offset % 7,
            'country':                       random.choice(ATTACK_COUNTRIES),
            'device_id':                     f"device_{random.randint(9000,9999)}",
            'new_device_flag':               1,
            'new_country_flag':              1,
            'new_payee_flag':                1,
            'failed_attempts_before_success': random.randint(1, 4),
            'time_to_transfer_seconds':      random.randint(15, 90),
            'transaction_amount':            profile['avg_amount'] * random.uniform(5, 12),
            'avg_user_amount':               profile['avg_amount'],
            'password_changed_flag':         1,
            'vpn_flag':                      1,
            'account_age_days':              profile['account_age_days'],
            'warmup_phase_flag':             1,  # was in warmup
            'campaign_flag':                 0,
            'mule_account_flag':             1,
            'typing_speed_anomaly':          1,
            'geo_velocity_kmh':              random.uniform(2000, 8000),
            'proxy_flag':                    1,
            'receiving_account':             random.choice(MULE_ACCOUNTS),
            'session_duration_seconds':      random.randint(20, 120),
            'pages_visited':                 random.randint(1, 3),
            'is_fraud':                      1,
            'fraud_type':                    'warmup_ato'
        }


# ─── Attack Pattern 3: Coordinated Campaign ───────────────────────────────────
def generate_campaign_attack(uid, profile, day_offset, campaign_ip):
    """Multiple accounts attacked from same IP/proxy in same hour"""
    return {
        'user_id':                       uid,
        'hour':                          random.randint(1, 4),
        'day_of_week':                   day_offset % 7,
        'country':                       random.choice(ATTACK_COUNTRIES),
        'device_id':                     campaign_ip,   # same device across accounts
        'new_device_flag':               1,
        'new_country_flag':              1,
        'new_payee_flag':                1,
        'failed_attempts_before_success': random.randint(2, 6),
        'time_to_transfer_seconds':      random.randint(20, 150),
        'transaction_amount':            profile['avg_amount'] * random.uniform(3, 8),
        'avg_user_amount':               profile['avg_amount'],
        'password_changed_flag':         random.choice([0, 1]),
        'vpn_flag':                      1,
        'account_age_days':              profile['account_age_days'],
        'warmup_phase_flag':             0,
        'campaign_flag':                 1,
        'mule_account_flag':             1,
        'typing_speed_anomaly':          1,
        'geo_velocity_kmh':              random.uniform(1000, 6000),
        'proxy_flag':                    1,
        'receiving_account':             random.choice(MULE_ACCOUNTS[:10]),  # concentrated mules
        'session_duration_seconds':      random.randint(15, 90),
        'pages_visited':                 random.randint(1, 3),
        'is_fraud':                      1,
        'fraud_type':                    'campaign'
    }


# ─── Attack Pattern 4: Residential Proxy (hard to detect) ────────────────────
def generate_proxy_attack(uid, profile, day_offset):
    """
    Attacker uses residential proxy — looks like legit country/device.
    Hardest to detect — only behavioral signals give it away.
    """
    hour = profile['usual_hour'] + random.randint(-3, 3)
    return {
        'user_id':                       uid,
        'hour':                          max(0, min(23, hour)),
        'day_of_week':                   day_offset % 7,
        'country':                       profile['usual_country'],  # looks legit!
        'device_id':                     random.choice(PROXY_IPS),
        'new_device_flag':               1,
        'new_country_flag':              0,                          # looks legit!
        'new_payee_flag':                1,
        'failed_attempts_before_success': random.randint(1, 3),
        'time_to_transfer_seconds':      random.randint(60, 300),   # not too fast
        'transaction_amount':            profile['avg_amount'] * random.uniform(2, 5),
        'avg_user_amount':               profile['avg_amount'],
        'password_changed_flag':         0,
        'vpn_flag':                      0,                          # proxy, not VPN
        'account_age_days':              profile['account_age_days'],
        'warmup_phase_flag':             0,
        'campaign_flag':                 0,
        'mule_account_flag':             1,
        'typing_speed_anomaly':          1,                          # gives it away
        'geo_velocity_kmh':              random.uniform(0, 80),      # looks legit!
        'proxy_flag':                    1,
        'receiving_account':             random.choice(MULE_ACCOUNTS),
        'session_duration_seconds':      random.randint(60, 400),
        'pages_visited':                 random.randint(2, 6),
        'is_fraud':                      1,
        'fraud_type':                    'proxy_ato'
    }


# ─── Main Generator ───────────────────────────────────────────────────────────
def generate_login_events(n_users=1000, n_days=180, target_events=200000):
    records = []
    profiles = generate_user_profiles(n_users)

    print("🔨 Generating normal events...")
    # Normal events — bulk
    normal_target = int(target_events * 0.94)
    for _ in range(normal_target):
        uid = random.randint(0, n_users - 1)
        day = random.randint(0, n_days)
        records.append(generate_normal_event(uid, profiles[uid], day))

    print("🔨 Generating classic ATO attacks...")
    for _ in range(int(target_events * 0.015)):
        uid = random.randint(0, n_users - 1)
        day = random.randint(0, n_days)
        records.append(generate_classic_ato(uid, profiles[uid], day))

    print("🔨 Generating warmup ATO attacks...")
    for _ in range(int(target_events * 0.015)):
        uid = random.randint(0, n_users - 1)
        day = random.randint(4, n_days)
        # 3 warmup days + 1 strike
        for phase_day in range(3):
            records.append(generate_warmup_ato(uid, profiles[uid], day - 3 + phase_day, 'warmup'))
        records.append(generate_warmup_ato(uid, profiles[uid], day, 'strike'))

    print("🔨 Generating campaign attacks...")
    n_campaigns = 50
    for _ in range(n_campaigns):
        campaign_ip = random.choice(PROXY_IPS)
        campaign_size = random.randint(10, 30)
        day = random.randint(0, n_days)
        for _ in range(campaign_size):
            uid = random.randint(0, n_users - 1)
            records.append(generate_campaign_attack(uid, profiles[uid], day, campaign_ip))

    print("🔨 Generating residential proxy attacks...")
    for _ in range(int(target_events * 0.01)):
        uid = random.randint(0, n_users - 1)
        day = random.randint(0, n_days)
        records.append(generate_proxy_attack(uid, profiles[uid], day))

    df = pd.DataFrame(records)
    df = df.sample(frac=1, random_state=42).reset_index(drop=True)  # shuffle

    print(f"\n✅ Total events: {len(df)}")
    print(f"📊 Fraud breakdown:")
    print(df['fraud_type'].value_counts())
    print(f"\n📊 Overall fraud rate: {df['is_fraud'].mean()*100:.3f}%")

    return df


if __name__ == "__main__":
    os.makedirs("../../dataset/raw", exist_ok=True)

    df = generate_login_events()
    output_path = r"E:\Projects\Fraud-detection-system\dataset\raw\synthetic_logins.csv"
    df.to_csv(output_path, index=False)
    print(f"\n💾 Saved to {output_path}")