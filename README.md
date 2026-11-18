# Phishing URL Detector

โปรเจกต์ ML ตรวจลิงก์ phishing จากหน้าตาของลิงก์อย่างเดียว ไม่ต้องเปิดเข้าไปในเว็บ ทำเป็นเว็บแอปด้วย Streamlit ให้ลองวางลิงก์เล่นได้

Demo: (ยังไม่ได้ deploy)

## ทำไมถึงทำ

ตอนเรียนวิชา cybersecurity เจอว่า phishing ยังเป็นวิธีที่คนโดนหลอกเอารหัสผ่านไปมากที่สุด เลยอยากลองดูว่าถ้าใช้ machine learning ดูแค่ตัวลิงก์ จะบอกได้ไหมว่าลิงก์ไหนน่าสงสัย ก่อนที่จะมีคนกดเข้าไป

## Dataset

[PhiUSIIL Phishing URL Dataset](https://archive.ics.uci.edu/dataset/967) จาก UCI มีประมาณ 235,000 ลิงก์ (ปลอดภัย 134,850 / phishing 100,945)

ใน dataset นี้ label 1 = ปลอดภัย, 0 = phishing ซึ่งกลับกับที่ผมใช้ เลยกลับค่าก่อนเทรน

## ที่ผ่านมาเจออะไรบ้าง

**v1** ใช้ feature จากทั้งลิงก์ (ความยาว, จำนวนจุด, มี https ไหม, ความยาว path ฯลฯ) ได้ accuracy 99.6% ดูดีมาก

แต่พอลองวางลิงก์ YouTube กับ Roblox ในแอป มันบอกว่าเป็น phishing 100% ไปไล่ดูแล้วเจอว่าลิงก์ปลอดภัยใน dataset เกือบทั้งหมดเป็นหน้าแรกแบบ `https://www.xxx.com` โมเดลเลยจำว่า "สั้น + มี https + มี www = ปลอดภัย" ไม่ได้เรียนรู้ว่า phishing หน้าตาเป็นยังไงจริงๆ (shortcut learning)

**v2** ตัด http/https, www และ path ออก ให้ดูแค่ชื่อโดเมนอย่างเดียว เช่น ความยาว, entropy ของตัวอักษร, สัดส่วนตัวเลข, ความยาว TLD

ตอนเทรนครั้งแรกไฟล์โมเดลใหญ่ 213MB GitHub ไม่รับ (limit 100MB) เลยจำกัดความลึกของต้นไม้กับบีบอัดไฟล์ เหลือ 8.9MB

| | v1 | v2 |
|---|---|---|
| Accuracy | 0.996 | 0.822 |
| Precision (phishing) | 0.999 | 0.906 |
| Recall (phishing) | 0.991 | 0.653 |

คะแนนลดลงเยอะ แต่ v2 ใช้กับลิงก์จริงได้ดีกว่า ส่วน v1 สูงเพราะใช้ทางลัดของ dataset

## ลองกับลิงก์จริง (v2)

| ลิงก์ | ผลที่ได้ | ถูกไหม |
|---|---|---|
| `https://www.roblox.com/home` | ปลอดภัย 71% | ถูก |
| `https://shopee.co.th/product/123` | ปลอดภัย 89% | ถูก |
| `http://paypal-secure-login.verify-acc.xyz` | phishing 100% | ถูก |
| `http://192.168.10.5/bank/login` | phishing 100% | ถูก |
| `http://kbank-update-account.com` | phishing 72% | ถูก (แต่ไม่ค่อยมั่นใจ) |
| `https://docs.google.com/document/d/abc123` | phishing 100% | ผิด |

## ข้อจำกัดที่ยังมี

- recall แค่ 0.65 คือยังปล่อยลิงก์ phishing หลุดไปประมาณ 1 ใน 3 สำหรับงาน security ถือว่ายังไม่พอ
- โมเดลคิดว่ามี subdomain = อันตราย เลยทาย `docs.google.com` ผิด
- ลิงก์ที่เอาชื่อแบรนด์มาปลอม เช่น `kbank-update-account.com` ยังจับได้แบบไม่มั่นใจ

## จะทำต่อ (v3)

- แยกโดเมนหลักออกจาก subdomain (`docs.google.com` -> `google.com`)
- เช็กว่าโดเมนอยู่ใน Tranco Top 1M ไหม
- เพิ่ม feature จับลิงก์ที่มีชื่อแบรนด์ดังแต่ไม่ใช่โดเมนจริงของแบรนด์นั้น

## ใช้อะไรทำ

Python, pandas, scikit-learn (Random Forest), Streamlit

## โครงสร้าง

```
app.py              เว็บแอป Streamlit
src/features.py     แปลงลิงก์เป็นตัวเลขให้โมเดล
src/train.py        เทรน วัดผล แล้วเซฟโมเดล
models/             ไฟล์โมเดล
data/               dataset (ไม่ได้อัปขึ้น GitHub ต้องโหลดเอง)
```

## รันเอง

```bash
python -m venv .venv
.venv\Scripts\Activate.ps1        # Mac/Linux: source .venv/bin/activate
pip install -r requirements.txt
```

โหลด dataset ไปไว้ใน `data/` แล้วกลับ label:

```bash
python -c "import pandas as pd; df=pd.read_csv('data/PhiUSIIL_Phishing_URL_Dataset.csv'); pd.DataFrame({'url':df['URL'],'label':1-df['label']}).to_csv('data/phishing.csv',index=False)"
```

เทรนแล้วเปิดแอป:

```bash
python src/train.py
streamlit run app.py
```

---

ทำโดย Bhirapat ([GitHub](https://github.com/bhirapatwork))
