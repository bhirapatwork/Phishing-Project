"""เว็บแอปเดโม่: วาง URL แล้วให้โมเดลทำนาย  (รัน: streamlit run app.py)"""
import sys
from pathlib import Path

import joblib
import streamlit as st

sys.path.append(str(Path(__file__).parent / "src"))
from features import build_feature_frame  # noqa: E402

st.set_page_config(page_title="Phishing URL Detector", page_icon="🛡️")
st.title("🛡️ Phishing URL Detector")
st.caption("Machine learning model that flags suspicious URLs from their structure.")

MODEL_PATH = Path("models/model.joblib")
if not MODEL_PATH.exists():
    st.error("ยังไม่มีโมเดล — รัน `python src/train.py` ก่อน")
    st.stop()

bundle = joblib.load(MODEL_PATH)
model, columns = bundle["model"], bundle["columns"]

url = st.text_input("Paste a URL", placeholder="http://secure-login-paypal.example.com/verify")
if url:
    X = build_feature_frame([url])[columns]
    prob = model.predict_proba(X)[0][1]
    if prob >= 0.5:
        st.error(f"⚠️ Likely PHISHING — {prob:.0%} confidence")
    else:
        st.success(f"✅ Looks safe — {1 - prob:.0%} confidence")
    with st.expander("Features the model saw"):
        st.dataframe(X.T.rename(columns={0: "value"}))
