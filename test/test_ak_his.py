import akshare as ak

stock_zh_a_hist_df = ak.stock_zh_a_hist(
    symbol="000021", period="daily", start_date="20250101", adjust="qfq"
)
print(stock_zh_a_hist_df)
