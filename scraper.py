import json, requests, pandas as pd, pytz
from datetime import datetime

tw_tz = pytz.timezone('Asia/Taipei')
now_str = datetime.now(tw_tz).strftime("%Y-%m-%d %H:%M:%S")

try:
    # 抓取證交所資料
    url = "https://www.twse.com.tw/exchangeReport/MI_INDEX?response=json&type=ALLBUTOTC"
    res = requests.get(url, timeout=10)
    data = res.json()

    if 'data5' not in data:
        raise Exception("今日數據尚未產生")

    df = pd.DataFrame(data['data5'], columns=data['fields5'])
    df['收盤價'] = pd.to_numeric(df['收盤價'].str.replace(',', ''), errors='coerce')
    df['開盤價'] = pd.to_numeric(df['開盤價'].str.replace(',', ''), errors='coerce')
    df['漲跌價差'] = pd.to_numeric(df['漲跌價差'].str.replace(',', ''), errors='coerce')
    
    # 計算漲跌幅
    df['漲跌幅'] = (df['漲跌價差'] / (df['收盤價'] - df['漲跌價差']) * 100).round(2)
    df = df.dropna(subset=['漲跌幅'])

    gainers = df.sort_values('漲跌幅', ascending=False).head(10)
    losers = df.sort_values('漲跌幅', ascending=True).head(10)

    res_data = {
        "update_time": now_str,
        "is_closed": True,
        "gainers": gainers[['證券代號', '證券名稱', '開盤價', '收盤價', '漲跌幅']].to_dict('records'),
        "losers": losers[['證券代號', '證券名稱', '開盤價', '收盤價', '漲跌幅']].to_dict('records')
    }
except Exception as e:
    # 如果失敗，產生模擬數據確保網頁不空白
    print(f"Error: {e}")
    res_data = {
        "update_time": now_str + " (模擬數據)",
        "is_closed": False,
        "gainers": [{"證券代號":"2330","證券名稱":"台積電","開盤價":1000,"收盤價":1025,"漲跌幅":2.5}],
        "losers": [{"證券代號":"0050","證券名稱":"元大台灣50","開盤價":150,"收盤價":148.5,"漲跌幅":-1.0}]
    }

with open('data.json', 'w', encoding='utf-8') as f:
    json.dump(res_data, f, ensure_ascii=False, indent=2)
