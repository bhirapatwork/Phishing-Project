"""แปลง URL เป็นตัวเลข (features) ให้โมเดลเรียนรู้ได้

v2: ดูแค่ชื่อโดเมน ไม่ดู http/https, www, path (กัน shortcut learning ของ dataset)
v3: แยกโดเมนหลัก (registered domain) ออกจาก subdomain แล้วเพิ่ม
    - is_top_domain       โดเมนหลักอยู่ในรายชื่อเว็บยอดนิยม (Tranco) ไหม
    - is_free_hosting     เป็นเว็บฝากฟรีที่ใครก็สร้าง subdomain ได้ไหม (เช่น xxx.weebly.com)
    - brand_impersonation มีชื่อแบรนด์ดังในลิงก์ แต่ไม่ใช่โดเมนจริงของแบรนด์
    - suspicious_tld      ใช้นามสกุลโดเมนที่ phishing ชอบใช้ (.xyz, .top, .tk ...)
"""
import math
import re
from collections import Counter
from pathlib import Path
from urllib.parse import urlparse

import pandas as pd

IP_PATTERN = re.compile(r"^\d{1,3}(\.\d{1,3}){3}$")

SUSPICIOUS_WORDS = ["login", "verify", "account", "update", "secure",
                    "bank", "confirm", "password", "signin", "wallet"]

# นามสกุลแบบ 2 ชั้น ต้องนับเป็นก้อนเดียว เช่น shopee.co.th -> โดเมนหลักคือ shopee.co.th ไม่ใช่ co.th
MULTI_PART_SUFFIXES = {
    "co.th", "ac.th", "go.th", "in.th", "or.th", "net.th", "mi.th",
    "co.uk", "org.uk", "ac.uk", "gov.uk",
    "com.au", "net.au", "org.au", "co.jp", "ne.jp", "ac.jp", "co.kr",
    "com.br", "com.cn", "com.sg", "com.my", "co.id", "com.vn", "com.ph",
    "co.in", "co.nz", "com.tw", "com.hk", "com.mx", "com.tr",
}

# เว็บฝากฟรี: subdomain เป็นของผู้ใช้ทั่วไป ไม่ใช่ของบริษัท
# ถึง google.com จะอยู่ใน top list แต่ sites.google.com ใครก็สร้างหน้า phishing ได้
FREE_HOSTING = {
    "weebly.com", "wixsite.com", "wix.com", "000webhostapp.com", "blogspot.com",
    "github.io", "netlify.app", "vercel.app", "pages.dev", "web.app",
    "firebaseapp.com", "herokuapp.com", "glitch.me", "repl.co", "godaddysites.com",
    "webflow.io", "square.site", "wordpress.com", "sites.google.com",
    "ngrok.io", "ngrok-free.app", "duckdns.org", "azurewebsites.net",
}

# ชื่อแบรนด์ -> โดเมนจริงของแบรนด์
BRANDS = {
    "paypal": {"paypal.com"},
    "apple": {"apple.com", "icloud.com"},
    "icloud": {"icloud.com", "apple.com"},
    "microsoft": {"microsoft.com", "live.com", "office.com"},
    "office365": {"office.com", "microsoft.com"},
    "outlook": {"outlook.com", "live.com", "office.com"},
    "google": {"google.com", "google.co.th", "youtube.com"},
    "gmail": {"google.com", "gmail.com"},
    "facebook": {"facebook.com", "fb.com"},
    "instagram": {"instagram.com"},
    "netflix": {"netflix.com"},
    "amazon": {"amazon.com", "amazon.co.jp", "amazon.co.uk"},
    "roblox": {"roblox.com"},
    "steam": {"steampowered.com", "steamcommunity.com"},
    "line": {"line.me"},
    "shopee": {"shopee.co.th", "shopee.com"},
    "lazada": {"lazada.co.th", "lazada.com"},
    "kbank": {"kasikornbank.com", "kbank.co.th"},
    "kasikorn": {"kasikornbank.com"},
    "scb": {"scb.co.th"},
    "krungthai": {"krungthai.com"},
    "bangkokbank": {"bangkokbank.com"},
    "truemoney": {"truemoney.com"},
    "dhl": {"dhl.com"},
    "kerry": {"kerryexpress.com"},
    "thailandpost": {"thailandpost.co.th"},
}

