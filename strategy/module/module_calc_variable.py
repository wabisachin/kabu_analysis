#!/usr/bin/env python3
# coding:utf-8


#このmoduleの概要
"""
各説明変数の数値算出のためのメソッドをここにまとめる.

(優位性が潜んでいそうな説明変数)
X1: 当日寄付価格の前日に対するGU幅(直近２０日のATRに対する比率で計算)
X2: 当日の出来高規模（直近２０日の出来高平均に対する比率で計算)
X3: 前日引け~当日寄付までの間に直近２０日の高値を巻き込んだ本数
X4: 直近６０日間に、当日寄付時点で依然として上にある高値の本数
X5: 前日引け~当日寄付きまでの間に、連続して高値を巻き込んだ本数
X6: 前日がATR幅以上の下落であるかどうか(大陰線全返しの検証)
X7: 前日が陰線であるかどうか
X8: 当日寄付の日経平均の前日比
X9: 前日の場中値上がり幅(直近20日間のATRに対する比率で計算)
X10: 前日３日間の上昇率(直近20日間ATRに対する比率)
X11: 当日日経平均の場中値上がり率
X12: 前日のボラティリティ(直近20日間のATRに対する比率で計算)
X13: 前日の値上がり率(直近20日間のATRに対する比率で計算)
X14: ストップ高連続日数（寄らず）
X15:前日終値が移動平均線より上（下）にあるか
x16:前日終値の移動平均線乖離率のATR比（25日）
x17:前日終値の移動平均乖離率(25日)
x18:前日終値（価格修正済）
x19:前日時点において短期移動平均線(20日）が長期移動平均線（60日）を上回っているか（下回っているか)どうか。上昇トレンド(下降トレンド)の判定フラグ。
x20:前日時点における短期移動平均線(20日）と長期移動平均線（60日）の乖離率のATR比

# X: 決算発表が前日にあったかどうか
# X: 寄付の約定枚数(直近20日の出来高平均に対する比率)
# X: 寄付の約定枚数(発行済株式数に対する比率)
# X: 寄付の約定枚数(浮動株に対する比率)
# X: 当日時点に残った信用買いの浮動株に対する割合
# X: 当日時点に残った信用売りの浮動株に対する割合
# X: 当日NY市場の前日比
# X: 当日USD/JPYの前日比
"""
from os import close
import pandas as pd
import statistics as st

#Dataframe型のi番目のデータから、直近n日間のATRを算出する関数(i:index, n:duration)
def calc_ATR(df, index, duration=20):
    temp_df = df.loc[index-duration:index-1]
    # print(temp_df)
    atr = st.mean([data["高値"] - data["安値"] for index, data in temp_df.iterrows()]) 
    # print("ATR:{}".format(atr))
    return atr

def calc_volume_avg(df, index, duration=20):
    temp_df = df.loc[index-duration:index-1]
    # print(temp_df.describe())
    volume_ave = temp_df.describe().loc["mean", "出来高"]

    return volume_ave

#単純移動平均線の算出関数
def calc_close_avg(df, index, duration=20):
    temp_df = df.loc[index-duration:index-1]
    # print(temp_df.describe())
    close_ave = temp_df.describe().loc["mean", "終値"]

    return close_ave

#--------------------------ここから説明変数の算出関数---------------------------------------

#説明変数X1の算出
def calc_x1(df, index, duration=20):

    open_today = df.loc[index, "始値"]
    close_yesterday = df.loc[index-1, "終値"]

    x1 = abs(open_today - close_yesterday)/calc_ATR(df, index, duration)

    return x1

#説明変数X2の算出
def calc_x2(df, index, duration=20):
    volume_ave = calc_volume_avg(df, index, duration)
    volume_today = df.loc[index, "出来高"]

    return volume_today/volume_ave

#説明変数X3の算出

