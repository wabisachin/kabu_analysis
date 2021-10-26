#!/usr/bin/env python3
# coding:utf-8


#moduleの概要
"""
期待値分析用のmoduleをここにまとめた。
"""

#moduleの使用方法
"""
いずれの関数においても、リスト形式にされたトレード結果を引数に渡す必要がある。
その際に、一つ一つのリスト要素は各トレードの結果が格納されたdict型データであり、
各dictデータは少なくとも以下の４つのkeyを保有する必要がある。

key = {日付(date)、ポジション方向(position)、銘柄コード(code)、損益(pl)}

つまり、引数として与えるデータは以下のようなリスト構造でなければならない。

<例＞
trade_list_sample = 
[{'date': '2020/01/15', 'position': 's', 'code': 'NI225', 'pl': -1.304},
 {'date': '2020/01/21', 'position': 's', 'code': 'NI225', 'pl': 2.664}, 
 {'date': '2020/04/23', 'position': 'l', 'code': 'NI225', 'pl': 0.332}, 
 {'date': '2020/09/30', 'position': 's', 'code': 'NI225', 'pl': -1.0}, 
 {'date': '2020/11/24', 'position': 'l', 'code': 'NI225', 'pl': 0.84}, 
 {'date': '2020/12/09', 'position': 'l', 'code': 'NI225', 'pl': -0.123}]

"""

#分析項目の用語一覧
"""
<検証項目一覧>
N(エントリー回数), N_P(勝ちトレードの回数　※収益０円は勝ちトレードにカウント）、N_L(負けトレードの回数)
total_P(利益の合計額), total_L(損失の合計額), max_P（最大利益pt）, max_L(最大損失pt), max_NP(最大連勝数）、max_NL(最大連敗数）

<検証項目から算出された項目一覧>
1: PL = total_P - total_L(pt単位のトータル損益)
2: PO=total_P/total_L(ペイオフ値)
3: win_rate = N_P/N = 1 - N_L/N (勝率。最大値は１)
4: EV=PL/N=PO*win_rate-(1-winrate)（１トレード当たりの期待値pt）
5: P_AVE = total_P/N_P(勝ちトレード１回あたりの平均利益pt)
6: L_AVE = total_L/N_L（負けトレード１回あたりの平均損失pt)

"""

#-------------------------------以下、module↓--------------------------------------------

import csv
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import re
import os

#時系列データ(.csv)から[日付、始値、高値、安値、終値]を抽出し、Dataflame型に変換する関数
# def get_data(fileName):

#     df= pd.read_csv(fileName)
#     df.drop(df.columns[5:], axis=1, inplace=True)
#     #2010/10/01は東証のシステムエラーのため、データから除去
#     df.drop(df.loc[df["日付"]=="2020/10/01"].index, inplace=True)
#     #データの古い順にsort
#     df = df.iloc[::-1]
#     #indexの番号が変わっていないので振り直す
#     df.reset_index(drop=True,inplace=True)
#     #csvデータの価格表示が",”を含んだ文字列型となっているので、取り除いてfloat型にキャスト
#     for name in df:
#         df[name] = df.loc[:, name].str.replace(",", "")
#     df = df.astype({"始値": "float", "高値":"float", "安値":"float", "終値":"float"})
#     return df

#時系列データ(.csv)から[日付、始値、高値、安値、終値]を抽出し、Dataflame型に変換する関数
def get_data(fileName):

    df= pd.read_csv(fileName)
    df.drop(df.columns[7:], axis=1, inplace=True)
    #2010/10/01は東証のシステムエラーのため、データから除去
    df.drop(df.loc[df["日付"]=="2020/10/01"].index, inplace=True)
    #データの古い順にsort
    df = df.iloc[::-1]
    #indexの番号が変わっていないので振り直す
    df.reset_index(drop=True,inplace=True)
    #csvデータの価格表示が",”を含んだ文字列型となっているので、取り除いてfloat型にキャスト
    for name in df:
        df[name] = df.loc[:, name].str.replace(",", "")
    df = df.astype({"始値": "float", "高値":"float", "安値":"float", "終値":"float","前日比":"float", "出来高":"int"})
    return df

