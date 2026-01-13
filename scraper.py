import json, requests, pandas as pd, pytz
from datetime import datetime

tw_tz = pytz.timezone('Asia/Taipei')
now = datetime.now(tw_tz)
now_str = now.strftime("%Y-%m-%d %H:%M:%S")

# 判斷交易時段
is_closed = now.hour > 14 or (now.hour == 14 and now.minute >= 30)

try:
    # 強化：加入 Browser 偽裝標頭 (User-Agent)
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    # 增加隨機參數避免快取
    url = f"https://www.twse.com.tw/exchangeReport/MI_INDEX?response=json&type=ALLBUTOTC&_={int(now.timestamp())}"
    
    res = requests.get(url, headers=headers, timeout=15)
    data = res.json()

    # 檢查 TWSE 是否回傳正常數據區塊 (data5 或 data9)
    data_key = 'data5' if 'data5' in data else 'data9' if 'data9' in data else None

    if not data_key:
        raise Exception("目前非交易時段或 API 未回應資料")

    fields_key = data_key.replace('data', 'fields')
    df = pd.DataFrame(data[data_key], columns=data[fields_key])
    
    # 數值清理
    for col in ['收盤價', '開盤價', '漲跌價差']:
        df[col] = pd.to_numeric(df[col].str.replace(',', ''), errors='coerce')
    
    # 計算漲跌幅
    df['漲跌幅'] = ((df['漲跌價差'] / (df['收盤價'] - df['漲跌價差'])) * 100).round(2)
    df = df.dropna(subset=['漲跌幅', '開盤價', '收盤價'])

    gainers = df.sort_values('漲跌幅', ascending=False).head(10)
    losers = df.sort_values('漲跌幅', ascending=True).head(10)

    res_data = {
        "update_time": now_str,
        "is_closed": is_closed,
        "gainers": gainers[['證券代號', '證券名稱', '開盤價', '收盤價', '漲跌幅']].to_dict('records'),
        "losers": losers[['證券代號', '證券名稱', '開盤價', '收盤價', '漲跌幅']].to_dict('records')
    }
except Exception as e:
    print(f"抓取失敗原因: {e}")
    # 保留模擬數據作為最後防線
    res_data = {
        "update_time": now_str + " (模擬數據 - 證交所連線忙碌)",
        "is_closed": False,
        "gainers": [{"證券代號":"2330","證券名稱":"台積電","開盤價":1000.00,"收盤價":1025.00,"漲跌幅":2.50}],
        "losers": [{"證券代號":"0050","證券名稱":"元大台灣50","開盤價":150.00,"收盤價":148.50,"漲跌幅":-1.00}]
    }

with open('data.json', 'w', encoding='utf-8') as f:
    json.dump(res_data, f, ensure_ascii=False, indent=2)