def calc_x3(df, index, duration=20):


    open_today = df.loc[index, "始値"]
    close_yesterday = df.loc[index-1, "終値"]
    #前日引けから当日寄付にかけて、直近２０日の高値をブレイクした本数
    breaked = 0

    #GUなら高値ブレイク本数のカウント
    if(open_today > close_yesterday):
        # print(len(df.loc[index-duration:index-1].query("高値<@open_today & @close_yesterday<高値")))
        breaked = len(df.loc[index-duration:index-1].query("高値<@open_today & @close_yesterday<高値"))
        
    #GDなら安値ブレイク本数のカウント
    elif(open_today < close_yesterday):
        # print(len(df.loc[index-duration:index-1].query("安値 < @close_yesterday & @open_today < 安値")))
        breaked = len(df.loc[index-duration:index-1].query("安値 < @close_yesterday & @open_today < 安値"))
    
    return breaked

def calc_x4(df, index, duration=60):

    open_today = df.loc[index, "始値"]
    close_yesterday = df.loc[index-1, "終値"]
    df_temp = df.loc[index-duration:index-1]

    if(open_today > close_yesterday):
        df_temp = df_temp[df_temp["高値"] > open_today]
    elif(open_today < close_yesterday):
        df_temp = df.loc[index-duration:index-1]
        df_temp = df_temp[df_temp["安値"] < open_today]

    return len(df_temp)

def calc_x5(df, index):
    counter = 0
    open_today = df.loc[index, "始値"]
    close_yesterday = df.loc[index-1, "終値"]

    df_temp = df[:index-1]
    #データの古い順にsort
    df_temp = df_temp.iloc[::-1]
    #indexの番号が変わっていないので振り直す
    df_temp.reset_index(drop=True,inplace=True)

    #GUなら本数カウント
    if(open_today > close_yesterday):
        # print(len(df.loc[index-duration:index-1].query("高値<@open_today & @close_yesterday<高値")))
        # breaked = len(df.loc[index-duration:index-1].query("高値<@open_today & @close_yesterday<高値"))
        for index, data in df_temp.iterrows():
            if(data["高値"] > open_today or close_yesterday > data["高値"]):
                break
            counter += 1
    #GDなら本数カウント
    elif(open_today < close_yesterday):
        for index, data in df_temp.iterrows():
            if(data["安値"] < open_today or close_yesterday < data["安値"]):
                break
            counter += 1
        # print(len(df.loc[index-duration:index-1].query("安値 < @close_yesterday & @open_today < 安値")))
        # breaked = len(df.loc[index-duration:index-1].query("安値 < @close_yesterday & @open_today < 安値"))
    return counter

def calc_x6(df, index, duration=20):
    #戻り値
    flag = 0

    open_today = df.loc[index, "始値"]
    close_yesterday = df.loc[index-1, "終値"]
    open_yesterday = df.loc[index-1, "始値"]
    atr = calc_ATR(df, index-1, duration)
    # df_temp = df[:index-1]
    # #データの古い順にsort
    # df_temp = df_temp.iloc[::-1]
    # #indexの番号が変わっていないので振り直す
    # df_temp.reset_index(drop=True,inplace=True)

    #GUなら大陰線返し判定
    if(open_today > close_yesterday):
        if((close_yesterday - open_yesterday) < atr*(-1)):
            flag = 1

    #GDなら大陽線返し判定
    elif(open_today < close_yesterday):
        if((close_yesterday - open_yesterday) > atr):
            flag = 1
        
    return flag

def calc_x7(df, index):

    #戻り値
    flag = 0

    open_today = df.loc[index, "始値"]
    close_yesterday = df.loc[index-1, "終値"]
    open_yesterday = df.loc[index-1, "始値"]
    
    #GUなら大陰線返し判定
    if((open_today > close_yesterday) and (close_yesterday < open_yesterday)):
        flag = 1

    #GDなら大陽線返し判定
    elif((open_today < close_yesterday) and (close_yesterday > open_yesterday)):
        flag = 1
        
    return flag

