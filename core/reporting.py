def profit_and_loss(df):
    df["month"] = df["date"].dt.to_period("M").astype(str)
    revenue = df[df["credit_account"].str.contains("Revenue")].groupby("month")["amount"].sum()
    expenses = df[df["debit_account"].str.contains("Expense")].groupby("month")["amount"].sum()
    return revenue, expenses
