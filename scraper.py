import json
import requests
import pandas as pd
import pytz
from datetime import datetime

# 設定時區
tw_tz = pytz.timezone('Asia/Taipei')

# 錯誤處理與資料保留
try:
    # 嘗試從 TWSE 抓取資料 (通常只在交易日有數據)
    url = "https://www.twse.com.tw/exchangeReport/MI_INDEX?response=json&type=ALLBUTOTC"
    response = requests.get(url)
    data = response.json()

    # 檢查是否有資料 (TWSE 可能在非交易日返回空資料)
    if not data or 'data5' not in data or not data['data5']:
        raise ValueError("No stock data available from TWSE.")

    # 將資料轉換為 DataFrame 方便處理
    df = pd.DataFrame(data['data5'], columns=data['fields5'])

    # 選擇需要的欄位並轉換為數值
    df = df[['證券代號', '證券名稱', '漲跌(+/-)', '漲跌價差', '最後揭示買價', '最後揭示賣價', '開盤價', '最高價', '最低價', '收盤價', '成交量', '成交金額(元)']]
    
    # 轉換漲跌幅為數值 (可能包含 'X' 代表今日無交易)
    df['漲跌價差'] = pd.to_numeric(df['漲跌價差'], errors='coerce').fillna(0)
    df['收盤價'] = pd.to_numeric(df['收盤價'], errors='coerce').fillna(0)
    
    # 計算漲跌幅百分比
    df['漲跌幅'] = (df['漲跌價差'] / (df['收盤價'] - df['漲跌價差'])) * 100
    df['漲跌幅'] = df['漲跌幅'].replace([float('inf'), -float('inf')], 0).round(2) # 處理除以零情況

    # 移除漲跌幅為 NaN 或無限大的行 (通常是停牌或無交易)
    df = df.dropna(subset=['漲跌幅'])

    # 篩選上漲和下跌前十名
    top_gainers = df[df['漲跌幅'] > 0].sort_values(by='漲跌幅', ascending=False).head(10)
    top_losers = df[df['漲跌幅'] < 0].sort_values(by='漲跌幅', ascending=True).head(10) # 注意是升序

    # 格式化輸出
    output_gainers = []
    for index, row in top_gainers.iterrows():
        output_gainers.append({
            "code": row['證券代號'],
            "name": row['證券名稱'],
            "change_percent": f"{row['漲跌幅']:.2f}%",
            "change_value": f"{row['漲跌價差']:.2f}",
            "close_price": f"{row['收盤價']:.2f}"
            # 可以根據需求添加更多欄位
        })

    output_losers = []
    for index, row in top_losers.iterrows():
        output_losers.append({
            "code": row['證券代號'],
            "name": row['證券名稱'],
            "change_percent": f"{row['漲跌幅']:.2f}%",
            "change_value": f"{row['漲跌價差']:.2f}",
            "close_price": f"{row['收盤價']:.2f}"
        })

    # 組合最終 JSON
    current_data = {
        "update_time": datetime.now(tw_tz).strftime("%Y-%m-%d %H:%M:%S"),
        "top_gainers": output_gainers,
        "top_losers": output_losers
    }

except Exception as e:
    print(f"Error during data fetch or processing: {e}")
    # 若出錯，嘗試載入舊資料，或使用預設錯誤訊息
    try:
        with open('data.json', 'r', encoding='utf-8') as f:
            current_data = json.load(f)
        current_data['update_time'] = datetime.now(tw_tz).strftime("%Y-%m-%d %H:%M:%S") + " (數據更新失敗，顯示舊資料)"
        current_data['error_message'] = str(e) # 記錄錯誤訊息
    except FileNotFoundError:
        # 如果連舊資料都沒有，則使用預設錯誤訊息
        current_data = {
            "update_time": datetime.now(tw_tz).strftime("%Y-%m-%d %H:%M:%S") + " (初始化/錯誤)",
            "top_gainers": [{"code": "N/A", "name": "資料讀取失敗", "change_percent": "--", "change_value": "--", "close_price": "--"}],
            "top_losers": [{"code": "N/A", "name": "資料讀取失敗", "change_percent": "--", "change_value": "--", "close_price": "--"}],
            "error_message": str(e)
        }

# 寫入 data.json
with open('data.json', 'w', encoding='utf-8') as f:
    json.dump(current_data, f, ensure_ascii=False, indent=2)

print("數據已更新！")
