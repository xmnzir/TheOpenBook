import matplotlib.pyplot as plt

def revenue_expense_chart(revenue, expenses):
    fig, ax = plt.subplots()
    revenue.plot(ax=ax, label="Revenue")
    expenses.plot(ax=ax, label="Expenses")
    ax.legend()
    return fig
