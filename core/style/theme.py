import streamlit as st

def load_theme():
    st.markdown("""
        <style>
        .main { background-color: #0e1117; }
        .main-title { color: #00ffcc; font-family: 'Courier New', monospace; font-weight: bold; }
        .ready-status { color: #00ff00; font-size: 0.8rem; font-family: monospace; border: 1px solid #00ff00; padding: 2px 8px; border-radius: 15px; width: fit-content; }
        div[data-testid="stSidebar"] { background-color: #161b22; border-right: 1px solid #30363d; }
        .stButton>button { background-color: #21262d; border: 1px solid #30363d; color: #c9d1d9; transition: 0.3s; }
        .stButton>button:hover { border-color: #00ffcc; color: #00ffcc; }
        </style>
    """, unsafe_allow_html=True)