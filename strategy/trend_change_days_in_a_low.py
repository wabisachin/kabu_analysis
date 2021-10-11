#!/usr/bin/env python3
# coding:utf-8

#検証における共通ガイドライン
"""
<品質を一律に守るためにすべての検証で守られるべき要項一覧>
期待値計算方式の明示： リスク量を固定したpt方式 or 資金量を固定したパーセント方式
合算・ロング・ショートの３つの種別で損益を集計

<検証項目一覧>
N(エントリー回数), N_P(勝ちトレードの回数　※収益０円は勝ちトレードにカウント）、N_L(負けトレードの回数)
total_P(利益の合計額), total_L(損失の合計額), max_P（最大利益pt）, max_L(最大損失pt), max_NP(最大連勝数）、max_NL(最大連敗数）

<検証項目から必ず算出されるべきデータ項目一覧>
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

関数名(func_method)は必ずファイル名(func_method.py)と一致していること。

作成ルール2:

関数の戻り値となるリスト要素の一つ一つは辞書型データでまとめられ、各辞書データは以下のkeyを保有する必要がある。

リスト要素の必要項目（dict型）：エントリー日(key:date)、銘柄コード(key:code)、ロングorショートの区別(key:position), pt換算損益(key:pl)

実際の関数の戻り値は、このトレード結果の情報に、パラメータ情報を追加した以下のdict型で統一される。

{"result": トレード結果のリスト, "params": 使用したパラメータの値（引数の順番と一致）}

<関数作成(func_method)から期待値計算までの手順>

実際の期待値は、関数(func_method)により抽出されたトレードリスト(dict["result"]}を引数に取る関数calc_EV（)によって計算される。

なお、関数calc_EV(trade_list)は、3つの区分（ロング・ショート合計、ロング、ショート）で期待値を算出し、その結果をポジション種別("ls", "l", "s")をkeyに取るdict型で返す。

"""

#この手法の概要
"""
直近〇日連続で終値が前日終値を上回り、当日は前日の安値以下で引けるときに大引けでエントリーする手法の期待値を検証。（ロングはその逆）

注意点として、この手法は損切り幅（リスク量固定）を基準にしたpt方式による期待値計算と、
資金量を一律にして（資金量固定）、そのパーセンテージを利益として積んでいくパーセント方式による期待値計算で結果が大きく異なる可能性がある。
この手法は宵越しを前提とするため、当日の寄付きを前提とした今のメイン手法と比べてロスカットに想定以上に大きなスリッページが入る確率が上がっている。
ただ、その影響は想定最大やられptを多めに見積もることによって、結果として同じように管理できる可能性が高いので、pt方式による期待値計算を優先した。
"""

#トレード戦略（エントリー、決済ロスカット条件、その他の付加条件等）
"""
エントリー条件１:直近〇日間連続して当日終値が前日終値を上回り、かつ当日終値が前日安値を下回ったらエントリー（ショート）
エントリー条件２:直近〇日間連続して当日終値が前日終値を下回り、かつ当日終値が前日高値を上回ったらエントリー（ロング）

決済条件１：利確条件は保有日数経過による大引け決済のみ。利食い指値は設定しない
決済条件２：ロングなら（前日or当日の安値のいずれか安い方）に触れたとき、ショートなら（前日or当日の高値のいずれか高い方）に触れた時に逆指値決済

備考１:引け値が前日比±0の場合は連続日数をリセット
備考２:前日の高値（安値）と引け値が同値ならエントリーしない。
"""
#備考欄
"""
１：手法は最終的に関数として定義される。その戻り値は、エントリー基準に合致した個々のトレードのリスト形式として返す。
そして、要素の一つ一つは以下の項目を満たした辞書形式で統一する。
｛エントリー日、銘柄コード、ロングorショートの区別,pt換算損益｝
そして、最終的にはこの統計分析をすることを念頭に、もうこの段階で、pandasで分析しやすいように型変換した形で返すのがいいかもしれない。

"""
#プログラム実装にあたる留意点、注意点、懸念点
"""
注意点として。この手法は損切り幅（リスク量固定）を基準にしたpt方式による期待値計算と、
資金量を一律にして（資金量固定）、そのパーセンテージを利益として積んでいくパーセント方式による期待値計算で結果が大きく異なる可能性が高い。
更にこの手法は宵越しを前提とするため、当日の寄付きを前提とした今のメイン手法と比べてロスカットが想定以上に膨らむ可能性を含んでいる。
ただ、その影響とて想定最大やられptを多めに見積もることによって、結果として同じように管理できる可能性が高いので、少額資金前提のpt方式による期待値計算を優先することにした。
１トレード毎のリスク量をコントロールするほうが資金管理戦略としては理にかなっている。
"""

