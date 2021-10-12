#!/usr/bin/env python3
# coding:utf-8

#検証における共通ガイドライン
"""
<検証方式一覧>
期待値計算方式： リスク量を固定したpt方式 
損益集計種別：合算・ロング・ショートの３つの種別

<検証項目一覧>
N(エントリー回数), N_P(勝ちトレードの回数　※収益０円は勝ちトレードにカウント）、N_L(負けトレードの回数)
total_P(利益の合計額), total_L(損失の合計額), max_P（最大利益pt）, max_L(最大損失pt), max_NP(最大連勝数）、max_NL(最大連敗数）

<検証項目から必ず算出されるべきデータ量一覧>
1: PL = total_P - total_L(pt単位のトータル損益)
2: PO=total_P/total_L(ペイオフ値)
3: win_rate = N_P/N = 1 - N_L/N (勝率。最大値は１)
4: EV=PL/N=PO*win_rate-(1-winrate)（１トレード当たりの期待値pt）
5: P_AVE = total_P/N_P(勝ちトレード１回あたりの平均利益pt)
6: L_AVE = total_L/N_L（負けトレード１回あたりの平均損失pt)

<関数(func_method)の作成ルール＞

ファイル作成の目的は、エントリー条件に合致するトレードを期間データの中から漏れなく抽出し、それをリスト形式にまとめた関数(func_method)を作ること。
なお、関数ファイル作成時には２つのルールを遵守する。

作成ルール1:

関数名は必ずファイル名と一致していること。(ファイル名:func_method.py→関数名:funk_method)

作成ルール2:

関数の戻り値となるリスト要素の一つ一つは辞書型データでまとめられ、各辞書データは以下のkeyを保有する必要がある。

リスト要素の必要項目（dict型）：エントリー日(key:date)、銘柄コード(key:code)、ロングorショートの区別(key:position), pt換算損益(key:pl)

実際の関数の戻り値は、このトレード結果の情報に、パラメータ情報を追加した以下のdict型で統一される。

{"result": トレード結果のリスト, "params": 使用したパラメータの値（引数の順番と一致）}

<関数作成(func_method)から期待値計算までの手順>

実際の期待値は、関数(func_method)により抽出されたトレードリスト(dict["result"]}を引数に取る関数calc_EV（)によって計算される。

なお、関数calc_EV(trade_list)は、3つの区分（ロング・ショート合計、ロング、ショート）で期待値を算出し、その結果をポジション種別("ls", "l", "s")をkeyに取るdict型で返す。

"""

#----------------------------------------------以下、プログラム開始↓↓↓-------------------------------------------------------

#この手法の概要
"""
寄付タイミングでの抵抗線ブレイク銘柄の順張り手法。抵抗ブレイク条件は前日の大引けから当日の寄付価格の間で、直近n日間の高値をx本以上ブレイクしたかで判定。(ショートはその逆)。nの初期値は20日。
"""

#トレード戦略（エントリー、決済ロスカット条件、その他の付加条件等）
"""
エントリー条件１:直近20日間の高値をx本以上,上回って寄付いたらロングエントリー
エントリー条件２:直近20日間の安値をx本以上,下回って寄り付いたらショートエントリー

決済条件１：利確条件は保有日数経過による大引け決済のみ。利食い指値は設定しない
決済条件２：保有期間中、直近２０日間のATRに倍率α（初期値:１)を掛けた値幅分逆行したらロスカット

備考１:寄付き価格と参照価格が同値なら本数ｘにカウントしない
"""

import pandas as pd
import datetime as dt
import statistics as st
# import module.module as md
import strategy.module.module as md#最終的に一階層上のexection.pyから実行することになるので、その位置からのパスを明示しないとエラーとなる。

#pandasのオプション設定
pd.set_option("display.max_rows", None)

