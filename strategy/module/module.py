#!/usr/bin/env python3
# coding:utf-8

import csv
from os import close
import pandas as pd
import statistics as st


#時系列データ(.csv)から[日付、始値、高値、安値、終値]を抽出し、Dataflame型に変換する関数(x8算出用)
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

#investing.comから入手したnikkei225csvデータの整形
def data_shaping_from_investing(fileName):
    with open(fileName, "r+") as f:
        writer = csv.writer(f)
        header = next(writer)
        for row in writer:
            print(row[0])

#Dataframe型のi番目のデータから、直近n日間のATRを算出する関数(i:index, n:duration)
def calc_ATR(df, index, duration=20):
    temp_df = df.loc[index-duration:index-1]
    # print(temp_df)
    atr = st.mean([data["高値"] - data["安値"] for index, data in temp_df.iterrows()]) 
    # print("ATR:{}".format(atr))
    return atr


#目的変数PLの算出

#Dataframe型のi番目の日の寄付にエントリーしてn日間保有した場合のトレード損益を算出する関数。ロスカット条件はATR*α(α:修正係数)以上の値幅逆行した場合。holding_dayは当日を含む。
def calc_pl_with_open(df, index, holding_days, α=1, atr_duration=20):
    entry_price = df.loc[index, "始値"]
    exit_price = df.loc[index+holding_days-1,"終値"]
    close_yesterday = df.loc[index-1, "終値"]
    losscut_range = calc_ATR(df, index, atr_duration) * α
    
    # print("ポジション:{}".format(position))
    # print("エントリー価格：{}".format(entry_price))
    # print("ロスカット幅(ATR)：{}".format(losscut_range))
    #ロングの場合
    if(entry_price > close_yesterday):
        #逆指値にタッチしたら値の書き換え
        for i, data in df.loc[index:index+holding_days-1].iterrows():
            # print(data)
            if(data["始値"] <= entry_price - losscut_range):
                # print("寄付きにロスカットされました！！！")
                exit_price = data["始値"]
                break
            elif(data["安値"] <= entry_price - losscut_range):
                # print("場中にロスカットされました")
                exit_price = entry_price - losscut_range
                break
        # print("決済価格：{}".format(exit_price))
        pl = (exit_price - entry_price)
    #ショートの場合
    elif(entry_price < close_yesterday):
        #逆指値にタッチしたら値の書き換え
        for i, data in df.loc[index:index+holding_days-1].iterrows():
            # print(data)
            if(data["始値"] >= entry_price + losscut_range):
                # print("寄付きにロスカットされました！！！")
                # print(data["日付"])
                exit_price = data["始値"]
                break
            elif(data["高値"] >= entry_price + losscut_range):
                # print("場中にロスカットされました")
                # print(data["日付"])
                exit_price = entry_price + losscut_range
                break
        # print("決済価格：{}".format(exit_price))
        pl = entry_price - exit_price
    # print("pl(修正前):{}円".format(pl))
    pl = pl/losscut_range
    # print("pl(修正後):{}pt".format(pl))

    #それ以外の場合はエラーを返す
    # else:
    #     print("無効な値がはいっています。l or s")
    #     raise ValueError

    return pl

