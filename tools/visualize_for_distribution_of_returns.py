#!/usr/bin/env python2
# coding:utf-8

"""
発見した優位性領域内における収益分布（度数分布）をヒストグラムとして可視化するスクリプト
"""

# import os
import glob
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os

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
print(df.describe())


# 発見した優位性領域の収益分布を可視化
def visualize_for_distribution_of_returns(df, title="distribution_of_returns"):
    
    df["pl_atr"].hist(by=df["position"], bins=20)
    plt.show()
    plt.savefig()


# print(df[(df["position"]=="l")&(0<df["x1"])&(df["x1"]<2)&(-1<df["x9"])&(df["x9"]<1)&(df["x2"]>2)])
# print(df[(df["position"]=="l")&(0<df["x1"])&(df["x1"]<2)&(-1<df["x9"])&(df["x9"]<1)&(df["x2"]>2)].describe())

visualize_for_distribution_of_returns(df[(df["x1"]<2)&(-1<df["x9"])&(df["x9"]<1)&(df["x2"]>2)])
# visualize_for_distribution_of_returns(df[(df["position"]=="l")&(df["x1"]<2)&(-1<df["x9"])&(df["x9"]<1)&(df["x2"]>2)])

# def visualize_for_distribution_of_returns_by_all_position(df):
#     visualize_for_distribution_of_returns(df[(df["position"]=="l")&(df["x1"]<2)&(-1<df["x9"])&(df["x9"]<1)&(df["x2"]>2)])
#     visualize_for_distribution_of_returns(df[(df["position"]=="s")&(df["x1"]<2)&(-1<df["x9"])&(df["x9"]<1)&(df["x2"]>2)])
