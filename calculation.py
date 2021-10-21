#!/usr/bin/env python2
# coding:utf-8

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import glob as gl
from matplotlib import cm

#pandasのオプション設定
pd.set_option("display.max_rows", None)
pd.set_option("display.max_columns", None)

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
print(df.describe())

#選択した特徴量を指定領域(bin)に分割して、各ビン内におけるpl_atr(ev)をグラフ化。(ビニング分析)
def plot_ev_by_quartile(df, variable):#widthは区間幅, rightは境界値。例えばx2の場合は各区間幅(width)は1,境界値は7が妥当。
    
    ev_list = []
    count_list = []
    #特徴量別のbin区間定義。関数pd.cut(df,labels, bins, right=True) はデフォルトでritht=Trueなので,右辺の末端を含むことを考慮してbinの範囲を指定した。
    label_list ={
        "x1": {"bin_labels":["x1<=1", "1<x1<=2","2<x1<=3","3<x1<=4","4<x1<=5","5<x1<=6","6<x1<=7", "7<x1"], "bins":[0,1,2,3,4,5,6,7,100]},
        "x2": {"bin_labels":["x2<=1", "1<x2<=2","2<x2<=3","3<x2<=4","4<x2<=5","5<x2<=6","6<x2<=7", "7<x2"], "bins":[0,1,2,3,4,5,6,7,100]},
        "x3": {"bin_labels":["x3<=5", "5<x3<=10","10<x3<=15","15<x3<=20"], "bins":[-1,5,10,15,20]},
        "x4": {"bin_labels":["x4<=10", "10<x4<=20","20<x4<=30","30<x4<=40", "40<x4<=50", "50<x4<=60"], "bins":[-1,10,20,30,40,50,60]},
        "x5": {"bin_labels":["x5=0", "x5=1","x5=2","x5=3","x5=4","x5=5","5<x5=10","10<x5<=20","20<x5"], "bins":[-1,0,1,2,3,4,5,10,20,100]},
        "x6": {"bin_labels":["0", "1"], "bins":[-1,0,1]},
        "x7": {"bin_labels":["0", "1"], "bins":[-1,0,1]},
        "x8": {"bin_labels":["-10％以上", "-10％~-7.5％","-7.5％~-5.0％","-5.0％~-2.5％","-2.5％~0％", "0％~2.5％", "2.5％~5.0％","5.0％~7.5％","7.5％~10.0％","10.0％以上" ], "bins":[-1,-0.1, -0.75, -0.5, -0.25, 0, 0.25, 0.5, 0.75, 0.1, 1]},
    }
    labels = label_list[variable]["bin_labels"]
    df["label"] = pd.cut(x=df[variable], bins=label_list[variable]["bins"], labels=label_list[variable]["bin_labels"])

    for label in labels:
        ev = df.loc[df["label"] == label]["pl_atr"].mean()
        count = df.loc[df["label"] == label]["label"].count()
        ev_list.append(ev)
        count_list.append(count)


    print(ev_list)
    print(count_list)

    fig, ax1 = plt.subplots()
    ax2 = ax1.twinx()
    ax1.grid(True)
    ax2.grid(False)
    color1 = cm.Set1.colors[1]
    color2 =cm.Set1.colors[0]
    plt.title("説明変数{}の各パラメータ値の出現頻度と期待値(pl_atr)".format(variable))
    ax2.spines["left"].set_color(color1)
    ax2.spines["right"].set_color(color2)
    ax1.tick_params(axis='y', colors = color1)
    ax2.tick_params(axis='y', colors=color2)
    ax1.plot(labels, ev_list, color=color1, label="pl_atr")
    ax2.bar(labels, count_list, color=color2, alpha=0.4, width=0.5, label="count")
    # ax2.bar(labels, count_list, color=cm.Set1.colors[0])
    # plt.tick_params(labelsize=10)
    handler1, label1 = ax1.get_legend_handles_labels()
    handler2, label2 = ax2.get_legend_handles_labels()
    ax1.legend(handler1+handler2, label1+label2, loc="upper right")

    plt.show()

        
print(df.head())
plot_ev_by_quartile(df, "x2")

