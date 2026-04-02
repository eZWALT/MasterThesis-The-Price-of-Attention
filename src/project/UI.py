import streamlit as st
import requests

API_URL = "http://localhost:8000/v1/completions"

st.title("vLLM Chatbot")

prompt = st.text_area("Enter your prompt:")

if st.button("Generate"):
    payload = {
        "model": "Qwen/Qwen3.5-9B",
        "prompt": prompt,
        "max_tokens": 256,
        "temperature": 0.7,
    }
    response = requests.post(API_URL, json=payload)
    if response.ok:
        result = response.json()
        st.write(result["choices"][0]["text"])
    else:
        st.error(f"Error: {response.text}")