import streamlit as st

from session_state import set_session_state
from chat import chat_completion
from template import general_default_prompt
from model_config import text_model

def generalChat(api_key: str):
    set_session_state("general", general_default_prompt, 4096, 0.70)
    
    if st.session_state.general_msg == []:
        disable = True
    elif st.session_state.general_msg != []:
        disable = False
    
    with st.sidebar:
        clear_btn = st.button("Clear", "clear_", type="primary", use_container_width=True, disabled=disable)
        undo_btn = st.button("Undo", "undo_", use_container_width=True, disabled=disable)
        retry_btn = st.button("Retry", "retry_", use_container_width=True, disabled=disable)

        model_list = text_model(api_key)
        model = st.selectbox("Model", model_list, index=0, key="gen_model", disabled=not disable)

        system_prompt = st.text_area("System Prompt", st.session_state.general_sys, key="gen_sys", disabled=not disable)

        with st.expander("Advanced Setting"):
            tokens: int = st.slider("Max Tokens", 1, 4096, st.session_state.general_tokens, 1, key="gen_tokens", disabled=not disable)
            temp: float = st.slider("Temperature", 0.00, 2.00, st.session_state.general_temp, 0.01, key="gen_temp", disabled=not disable)
            topp: float = st.slider("Top P", 0.01, 1.00, st.session_state.general_topp, 0.01, key="gen_topp", disabled=not disable)
            freq: float = st.slider("Frequency Penalty", -2.00, 2.00, st.session_state.general_freq, 0.01, key="gen_freq", disabled=not disable)
            pres: float = st.slider("Presence Penalty", -2.00, 2.00, st.session_state.general_pres, 0.01, key="gen_pres", disabled=not disable)
            if st.toggle("Set stop", key="gen_stop_toggle", disabled=not disable):
                st.session_state.general_stop = []
                stop_str = st.text_input("Stop", st.session_state.general_stop_str, key="gen_stop_str", disabled=not disable)
                st.session_state.general_stop_str = stop_str
                submit_stop = st.button("Submit", "gen_submit_stop", disabled=not disable)
                if submit_stop and stop_str:
                    st.session_state.general_stop.append(st.session_state.general_stop_str)
                    st.session_state.general_stop_str = ""
                    st.rerun()
                if st.session_state.general_stop:
                    for stop_str in st.session_state.general_stop:
                        st.markdown(f"`{stop_str}`")
            
        st.session_state.general_sys = system_prompt
        st.session_state.general_tokens = tokens
        st.session_state.general_temp = temp
        st.session_state.general_topp = topp
        st.session_state.general_freq = freq
        st.session_state.general_pres = pres
    
    for i in st.session_state.general_cache:
        with st.chat_message(i["role"]):
            st.markdown(i["content"])

    if query := st.chat_input("Say something...", key="gen_query", disabled=model==""):
        with st.chat_message("user"):
            st.markdown(query)
        st.session_state.general_msg.append({"role": "user", "content": query})
        messages = [{"role": "system", "content": system_prompt}] + st.session_state.general_msg
        with st.chat_message("assistant"):
            try:
                response = chat_completion(api_key, model, messages, tokens, temp, topp, freq, pres, st.session_state.general_stop)
                result = st.write_stream(chunk.choices[0].delta.content for chunk in response if chunk.choices[0].delta.content is not None)
                st.session_state.general_msg.append({"role": "assistant", "content": result})
            except Exception as e:
                st.error(f"Error occured: {e}")
        st.session_state.general_cache = st.session_state.general_msg
        st.rerun()

    if clear_btn:
        st.session_state.general_sys = general_default_prompt
        st.session_state.general_tokens = 4096
        st.session_state.general_temp = 0.70
        st.session_state.general_topp = 0.70
        st.session_state.general_freq = 0.00
        st.session_state.general_pres = 0.00
        st.session_state.general_stop = None
        st.session_state.general_msg = []
        st.session_state.general_cache = []
        st.rerun()

    if undo_btn:
        del st.session_state.general_msg[-1]
        del st.session_state.general_cache[-1]
        st.rerun()

    if retry_btn:
        st.session_state.general_msg.pop()
        st.session_state.general_cache = []
        st.session_state.general_retry = True
        st.rerun()
    if st.session_state.general_retry:
        for i in st.session_state.general_msg:
            with st.chat_message(i["role"]):
                st.markdown(i["content"])
        messages = [{"role": "system", "content": system_prompt}] + st.session_state.general_msg
        with st.chat_message("assistant"):
            try:
                response = chat_completion(api_key, model, messages, tokens, temp, topp, freq, pres, st.session_state.general_stop)
                result = st.write_stream(chunk.choices[0].delta.content for chunk in response if chunk.choices[0].delta.content is not None)
                st.session_state.general_msg.append({"role": "assistant", "content": result})
            except Exception as e:
                st.error(f"Error occured: {e}")
        st.session_state.general_cache = st.session_state.general_msg
        st.session_state.general_retry = False
        st.rerun()
