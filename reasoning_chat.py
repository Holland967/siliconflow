import streamlit as st

from session_state import set_session_state
from chat import chat_completion
from template import qwen_reasoning_prompt, marco_reasoning_prompt
from model_config import reasoning_model_list

def reasoningChat(api_key: str):
    set_session_state("reasoning", "", 8192, 0.50)
    
    if st.session_state.reasoning_msg == []:
        disable = True
    elif st.session_state.reasoning_msg != []:
        disable = False
    
    with st.sidebar:
        clear_btn = st.button("Clear", "re_clear", type="primary", use_container_width=True, disabled=disable)
        undo_btn = st.button("Undo", "re_undo", use_container_width=True, disabled=disable)
        retry_btn = st.button("Retry", "re_retry", use_container_width=True, disabled=disable)

        model_list = reasoning_model_list
        model = st.selectbox("Model", model_list, 0, key="reason_model", disabled=not disable)
        st.session_state.reasoning_model = model

        if model == "AIDC-AI/Marco-o1":
            st.session_state.reasoning_sys = marco_reasoning_prompt
        else:
            st.session_state.reasoning_sys = qwen_reasoning_prompt
        
        with st.expander("Advanced Setting"):
            tokens = st.slider("Max Tokens", 1, 8192, st.session_state.reasoning_tokens, 1, key="re_tokens", disabled=not disable)
            temp = st.slider("Temperature", 0.00, 2.00, st.session_state.reasoning_temp, 0.01, key="re_temp", disabled=not disable)
            topp = st.slider("Top P", 0.01, 1.00, st.session_state.reasoning_topp, 0.01, key="re_topp", disabled=not disable)
            freq = st.slider("Frequency Penalty", -2.00, 2.00, st.session_state.reasoning_freq, 0.01, key="re_freq", disabled=not disable)
            pres = st.slider("Presence Penalty", -2.00, 2.00, st.session_state.reasoning_pres, 0.01, key="re_pres", disabled=not disable)
            if st.toggle("Set stop", key="re_stop_toggle", disabled=not disable):
                st.session_state.reasoning_stop = []
                stop_str = st.text_input("Stop", st.session_state.reasoning_stop_str, key="re_stop_str", disabled=not disable)
                st.session_state.visual_stop_str = stop_str
                submit_stop = st.button("Submit", "re_submit_stop", disabled=not disable)
                if submit_stop and stop_str:
                    st.session_state.reasoning_stop.append(st.session_state.reasoning_stop_str)
                    st.session_state.reasoning_stop_str = ""
                    st.rerun()
                if st.session_state.reasoning_stop:
                    for stop_str in st.session_state.reasoning_stop:
                        st.markdown(f"`{stop_str}`")
        
        st.session_state.reasoning_tokens = tokens
        st.session_state.reasoning_temp = temp
        st.session_state.reasoning_topp = topp
        st.session_state.reasoning_freq = freq
        st.session_state.reasoning_pres = pres

    if st.session_state.reasoning_model == "Qwen/QVQ-72B-Preview":
        from process_image import image_processor
        image_type = ["PNG", "JPG", "JPEG"]
        uploaded_image: list = st.file_uploader("Upload an image", type=image_type, accept_multiple_files=True, key="re_uploaded_image")
        base64_image_list = []
        if uploaded_image is not None:
            with st.expander("Image"):
                for i in uploaded_image:
                    st.image(uploaded_image, output_format="PNG")
                    base64_image_list.append(image_processor(i))
        
        for i in st.session_state.reasoning_cache:
            with st.chat_message(i["role"]):
                st.markdown(i["content"])
        
        if query := st.chat_input("Say something...", key="re_qvq_query", disabled=base64_image_list==[]):
            with st.chat_message("user"):
                st.markdown(query)
            
            st.session_state.reasoning_msg.append({"role": "user", "content": query})

            if len(st.session_state.reasoning_msg) == 1:
                messages = [
                    {"role": "system", "content": st.session_state.reasoning_sys},
                    {"role": "user", "content": []}
                ]
                for base64_img in base64_image_list:
                    img_url_obj = {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_img}", "detail": "high"}}
                    messages[1]["content"].append(img_url_obj)
                messages[1]["content"].append({"type": "text", "text": query})
            elif len(st.session_state.reasoning_msg) > 1:
                messages = [
                    {"role": "system", "content": st.session_state.reasoning_sys},
                    {"role": "user", "content": []}
                ]
                for base64_img in base64_image_list:
                    img_url_obj = {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_img}", "detail": "high"}}
                    messages[1]["content"].append(img_url_obj)
                messages[1]["content"].append({"type": "text", "text": st.session_state.reasoning_msg[0]["content"]})
                messages += st.session_state.reasoning_msg[1:]
            
            with st.chat_message("assistant"):
                try:
                    response = chat_completion(api_key, model, messages, tokens, temp, topp, freq, pres, st.session_state.reasoning_stop)
                    result = st.write_stream(chunk.choices[0].delta.content for chunk in response if chunk.choices[0].delta.content is not None)
                    st.session_state.reasoning_msg.append({"role": "assistant", "content": result})
                except Exception as e:
                    st.error(f"Error occured: {e}")
            
            st.session_state.reasoning_cache = st.session_state.reasoning_msg
            st.rerun()

        if retry_btn:
            st.session_state.reasoning_msg.pop()
            st.session_state.reasoning_cache = []
            st.session_state.reasoning_retry = True
            st.rerun()
        if st.session_state.reasoning_retry:
            for i in st.session_state.reasoning_msg:
                with st.chat_message(i["role"]):
                    st.markdown(i["content"])
            if len(st.session_state.reasoning_msg) == 1:
                messages = [
                    {"role": "system", "content": st.session_state.reasoning_sys},
                    {"role": "user", "content": []}
                ]
                for base64_img in base64_image_list:
                    img_url_obj = {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_img}", "detail": "high"}}
                    messages[1]["content"].append(img_url_obj)
                messages[1]["content"].append({"type": "text", "text": st.session_state.reasoning_msg[0]["content"]})
            elif len(st.session_state.reasoning_msg) > 1:
                messages = [
                    {"role": "system", "content": st.session_state.reasoning_sys},
                    {"role": "user", "content": []}
                ]
                for base64_img in base64_image_list:
                    img_url_obj = {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_img}", "detail": "high"}}
                    messages[1]["content"].append(img_url_obj)
                messages[1]["content"].append({"type": "text", "text": st.session_state.reasoning_msg[0]["content"]})
                messages += st.session_state.reasoning_msg[1:]
            
            with st.chat_message("assistant"):
                try:
                    response = chat_completion(api_key, model, messages, tokens, temp, topp, freq, pres, st.session_state.reasoning_stop)
                    result = st.write_stream(chunk.choices[0].delta.content for chunk in response if chunk.choices[0].delta.content is not None)
                    st.session_state.reasoning_msg.append({"role": "assistant", "content": result})
                except Exception as e:
                    st.error(f"Error occured: {e}")
            
            st.session_state.reasoning_cache = st.session_state.reasoning_msg
            st.session_state.reasoning_retry = False
            st.rerun()
    else:
        for i in st.session_state.reasoning_cache:
            with st.chat_message(i["role"]):
                st.markdown(i["content"])
        
        if query := st.chat_input("Say something...", key="re_query", disabled=model==""):
            with st.chat_message("user"):
                st.markdown(query)
            
            st.session_state.reasoning_msg.append({"role": "user", "content": query})

            messages = [{"role": "system", "content": st.session_state.reasoning_sys}] + st.session_state.reasoning_msg

            with st.chat_message("assistant"):
                try:
                    response = chat_completion(api_key, model, messages, tokens, temp, topp, freq, pres, st.session_state.reasoning_stop)
                    result = st.write_stream(chunk.choices[0].delta.content for chunk in response if chunk.choices[0].delta.content is not None)
                    st.session_state.reasoning_msg.append({"role": "assistant", "content": result})
                except Exception as e:
                    st.error(f"Error occured: {e}")
            
            st.session_state.reasoning_cache = st.session_state.reasoning_msg
            st.rerun()

        if retry_btn:
            st.session_state.reasoning_msg.pop()
            st.session_state.reasoning_cache = []
            st.session_state.reasoning_retry = True
            st.rerun()
        if st.session_state.reasoning_retry:
            for i in st.session_state.reasoning_msg:
                with st.chat_message(i["role"]):
                    st.markdown(i["content"])
            
            messages = [{"role": "system", "content": st.session_state.reasoning_sys}] + st.session_state.reasoning_msg

            with st.chat_message("assistant"):
                try:
                    response = chat_completion(api_key, model, messages, tokens, temp, topp, freq, pres, st.session_state.reasoning_stop)
                    result = st.write_stream(chunk.choices[0].delta.content for chunk in response if chunk.choices[0].delta.content is not None)
                    st.session_state.reasoning_msg.append({"role": "assistant", "content": result})
                except Exception as e:
                    st.error(f"Error occured: {e}")
            
            st.session_state.reasoning_cache = st.session_state.reasoning_msg
            st.session_state.reasoning_retry = False
            st.rerun()

    if clear_btn:
        st.session_state.reasoning_tokens = 8192
        st.session_state.reasoning_temp = 0.50
        st.session_state.reasoning_topp = 0.70
        st.session_state.reasoning_freq = 0.00
        st.session_state.reasoning_pres = 0.00
        st.session_state.reasoning_msg = []
        st.session_state.reasoning_cache = []
        st.session_state.reasoning_stop = None
        st.rerun()

    if undo_btn:
        del st.session_state.reasoning_msg[-1]
        del st.session_state.reasoning_cache[-1]
        st.rerun()