#Dataframe型のi番目の日の寄付にエントリーしてn日間保有した場合のトレード損益を算出する関数。ロスカット条件は前日の高値(安値)を下回った時
def calc_pl_with_open_losscut_by_yesterday_highlow(df, index, holding_days, atr_duration=20):
    entry_price = df.loc[index, "始値"]
    exit_price = df.loc[index+holding_days-1,"終値"]
    close_yesterday = df.loc[index-1, "終値"]
    high_yesterday = df.loc[index-1, "高値"]
    low_yesterday = df.loc[index-1, "安値"]
    atr = calc_ATR(df, index, atr_duration)
    
    # print("ポジション:{}".format(position))
    # print("エントリー価格：{}".format(entry_price))
    # print("ロスカット幅(ATR)：{}".format(losscut_range))
    #ロングの場合
    if(entry_price > close_yesterday):
        #損切り幅の算出
        losscut_range = entry_price - low_yesterday
        #逆指値にタッチしたら値の書き換え
        for i, data in df.loc[index:index+holding_days-1].iterrows():
            # print(data)
            if(data["始値"] <= low_yesterday):
                # print("寄付きにロスカットされました！！！")
                exit_price = data["始値"]
                break
            elif(data["安値"] <= low_yesterday):
                # print("場中にロスカットされました")
                exit_price = low_yesterday
                break
        # print("決済価格：{}".format(exit_price))
        pl = (exit_price - entry_price)
    #ショートの場合
    elif(entry_price < close_yesterday):
        #損切り幅の算出
        losscut_range = high_yesterday - entry_price
        #逆指値にタッチしたら値の書き換え
        for i, data in df.loc[index:index+holding_days-1].iterrows():
            # print(data)
            if(data["始値"] >= high_yesterday):
                # print("寄付きにロスカットされました！！！")
                # print(data["日付"])
                exit_price = data["始値"]
                break
            elif(data["高値"] >= high_yesterday):
                # print("場中にロスカットされました")
                # print(data["日付"])
                exit_price = high_yesterday
                break
        # print("決済価格：{}".format(exit_price))
        pl = entry_price - exit_price
    # print("----------------------------")
    # print(df.loc[index, "日付"])
    # print("pl(修正前):{}円".format(pl))
    # print("losscut_range: {}".format(losscut_range))
    pl = pl/losscut_range
    # print("pl(修正後):{}pt".format(pl))

    pl_atr = pl*(losscut_range/atr)

    #それ以外の場合はエラーを返す
    # else:
    #     print("無効な値がはいっています。l or s")
    #     raise ValueError

    return {"pl_lc": pl, "pl_atr": pl_atr}


#Dataframe型のi番目の日の寄付にエントリーしてn日間保有した場合のトレード損益を算出する関数。ロスカット条件は前日の終値を下回った(上回った)時
def calc_pl_with_open_losscut_by_yesterday_close(df, index, holding_days, atr_duration=20):
    entry_price = df.loc[index, "始値"]
    exit_price = df.loc[index+holding_days-1,"終値"]
    close_yesterday = df.loc[index-1, "終値"]
    # high_yesterday = df.loc[index-1, "高値"]
    # low_yesterday = df.loc[index-1, "安値"]
    atr = calc_ATR(df, index, atr_duration)
    
    # print("ポジション:{}".format(position))
    # print("エントリー価格：{}".format(entry_price))
    # print("ロスカット幅(ATR)：{}".format(losscut_range))
    #ロングの場合
    if(entry_price > close_yesterday):
        #損切り幅の算出
        losscut_range = entry_price - close_yesterday
        #逆指値にタッチしたら値の書き換え
        for i, data in df.loc[index:index+holding_days-1].iterrows():
            # print(data)
            if(data["始値"] <= close_yesterday):
                # print("寄付きにロスカットされました！！！")
                exit_price = data["始値"]
                break
            elif(data["安値"] <= close_yesterday):
                # print("場中にロスカットされました")
                exit_price = close_yesterday
                break
        # print("決済価格：{}".format(exit_price))
        pl = (exit_price - entry_price)
    #ショートの場合
    elif(entry_price < close_yesterday):
        #損切り幅の算出
        losscut_range = close_yesterday - entry_price
        #逆指値にタッチしたら値の書き換え
        for i, data in df.loc[index:index+holding_days-1].iterrows():
            # print(data)
            if(data["始値"] >= close_yesterday):
                # print("寄付きにロスカットされました！！！")
                # print(data["日付"])
                exit_price = data["始値"]
                break
            elif(data["高値"] >= close_yesterday):
                # print("場中にロスカットされました")
                # print(data["日付"])
                exit_price = close_yesterday
                break
        # print("決済価格：{}".format(exit_price))
        pl = entry_price - exit_price
    # print("----------------------------")
    # print(df.loc[index, "日付"])
    # print("atr:{}".format(atr))
    # print("pl(修正前):{}円".format(pl))
    # print("losscut_range: {}".format(losscut_range))
    pl = pl/losscut_range
    # print("pl(修y正後):{}pt".format(pl))

    pl_atr = pl*(losscut_range/atr)

    #それ以外の場合はエラーを返す
    # else:
    #     print("無効な値がはいっています。l or s")
    #     raise ValueError

    return {"pl_lc": pl, "pl_atr": pl_atr}

