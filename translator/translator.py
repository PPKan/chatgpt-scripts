#!/usr/bin/env python
# coding: utf-8

# # Stratechery Translater

# ## Read Stratechery file

# In[41]:


import sys
from bs4 import BeautifulSoup


def get_file_name():
    # Check the number of command-line arguments
    if len(sys.argv) != 2:
        print("使用方法： python3 myscript.py <filename.html>")
        print("範例： python3 myscript.py example.html")
        sys.exit()

    # Get the first command-line argument
    filename = sys.argv[1]

    # Check if the argument is an HTML file
    if not filename.endswith('.html'):
        print("錯誤：檔案必須是.html檔案")
        sys.exit()

    return filename

def get_article_tag(html):
    soup = BeautifulSoup(html, 'lxml')

    article_tag = soup.find('article')

    return str(article_tag)

def insert_modified_article_tag(html, modified_article_tag):
    soup = BeautifulSoup(html, 'lxml')

    original_article_tag = soup.find('article')
    if original_article_tag:
        new_article_tag = BeautifulSoup(modified_article_tag, 'lxml').article
        if new_article_tag:
            original_article_tag.replace_with(new_article_tag)

    return str(soup)

def read_html_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as post_file:
        whole_html = post_file.read()
    return whole_html

import os
import openai

def load_api_key():
    from dotenv import load_dotenv, find_dotenv
    
    # Check if .env file exists
    try:
        _ = load_dotenv(find_dotenv())
    except FileNotFoundError:
        print("錯誤：請將 '.env.template' 更名為 '.env'，並加入您的 OpenAI API 金鑰。")
        sys.exit()
    
    openai.api_key  = os.getenv('OPENAI_API_KEY')


# In[32]:


def get_completion(prompt, model="gpt-3.5-turbo"):
    messages = [{"role": "user", "content": prompt}]
    response = openai.ChatCompletion.create(
        model=model,
        messages=messages,
        temperature=0, # this is the degree of randomness of the model's output
    )
    return response.choices[0].message["content"]

def get_completion_from_messages(messages, model="gpt-3.5-turbo", temperature=0):
    response = openai.ChatCompletion.create(
        model=model,
        messages=messages,
        temperature=temperature, # this is the degree of randomness of the model's output
    )
#     print(str(response.choices[0].message))
    return response.choices[0].message["content"]


# ### main functions to interact with chatgpt api to translate the html

# In[33]:


def read_string_in_chunks(input_string, chunk_size=3500):
    for i in range(0, len(input_string), chunk_size):
        yield input_string[i:i + chunk_size]

def process_with_chatgpt_api(chunk, chatgpt_api_func):
    # Here you would call your chatgpt api function with the chunk as input.
    response = chatgpt_api_func(chunk)
    return response


# In[34]:


def translate_article(article_tag):
    chunks = list(read_string_in_chunks(article_tag))
    length = len(chunks)
    
    translated = []
    for i, chunk in enumerate(chunks):
        
        messages =  [  
        {'role':'system', 'content':'You are an technology article professional translater at translating article from English to zh-hant-tw.'},
        {'role':'assistant', 'content':'Ok, I am a professional translator from English to zh-hant-tw.'}
        ]
        
        messages.append({'role':'user', 'content':f"""
        You are being provided a part of html code of an article, it is most likely a part of technology column, \
        but some times it will be something other than that, the content of the html is delimited in three backticks below.
        
        The text you translate will be concat to other translated passage, \
        so make sure to output the full text containing original html code, \
        and do not quote in three backticks.
        
        You have to:
        1. Read through the html code, remember, the passage might seems being cut in half, which is totally normal.
        2. Translate the article inside into zh-hant-TW.
        3. Rewrite the translated article to make it more readible for ZH-HANT-TW reader \
        by changing the word or the word sequence.
        3. Output the translated html code without three backticks quoted.
       
        part of the passage: {i+1} / {length}
        content: ```{chunk}```
        """
        })
        
        response = get_completion_from_messages(messages, temperature=0)
        translated.append(response)    
    
    return translated



# ### Parse the array (trimming the unnecessary line break and backticks)

# In[36]:


def trim_strings(array):
    return [
        s[3:-3] if s.startswith('```') and s.endswith('```') else
        s[2:-2] if s.startswith('\n') and s.endswith('\n') else
        s
        for s in array
    ]


# ### Output the function to a file

# In[38]:


from datetime import datetime

def write_to_file(text, optional_name=""):
    
    # Get the current date
    current_date = datetime.now()

    # Format the date as a string in the format "yymmdd"
    date_string = current_date.strftime('%y%m%d')

    # Create the filename
    filename = f"{date_string}-Stratechery{optional_name}.html"

    # Write the text to the file
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(text)      
    
    return filename

# In[39]:


def main():
    load_api_key()
    file_path = get_file_name()
    print('成功讀取檔案')
    whole_html = read_html_file(file_path)
    article_tag = get_article_tag(whole_html)
    print('翻譯中，這會花一點時間')
    translated_array = translate_article(article_tag)
    print('翻譯完成，正在處理資料')
    trimmed_translated_array = trim_strings(translated_array)
    translated = ''.join(trimmed_translated_array)
    translated_html = insert_modified_article_tag(whole_html, translated)
    filename = write_to_file(translated_html)
    print(f'已寫入檔案 -- {filename}')
    
if __name__ == "__main__":
    main()