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


<関数作成の目的>

関数作成における目的は、
1: ノイズを除去できる最小限のエントリー条件を指定して、
2: その条件に見合うトレードをサンプルデータの中から全て漏れなく抽出し
3: その結果をDataFrame型のデータとしてまとめる
ことである。

ここで、1:最小限のエントリー条件を設定するために適切なパラメータを指定しなければならない。
ただし、ここでの目的はあくまでスクリーニングとしての機能を果たすことにあるので、ノイズを除去できる程度の小さな数字が妥当といえる。
この値が大きすぎると、優位性のある領域をノイズとして除外してしまうリスクが生じる。

(スクリーニング条件としてのパラメータが持つ意味と、検証における説明変数としてのパラメータの意味を混同していたので注意)

この意味を踏まえると、手法関数(func_method)実行時に引数として渡すパラメータ値はあくまでスクリーニングを果たすだけのものなので、
データ量が多くて検証に時間がかかる場合を除いて、一度設定したパラメータ値は基本的にその後いじることはない。

各トレード結果の説明変数としてのパラメータX1は、後に目的変数Y（pl）と一緒にDataFrame型の要素として保持することになるので、スクリーニング条件を始めから厳しく設定しすぎる必要はない。

<関数(func_method)の作成ルール>

関数ファイル作成時には２つのルールを遵守する。

[ルール1]

関数名は必ずファイル名と一致していること。(ファイル名:func_method.py　→　関数名:funk_method)

[ルール２]

ファイル名の命名規則は以下のルールを守る。

(エントリータイミング)_(順張りor逆張り/follow or resist)_(決済タイミング)_(スクリーニングに用いた説明変数).py

<例>寄付での順張りエントリー,大引け返済ルールの手法ならopen_follow_close_X1.py

[ルール3]

DataFrame型のテーブルとしてまとめられた各トレード結果は以下のcolumn要素を持つデータとして格納される。

column：エントリー日(key:date)、銘柄コード(key:code)、ロングorショートの区別(key:position), pt換算損益(key:pl_lc), 各説明変数X1,X2,X3,・・・・

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
Y1:pl_lc(ロスカット幅に対する損益)
Y2:pl_ATR(ATRに対する損益)


(優位性が潜んでいそうな説明変数)
X1: 当日寄付価格の前日に対するGU幅(直近２０日のATRに対する比率で計算)
X2: 当日の出来高規模（直近２０日の出来高平均に対する比率で計算)
X3: 前日引け~当日寄付までの間に直近２０日の高値を巻き込んだ本数
X4: 直近６０日間に、当日寄付時点で依然として上にある高値の本数
X5: 前日引け~当日寄付きまでの間に、連続して高値を巻き込んだ本数
X6: 前日がATR幅以上の下落であるかどうか(大陰線全返しの検証)
X7: 前日が陰線であるかどうか
X8: 当日寄付の日経の前日比



# X: 決算発表が前日にあったかどうか
# X: 寄付の約定枚数(直近20日の出来高平均に対する比率)
# X: 寄付の約定枚数(発行済株式数に対する比率)
# X: 寄付の約定枚数(浮動株に対する比率)
# X: 当日時点に残った信用買いの浮動株に対する割合
# X: 当日時点に残った信用売りの浮動株に対する割合
# X: 当日NY市場の前日比
# X: 当日USD/JPYの前日比

このうち値の算出に固有のパラメータを必要とするのはX1,X2, X3, X4。
"""

#----------------------------------------------以下、プログラム開始↓↓↓-------------------------------------------------------

#この手法の概要（スクリーニング条件）
"""
大きなギャップが発生した日に指値待機して、約定したら〇日後の大引けで決済する順張り手法の検証。
"""

#スクリーニング条件
"""
当日のGU/GD幅が前日比２％以上(更新値幅の上限が2％なので、それを超える水準で寄付を迎える場合,必ず特別気配スタートとなる)
"""

#トレード戦略（エントリー、決済ロスカット条件）
"""

エントリー条件１:当日寄付きが前日比2％(GU)以上ならロングエントリー
エントリー条件２:当日寄付きが前日比-2％(GD)以下ならショートエントリー

決済条件１：利確条件は保有日数経過による大引け決済のみ。利食い指値は設定しない
決済条件２：保有期間中、直近２０日間のATRに倍率α（初期値:１)を掛けた値幅分逆行したらロスカット

