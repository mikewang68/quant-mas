# akshare_hs300_weekly_backtest.py
import akshare as ak
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime

START_DATE = "20140101"
END_DATE = "20250811"
MAX_HOLD = 20
INITIAL_CAPITAL = 1_000_000
FEE_RATE = 0.0003
SLIPPAGE_RATE = 0.0002


def get_stock_list():
    # 从本地hs300_list.txt读取股票代码
    with open("hs300_list.txt", "r") as f:
        stocks = [line.strip() for line in f.readlines()]
    # 转换成akshare需要的格式：尾部加 .SZ 或 .SH
    ak_stocks = []
    for code in stocks:
        if code.startswith("6"):
            ak_stocks.append(code)
        else:
            ak_stocks.append(code)
    return ak_stocks[:100]  # 只取前100只


def get_weekly_data(stock_code):
    try:
        df = ak.stock_zh_a_hist(
            symbol=stock_code,
            period="weekly",
            start_date=START_DATE,
            end_date=END_DATE,
            adjust="qfq",
        )
        df.rename(
            columns={
                "日期": "trade_date",
                "开盘": "open",
                "收盘": "close",
                "最高": "high",
                "最低": "low",
                "成交量": "vol",
            },
            inplace=True,
        )
        df["trade_date"] = pd.to_datetime(df["trade_date"])
        df.set_index("trade_date", inplace=True)
        df.sort_index(inplace=True)
        return df[["open", "high", "low", "close", "vol"]]
    except Exception as e:
        print(f"获取{stock_code}数据失败：{e}")
        return None


# 各类指标计算（MA, MACD, KDJ, RSI）同之前略，以下直接写出即可
def calc_ma(df, window):
    return df["close"].rolling(window=window).mean()


def calc_macd(df, fast=12, slow=26, signal=9):
    ema_fast = df["close"].ewm(span=fast, adjust=False).mean()
    ema_slow = df["close"].ewm(span=slow, adjust=False).mean()
    dif = ema_fast - ema_slow
    dea = dif.ewm(span=signal, adjust=False).mean()
    macd = 2 * (dif - dea)
    return dif, dea, macd


def calc_kdj(df, n=9, k_period=3, d_period=3):
    low_list = df["low"].rolling(n).min()
    high_list = df["high"].rolling(n).max()
    rsv = (df["close"] - low_list) / (high_list - low_list) * 100
    k = rsv.ewm(com=k_period - 1, adjust=False).mean()
    d = k.ewm(com=d_period - 1, adjust=False).mean()
    j = 3 * k - 2 * d
    return k, d, j


def calc_rsi(df, period=14):
    delta = df["close"].diff()
    up = delta.clip(lower=0)
    down = -1 * delta.clip(upper=0)
    ma_up = up.rolling(window=period).mean()
    ma_down = down.rolling(window=period).mean()
    rsi = 100 * ma_up / (ma_up + ma_down)
    return rsi


def strategy_trend_follow(df):
    df = df.copy()
    df["ma5"] = calc_ma(df, 5)
    df["ma10"] = calc_ma(df, 10)
    df["ma20"] = calc_ma(df, 20)
    df["dif"], df["dea"], df["macd"] = calc_macd(df)
    df["ma5_ma10_cross"] = (df["ma5"] > df["ma10"]) & (
        df["ma5"].shift(1) <= df["ma10"].shift(1)
    )
    df["macd_cross"] = (df["dif"] > df["dea"]) & (
        df["dif"].shift(1) <= df["dea"].shift(1)
    )
    df["close_break_high20"] = df["close"] > df["close"].rolling(20).max().shift(1)
    df["buy_signal"] = (
        df["ma5_ma10_cross"] & df["macd_cross"] & df["close_break_high20"]
    )
    df["sell_signal"] = df["close"] < df["ma10"]
    return df[["buy_signal", "sell_signal"]]


def strategy_pullback(df):
    df = df.copy()
    df["ma20"] = calc_ma(df, 20)
    df["k"], df["d"], df["j"] = calc_kdj(df)
    df["rsi"] = calc_rsi(df)
    df["ma20_up"] = df["ma20"] > df["ma20"].shift(1)
    df["oversold"] = (df["j"] < 20) | (df["rsi"] < 30)
    df["close_above_ma20"] = df["close"] > df["ma20"]
    df["buy_signal"] = df["ma20_up"] & df["oversold"] & df["close_above_ma20"]
    df["sell_signal"] = df["close"] < df["ma20"]
    return df[["buy_signal", "sell_signal"]]