#時系列データcsvファイルから[日付、始値、高値、安値、終値]だけを抽出し、データの古い順にソートしてリスト化する関数
def get_data_from_csv(fileName):

    data = []

    with open(fileName,"r",) as f:
        reader = csv.reader(f)
        header = next(reader) #ヘッダーはデータではないのでスキップ
        for row in reader:
            del(row[5:])#日付、始値、高値、安値、終値以外のデータを除外
            if (row[0] == '2020/10/01'):#2020/10/1は東証のシステムエラーなので除外
                continue
            for i in range(4):#文字列データを数値データに変換
                row[i+1]  =row[i+1].replace(",", "")
                row[i+1] = float(row[i+1])
            data.append(row)

    data.reverse()

    return data


#investing.comから入手したnikkei225csvデータの整形
def data_shaping_from_investing(fileName):
    with open(fileName, "r+") as f:
        writer = csv.writer(f)
        header = next(writer)
        for row in writer:
            print(row[0])

#Dataframe型でまとめられたトレード結果の集計。３つの売買区分別（合算、ロング、ショート）に集計して結果を返す
def summary_PL(trade_result, display=1):
    #目的の変数定義
    results  = pd.DataFrame(index=["ls", "l", "s"], columns=["N", "N_P", "N_L", "total_P", "total_L", "max_P", "max_L", "max_NP", "max_NP"])
    trades = {"ls": trade_result, "l": trade_result.loc[trade_result["position"] == "l"], "s": trade_result.loc[trade_result["position"] == "s"]}
    #データ要素0埋め
    results.fillna(0, inplace=True)
    # print("------check------")
    # print(trades)
    for index, result in results.iterrows():
        #テーブルに値を代入
        results.loc[index,"N"] = len(trades[index])
        results.loc[index, "N_P"] = len(trades[index].query("pl>=0"))
        results.loc[index, "N_L"] = len(trades[index].query("pl<0"))
        results.loc[index, "total_P"] = trades[index].query("pl>=0")["pl"].sum()
        results.loc[index, "total_L"] = trades[index].query("pl<0")["pl"].sum()
        results.loc[index, "max_P"] = trades[index].describe().loc["max", "pl"]
        results.loc[index, "max_L"] = trades[index].describe().loc["min", "pl"]

    if(display==1):
        for index, result in results.iterrows():
            print("---------------------{}のresult-------------------".format(index))
            print(trades[index])
            print("")
            print("<summary>".format(index))
            print(result)
        
    return results

#期待値を算出する関数(dataFrame型version)
# result = {"ls":{}, "l":{}, "s":{}}
#     result["ls"]={"PL":0, "PO":0, "win_rate":0, "EV":0, "P_AVE":0, "L_AVE":0}
#     result["l"]={"PL":0, "PO":0, "win_rate":0, "EV":0, "P_AVE":0, "L_AVE":0}
#     result["s"]={"PL":0, "PO":0, "win_rate":0, "EV":0, "P_AVE":0, "L_AVE":0}

def calc_EV(trade_result, display=1):

    #目的変数の構造
    results = pd.DataFrame(index=["ls", "l", "s"], columns=["N", "PL","EV", "PF", "win_rate", "PO", "P_AVE", "L_AVE"])

    summary = summary_PL(trade_result, display=0)

    for index, row in summary.iterrows():
        results.loc[index, "N"] = row["N"]
        results.loc[index, "PL"] = row["total_P"]+row["total_L"]
        results.loc[index, "EV"] = (row["total_P"]+row["total_L"])/row["N"] if row["N"]!=0 else "-"
        results.loc[index, "PF"] = row["total_P"]/row["total_L"]*(-1) if row["total_L"]!=0 else "-"
        results.loc[index, "win_rate"] = row["N_P"]/row["N"] if row["N"]!=0 else "-"
        results.loc[index, "P_AVE"] = row["total_P"]/row["N_P"] if row["N_P"]!=0 else "-"
        results.loc[index, "L_AVE"] = row["total_L"]/row["N_L"]if row["N_L"]!=0 else "-"
        results.loc[index, "PO"] = results.loc[index, "P_AVE"]/results.loc[index, "L_AVE"]*(-1) if results.loc[index, "L_AVE"]!=0 else "-"
    
    if(display==1):
        trades = {"ls": trade_result, "l": trade_result.loc[trade_result["position"] == "l"], "s": trade_result.loc[trade_result["position"] == "s"]}
        for index, result in results.iterrows():

            print("---------------------{}のresult-------------------".format(index))
            print(trades[index])
            print("")
            print("[summary]")
            print(summary.loc[index,:])
            print("")
            print("[EV]")
            print(result)

    return results

