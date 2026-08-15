#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""一次性脚本：给 gallery.json 的 map.places 各加一个稳定 pid。"""
import json

P = "/Users/sunhaixin7/WorkBuddy/景德镇/album/gallery.json"

# 地点名关键词 -> pid（按顺序匹配，先命中先得）
PLACE_KW = [
    ("麗枫", "hotel_lifeng"),
    ("景瀚", "hotel_jinghan"),
    ("罗家机场", "base_airport"),
    ("陶瓷博物馆", "museum_ceramic"),
    ("御窑博物馆", "museum_yuyao"),
    ("民窑博物馆", "museum_minyao"),
    ("今夕美术馆", "museum_jinxi"),
    ("直升机科技馆", "museum_helicopter"),
    ("陶溪川", "shop_taoxichuan"),
    ("雕塑瓷厂", "shop_diaosu"),
    ("陶阳新村夜市", "shop_fuzhounight"),
    ("新平村瓷宫", "shop_cipalace"),
    ("古窑民俗博览区", "shop_guyao"),
    ("陶阳里历史文化旅游区", "shop_taoyangli"),
    ("七四O厂", "shop_740"),
    ("东郊学堂", "shop_dongjiao"),
    ("丙丁柴窑", "shop_bingding"),
    ("山闾村戏台", "shop_shanlv"),
    ("小樱青花扎染", "kids_xiaoying"),
    ("绿西玻璃", "kids_lvxi"),
    ("胖师傅写真", "kids_pangshifu"),
    ("江窑", "kids_jiangyao"),
    ("前程漂流", "kids_qiancheng"),
    ("抚州弄大排档", "food_fuzhou_dapaidang"),
    ("抚州弄", "food_fuzhou"),
    ("花香酒酿", "food_huaxiang"),
    ("泥上风土", "food_nishang"),
    ("一番街烤肉", "food_yifan"),
    ("陶源谷", "nature_sanbao"),
    ("瑶里古镇风景区", "nature_yaoli"),
    ("东埠", "nature_dongbu"),
    ("寒溪", "nature_hanxi"),
    ("饶州古镇", "nature_raozhou"),
    ("鄱阳湖", "nature_poyang"),
]


def match_pid(text):
    for kw, pid in PLACE_KW:
        if kw in text:
            return pid
    return None


d = json.load(open(P, encoding="utf-8"))
places = d["map"]["places"]
missed = []
for pl in places:
    if "pid" not in pl:
        pid = match_pid(pl["name"])
        if pid:
            pl["pid"] = pid
        else:
            missed.append(pl["name"])
json.dump(d, open(P, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
print("已写入 pid 的地点数:", sum(1 for p in places if "pid" in p), "/", len(places))
if missed:
    print("⚠️ 未匹配到 pid 的地点:", missed)
else:
    print("✓ 所有地点均匹配到 pid")
