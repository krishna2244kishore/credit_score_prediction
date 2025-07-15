# DeFi Wallet Credit Scoring

This project assigns a credit score (0-1000) to each wallet based on historical transaction behavior on the Aave V2 protocol, using only transaction-level data.

## Method, Architecture, and Processing Flow

### Method Chosen
- The project uses a **rule-based scoring system** to assign credit scores to DeFi wallets.
- The rules are designed to reward responsible, long-term, and safe protocol usage, and penalize risky, bot-like, or exploitative behavior.
- All features are engineered from raw transaction data, with no external data or labels required.

### Architecture Overview
- **Input:** `user-wallet-transactions.json` (raw transaction-level data)
- **Processing:**
  - Feature engineering per wallet (counts, sums, ratios, activity span, etc.)
  - Rule-based scoring logic applied to engineered features
- **Output:** `wallet_scores.csv` (wallet address, credit score)

### Processing Flow
1. **Data Loading:**
   - The script reads the JSON file containing all wallet transactions.
2. **Feature Engineering:**
   - For each wallet, the script computes:
     - Number and sum of each action type (deposit, borrow, repay, etc.)
     - Ratios (repay/borrow, borrow/deposit, liquidation rate)
     - Activity span (days between first and last transaction)
     - Average and standard deviation of transaction size (USD)
3. **Scoring:**
   - The rule-based logic assigns a score to each wallet based on the engineered features (see "Scoring Logic" below).
4. **Output Generation:**
   - The script writes the results to `wallet_scores.csv`, listing each wallet and its credit score.

---

## Features Engineered
- **Total transactions** per wallet
- **Counts and USD sums** for each action: deposit, borrow, repay, redeemunderlying, liquidationcall
- **Repay/Borrow ratio**: Measures repayment discipline
- **Borrow/Deposit ratio**: Indicates risk appetite
- **Liquidation rate**: Fraction of borrows that ended in liquidation
- **Activity span**: Days between first and last transaction
- **Average and stddev of transaction size (USD)**

## Scoring Logic
- **Base score:** 500
- **+5** per deposit (max +100)
- **+10** per repay (max +100)
- **-50** per liquidation (max -200)
- **+100 × repay/borrow ratio** (max +200)
- **-50 × borrow/deposit ratio** (max -150)
- **-200 × liquidation rate** (max -200)
- **+2 per active day** (max +100)
- **Score is clamped between 0 and 1000**

### Scoring Logic Explanation

The scoring system is designed to reward responsible and reliable DeFi behavior, while penalizing risky or exploitative actions. Here is how the score is determined in simple terms:

- Every wallet starts with a base score of 500.
- Making deposits and repaying borrowed funds increases the score, as these actions show responsible participation.
- Each deposit adds 5 points (up to 100 points total), and each repayment adds 10 points (up to 100 points total).
- If a wallet is liquidated (meaning it failed to maintain healthy collateral), it loses 50 points per liquidation (up to 200 points lost). This is a strong signal of risky or poor management.
- Wallets that repay a high proportion of what they borrow get a bonus (up to 200 points), showing good repayment discipline.
- Wallets that borrow much more than they deposit are penalized (up to 150 points lost), as this can indicate risky leverage.
- If a wallet is frequently liquidated compared to how often it borrows, it is penalized further (up to 200 points lost).
- Wallets that are active over a longer period (more days between first and last transaction) get a small bonus (2 points per day, up to 100 points), as this suggests consistent, non-bot-like behavior.
- The final score is always kept between 0 and 1000.

In summary, high scores mean the wallet is reliable, repays what it borrows, avoids liquidation, and participates over time. Low scores mean the wallet is risky, often liquidated, or shows signs of exploitative or bot-like activity.

### Rationale
- More deposits and repays = responsible usage
- More liquidations, high borrow/deposit = risky
- High repay/borrow = good discipline
- Longer activity = reliability

## How to Use
1. Place `user-wallet-transactions.json` in the project directory.
2. Run:
   ```bash
   python score_wallets.py
   ```
3. Output: `wallet_scores.csv` (wallet address, credit score)
