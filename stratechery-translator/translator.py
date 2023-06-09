#!/usr/bin/env python
# coding: utf-8

import sys
import argparse
from bs4 import BeautifulSoup
import os
import openai
from dotenv import load_dotenv, find_dotenv
from typing import List
import opencc
from concurrent.futures import ThreadPoolExecutor
import requests
from urllib.parse import urlparse
import webbrowser
# from datetime import datetime

def load_api_key():
    """
    Load api key from dotenv and save it as a glocal variable: openai.api_key
    """

    # Check if .env file exists
    try:
        _ = load_dotenv(find_dotenv())
    except FileNotFoundError:
        print("錯誤：請將 '.env.template' 更名為 '.env'，並加入您的 OpenAI API 金鑰。")
        sys.exit()
    
    openai.api_key  = os.getenv('OPENAI_API_KEY')
    return

def is_valid_url(url: str) -> bool:
    """
    :param url: The URL string to be checked

    Check if a URL is valid
    """
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except ValueError:
        return False

def get_url_and_params():
    """
    :returns: 
        - url - URL of the webpage to process
        - model - model of chatgpt, preset to gpt-3.5-turbo
        - temperature - temperature of chatgpt, preset to 0
        - chunk_size - chunk size for adapting the chatgpt model, preset to 3500
        - max_workers - Max workers to do threading, default set to 4

    Get the URL from system arguments.

    """
    parser = argparse.ArgumentParser()
    parser.add_argument('url', help='URL of the webpage to process')
    parser.add_argument('--model', type=str, default='gpt-3.5-turbo', help='model of chatgpt, preset to gpt-3.5-turbo')
    parser.add_argument('--temperature', type=int, default=0, help='temperature of chatgpt, preset to 0')
    parser.add_argument('--chunk-size', type=int, default=3500, help='chunk size for adapting the chatgpt model, preset to 3500')
    parser.add_argument('--max-workers', type=int, default=15, help='Max workers to do threading, default set to 15')

    args = parser.parse_args()

    # Check if the argument is a valid URL
    if not is_valid_url(args.url):
        print("錯誤：必須提供有效的網址")
        sys.exit()

    return args.url, args.model, args.temperature, args.chunk_size, args.max_workers

def read_html_from_url(url: str):
    """
    :param url: URL to the webpage

    Send a GET request to the provided URL and return its HTML content.
    """

    response = requests.get(url)
    response.raise_for_status()  # If the request failed, this will raise a HTTPError

    whole_html = response.text
    # print(f"Successfully retrieved HTML from {url}")
    return whole_html

def get_article_tag(html) -> str:
    """
    :param html: The stratechery html article string

    Extract article tag from a html string
    """
    # read html code with bs4
    soup = BeautifulSoup(html, 'lxml')

    # get the article tag
    article_tag = soup.find('article')

    # print('成功抽出文章內容')

    return str(article_tag)

def insert_article_tag(html: str, modified_article_tag: str) -> str:
    """
    :param html: The original html code used to be inserted.
    :param modified_article_tag: The translated article tag.

    Insert The modified article tag into original html code and return in string format.
    """
    # read html code with bs4
    soup = BeautifulSoup(html, 'lxml')

    # replace the original article tag with the new one
    original_article_tag = soup.find('article')
    if original_article_tag:
        new_article_tag = BeautifulSoup(modified_article_tag, 'lxml').article
        if new_article_tag:
            original_article_tag.replace_with(new_article_tag)
        else:
            print("讀取翻譯後article tag失敗")
    else:
        print("讀取原檔案失敗: 找不到<article>")

    return str(soup)



