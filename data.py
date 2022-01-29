import time
from datetime import date

import finviz as fv
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import yfinance as yf

YELLOW = "#FEBD18"
RED = "#800000"
GREY = "#363636"

plt.rcParams.update({"font.size": 14})
plt.xticks(rotation=25)


def price_chart(ticker):
    stock = yf.Ticker(ticker)
    hist = stock.history(period="1y", interval="1d")
    df = pd.DataFrame(data=hist, columns=["Close"])
    df.reset_index(inplace=True)

    plt.plot(df["Date"], df["Close"], color=RED)
    plt.title(f"{ticker} Price History")
    plt.savefig(f"{ticker}-price-chart.png", bbox_inches="tight")
    plt.clf()


def bar_plot(df, x, y, color, title, file_name):
    fig = plt.figure(figsize=(5, 4))
    ax = sns.barplot(data=df, x=x, y=y, color=color)
    sns.despine()
    plt.bar_label(ax.containers[0])
    plt.title(title, pad=15)
    plt.savefig(file_name, bbox_inches="tight")
    plt.clf()


def stacked_bar(df, x, y1, y2, color, title, file_name):
    fig, ax = plt.subplots(figsize=(5, 4))

    ax.bar(x, y1, color=color[0], label="Revenue")
    ax.bar(x, y2, color=color[1], bottom=y1, label="Earnings")

    ax.spines["right"].set_visible(False)
    ax.spines["top"].set_visible(False)

    plt.bar_label(ax.containers[1])
    ax.set_title(title, pad=15)
    ax.legend()
    plt.savefig(file_name, bbox_inches="tight")
    plt.close(fig)


def get_news(ticker):
    # format: [date, short, link]
    return fv.get_news(ticker)


def get_profile(ticker):
    stock_info = fv.get_stock(ticker)

    keys = ["Price", "Beta", "Market Cap", "P/E", "P/B", "EPS (ttm)", "ROE", "ROI"]
    return keys, [stock_info[key] for key in keys]


def get_summary(ticker):
    stock = yf.Ticker(ticker)
    return stock.info["longBusinessSummary"]


def get_graphs(ticker):

    # yfinance objects
    stock = yf.Ticker(ticker)
    financial_data = pd.DataFrame(data=stock.financials)
    balance_data = pd.DataFrame(data=stock.balance_sheet)
    cashflow_data = pd.DataFrame(data=stock.cashflow)
    earnings_data = pd.DataFrame(data=stock.earnings)

    years = [date.today().year - i for i in [0, 1, 2, 3]]

    # Financials
    mil = 1_000_000
    def graph_format(l): return [l[i]/mil for i in range(4)]

    gross = graph_format(financial_data.loc["Gross Profit"])
    ebit = graph_format(financial_data.loc["Ebit"])
    debt_short = graph_format(balance_data.loc["Short Long Term Debt"])
    debt_long = graph_format(balance_data.loc["Long Term Debt"])

    revenue = [earnings_data.iloc[i][0] / mil for i in range(4)]
    earnings = [earnings_data.iloc[i][1] / mil for i in range(4)]

    # Derive Free Cash Flows (operating cash - capex)
    operating_cash = cashflow_data.loc["Total Cash From Operating Activities"]
    capital_expend = cashflow_data.loc["Capital Expenditures"]
    fcf = [(x-y) / mil for (x, y) in zip(operating_cash, capital_expend)]

    ### Save charts ###

    # Financial
    price_chart(ticker)
    bar_plot(
        financial_data, years, gross, RED,
        "Gross Profit ($ millions)",
        f"{ticker}-gross-profit.png",
    )
    bar_plot(
        financial_data, years, ebit, RED,
        "EBIT ($ millions)", f"{ticker}-ebit.png"
    )
    # Balance sheet
    bar_plot(
        balance_data, years, debt_short, RED,
        "Short Long Term Debt ($ millions)",
        f"{ticker}-debt_short.png",
    )
    bar_plot(
        balance_data, years, debt_long, RED,
        "Long Term Debt ($ millions)",
        f"{ticker}-debt_long.png",
    )
    # Cashflow
    bar_plot(
        cashflow_data, years, fcf, RED,
        "Free Cash Flow ($ millions)", f"{ticker}-fcf.png",)
    # Earnings data
    stacked_bar(
        earnings_data,
        years,
        revenue,
        earnings,
        (RED, GREY),
        "Revenue/Earnings ($ millions)",
        f"{ticker}-revenue_earnings.png",
    )


def main():
    input('input ticker: ').upper()
    get_graphs()


if __name__ == "__main__":
    main()
