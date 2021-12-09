#!/usr/bin/env python2
# coding:utf-8

# import os
import glob
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os

#自作モジュール
import module.module_calclation as mc

#pandasのオプション設定
pd.set_option("display.max_rows", None)
pd.set_option("display.max_columns", None)

#フォルダ内にある分析手法を取得
results = glob.glob("./result/*")

#パスを削除して、フォルダ名のみを抽出
# result_name_list = [s.replace("./result/", "").replace(".py", "") for s in results]

#検証データを選択
print("<検証したいトレードシステムを選択してください(半角数字）>")
[print("{}: {}".format(i,s.replace("./result/", ""))) for i, s in enumerate(results)]
selected_label = int(input())

file_name = results[selected_label]

df = pd.read_csv(file_name)
# print(df.describe())

#トレード手法に対応するディレクトリの作成
name_selected = file_name.replace("./result/", "").replace(".csv", "")
if not os.path.exists("analysis/{}".format(name_selected)):
    os.mkdir("analysis/{}".format(name_selected))

#２軸グラフを画像ファイルとして保存
# mc.plot_all_biaxial_graph_for_EV(df, name_selected)

# mc.visualize_for_EV_by_heatmap(df, "x1", "x2", name_selected, save=True)
# mc.visualize_for_EV_by_heatmap(df, "x3", "x1", name_selected, save=True)
# mc.visualize_for_EV_by_heatmap(df, "x3", "x2", name_selected, save=True)
# mc.visualize_for_EV_by_heatmap(df, "x4", "x2", name_selected, save=True)
# mc.visualize_for_EV_by_heatmap(df, "x5", "x2", name_selected, save=True)
# mc.visualize_for_EV_by_heatmap(df, "x6", "x2", name_selected, save=True)
# mc.visualize_for_EV_by_heatmap(df, "x7", "x2", name_selected, save=True)
# mc.visualize_for_EV_by_heatmap(df, "x8", "x2", name_selected, save=True)
# mc.visualize_for_EV_by_heatmap(df, "x9", "x1", name_selected, save=True)
# mc.visualize_for_EV_by_heatmap(df, "x9", "x2", name_selected, save=True)
# mc.visualize_for_EV_by_heatmap(df, "x10", "x2", name_selected, save=True)
# mc.visualize_for_EV_by_heatmap(df, "x11", "x2", name_selected, save=True)


print("x2>2条件下のヒートマップ検証")
# mc.visualize_for_EV_by_heatmap(df[(df["x11"]>=0)&(df["x9"]<1)&(df["x9"]>-1)], "x1", "x2", name_selected, "x11>=0")
# mc.visualize_for_EV_by_heatmap(df[(df["x11"]<0)&(df["x9"]<1)&(df["x9"]>-1)], "x1", "x2", name_selected, "x11<0")
# mc.visualize_for_EV_by_heatmap(df[(df["x8"]>=0)&(df["x9"]<1)&(df["x9"]>-1)], "x1", "x2", name_selected, "x8>=0")
# mc.visualize_for_EV_by_heatmap(df[(df["x8"]<0)&(df["x9"]<1)&(df["x9"]>-1)], "x1", "x2", name_selected, "x8<0")
# mc.visualize_for_EV_by_heatmap(df[(df["x1"]<2)&(df["x1"]>0)&(df["x9"]<1)&(df["x9"]>-1)], "x8", "x2", name_selected, "0<x1<2, -1<x9<1")
# mc.visualize_for_EV_by_heatmap(df[(df["x9"]<1)&(df["x9"]>-1)], "x1", "x2", name_selected)
# mc.visualize_for_EV_by_heatmap(df[(df["x2"]>2)], "x7", "x1", name_selected, "x2>2")
# mc.visualize_for_EV_by_heatmap(df[(df["x2"]>2)], "x9", "x1", name_selected, "x2>2")

# mc.visualize_for_EV_by_heatmap(df[(df["x2"]>0)&(df["x2"]<2)], "x4", "x1", name_selected, "0<x2<2")
# mc.visualize_for_EV_by_heatmap(df[(df["x2"]>2)&(df["x2"]<4)], "x4", "x1", name_selected, "2<x2<4")
# mc.visualize_for_EV_by_heatmap(df[(df["x2"]>4)&(df["x2"]<6)], "x4", "x1", name_selected, "4<x2<6")
# mc.visualize_for_EV_by_heatmap(df[(df["x2"]>6)&(df["x2"]<8)], "x4", "x1", name_selected, "6<x2<8")
# mc.visualize_for_EV_by_heatmap(df[(df["x2"]>8)&(df["x2"]<10)], "x4", "x1", name_selected, "8<x2<10")
# mc.visualize_for_EV_by_heatmap(df[(df["x2"]>10)&(df["x2"]<20)], "x4", "x1", name_selected, "10<x2<20")

# print(df[(df["position"]=="l")&(df["x2"]>2)&(df["x1"]<2)&(df["x9"]<1)&(df["x9"]>-1)].loc[:, ["date","code","position", "pl_atr"]])
# print(df[(df["position"]=="l")&(df["x2"]>2)&(df["x1"]<2)&(df["x9"]<1)&(df["x9"]>-1)].describe())
# print(df[(df["position"]=="l")&(df["x2"]>7)&(df["x1"]<2)&(df["x7"]==1)].loc[:, ["date","code","position", "pl_atr"]])
# print(df[(df["position"]=="l")&(df["x2"]>7)&(df["x1"]<2)&(df["x7"]==1)].describe())
print(df[(df["position"]=="l")&(df["x1"]>4)].loc[:, ["date","code","position", "pl_atr"]])
print(df[(df["position"]=="l")&(df["x1"]>4)].describe())
# print(df[(df["position"]=="s")&(df["x2"]>2)&(df["x1"]<2)&(df["x9"]<1)&(df["x9"]>-1)].describe())