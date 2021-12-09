#!/usr/bin/env python2
# coding:utf-8

"""
このプログラムでは検証で見つかった優位性領域に対して、各期間ごとの収益状況の分布がどうなっているか検証する
"""

import glob
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os
import datetime

#pandasのオプション設定
pd.set_option("display.max_rows", None)
pd.set_option("display.max_columns", None)

#フォルダ内にある分析手法を取得
results = glob.glob("../result/*")

#パスを削除して、フォルダ名のみを抽出
# result_name_list = [s.replace("./result/", "").replace(".py", "") for s in results]

#検証データを選択
print("<検証したいトレードシステムを選択してください(半角数字）>")
[print("{}: {}".format(i,s.replace("../result/", ""))) for i, s in enumerate(results)]
selected_label = int(input())

file_name = results[selected_label]

df = pd.read_csv(file_name)
# print(df.head())
# print(df.dtypes)

df["date"] = pd.to_datetime(df["date"])
# print(df.dtypes)
# print(df.head())
# print(df.loc[0,"date"])
# print(type(df.loc[0, "date"]))
# print(datetime.datetime.strptime(df.loc[0,"date"], '%Y/%m/%d'))

#検証で見つかった優位性領域の切り取り
target = df[(df["position"]=="l")&(df["x1"]<2)&(df["x2"]>2)&(df["x9"]>-1)&(df["x9"]<1)]
# print(target)
print("------2015-2021-------")
print(target.describe())

print("----------2021------------------")
print(target[(target["date"]<=pd.Timestamp(2021,12,31)) &(target["date"]>=pd.Timestamp(2021,1,1))])
print(target[(target["date"]<=pd.Timestamp(2021,12,31)) &(target["date"]>=pd.Timestamp(2021,1,1))].describe())
print("----------2020------------------")
print(target[(target["date"]<=pd.Timestamp(2020,12,31)) &(target["date"]>=pd.Timestamp(2020,1,1))])
print(target[(target["date"]<=pd.Timestamp(2020,12,31)) &(target["date"]>=pd.Timestamp(2020,1,1))].describe())
print("----------2019------------------")
# print(target[(target["date"]<=pd.Timestamp(2019,12,31)) &(target["date"]>=pd.Timestamp(2019,1,1))])
print(target[(target["date"]<=pd.Timestamp(2019,12,31)) &(target["date"]>=pd.Timestamp(2019,1,1))].describe())
print("----------2018------------------")
# print(target[(target["date"]<=pd.Timestamp(2018,12,31)) &(target["date"]>=pd.Timestamp(2018,1,1))])
print(target[(target["date"]<=pd.Timestamp(2018,12,31)) &(target["date"]>=pd.Timestamp(2018,1,1))].describe())
print("----------2017------------------")
# print(target[(target["date"]<=pd.Timestamp(2017,12,31)) &(target["date"]>=pd.Timestamp(2017,1,1))])
print(target[(target["date"]<=pd.Timestamp(2017,12,31)) &(target["date"]>=pd.Timestamp(2017,1,1))].describe())
print("----------2016------------------")
# print(target[(target["date"]<=pd.Timestamp(2016,12,31)) &(target["date"]>=pd.Timestamp(2016,1,1))])
print(target[(target["date"]<=pd.Timestamp(2016,12,31)) &(target["date"]>=pd.Timestamp(2016,1,1))].describe())
print("----------2015------------------")
# print(target[(target["date"]<=pd.Timestamp(2015,12,31)) &(target["date"]>=pd.Timestamp(2015,1,1))])
print(target[(target["date"]<=pd.Timestamp(2015,12,31)) &(target["date"]>=pd.Timestamp(2015,1,1))].describe())



