import re
import json

def parse_markdown(content):
    lines = content.split("\n")
    data = []
    for index, line in enumerate(lines):
        count = line.count("#")
        # 移除 '#' 並清理內容中的空格與換行符號
        text = ' '.join(line.replace("#", "").strip().split())
        category = None
        if count == 1:
            category = "head"
        elif count == 2:
            category = "title"
        elif count == 3:
            category = "subtitle"
        elif count == 4:
            category = "chapter"
        if category:
            data.append({"id": index+1, "category": category, "content": text})
    return json.dumps(data, ensure_ascii=False)


content = """
# 目錄

## 1. 攝影基礎
### 1.1 相機概述
#### 1.1.1 DSLR與Mirrorless
#### 1.1.2 相機的主要組成部分
### 1.2 操作相機
#### 1.2.1 如何拿取與安全使用相機
#### 1.2.2 如何調整鏡頭與焦距
### 1.3 相機模式與功能
#### 1.3.1 全自動模式與手動模式
#### 1.3.2 其他重要模式介紹：光圈優先、快門優先等

## 2. 攝影原理
### 2.1 曝光三原則
#### 2.1.1 光圈
#### 2.1.2 快門速度
#### 2.1.3 ISO
### 2.2 白平衡
### 2.3 對焦
#### 2.3.1 自動對焦與手動對焦
#### 2.3.2 對焦方式的選擇

## 3. 構圖技巧
### 3.1 知名構圖法則
#### 3.1.1 三分法
#### 3.1.2 黃金比例
### 3.2 運用色彩
### 3.3 創意構圖

## 4. 光與影的運用
### 4.1 光線的角度
### 4.2 光的強弱與色溫
### 4.3 運用影子

## 5. 風景攝影
### 5.1 風景攝影技巧
#### 5.1.1 選擇地點與時間
#### 5.1.2 使用寬角鏡頭與長焦鏡頭
### 5.2 自然光線的運用
### 5.3 風景攝影構圖

## 6. 花卉攝影
### 6.1 花卉攝影技巧
#### 6.1.1 選擇與安排背景
#### 6.1.2 使用微距鏡頭
### 6.2 光線的運用
### 6.3 花卉攝影構圖

## 7. 後製處理
### 7.1 照片的基本調整
### 7.2 專業後製軟體介紹
#### 7.2.1 Lightroom
#### 7.2.2 Photoshop
### 7.3 風景與花卉照片的特別後製技巧

## 8. 攝影器材選擇與維護
### 8.1 選擇適合的相機與鏡頭
### 8.2 保護與清潔攝影器材
### 8.3 攝影配件介紹

## 9. 實戰應用與練習
### 9.1 實例分析
### 9.2 練習與挑戰

## 10. 攝影的未來與趨勢
### 10.1 技術的進步
### 10.2 攝影的新趨勢
### 10.3 進階學習資源與建議
"""

import json

def parse_json(input_json, templates):
    # 將 json 轉換為 Python 的 dict
    data = json.loads(input_json)

    output = []

    for item in data:
        # 根據分類選擇模板
        template = templates[item["category"]]

        # 去除內容中的換行和多餘的空格
        content = ' '.join(item["content"].split())

        # 將內容插入模板中
        filled_template = template.format(content=content)

        # 將新的內容添加到輸出列表中
        output.append({"id": item["id"], "category": item["category"], "content": filled_template})

    # 將輸出列表轉換為 json
    output_json = json.dumps(output)

    return output_json



# 你的模板
templates = {
    "head": """{content}""",
    "title": """
你是一名風景、花卉攝影大師，你的將被指派撰寫教科書的內容，以下是詳細的工作敘述

首先，請你詳細閱讀目錄，目錄以```分隔在最下方。

接著是你的工作，你的工作是替教科書的「{content}」撰寫內容，「{content}」是一個章節總覽，你必須介紹這個章節內會教授些什麼知識，請你"不要"分開章節介紹，以簡單語句涵蓋章節內容。

1. 內容要求：
1.1 總字數不得超過500字
1.2 在文章最後給不超過3題的章節引導問題

2. 輸出要求
2.1 請以zh-hant-tw輸出
2.2 請以markdown格式輸出，並在前後加上```
""",
    "subtitle": """
你是一名風景、花卉攝影大師，你的將被指派撰寫教科書的內容，以下是詳細的工作敘述

首先，請你詳細閱讀目錄，目錄以```分隔在最下方。

接著是你的工作，你的工作是替教科書的「{content}」撰寫內容，「{content}」是一個小節總覽，你必須介紹這個小節內會教授些什麼知識，請你"不要"分開小節介紹，以簡單語句涵蓋小節內容。

1. 內容要求：
1.1 總字數不得少於2000字
1.2 在文章最後給不超過3題的小節引導問題

2. 輸出要求
2.1 請以zh-hant-tw輸出
2.2 請以markdown格式輸出，並在前後加上```
    """,
    "chapter": """
你是一名風景、花卉攝影大師，你的將被指派撰寫教科書的內容，以下是詳細的工作敘述

首先，請你詳細閱讀目錄，目錄以```分隔在最下方。

接著是你的工作，你的工作是替教科書的「{content}」撰寫內容，「{content}」是一個小節，你必須替這個小節撰寫教學內容，這也是這本教科書中最重要的部分。

1. 內容要求：
1.1 總字數不得少於3000字
1.2 在文章最後給作業與反思題

2. 輸出要求
2.1 請以zh-hant-tw輸出
2.2 請以markdown格式輸出，並在前後加上```
    """,
}

input_json = parse_markdown(content)

# 你的 json 數據
# input_json = '[{"id": 1, "category": "head", "content": "目錄"}, ...]'

# 使用函式
output_json = parse_json(input_json, templates)

# print(output_json)

def parse_json2(input_json):
    # 将 JSON 解析为 Python 字典
    data = json.loads(input_json)

    # 提取 content 并打印出来
    for item in data:
        print(item["content"])
        print("\n ------------------------------ \n")
        
parse_json2(output_json)




