import json, pandas as pd, pytz, os
from datetime import datetime

# 設定時間
tw_tz = pytz.timezone('Asia/Taipei')
now = datetime.now(tw_tz)
now_str = now.strftime("%Y-%m-%d %H:%M:%S")

def process_csv_to_json():
    csv_file = 'input.csv'
    
    # 檢查檔案是否存在
    if not os.path.exists(csv_file):
        print(f"找不到 {csv_file}，請先建立檔案。")
        return

    try:
        # 讀取你的手寫數據
        df = pd.read_csv(csv_file)
        
        # 自動計算漲跌幅（制式化邏輯）
        df['今日漲跌幅'] = (((df['收盤價'] - df['昨收價']) / df['昨收價']) * 100).round(2)
        
        # 根據正負分組
        gainers = df[df['今日漲跌幅'] >= 0].sort_values('今日漲跌幅', ascending=False)
        losers = df[df['今日漲跌幅'] < 0].sort_values('今日漲跌幅', ascending=True)

        res_data = {
            "update_time": now_str,
            "is_closed": False, # 你可以根據心情手動改為 True/False
            "gainers": gainers.to_dict('records'),
            "losers": losers.to_dict('records')
        }

        # 寫入網頁專用的 data.json
        with open('data.json', 'w', encoding='utf-8') as f:
            json.dump(res_data, f, ensure_ascii=False, indent=2)
            
        print("CSV 數據已成功轉換為網頁制式格式！")

    except Exception as e:
        print(f"轉換失敗: {e}")

if __name__ == "__main__":
    process_csv_to_json()
