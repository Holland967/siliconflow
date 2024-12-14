import streamlit as st

from session_state import set_session_state
from component import set_component

def reasoning_chatting(api_key: str, base_url: str) -> None:
    from model_config import reasoning_chat_model_list
    from chat_completion import ChatCompletion
    from template import qwq_reasoning_prompt, marco_reasoning_prompt

    mode: str = "reasoning_chat"
    model_list: list = reasoning_chat_model_list

    chat = ChatCompletion(api_key=api_key, base_url=base_url)

    set_session_state(
        mode=mode,
        prompt="",
        tokens=8192,
        temp=0.70)
    
    clear_btn, undo_btn, retry_btn, model, system_prompt, max_tokens, \
        temperature, top_p, frequency_penalty, presence_penalty = set_component(
            mode=mode,
            disable_1=st.session_state[f"{mode}_msg"]==[],
            disable_2=st.session_state[f"{mode}_msg"]!=[],
            model_list=model_list,
            prompt=st.session_state[f"{mode}_sys"],
            max_token_limit=8192,
            tokens=st.session_state[f"{mode}_tokens"],
            temp=st.session_state[f"{mode}_temp"],
            topp=st.session_state[f"{mode}_topp"],
            freq=st.session_state[f"{mode}_freq"],
            pres=st.session_state[f"{mode}_pres"])
    
    st.session_state[f"{mode}_sys"] = system_prompt
    st.session_state[f"{mode}_tokens"] = max_tokens
    st.session_state[f"{mode}_temp"] = temperature
    st.session_state[f"{mode}_topp"] = top_p
    st.session_state[f"{mode}_freq"] = frequency_penalty
    st.session_state[f"{mode}_pres"] = presence_penalty

    for i in st.session_state[f"{mode}_cache"]:
        with st.chat_message(i["role"]):
            st.markdown(i["content"])
    
    if query := st.chat_input("Say something...", key=f"{mode}_query"):
        st.session_state[f"{mode}_msg"].append({"role": "user", "content": query})
        with st.chat_message("user"):
            st.markdown(query)
        
        messages: list = [{"role": "system", "content": system_prompt}] + st.session_state[f"{mode}_msg"]

        with st.chat_message("assistant"):
            response = chat.chat_completions(model, messages, max_tokens, temperature, top_p, frequency_penalty, presence_penalty)
            result: str = st.write_stream(chunk.choices[0].delta.content for chunk in response if chunk.choices[0].delta.content is not None)
        
        st.session_state[f"{mode}_msg"].append({"role": "assistant", "content": result})
        st.session_state[f"{mode}_cache"] = st.session_state[f"{mode}_msg"]
        st.rerun()
    
    if clear_btn:
        if model == "Qwen/QwQ-32B-Preview":
            st.session_state[f"{mode}_sys"] = qwq_reasoning_prompt
        elif model == "AIDC-AI/Marco-o1":
            st.session_state[f"{mode}_sys"] = marco_reasoning_prompt
        st.session_state[f"{mode}_msg"] = []
        st.session_state[f"{mode}_cache"] = []
        st.session_state[f"{mode}_tokens"] = 8192
        st.session_state[f"{mode}_temp"] = 0.70
        st.session_state[f"{mode}_topp"] = 0.90
        st.session_state[f"{mode}_freq"] = 0.00
        st.session_state[f"{mode}_pres"] = 0.00
        st.rerun()
    
    if undo_btn:
        del st.session_state[f"{mode}_msg"][-1]
        del st.session_state[f"{mode}_cache"][-1]
        st.rerun()
    
    if retry_btn:
        st.session_state[f"{mode}_msg"].pop()
        st.session_state[f"{mode}_cache"] = []
        st.session_state[f"{mode}_retry"] = True
        st.rerun()
    if st.session_state[f"{mode}_retry"]:
        for i in st.session_state[f"{mode}_msg"]:
            with st.chat_message(i["role"]):
                st.markdown(i["content"])

        messages: list = [{"role": "system", "content": system_prompt}] + st.session_state[f"{mode}_msg"]

        with st.chat_message("assistant"):
            response = chat.chat_completions(model, messages, max_tokens, temperature, top_p, frequency_penalty, presence_penalty)
            result: str = st.write_stream(chunk.choices[0].delta.content for chunk in response if chunk.choices[0].delta.content is not None)
        
        st.session_state[f"{mode}_msg"].append({"role": "assistant", "content": result})
        st.session_state[f"{mode}_cache"] = st.session_state[f"{mode}_msg"]

        st.session_state[f"{mode}_retry"] = False
        st.rerun()