#選択した特徴量を指定領域(bin)毎に分割して、各ビン内におけるpl_atr(ev)をヒストグラムと共に２軸グラフ化。(ビニング分析)
def plot_biaxial_graph_for_EV(df, variable, name_dir, save=1):#widthは区間幅, rightは境界値。例えばx2の場合は各区間幅(width)は1,境界値は7が妥当。
    
    ev_list = []
    count_list = []
    #特徴量別のbin区間定義。関数pd.cut(df,labels, bins, right=True) はデフォルトでritht=Trueなので,右辺の末端を含むことを考慮してbinの範囲を指定した。
    label_list ={
        "x1": {"bin_labels":["0~1", "1~2","2~3","3~4","4~5","5~6","6~7", "7~"], "bins":[0,1,2,3,4,5,6,7,100]},
        "x2": {"bin_labels":["~1", "1~2","2~3","3~4","4~5","5~6","6~7", "7~"], "bins":[0,1,2,3,4,5,6,7,100]},
        "x3": {"bin_labels":["~5", "5~10","10~15","15~20"], "bins":[-1,5,10,15,20]},
        "x4": {"bin_labels":["~10", "10~20","20~30","30~40", "40~50", "50~60"], "bins":[-1,10,20,30,40,50,60]},
        "x5": {"bin_labels":["0", "1","2","3","4","5","5~10","10~20","20~"], "bins":[-1,0,1,2,3,4,5,10,20,100]},
        "x6": {"bin_labels":["0", "1"], "bins":[-1,0,1]},
        "x7": {"bin_labels":["0", "1"], "bins":[-1,0,1]},
        "x8": {"bin_labels":["-10％以上", "-10％~-7.5％","-7.5％~-5.0％","-5.0％~-2.5％","-2.5％~0％", "0％~2.5％", "2.5％~5.0％","5.0％~7.5％","7.5％~10.0％","10.0％以上" ], "bins":[-1,-0.1, -0.75, -0.5, -0.25, 0, 0.25, 0.5, 0.75, 0.1, 1]},
    }
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
    color1, color2 = "skyblue", "orange"

    # plt.title("説明変数{}の各パラメータ値の出現頻度と期待値(pl_atr)".format(variable))
    plt.title("Biaxial graph for {}(hist & EV)".format(variable))
    ax1.set_xlabel(variable)
    ax2.spines["left"].set_color(color1)
    ax2.spines["right"].set_color(color2)
    ax1.tick_params(axis='y', colors = color1)
    ax2.tick_params(axis='y', colors=color2)
    ax1.plot(labels, ev_list, color=color1, label="pl_atr")
    ax2.bar(labels, count_list, color=color2, alpha=0.6, width=0.5, label="count")
    # ax2.bar(labels, count_list, color=cm.Set1.colors[0])
    plt.tick_params(labelsize=10)
    handler1, label1 = ax1.get_legend_handles_labels()
    handler2, label2 = ax2.get_legend_handles_labels()
    ax1.legend(handler1+handler2, label1+label2, loc="upper right")

    #save=0なら画像保存せずにfigureに表示する
    plt.savefig("analysis/{}/Biaxial graph for {}.png".format(name_dir,variable)) if save==1 else plt.show()


def plot_all_biaxial_graph_for_EV(df, name_dir):

    #dfのcolumnから特徴量だけ抽出してリスト化
    variables = [col for col in df.columns if re.search(r'x\d', col)]

    """x8がエラーを吐き出すので一時的に除外"""
    variables.remove("x8")

    """x8がエラーを吐き出すので一時的に除外"""

    length = len(variables)
    #描写領域の確保
    fig = plt.figure()
    ax_list = []

    # 各特徴量ごとのEV-hist２軸グラフを画像ファイルの連続保存
    for i, variable in enumerate(variables):
        plot_biaxial_graph_for_EV(df, variable, name_dir)

