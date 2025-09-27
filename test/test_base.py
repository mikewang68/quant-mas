import akshare as ak

stock_info = ak.stock_individual_info_em(symbol="300339")
info_dict = {}
if not stock_info.empty:
    for _, row in stock_info.iterrows():
        info_dict[row["item"]] = row["value"]

print(info_dict)

financial_indicators = ak.stock_financial_abstract_ths(symbol="300339")
print(financial_indicators)
