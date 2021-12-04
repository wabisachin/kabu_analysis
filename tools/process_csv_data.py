#!/usr/bin/env python2
# coding:utf-8


import pandas as pd

df = pd.read_csv("nikkei225_20010903_20211110.csv")
print(df)
print(df.dtypes)
# df["日付"] = df["日付"].astype(str)+","
df["出来高"] = df["出来高"].astype(str)+","
df["前日比"] = df["前日比"].astype(str)+","

df.to_csv("./nikkei225_20010903_20211110_modify.csv", index=False)