#Dataframe型のi番目の日に指値エントリー(limit_price)してn日間保有した場合のトレード損益を算出する関数。ロスカット条件はATR*α(α:修正係数)以上の値幅逆行した場合。holding_dayは当日を含む。
def calc_pl_with_after_open(df, index, holding_days, limit_price, α=1, atr_duration=20):
    open_price = df.loc[index, "始値"]
    exit_price = df.loc[index+holding_days-1,"終値"]
    close_yesterday = df.loc[index-1, "終値"]
    losscut_range = calc_ATR(df, index, atr_duration) * α
    
    # print("ポジション:{}".format(position))
    # print("エントリー価格：{}".format(entry_price))
    # print("ロスカット幅(ATR)：{}".format(losscut_range))
    #ロングの場合
    if(open_price > close_yesterday):
        #逆指値にタッチしたら値の書き換え
        for i, data in df.loc[index:index+holding_days-1].iterrows():
            # print(data)
            if(data["始値"] <= limit_price - losscut_range):
                # print("寄付きにロスカットされました！！！")
                exit_price = data["始値"]
                break
            elif(data["安値"] <= limit_price - losscut_range):
                # print("場中にロスカットされました")
                exit_price = limit_price - losscut_range
                break
        # print("決済価格：{}".format(exit_price))
        pl = (exit_price - limit_price)
    #ショートの場合
    elif(open_price < close_yesterday):
        #逆指値にタッチしたら値の書き換え
        for i, data in df.loc[index:index+holding_days-1].iterrows():
            # print(data)
            if(data["始値"] >= limit_price + losscut_range):
                # print("寄付きにロスカットされました！！！")
                # print(data["日付"])
                exit_price = data["始値"]
                break
            elif(data["高値"] >= limit_price + losscut_range):
                # print("場中にロスカットされました")
                # print(data["日付"])
                exit_price = limit_price + losscut_range
                break
        # print("決済価格：{}".format(exit_price))
        pl = limit_price - exit_price
    print("-------------------")
    print("atr:{}".format(calc_ATR(df, index, atr_duration)))
    print("日付:{}".format(df.loc[index, "日付"]))
    print("limit_price:{}".format(limit_price))
    print("exit_price:{}".format(exit_price))
    print("pl(修正前):{}円".format(pl))
    pl = pl/losscut_range
    print("pl(修正後):{}pt".format(pl))

    #それ以外の場合はエラーを返す
    # else:
    #     print("無効な値がはいっています。l or s")
    #     raise ValueError

    return pl

# def calc_PL_with_open(df, index, position, holding_days, atr_duration, α):
#     entry_price = df.loc[index, "始値"]
#     exit_price = df.loc[index+holding_days-1,"終値"]
#     losscut_range = calc_ATR(df, index, atr_duration) * α
#     # print("ポジション:{}".format(position))
#     # print("エントリー価格：{}".format(entry_price))
#     # print("ロスカット幅(ATR)：{}".format(losscut_range))
#     #ロングの場合
#     if(position == "l"):
#         #逆指値にタッチしたら値の書き換え
#         for i, data in df.loc[index:index+holding_days-1].iterrows():
#             # print(data)
#             if(data["始値"] <= entry_price - losscut_range):
#                 # print("寄付きにロスカットされました！！！")
#                 exit_price = data["始値"]
#                 break
#             elif(data["安値"] <= entry_price - losscut_range):
#                 # print("場中にロスカットされました")
#                 exit_price = entry_price - losscut_range
#                 break
#         # print("決済価格：{}".format(exit_price))
#         pl = (exit_price - entry_price)
#     #ショートの場合
#     elif(position == "s"):
#         #逆指値にタッチしたら値の書き換え
#         for i, data in df.loc[index:index+holding_days-1].iterrows():
#             # print(data)
#             if(data["始値"] >= entry_price + losscut_range):
#                 # print("寄付きにロスカットされました！！！")
#                 # print(data["日付"])
#                 exit_price = data["始値"]
#                 break
#             elif(data["高値"] >= entry_price + losscut_range):
#                 # print("場中にロスカットされました")
#                 # print(data["日付"])
#                 exit_price = entry_price + losscut_range
#                 break
#         # print("決済価格：{}".format(exit_price))
#         pl = entry_price - exit_price
#     # print("pl(修正前):{}円".format(pl))
#     pl = pl/losscut_range
#     # print("pl(修正後):{}pt".format(pl))

