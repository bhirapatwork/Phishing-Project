"""ตัดรายชื่อ Tranco Top 1M ให้เหลือ N อันดับแรก แล้วเซฟไว้ที่ models/top_domains.txt

ทำไมไม่ใช้ทั้งล้าน: ไฟล์เล็กกว่า อัปขึ้น GitHub/Streamlit ได้ และเว็บอันดับท้ายๆ
ของ list บางทีก็เป็นเว็บแปลกๆ ที่ไม่ควรเชื่อ

วิธีใช้:  python src/build_toplist.py --src data/top-1m.csv --top 100000
"""
import argparse
from pathlib import Path

import pandas as pd


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--src", default="data/top-1m.csv")
    p.add_argument("--top", type=int, default=100_000)
    p.add_argument("--out", default="models/top_domains.txt")
    args = p.parse_args()

    df = pd.read_csv(args.src, header=None, names=["rank", "domain"], nrows=args.top)
    domains = df["domain"].astype(str).str.lower().str.removeprefix("www.")
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    Path(args.out).write_text("\n".join(domains.drop_duplicates()), encoding="utf-8")
    print(f"Saved {domains.nunique():,} domains -> {args.out}")


if __name__ == "__main__":
    main()
