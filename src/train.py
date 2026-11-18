"""เทรนโมเดลตรวจจับ phishing URL

วิธีใช้:  python src/train.py --data data/phishing.csv --url-col url --label-col label
(label: 1 = phishing, 0 = ปลอดภัย)
"""
import argparse
from pathlib import Path

import joblib
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.model_selection import train_test_split

from features import build_feature_frame


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--data", default="data/phishing.csv")
    p.add_argument("--url-col", default="url")
    p.add_argument("--label-col", default="label")
    p.add_argument("--out", default="models/model.joblib")
    p.add_argument("--drop", nargs="*", default=[],
                   help="feature ที่ไม่อยากให้โมเดลใช้ เช่น --drop num_subdomains subdomain_length")
    args = p.parse_args()

    df = pd.read_csv(args.data).dropna(subset=[args.url_col, args.label_col])
    X = build_feature_frame(df[args.url_col]).drop(columns=args.drop)
    if args.drop:
        print("Dropped features:", args.drop)
    y = df[args.label_col].astype(int)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y)

    model = RandomForestClassifier(n_estimators=100, max_depth=20,
                                   min_samples_leaf=5, random_state=42, n_jobs=-1)
    model.fit(X_train, y_train)

    pred = model.predict(X_test)
    print(classification_report(y_test, pred, digits=3))
    print("Confusion matrix:\n", confusion_matrix(y_test, pred))

    # feature ไหนที่โมเดลใช้ตัดสินมากที่สุด (เอาไปเขียนใน README ได้)
    importance = pd.Series(model.feature_importances_, index=X.columns)
    print("\nFeature importance:")
    print(importance.sort_values(ascending=False).round(3).to_string())

    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    joblib.dump({"model": model, "columns": list(X.columns)}, args.out, compress=3)
    print(f"Saved model -> {args.out}")


if __name__ == "__main__":
    main()
