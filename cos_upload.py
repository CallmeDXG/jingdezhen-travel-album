#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
cos_upload.py —— 把相册 images/ 下的全部照片上传到腾讯云 COS（国内图床）。

前置条件（一次性）：
  1) 腾讯云控制台开通「对象存储 COS」，建一个【公共读】Bucket（地域建议 ap-shanghai）。
  2) 访问管理 CAM 建子账号，授予 QcloudCOSFullAccess 权限，拿到 SecretId / SecretKey。
  3) 在同目录创建 .cos_config.json（已被 .gitignore 排除，不会上传到 GitHub）：
     {
       "enabled": true,
       "bucket": "jdz-album-125xxxxxxx",
       "region": "ap-shanghai",
       "cdn_base": "https://jdz-album-125xxxxxxx.cos.ap-shanghai.myqcloud.com",
       "secret_id": "AKIDxxxxxxxx",
       "secret_key": "xxxxxxxx"
     }

用法：
    python3 cos_upload.py            # 上传 images/ 下所有图片（已存在则覆盖）
    python3 cos_upload.py --check    # 仅打印将上传的文件，不真正上传

不依赖官方 SDK，纯标准库 + requests 实现 COS XML API 签名（避开沙箱内存限制）。
"""
import os
import sys
import json
import time
import hmac
import hashlib
from urllib.parse import quote

try:
    import requests
except ImportError:
    print("缺少 requests，请先执行: pip install requests")
    sys.exit(1)

ROOT = os.path.dirname(os.path.abspath(__file__))
IMAGES_DIR = os.path.join(ROOT, "images")
CONFIG_PATH = os.path.join(ROOT, ".cos_config.json")
SUPPORTED = (".jpg", ".jpeg", ".png", ".webp", ".gif", ".heic", ".avif")


def sign(secret_id, secret_key, method, uri, params, headers, expire=600):
    now = int(time.time())
    sign_time = "%d;%d" % (now, now + expire)
    sign_key = hmac.new(secret_key.encode("utf-8"), sign_time.encode("utf-8"), hashlib.sha1).hexdigest()

    http_method = method.lower()
    param_keys = sorted(params.keys())
    url_param_list = ";".join(param_keys)
    http_params = "&".join("%s=%s" % (k, quote(str(params[k]), safe="-_.~")) for k in param_keys)

    header_items = sorted((h.lower(), str(headers[h])) for h in headers)
    http_header_list = ";".join(k for k, v in header_items)
    http_headers = "&".join("%s=%s" % (k, quote(v, safe="-_.~")) for k, v in header_items)

    fmt_str = "%s\n%s\n%s\n%s\n" % (http_method, uri, http_params, http_headers)
    str_to_sign = "sha1\n%s\n%s\n" % (sign_time, hashlib.sha1(fmt_str.encode("utf-8")).hexdigest())
    signature = hmac.new(sign_key.encode("utf-8"), str_to_sign.encode("utf-8"), hashlib.sha1).hexdigest()

    return ("q-sign-algorithm=sha1&q-ak=%s&q-sign-time=%s&q-key-time=%s"
            "&q-url-param-list=%s&q-header-list=%s&q-signature=%s"
            % (secret_id, sign_time, sign_time, url_param_list, http_header_list, signature))


def collect_images():
    files = []
    for name in sorted(os.listdir(IMAGES_DIR)):
        if name.lower().endswith(SUPPORTED):
            files.append(name)
    return files


def upload_one(bucket, region, secret_id, secret_key, key, data):
    host = "%s.cos.%s.myqcloud.com" % (bucket, region)
    enc_key = quote(key, safe="/")
    url = "https://%s/%s" % (host, enc_key)
    headers = {"Host": host, "Content-Type": "image/jpeg"}
    auth = sign(secret_id, secret_key, "put", "/" + enc_key, {}, headers)
    headers["Authorization"] = auth
    r = requests.put(url, data=data, headers=headers, timeout=60)
    return r.status_code, r.text[:200]


def main():
    check_only = "--check" in sys.argv
    if not os.path.exists(CONFIG_PATH):
        print("未找到 .cos_config.json，请先按脚本顶部说明创建配置文件（含 bucket/region/secret_id/secret_key）。")
        sys.exit(1)
    cfg = json.load(open(CONFIG_PATH, encoding="utf-8"))
    bucket = cfg["bucket"]
    region = cfg["region"]
    secret_id = cfg["secret_id"]
    secret_key = cfg["secret_key"]

    files = collect_images()
    print("将上传 %d 张照片到 COS bucket=%s region=%s" % (len(files), bucket, region))
    if check_only:
        for n in files:
            print("  -", "images/" + n)
        return

    ok = 0
    for n in files:
        path = os.path.join(IMAGES_DIR, n)
        key = "images/" + n
        with open(path, "rb") as f:
            data = f.read()
        try:
            code, msg = upload_one(bucket, region, secret_id, secret_key, key, data)
            if 200 <= code < 300:
                ok += 1
                print("  ✓ %s (%dKB)" % (key, len(data) // 1024))
            else:
                print("  ✗ %s -> HTTP %d %s" % (key, code, msg))
        except Exception as e:
            print("  ✗ %s -> 异常 %s" % (key, e))
    print("完成：成功 %d / 共 %d" % (ok, len(files)))
    if ok == len(files):
        print("下一步：确认 .cos_config.json 的 enabled=true，然后运行 python3 build_album.py 重新生成，git push 即可。")
    else:
        print("部分失败，请检查网络/密钥后重跑本脚本（已成功的会被覆盖重传，安全）。")


if __name__ == "__main__":
    main()