def calc_x8(df, df_NI225, index):
    # df_NI225 = pd.read_csv("./dataset/NI225/nikkei225_20010903_20210930.csv")
    today = df.loc[index, "日付"]
    yesterday = df.loc[index-1, "日付"]
    # print(df_NI225["日付"].dtype)
    # print(type(today))
    # print("------今日の日付:{}-----".format(today))
    # print("------昨日の日付:{}-----".format(yesterday))

    today_NI225 = df_NI225.query("日付 == '{}'".format(today))
    # today_NI225 = df_NI225.query("日付 == '2016/12/16'".format(today))
    # print("-----today_NI225:{}".format(today_NI225))
    # yesterday_NI225 = df_NI225.loc[df["日付"] == yesterday]
    yesterday_NI225 = df_NI225.query("日付 == '{}'".format(yesterday))
    # print("-----today_NI225:{}".format(today_NI225[""]))
    # print(type(today_NI225["始値"]))
    # print(today_NI225.index)
    # print("----始値:{}".format(today_NI225["始値"].replace(",", "")))
    today_NI225_open = float(today_NI225["始値"].iloc[-1].replace(",", ""))
    yesterday_NI225_close = float(yesterday_NI225["終値"].iloc[-1].replace(",", ""))
    # print("----終値:{}".format(yesterday_NI225_close))
    ratio = (today_NI225_open - yesterday_NI225_close)/yesterday_NI225_close
    # print("----ratio:{}".format(ratio))

    return ratio

def calc_x9(df, index, duration=20):

    atr = calc_ATR(df, index, duration)
    open_yesterday = df.loc[index-1, "始値"]
    close_yesterday = df.loc[index-1, "終値"]

    x1 = (close_yesterday - open_yesterday)/atr
    # print("--------")
    # print(df.loc[index,"日付"])
    # print("<x9のパラメータ値>")
    # print(open_yesterday,close_yesterday, atr)

    return x1

def calc_x10(df, index, days=3, duration=20):
    atr = calc_ATR(df, index, duration)

    open_price = df.loc[index-days, "始値"]
    end_price = df.loc[index-1, "終値"]
    # print("<x10のパラメータ値>")
    # print(open_price, end_price, atr)
    x1 = (end_price - open_price)/atr

    return x1

def calc_x11(df, df_NI225, index):
    today = df.loc[index, "日付"]
    # yesterday = df.loc[index-1, "日付"]
    # print(df_NI225["日付"].dtype)
    # print(type(today))
    # print("------今日の日付:{}-----".format(today))
    # print("------昨日の日付:{}-----".format(yesterday))

    today_NI225 = df_NI225.query("日付 == '{}'".format(today))
    # today_NI225 = df_NI225.query("日付 == '2016/12/16'".format(today))
    # print("-----today_NI225:{}".format(today_NI225))
    # yesterday_NI225 = df_NI225.loc[df["日付"] == yesterday]
    # yesterday_NI225 = df_NI225.query("日付 == '{}'".format(yesterday))
    # print("-----today_NI225:{}".format(today_NI225[""]))
    # print(type(today_NI225["始値"]))
    # print(today_NI225.index)
    # print("----始値:{}".format(today_NI225["始値"].replace(",", "")))
    today_NI225_open = float(today_NI225["始値"].iloc[-1].replace(",", ""))
    today_NI225_close = float(today_NI225["終値"].iloc[-1].replace(",", ""))
    # print("----終値:{}".format(yesterday_NI225_close))
    ratio = (today_NI225_close - today_NI225_open)/today_NI225_open
    # print("----ratio:{}".format(ratio))

    return ratio

def calc_x12(df, index, duration=20):

    atr = calc_ATR(df, index, duration)
    high_yesterday = df.loc[index-1, "高値"]
    low_yesterday = df.loc[index-1, "安値"]

    x1 = (high_yesterday - low_yesterday)/atr
    # print("--------")
    # print(df.loc[index,"日付"])
    # print("<x9のパラメータ値>")
    # print(open_yesterday,close_yesterday, atr)

    return x1

def calc_x13(df, index, duration=20):

    atr = calc_ATR(df, index, duration)
    close_yesterday = df.loc[index-1, "終値"]
    close_2days_ago = df.loc[index-2, "終値"]

    x1 = (close_yesterday - close_2days_ago)/atr
    # print("--------")
    # print(df.loc[index,"日付"])
    # print("<x9のパラメータ値>")
    # print(open_yesterday,close_yesterday, atr)

    return x1