#----------------------------------------------以下、プログラム開始↓↓↓-------------------------------------------------------

# import module
# import module_calculation as cl

# data_set = module.get_data_from_csv("./nikkei225_daily/nikkei225_2020.csv")

# #トレードリスト定義
# trade_list = []

# #変数定義
# data_label = 0 #現在のデータ番号を格納
# counter = 0 #連続上昇or下落日数のカウント（上昇なら+１、下落なら-1）

# #各種パラメータ定義（3種以内が望ましい）
# stock_code = "NI225" #銘柄コード
# consevtive_days = 3 #終値上昇or下落の連続日数
# holding_days = 5 #保有日数

# #一時変数定義
# trade = {} #個々のトレードの結果を格納する変数
# total_sample = 0
# n_sample = 0

# #手法検証のための関数(※完成するまではいいけど、最後まとめるときは関数として定義しておく！！)

# for data in data_set:

#     #データ前処理１：検証初日は前日データを参照できないのでスキップ
#     if(data_label == 0):
#         data_label += 1
#         continue
#     #データ前処理２：データの最後から起算して、保有日数を超える分のデータは損益計算できないのでスキップ
#     if(data_label >=len(data_set) - holding_days):
#         break

#     #例外処理１：ストップ高（ストップ安）張り付きはエントリーできないので除外
#     if (data[1] == data[2] and data[2] == data[3] and data[3] == data[4] and abs(data[1]-data_set[data_label-1][4])/data_set[data_label-1][1] > 0.1):
#         data_label += 1
#         continue

#     #連続日数が規定を超えたらその日の動きを監視

#     #連続上昇日数が基準を超えて、かつ前日の安値を下回って引けたらショートエントリー
#     if(counter >= consevtive_days and data_set[data_label][4] < data_set[data_label-1][3]):
#         print("------------------------------------------")
#         print(data)
#         print('連続{}日上昇！ショートエントリー'.format(counter))

#         #損益計算
#         entry_price = data_set[data_label][4]
#         exit_price = data_set[data_label + holding_days][4]
#         losscut_price = max(data_set[data_label][2], data_set[data_label - 1][2])
#         losscut_range = abs(losscut_price - entry_price)

#         pl = entry_price - exit_price

#         #もし逆指値条件に引っかかるなら損益plを書き換え
#         for i in range(holding_days):
#             if (losscut_price <= data_set[data_label + (i+1)][1]):
#                 print("ショートポジが寄付でロスカットされました")
#                 pl = entry_price - data_set[data_label + (i+1)][1]
#                 break
#             elif(losscut_price <= data_set[data_label + (i+1)][2]):
#                 print("ショートポジがザラバ中にロスカットされました！！")
#                 pl = losscut_range*(-1)
#                 break
#         print(entry_price)
#         print(losscut_price)
#         print(exit_price)
#         print(losscut_range)
#         print("損益は{}円です".format(pl))
#         print("調整前のplは{}".format(pl))
#         pl = round(pl/losscut_range, 3)
#         print("損益は{}ptです".format(pl))
#         # print(holding_days)
#         trade["date"] = data[0]
#         trade["code"] = stock_code
#         trade["position"] = "s"
#         trade["pl"] = pl


#         trade_list.append(trade)
#         total_sample+=pl
#         n_sample += 1
        
#     #連続下落日数が基準を超えて、かつ前日の高値を上回って引けたらロングエントリー
#     if(counter <= consevtive_days*(-1) and data_set[data_label][4] > data_set[data_label - 1][2]):
#         print("------------------------------------------")
#         print('連続{}日下落！ロングエントリー'.format(counter*(-1)))
#         print(data)

#         #損益計算
#         entry_price = data_set[data_label][4]
#         exit_price = data_set[data_label + holding_days][4]
#         losscut_price = min(data_set[data_label][3], data_set[data_label - 1][3])
#         losscut_range = abs(losscut_price - entry_price)

#         pl = exit_price - entry_price

