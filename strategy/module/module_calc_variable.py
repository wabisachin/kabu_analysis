#!/usr/bin/env python3
# coding:utf-8


#このmoduleの概要
"""
各説明変数の数値算出のためのメソッドをここにまとめる。
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
    print(temp_df.describe())
    volume_ave = temp_df.describe().loc["mean", "出来高"]

    return volume_ave

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
    