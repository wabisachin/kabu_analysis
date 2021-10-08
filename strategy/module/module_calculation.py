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


#トレード結果の集計。３つの売買区分（合算、ロング、ショート）別に集計して、結果を返す。
def summary_PL(trade_list, display=1):

    #目的の変数定義
    result = {}
    #変数の構造を指定
    result["ls"] = {}
    result["l"] = {}
    result["s"] = {}


    result["ls"] = {"N": 0, "N_P":0, "N_L":0, "total_P":0, "total_L":0, "max_P":0, "max_L":0, "max_NP":0, "max_NL":0}
    result["l"] = {"N": 0, "N_P":0, "N_L":0, "total_P":0, "total_L":0, "max_P":0, "max_L":0, "max_NP":0, "max_NL":0}
    result["s"] = {"N": 0, "N_P":0, "N_L":0, "total_P":0, "total_L":0, "max_P":0, "max_L":0, "max_NP":0, "max_NL":0}
    
    #一時変数定義
    counter_LS = 0#連勝数を格納
    counter_L = 0
    counter_S = 0

    #日付順にトレードリストをsort。この処理は後に最大連勝数、最大連敗数をカウントするために行う。
    sorted_trade_list = sorted(trade_list, key=lambda x: x["date"])

    # print("<<sortされたトレードリスト>>")
    # print(sorted_trade_list)

    for trade in sorted_trade_list:
        
        #トータルスコアを集計
        result["ls"]["N"] += 1
        if(trade["pl"] >= 0):
            result["ls"]["N_P"] += 1 
            result["ls"]["total_P"] += trade["pl"]
            result["ls"]["max_P"] = max(result["ls"]["max_P"], trade["pl"])
            #連勝数カウント
            if counter_LS >= 0:
                counter_LS +=1
            else:
                counter_LS = 1
            result["ls"]["max_NP"] = max(counter_LS, result["ls"]["max_NP"])

        else:
            result["ls"]["N_L"] += 1
            result["ls"]["total_L"] += trade["pl"]
            result["ls"]["max_L"] = min(result["ls"]["max_L"], trade["pl"])
            #連敗数カウント
            if counter_LS <= 0:
                counter_LS -=1
            else:
                counter_LS = -1
            result["ls"]["max_NL"] = min(counter_LS, result["ls"]["max_NL"]*(-1))*(-1)

        #ロングのスコアを集計
        if(trade["position"] == "l"):

            result["l"]["N"] += 1
            if(trade["pl"] >= 0):
                result["l"]["N_P"] += 1 
                result["l"]["total_P"] += trade["pl"]
                result["l"]["max_P"] = max(result["l"]["max_P"], trade["pl"])
                #連勝数カウント
                if counter_L >= 0:
                    counter_L +=1
                else:
                    counter_L = 1
                result["l"]["max_NP"] = max(counter_L, result["l"]["max_NP"])

            else:
                result["l"]["N_L"] += 1
                result["l"]["total_L"] += trade["pl"]
                result["l"]["max_L"] = min(result["l"]["max_L"], trade["pl"])
                #連敗数カウント
                if counter_L <= 0:
                    counter_L -=1
                else:
                    counter_L = -1
                result["l"]["max_NL"] = min(counter_L, result["l"]["max_NL"]*(-1))*(-1)
        
        #ショートのスコアを集計
        elif(trade["position"] == "s"):
            result["s"]["N"] += 1
            if(trade["pl"] >= 0):
                result["s"]["N_P"] += 1 
                result["s"]["total_P"] += trade["pl"]
                result["s"]["max_P"] = max(result["s"]["max_P"], trade["pl"])
                #連勝数カウント
                if counter_S >= 0:
                    counter_S +=1
                else:
                    counter_S = 1
                result["s"]["max_NP"] = max(counter_S, result["s"]["max_NP"])

            else:
                result["s"]["N_L"] += 1
                result["s"]["total_L"] += trade["pl"]
                result["s"]["max_L"] = min(result["s"]["max_L"], trade["pl"])
                #連敗数カウント
                if counter_S <= 0:
                    counter_S -=1
                else:
                    counter_S = -1
                result["s"]["max_NL"] = min(counter_S, result["s"]["max_NL"]*(-1))*(-1)
                
    #デフォルトでは結果をprintするように指定、表示が邪魔な場合は引数にdisplay=0を指定することで非表示にできる
    if(display == 1):
        print("-----------------------------------------------")
        print("<LS合算>")
        print("総エントリー回数：{}".format(result["ls"]["N"]))
        print("勝ちトレードの回数：{}".format(result["ls"]["N_P"]))
        print("負けトレードの回数：{}".format(result["ls"]["N_L"]))
        print("勝ちトレードの利益合計：{}".format(result["ls"]["total_P"]))
        print("負けトレードの損失合計：{}".format(result["ls"]["total_L"]))
        print("１トレードでの最大利益pt：{}".format(result["ls"]["max_P"]))
        print("１トレードでの最大損失pt：{}".format(result["ls"]["max_L"]))
        print("最大連勝数：{}".format(result["ls"]["max_NP"]))
        print("最大連敗数：{}".format(result["ls"]["max_NL"]))
        print("-----------------------------------------------")
        print("<L>")
        print("総エントリー回数：{}".format(result["l"]["N"]))
        print("勝ちトレードの回数：{}".format(result["l"]["N_P"]))
        print("負けトレードの回数：{}".format(result["l"]["N_L"]))
        print("勝ちトレードの利益合計：{}".format(result["l"]["total_P"]))
        print("負けトレードの損失合計：{}".format(result["l"]["total_L"]))
        print("１トレードでの最大利益pt：{}".format(result["l"]["max_P"]))
        print("１トレードでの最大損失pt：{}".format(result["l"]["max_L"]))
        print("最大連勝数：{}".format(result["l"]["max_NP"]))
        print("最大連敗数：{}".format(result["l"]["max_NL"]))
        print("-----------------------------------------------")
        print("<S>")
        print("総エントリー回数：{}".format(result["s"]["N"]))
        print("勝ちトレードの回数：{}".format(result["s"]["N_P"]))
        print("負けトレードの回数：{}".format(result["s"]["N_L"]))
        print("勝ちトレードの利益合計：{}".format(result["s"]["total_P"]))
        print("負けトレードの損失合計：{}".format(result["s"]["total_L"]))
        print("１トレードでの最大利益pt：{}".format(result["s"]["max_P"]))
        print("１トレードでの最大損失pt：{}".format(result["s"]["max_L"]))
        print("最大連勝数：{}".format(result["s"]["max_NP"]))
        print("最大連敗数：{}".format(result["s"]["max_NL"]))

    return result

