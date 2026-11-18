# 🛡️ Phishing URL Detector

A machine learning project that detects phishing URLs using only the structure of the link (length, symbols, subdomains, suspicious keywords), with a live Streamlit demo.

**Live demo:** _(add your Streamlit Cloud link here)_

## Why
Phishing is one of the most common ways attackers steal credentials. This project explores whether a lightweight model can flag suspicious links *before* a user clicks them, without visiting the page.

## Results
| Metric | Score |
|---|---|
| Accuracy | _fill in_ |
| Precision (phishing) | _fill in_ |
| Recall (phishing) | _fill in_ |

_Add a confusion matrix image and a feature-importance chart here._

## Tech stack
Python · pandas · scikit-learn (Random Forest) · Streamlit · Git/GitHub

## Project structure
```
├── app.py              # Streamlit web app
├── src/
│   ├── features.py     # URL → numeric features
│   └── train.py        # train + evaluate + save model
├── notebooks/          # EDA (exploratory data analysis)
├── models/             # saved model
└── data/               # dataset (not committed)
```

## How to run
```bash
python -m venv .venv
# Windows: .venv\Scripts\activate   |  macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
python src/train.py --data data/phishing.csv --url-col url --label-col label
streamlit run app.py
```

## Dataset
_Name, link and licence of the dataset you used._

## What I learned / next steps
- _e.g. which features mattered most, where the model fails, ideas to improve_

## Author
Bhirapat — [GitHub](https://github.com/bhirapatwork)