"""

import pandas as pd
import datetime as dt
import statistics as st

#モジュール内でテストを実行する場合はこっちを利用
if __name__ == "__main__":
    import module.module as md 
    import module.module_calc_variable as mcv
    df_NI225 = pd.read_csv("../dataset/NI225/nikkei225_20010903_20211110.csv")#検証に必要なファイルの事前読み込み

#exection.pyで実行する場合はこっちを有効。
else:
    import strategy.module.module as md#最終的に一階層上のexection.pyから実行することになるので、その位置からのパスを明示しないとエラーとなる。
    import strategy.module.module_calc_variable as mcv
    df_NI225 = pd.read_csv("./dataset/NI225/nikkei225_20010903_20211110.csv")#検証に必要なファイルの事前読み込み

#pandasのオプション設定
pd.set_option("display.max_rows", None)

# 今回はpandasのDataframe型を利用する
def after_open_follow_close(dataset, code, holding_days, α, atr_ratio=2, params_x1=20, params_x2=20, params_x3=20, params_x4=60):#入力パラメータは基本的には保有日数のみでいい。

    # 戻り値の変数定義
    trades = pd.DataFrame(columns=["date", "code", "position", "pl_lc","pl_atr",  "x1", "x2", "x3", "x4", "x5", "x6", "x7", "x8", "x9", "x10"]) #各トレード結果のリストを格納。breakedは期間にブレイクされた日数,ratioはギャップ幅とATRとの比率
    params = [] #保有日数、LC乗数値α、各説明変数に用いたパラメータ値(X1, X2, X3, X4)を格納 ※リスト番号はdef定義時の引数の順番に対応（data_set,codeは除く)

    #データ構造をキャスト
    trades["pl_lc"] = trades["pl_lc"].astype(float)
    trades["pl_atr"] = trades["pl_atr"].astype(float)
    trades["x1"] = trades["x1"].astype(float)
    trades["x2"] = trades["x2"].astype(float)
    trades["x3"] = trades["x3"].astype(int)
    trades["x4"] = trades["x4"].astype(int)
    trades["x5"] = trades["x5"].astype(int)
    trades["x6"] = trades["x6"].astype(int)
    trades["x7"] = trades["x7"].astype(int)
    trades["x8"] = trades["x8"].astype(float)
    trades["x9"] = trades["x9"].astype(float)
    trades["x10"] = trades["x10"].astype(float)

    #独自パラメータが必要な説明変数のパラメータ設定
    params_duration = [params_x1, params_x2, params_x3, params_x4]
        
    #検証
    for index, data in dataset.iterrows():

        #トレード結果
        trade = pd.Series(index=["date", "code", "position", "pl_lc", "pl_atr", "x1","x2", "x3", "x4", "x5", "x6", "x7", "x8", "x9", "x10"])

        #検証前処理
        #データの先頭からX日間前のデータｈ参照できないのでスキップ（X:duration)
        if(index - max(params_duration) < 0):
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

        # 当日始値時点における前日比
        gap_rate = (open_today - close_yesterday)/close_yesterday
        # print("---gaprate---")
        # print(gap_rate)
        
        #前日比±2％以下の変動幅はギャップ無しの為スキップ
        if(-0.02 < gap_rate and gap_rate < 0.02):
            continue

        #指値価格の算出
        atr = md.calc_ATR(dataset, index)
        limit_price = close_yesterday + atr*atr_ratio if open_today > close_yesterday else close_yesterday - atr*atr_ratio

        #ギャップがあったとしても、寄付エントリーになってしまう場合はopen_follow_close手法と検証結果が被るのでスキップ
        if(open_today > close_yesterday and limit_price>=open_today):
            continue
        elif(open_today < close_yesterday and limit_price<=open_today):
            continue
        
        #指値が刺さらなかったらスキップ
        if(open_today > close_yesterday and limit_price <= dataset.loc[index, "安値"]):
            continue
        elif(open_today < close_yesterday and limit_price >= dataset.loc[index, "高値"]):
            continue

        #指値待機＆約定したパターンのトレード結果集計

        trade["date"] = data["日付"]
        trade["position"] = "l" if gap_rate >0 else "s"
        trade["code"] = code
        trade["pl_lc"] = md.calc_pl_with_after_open(dataset, index, holding_days, limit_price)
        trade["pl_atr"] = trade["pl_lc"] * α
        trade["x1"] = mcv.calc_x1(dataset, index, params_x1)
        trade["x2"] = mcv.calc_x2(dataset, index, params_x2)
        trade["x3"] = mcv.calc_x3(dataset, index, params_x3)
        trade["x4"] = mcv.calc_x4(dataset, index, params_x4)
        trade["x5"] = mcv.calc_x5(dataset, index)
        trade["x6"] = mcv.calc_x6(dataset, index)
        trade["x7"] = mcv.calc_x7(dataset, index)
        trade["x8"] = mcv.calc_x8(dataset, df_NI225, index)
        trade["x9"] = mcv.calc_x9(dataset, index)
        trade["x10"] = mcv.calc_x10(dataset, index)

        trades = trades.append(trade,ignore_index=True)

        # print("----trade結果---")
        # print(trade)

    return {"result": trades, "params": params}

#プログラムテスト用
if __name__ == '__main__':

    # dataset = md.get_data("../dataset/nikkei225_daily/nikkei225_2020.csv")
    dataset = md.get_data("../dataset/sample_dataset/5218_5year.csv")
    # dataset = md.get_data("../dataset/data_market_capitalization_top100/9984.csv")

    # print(dataset)
    summary = after_open_follow_close(dataset, "sample", 1, 1)
    result = summary["result"]
    print("------------結果---------------")
    print(result)
    print(result.describe())
    # print("----------x2>2の結果------------")
    # print(result.loc[result["x2"] > 2].describe())
