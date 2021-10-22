#!/usr/bin/env python2
# coding:utf-8

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import glob as gl
import re
import module.module_calclation as mc

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
# def plot_biaxial_graph_for_EV(df, variable):#widthは区間幅, rightは境界値。例えばx2の場合は各区間幅(width)は1,境界値は7が妥当。
    
#     ev_list = []
#     count_list = []
#     #特徴量別のbin区間定義。関数pd.cut(df,labels, bins, right=True) はデフォルトでritht=Trueなので,右辺の末端を含むことを考慮してbinの範囲を指定した。
#     label_list ={
#         "x1": {"bin_labels":["x1<=1", "1<x1<=2","2<x1<=3","3<x1<=4","4<x1<=5","5<x1<=6","6<x1<=7", "7<x1"], "bins":[0,1,2,3,4,5,6,7,100]},
#         "x2": {"bin_labels":["x2<=1", "1<x2<=2","2<x2<=3","3<x2<=4","4<x2<=5","5<x2<=6","6<x2<=7", "7<x2"], "bins":[0,1,2,3,4,5,6,7,100]},
#         "x3": {"bin_labels":["x3<=5", "5<x3<=10","10<x3<=15","15<x3<=20"], "bins":[-1,5,10,15,20]},
#         "x4": {"bin_labels":["x4<=10", "10<x4<=20","20<x4<=30","30<x4<=40", "40<x4<=50", "50<x4<=60"], "bins":[-1,10,20,30,40,50,60]},
#         "x5": {"bin_labels":["x5=0", "x5=1","x5=2","x5=3","x5=4","x5=5","5<x5=10","10<x5<=20","20<x5"], "bins":[-1,0,1,2,3,4,5,10,20,100]},
#         "x6": {"bin_labels":["0", "1"], "bins":[-1,0,1]},
#         "x7": {"bin_labels":["0", "1"], "bins":[-1,0,1]},
#         "x8": {"bin_labels":["-10％以上", "-10％~-7.5％","-7.5％~-5.0％","-5.0％~-2.5％","-2.5％~0％", "0％~2.5％", "2.5％~5.0％","5.0％~7.5％","7.5％~10.0％","10.0％以上" ], "bins":[-1,-0.1, -0.75, -0.5, -0.25, 0, 0.25, 0.5, 0.75, 0.1, 1]},
#     }
#     labels = label_list[variable]["bin_labels"]
#     df["label"] = pd.cut(x=df[variable], bins=label_list[variable]["bins"], labels=label_list[variable]["bin_labels"])

#     for label in labels:
#         ev = df.loc[df["label"] == label]["pl_atr"].mean()
#         count = df.loc[df["label"] == label]["label"].count()
#         ev_list.append(ev)
#         count_list.append(count)


#     print(ev_list)
#     print(count_list)

#     #matplotlib.pypltによる描写
#     fig, ax1 = plt.subplots()
#     ax2 = ax1.twinx()
#     ax1.grid(True)
#     ax2.grid(False)
#     color1, color2 = "skyblue", "orange"

#     plt.title("Biaxial graph for {}(hist & EV)".format(variable))
#     ax2.spines["left"].set_color(color1)
#     ax2.spines["right"].set_color(color2)
#     ax1.tick_params(axis='y', colors = color1)
#     ax2.tick_params(axis='y', colors=color2)
#     ax1.plot(labels, ev_list, color=color1, label="pl_atr")
#     ax2.bar(labels, count_list, color=color2, alpha=0.6, width=0.5, label="count")
#     plt.tick_params(labelsize=10)
#     handler1, label1 = ax1.get_legend_handles_labels()
#     handler2, label2 = ax2.get_legend_handles_labels()
#     ax1.legend(handler1+handler2, label1+label2, loc="upper right")

#     # plt.close(fig)
#     plt.savefig("Biaxial graph for {}.png".format(variable))
#     # plt.show()


