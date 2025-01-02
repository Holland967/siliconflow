import streamlit as st

def set_session_state(mode: str, sys: str, tokens: int, temp: float):
    if f"{mode}_sys" not in st.session_state:
        st.session_state[f"{mode}_sys"] = sys
    if f"{mode}_msg" not in st.session_state:
        st.session_state[f"{mode}_msg"] = []
    if f"{mode}_cache" not in st.session_state:
        st.session_state[f"{mode}_cache"] = []
    if f"{mode}_tokens" not in st.session_state:
        st.session_state[f"{mode}_tokens"] = tokens
    if f"{mode}_temp" not in st.session_state:
        st.session_state[f"{mode}_temp"] = temp
    if f"{mode}_topp" not in st.session_state:
        st.session_state[f"{mode}_topp"] = 0.70
    if f"{mode}_freq" not in st.session_state:
        st.session_state[f"{mode}_freq"] = 0.00
    if f"{mode}_pres" not in st.session_state:
        st.session_state[f"{mode}_pres"] = 0.00
    if f"{mode}_stop" not in st.session_state:
        st.session_state[f"{mode}_stop"] = None
    if f"{mode}_stop_str" not in st.session_state:
        st.session_state[f"{mode}_stop_str"] = ""
    if f"{mode}_retry" not in st.session_state:
        st.session_state[f"{mode}_retry"] = False