# sns.countplot(x="x4", data = df)
# sns.countplot(x="x2", data = df)
# sns.displot(df["x2"], kde = False, bins = 10)
# plt.show()

# df.plot.scatter(x="x3", y="x5")
# plt.show()


# print(df.dtypes)
# scatter = df.plot.scatter(x="x1", y="pl_atr")
# scatter.plot()
# plt.show()
# sns.scatterplot(x="x1", y="pl_atr", data=df, color="red", alpha=0.5)
# print(df.corr())
# print(df.describe())
# plt.scatter(df["x1"], df["x2"])
# plt.xlabel("x2")
# plt.ylabel("pl_atr")
# plt.show()


#2<x2, position="l", x7=0のヒートマップをx2,x4の二次元で作成。目的変数y:pl_atr
# df_x7_0 = df.loc[df["x7"]==0]









# print("-------x2>2の結果----------")
# print(df.loc[df["x2"]>2].describe())
# print("-------x2>2,かつx6=1の結果--------")
# print(df.loc[(df["x2"]>2) & (df["x6"]==1)].describe())
# print("-----x2>2, かつx7=1の結果-------")
# print(df.loc[(df["x2"]>2) & (df["x7"]==1)].describe())
# print("-----x2>2, 0<x1<3,かつlの結果-----")
# print(df.loc[(df["x2"]>2) &(df["x1"]<3) & (df["x1"]>0) & (df["position"]=="l")])
# print("-----x2>2, 0<x1<1,かつlの結果-----")
# print(df.loc[(df["x2"]>2) &(df["x1"]<1) & (df["x1"]>0) & (df["position"]=="l")].describe())
# print("-----x2>2, 1<x1<2,かつlの結果-----")
# print(df.loc[(df["x2"]>2) &(df["x1"]<2) & (df["x1"]>1) & (df["position"]=="l")].describe())
# print("-----x2>2, 2<x1<3,かつlの結果-----")
# print(df.loc[(df["x2"]>2) &(df["x1"]<3) & (df["x1"]>2) & (df["position"]=="l")].describe())
# print("-----x2>2, 3<x1<4,かつlの結果-----")
# print(df.loc[(df["x2"]>2) &(df["x1"]<4) & (df["x1"]>3) & (df["position"]=="l")].describe())
# print("-----x2>2, 4<x1<5,かつlの結果-----")
# print(df.loc[(df["x2"]>2) &(df["x1"]<5) & (df["x1"]>4) & (df["position"]=="l")].describe())



# print("-----x2>2, 0<x1<1,かつl、かつx7=1の結果-----")
# print(df.loc[(df["x2"]>2) &(df["x1"]<1) & (df["x1"]>0) & (df["position"]=="l") &(df["x7"] == 1)].describe())
# print("-----x2>2, 1<x1<2,かつl, かつx7=0の結果-----")
# print(df.loc[(df["x2"]>2) &(df["x1"]<2) & (df["x1"]>1) & (df["position"]=="l") &(df["x7"] == 0)].describe())
# print("-----x2>2, 1<x1<2,かつl, かつx7=1の結果-----")
# print(df.loc[(df["x2"]>2) &(df["x1"]<2) & (df["x1"]>1) & (df["position"]=="l") &(df["x7"] == 1)].describe())
# print("-----x2>2, 1<x1<2,かつl, かつx6=0の結果-----")
# print(df.loc[(df["x2"]>2) &(df["x1"]<2) & (df["x1"]>1) & (df["position"]=="l") &(df["x6"] == 0)].describe())
# print("-----x2>2, 1<x1<2,かつl, かつx6=1の結果-----")
# print(df.loc[(df["x2"]>2) &(df["x1"]<2) & (df["x1"]>1) & (df["position"]=="l") &(df["x6"] == 1)].describe())
# print("-----x2>2, 1<x1<2,かつl, かつx4<30の結果-----")
# print(df.loc[(df["x2"]>2) &(df["x1"]<2) & (df["x1"]>1) & (df["position"]=="l") &(df["x4"] <30)].describe())
# print("-----x2>2, 1<x1<2,かつl, かつx4>=30の結果-----")
# print(df.loc[(df["x2"]>2) &(df["x1"]<2) & (df["x1"]>1) & (df["position"]=="l") &(df["x4"] >= 30)].describe())
