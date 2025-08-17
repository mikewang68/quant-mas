import akshare as ak

df = ak.stock_zh_a_hist(
    symbol="000692",
    period="daily",
    start_date="20250701",
    end_date="20250816",
    adjust="qfq",
)
# stock_bid_ask_em_df = ak.stock_bid_ask_em(symbol="000692")
print(df)
