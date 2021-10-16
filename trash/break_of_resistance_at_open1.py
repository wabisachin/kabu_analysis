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
2: PF = total_P/total/L(プロフィットファクター)
3: win_rate = N_P/N = 1 - N_L/N (勝率。最大値は１)
4: P_AVE = total_P/N_P(勝ちトレード１回あたりの平均利益pt)
5: L_AVE = total_L/N_L（負けトレード１回あたりの平均損失pt)
6: PO=P_AVE/L_AVE(ペイオフ値)
7: EV=PL/N=PO*win_rate-(1-winrate)（１トレード当たりの期待値pt）


<手法関数作成の目的とゴール>

各手法関数作成における目的は、ノイズを除去できる最小限のエントリー条件を指定して、
そのエントリー条件に合致するトレードを期間データの中から全て漏れなく抽出し、その結果をDataFrame型データとしてまとめることである。

ここで、最小限のエントリー条件に用いるパラメータ数値は、あくまでスクリーニングとしての意味合いであることに注意する。
(スクリーニング条件としてのパラメータが持つ意味と、検証における説明変数としてのパラメータの意味を混同していたので注意)

この意味を踏まえると、手法関数(func_method)実行時に引数として渡すエントリー条件のパラメータ（今回であれば、GU判定の閾値）はあくまでスクリーニング機能としての数値なので、ノイズを除去できそうな基準の最小値を最初に設定して以降、一切イジる必要のない数値である。
各トレード結果の説明変数としてのパラメータX1は、後に目的変数Y（pl）と一緒にDataFrame型の要素として保持することになるので、スクリーニング条件を始めから厳しく設定しすぎる必要はない。ノイズによるデータ量を削減できる程度であればいい。

<関数(func_method)の作成ルール>

関数ファイル作成時には２つのルールを遵守する。

作成ルール1:

関数名は必ずファイル名と一致していること。(ファイル名:func_method.py　→　関数名:funk_method)

作成ルール2:

DataFrame型のテーブルとしてまとめられた各トレード結果は以下のcolumn要素を持つデータとして格納される。

column：エントリー日(key:date)、銘柄コード(key:code)、ロングorショートの区別(key:position), pt換算損益(key:pl), 各説明変数X1,X2,X3,・・・・

なお実際の戻り値は、このトレード結果の情報に、使用したパラメータ情報を追加したdict型データとして返される。

{"result": トレード結果のテーブル(DataFrame型), "params": 使用したパラメータの値（引数の順番と一致）}

<関数作成(func_method)から期待値計算までの手順>

実際の期待値は、関数(func_method)により抽出されたトレードリスト(dict["result"]}を引数に取る関数calc_EV（)によって計算される。

なお、関数calc_EV(df)は、3つの区分（ロング・ショート合計、ロング、ショート）で期待値をそれぞれ算出し、
その結果をポジション種別("ls", "l", "s")をkeyに取るdict型で返す。
ちなみにkeyの要素はトレード結果を格納するので、もちろんDataFrame型である。

<分析における目的変数と説明変数の一覧>
※解説はロングポジションの場合。ショートは高値を安値に読み替える。

(目的変数)
Y:pl(損益)

(優位性が潜んでいそうな説明変数)
X1: 当日寄付価格の前日に対するGU幅(直近２０日のATRに対する比率で計算)
X2: 当日の出来高規模（直近２０日の出来高平均に対する比率で計算)
X3: 前日引け~当日寄付までの間に直近２０日の高値を巻き込んだ本数
X4: 直近６０日間に、当日寄付で依然として高値を巻き込めていない本数
X5: 前日引け~当日寄付きまでの間に、連続して高値を巻き込んだ本数
X6: 決算発表が前日にあったかどうか
X7: 寄付の約定枚数(直近20日の出来高平均に対する比率)
X8: 寄付の約定枚数(発行済株式数に対する比率)
X9: 寄付の約定枚数(浮動株に対する比率)
X10:当日時点に残った信用買いの浮動株に対する割合
X11:当日時点に残った信用売りの浮動株に対する割合
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
# dataset = md.get_data("../dataset/sample_dataset/2929_5year.csv")
# dataset = md.get_data("../dataset/data_market_capitalization_top100/7751.csv")
# dataset = md.get_data("../dataset/NI225/nikkei225_20010903_20210930.csv")

# summary = break_of_resistance_at_open1(dataset, "sample", 3, 20, 8)
# result = summary["result"]
# print("------------結果---------------")
# print(result)
# print(result.describe())
