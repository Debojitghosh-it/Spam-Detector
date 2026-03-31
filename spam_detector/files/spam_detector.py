import pandas as pd
import numpy as np
import re
import pickle
import os
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.linear_model import LogisticRegression
from sklearn.svm import LinearSVC
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score,
    f1_score, confusion_matrix, classification_report
)
import nltk
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer

# Download required NLTK data
nltk.download('stopwords', quiet=True)
nltk.download('punkt', quiet=True)

# ─────────────────────────────────────────────
# 1. TEXT PREPROCESSING
# ─────────────────────────────────────────────

stemmer = PorterStemmer()
stop_words = set(stopwords.words('english'))


def preprocess_text(text: str) -> str:
    """
    Clean and normalize raw email text.
    Steps:
      - Lowercase
      - Remove URLs, email addresses, numbers
      - Remove punctuation / special chars
      - Tokenize
      - Remove stopwords
      - Stem each token
    """
    text = text.lower()
    text = re.sub(r'http\S+|www\S+', ' url ', text)          # URLs
    text = re.sub(r'\S+@\S+', ' email ', text)               # Email addresses
    text = re.sub(r'\d+', ' num ', text)                     # Numbers
    text = re.sub(r'[^a-z\s]', ' ', text)                   # Punctuation
    text = re.sub(r'\s+', ' ', text).strip()                 # Extra whitespace

    tokens = text.split()
    tokens = [stemmer.stem(t) for t in tokens if t not in stop_words and len(t) > 1]
    return ' '.join(tokens)


# ─────────────────────────────────────────────
# 2. DATA LOADING
# ─────────────────────────────────────────────

def load_dataset(filepath: str) -> pd.DataFrame:
    """
    Load the SMS Spam Collection dataset.
    Expected columns: label (ham/spam), message
    Supports tab-separated format from UCI repository.
    """
    df = pd.read_csv(filepath, sep='\t', header=None,
                     names=['label', 'message'], encoding='latin-1')
    df.dropna(inplace=True)
    df.drop_duplicates(inplace=True)
    df['label_enc'] = df['label'].map({'ham': 0, 'spam': 1})
    return df


def load_sample_data() -> pd.DataFrame:
    """
    Built-in sample dataset for quick demo / testing
    when no external CSV is available.
    """
    samples = [
        # Spam examples
        ("spam", "WINNER!! As a valued network customer you have been selected to receive a £900 prize reward!"),
        ("spam", "Free entry in 2 a wkly comp to win FA Cup final tkts 21st May 2005."),
        ("spam", "Nah I don't think he goes to usf, he lives around here though"),
        ("spam", "Congratulations! You've won a $1000 Walmart gift card. Click here to claim now!"),
        ("spam", "URGENT! Your mobile number has been awarded a £2,000 Bonus Caller Prize!"),
        ("spam", "SIX chances to win CASH! From 100 to 20,000 pounds txt> CSH11 and send to 87575."),
        ("spam", "England v Macedonia - dont miss the goals/team news. Txt ur national team to 87077."),
        ("spam", "Thanks for your subscription to Ringtone UK your mobile will be charged £5/month."),
        ("spam", "You have won a Nokia 6610 - call 09061743386 to claim your prize now."),
        ("spam", "FREE MESSAGE: Congratulations - you've been selected for free broadband!"),
        ("spam", "Call from 0845 7201090 for an interview. Don't miss this chance. Reply STOP to cancel."),
        ("spam", "Win a cash prize of £1000 or a luxury holiday! Send WIN to 89080 now!"),
        ("spam", "Your phone has a virus! Click here to remove it immediately or lose all data."),
        ("spam", "Claim your prize: You've been chosen as our weekly winner! Act fast!"),
        ("spam", "LIMITED TIME: Get a FREE iPhone by completing this short survey. Hurry!"),
        # Ham examples
        ("ham", "I'm gonna be home soon and i don't want to talk about this stuff anymore tonight"),
        ("ham", "Even my brother is not like to speak with me. They treat me like aids patent."),
        ("ham", "I HAVE A DATE ON SUNDAY WITH WILL!!"),
        ("ham", "As per your request 'Melle Melle (Oru Minnaminunginte Nurungu Vettam)' has been set as your callertune"),
        ("ham", "Ok lar... Joking wif u oni..."),
        ("ham", "Did you catch the game last night? What a match!"),
        ("ham", "Hey, are we still on for lunch tomorrow at 1pm?"),
        ("ham", "Can you send me the notes from today's meeting?"),
        ("ham", "I'll be there in 10 minutes, just stuck in traffic."),
        ("ham", "Happy birthday! Hope you have a wonderful day."),
        ("ham", "The project deadline has been moved to next Friday."),
        ("ham", "Let me know if you need help with the assignment."),
        ("ham", "Don't forget to pick up some milk on your way home."),
        ("ham", "The meeting has been rescheduled for 3pm in conference room B."),
        ("ham", "I got the job offer! Starting next Monday, so excited!"),
        ("ham", "Can we reschedule our call? Something came up this afternoon."),
        ("ham", "Thanks for the birthday wishes everyone, really made my day!"),
        ("ham", "Please review the attached document and share your feedback."),
        ("ham", "Looking forward to seeing you at the conference next week."),
        ("ham", "The Wi-Fi password is written on the back of the router."),
    ]
    df = pd.DataFrame(samples, columns=['label', 'message'])
    df['label_enc'] = df['label'].map({'ham': 0, 'spam': 1})
    return df


# ─────────────────────────────────────────────
# 3. SPAM DETECTOR CLASS
# ─────────────────────────────────────────────