#     #それ以外の場合はエラーを返す
#     # else:
#     #     print("無効な値がはいっています。l or s")
#     #     raise ValueError

#     return pl



#----------------過去の関数たち---------------


#時系列データ(.csv)から[日付、始値、高値、安値、終値]を抽出し、Dataflame型に変換する関数
# def get_data(fileName):

#     df= pd.read_csv(fileName)
#     df.drop(df.columns[7:], axis=1, inplace=True)
#     #2010/10/01は東証のシステムエラーのため、データから除去
#     df.drop(df.loc[df["日付"]=="2020/10/01"].index, inplace=True)
#     #データの古い順にsort
#     df = df.iloc[::-1]
#     #indexの番号が変わっていないので振り直す
#     df.reset_index(drop=True,inplace=True)
#     #csvデータの価格表示が",”を含んだ文字列型となっているので、取り除いてfloat型にキャスト
#     for name in df:
#         df[name] = df.loc[:, name].str.replace(",", "")
#     df = df.astype({"始値": "float", "高値":"float", "安値":"float", "終値":"float","前日比":"float", "出来高":"int"})
#     return df

# #時系列データcsvファイルから[日付、始値、高値、安値、終値]だけを抽出し、データの古い順にソートしてリスト化する関数
# def get_data_from_csv(fileName):

#     data = []

#     with open(fileName,"r",) as f:
#         reader = csv.reader(f)
#         header = next(reader) #ヘッダーはデータではないのでスキップ
#         for row in reader:
#             del(row[5:])#日付、始値、高値、安値、終値以外のデータを除外
#             if (row[0] == '2020/10/01'):#2020/10/1は東証のシステムエラーなので除外
#                 continue
#             for i in range(4):#文字列データを数値データに変換
#                 row[i+1]  =row[i+1].replace(",", "")
#                 row[i+1] = float(row[i+1])
#             data.append(row)

#     data.reverse()

#     return data

# #GU,GDのフラグ判定
# def flag_gu_or_gd(rate, open_price_today, close_price_yesterday): #rateは10％は0.1
    
#     if ((open_price_today- close_price_yesterday)/close_price_yesterday > rate):#GUなら１をreturn
#         return 1
#     elif ((open_price_today- close_price_yesterday)/close_price_yesterday < rate*(-1)):#GDなら-１をreturn
#         return -1
#     else:
#         return 0
# #ストップ高ストップ安判定
# def whether_price_stop(prices):
#     if (prices[1] == prices[2] and prices[2] == prices[3] and prices[3] == prices[4]):
#         return True
#     else:
#         return False

# #前日比何％のギャップアップorギャップダウンか返す関数
# def gap_rate(open_price_today, close_price_yesterday):
#     return ((open_price_today - close_price_yesterday)/close_price_yesterday)

# #大陰線（大陽線）の終値に対する％を返す関数(大陰線なら負の数、大陽線なら正の数)
# def full_return_rate(open_price_yesterday, close_price_yesterday):
#     return ((close_price_yesterday - open_price_yesterday)/close_price_yesterday)

# #大陰線（大陽線）かどうかの判定。条件: 実線部の大きさの絶対値が当日終値のy％以上、かつ実線部分が全体のx割以上を占めている(x:rate,y:solid_rate)
# def  judge_full_return(open_price_yesterday, high_price_yesterday, low_price_yesterday, close_price_yesterday, rate, solid_rate):
#     #大陽線判定 
#     if ((close_price_yesterday - open_price_yesterday)/close_price_yesterday > rate):
#         if (abs(close_price_yesterday - open_price_yesterday)/(high_price_yesterday - low_price_yesterday) > solid_rate):
#             return 1
#         else:
#             return 0
#     #大陰線判定
#     elif ((close_price_yesterday - open_price_yesterday)/close_price_yesterday < rate*(-1)):
#         if (abs(close_price_yesterday - open_price_yesterday)/(high_price_yesterday - low_price_yesterday) > solid_rate):
#             return -1
#         return 0
#     else:
#         return 0
