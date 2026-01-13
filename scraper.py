import json, pandas as pd, pytz, os
from datetime import datetime

tw_tz = pytz.timezone('Asia/Taipei')
now = datetime.now(tw_tz)

def process():
    if not os.path.exists('input.csv'):
        print("Error: input.csv not found")
        return
    
    df = pd.read_csv('input.csv')
    # 制式化計算今日漲跌幅
    df['今日漲跌幅'] = (((df['收盤價'] - df['昨收價']) / df['昨收價']) * 100).round(2)
    
    gainers = df[df['今日漲跌幅'] >= 0].sort_values('今日漲跌幅', ascending=False)
    losers = df[df['今日漲跌幅'] < 0].sort_values('今日漲跌幅', ascending=True)

    output = {
        "update_time": now.strftime("%Y-%m-%d %H:%M:%S"),
        "is_closed": False,
        "gainers": gainers.to_dict('records'),
        "losers": losers.to_dict('records')
    }

    with open('data.json', 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    process()