# 今回はpandasのDataframe型を利用する
def break_of_resistance_at_open1(dataset, code, holding_days=0, duration=0, threshold=0, α=1):

    # 戻り値の変数定義
    trades = pd.DataFrame(columns=["date", "code", "position", "pl", "breaked"]) #各トレード結果のリストを格納。breakedは期間にブレイクされた日数
    params = [] #各パラメータを格納 ※リスト番号はdef定義時の引数の順番に対応（data_set,codeは除く)

    #tradesのデータ構造をキャスト
    trades["breaked"] = trades["breaked"].astype(int)

    #一時変数定義
    # trade = pd.DataFrame(columns=['date', 'code', 'position', 'pl']) #個々のトレードの結果を格納する変数
    position = "" #トレードの売買種別（L ro S)を格納
    counter_breaked = 0#直近何本の高値/安値がブレイクされたか
    ath = 0 #ATH(直近ｎ日間における一日の平均ボラティレティ)

    #検証のガイドライン(初回のみ表示させるためのif分)
    if(holding_days == 0 and duration==0 and threshold==0):
        #手法の概要説明
        print("<この手法の概要>")
        description = "寄付きタイミングでの抵抗線ブレイク順張り手法。ブレイク判定は直近n日間の高値をx本寄付き時点で抜けていたらロングエントリー。ショートはその逆"
        print(description)

        #手法のパラメータ説明
        print("<必要となるパラメータ>")
        description = "保有日数（holding_days),直近判定期間(duration、初期値は２０日),閾値（threshold,初期値は５本）"
        print(description)

        #検証初回はパラメータを入力させる
        print("パラメータ１：保有日数を入力してください")
        holding_days = int(input())
        params.append(holding_days)
        print("パラメータ２：直近判定期間を設定(duration)")
        duration = int(input())
        params.append(duration)
        print("パラメータ３：閾値（何本以上で抵抗ブレイク判定を出すか）を設定(threshold)")
        threshold = int(input())
        params.append(threshold)

    for index, data in dataset.iterrows():

        #データの先頭からX日間前のデータｈ参照できないのでスキップ（X:duration)
        if(index - duration < 0):
            continue
        #データの終わりからX日間後のデータは参照できないのでスキップ）(X:holding_days)
        if (index + holding_days > len(dataset)):
            continue
        #例外処理１：ストップ高（ストップ安）張り付きはエントリーできないので除外
        if (data["始値"] == data["高値"] and data["高値"] == data["安値"] and data["安値"] == data["終値"] and abs(dataset.loc[index-1, "終値"]- dataset.loc[index, "始値"])/dataset.loc[index, "始値"] > 0.1):
            continue    

        open_today = data["始値"]
        close_yesterday = dataset.loc[index-1, "終値"]
        # print(open_today)
        # print(close_yesterday)
        
        #GUなら高値ブレイク本数のカウント
        if(open_today > close_yesterday):
            # print(len(dataset.loc[index-duration:index-1].query("高値<@open_today & @close_yesterday<高値")))
            counter_breaked = len(dataset.loc[index-duration:index-1].query("高値<@open_today & @close_yesterday<高値"))
            position = "l"
            
        #GDなら安値ブレイク本数のカウント
        elif(open_today < close_yesterday):
            # print(len(dataset.loc[index-duration:index-1].query("安値 < @close_yesterday & @open_today < 安値")))
            counter_breaked = len(dataset.loc[index-duration:index-1].query("安値 < @close_yesterday & @open_today < 安値"))
            position = "s"

        #閾値を超えた日はエントリー！trade結果を集計
        if(counter_breaked >= threshold):  
            # print("閾値を超えました！")   
            pl = md.calc_PL_with_open(dataset, index, position, holding_days, 5, α)
            # print(position)
            # print(pl)
            #今回のトレード結果
            trade = pd.Series([data["日付"], code, position, pl, counter_breaked],index=["date", "code", "position", "pl", "breaked"])
            # print(trade)
            #トレード結果をテーブルへ追加
            trades = trades.append(trade,ignore_index=True)

        #次のループへのパラメータ調整
        counter_breaked = 0
        atr = 0
        position = ""

    return {"result": trades, "params": params}



# dataset = md.get_data("../dataset/nikkei225_daily/nikkei225_2006.csv")
# dataset = md.get_data("../dataset/sample_dataset/2150_5year.csv")
dataset = md.get_data("../dataset/data_market_capitalization_top100/9984.csv")
# dataset = md.get_data("../dataset/NI225/nikkei225_20010903_20210930.csv")

summary = break_of_resistance_at_open1(dataset, "sample", 3, 20, 8)
result = summary["result"]
print("------------結果---------------")
print(result)
print(result.describe())
