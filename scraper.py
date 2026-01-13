import json, requests, pandas as pd, pytz
from datetime import datetime

tw_tz = pytz.timezone('Asia/Taipei')
now = datetime.now(tw_tz)
now_str = now.strftime("%Y-%m-%d %H:%M:%S")

# 判斷交易時段 (09:00 - 14:30)
is_closed = now.hour > 14 or (now.hour == 14 and now.minute >= 30)

try:
    url = "https://www.twse.com.tw/exchangeReport/MI_INDEX?response=json&type=ALLBUTOTC"
    res = requests.get(url, timeout=10)
    data = res.json()

    df = pd.DataFrame(data['data5'], columns=data['fields5'])
    # 數值清理：處理逗號並轉為數字
    for col in ['收盤價', '開盤價', '漲跌價差']:
        df[col] = pd.to_numeric(df[col].str.replace(',', ''), errors='coerce')
    
    # 計算漲跌幅，強制保留兩位小數
    df['漲跌幅'] = ((df['漲跌價差'] / (df['收盤價'] - df['漲跌價差'])) * 100).round(2)
    df = df.dropna(subset=['漲跌幅'])

    # 取得前十名與後十名
    gainers = df.sort_values('漲跌幅', ascending=False).head(10)
    losers = df.sort_values('漲跌幅', ascending=True).head(10)

    res_data = {
        "update_time": now_str,
        "is_closed": is_closed,
        "gainers": gainers[['證券代號', '證券名稱', '開盤價', '收盤價', '漲跌幅']].to_dict('records'),
        "losers": losers[['證券代號', '證券名稱', '開盤價', '收盤價', '漲跌幅']].to_dict('records')
    }
except Exception as e:
    # 備援模擬數據：確保格式與上方一致
    res_data = {
        "update_time": now_str + " (模擬數據)",
        "is_closed": False,
        "gainers": [{"證券代號":"2330","證券名稱":"台積電","開盤價":1000.00,"收盤價":1025.55,"漲跌幅":2.56}],
        "losers": [{"證券代號":"0050","證券名稱":"元大台灣50","開盤價":150.00,"收盤價":148.45,"漲跌幅":-1.03}]
    }

with open('data.json', 'w', encoding='utf-8') as f:
    json.dump(res_data, f, ensure_ascii=False, indent=2)
