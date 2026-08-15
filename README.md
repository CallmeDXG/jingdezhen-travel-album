# 景德镇亲子游 · 相册（可分享版）

按《景德镇亲子游攻略》自动生成的旅行相册：时间、地址与攻略完全一致，附带高德地图（微信内可正常加载）。

- 在线相册：部署到 GitHub Pages 后，会得到一个 `https://callmedxg.github.io/<仓库名>/` 的链接，直接发给妈妈、姥姥、朋友，在微信里点开即可看。
- 地图：标注了攻略里全部目的地（酒店/博物馆/亲子手工/美食/自然古镇等），可按分类筛选。
- 照片：每天拍完发给我，我加到对应那天的格子里，重新生成并推送，家人刷新就能看到。

## 目录结构

```
album/
├── index.html        # 相册页面（由脚本生成，勿手改）
├── gallery.json      # 单一数据源：每日行程 + 地图点位（改这里）
├── build_album.py    # 生成脚本：读 gallery.json → 写 index.html
├── images/           # 旅行照片放这里（按 D1_xxx.jpg 命名最清晰）
└── README.md
```

## 每天加照片（两步）

1. 把当天照片放进 `images/`，例如 `images/D1_airport.jpg`、`images/D2_museum.jpg`。
2. 在 `gallery.json` 里找到对应那天的 event，把 `photos` 从 `[]` 改成：
   ```json
   "photos": [
     { "src": "images/D1_airport.jpg", "caption": "落地啦！" },
     { "src": "images/D1_hotel.jpg", "caption": "麗枫酒店，离博物馆超近" }
   ]
   ```
3. 运行 `python3 build_album.py` 重新生成 `index.html`，然后 `git push`。

> 也可以直接把照片发给我（爸爸/你），我来加、生成并推送，你什么都不用装。

## 本地预览

```bash
cd album
python3 build_album.py
python3 -m http.server 8000   # 浏览器打开 http://localhost:8000
```

## 部署到 GitHub Pages（分享链接）

首次建仓库并开启 Pages（已登录 `gh` 时）：

```bash
cd album
git init
git add -A
git commit -m "init album"
gh repo create jingdezhen-travel-album --public --source . --push
gh api -X POST /repos/CallmeDXG/jingdezhen-travel-album/pages \
  -f source[branch]=main -f source[path]=/
```

之后每天更新只需：

```bash
git add -A
git commit -m "更新 Dn 照片"
git push
```

Pages 通常 1 分钟内自动 rebuild，家人刷新链接即可看到新照片。
