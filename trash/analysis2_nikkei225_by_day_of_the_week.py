#!/usr/bin/env python3
# coding:utf-8

"""
寄り付きで買って、当日の引けで売った場合の曜日別期待値を検証。
あくまで検証であり、損切り条件は問わない。
"""

import datetime as dt
import module

data_set = module.get_data_from_csv("./nikkei225_20130101_20131231.csv")

#total収益の変数定義
mon_pl= 0
tue_pl = 0
wen_pl = 0
thu_pl = 0
fri_pl = 0
#日数のカウント
mon = 0
tue = 0
wen = 0
thu = 0
fri = 0



#一時的なデータ保持変数

data_num = 0

for data in data_set:

    #検証最終日にループを止める処理
    if (data[0] == '2013/12/30'):
        break

    pl = data[4]-data[1]
    pl = pl/data[4]*100

    today_str = data[0]
    # print(today_str)
    # print(type(today))
    today = today_str.split("/")
    today = [int(s) for s in today]
    # print(today)
    # print(type(today))
    today = dt.date(*today)
    day_of_week_today = today.strftime('%A')
    # print(day_of_week_today)

    if(day_of_week_today == 'Monday'):
        mon_pl += pl
        mon += 1
    elif(day_of_week_today == 'Tuesday'):
        tue_pl += pl
        tue += 1
    elif(day_of_week_today == 'Wednesday'):
        wen_pl += pl
        wen += 1
    elif(day_of_week_today == 'Thursday'):
        thu_pl += pl
        thu += 1
    elif(day_of_week_today == 'Friday'):
        fri_pl += pl
        fri += 1

    #一時変数の初期化、加算

    data_num += 1
    pl = 0

print("--------------------寄付で買って当日の引けで売る--------------------------")
print('月曜日のトータル収益は{}％,日数は{}, 平均は{}です'.format(mon_pl, mon, mon_pl/mon))
print('火曜日のトータル収益は{}％,日数は{}, 平均は{}です'.format(tue_pl, tue, tue_pl/tue))
print('水曜日のトータル収益は{}％,日数は{}, 平均は{}です'.format(wen_pl, wen, wen_pl/wen))
print('木曜日のトータル収益は{}％,日数は{}, 平均は{}です'.format(thu_pl, thu, thu_pl/thu))
print('金曜日のトータル収益は{}％,日数は{}, 平均は{}です'.format(fri_pl, fri, fri_pl/fri))
    