def strategy_volume_breakout(df):
    df = df.copy()
    df["vol_avg8"] = df["vol"].rolling(8).mean()
    df["ma20_high"] = df["close"].rolling(20).max()
    df["dif"], df["dea"], df["macd"] = calc_macd(df)
    df["buy_signal"] = (
        (df["close"] > df["ma20_high"].shift(1))
        & (df["vol"] > 1.5 * df["vol_avg8"])
        & (df["dif"] > 0)
    )
    df["sell_signal"] = df["close"] < df["close"].shift(1)
    return df[["buy_signal", "sell_signal"]]


def backtest(stock_list, strategy_func):
    capital = INITIAL_CAPITAL
    position = {}
    capital_hist = []
    dates = []
    holding_max = MAX_HOLD

    data_cache = {}
    for stock in stock_list:
        df = get_weekly_data(stock)
        if df is not None and not df.empty:
            data_cache[stock] = df

    if len(data_cache) == 0:
        print("无数据，回测停止")
        return None
    common_dates = sorted(
        set.intersection(*[set(df.index) for df in data_cache.values()])
    )

    for date in common_dates:
        dates.append(date)
        total_value = capital + sum(
            [
                data_cache[s].loc[date]["close"] * position[s]
                if s in position and date in data_cache[s].index
                else 0
                for s in position
            ]
        )
        capital_hist.append(total_value)

        for stock in stock_list:
            df = data_cache.get(stock)
            if df is None or date not in df.index:
                continue
            signals = strategy_func(df.loc[:date])
            if signals is None or date not in signals.index:
                continue
            buy = signals.loc[date]["buy_signal"]
            sell = signals.loc[date]["sell_signal"]
            price = df.loc[date]["close"]

            if buy and stock not in position and len(position) < holding_max:
                shares = capital / (holding_max * price)
                cost = shares * price * (1 + FEE_RATE + SLIPPAGE_RATE)
                if capital >= cost:
                    capital -= cost
                    position[stock] = shares

            if sell and stock in position:
                shares = position[stock]
                revenue = shares * price * (1 - FEE_RATE - SLIPPAGE_RATE)
                capital += revenue
                del position[stock]

    last_date = common_dates[-1]
    final_value = capital + sum(
        [
            data_cache[s].loc[last_date]["close"] * position[s]
            if s in position and last_date in data_cache[s].index
            else 0
            for s in position
        ]
    )
    capital_hist[-1] = final_value

    capital_series = pd.Series(capital_hist, index=dates)
    returns = capital_series.pct_change().dropna()
    annual_return = (capital_series[-1] / capital_series[0]) ** (
        52 / len(capital_series)
    ) - 1
    annual_vol = returns.std() * np.sqrt(52)
    sharpe = annual_return / annual_vol if annual_vol != 0 else np.nan
    max_drawdown = (
        (capital_series.cummax() - capital_series) / capital_series.cummax()
    ).max()

    results = {
        "net_value_series": capital_series,
        "annual_return": annual_return,
        "annual_volatility": annual_vol,
        "sharpe_ratio": sharpe,
        "max_drawdown": max_drawdown,
    }
    return results


if __name__ == "__main__":
    stock_list = get_stock_list()
    print(f"读取股票列表，共计 {len(stock_list)} 只")

    print("开始回测策略一（趋势跟随）...")
    res1 = backtest(stock_list, strategy_trend_follow)
    print(
        f"策略一年化收益率: {res1['annual_return']:.2%}, 最大回撤: {res1['max_drawdown']:.2%}"
    )

    print("开始回测策略二（回踩低吸）...")
    res2 = backtest(stock_list, strategy_pullback)
    print(
        f"策略二年化收益率: {res2['annual_return']:.2%}, 最大回撤: {res2['max_drawdown']:.2%}"
    )

    print("开始回测策略三（放量突破）...")
    res3 = backtest(stock_list, strategy_volume_breakout)
    print(
        f"策略三年化收益率: {res3['annual_return']:.2%}, 最大回撤: {res3['max_drawdown']:.2%}"
    )
