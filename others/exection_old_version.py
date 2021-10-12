#!/usr/bin/env python2
# coding:utf-8

#複数銘柄分析の実行ファイル。

import glob
import module.module_calclation as mc
# import strategy.trend_change_days_in_a_low as tc

#フォルダ内にあるデータセットを取得
datasets = glob.glob("./dataset/*")
#パスを削除して、フォルダ名のみを抽出
datasets_name = [s.replace("./dataset/", "") for s in datasets]
#検証データセットを選択
print("<検証したいデータセットの番号を選択してください(半角数字）>")
[print("{}: {}".format(i,s.replace("./dataset/", ""))) for i, s in enumerate(datasets)]
selected_label = int(input())

selected_dataset = glob.glob("./dataset/{}/*".format(datasets_name[selected_label]))
# print("--------選択されたデータセットのリスト--------")
# print(selected_dataset)

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
exec("import strategy.{} as tc".format(selected_method))

#変数定義
results = [] #全銘柄のトレード結果を格納
params = [] #設定パラメータを保持

for data_name in selected_dataset:
    
    data = mc.get_data_from_csv("{}".format(data_name))
    # print("-------データセット名-------")
    # print(data_name)
    code = data_name.replace(datasets[selected_label] + "/", "").replace(".csv", "")#ファイル名の拡張子（.csv）を取り除いた銘柄コード

    #手法検証
    # summary = tc.trend_change_days_in_a_low(data, code, *params)
    summary = eval("tc.{}(data, code, *params)".format(selected_method))

    result = summary["result"]
    params = summary["params"] if params == [] else params#ループ中、何度も同じパラメータを入力させられる手間を省くための処理
    # print(result)
    # mc.calc_EV(result)
    results.extend(result)

print(results)

print("<全てのトレード結果集計>")
mc.calc_EV(results)