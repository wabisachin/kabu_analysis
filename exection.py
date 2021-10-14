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
print("<検証した分析手法の番号を選択してください(半角数字）>")
[print("{}: {}".format(i,s.replace("./strategy/", ""))) for i, s in enumerate(strategys)]
selected_method_label = int(input())
selected_method = strategys_name[selected_method_label]
#選択された分析手法のmoduleをimport
exec("import strategy.{} as st".format(selected_method))

#変数定義
results = pd.DataFrame() #全銘柄のトレード結果を格納
params = [] #設定パラメータを保持

for data_name in selected_dataset:
    
    data = mc.get_data("{}".format(data_name))
    # print(data)
    code = data_name.replace(datasets[selected_label] + "/", "").replace(".csv", "")#ファイル名の拡張子（.csv）を取り除いた銘柄コード
    print(code)
    #手法検証開始
    summary = eval("st.{}(data, code, *params)".format(selected_method))

    result = summary["result"]
    params = summary["params"] if params == [] else params#ループ中、何度も同じパラメータを入力させられる手間を省くための処理
    
    results = results.append(result)

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

# ev = mc.calc_EV(results)
# print("")
# print("-----------------最終結果まとめ------------------")
# print("")
# print(ev)
# print("")