#!/usr/bin/env python2
# coding:utf-8

import pandas as pd
import glob as gl

#フォルダ内にある分析手法を取得
results = gl.glob("./result/*")

#パスを削除して、フォルダ名のみを抽出
# result_name_list = [s.replace("./result/", "").replace(".py", "") for s in results]

#検証データを選択
print("<検証したいトレードシステムを選択してください(半角数字）>")
[print("{}: {}".format(i,s.replace("./result/", ""))) for i, s in enumerate(results)]
selected_label = int(input())

file_name = results[selected_label]

df = pd.read_csv(file_name)

print("-------x2>2の結果----------")
print(df.loc[df["x2"]>2].describe())
# print("-------x2>2,かつx6=1の結果--------")
# print(df.loc[(df["x2"]>2) & (df["x6"]==1)].describe())
# print("-----x2>2, かつx7=1の結果-------")
# print(df.loc[(df["x2"]>2) & (df["x7"]==1)].describe())


print("-------x2>2,かつlの結果--------")
print(df.loc[(df["x2"]>2) & (df["position"]=="l")].describe())
# print("-------x2>2,かつl,かつx7=1の結果--------")
# print(df.loc[(df["x2"]>2) & (df["position"]=="l") & (df["x7"]==1)].describe())
# print("-------x2>2,かつl,かつx7=0の結果--------")
# print(df.loc[(df["x2"]>2) & (df["position"]=="l") & (df["x7"]==0)].describe())
# print("-----x2>2, かつl,かつx1<２の結果------")
# print(df.loc[(df["x2"]>2) & (df["position"]=="l")& (df["x1"] < 2)].describe())
# print("-------x2>2,かつl,かつx4<30の結果--------")
# print(df.loc[(df["x2"]>2) & (df["position"]=="l") &(df["x4"]<30)].describe())
# print("-------x2>2,かつl,かつx4>30の結果--------")
# print(df.loc[(df["x2"]>2) & (df["position"]=="l") &(df["x4"]>30)].describe())
# print("-------x2>2,かつl,かつx4<3の結果--------")
# print(df.loc[(df["x2"]>2) & (df["position"]=="l") &(df["x4"]<3)].describe())
# print("-------x2>2,かつl,かつx5>=1の結果--------")
# print(df.loc[(df["x2"]>2) & (df["position"]=="l") &(df["x3"]>=1)].describe())
# print("-------x2>2,かつl,かつx5=0の結果--------")
# print(df.loc[(df["x2"]>2) & (df["position"]=="l") &(df["x3"]==0)].describe())
# print("-------x2>2,かつl,かつx6=1,かつ1<x1<2の結果--------")
# print(df.loc[(df["x2"]>2) & (df["position"]=="l") &(df["x6"]==1) &(df["x1"]>1)&(df["x1"]<2)].describe())
# print("-------x2>2,かつl,かつx7=1,かつ1<x1<2の結果--------")
# print(df.loc[(df["x2"]>2) & (df["position"]=="l") &(df["x7"]==1) &(df["x1"]>1)&(df["x1"]<2)].describe())
print("-------x2>2,かつl,かつ0<x1<2の結果--------")
print(df.loc[(df["x2"]>2) & (df["position"]=="l") &(df["x1"]>0)&(df["x1"]<2)].describe())

print("-------x2>2,かつsの結果--------")
print(df.loc[(df["x2"]>2) & (df["position"]=="s")].describe())
# print("-------x2>2,かつs,かつx7=1の結果--------")
# print(df.loc[(df["x2"]>2) & (df["position"]=="s") & (df["x7"]==1)].describe())
# print("-------x2>2,かつs,かつx7=0の結果--------")
# print(df.loc[(df["x2"]>2) & (df["position"]=="s") & (df["x7"]==0)].describe())
# print("-----x2>2, かつs,かつx1<２の結果------")
# print(df.loc[(df["x2"]>2) & (df["position"]=="s")& (df["x1"] < 2)].describe())
# print("-------x2>2,かつs,かつx4<30の結果--------")
# print(df.loc[(df["x2"]>2) & (df["position"]=="s") &(df["x4"]<30)].describe())
# print("-------x2>2,かつs,かつx4>30の結果--------")
# print(df.loc[(df["x2"]>2) & (df["position"]=="s") &(df["x4"]>30)].describe())
# print("-------x2>2,かつs,かつx4<3の結果--------")
# print(df.loc[(df["x2"]>2) & (df["position"]=="s") &(df["x4"]<3)].describe())
# print("-------x2>2,かつs,かつx5>=1の結果--------")
# print(df.loc[(df["x2"]>2) & (df["position"]=="s") &(df["x5"]>=1)].describe())
# print("-------x2>2,かつs,かつx5=0の結果--------")
# print(df.loc[(df["x2"]>2) & (df["position"]=="s") &(df["x5"]==0)].describe())
# print("-------x2>2,かつs,かつx6=1,かつ1<x1<2の結果--------")
# print(df.loc[(df["x2"]>2) & (df["position"]=="s") &(df["x6"]==1) &(df["x1"]>1)&(df["x1"]<2)].describe())
print("-------x2>2,かつs,かつ1<x1<2の結果--------")
print(df.loc[(df["x2"]>2) & (df["position"]=="s") &(df["x1"]>1)&(df["x1"]<2)].describe())

# print("x2>2の結果")
# print(df.loc[df["x2"]>2].describe())
# print("x2>2の結果")
# print(df.loc[df["x2"]>2].describe())
# print("x2>2の結果")
# print(df.loc[df["x2"]>2].describe())
# print("x2>2の結果")
# print(df.loc[df["x2"]>2].describe())



