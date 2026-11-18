"""แปลง URL เป็นตัวเลข (features) ให้โมเดลเรียนรู้ได้

v2: ดูเฉพาะ "ชื่อโดเมน" (host) เท่านั้น
เหตุผล: ใน PhiUSIIL ลิงก์ปลอดภัยเกือบทั้งหมดเป็นหน้าแรก (https://www.xxx.com)
ถ้าให้โมเดลดู http/https, www หรือ path โมเดลจะจำ "รูปแบบการเก็บข้อมูล"
แทนที่จะเรียนรู้ว่าอะไรคือ phishing จริง ๆ (เรียกว่า shortcut learning / data leakage)
"""
import math
import re
from collections import Counter
from urllib.parse import urlparse

import pandas as pd

SUSPICIOUS_WORDS = ["login", "verify", "account", "update", "secure",
                    "bank", "confirm", "password", "signin", "wallet"]
IP_PATTERN = re.compile(r"^\d{1,3}(\.\d{1,3}){3}$")


def get_host(url: str) -> str:
    url = str(url).strip().lower()
    if "://" not in url:
        url = "http://" + url
    host = urlparse(url).netloc.split("@")[-1].split(":")[0]
    if host.startswith("www."):
        host = host[4:]
    return host


def entropy(s: str) -> float:
    if not s:
        return 0.0
    counts = Counter(s)
    return -sum(c / len(s) * math.log2(c / len(s)) for c in counts.values())


def extract_features(url: str) -> dict:
    host = get_host(url)
    parts = host.split(".")
    tld = parts[-1] if len(parts) > 1 else ""
    return {
        "host_length": len(host),
        "num_dots": host.count("."),
        "num_hyphens": host.count("-"),
        "num_digits": sum(c.isdigit() for c in host),
        "digit_ratio": sum(c.isdigit() for c in host) / max(len(host), 1),
        "num_subdomains": max(len(parts) - 2, 0),
        "longest_label": max((len(p) for p in parts), default=0),
        "tld_length": len(tld),
        "host_entropy": entropy(host),
        "has_ip_host": int(bool(IP_PATTERN.match(host))),
        "has_at_in_url": int("@" in str(url)),
        "suspicious_word_count": sum(w in host for w in SUSPICIOUS_WORDS),
    }


def build_feature_frame(urls) -> pd.DataFrame:
    return pd.DataFrame([extract_features(u) for u in urls])