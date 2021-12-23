#!/usr/bin/env python2
# coding:utf-8

# import os
import os
import glob
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import scipy as sp
from sklearn.tree import DecisionTreeRegressor
from sklearn.tree import export_graphviz
# from dtreeviz.trees import *
import graphviz

#matplotlibの日本語利用のためのパッケージ
import japanize_matplotlib

#自作モジュール
import module.module_calclation as mc
from strategy.module.module import calc_ATR

#pandasのオプション設定
pd.set_option("display.max_rows", None)
pd.set_option("display.max_columns", None)

#フォルダ内にある分析手法を取得
results = glob.glob("./result/*")

#検証データを選択
print("<検証したいトレードシステムを選択してください(半角数字）>")
[print("{}: {}".format(i,s.replace("./result/", ""))) for i, s in enumerate(results)]
selected_label = int(input())

file_name = results[selected_label]

df = pd.read_csv(file_name)

# #トレード手法に対応するディレクトリの作成
# name_selected = file_name.replace("./result/", "").replace(".csv", "")
# if not os.path.exists("analysis/{}".format(name_selected)):
#     os.mkdir("analysis/{}".format(name_selected))

#勝ちトレード、負けトレードだったかのフラグを変数に追加
win_label = pd.cut(df["pl_atr"], bins=[-100,0,100], right=False, labels=[0,1])
df["win_label"] = win_label

# 目的変数
Y_name = "pl_atr"
# 説明変数
X_name = ["x1", "x2", "x3", "x4", "x5", "x6", "x7", "x8", "x9", "x10", "x11"]


X_train = df[X_name]
Y_train = df[Y_name]

print(X_train.head())

#機械学習モデル（決定木）
dtree = DecisionTreeRegressor(max_depth=3)
dtree.fit(X_train, Y_train)

print(dtree.score(X_train, Y_train))

dot_data = export_graphviz(dtree)
graph = graphviz.Source(dot_data)
graph.render("tree", format="png")