#期待値を算出する関数
def calc_EV(trade_list):
    
    #変数、データ構造定義
    result = {"ls":{}, "l":{}, "s":{}}
    result["ls"]={"PL":0, "PO":0, "win_rate":0, "EV":0, "P_AVE":0, "L_AVE":0}
    result["l"]={"PL":0, "PO":0, "win_rate":0, "EV":0, "P_AVE":0, "L_AVE":0}
    result["s"]={"PL":0, "PO":0, "win_rate":0, "EV":0, "P_AVE":0, "L_AVE":0}

    data = summary_PL(trade_list, display=0)
    
    #合算
    result["ls"]["PL"] = data["ls"]["total_P"] + data["ls"]["total_L"]
    result["ls"]["PO"] = data["ls"]["total_P"]/data["ls"]["total_L"]
    result["ls"]["win_rate"] = float(data["ls"]["N_P"])/data["ls"]["N"]
    result["ls"]["EV"] = (data["ls"]["total_P"] + data["ls"]["total_L"])/data["ls"]["N"]
    result["ls"]["P_AVE"] = data["ls"]["total_P"]/data["ls"]["N_P"]
    result["ls"]["L_AVE"] = data["ls"]["total_L"]/data["ls"]["N_L"]
    #ロング
    result["l"]["PL"] = data["l"]["total_P"] + data["l"]["total_L"]
    result["l"]["PO"] = data["l"]["total_P"]/data["l"]["total_L"]
    result["l"]["win_rate"] = float(data["l"]["N_P"])/data["l"]["N"]
    result["l"]["EV"] = (data["l"]["total_P"] + data["l"]["total_L"])/data["l"]["N"]
    result["l"]["P_AVE"] = data["l"]["total_P"]/data["l"]["N_P"]
    result["l"]["L_AVE"] = data["l"]["total_L"]/data["l"]["N_L"]
    #ショート
    result["s"]["PL"] = data["s"]["total_P"] + data["s"]["total_L"]
    result["s"]["PO"] = data["s"]["total_P"]/data["s"]["total_L"]
    result["s"]["win_rate"] = float(data["s"]["N_P"])/data["s"]["N"]
    result["s"]["EV"] = (data["s"]["total_P"] + data["s"]["total_L"])/data["s"]["N"]
    result["s"]["P_AVE"] = data["s"]["total_P"]/data["s"]["N_P"]
    result["s"]["L_AVE"] = data["s"]["total_L"]/data["s"]["N_L"]

    print("---------------------")
    print("<LS合算の期待値>")
    print("総利益(pt): {}".format(result["ls"]["PL"]))
    print("総エントリー回数:{}".format(data["ls"]["N"]))
    print("ペイオフ値: {}".format(result["ls"]["PO"]*(-1)))
    print("勝率: {}％".format(result["ls"]["win_rate"]*100))
    print("1トレードの期待値(EV): {}".format(result["ls"]["EV"]))
    print("1トレードの平均利益(pt): {}".format(result["ls"]["P_AVE"]))
    print("1トレードの平均損失(pt): {}".format(result["ls"]["L_AVE"]))
    print("1トレードの最大利益(pt):{}".format(data["ls"]["max_P"]))
    print("1トレードの最大損失(pt):{}".format(data["ls"]["max_L"]))
    


    print("---------------------")
    print("<Lの期待値>")
    print("総利益(pt): {}".format(result["l"]["PL"]))
    print("総エントリー回数:{}".format(data["l"]["N"]))
    print("ペイオフ値: {}".format(result["l"]["PO"]*(-1)))
    print("勝率: {}％".format(result["l"]["win_rate"]*100))
    print("1トレードの期待値(EV): {}".format(result["l"]["EV"]))
    print("1トレードの平均利益(pt): {}".format(result["l"]["P_AVE"]))
    print("1トレードの平均損失(pt): {}".format(result["l"]["L_AVE"]))
    print("1トレードの最大利益(pt):{}".format(data["l"]["max_P"]))
    print("1トレードの最大損失(pt):{}".format(data["l"]["max_L"]))

    print("---------------------")
    print("<Sの期待値>")
    print("総利益(pt): {}".format(result["s"]["PL"]))
    print("総エントリー回数:{}".format(data["s"]["N"]))
    print("ペイオフ値: {}".format(result["s"]["PO"]*(-1)))
    print("勝率: {}％".format(result["s"]["win_rate"]*100))
    print("1トレードの期待値(EV): {}".format(result["s"]["EV"]))
    print("1トレードの平均利益(pt): {}".format(result["s"]["P_AVE"]))
    print("1トレードの平均損失(pt): {}".format(result["s"]["L_AVE"]))
    print("1トレードの最大利益(pt):{}".format(data["s"]["max_P"]))
    print("1トレードの最大損失(pt):{}".format(data["s"]["max_L"]))


    return result