# print(df.head())
# print(df.columns)
# print(df.columns[1])
# #特徴量一覧
# variables = [col for col in df.columns if re.search(r'x\d', col)]
# print(variables)

def plot_all_biaxial_graph_for_EV(df):

    #特徴量別のbin区間定義。関数pd.cut(df,labels, bins, right=True) はデフォルトでritht=Trueなので,右辺の末端を含むことを考慮してbinの範囲を指定した。
    # label_list ={
    #     "x1": {"bin_labels":["x1<=1", "1<x1<=2","2<x1<=3","3<x1<=4","4<x1<=5","5<x1<=6","6<x1<=7", "7<x1"], "bins":[0,1,2,3,4,5,6,7,100]},
    #     "x2": {"bin_labels":["x2<=1", "1<x2<=2","2<x2<=3","3<x2<=4","4<x2<=5","5<x2<=6","6<x2<=7", "7<x2"], "bins":[0,1,2,3,4,5,6,7,100]},
    #     "x3": {"bin_labels":["x3<=5", "5<x3<=10","10<x3<=15","15<x3<=20"], "bins":[-1,5,10,15,20]},
    #     "x4": {"bin_labels":["x4<=10", "10<x4<=20","20<x4<=30","30<x4<=40", "40<x4<=50", "50<x4<=60"], "bins":[-1,10,20,30,40,50,60]},
    #     "x5": {"bin_labels":["x5=0", "x5=1","x5=2","x5=3","x5=4","x5=5","5<x5=10","10<x5<=20","20<x5"], "bins":[-1,0,1,2,3,4,5,10,20,100]},
    #     "x6": {"bin_labels":["0", "1"], "bins":[-1,0,1]},
    #     "x7": {"bin_labels":["0", "1"], "bins":[-1,0,1]},
    #     "x8": {"bin_labels":["-10％以上", "-10％~-7.5％","-7.5％~-5.0％","-5.0％~-2.5％","-2.5％~0％", "0％~2.5％", "2.5％~5.0％","5.0％~7.5％","7.5％~10.0％","10.0％以上" ], "bins":[-1,-0.1, -0.75, -0.5, -0.25, 0, 0.25, 0.5, 0.75, 0.1, 1]},
    # }
    #dfのcolumnから特徴量だけ抽出してリスト化
    variables = [col for col in df.columns if re.search(r'x\d', col)]

    """x8がエラーを吐き出すので一時的に除外"""
    variables.remove("x8")

    """x8がエラーを吐き出すので一時的に除外"""

    length = len(variables)
    #描写領域の確保
    fig = plt.figure()
    ax_list = []

    for i, variable in enumerate(variables):
        mc.plot_biaxial_graph_for_EV(df, variable)
        # ev_list = []
        # count_list = []

        # labels = label_list[variable]["bin_labels"]
        # df["label"] = pd.cut(x=df[variable], bins=label_list[variable]["bins"], labels=label_list[variable]["bin_labels"])

        # for label in labels:
        #     ev = df.loc[df["label"] == label]["pl_atr"].mean()
        #     count = df.loc[df["label"] == label]["label"].count()
        #     ev_list.append(ev)
        #     count_list.append(count)

        # print(ev_list)
        # print(count_list)

        # ax1 = fig.add_subplot((length/2)+1, 2, i+1)
        # ax2 = ax1.twinx()
        # color1, color2 = "skyblue", "orange"
        # plt.title("Biaxial graph for {}(hist & EV)".format(variable))
        # ax2.spines["left"].set_color(color1)
        # ax2.spines["right"].set_color(color2)
        # ax1.tick_params(axis='y', colors = color1)
        # ax2.tick_params(axis='y', colors=color2)
        # ax1.plot(labels, ev_list, color=color1, label="pl_atr")
        # ax2.bar(labels, count_list, color=color2, alpha=0.6, width=0.5, label="count")
        # plt.tick_params(labelsize=10)
        # handler1, label1 = ax1.get_legend_handles_labels()
        # handler2, label2 = ax2.get_legend_handles_labels()
        # ax1.legend(handler1+handler2, label1+label2, loc="upper right")
    
    # plt.show()

