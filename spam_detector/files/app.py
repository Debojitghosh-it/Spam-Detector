"""
Streamlit Web App — Spam Email Detector
Run with:  streamlit run app.py
"""

import streamlit as st
import pandas as pd
import os
from spam_detector import SpamDetector, load_dataset, load_sample_data

# ─────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Spam Detector",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
# CUSTOM CSS
# ─────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=DM+Sans:wght@300;400;600&display=swap');

    html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }
    h1, h2, h3 { font-family: 'Space Mono', monospace; }

    .spam-badge {
        background: linear-gradient(135deg, #FF4B4B, #FF0000);
        color: white; padding: 12px 24px; border-radius: 8px;
        font-size: 1.5rem; font-weight: bold; text-align: center;
        box-shadow: 0 4px 15px rgba(255,75,75,0.4);
    }
    .ham-badge {
        background: linear-gradient(135deg, #00C851, #007E33);
        color: white; padding: 12px 24px; border-radius: 8px;
        font-size: 1.5rem; font-weight: bold; text-align: center;
        box-shadow: 0 4px 15px rgba(0,200,81,0.4);
    }
    .metric-card {
        background: #1e1e2e; color: white; border-radius: 10px;
        padding: 15px; text-align: center; border: 1px solid #333;
    }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# SESSION STATE — load / train model once
# ─────────────────────────────────────────────
@st.cache_resource
def get_model(model_type: str):
    model_path = f'spam_model_{model_type}.pkl'
    detector   = SpamDetector(model_type=model_type)

    dataset_path = 'SMSSpamCollection'
    df = load_dataset(dataset_path) if os.path.exists(dataset_path) else load_sample_data()

    detector.train(df)
    detector.save(model_path)
    return detector, len(df)


# ─────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────
with st.sidebar:
    st.title("⚙️ Settings")
    st.markdown("---")

    model_type = st.selectbox(
        "ML Algorithm",
        options=['naive_bayes', 'logistic_regression', 'svm'],
        format_func=lambda x: {
            'naive_bayes'         : '🧮 Naive Bayes',
            'logistic_regression' : '📈 Logistic Regression',
            'svm'                 : '⚡ Support Vector Machine',
        }[x]
    )

    st.markdown("---")
    st.markdown("### 📚 About")
    st.markdown("""
    This app uses **TF-IDF** vectorization + classical
    ML to classify emails as **Spam** or **Ham**.

    **Steps:**
    1. Text cleaning & stemming
    2. TF-IDF feature extraction
    3. ML model classification
    """)

    st.markdown("---")
    st.markdown("### 📦 Dataset")
    st.markdown("""
    Place the `SMSSpamCollection` file (from the
    [UCI Repository](https://archive.ics.uci.edu/dataset/228/sms+spam+collection))
    in the same folder for full training.
    Otherwise, built-in sample data is used.
    """)


# ─────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────
st.title("🛡️ Spam Email Detector")
st.caption("Powered by TF-IDF + Machine Learning")
st.markdown("---")

# Load model
with st.spinner("Training model..."):
    detector, dataset_size = get_model(model_type)

st.success(f"✅ Model ready! Trained on {dataset_size} samples using {model_type.replace('_', ' ').title()}.")

# ─────────────────────────────────────────────
# TABS
# ─────────────────────────────────────────────
tab1, tab2, tab3 = st.tabs(["🔍 Single Email", "📋 Batch Check", "📊 Examples"])

# ── TAB 1 : Single Email ──────────────────────
with tab1:
    st.subheader("Check a Single Email")
    email_text = st.text_area(
        "Paste your email content here:",
        height=200,
        placeholder="Type or paste email text here...",
    )

    col1, col2 = st.columns([1, 3])
    with col1:
        check_btn = st.button("🔍 Analyse Email", use_container_width=True)

    if check_btn and email_text.strip():
        with st.spinner("Analysing..."):
            result = detector.predict(email_text)

        st.markdown("---")
        col_a, col_b, col_c = st.columns(3)

        badge_html = (
            f'<div class="spam-badge">🚨 SPAM DETECTED</div>'
            if result['is_spam'] else
            f'<div class="ham-badge">✅ SAFE — NOT SPAM</div>'
        )
        with col_a:
            st.markdown(badge_html, unsafe_allow_html=True)
        with col_b:
            st.metric("Confidence", f"{result['confidence']}%")
        with col_c:
            st.metric("Model", model_type.replace('_', ' ').title())

        with st.expander("🔬 Processed Text (after cleaning)"):
            st.code(result['clean_text'])

    elif check_btn:
        st.warning("Please enter some email text first.")


# ── TAB 2 : Batch ─────────────────────────────
with tab2:
    st.subheader("Batch Email Analysis")
    st.markdown("Enter one email per line:")

    batch_input = st.text_area(
        "Emails (one per line):",
        height=250,
        placeholder="Email 1...\nEmail 2...\nEmail 3...",
    )

    if st.button("🚀 Analyse All", use_container_width=True):
        emails = [e.strip() for e in batch_input.strip().split('\n') if e.strip()]
        if emails:
            with st.spinner(f"Analysing {len(emails)} emails..."):
                results = detector.predict_batch(emails)

            rows = []
            for email, res in zip(emails, results):
                rows.append({
                    'Email'     : email[:80] + ('...' if len(email) > 80 else ''),
                    'Label'     : res['label'],
                    'Confidence': f"{res['confidence']}%",
                })

            df_results = pd.DataFrame(rows)

            spam_count = sum(1 for r in results if r['is_spam'])
            ham_count  = len(results) - spam_count

            col1, col2, col3 = st.columns(3)
            col1.metric("Total Emails", len(results))
            col2.metric("🚨 Spam", spam_count)
            col3.metric("✅ Ham",  ham_count)

            st.dataframe(
                df_results.style.apply(
                    lambda row: ['background-color: #ffcccc' if row['Label'] == 'SPAM'
                                 else 'background-color: #ccffcc'] * len(row),
                    axis=1
                ),
                use_container_width=True,
            )
        else:
            st.warning("Please enter at least one email.")


# ── TAB 3 : Examples ──────────────────────────
with tab3:
    st.subheader("Try These Examples")

    examples = {
        "🚨 Spam 1 — Prize Winner"  : "WINNER!! You have been selected to receive a £900 prize reward! Call 09061701461 to claim.",
        "🚨 Spam 2 — Phishing"      : "URGENT: Your account has been compromised. Click here immediately to verify your details and avoid suspension.",
        "🚨 Spam 3 — Offer"         : "Congratulations! You've won a FREE iPhone 15. Complete a short survey to claim your prize now!",
        "✅ Ham 1 — Casual"         : "Hey! Are we still on for lunch tomorrow at 1pm? Let me know if you need to reschedule.",
        "✅ Ham 2 — Work"           : "Please review the attached project report and share your feedback by end of business today.",
        "✅ Ham 3 — Personal"       : "Happy birthday! Hope you have a wonderful day filled with joy and celebration.",
    }

    selected = st.selectbox("Choose an example:", list(examples.keys()))

    st.text_area("Email content:", value=examples[selected], height=120, key="example_text")

    if st.button("🔍 Check This Example"):
        result = detector.predict(examples[selected])
        badge_html = (
            f'<div class="spam-badge">🚨 SPAM DETECTED — {result["confidence"]}% confident</div>'
            if result['is_spam'] else
            f'<div class="ham-badge">✅ HAM (Safe) — {result["confidence"]}% confident</div>'
        )
        st.markdown(badge_html, unsafe_allow_html=True)