class SpamDetector:
    """
    End-to-end spam detection pipeline.
    Supports Naive Bayes, Logistic Regression, and SVM.
    """

    MODELS = {
        'naive_bayes': MultinomialNB(alpha=0.1),
        'logistic_regression': LogisticRegression(max_iter=1000, C=1.0),
        'svm': LinearSVC(C=1.0, max_iter=1000),
    }

    def __init__(self, model_type: str = 'naive_bayes'):
        if model_type not in self.MODELS:
            raise ValueError(f"model_type must be one of {list(self.MODELS.keys())}")
        self.model_type = model_type
        self.model = self.MODELS[model_type]
        self.vectorizer = TfidfVectorizer(
            max_features=5000,
            ngram_range=(1, 2),   # unigrams + bigrams
            min_df=2,
            sublinear_tf=True,
        )
        self.is_trained = False

    # ── Training ──────────────────────────────

    def train(self, df: pd.DataFrame):
        """
        Train the model on a labelled DataFrame.
        Expects columns: 'message', 'label_enc'
        """
        print(f"\n{'='*50}")
        print(f"  Training SpamDetector ({self.model_type})")
        print(f"{'='*50}")

        df['clean'] = df['message'].apply(preprocess_text)

        X_train, X_test, y_train, y_test = train_test_split(
            df['clean'], df['label_enc'],
            test_size=0.2, random_state=42, stratify=df['label_enc']
        )

        X_train_tfidf = self.vectorizer.fit_transform(X_train)
        X_test_tfidf  = self.vectorizer.transform(X_test)

        self.model.fit(X_train_tfidf, y_train)
        self.is_trained = True

        # Evaluation
        y_pred = self.model.predict(X_test_tfidf)
        self._print_metrics(y_test, y_pred)

        return self

    def _print_metrics(self, y_true, y_pred):
        print(f"\n  Accuracy  : {accuracy_score(y_true, y_pred):.4f}")
        print(f"  Precision : {precision_score(y_true, y_pred, zero_division=0):.4f}")
        print(f"  Recall    : {recall_score(y_true, y_pred, zero_division=0):.4f}")
        print(f"  F1 Score  : {f1_score(y_true, y_pred, zero_division=0):.4f}")
        print(f"\n  Confusion Matrix:")
        cm = confusion_matrix(y_true, y_pred)
        print(f"    TN={cm[0][0]}  FP={cm[0][1]}")
        print(f"    FN={cm[1][0]}  TP={cm[1][1]}")
        print(f"\n  Classification Report:\n")
        print(classification_report(y_true, y_pred, target_names=['Ham', 'Spam']))

    # ── Prediction ────────────────────────────

    def predict(self, text: str) -> dict:
        """
        Predict whether a single email is spam or ham.
        Returns a dict with label, confidence, and clean tokens.
        """
        if not self.is_trained:
            raise RuntimeError("Model is not trained yet. Call .train() first.")

        clean = preprocess_text(text)
        vec   = self.vectorizer.transform([clean])
        pred  = self.model.predict(vec)[0]

        # Confidence (probability) — SVM uses decision function
        if hasattr(self.model, 'predict_proba'):
            proba = self.model.predict_proba(vec)[0]
            confidence = proba[pred]
        else:
            score = self.model.decision_function(vec)[0]
            confidence = float(1 / (1 + np.exp(-abs(score))))  # sigmoid

        return {
            'label'     : 'SPAM' if pred == 1 else 'HAM',
            'is_spam'   : bool(pred),
            'confidence': round(confidence * 100, 2),
            'clean_text': clean,
        }

    def predict_batch(self, texts: list) -> list:
        """Predict a list of emails."""
        return [self.predict(t) for t in texts]

    # ── Persistence ───────────────────────────

    def save(self, path: str = 'spam_model.pkl'):
        with open(path, 'wb') as f:
            pickle.dump({'model': self.model, 'vectorizer': self.vectorizer,
                         'model_type': self.model_type}, f)
        print(f"  Model saved to '{path}'")

    @classmethod
    def load(cls, path: str = 'spam_model.pkl') -> 'SpamDetector':
        with open(path, 'rb') as f:
            data = pickle.load(f)
        detector = cls(model_type=data['model_type'])
        detector.model      = data['model']
        detector.vectorizer = data['vectorizer']
        detector.is_trained = True
        print(f"  Model loaded from '{path}'")
        return detector


# ─────────────────────────────────────────────
# 4. QUICK DEMO
# ─────────────────────────────────────────────

if __name__ == '__main__':
    # Load data (use sample data if no CSV found)
    dataset_path = 'SMSSpamCollection'
    if os.path.exists(dataset_path):
        print("Loading SMS Spam Collection dataset...")
        df = load_dataset(dataset_path)
    else:
        print("Dataset not found — using built-in sample data.")
        df = load_sample_data()

    print(f"Dataset size  : {len(df)} samples")
    print(f"Spam count    : {df['label_enc'].sum()}")
    print(f"Ham  count    : {(df['label_enc'] == 0).sum()}")

    # Train model
    detector = SpamDetector(model_type='naive_bayes')
    detector.train(df)
    detector.save('spam_model.pkl')

    # Test predictions
    test_emails = [
        "Congratulations! You've won a FREE iPhone. Click here to claim now!",
        "Hey, are we still meeting for lunch tomorrow at noon?",
        "URGENT: Your bank account has been compromised. Call 0800-XXX now.",
        "Can you please send me the report before end of day?",
        "You have been selected to receive a £500 prize! Reply YES to claim.",
    ]

    print(f"\n{'='*50}")
    print("  SAMPLE PREDICTIONS")
    print(f"{'='*50}")
    for email in test_emails:
        result = detector.predict(email)
        icon = "🚨" if result['is_spam'] else "✅"
        print(f"\n{icon} [{result['label']}] {result['confidence']}% confidence")
        print(f"   Email : {email[:70]}...")