#         #もし逆指値条件に引っかかるなら損益plを書き換え
#         for i in range(holding_days):
#             if (losscut_price >= data_set[data_label + (i+1)][1]):
#                 print("ロングポジが寄付でロスカットされました")
#                 pl = data_set[data_label + (i+1)][1] - entry_price
#                 break
#             elif(losscut_price >= data_set[data_label + (i+1)][3]):
#                 print("ロングポジがザラバ中にロスカットされました！！")
#                 pl = losscut_range*(-1)
#                 break
#         print(entry_price)
#         print(losscut_price)
#         print(exit_price)
#         print(losscut_range)
#         print("損益は{}円です".format(pl))
#         pl = round(pl/losscut_range, 3)
#         print("損益は{}ptです".format(pl))
#         # print(holding_days)
#         total_sample+=pl
#         n_sample += 1

#         trade["date"] = data[0]
#         trade["code"] = stock_code
#         trade["position"] = "l"
#         trade["pl"] = pl


#         trade_list.append(trade)



#     #連続高値引けパターンの条件分岐

#     #連続上昇なら連続日数をカウント
#     if(counter >= 0 and data_set[data_label][4] > data_set[data_label-1][4]):
#         counter += 1
#      #連続下落なら連続日数をカウント
#     elif(counter<=0 and data_set[data_label][4] < data_set[data_label-1][4]):
#         counter -= 1
#     #連続上昇中だったならカウンターをリセットして連続日数-１に書き換え
#     elif(counter > 0 and data_set[data_label][4] < data_set[data_label-1][4]):
#         counter = -1
#     #連続下落中だったならカウンターをリセットして連続日数＋１に書き換え
#     elif(counter < 0 and data_set[data_label][4] > data_set[data_label-1][4]):
#         counter = 1
#     #前日比±0で引けたらカウンターリセット
#     else:
#         counter = 0
    
#     #次のループへのパラメータ調整
#     data_label += 1
#     trade = {}

# print(trade_list)

# cl.calc_EV(trade_list)

# import module.module_calculation as cl

# data_set = md.get_data_from_csv("./nikkei225_daily/nikkei225_2020.csv")

#各種パラメータ定義（3種以内が望ましい）
# code = "NI225_2020" #銘柄コード
# consevtive_days = 3 #終値上昇or下落の連続日数
# holding_days = 5 #保有日数

#手法検証の関数