def calc_x14(df, index):
    
    counter = 0
    #例外処理１：ストップ高（ストップ安）張り付きはエントリーできないので除外
    while(df.loc[index-counter-1, "始値"] == df.loc[index-counter-1, "高値"] and df.loc[index-counter-1, "高値"] == df.loc[index-counter-1, "安値"] and df.loc[index-counter-1, "安値"] == df.loc[index-counter-1, "終値"] and abs(df.loc[index-counter-2, "終値"] - df.loc[index-counter-1, "始値"])/df.loc[index-counter-2, "終値"] > 0.1):
            counter = counter + 1

    return counter

def calc_x15(df, index, duration=25):

    #戻り値
    flag = 0

    open_today = df.loc[index, "始値"]
    close_yesterday = df.loc[index-1, "終値"]
    close_ave = calc_close_avg(df, index, duration)

    #GUかつ前日終値が移動平均より上ならフラグ点灯
    if((open_today > close_yesterday) and (close_yesterday > close_ave)):
        flag = 1

    #GDかつ前日終値が移動平均より下ならフラグ点灯
    elif((open_today < close_yesterday) and (close_yesterday < close_ave)):
        flag = 1
        
    return flag

def calc_x16(df, index, duration=25):

    #戻り値(移動平均線乖離率のATR比)
    rate_of_deviation = 0

    close_yesterday = df.loc[index-1, "終値"]
    close_ave = calc_close_avg(df, index, duration)
    atr = calc_ATR(df, index, duration)

    rate_of_deviation = (close_yesterday - close_ave)/atr

    # print("-----------")
    # print(df.loc[index,"日付"])
    # print("atr:{}".format(atr))
    # print("移動平均:{}".format(close_ave))

    return rate_of_deviation

def calc_x17(df, index, duration=25):

    #戻り値(移動平均線乖離率)
    rate_of_deviation = 0

    close_yesterday = df.loc[index-1, "終値"]
    close_ave = calc_close_avg(df, index, duration)

    rate_of_deviation = (close_yesterday - close_ave)/close_ave

    # print("-----------")
    # print(df.loc[index,"日付"])
    # print("atr:{}".format(atr))
    # print("移動平均:{}".format(close_ave))

    return rate_of_deviation

def calc_x18(df, index):

    close_yesterday = df.loc[index-1, "終値"]
    return close_yesterday

def calc_x19(df, index, duration1=20, duration2=60):

    #戻り値(上昇トレンド、下降トレンドの順張りflag)
    flag = 0

    open_today = df.loc[index, "始値"]
    close_yesterday = df.loc[index-1, "終値"]

    #短期移動平均線
    moving_ave1 = calc_close_avg(df, index, duration1)
    #長期移動平均線
    moving_ave2 = calc_close_avg(df, index, duration2)


    #GUかつ短期移動平均線>長期位平均線なら上昇トレンド→順張りフラグ点灯
    if((open_today > close_yesterday) and (moving_ave1 > moving_ave2)):
        flag = 1

    #GDかつ短期移動平均線<長期位平均線なら下降トレンド→順張りフラグ点灯
    elif((open_today < close_yesterday) and (moving_ave1 < moving_ave2)):
        flag = 1
        
    return flag

def calc_x20(df, index, duration1=20, duration2=60):

    #戻り値(短期移動平均線と長期移動平均線のATR比乖離率のflag)
    rate_of_deviation = 0


    atr = calc_ATR(df, index, duration1)
    #短期移動平均線
    moving_ave1 = calc_close_avg(df, index, duration1)
    #長期移動平均線
    moving_ave2 = calc_close_avg(df, index, duration2)

    rate_of_deviation = (moving_ave1 - moving_ave2)/atr

    # print("-----------")
    # print(df.loc[index,"日付"])
    # print("atr:{}".format(atr))
    # print("移動平均:{}".format(close_ave))

    return rate_of_deviation

