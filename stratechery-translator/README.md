# Stratechery Translator

作為prompt engineering上完課之後的第一個小專案，把我平常很懶得用英文閱讀的stratechery用chatgpt翻譯成繁體中文。

具體是用beautifulsoap4抽取裡面的article tag，把article tag翻譯成中文後再放回去html裡面

翻譯完的示意圖像這樣

![](https://imgur.com/a/KK6iXEE)

下方簡單說明一下這怎麼跑

### usage
translator.py [-h] [--model MODEL] [--temperature TEMPERATURE] [--chunk-size CHUNK_SIZE] [--max-workers MAX_WORKERS] file

#### positional arguments:
  file -  HTML file to process

#### optional arguments:  
  -h, --help  
  show this help message and exit

  --model MODEL  
  model of chatgpt, preset to gpt-3.5-turbo

  --temperature TEMPERATURE  
  temperature of chatgpt, preset to 0  

  --chunk-size CHUNK_SIZE  
  chunk size for adapting the chatgpt model, preset to 3500

  --max-workers MAX_WORKERS  
  Max workers to do threading, default set to 4

## 詳細步驟
### 下載檔案

1. 對stratechery按右鍵檢視原始碼
2. 把整個html原始碼貼在記事本
3. 另存記事本為html檔(.html)

### 獲取chatgpt api

1. 到這裡 [https://platform.openai.com/account/api-keys](https://platform.openai.com/account/api-keys)
2. 弄完你的付款手續之後把生成的api key複製起來
3. 把`.env.template`改成`.env`
4. 填入你的api key至第一行

### 翻譯

1. 下載python (google python)
2. 運行 `pip install -r requirements.txt` 下載所需的模組
3. 運行 python translator.py
