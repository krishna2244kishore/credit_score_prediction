import json
import pandas as pd
import numpy as np
from collections import defaultdict

# Load data
with open('user-wallet-transactions.json', 'r') as f:
    data = json.load(f)

# Convert to DataFrame
records = []
for tx in data:
    record = {
        'userWallet': tx['userWallet'],
        'action': tx['action'],
        'amount': float(tx['actionData']['amount']),
        'assetSymbol': tx['actionData']['assetSymbol'],
        'assetPriceUSD': float(tx['actionData']['assetPriceUSD']),
        'timestamp': tx['timestamp']
    }
    records.append(record)
df = pd.DataFrame(records)

# Feature engineering per wallet
def compute_features(df):
    features = []
    grouped = df.groupby('userWallet')
    for wallet, group in grouped:
        feat = {'userWallet': wallet}
        feat['n_tx'] = len(group)
        for action in ['deposit', 'borrow', 'repay', 'redeemunderlying', 'liquidationcall']:
            action_df = group[group['action'] == action]
            feat[f'n_{action}'] = len(action_df)
            feat[f'sum_{action}_usd'] = (action_df['amount'] * action_df['assetPriceUSD']).sum()
        # Repay/Borrow ratio
        feat['repay_borrow_ratio'] = (
            feat['sum_repay_usd'] / feat['sum_borrow_usd'] if feat['sum_borrow_usd'] > 0 else 0
        )
        # Borrow/Deposit ratio
        feat['borrow_deposit_ratio'] = (
            feat['sum_borrow_usd'] / feat['sum_deposit_usd'] if feat['sum_deposit_usd'] > 0 else 0
        )
        # Liquidation rate
        feat['liquidation_rate'] = (
            feat['n_liquidationcall'] / feat['n_borrow'] if feat['n_borrow'] > 0 else 0
        )
        # Activity span
        feat['active_days'] = (
            (group['timestamp'].max() - group['timestamp'].min()) / 86400 if len(group) > 1 else 0
        )
        # Average tx size (USD)
        feat['avg_tx_usd'] = (group['amount'] * group['assetPriceUSD']).mean()
        # Stddev tx size (USD)
        feat['std_tx_usd'] = (group['amount'] * group['assetPriceUSD']).std()
        features.append(feat)
    return pd.DataFrame(features)

features_df = compute_features(df)

# Scoring logic (rule-based, 0-1000)
def score_row(row):
    score = 500
    # Reward more deposits and repays
    score += min(row['n_deposit'] * 5, 100)
    score += min(row['n_repay'] * 10, 100)
    # Penalize liquidations
    score -= min(row['n_liquidationcall'] * 50, 200)
    # Reward high repay/borrow ratio
    score += min(row['repay_borrow_ratio'] * 100, 200)
    # Penalize high borrow/deposit ratio (risk)
    score -= min(row['borrow_deposit_ratio'] * 50, 150)
    # Penalize high liquidation rate
    score -= min(row['liquidation_rate'] * 200, 200)
    # Reward longer activity
    score += min(row['active_days'] * 2, 100)
    # Clamp score
    return int(np.clip(score, 0, 1000))

features_df['credit_score'] = features_df.apply(score_row, axis=1)

# Output
features_df[['userWallet', 'credit_score']].to_csv('wallet_scores.csv', index=False)
print('Scoring complete. Output written to wallet_scores.csv') 