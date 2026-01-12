import pandas as pd

def generate_ledger(df):
    debit = df[["date", "description", "debit_account", "amount"]].copy()
    debit.columns = ["date", "description", "account", "debit"]
    debit["credit"] = 0.0

    credit = df[["date", "description", "credit_account", "amount"]].copy()
    credit.columns = ["date", "description", "account", "credit"]
    credit["debit"] = 0.0


    ledger = pd.concat([debit, credit], ignore_index=True)

    ledger = (
        ledger
        .groupby(["date", "description", "account"], as_index=False)
        .sum()
        .sort_values("date")
    )

    return ledger


def trial_balance(ledger):
    tb = (
        ledger
        .groupby("account", as_index=False)[["debit", "credit"]]
        .sum()
    )
    tb["balance"] = tb["debit"] - tb["credit"]
    return tb
