import pandas as pd

IFRS_SCHEMA = {
    "date": "Transaction Date",
    "description": "Description",
    "debit_account": "Debit Account",
    "credit_account": "Credit Account",
    "amount": "Amount"
}

def validate_schema(df):
    return set(IFRS_SCHEMA.keys()).issubset(df.columns)

def map_schema(df, mapping):
    df = df.rename(columns=mapping)
    df = df[list(IFRS_SCHEMA.keys())]
    df["date"] = pd.to_datetime(df["date"])
    df["amount"] = df["amount"].astype(float)
    return df
