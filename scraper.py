import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime, timedelta

def get_lottery_data():
    # 使用API接口获取数据
    url = "https://www.cwl.gov.cn/cwl_admin/front/cwlkj/search/kjxx/findDrawNotice"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        "Content-Type": "application/json;charset=UTF-8",
        "Origin": "https://www.cwl.gov.cn",
        "Referer": "https://www.cwl.gov.cn/ygkj/wqkjgg/ssq/"
    }
    
    # 计算两年前的日期
    today = datetime.now()
    two_years_ago = today - timedelta(days=1200)
    
    params = {
        "name": "ssq",
        "issueCount": "",
        "issueStart": "",
        "issueEnd": "",
        "dayStart": two_years_ago.strftime("%Y-%m-%d"),
        "dayEnd": today.strftime("%Y-%m-%d"),
        "pageNo": "1",
        "pageSize": "300",  # 增加每页数量以获取更多数据
    }
    
    data_list = []
    try:
        response = requests.get(url, headers=headers, params=params, timeout=10)
        
        if response.status_code != 200:
            print(f"请求失败，状态码: {response.status_code}")
            return None
            
        print("请求成功，开始解析数据...")
        
        json_data = response.json()
        if 'result' not in json_data:
            print("API返回数据格式错误")
            return None
            
        for item in json_data['result']:
            # 解析红球和蓝球
            red_balls = [int(num) for num in item['red'].split(',')]
            blue_ball = int(item['blue'])
            
            data_list.append({
                'period': item['code'],
                'date': item['date'],
                'red_balls': red_balls,
                'blue_ball': blue_ball,
                'sales': item['sales'],
                'prize_pool': item['poolmoney']
            })
            
        print(f"成功获取 {len(data_list)} 期数据")
    
    except Exception as e:
        print(f"Error scraping data: {e}")
        return None
    
    return data_list

def save_to_csv(data):
    # 创建DataFrame
    df_data = []
    for item in data:
        row = {
            'period': item['period'],
            'date': item['date'],
            'blue_ball': item['blue_ball'],
            'sales': item['sales'],
            'prize_pool': item['prize_pool']
        }
        # 添加红球列
        for i, ball in enumerate(item['red_balls'], 1):
            row[f'red_ball_{i}'] = ball
        df_data.append(row)
    
    df = pd.DataFrame(df_data)
    
    # 保存CSV文件
    filename = f'ssq_data_{datetime.now().strftime("%Y%m%d")}.csv'
    df.to_csv(filename, index=False, encoding='utf-8')
    return filename

def main():
    print("开始抓取双色球数据...")
    data = get_lottery_data()
    if data:
        filename = save_to_csv(data)
        print(f"数据已保存到: {filename}")
        print(f"共抓取 {len(data)} 期数据")
    else:
        print("数据抓取失败")

if __name__ == "__main__":
    main()
