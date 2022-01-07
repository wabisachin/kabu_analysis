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
from sklearn.preprocessing import LabelEncoder
from sklearn.tree import DecisionTreeRegressor, export_graphviz, plot_tree
from dtreeviz.trees import dtreeviz
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
X_name = ["position_encorded","x1", "x2", "x3", "x4", "x5", "x6", "x7", "x8", "x9", "x10"]

#positionをラベルエンコード
enc = LabelEncoder()
label_encoder = enc.fit_transform(df.loc[:, "position"])
df["position_encorded"] = label_encoder

#学習用データ
X_train = df[X_name]
Y_train = df[Y_name]


#機械学習モデルの選択（決定木）
dtree = DecisionTreeRegressor(max_depth=3, min_samples_leaf=30)
model = dtree.fit(X_train, Y_train)

print(model.score(X_train, Y_train))
# print(dtree.score(X_train, Y_train))

#dtreeによる可視化
# viz = dtreeviz(model, X_train, Y_train, X_name, Y_name, "pl_atr")
# viz.view()

#graphvizによる可視化
fig = plt.figure(figsize=(12, 6))
#描画
plot_tree(
    model,
    max_depth=10,
    feature_names = X_name,
    filled=True,
    precision=2,
    fontsize=10
    # proportion=True,
    )
plt.show()
#matplotlibで保存
# plt.savefig("tree.pdf")

#特徴量重要度
# feature = dtree.feature_inportances_
# label = df.columns
# indices = np.argsort(feature)
# fig = plt.figure(fig=(10, 10))
# plt.barh()
# plt.yticks(range(len(feature)), label[indices], fontsize=14)
# plt.xticks(fontsize=14)
# plt.ylabel("Feature", fontsize=18)
# plt.xlabel("Feature Importance", fontsize=18)



# dot_data = export_graphviz(model)
# graph = graphviz.Source(dot_data)
# graph.render("wave-tree", format="png")