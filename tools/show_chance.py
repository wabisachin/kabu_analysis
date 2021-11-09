#!/usr/bin/env python3
# coding:utf-8

#銘柄codeを与えれば,当日の各説明変数Xの値を表示するスクリプト

from bs4 import BeautifulSoup
import traceback
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import pandas as pd


INTERVAL_TIME =2

def get_driver():
    #ヘッドレスモードでブラウザを起動
    options = Options()
    # options.add_argument('--headless')  

    #ブラウザを起動
    driver = webdriver.Chrome(options=options)
    return driver

def get_source_from_page(driver, page):
    try:
        driver.get(page)
        driver.implicitly_wait(10)#見つからない場合は10秒待つ
        page_source = driver.page_source
 
        return page_source
 
    except Exception as e:
 
        print("Exception\n" + traceback.format_exc())
 
        return None

def get_data_from_source(src):
    soup = BeautifulSoup(src, "lxml")
    # target = soup.select("#wrapper_main#container#main#stock_kabuka_table")
    # data = soup.select("#stock_kabuka_table.stock_kabuka_dwn")
    data = soup.select("#stock_kabuka_table")
    return data


if __name__ == "__main__":

    base_url = "https://kabutan.jp/stock/kabuka?code="
    driver = get_driver()
    source = get_source_from_page(driver, "https://kabutan.jp/stock/kabuka?code=4528")
    # print(source)
    text = get_data_from_source(source)
    print(text)