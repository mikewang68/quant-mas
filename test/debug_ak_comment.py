import akshare as ak
import pandas as pd

df = ak.stock_comment_em()
# df = ak.stock_comment_detail_scrd_focus_em("300339")  #
# df = ak.stock_comment_detail_zlkp_jgcyd_em("300339")
# df = ak.stock_comment_detail_zhpj_lspf_em("300339")
# df = ak.stock_comment_detail_scrd_desire_daily_em("300339")
# df = ak.stock_comment_detail_scrd_desire_em(symbol="300339")

print(df)
