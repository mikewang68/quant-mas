import akshare as ak

# 获取所有沪深指数的实时行情，其中包含指数名称和代码
# df_all_index = ak.stock_zh_index_spot()
df = ak.stock_zh_index_spot_em(symbol="沪深重要指数")
print(df)

df_index = ak.index_zh_a_hist(
    symbol="000016", period="daily", start_date="19900101", end_date="20250829"
)
print(df_index)