plot_all_biaxial_graph_for_EV(df)




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

# print("-----lの結果-----")
# print(df.loc[df["position"]=="l"].describe())
# print("-----l, かつ0<x2<1の結果-----")
# print(df.loc[(df["x2"]>0) &(df["x2"]<1) & (df["position"]=="l")].describe())
# print("-----l, かつ1<x2<2の結果-----")
# print(df.loc[(df["x2"]>1) &(df["x2"]<2) & (df["position"]=="l")].describe())
# print("-----l, かつ2<x2<3の結果-----")
# print(df.loc[(df["x2"]>2) &(df["x2"]<3) & (df["position"]=="l")].describe())
# print("-----l, かつ3<x2<4の結果-----")
# print(df.loc[(df["x2"]>3) &(df["x2"]<4) & (df["position"]=="l")].describe())
# print("-----l, かつ4<x2<5の結果-----")
# print(df.loc[(df["x2"]>4) &(df["x2"]<5) & (df["position"]=="l")].describe())
# print("-----l, かつ5<x2<6の結果-----")
# print(df.loc[(df["x2"]>5) &(df["x2"]<6) & (df["position"]=="l")].describe())
# print("-----l, かつ6<x2<7の結果-----")
# print(df.loc[(df["x2"]>6) &(df["x2"]<7) & (df["position"]=="l")].describe())
# print("-----l, かつ7<x2<8の結果-----")
# print(df.loc[(df["x2"]>7) &(df["x2"]<8) & (df["position"]=="l")].describe())
# print("-----l, かつ8<x2<9の結果-----")
# print(df.loc[(df["x2"]>8) &(df["x2"]<9) & (df["position"]=="l")].describe())
# print("-----l, かつ9<x2の結果-----")
# print(df.loc[(df["x2"]>9)& (df["position"]=="l")].describe())
# print("---------------")
# print("-----l, かつ2<x2<3の結果-----")
# print(df.loc[(df["x2"]>2) &(df["x2"]<3) & (df["position"]=="l")].describe())
# print("-----l, かつ2<x2<3,かつx7=0の結果-----")
# print(df.loc[(df["x2"]>2) &(df["x2"]<3) & (df["position"]=="l")&(df["x7"]==0)].describe())
# print("-----l, かつ2<x2<3,かつx7=1の結果-----")
# print(df.loc[(df["x2"]>2) &(df["x2"]<3) & (df["position"]=="l")&(df["x7"]==1)].describe())
# print("-----l, かつ2<x2<3,かつ1<x1<2の結果-----")
# print(df.loc[(df["x2"]>2) &(df["x2"]<3) & (df["position"]=="l")&(df["x1"]>1)&(df["x1"]<2)].describe())
# print("-----l, かつ2<x2<3,かつ2<x1<3の結果-----")
# print(df.loc[(df["x2"]>2) &(df["x2"]<3) & (df["position"]=="l")&(df["x1"]>2)&(df["x1"]<3)].describe())
# print("-----l, かつ2<x2<3,かつ3<x1<4の結果-----")
# print(df.loc[(df["x2"]>2) &(df["x2"]<3) & (df["position"]=="l")&(df["x1"]>3)&(df["x1"]<4)].describe())
# print("-----l, かつ2<x2<3,かつ4<x1<5の結果-----")
# print(df.loc[(df["x2"]>2) &(df["x2"]<3) & (df["position"]=="l")&(df["x1"]>4)&(df["x1"]<5)].describe())
# print("-----l, かつ2<x2<3,かつ5<x1の結果-----")
# print(df.loc[(df["x2"]>2) &(df["x2"]<3) & (df["position"]=="l")&(df["x1"]>5)].describe())