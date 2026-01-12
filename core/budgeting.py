import pandas as pd

def create_budget(revenue, expenses):
    return pd.DataFrame({
        "type": ["Revenue", "Expense"],
        "budget": [revenue.mean(), expenses.mean()]
    })

def variance(actual, budget):
    merged = actual.merge(budget, on="type")
    merged["variance"] = merged["amount"] - merged["budget"]
    merged["variance_pct"] = (merged["variance"] / merged["budget"]) * 100
    return merged
