#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
build_album.py —— 根据 gallery.json 生成 album/index.html 相册页面。

用法:
    python3 build_album.py

每天拍完照后:
    1) 把照片放进 images/ 目录(建议按 D1/D2... 命名,如 images/D1_airport.jpg)
    2) 在 gallery.json 对应 event 的 "photos" 里加 {"src":"images/D1_airport.jpg","caption":"落地啦"}
    3) 重新运行本脚本: python3 build_album.py
    4) 把 album/ 整个目录推到 GitHub(Pages 自动更新)
"""
import json
import datetime
import os

ROOT = os.path.dirname(os.path.abspath(__file__))


def load():
    with open(os.path.join(ROOT, "gallery.json"), encoding="utf-8") as f:
        return json.load(f)


CAT_LABEL = {
    "museum": "博物馆", "shop": "门店/市集", "kids": "亲子手工",
    "food": "美食", "nature": "自然/古镇", "base": "交通/基地", "hotel": "酒店",
}

TEMPLATE = r"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>__TITLE__</title>
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
<style>
  * { margin: 0; padding: 0; box-sizing: border-box; }
  :root {
    --ink: #4a3526; --paper: #fdf6ee; --card: #fffdfa;
    --celadon: #6fd6c4; --celadon-d: #2f9b85;
    --clay: #ff8c69; --clay-d: #e06a44;
    --gold: #ffc861; --blue: #6fb1e0; --muted: #9b8775; --line: #f0e6da;
  }
  body { font-family: -apple-system, "PingFang SC", "Microsoft YaHei", sans-serif;
    background: var(--paper); color: var(--ink); line-height: 1.7; -webkit-font-smoothing: antialiased; }
  .hero { background: linear-gradient(135deg, #ffb088 0%, #ffd6a5 100%); color: #7a4a2a;
    padding: 40px 22px 30px; text-align: center; position: relative; overflow: hidden; }
  .hero::after { content: ""; position: absolute; left: 0; right: 0; bottom: 0; height: 5px;
    background: repeating-linear-gradient(90deg, var(--gold) 0 18px, transparent 18px 36px); opacity: .5; }
  .hero h1 { font-size: 26px; letter-spacing: 1px; margin-bottom: 8px; }
  .hero .sub { font-size: 14px; opacity: .92; }
  .hero .meta { display: flex; flex-wrap: wrap; gap: 10px; justify-content: center; margin-top: 16px; }
  .hero .chip { background: rgba(255,255,255,.18); border: 1px solid rgba(255,255,255,.35);
    padding: 6px 14px; border-radius: 20px; font-size: 13px; }
  .progress { max-width: 920px; margin: 0 auto; padding: 16px 16px 0; }
  .progress .bar { height: 10px; background: #efe4d6; border-radius: 6px; overflow: hidden; }
  .progress .bar > i { display: block; height: 100%; background: linear-gradient(90deg, var(--celadon), var(--celadon-d)); }
  .progress .txt { font-size: 13px; color: var(--muted); margin-top: 8px; text-align: center; }
  .wrap { max-width: 920px; margin: 0 auto; padding: 18px 16px 60px; }
  section { margin-bottom: 30px; }
  h2 { font-size: 19px; color: var(--celadon-d); border-left: 5px solid var(--clay);
    padding-left: 12px; margin-bottom: 14px; display: flex; align-items: center; gap: 8px; }
  h2 .ic { font-size: 21px; }
  /* map */
  #map { height: 460px; border-radius: 14px; border: 1px solid var(--line); z-index: 1; }
  .map-legend { display: flex; flex-wrap: wrap; gap: 10px 16px; margin-top: 12px; font-size: 13px; }
  .map-legend span { display: inline-flex; align-items: center; gap: 6px; }
  .dot { width: 13px; height: 13px; border-radius: 50%; display: inline-block; border: 2px solid #fff; box-shadow: 0 0 0 1px rgba(0,0,0,.15); }
  .dot.hotel { background: #e08ad0; } .dot.museum { background: var(--blue); } .dot.shop { background: var(--clay); }
  .dot.kids { background: #6fd6c4; } .dot.food { background: var(--gold); } .dot.nature { background: #ffb088; } .dot.base { background: #ffb088; }
  .filter-bar { display: flex; flex-wrap: wrap; gap: 8px; margin-bottom: 12px; }
  .filter-bar button { border: 1px solid var(--line); background: #fff; color: var(--muted);
    padding: 6px 13px; border-radius: 18px; font-size: 13px; cursor: pointer; }
  .filter-bar button.active { background: var(--celadon-d); color: #fff; border-color: var(--celadon-d); }
  /* day */
  .day { background: var(--card); border: 1px solid var(--line); border-radius: 14px; margin-bottom: 14px; overflow: hidden; }
  .day-head { background: linear-gradient(90deg, #fdf6ee, #f7ecdf); padding: 13px 18px;
    display: flex; align-items: baseline; gap: 12px; border-bottom: 1px solid var(--line); flex-wrap: wrap; }
  .day-head .d { font-size: 17px; font-weight: 700; color: var(--clay-d); }
  .day-head .date { font-size: 13px; color: var(--muted); }
  .day-head .theme { margin-left: auto; font-size: 13px; color: var(--celadon-d); }
  .day-body { padding: 6px 18px 16px; }
  .tl { position: relative; padding-left: 22px; }
  .tl::before { content: ""; position: absolute; left: 6px; top: 6px; bottom: 6px; width: 2px; background: var(--line); }
  .ev { position: relative; padding: 12px 0; border-bottom: 1px dashed var(--line); }
  .ev:last-child { border-bottom: none; }
  .ev::before { content: ""; position: absolute; left: -19px; top: 18px; width: 11px; height: 11px; border-radius: 50%;
    background: var(--celadon); border: 2px solid #fff; box-shadow: 0 0 0 1px var(--celadon); }
  .ev .t { font-size: 13px; color: var(--muted); font-weight: 600; }
  .ev .act { font-size: 15px; font-weight: 600; margin: 2px 0; }
  .ev .addr { font-size: 12.5px; color: var(--clay-d); margin-top: 3px; }
  .ev .note { font-size: 13px; color: var(--muted); }
  .ev.empty .act { color: var(--muted); font-weight: 400; font-style: italic; }
  .ev.empty::before { background: var(--muted); box-shadow: 0 0 0 1px var(--muted); }
  .tag { display: inline-block; font-size: 11px; padding: 1px 8px; border-radius: 10px; margin-right: 6px;
    background: #e8f7f3; color: #2f9b85; vertical-align: middle; }
  /* 专属测评 */
  .ev .stars { color: #ffb400; letter-spacing: 2px; font-size: 14px; margin-left: 6px; vertical-align: middle; }
  .ev .stars .num { color: var(--muted); font-size: 12px; letter-spacing: 0; margin-left: 4px; }
  .rating-reason { margin-top: 8px; background: #fff8ec; border-left: 3px solid var(--gold);
    border-radius: 0 8px 8px 0; padding: 8px 12px; font-size: 13px; color: #7a5a2a; line-height: 1.65; }
  .rating-reason .who { font-weight: 700; color: var(--clay-d); margin-right: 2px; }
  /* photos */
  .gal { display: grid; grid-template-columns: repeat(auto-fill, minmax(150px, 1fr)); gap: 8px; margin-top: 10px; }
  .gal .ph { width: 100%; height: 150px; object-fit: cover; border-radius: 10px; border: 1px solid var(--line);
    background: #f3efe8; cursor: pointer; transition: transform .15s; }
  .gal .ph:active { transform: scale(.97); }
  .ph-empty { margin-top: 10px; border: 2px dashed var(--line); border-radius: 10px; padding: 18px;
    text-align: center; color: var(--muted); font-size: 13px; background: #fbf6ec; }
  .cap { font-size: 12px; color: var(--muted); margin-top: 4px; text-align: center; }
  /* lightbox */
  #lb { display: none; position: fixed; inset: 0; background: rgba(0,0,0,.9); z-index: 9999;
    align-items: center; justify-content: center; flex-direction: column; padding: 20px; }
  #lb img { max-width: 100%; max-height: 82vh; border-radius: 10px; }
  #lb .lb-cap { color: #fff; margin-top: 12px; font-size: 14px; text-align: center; }
  #lb .lb-close { position: absolute; top: 16px; right: 20px; color: #fff; font-size: 30px; cursor: pointer; }
  footer { text-align: center; color: var(--muted); font-size: 12px; padding: 20px; }
  @media (max-width: 600px) {
    #map { height: 380px; }
    .gal { grid-template-columns: repeat(2, 1fr); }
    .gal .ph { height: 120px; }
  }
</style>
</head>
<body>

<div class="hero">
  <h1>🏺 __TITLE__</h1>
  <div class="sub">__SUBTITLE__</div>
  <div class="meta">
    <span class="chip">📅 __DATES__</span>
    <span class="chip">🚗 __TRIP__</span>
    <span class="chip">👧 一大一小(10岁)</span>
  </div>
</div>

<div class="progress">
  <div class="bar"><i style="width:__PCT__%"></i></div>
  <div class="txt">__PROGRESSTXT__ · 最后更新 __UPDATED__</div>
</div>

<div class="wrap">

  <section>
    <h2><span class="ic">🗺️</span>旅行地图 · 标注所有目的地</h2>
    <div class="filter-bar" id="filterBar">
      <button class="active" data-cat="all">全部</button>
      <button data-cat="hotel">🏨 酒店</button>
      <button data-cat="museum">博物馆</button>
      <button data-cat="shop">门店/市集</button>
      <button data-cat="kids">亲子手工</button>
      <button data-cat="food">美食</button>
      <button data-cat="nature">自然/古镇</button>
      <button data-cat="base">交通/基地</button>
    </div>
    <div id="map"></div>
    <div class="map-legend">
      <span><i class="dot hotel"></i>酒店（已订）</span>
      <span><i class="dot museum"></i>博物馆/展馆</span>
      <span><i class="dot shop"></i>门店/市集</span>
      <span><i class="dot kids"></i>亲子手工</span>
      <span><i class="dot food"></i>美食</span>
      <span><i class="dot nature"></i>自然/古镇</span>
      <span><i class="dot base"></i>机场/租车</span>
    </div>
  </section>

  <section>
    <h2><span class="ic">📅</span>每日相册（按行程时间）</h2>
    __DAYS__
  </section>

  <div class="ph-empty" style="border-style:solid;">
    📷 照片每天都在更新中～ 拍完发给我，我就帮你加到对应那一天的格子里。
  </div>
</div>

<footer>景德镇亲子游相册 · 由攻略自动生成 · 地图数据 © 高德地图</footer>

<div id="lb"><span class="lb-close" onclick="closeLightbox()">×</span><img src="" alt=""><div class="lb-cap"></div></div>

<script>
function openLightbox(img){
  var o = document.getElementById('lb');
  o.querySelector('img').src = img.src;
  o.querySelector('img').alt = img.alt;
  o.querySelector('.lb-cap').textContent = img.alt || '';
  o.style.display = 'flex';
}
function closeLightbox(){ document.getElementById('lb').style.display = 'none'; }
document.getElementById('lb').addEventListener('click', function(e){ if(e.target === this) closeLightbox(); });

// ===== 地图 =====
var map = L.map('map', { scrollWheelZoom: true }).setView(__CENTER__, __ZOOM__);
L.tileLayer('https://webrd01.is.autonavi.com/appmaptile?lang=zh_cn&size=1&scale=1&style=8&x={x}&y={y}&z={z}', {
  maxZoom: 18, attribution: '© 高德地图'
}).addTo(map);

var places = __PLACES__;
var colorMap = { museum:'#6fb1e0', shop:'#ff8c69', kids:'#6fd6c4', food:'#ffc861', nature:'#ffb088', base:'#ffb088', hotel:'#e08ad0' };
var markers = {};
places.forEach(function(p){
  var m = L.circleMarker([p.lat, p.lng], {
    radius: p.cat==='hotel'?10:8, color:'#fff', weight:2,
    fillColor: colorMap[p.cat] || '#999', fillOpacity: 1
  }).addTo(map);
  m.bindPopup('<b>'+p.name+'</b><br>'+(p.desc||'').replace(/\n/g,'<br>'));
  markers[p.cat] = markers[p.cat] || [];
  markers[p.cat].push(m);
});
document.getElementById('filterBar').addEventListener('click', function(e){
  if (e.target.tagName !== 'BUTTON') return;
  document.querySelectorAll('#filterBar button').forEach(function(b){ b.classList.remove('active'); });
  e.target.classList.add('active');
  var cat = e.target.dataset.cat;
  Object.keys(markers).forEach(function(k){
    var show = (cat === 'all' || cat === k);
    markers[k].forEach(function(m){ if (show) m.addTo(map); else map.removeLayer(m); });
  });
});
</script>

</body>
</html>
"""