#2変数のpivot_tableをポジション別で作成。(value:pl_atr)
def make_pivot_table_for_pl(df, var1, var2, margins=True):

    #戻り値
    dict_heatmap = {}

    #特徴量別のbin区間定義。関数pd.cut(df,labels, bins, right=True) はデフォルトでritht=Trueなので,右辺の末端を含むことを考慮してbinの範囲を指定した。
    label_list ={
        "x1": {"bin_labels":["0~1", "1~2","2~3","3~4","4~5","5~6","6~7", "7~"], "bins":[0,1,2,3,4,5,6,7,100]},
        "x2": {"bin_labels":["~1", "1~2","2~3","3~4","4~5","5~6","6~7", "7~"], "bins":[0,1,2,3,4,5,6,7,100]},
        "x3": {"bin_labels":["~5", "5~10","10~15","15~20"], "bins":[-1,5,10,15,20]},
        "x4": {"bin_labels":["~10", "10~20","20~30","30~40", "40~50", "50~60"], "bins":[-1,10,20,30,40,50,60]},
        "x5": {"bin_labels":["0", "1","2","3","4","5","5~10","10~20","20~"], "bins":[-1,0,1,2,3,4,5,10,20,100]},
        "x6": {"bin_labels":["0", "1"], "bins":[-1,0,1]},
        "x7": {"bin_labels":["0", "1"], "bins":[-1,0,1]},
        "x8": {"bin_labels":["-10％以上", "-10％~-7.5％","-7.5％~-5.0％","-5.0％~-2.5％","-2.5％~0％", "0％~2.5％", "2.5％~5.0％","5.0％~7.5％","7.5％~10.0％","10.0％以上" ], "bins":[-1,-0.1, -0.75, -0.5, -0.25, 0, 0.25, 0.5, 0.75, 0.1, 1]},
    }
    for position in ["ls", "l", "s"]:
        df_temp = df[df["position"] == position] if position in ["l", "s"] else df
        #選択された2変数をビニングし,カテゴリー変数を付与
        for var in [var1, var2]:
            labels = label_list[var]["bin_labels"]
            df_temp["{}_label".format(var)] = pd.cut(x=df_temp[var], bins=label_list[var]["bins"], labels=label_list[var]["bin_labels"])
        #カテゴリー化された2変数に対して、ピボットテーブルを作成(value:pl_atr)
        if margins:
            df_heatmap = pd.pivot_table(df_temp, index="{}_label".format(var1), columns="{}_label".format(var2), values="pl_atr", margins=True)
        else:
            df_heatmap = pd.pivot_table(df_temp, index="{}_label".format(var1), columns="{}_label".format(var2), values="pl_atr")
        dict_heatmap[position] = df_heatmap

    return dict_heatmap

#２変数のクロス集計をポジション別で作成(value:count)
def make_pivot_table_for_N(df, var1, var2, margins=True):
    #戻り値
    dict_heatmap = {}

    #特徴量別のbin区間定義。関数pd.cut(df,labels, bins, right=True) はデフォルトでritht=Trueなので,右辺の末端を含むことを考慮してbinの範囲を指定した。
    label_list ={
        "x1": {"bin_labels":["0~1", "1~2","2~3","3~4","4~5","5~6","6~7", "7~"], "bins":[0,1,2,3,4,5,6,7,100]},
        "x2": {"bin_labels":["~1", "1~2","2~3","3~4","4~5","5~6","6~7", "7~"], "bins":[0,1,2,3,4,5,6,7,100]},
        "x3": {"bin_labels":["~5", "5~10","10~15","15~20"], "bins":[-1,5,10,15,20]},
        "x4": {"bin_labels":["~10", "10~20","20~30","30~40", "40~50", "50~60"], "bins":[-1,10,20,30,40,50,60]},
        "x5": {"bin_labels":["0", "1","2","3","4","5","5~10","10~20","20~"], "bins":[-1,0,1,2,3,4,5,10,20,100]},
        "x6": {"bin_labels":["0", "1"], "bins":[-1,0,1]},
        "x7": {"bin_labels":["0", "1"], "bins":[-1,0,1]},
        "x8": {"bin_labels":["-10％以上", "-10％~-7.5％","-7.5％~-5.0％","-5.0％~-2.5％","-2.5％~0％", "0％~2.5％", "2.5％~5.0％","5.0％~7.5％","7.5％~10.0％","10.0％以上" ], "bins":[-1,-0.1, -0.75, -0.5, -0.25, 0, 0.25, 0.5, 0.75, 0.1, 1]},
    }

    for position in ["ls", "l", "s"]:
        df_temp = df[df["position"] == position] if position in ["l", "s"] else df
        #選択された2変数をビニングし,カテゴリー変数を付与
        for var in [var1, var2]:
            labels = label_list[var]["bin_labels"]
            df_temp["{}_label".format(var)] = pd.cut(x=df_temp[var], bins=label_list[var]["bins"], labels=label_list[var]["bin_labels"])
        #カテゴリー化された2変数に対して、ピボットテーブルを作成(value:N)
        if margins:
            df_heatmap = pd.crosstab(df_temp["{}_label".format(var1)], df_temp["{}_label".format(var2)], margins=True)
        else:
            df_heatmap = pd.crosstab(df_temp["{}_label".format(var1)], df_temp["{}_label".format(var2)])
        dict_heatmap[position] = df_heatmap

    return dict_heatmap

