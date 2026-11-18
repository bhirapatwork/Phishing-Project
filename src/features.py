"""แปลง URL เป็นตัวเลข (features) ให้โมเดลเรียนรู้ได้"""
import re
from urllib.parse import urlparse

import pandas as pd

SUSPICIOUS_WORDS = ["login", "verify", "account", "update", "secure",
                    "bank", "confirm", "password", "signin", "wallet"]
IP_PATTERN = re.compile(r"^\d{1,3}(\.\d{1,3}){3}$")


def extract_features(url: str) -> dict:
    url = str(url).strip()
    if not url.startswith(("http://", "https://")):
        url = "http://" + url
    parsed = urlparse(url)
    host = parsed.netloc.lower().split(":")[0]
    lower = url.lower()

    return {
        "url_length": len(url),
        "host_length": len(host),
        "path_length": len(parsed.path),
        "num_dots": url.count("."),
        "num_hyphens": url.count("-"),
        "num_digits": sum(c.isdigit() for c in url),
        "num_special": sum(c in "@?=&%_~" for c in url),
        "num_subdomains": max(host.count(".") - 1, 0),
        "has_at_symbol": int("@" in url),
        "has_ip_host": int(bool(IP_PATTERN.match(host))),
        "uses_https": int(parsed.scheme == "https"),
        "suspicious_word_count": sum(w in lower for w in SUSPICIOUS_WORDS),
    }


def build_feature_frame(urls) -> pd.DataFrame:
    return pd.DataFrame([extract_features(u) for u in urls])
