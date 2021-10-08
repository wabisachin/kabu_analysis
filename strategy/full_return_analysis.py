#!/usr/bin/env python3
# coding:utf-8

"""
大陰線全返しパターン発生後、x日間保有後に売却する手法の期待値。
条件１：エントリーは当日の始値
条件２：x日後の終値で決済
条件３：損切りの逆指値はGU幅に対する割合で決定。保有期間中、逆指値水準に触れた時点でロスカット。
条件４：指値売りはしない。利食い条件は日数経過のみ。
"""

import module

data_set = module.get_data_from_csv("./9984_5year.csv")

#変数定義
list_num = 0 #先頭から何日目のデータかどうか
losscut_temp = 0 #ロスカット判定用の高値（安値）を一時的に保持するための変数
exit_price = 0 #利食い価格を保持するための変数
entry_count = 0
total_pt_score = 0
previous_day = data_set[0]#前日の日足データを保持する変数・初期値はスクリーニング開始日。

#パラメータ定義
GAP_RATE = 0.01 #ギャップアップ（ダウン）を前日比何％以上で判定するか
FULLRETURN_RATE = 0.01 #大陰線(大陽線)判定の大きさ
LOSSCUT_RATE = 0.5 #GU幅に対する損切り幅の割合
REALBODY_RATE = 0.8 #大陽線、大陰線のローソク足の実体部分の割合
HOLDING_PERIOD = 1 #銘柄の保有日数(当日も含めて)

#当日の寄り付き価格が前日比１０％以上の日のみを抽出
for data in data_set:
    
    #ストップ高（ストップ安）張り付きはエントリーできないので除外
    if (data[1] == data[2] and data[2] == data[3] and data[3] == data[4] and abs(data[1]-previous_day[4])/previous_day[1] > 0.1):
        previous_day = data
        list_num += 1
        continue
    
    #roop内で用いる変数定義
    previous_closing_price = previous_day[4]
    entry_price = data[1]
    losscut_range = (abs(data[1] - previous_closing_price))*LOSSCUT_RATE

    gap_rate = module.gap_rate(data[1], previous_closing_price)
    full_return_rate = module.full_return_rate(previous_day[1], previous_day[4])

    #x％以上のGUでロングエントリー（ロスカット条件はGU幅のy％のドローダウン、利食いは当日引け。x:GAP_RATE,y:LOSSCUT_RATE）
    if (module.flag_gu_or_gd(GAP_RATE, data[1], previous_closing_price) == 1):

        #大陰線全返しでないならnext
        if (module.judge_full_return(previous_day[1], previous_day[2],previous_day[3],previous_day[4],FULLRETURN_RATE, REALBODY_RATE)!= -1 or gap_rate < full_return_rate*(-1)):
            previous_day = data
            list_num += 1
            continue
        print('上げ: {}'.format(data[0]))

        # #損切り
        # if (entry_price - losscut_range > data[3]):
        #     print("ロングポジがロスカットされました！！")
        #     pl = losscut_range*(-1)
        # else:
        #     pl = data[4] - data[1]
        # pl_point = pl/losscut_range
        # print('この日はロングポジです')
        # # print('この日のlosscut_rangeは{}円です'.format(losscut_range))
        # print('この日の損益は{}円です'.format(pl))
        # print('この日の獲得ptは{}です'.format(pl_point))
        # print("---------------------------")

        #逆指値に引っかからなかったケースの損益を先に計算
        exit_price = data_set[list_num + HOLDING_PERIOD - 1][4]
        pl = exit_price - data[1]

        #損切りなら損益を書き換え
        for i in range(HOLDING_PERIOD):
            if (entry_price - losscut_range > data_set[list_num + i][3]):
                print("ロングポジがロスカットされました！！")
                #寄り付きが逆指値価格より下なら、寄り付きで決済、そうでないならロスカット価格で決済
                if (entry_price - losscut_range > data_set[list_num + i][1]):
                    pl = data_set[list_num + i][1] - entry_price
                else:
                    pl = losscut_range*(-1)
                break
        
        pl_point = pl/losscut_range
        print('この日はロングポジです')
        # print('list_numは{}'.format(list_num))
        # print('今日の情報は{}'.format(data_set[list_num]))
        print('この日のlosscut_rangeは{}円です'.format(losscut_range))
        print('この日の損益は{}円です'.format(pl))
        print('この日の獲得ptは{}です'.format(pl_point))
        print("---------------------------")

        #トータルスコアの集計加算
        entry_count+=1
        total_pt_score+=pl_point

    #x％以上のGDでショートエントリー(x:GAP_RATE)
    elif (module.flag_gu_or_gd(GAP_RATE, data[1], previous_closing_price) == -1):

        #大陽線全返しでないならnext

        if (module.judge_full_return(previous_day[1], previous_day[2],previous_day[3],previous_day[4],FULLRETURN_RATE, REALBODY_RATE) != 1 or gap_rate > full_return_rate*(-1)):
            previous_day = data
            list_num += 1
            continue
        print('下げ: {}'.format(data[0]))

        # #損切り
        # if (entry_price + losscut_range < data[2]):
        #     print("ショートポジがロスカットされました！！")
        #     pl = losscut_range*(-1)
        # else:
        #     pl = data[1] - data[4]
        # pl_point = pl/losscut_range
        # print('この日はショートポジです')
        # # print('この日のlosscut_rangeは{}円です'.format(losscut_range))
        # print('この日の損益は{}円です'.format(pl))
        # print('この日の獲得ptは{}です'.format(pl_point))
        # print("---------------------------")

        #逆指値に引っかからなかったケースの損益を先に計算
        exit_price = data_set[list_num + HOLDING_PERIOD - 1][4]
        pl = data[1] - exit_price

        #損切りなら損益を書き換え
        for i in range(HOLDING_PERIOD):
            if (entry_price + losscut_range < data_set[list_num + i][2]):
                print("ショートポジがロスカットされました！！")
                #寄付が逆指値価格より上なら、寄付で決済、そうでないならロスカット価格で決済
                if (entry_price + losscut_range < data_set[list_num + i][1]):
                    pl = entry_price - data_set[list_num + i][1]
                else:
                    pl = losscut_range*(-1)
                break
        
        pl_point = pl/losscut_range
        print('この日はショートポジです')
        print('この日のlosscut_rangeは{}円です'.format(losscut_range))
        print('この日の損益は{}円です'.format(pl))
        print('この日の獲得ptは{}です'.format(pl_point))
        print("---------------------------")

        #トータルスコアの集計加算
        entry_count+=1
        total_pt_score+=pl_point


    #temp変数の初期化
    # print(data)
    # print('list_num版はこちら{}'.format(data_set[list_num]))
    list_num += 1
    losscut_temp = 0
    exit_price = 0

    previous_day = data

average = total_pt_score/entry_count
print('トータルエントリー回数: {}回'.format(entry_count))
print('pt獲得合計：{}'.format(total_pt_score))
print('平均獲得スコア: {}'.format(average))