def render_stars(n):
    n = max(0, min(5, int(n)))
    filled = "⭐" * n
    empty = "☆" * (5 - n)
    return '<span class="stars" title="%d 星">%s%s<span class="num">%d/5</span></span>' % (n, filled, empty, n)


def render_event(ev):
    photos = ev.get("photos", [])
    if ev.get("empty"):
        return ('<div class="ev empty"><div class="t">%s</div><div class="act">%s</div></div>'
                % (ev.get("time", ""), ev.get("act", "")))
    cells = ""
    if photos:
        for p in photos:
            src = p["src"]
            cap = p.get("caption", "")
            cells += ('<img class="ph" src="%s" alt="%s" onclick="openLightbox(this)" loading="lazy">'
                      % (src, cap))
        gal = '<div class="gal">%s</div>' % cells
    else:
        gal = '<div class="ph-empty">📷 待添加照片</div>'
    tag = ('<span class="tag">%s</span>' % CAT_LABEL.get(ev["cat"], "")) if ev.get("cat") else ""
    note = ('<div class="note">%s</div>' % ev["note"]) if ev.get("note") else ""
    addr = ('<div class="addr">📍 %s</div>' % ev["addr"]) if ev.get("addr") else ""
    stars = render_stars(ev["rating"]) if ev.get("rating") is not None else ""
    rr = ev.get("rating_reason")
    rr_html = ('<div class="rating-reason"><span class="who">🤖 我的专属测评</span>：%s</div>' % rr) if rr else ""
    return ('<div class="ev"><div class="t">%s</div><div class="act">%s%s%s</div>%s%s%s%s</div>'
            % (ev.get("time", ""), tag, ev.get("act", ""), stars, addr, note, rr_html, gal))