#2変数間のplヒートマップ図の可視化。
def visualize_for_EV_by_heatmap(df, var1, var2, name_dir="", save=False):

    dict_pivot_pl = make_pivot_table_for_pl(df, var1, var2, margins=False)
    dict_pivot_N = make_pivot_table_for_N(df, var1, var2, margins=False)
    #描写領域の確保
    fig = plt.figure(figsize=(12,8))
    plt.subplots_adjust(wspace=0.3, hspace=0.6)
    positions = ["ls", "l", "s"]
    #２種類のヒートマップ図をポジション別にそれぞれ可視化(pl_atr, N)
    for i, position in enumerate(positions, 1):
        ax1 = fig.add_subplot(len(positions),2,i*2-1)
        ax1.set_title("<{}: pl_atr with {}&{}>".format(position,var1, var2))
        sns.heatmap(dict_pivot_pl[position], ax=ax1,vmin=-1, vmax=1,center=0, cmap="coolwarm",annot=True, fmt=".2f")
        ax2 = fig.add_subplot(len(positions),2,i*2)
        ax2.set_title("<{}: N with {}&{}>".format(position, var1, var2))
        sns.heatmap(dict_pivot_N[position], ax=ax2, vmin=0, vmax=1000,cmap="YlGn", annot=True, fmt="d")

    #save=0なら画像保存せずにfigureに表示する
    plt.savefig("analysis/{}/Heatmap with {}&{} for pl.png".format(name_dir,var1, var2)) if save else plt.show()









#------------------------------------<現在使ってない関数>----------------------------------------------

#トレード結果の集計。３つの売買区分（合算、ロング、ショート）別に集計して、結果を返す。
# def summary_PL_old(trade_list, display=1):

#     #目的の変数定義
#     result = {}
#     #構造を指定
#     result = {"ls":{}, "l":{}, "s":{}}
#     result["ls"] = {"N": 0, "N_P":0, "N_L":0, "total_P":0, "total_L":0, "max_P":0, "max_L":0, "max_NP":0, "max_NL":0}
#     result["l"] = {"N": 0, "N_P":0, "N_L":0, "total_P":0, "total_L":0, "max_P":0, "max_L":0, "max_NP":0, "max_NL":0}
#     result["s"] = {"N": 0, "N_P":0, "N_L":0, "total_P":0, "total_L":0, "max_P":0, "max_L":0, "max_NP":0, "max_NL":0}
    
#     #一時変数定義
#     counter_LS = 0#連勝数を格納
#     counter_L = 0
#     counter_S = 0

#     #日付順にトレードリストをsort。この処理は後に最大連勝数、最大連敗数をカウントするために行う。
#     sorted_trade_list = sorted(trade_list, key=lambda x: x["date"])

#     for trade in sorted_trade_list:
        
#         #トータルスコアを集計
#         result["ls"]["N"] += 1
#         if(trade["pl"] >= 0):
#             result["ls"]["N_P"] += 1 
#             result["ls"]["total_P"] += trade["pl"]
#             result["ls"]["max_P"] = max(result["ls"]["max_P"], trade["pl"])
#             #連勝数カウント
#             if counter_LS >= 0:
#                 counter_LS +=1
#             else:
#                 counter_LS = 1
#             result["ls"]["max_NP"] = max(counter_LS, result["ls"]["max_NP"])