def translate_article(article_tag: str, chunk_size: int, model: str, temperature: int, max_workers: int) -> str:
    """
    :param article_tag: The article tag in English fro translate in string format.
    :param chunk_size: The length of each chunk being splitted to adapt the api word length limitation.
    :param model: Chat gpt model.
    :param temperature: Chat gpt api temperature.
    :param max_workers: Number of threading.

    Main function that takes a string as input to talk to chatgpt to translate the string into zh-hant-tw.
    1. Split the article tag into an array with read_string_in_chunks function.
    2. Iterate through the array to translate each chunk.
    3. Put the translated chunk into a new array.
    """

    def read_string_in_chunks(input_string: str, chunk_size) -> List[str]:
        """
        :param input_string: The input string for split into array.
        :param chunk_size: The size of characters to trim.

        The function reads a string then truncate them into a array based on the chunk_size parameter.
        """
        for i in range(0, len(input_string), chunk_size):
            yield input_string[i:i + chunk_size]

    def get_completion_from_messages(messages, model, temperature) -> str:
        """
        :param messages: messages the run the chat-gpt model (include role and chat in json format)
        :param model: chatgpt model, preset to gpt-3.5-turbo
        :param temperature: temperature to talk to chatgpt, preset to 0.

        Chatgpt-api function to ask for chat with messages set.
        """
        response = openai.ChatCompletion.create(
            model=model,
            messages=messages,
            temperature=temperature, # this is the degree of randomness of the model's output
        )
        return response.choices[0].message["content"]

    def trim_strings(array: List[str]) -> List[str]:
        """
        :param array: The array of translated article tag.

        Iterate through the article tag to check if there's backsticks generated by chatgpt.
        """
        
        new_array = []

        for chunk in array:
            if chunk.startswith('```'):
                chunk = chunk[3:]
            if chunk.endswith('```'):
                chunk = chunk[:-3]

            new_array.append(chunk)

        return new_array

    def simplified_to_traditional(simplified_string) -> str:
        """
        :param simplified_string: a string to be convert to traditional Chinese

        A function from opencc to convert a string of simplified Chinese to traditional Chinese.
        """
        converter = opencc.OpenCC('s2t.json')

        traditional_string = converter.convert(simplified_string)

        return traditional_string
 
    # print how much token are used
    print(f'耗費時元(token)數量: {len(article_tag)}')
    print(f'預估耗費金額: {len(article_tag) / 1000 * 0.002}')

    # make a article tag into a list of strings
    chunks = list(read_string_in_chunks(article_tag, chunk_size))
    length = len(chunks)

    def process_chunk(i, chunk):
        """
        A worker for impolementing threading.
        """
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
        
        # interact with chatgpt inside the iteration
        print(f'正在翻譯第 {i+1}/{length} 個段落')
        response = get_completion_from_messages(messages, model, temperature)
        # convert simplified to traditional (which happenes occationally)
        response = simplified_to_traditional(response)
        print(f'第 {i+1}/{length} 段落已翻譯完畢')
        return response

    # create a ThreadPoolExecutor
    with ThreadPoolExecutor(max_workers) as executor:
        # submit tasks to the executor
        futures = [executor.submit(process_chunk, i, chunk) for i, chunk in enumerate(chunks)]

    # collect results as they become available
    translated_array = [future.result() for future in futures]

    # trim the array
    translated_array = trim_strings(translated_array)    

    # combine the array back into a string
    translated_article_tag = ''.join(translated_array)

    return translated_article_tag

def extract_title_from_url(url: str) -> str:
    """
    :param url: The URL of the article

    Extract the title of the article from the URL
    """
    parsed_url = urlparse(url)
    
    # Split the path and take the last part as the title
    title = parsed_url.path.split('/')[2]
    return title

def write_to_file(html, title):
    """
    :param html: the html code to be written.
    :param filename: the filename of the file.

    Write the translated html code into the file inside translated directory
    """
    # Ensure the directory exists
    directory = ".\\translated"
    if not os.path.exists(directory):
        print('tanslated資料夾不存在，已自動建立')
        os.makedirs(directory)

    # Create the filename
    file_path = f"{directory}\\Translated_{title}.html"
    # Write the text to the file
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(html)
        print(f'檔案已儲存於 {file_path}')
    
    return file_path

def open_html_file(file_path: str):
    """
    :param file_path: The path to the HTML file

    Open the HTML file in the default web browser
    """
    # Check if the file exists
    if not os.path.isfile(file_path):
        print(f"The file {file_path} does not exist.")
        return

    # Open the file in the default browser
    webbrowser.open('file://' + os.path.realpath(file_path))


def main():
    
    # load the api key from .env file
    load_api_key()

    # get user input
    url, model, temperature, chunk_size, max_workers = get_url_and_params()

    # read html file and store the html into a variable
    english_whole_html = read_html_from_url(url)

    # extract the article tag from the html
    english_article_tag = get_article_tag(english_whole_html)

    # main process for translating the article tag from English to Zh-Hant-TW
    translated_article_tag = translate_article(english_article_tag,chunk_size=chunk_size, model=model, temperature=temperature, max_workers=max_workers)

    # insert the html tag back into the original html code.
    translated_html = insert_article_tag(english_whole_html, translated_article_tag)

    # extract title form url
    title = extract_title_from_url(url)

    # write the file to translated directory
    file_path = write_to_file(translated_html, title)
    
    # open the translated file with default browser
    open_html_file(file_path)

if __name__ == "__main__":
    main()