def render_day(d):
    events = "".join(render_event(ev) for ev in d["events"])
    emoji = d.get("emoji", "")
    date_label = ("%s %s" % (emoji, d["date"])) if emoji else d["date"]
    return ('<div class="day"><div class="day-head"><span class="d">%s</span>'
            '<span class="date">%s</span><span class="theme">%s</span></div>'
            '<div class="day-body"><div class="tl">%s</div></div></div>'
            % (d["d"], date_label, d.get("theme", ""), events))


def main():
    data = load()
    meta = data.get("meta", {})
    days = data["days"]
    mapdata = data.get("map", {})
    places = mapdata.get("places", [])

    total_days = len(days)
    total_photos = sum(len(ev.get("photos", [])) for d in days for ev in d["events"])
    done_days = sum(1 for d in days if any(ev.get("photos") for ev in d["events"]))
    pct = round(100 * done_days / total_days) if total_days else 0
    progress_txt = "已记录 %d/%d 天 · 共 %d 张照片" % (done_days, total_days, total_photos)
    updated = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

    html = (TEMPLATE
            .replace("__TITLE__", meta.get("title", "景德镇亲子游 · 相册"))
            .replace("__SUBTITLE__", meta.get("subtitle", ""))
            .replace("__DATES__", meta.get("dates", ""))
            .replace("__TRIP__", meta.get("trip", ""))
            .replace("__PCT__", str(pct))
            .replace("__PROGRESSTXT__", progress_txt)
            .replace("__UPDATED__", updated)
            .replace("__DAYS__", "".join(render_day(d) for d in days))
            .replace("__CENTER__", str(mapdata.get("center", [29.26, 117.20])))
            .replace("__ZOOM__", str(mapdata.get("zoom", 11)))
            .replace("__PLACES__", json.dumps(places, ensure_ascii=False)))

    out = os.path.join(ROOT, "index.html")
    with open(out, "w", encoding="utf-8") as f:
        f.write(html)
    print("生成成功: %s" % out)
    print("进度: %s (%.0f%%)" % (progress_txt, pct))


if __name__ == "__main__":
    main()
