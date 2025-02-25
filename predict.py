import pandas as pd
import numpy as np
import json
from datetime import datetime
import openai

def generate_prompt(df):
    """生成OpenAI API的提示词"""
    history_data = []
    
    prompt = """作为双色球预测专家，我会给你近几百期的开奖数据，请你分析这些数据并生成5组最有可能中奖的号码组合。

以下是历史开奖数据（期号 : 6个红球 1个蓝球）:
"""
    # 提取最后200期数据
    for _, row in df.tail(200).iterrows():
        # 格式化日期和号码
        red_balls = [row[f'red_ball_{i}'] for i in range(1, 7)]
        prompt += f"{row['period']}: 红{sorted(red_balls)} 蓝{row['blue_ball']}\n"
    
    prompt += """
请根据以上所有历史数据进行深入分析，然后生成最新一期最可能的5组最可能中奖的号码组合。

要求每组号码包含：
- 6个红球号码(1-33，不重复，升序排列)
- 1个蓝球号码(1-16)
- 每组号码的详细选号理由

请严格按照以下格式输出：
第1组：红球[01 02 03 04 05 06]，蓝球[01]
选号理由：xxxxxx

第2组：红球[xx xx xx xx xx xx]，蓝球[xx]
选号理由：xxxxxx

以此类推到第5组
"""
    
    return prompt

def predict_numbers(api_key=""):
    """使用OpenAI API生成预测结果"""
    try:
        # 直接读取CSV数据
        df = pd.read_csv('ssq_data_20250221.csv')
        prompt = generate_prompt(df)
        print("生成OpenAI API提示词...")
        print(prompt)
        
        if not api_key:
            # 如果没有API key，生成演示数据
            print("使用模拟数据(未提供API key)")
            predictions = []
            for _ in range(5):
                red = sorted(list(np.random.choice(33, 6, replace=False) + 1))
                blue = int(np.random.randint(1, 17))
                predictions.append({"red": red, "blue": blue})
            return predictions
            
        import openai
        openai.api_key = api_key
        print("正在请求OpenAI分析数据...")
        response = openai.ChatCompletion.create(
            model="gpt-4o",  # 使用GPT-4模型
            messages=[
                {"role": "system", "content": "你是一个双色球预测专家，基于历史数据分析生成预测号码。"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
        )
        
        # 解析返回的JSON结果
        content = response.choices[0].message.content
        print("API响应内容:")
        #print(content)
        
        # 解析响应内容
        predictions = []
        groups = content.split("第")[1:]  # 分割每组预测
        
        for group in groups:
            try:
                # 提取号码行
                number_line = group.split('\n')[0]  # 第一行包含号码
                reason_line = group.split('选号理由：')[1].split('\n')[0]  # 获取理由行
                
                # 解析红球和蓝球
                balls_part = number_line.split('：')[1] if '：' in number_line else number_line
                red_part = balls_part.split('红球[')[1].split(']')[0]
                blue_part = balls_part.split('蓝球[')[1].split(']')[0]
                
                # 转换为数字列表
                red_nums = [int(x) for x in red_part.strip().split()]
                blue_num = int(blue_part.strip())
                
                predictions.append({
                    "red": red_nums,
                    "blue": blue_num,
                    "reason": reason_line.strip()
                })
            except Exception as e:
                print(f"解析组号码时出错: {e}")
                continue
        
        return predictions if len(predictions) == 5 else None
        
    except Exception as e:
        print(f"预测过程出错: {e}")
        return None

def main():
    # 这里可以填入你的OpenAI API key
    api_key = ""
    
    predictions = predict_numbers(api_key)
    if predictions:
        print("\n====== 双色球智能预测 ======")
        print(f"预测时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 40)
        print("\n预测结果及理由:")
        print("-" * 40)
        for i, pred in enumerate(predictions, 1):
            red_str = " ".join(f"{num:02d}" for num in pred['red'])
            print(f"\n第{i:02d}组: 红球:[{red_str}] 蓝球:[{pred['blue']:02d}]")
            #print(f"选号理由: {pred['reason']}")
            #print("-" * 40)
        print("=" * 40)
        print("声明：此预测仅供参考，购彩需理性")
    else:
        print("预测失败，请检查API key或重试")

if __name__ == "__main__":
    main()