#         else:
#             result["ls"]["N_L"] += 1
#             result["ls"]["total_L"] += trade["pl"]
#             result["ls"]["max_L"] = min(result["ls"]["max_L"], trade["pl"])
#             #連敗数カウント
#             if counter_LS <= 0:
#                 counter_LS -=1
#             else:
#                 counter_LS = -1
#             result["ls"]["max_NL"] = min(counter_LS, result["ls"]["max_NL"]*(-1))*(-1)

#         #ロングのスコアを集計
#         if(trade["position"] == "l"):

#             result["l"]["N"] += 1
#             if(trade["pl"] >= 0):
#                 result["l"]["N_P"] += 1 
#                 result["l"]["total_P"] += trade["pl"]
#                 result["l"]["max_P"] = max(result["l"]["max_P"], trade["pl"])
#                 #連勝数カウント
#                 if counter_L >= 0:
#                     counter_L +=1
#                 else:
#                     counter_L = 1
#                 result["l"]["max_NP"] = max(counter_L, result["l"]["max_NP"])

#             else:
#                 result["l"]["N_L"] += 1
#                 result["l"]["total_L"] += trade["pl"]
#                 result["l"]["max_L"] = min(result["l"]["max_L"], trade["pl"])
#                 #連敗数カウント
#                 if counter_L <= 0:
#                     counter_L -=1
#                 else:
#                     counter_L = -1
#                 result["l"]["max_NL"] = min(counter_L, result["l"]["max_NL"]*(-1))*(-1)
        
#         #ショートのスコアを集計
#         elif(trade["position"] == "s"):
#             result["s"]["N"] += 1
#             if(trade["pl"] >= 0):
#                 result["s"]["N_P"] += 1 
#                 result["s"]["total_P"] += trade["pl"]
#                 result["s"]["max_P"] = max(result["s"]["max_P"], trade["pl"])
#                 #連勝数カウント
#                 if counter_S >= 0:
#                     counter_S +=1
#                 else:
#                     counter_S = 1
#                 result["s"]["max_NP"] = max(counter_S, result["s"]["max_NP"])

#             else:
#                 result["s"]["N_L"] += 1
#                 result["s"]["total_L"] += trade["pl"]
#                 result["s"]["max_L"] = min(result["s"]["max_L"], trade["pl"])
#                 #連敗数カウント
#                 if counter_S <= 0:
#                     counter_S -=1
#                 else:
#                     counter_S = -1
#                 result["s"]["max_NL"] = min(counter_S, result["s"]["max_NL"]*(-1))*(-1)
                
#     keys = result.keys()

#     if(display == 1):#デフォルトでは結果をprintするように指定、表示が邪魔な場合は引数にdisplay=0を指定することで非表示にできる
#         for key in keys:
#             print("-----------------------------------------------")
#             print("<{}合算>".format(key.upper()))
#             print("総エントリー回数：{}".format(result[key]["N"]))
#             print("勝ちトレードの回数：{}".format(result[key]["N_P"]))
#             print("負けトレードの回数：{}".format(result[key]["N_L"]))
#             print("勝ちトレードの利益合計：{}".format(result[key]["total_P"]))
#             print("負けトレードの損失合計：{}".format(result[key]["total_L"]))
#             print("１トレードでの最大利益pt：{}".format(result[key]["max_P"]))
#             print("１トレードでの最大損失pt：{}".format(result[key]["max_L"]))
#             print("最大連勝数：{}".format(result[key]["max_NP"]))
#             print("最大連敗数：{}".format(result[key]["max_NL"]))

