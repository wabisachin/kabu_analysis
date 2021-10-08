#!/usr/bin/env python3
# coding:utf-8

import csv

#時系列データcsvファイルから[日付、始値、高値、安値、終値]だけを抽出し、データの古い順にソートしてリスト化する関数
def get_data_from_csv(fileName):

    data = []

    with open(fileName,"r",) as f:
        reader = csv.reader(f)
        header = next(reader) #ヘッダーはデータではないのでスキップ
        for row in reader:
            del(row[5:])#日付、始値、高値、安値、終値以外のデータを除外
            if (row[0] == '2020/10/01'):#2020/10/1は東証のシステムエラーなので除外
                continue
            for i in range(4):#文字列データを数値データに変換
                row[i+1]  =row[i+1].replace(",", "")
                row[i+1] = float(row[i+1])
            data.append(row)

    data.reverse()

    return data


#investing.comから入手したnikkei225csvデータの整形
def data_shaping_from_investing(fileName):
    with open(fileName, "r+") as f:
        writer = csv.writer(f)
        header = next(writer)
        for row in writer:
            print(row[0])



#GU,GDのフラグ判定
def flag_gu_or_gd(rate, open_price_today, close_price_yesterday): #rateは10％は0.1
    
    if ((open_price_today- close_price_yesterday)/close_price_yesterday > rate):#GUなら１をreturn
        return 1
    elif ((open_price_today- close_price_yesterday)/close_price_yesterday < rate*(-1)):#GDなら-１をreturn
        return -1
    else:
        return 0
#ストップ高ストップ安判定
def whether_price_stop(prices):
    if (prices[1] == prices[2] and prices[2] == prices[3] and prices[3] == prices[4]):
        return True
    else:
        return False

#前日比何％のギャップアップorギャップダウンか返す関数
def gap_rate(open_price_today, close_price_yesterday):
    return ((open_price_today - close_price_yesterday)/close_price_yesterday)

#大陰線（大陽線）の終値に対する％を返す関数(大陰線なら負の数、大陽線なら正の数)
def full_return_rate(open_price_yesterday, close_price_yesterday):
    return ((close_price_yesterday - open_price_yesterday)/close_price_yesterday)

#大陰線（大陽線）かどうかの判定。条件: 実線部の大きさの絶対値が当日終値のy％以上、かつ実線部分が全体のx割以上を占めている(x:rate,y:solid_rate)
def  judge_full_return(open_price_yesterday, high_price_yesterday, low_price_yesterday, close_price_yesterday, rate, solid_rate):
    #大陽線判定 
    if ((close_price_yesterday - open_price_yesterday)/close_price_yesterday > rate):
        if (abs(close_price_yesterday - open_price_yesterday)/(high_price_yesterday - low_price_yesterday) > solid_rate):
            return 1
        else:
            return 0
    #大陰線判定
    elif ((close_price_yesterday - open_price_yesterday)/close_price_yesterday < rate*(-1)):
        if (abs(close_price_yesterday - open_price_yesterday)/(high_price_yesterday - low_price_yesterday) > solid_rate):
            return -1
        return 0
    else:
        return 0