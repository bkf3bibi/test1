import json, requests, pytz
from datetime import datetime

# 1. 設定時區
tw_tz = pytz.timezone('Asia/Taipei')
now = datetime.now(tw_tz).strftime("%Y-%m-%d %H:%M:%S")

# 2. 爬取真實新聞 (以 Yahoo 財經 RSS 為例，較穩定且不需 Key)
news_list = []
try:
    # 這裡抓取台灣財經新聞
    response = requests.get("https://tw.stock.yahoo.com/rss/s/tw-stock")
    # 簡單的文字處理來抓取標題 (這是一個簡易示範)
    content = response.text
    titles = content.split('<title>')[2:7] # 取前 5 則
    for t in titles:
        title_text = t.split('</title>')[0]
        news_list.append({"title": title_text, "status": "自動掃描完成"})
except:
    news_list = [{"title": "新聞抓取失敗", "status": "請檢查網路連線"}]

# 3. 儲存成 JSON
data = {
    "update_time": now,
    "stock_news": news_list if news_list else [{"title": "目前無新聞", "status": "請稍後再試"}]
}

with open('data.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
