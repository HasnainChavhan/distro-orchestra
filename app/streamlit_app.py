import streamlit as st
import requests
import pandas as pd
import os

API_URL = os.getenv("API_URL", "http://localhost:8000")

st.set_page_config(page_title="Distro Orchestra Sentiment", page_icon="🎭", layout="wide")

st.title("🎭 Distro Orchestra Sentiment Analysis")
st.markdown("Real-time NLP sentiment analysis using HuggingFace BERT & FastAPI.")

st.sidebar.header("Model Info")
st.sidebar.text("Model: Twitter-RoBERTa / DistilBERT")
st.sidebar.text("API Status: " + ("Running" if requests.get(f"{API_URL}/health").status_code == 200 else "Unavailable") )

tab1, tab2 = st.tabs(["Single Text", "Batch (CSV)"])

with tab1:
    text_input = st.text_area("Enter text to analyze:", "I absolutely love this product!")
    if st.button("Analyze", type="primary"):
        with st.spinner("Analyzing..."):
            try:
                res = requests.post(f"{API_URL}/analyze", json={"text": text_input}).json()
                sentiment = res.get("sentiment", "UNKNOWN")
                conf = res.get("confidence", 0) * 100
                
                color = "gray"
                if sentiment == "POSITIVE": color = "green"
                elif sentiment == "NEGATIVE": color = "red"
                
                st.markdown(f"### Result: <span style='color:{color}'>{sentiment}</span> ({conf:.1f}%)", unsafe_allow_html=True)
                
                probs = res.get("probabilities", {})
                st.bar_chart(pd.DataFrame.from_dict(probs, orient='index', columns=['Probability']))
                st.caption(f"Processing time: {res.get('processing_time', 0):.4f}s")
            except Exception as e:
                st.error(f"Error connecting to API: {e}")

with tab2:
    uploaded_file = st.file_uploader("Upload CSV with 'text' column", type=['csv'])
    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file)
        if 'text' in df.columns:
            if st.button("Analyze Batch"):
                with st.spinner("Analyzing batch..."):
                    texts = df['text'].tolist()
                    try:
                        res = requests.post(f"{API_URL}/analyze/batch", json={"texts": texts}).json()
                        results = res.get("results", [])
                        
                        out_df = pd.DataFrame([{
                            "text": r["text"],
                            "sentiment": r["sentiment"],
                            "confidence": f"{r['confidence']*100:.1f}%"
                        } for r in results])
                        st.dataframe(out_df, use_container_width=True)
                        st.success(f"Processed {res.get('total')} items in {res.get('processing_time', 0):.2f}s")
                    except Exception as e:
                        st.error(f"Error: {e}")
        else:
            st.error("CSV must contain a 'text' column.")
