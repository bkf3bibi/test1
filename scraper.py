import json, pytz
from datetime import datetime

# 設定台北時間
tw_tz = pytz.timezone('Asia/Taipei')
now = datetime.now(tw_tz).strftime("%Y-%m-%d %H:%M:%S")

# 模擬資料 (之後可換成真正的 requests 爬蟲)
data = {
    "update_time": now,
    "stock_news": [
        {"title": "台積電盤後分析", "status": "今日表現平穩"},
        {"title": "大盤趨勢", "status": "機器人自動更新成功"}
    ]
}

with open('data.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