SUSPICIOUS_TLDS = {"xyz", "top", "tk", "ml", "ga", "cf", "gq", "buzz", "icu",
                   "cyou", "rest", "click", "link", "live", "shop", "online",
                   "site", "work", "support", "info", "monster", "sbs"}

TOP_DOMAINS_PATH = Path(__file__).resolve().parent.parent / "models" / "top_domains.txt"
TOP_DOMAINS = set()
if TOP_DOMAINS_PATH.exists():
    TOP_DOMAINS = set(TOP_DOMAINS_PATH.read_text(encoding="utf-8").split())


def get_host(url: str) -> str:
    url = str(url).strip().lower()
    if "://" not in url:
        url = "http://" + url
    host = urlparse(url).netloc.split("@")[-1].split(":")[0].strip(".")
    if host.startswith("www."):
        host = host[4:]
    return host


def split_host(host: str):
    """คืน (subdomain, ชื่อโดเมน, นามสกุล) เช่น docs.google.com -> ('docs', 'google', 'com')"""
    if IP_PATTERN.match(host):
        return "", host, ""
    parts = host.split(".")
    if len(parts) >= 3 and ".".join(parts[-2:]) in MULTI_PART_SUFFIXES:
        return ".".join(parts[:-3]), parts[-3], ".".join(parts[-2:])
    if len(parts) >= 2:
        return ".".join(parts[:-2]), parts[-2], parts[-1]
    return "", host, ""


def entropy(s: str) -> float:
    if not s:
        return 0.0
    counts = Counter(s)
    return -sum(c / len(s) * math.log2(c / len(s)) for c in counts.values())


def is_free_hosting(host: str, registered: str) -> bool:
    return any(host == h or host.endswith("." + h) for h in FREE_HOSTING)


def brand_impersonation(host: str, registered: str) -> int:
    # ค้นทีละส่วนที่คั่นด้วยจุด ไม่งั้น app.leb2 จะต่อกันเป็น "appleb2" แล้วเจอคำว่า apple
    squashed = " ".join(part.replace("-", "") for part in host.split("."))
    for brand, official in BRANDS.items():
        if len(brand) <= 4:
            # ชื่อสั้น (line, scb, dhl) ต้องเป็นคำแยก ไม่งั้น "online" จะนับเป็น "line"
            if re.search(rf"(^|[.\-]){brand}([.\-]|$)", host) and registered not in official:
                return 1
        elif brand in squashed and registered not in official:
            return 1
    return 0


def extract_features(url: str) -> dict:
    host = get_host(url)
    sub, name, suffix = split_host(host)
    registered = f"{name}.{suffix}" if suffix else name
    free_host = is_free_hosting(host, registered)

    return {
        # จากชื่อโดเมนหลัก (ไม่รวม subdomain)
        "domain_length": len(name),
        "domain_hyphens": name.count("-"),
        "domain_digits": sum(c.isdigit() for c in name),
        "domain_entropy": entropy(name),
        "tld_length": len(suffix),
        "suspicious_tld": int(suffix.split(".")[-1] in SUSPICIOUS_TLDS),
        # จาก subdomain
        "subdomain_length": len(sub),
        "num_subdomains": len(sub.split(".")) if sub else 0,
        # ทั้ง host
        "host_length": len(host),
        "has_ip_host": int(bool(IP_PATTERN.match(host))),
        "has_at_in_url": int("@" in str(url)),
        "suspicious_word_count": sum(w in host for w in SUSPICIOUS_WORDS),
        # v3
        "is_top_domain": int(registered in TOP_DOMAINS and not free_host),
        "is_free_hosting": int(free_host),
        "brand_impersonation": brand_impersonation(host, registered),
    }


def build_feature_frame(urls) -> pd.DataFrame:
    return pd.DataFrame([extract_features(u) for u in urls])