def trend_change_days_in_a_low(data_set, code, holding_days=0, consevtive_days=0):#consetive_daysは引け値連続上昇（下落）日数のボーダー日数
    
    #目的変数の定義
    trade_list = [] #各トレード結果のリストを格納
    params = [] #各パラメータを格納 ※リスト番号はdef定義時の引数の順番に対応（data_set,codeは除く）

    #変数定義
    data_label = 0 #現在のデータ番号を格納
    counter = 0 #連続上昇or下落日数のカウント（上昇なら+１、下落なら-1）

    #検証のガイドライン(初回のみ表示させるためのif分)
    if(holding_days == 0 and consevtive_days == 0):
        #手法の概要説明
        print("<この手法の概要>")
        description = "直近〇日連続で終値が前日終値を上回り、当日は前日の安値以下で引けるときに大引けでショートエントリーする手法の期待値を検証。(ロングはその逆）\
        注意点として、この手法は損切り幅（リスク量固定）を基準にしたpt方式による期待値計算と、\
        資金量を一律にして(資金量固定）、そのパーセンテージを利益として積んでいくパーセント方式による期待値計算で結果が大きく異なる可能性がある。\
        なお、この手法は宵越しを前提とするため、当日の寄付きを前提とした今のメイン手法と比べてロスカットに想定以上に大きなスリッページが入る確率が上がっている。\
        ただ、その影響は想定最大やられptを多めに見積もることによって、結果として同じように管理できると思われる。結果としてpt方式を採用することにした"
        print(description)

        #手法のパラメータ説明
        print("<パラメータの説明>")
        description = "この手法は２つのパラメータ(保有日数、連続上昇or下落日数のボーダー）を取る"
        print(description)

        #検証初回はパラメータを入力させる
        print("パラメータ１：保有日数を入力してください")
        holding_days = int(input())
        params.append(holding_days)
        print("パラメータ２：連続上昇（下落）日数のボーダー値を入力してください")
        consevtive_days = int(input())
        params.append(consevtive_days)

    #一時変数定義
    trade = {} #個々のトレードの結果を格納する変数
    total_sample = 0
    n_sample = 0

    for data in data_set:

        #データ前処理１：検証初日は前日データを参照できないのでスキップ
        if(data_label == 0):
            data_label += 1
            continue
        #データ前処理２：データの最後から起算して、保有日数を超える分のデータは損益計算できないのでスキップ
        if(data_label >=len(data_set) - holding_days):
            break

        #例外処理１：ストップ高（ストップ安）張り付きはエントリーできないので除外
        if (data[1] == data[2] and data[2] == data[3] and data[3] == data[4] and abs(data[1]-data_set[data_label-1][4])/data_set[data_label-1][1] > 0.1):
            data_label += 1
            continue

        #連続日数が規定を超えたらその日の動きを監視

        #連続上昇日数が基準を超えて、かつ前日の安値を下回って引けたらショートエントリー
        if(counter >= consevtive_days and data_set[data_label][4] < data_set[data_label-1][3]):
            print("------------------------------------------")
            print(data)
            print('連続{}日上昇！ショートエントリー'.format(counter))

            #損益計算
            entry_price = data_set[data_label][4]
            exit_price = data_set[data_label + holding_days][4]
            losscut_price = max(data_set[data_label][2], data_set[data_label - 1][2])
            losscut_range = abs(losscut_price - entry_price)

            pl = entry_price - exit_price

            #もし逆指値条件に引っかかるなら損益plを書き換え
            for i in range(holding_days):
                if (losscut_price <= data_set[data_label + (i+1)][1]):
                    print("ショートポジが寄付でロスカットされました")
                    pl = entry_price - data_set[data_label + (i+1)][1]
                    break
                elif(losscut_price <= data_set[data_label + (i+1)][2]):
                    print("ショートポジがザラバ中にロスカットされました！！")
                    pl = losscut_range*(-1)
                    break
            print(entry_price)
            print(losscut_price)
            print(exit_price)
            print(losscut_range)
            print("損益は{}円です".format(pl))
            print("調整前のplは{}".format(pl))
            pl = round(pl/losscut_range, 3)
            print("損益は{}ptです".format(pl))
            # print(holding_days)
            trade["date"] = data[0]
            trade["code"] = code
            trade["position"] = "s"
            trade["pl"] = pl


            trade_list.append(trade)
            total_sample+=pl
            n_sample += 1
            
        #連続下落日数が基準を超えて、かつ前日の高値を上回って引けたらロングエントリー
        if(counter <= consevtive_days*(-1) and data_set[data_label][4] > data_set[data_label - 1][2]):
            print("------------------------------------------")
            print('連続{}日下落！ロングエントリー'.format(counter*(-1)))
            print(data)

            #損益計算
            entry_price = data_set[data_label][4]
            exit_price = data_set[data_label + holding_days][4]
            losscut_price = min(data_set[data_label][3], data_set[data_label - 1][3])
            losscut_range = abs(losscut_price - entry_price)

            pl = exit_price - entry_price

            #もし逆指値条件に引っかかるなら損益plを書き換え
            for i in range(holding_days):
                if (losscut_price >= data_set[data_label + (i+1)][1]):
                    print("ロングポジが寄付でロスカットされました")
                    pl = data_set[data_label + (i+1)][1] - entry_price
                    break
                elif(losscut_price >= data_set[data_label + (i+1)][3]):
                    print("ロングポジがザラバ中にロスカットされました！！")
                    pl = losscut_range*(-1)
                    break
            print(entry_price)
            print(losscut_price)
            print(exit_price)
            print(losscut_range)
            print("損益は{}円です".format(pl))
            pl = round(pl/losscut_range, 3)
            print("損益は{}ptです".format(pl))
            # print(holding_days)
            total_sample+=pl
            n_sample += 1

            trade["date"] = data[0]
            trade["code"] = code
            trade["position"] = "l"
            trade["pl"] = pl


            trade_list.append(trade)



        #連続高値引けパターンの条件分岐

        #連続上昇なら連続日数をカウント
        if(counter >= 0 and data_set[data_label][4] > data_set[data_label-1][4]):
            counter += 1
        #連続下落なら連続日数をカウント
        elif(counter<=0 and data_set[data_label][4] < data_set[data_label-1][4]):
            counter -= 1
        #連続上昇中だったならカウンターをリセットして連続日数-１に書き換え
        elif(counter > 0 and data_set[data_label][4] < data_set[data_label-1][4]):
            counter = -1
        #連続下落中だったならカウンターをリセットして連続日数＋１に書き換え
        elif(counter < 0 and data_set[data_label][4] > data_set[data_label-1][4]):
            counter = 1
        #前日比±0で引けたらカウンターリセット
        else:
            counter = 0
        
        #次のループへのパラメータ調整
        data_label += 1
        trade = {}

    # print(trade_list)
    return {"result": trade_list, "params": params}

