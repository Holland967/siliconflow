import streamlit as st

def set_component(
    mode: str,
    disable_1: bool=False,
    disable_2: bool=False,
    model_list: list=[],
    prompt: str="",
    max_token_limit: int=4096,
    tokens: int=4096,
    temp: float=0.70,
    topp: float=0.90,
    freq: float=0.00,
    pres: float=0.00):
    from template import qwq_reasoning_prompt, marco_reasoning_prompt

    clear_btn: bool = st.sidebar.button("Clear", f"{mode}_clear", type="primary", use_container_width=True, disabled=disable_1)
    undo_btn: bool = st.sidebar.button("Undo", f"{mode}_undo", use_container_width=True, disabled=disable_1)
    retry_btn: bool = st.sidebar.button("Retry", f"{mode}_retry_btn", use_container_width=True, disabled=disable_1)
    model: str = st.sidebar.selectbox("Model", model_list, 0, key=f"{mode}_model", disabled=disable_2)
    if model == "Qwen/QwQ-32B-Preview":
        prompt = qwq_reasoning_prompt
    elif model == "AIDC-AI/Marco-o1":
        prompt = marco_reasoning_prompt
    else:
        prompt = prompt
    system_prompt: str = st.sidebar.text_area("System Prompt", prompt, key=f"{mode}_system_prompt", disabled=disable_2)
    max_tokens: int = st.sidebar.slider("Max Tokens", 1, max_token_limit, tokens, 1, key=f"{mode}_max_tokens", disabled=disable_2)
    temperature: float = st.sidebar.slider("Temperature", 0.00, 2.00, temp, 0.01, key=f"{mode}_temperature", disabled=disable_2)
    top_p: float = st.sidebar.slider("Top P", 0.01, 1.00, topp, 0.01, key=f"{mode}_top_p", disabled=disable_2)
    frequency_penalty: float = st.sidebar.slider("Frequency Penalty", -2.00, 2.00, freq, 0.01, key=f"{mode}_frequency_penalty", disabled=disable_2)
    presence_penalty: float = st.sidebar.slider("Presence Penalty", -2.00, 2.00, pres, 0.01, key=f"{mode}_presence_penalty", disabled=disable_2)
    
    return clear_btn, undo_btn, retry_btn, model, system_prompt, max_tokens, temperature, top_p, frequency_penalty, presence_penalty
