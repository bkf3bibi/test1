import json, requests, pandas as pd, pytz
from datetime import datetime

tw_tz = pytz.timezone('Asia/Taipei')
now = datetime.now(tw_tz)
now_str = now.strftime("%Y-%m-%d %H:%M:%S")

# 判斷是否為收盤時間 (14:30 後)
is_closed = now.hour > 14 or (now.hour == 14 and now.minute >= 30)

try:
    # 抓取證交所全部個股行情
    url = "https://www.twse.com.tw/exchangeReport/MI_INDEX?response=json&type=ALLBUTOTC"
    res = requests.get(url)
    data = res.json()

    if 'data5' not in data:
        raise Exception("證交所目前未提供資料")

    # 欄位定義：[證券代號, 證券名稱, 成交股數, 成交筆數, 成交金額, 開盤價, 最高價, 最低價, 收盤價, 漲跌(+/-), 漲跌價差...]
    df = pd.DataFrame(data['data5'], columns=data['fields5'])
    
    # 數值轉換
    for col in ['開盤價', '收盤價', '漲跌價差']:
        df[col] = pd.to_numeric(df[col].str.replace(',', ''), errors='coerce')
    
    # 計算漲跌幅 (收盤價 - 開盤價 / 開盤價)
    df['漲跌幅'] = ((df['收盤價'] - (df['收盤價'] - df['漲跌價差'])) / (df['收盤價'] - df['漲跌價差']) * 100).round(2)
    df = df.dropna(subset=['漲跌幅'])

    # 排序上漲與下跌
    gainers = df.sort_values('漲跌幅', ascending=False).head(10)
    losers = df.sort_values('漲跌幅', ascending=True).head(10)

    def format_list(target_df):
        return target_df[['證券代號', '證券名稱', '開盤價', '收盤價', '漲跌價差', '漲跌幅']].to_dict('records')

    res_data = {
        "update_time": now_str,
        "is_closed": is_closed,
        "gainers": format_list(gainers),
        "losers": format_list(losers)
    }

except Exception as e:
    res_data = {"error": str(e), "update_time": now_str}

with open('data.json', 'w', encoding='utf-8') as f:
    json.dump(res_data, f, ensure_ascii=False, indent=2)
