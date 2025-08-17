import akshare as ak
import pandas as pd
import numpy as np
import argparse


# 计算 RSI
def calc_rsi(series, period):
    delta = series.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))


# 周线多头排列过滤（稳定版）
def weekly_filter(symbol, start, end):
    df = ak.stock_zh_a_hist(
        symbol=symbol,
        period="daily",
        start_date=start.replace("-", ""),
        end_date=end.replace("-", ""),
        adjust="qfq",
    )
    if df is None or df.empty:
        print(f"{symbol} 无数据，跳过")
        return False

    df.rename(
        columns={
            "日期": "date",
            "开盘": "open",
            "收盘": "close",
            "最高": "high",
            "最低": "low",
            "成交量": "volume",
        },
        inplace=True,
    )

    df["date"] = pd.to_datetime(df["date"])
    df.set_index("date", inplace=True)

    df_week = df.resample("W").last()
    df_week["MA5"] = df_week["close"].rolling(window=5).mean()
    df_week["MA10"] = df_week["close"].rolling(window=10).mean()
    df_week["MA20"] = df_week["close"].rolling(window=20).mean()

    if len(df_week) < 20:
        return False

    last = df_week.iloc[-1]
    return last["MA5"] > last["MA10"] > last["MA20"]


# 回测函数（稳定版 + 回踩确认 + 日线多头策略）
def backtest(symbols, start, end, initial_cash=1000000):
    cash = initial_cash
    positions = {}
    equity_curve = []

    symbols = [s for s in symbols if weekly_filter(s, start, end)]
    print(f"通过周线多头排列过滤的股票: {symbols}")

    for symbol in symbols:
        print(f"获取 {symbol} 数据...")
        df = ak.stock_zh_a_hist(
            symbol=symbol,
            period="daily",
            start_date=start.replace("-", ""),
            end_date=end.replace("-", ""),
            adjust="qfq",
        )
        if df is None or df.empty:
            print(f"{symbol} 无日线数据，跳过")
            continue

        df.rename(
            columns={
                "日期": "date",
                "开盘": "open",
                "收盘": "close",
                "最高": "high",
                "最低": "low",
                "成交量": "volume",
            },
            inplace=True,
        )

        df["date"] = pd.to_datetime(df["date"])
        df.set_index("date", inplace=True)
        df.sort_index(inplace=True)

        df["MA20"] = df["close"].rolling(window=20).mean()
        df["MA50"] = df["close"].rolling(window=50).mean()
        df["RSI"] = calc_rsi(df["close"], 14)

        for i in range(50, len(df)):
            row = df.iloc[i]
            prev_row = df.iloc[i - 1]

            if (
                row["MA20"] > row["MA50"]
                and row["close"] > row["MA20"]
                and row["RSI"] > 50
                and prev_row["close"] < prev_row["MA20"]
                and row["close"] > row["MA20"]
            ):
                if symbol not in positions:
                    qty = int(cash // (row["close"] * len(symbols)))
                    if qty > 0:
                        cash -= qty * row["close"]
                        positions[symbol] = qty

            elif symbol in positions and row["close"] < row["MA20"]:
                qty = positions.pop(symbol)
                cash += qty * row["close"]

            # 用 iloc 代替 loc，避免 KeyError
            total_value = cash + sum(
                df.iloc[i]["close"] * qty for s, qty in positions.items()
            )
            equity_curve.append({"date": row.name, "equity": total_value})

    eq_df = pd.DataFrame(equity_curve)
    eq_df.to_csv("equity_curve.csv", index=False)
    print("回测完成，资金曲线已保存到 equity_curve.csv")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--symbols", nargs="+", required=True, help="股票代码列表，例如 000001 600519"
    )
    parser.add_argument("--start", required=True, help="回测开始日期 YYYY-MM-DD")
    parser.add_argument("--end", required=True, help="回测结束日期 YYYY-MM-DD")
    parser.add_argument("--initial-cash", type=float, default=1000000, help="初始资金")
    args = parser.parse_args()

    backtest(args.symbols, args.start, args.end, args.initial_cash)