#         # print("-----------------------------------------------")
#         # print("<LS合算>")
#         # print("総エントリー回数：{}".format(result["ls"]["N"]))
#         # print("勝ちトレードの回数：{}".format(result["ls"]["N_P"]))
#         # print("負けトレードの回数：{}".format(result["ls"]["N_L"]))
#         # print("勝ちトレードの利益合計：{}".format(result["ls"]["total_P"]))
#         # print("負けトレードの損失合計：{}".format(result["ls"]["total_L"]))
#         # print("１トレードでの最大利益pt：{}".format(result["ls"]["max_P"]))
#         # print("１トレードでの最大損失pt：{}".format(result["ls"]["max_L"]))
#         # print("最大連勝数：{}".format(result["ls"]["max_NP"]))
#         # print("最大連敗数：{}".format(result["ls"]["max_NL"]))
#         # print("-----------------------------------------------")
#         # print("<L>")
#         # print("総エントリー回数：{}".format(result["l"]["N"]))
#         # print("勝ちトレードの回数：{}".format(result["l"]["N_P"]))
#         # print("負けトレードの回数：{}".format(result["l"]["N_L"]))
#         # print("勝ちトレードの利益合計：{}".format(result["l"]["total_P"]))
#         # print("負けトレードの損失合計：{}".format(result["l"]["total_L"]))
#         # print("１トレードでの最大利益pt：{}".format(result["l"]["max_P"]))
#         # print("１トレードでの最大損失pt：{}".format(result["l"]["max_L"]))
#         # print("最大連勝数：{}".format(result["l"]["max_NP"]))
#         # print("最大連敗数：{}".format(result["l"]["max_NL"]))
#         # print("-----------------------------------------------")
#         # print("<S>")
#         # print("総エントリー回数：{}".format(result["s"]["N"]))
#         # print("勝ちトレードの回数：{}".format(result["s"]["N_P"]))
#         # print("負けトレードの回数：{}".format(result["s"]["N_L"]))
#         # print("勝ちトレードの利益合計：{}".format(result["s"]["total_P"]))
#         # print("負けトレードの損失合計：{}".format(result["s"]["total_L"]))
#         # print("１トレードでの最大利益pt：{}".format(result["s"]["max_P"]))
#         # print("１トレードでの最大損失pt：{}".format(result["s"]["max_L"]))
#         # print("最大連勝数：{}".format(result["s"]["max_NP"]))
#         # print("最大連敗数：{}".format(result["s"]["max_NL"]))

#     return result

# #期待値を算出する関数
# def calc_EV_old(trade_list):
    
#     #変数、データ構造定義
#     result = {"ls":{}, "l":{}, "s":{}}
#     result["ls"]={"PL":0, "PO":0, "win_rate":0, "EV":0, "P_AVE":0, "L_AVE":0}
#     result["l"]={"PL":0, "PO":0, "win_rate":0, "EV":0, "P_AVE":0, "L_AVE":0}
#     result["s"]={"PL":0, "PO":0, "win_rate":0, "EV":0, "P_AVE":0, "L_AVE":0}

#     data = summary_PL_old(trade_list, display=0)

#     keys = result.keys()
    
#     for key in keys:

#         result[key]["PL"] = data[key]["total_P"] + data[key]["total_L"]
#         result[key]["PO"] = data[key]["total_P"]/data[key]["total_L"]*(-1) if data[key]["total_L"]!=0 else " - "
#         result[key]["win_rate"] = float(data[key]["N_P"])/data[key]["N"] if data[key]["N"]!=0 else " - "
#         result[key]["EV"] = (data[key]["total_P"] + data[key]["total_L"])/data[key]["N"]  if data[key]["N"]!=0 else " - "
#         result[key]["P_AVE"] = data[key]["total_P"]/data[key]["N_P"]  if data[key]["N_P"]!=0 else " - "
#         result[key]["L_AVE"] = data[key]["total_L"]/data[key]["N_L"]  if data[key]["N_L"]!=0 else " - "

#         print("---------------------")
#         print("<{}合算の期待値>".format(key.upper()))
#         print("総利益(pt): {}".format(result[key]["PL"]))
#         print("総エントリー回数:{}".format(data[key]["N"]))
#         print("ペイオフ値: {}".format(result[key]["PO"]))
#         print("勝率: {}％".format(result[key]["win_rate"]*100))
#         print("1トレードの期待値(EV): {}".format(result[key]["EV"]))
#         print("1トレードの平均利益(pt): {}".format(result[key]["P_AVE"]))
#         print("1トレードの平均損失(pt): {}".format(result[key]["L_AVE"]))
#         print("1トレードの最大利益(pt):{}".format(data[key]["max_P"]))
#         print("1トレードの最大損失(pt):{}".format(data[key]["max_L"]))
    
