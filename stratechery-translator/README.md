# Stratechery Translator

作為prompt engineering上完課之後的第一個小專案，把我平常很懶得用英文閱讀的stratechery用chatgpt翻譯成繁體中文。

具體是用beautifulsoap4抽取裡面的article tag，把article tag翻譯成中文後再放回去html裡面

翻譯完的示意圖像這樣

![](https://imgur.com/a/KK6iXEE)


# usage
```bash
usage: translator.py [-h] [--model MODEL] [--temperature TEMPERATURE] [--chunk-size CHUNK_SIZE]
                     [--max-workers MAX_WORKERS]
                     url

positional arguments:
  url                   URL of the webpage to process

options:
  -h, --help            show this help message and exit
  --model MODEL         model of chatgpt, preset to gpt-3.5-turbo
  --temperature TEMPERATURE
                        temperature of chatgpt, preset to 0
  --chunk-size CHUNK_SIZE
                        chunk size for adapting the chatgpt model, preset to 3500
  --max-workers MAX_WORKERS
                        Max workers to do threading, default set to 4
```