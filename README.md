# 🛡️ Spam Email Detector

A production-ready spam email classifier built with Python,
TF-IDF vectorization, and classical ML algorithms.

---

## 📁 Project Structure

```
spam_detector/
├── spam_detector.py   ← Core ML pipeline (preprocessing, training, prediction)
├── app.py             ← Streamlit web UI
├── requirements.txt   ← Python dependencies
└── README.md
```

---

## ⚙️ Setup & Installation

### 1. Clone / download this folder

### 2. Create a virtual environment (recommended)
```bash
python -m venv venv
source venv/bin/activate        # macOS / Linux
venv\Scripts\activate           # Windows
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. (Optional) Download the real dataset
Get the SMS Spam Collection from:
https://archive.ics.uci.edu/dataset/228/sms+spam+collection

Extract `SMSSpamCollection` (tab-separated file) into the project folder.
If not present, the built-in sample data is used automatically.

---

## 🚀 Run the App

### Web UI (Streamlit)
```bash
streamlit run app.py
```
Then open http://localhost:8501 in your browser.

### Command-line demo
```bash
python spam_detector.py
```

---

## 🧠 How It Works

```
Raw Email
    ↓
Preprocessing
  • Lowercase
  • Remove URLs, emails, numbers
  • Remove punctuation
  • Tokenize + remove stopwords
  • Porter Stemming
    ↓
TF-IDF Vectorization
  (5000 features, unigrams + bigrams)
    ↓
ML Model
  • Naive Bayes        ← default, fastest
  • Logistic Regression
  • Support Vector Machine
    ↓
Prediction: SPAM 🚨 or HAM ✅ + Confidence %
```

---

## 📊 Expected Performance (on SMS Spam Collection)

| Model               | Accuracy | Precision | Recall | F1    |
|---------------------|----------|-----------|--------|-------|
| Naive Bayes         | ~98%     | ~97%      | ~94%   | ~96%  |
| Logistic Regression | ~98%     | ~97%      | ~95%   | ~96%  |
| SVM                 | ~98%     | ~98%      | ~94%   | ~96%  |

---

## 🔧 Using the API Directly

```python
from spam_detector import SpamDetector, load_sample_data

# Train
detector = SpamDetector(model_type='naive_bayes')
df = load_sample_data()
detector.train(df)

# Predict
result = detector.predict("You've won a FREE iPhone! Click here now.")
print(result)
# {'label': 'SPAM', 'is_spam': True, 'confidence': 97.3, 'clean_text': '...'}

# Save & reload
detector.save('my_model.pkl')
detector2 = SpamDetector.load('my_model.pkl')

# Batch predict
emails = ["Hello, how are you?", "WIN £1000 NOW!"]
results = detector.predict_batch(emails)
```

---

## 📦 Dependencies

| Library       | Purpose                        |
|---------------|--------------------------------|
| scikit-learn  | ML models + TF-IDF             |
| pandas        | Data handling                  |
| numpy         | Numerical operations           |
| nltk          | Stopwords + stemming           |
| streamlit     | Web UI                         |

---

## 🔮 Ideas to Extend

- Add email subject line as a separate feature
- Use deep learning (BERT, DistilBERT) for higher accuracy
- Add an API endpoint with FastAPI
- Connect to Gmail API for real-time classification
- Add explainability (LIME / SHAP) to show why an email is spam