#     # #合算
#     # result["ls"]["PL"] = data["ls"]["total_P"] + data["ls"]["total_L"]
#     # result["ls"]["PO"] = data["ls"]["total_P"]/data["ls"]["total_L"]
#     # result["ls"]["win_rate"] = float(data["ls"]["N_P"])/data["ls"]["N"]
#     # result["ls"]["EV"] = (data["ls"]["total_P"] + data["ls"]["total_L"])/data["ls"]["N"]
#     # result["ls"]["P_AVE"] = data["ls"]["total_P"]/data["ls"]["N_P"]
#     # result["ls"]["L_AVE"] = data["ls"]["total_L"]/data["ls"]["N_L"]
#     # #ロング
#     # result["l"]["PL"] = data["l"]["total_P"] + data["l"]["total_L"]
#     # result["l"]["PO"] = data["l"]["total_P"]/data["l"]["total_L"]
#     # result["l"]["win_rate"] = float(data["l"]["N_P"])/data["l"]["N"]
#     # result["l"]["EV"] = (data["l"]["total_P"] + data["l"]["total_L"])/data["l"]["N"]
#     # result["l"]["P_AVE"] = data["l"]["total_P"]/data["l"]["N_P"]
#     # result["l"]["L_AVE"] = data["l"]["total_L"]/data["l"]["N_L"]
#     # #ショート
#     # result["s"]["PL"] = data["s"]["total_P"] + data["s"]["total_L"]
#     # result["s"]["PO"] = data["s"]["total_P"]/data["s"]["total_L"]
#     # result["s"]["win_rate"] = float(data["s"]["N_P"])/data["s"]["N"]
#     # result["s"]["EV"] = (data["s"]["total_P"] + data["s"]["total_L"])/data["s"]["N"]
#     # result["s"]["P_AVE"] = data["s"]["total_P"]/data["s"]["N_P"]
#     # result["s"]["L_AVE"] = data["s"]["total_L"]/data["s"]["N_L"]

#     # print("---------------------")
#     # print("<LS合算の期待値>")
#     # print("総利益(pt): {}".format(result["ls"]["PL"]))
#     # print("総エントリー回数:{}".format(data["ls"]["N"]))
#     # print("ペイオフ値: {}".format(result["ls"]["PO"]))
#     # print("勝率: {}％".format(result["ls"]["win_rate"]*100))
#     # print("1トレードの期待値(EV): {}".format(result["ls"]["EV"]))
#     # print("1トレードの平均利益(pt): {}".format(result["ls"]["P_AVE"]))
#     # print("1トレードの平均損失(pt): {}".format(result["ls"]["L_AVE"]))
#     # print("1トレードの最大利益(pt):{}".format(data["ls"]["max_P"]))
#     # print("1トレードの最大損失(pt):{}".format(data["ls"]["max_L"]))
    


#     # print("---------------------")
#     # print("<Lの期待値>")
#     # print("総利益(pt): {}".format(result["l"]["PL"]))
#     # print("総エントリー回数:{}".format(data["l"]["N"]))
#     # print("ペイオフ値: {}".format(result["l"]["PO"]))
#     # print("勝率: {}％".format(result["l"]["win_rate"]*100))
#     # print("1トレードの期待値(EV): {}".format(result["l"]["EV"]))
#     # print("1トレードの平均利益(pt): {}".format(result["l"]["P_AVE"]))
#     # print("1トレードの平均損失(pt): {}".format(result["l"]["L_AVE"]))
#     # print("1トレードの最大利益(pt):{}".format(data["l"]["max_P"]))
#     # print("1トレードの最大損失(pt):{}".format(data["l"]["max_L"]))

#     # print("---------------------")
#     # print("<Sの期待値>")
#     # print("総利益(pt): {}".format(result["s"]["PL"]))
#     # print("総エントリー回数:{}".format(data["s"]["N"]))
#     # print("ペイオフ値: {}".format(result["s"]["PO"]))
#     # print("勝率: {}％".format(result["s"]["win_rate"]*100))
#     # print("1トレードの期待値(EV): {}".format(result["s"]["EV"]))
#     # print("1トレードの平均利益(pt): {}".format(result["s"]["P_AVE"]))
#     # print("1トレードの平均損失(pt): {}".format(result["s"]["L_AVE"]))
#     # print("1トレードの最大利益(pt):{}".format(data["s"]["max_P"]))
#     # print("1トレードの最大損失(pt):{}".format(data["s"]["max_L"]))


#     return result