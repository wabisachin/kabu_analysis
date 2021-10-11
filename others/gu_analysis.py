#!/usr/bin/env python3
# coding:utf-8

from module import module, module_calculation
data_list = module.get_data_from_csv("../dataset/sample_dataset/3994_5year.csv")
#変数定義
entry_count = 0
total_pt_score = 0
GUPRATE = 0.03 #ギャップアップ（ダウン）を前日比何％以上で判定するか
losscut_rate = 0.3 #GU幅に対する損切り幅の割合
previous_day = data_list[0]#前日の日足データを保持する変数・初期値はスクリーニング開始日。

#当日の寄り付き価格が前日比１０％以上の日のみを抽出
for data in data_list:
    # print(data)

    #ストップ高（ストップ安）張り付きはエントリーできないので除外
    if (data[1] == data[2] and data[2] == data[3] and data[3] == data[4]):
        previous_day = data
        continue

    previous_closing_price = previous_day[4]
    entry_price = data[1]
    losscut_range = (abs(data[1] - previous_closing_price))*losscut_rate

    #5％以上のGUでエントリー（ロスカット条件はGU幅の1/2のドローダウン、利食いは当日引け）
    if (module.flag_gu_or_gd(GUPRATE, data[1], previous_closing_price) == 1):
        print('上げ: {}'.format(data[0]))
        #損切り幅
        if (entry_price - losscut_range > data[3]):
            print("ロングポジがロスカットされました！！")
            pl = losscut_range*(-1)
        else:
            pl = data[4] - data[1]
        pl_point = pl/losscut_range
        print('この日はロングポジです')
        print('この日のlosscut_rangeは{}円です'.format(losscut_range))
        print('この日の損益は{}円です'.format(pl))
        print('この日の獲得ptは{}です'.format(pl_point))
        print("---------------------------")

        #トータルスコアの集計加算
        entry_count+=1
        total_pt_score+=pl_point

    #10％以上のGD
    elif (module.flag_gu_or_gd(GUPRATE, data[1], previous_closing_price) == -1):
        print('下げ: {}'.format(data[0]))
        if (entry_price + losscut_range < data[2]):
            print("ショートポジがロスカットされました！！")
            pl = losscut_range*(-1)
        else:
            pl = data[1] - data[4]
        pl_point = pl/losscut_range
        print('この日はショートポジです')
        print('この日のlosscut_rangeは{}円です'.format(losscut_range))
        print('この日の損益は{}円です'.format(pl))
        print('この日の獲得ptは{}です'.format(pl_point))
        print("---------------------------")

        #トータルスコアの集計加算
        entry_count+=1
        total_pt_score+=pl_point

    previous_day = data

average = total_pt_score/entry_count
print('トータルエントリー回数: {}回'.format(entry_count))
print('pt獲得合計：{}'.format(total_pt_score))
print('平均獲得スコア: {}'.format(average))