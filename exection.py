#!/usr/bin/env python2
# coding:utf-8

#複数銘柄分析の実行ファイル。

import glob
import pandas as pd
import module.module_calclation as mc

#フォルダ内にあるデータセットを取得
datasets = glob.glob("./dataset/*")
#パスを削除して、フォルダ名のみを抽出
datasets_name = [s.replace("./dataset/", "") for s in datasets]
#検証データセットを選択
print("<検証したいデータセットの番号を選択してください(半角数字）>")
[print("{}: {}".format(i,s.replace("./dataset/", ""))) for i, s in enumerate(datasets)]
selected_label = int(input())

selected_dataset = glob.glob("./dataset/{}/*".format(datasets_name[selected_label]))

#フォルダ内にある分析手法を取得
strategys = glob.glob("./strategy/*")
#パスを削除して、フォルダ名のみを抽出
strategys_name = [s.replace("./strategy/", "").replace(".py", "") for s in strategys]
#分析手法を選択
print("<検証したい分析手法の番号を選択してください(半角数字）>")
[print("{}: {}".format(i,s.replace("./strategy/", ""))) for i, s in enumerate(strategys)]
selected_method_label = int(input())
selected_method = strategys_name[selected_method_label]
#選択された分析手法のmoduleをimport
exec("import strategy.{} as st".format(selected_method))

#保有日数の入力
print("パラメータ１：保有日数を入力してください")
holding_days = int(input())

#損切り逆指値乗数αの値を入力
print("逆指値乗数αの値を入力してください(0.5<α<2.0)")
α = float(input())

#変数定義
results = pd.DataFrame() #全銘柄のトレード結果を格納
params = [] #設定パラメータを保持

for data_name in selected_dataset:
    
    data = mc.get_data("{}".format(data_name))
    # print(data)
    code = data_name.replace(datasets[selected_label] + "/", "").replace(".csv", "")#ファイル名の拡張子（.csv）を取り除いた銘柄コード
    print(code)
    #手法検証開始
    summary = eval("st.{}(data, code, holding_days, α, *params)".format(selected_method))

    result = summary["result"]
    params = summary["params"] if params == [] else params#ループ中、何度も同じパラメータを入力させられる手間を省くための処理
    
    results = results.append(result)

#文字列型の日付データをdatetime型に変えてデータの古い順にsort
# results["date"] = pd.to_datetime(results["date"], format="%Y%m%d")
# results.sort_values("date", inplace=True)
#indexの番号が変わっていないので振り直す
results.reset_index(drop=True,inplace=True)
# results = results.iloc[::-1]
#csv出力を選択
print("結果をcsv出力するか選んでください(y/n)")
flag = input()

if(flag=="y"):
    results.to_csv("result/{}__{}__{}days__{}.csv".format(datasets_name[selected_label], selected_method, holding_days, α), index=False)

# print(results)
print("------------結果---------------")
print(results)
print(results.describe())
print("----------x2>2の結果------------")
print(results.loc[results["x2"] > 2].describe())
print("----------x2>3の結果------------")
print(results.loc[results["x2"] > 3].describe())
print("----------x2>5の結果------------")
print(results.loc[results["x2"] > 5].describe())
print("----------x2>7の結果------------")
print(results.loc[results["x2"] > 7].describe())

# print("----------x2>2, 5<x1<6の結果------------")
# print(results.loc[(results["x2"] > 2) & (results["x1"] > 5)& (results["x1"] <6)].describe())
# print("----------x2>3, 2<x1<7の結果------------")
# print(results.loc[(results["x2"] > 3) & (results["x1"] > 5)& (results["x1"] <6)].describe())
# print("----------x2>5, 2<x1<7の結果------------")
# print(results.loc[(results["x2"] > 5) & (results["x1"] > 5)& (results["x1"] <6)].describe())
# print("----------x2>7, 2<x1<7の結果------------")
# print(results.loc[(results["x2"] > 7) & (results["x1"] > 5)& (results["x1"] <6)].describe())

# print("----------x2>2, x1<1の結果------------")
# print(results.loc[(results["x2"] > 2) & (results["x1"]<1)].describe())
# print("----------x2>3, x1<1の結果------------")
# print(results.loc[(results["x2"] > 3) & (results["x1"]<1)].describe())
# print("----------x2>5, x1<1の結果------------")
# print(results.loc[(results["x2"] > 5) & (results["x1"]<1)].describe())
# print("----------x2>7, x1<1の結果------------")
# print(results.loc[(results["x2"] > 7) & (results["x1"]<1)].describe())

# print("----------x1<2の結果------------")
# print(results.loc[results["x1"] < 2].describe())
# print("----------x1>2の結果------------")
# print(results.loc[results["x1"] > 2].describe())
# print("----------x1>5の結果------------")
# print(results.loc[results["x1"] > 5].describe())
# print("----------x1>7の結果------------")
# print(results.loc[results["x1"] > 7].describe())


# print("----------x1<1の結果(偽陽性の判定)------------")
# print(results.loc[(results["x1"] > 5)& (results["x1"] <6)].describe())


# ev = mc.calc_EV(results)
# print("")
# print("-----------------最終結果まとめ------------------")
# print("")
# print(ev)
# print("")