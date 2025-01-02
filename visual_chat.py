import streamlit as st

from session_state import set_session_state
from chat import chat_completion
from template import visual_default_prompt
from model_config import visual_model_list

def visualChat(api_key: str):
    set_session_state("visual", visual_default_prompt, 4096, 0.50)
    
    if st.session_state.visual_msg == []:
        disable = True
    elif st.session_state.visual_msg != []:
        disable = False
    
    with st.sidebar:
        clear_btn = st.button("Clear", "vi_clear", type="primary", use_container_width=True, disabled=disable)
        undo_btn = st.button("Undo", "vi_undo", use_container_width=True, disabled=disable)
        retry_btn = st.button("Retry", "vi_retry", use_container_width=True, disabled=disable)

        model_list = visual_model_list
        model = st.selectbox("Model", model_list, 0, key="vi_model", disabled=not disable)

        system_prompt = st.text_area("System Prompt", st.session_state.visual_sys, key="vi_sys", disabled=not disable)

        with st.expander("Advanced Setting"):
            tokens = st.slider("Max Tokens", 1, 4096, st.session_state.visual_tokens, 1, key="vi_tokens", disabled=not disable)
            temp = st.slider("Temperature", 0.00, 2.00, st.session_state.visual_temp, 0.01, key="vi_temp", disabled=not disable)
            topp = st.slider("Top P", 0.01, 1.00, st.session_state.visual_topp, 0.01, key="vi_topp", disabled=not disable)
            freq = st.slider("Frequency Penalty", -2.00, 2.00, st.session_state.visual_freq, 0.01, key="vi_freq", disabled=not disable)
            pres = st.slider("Presence Penalty", -2.00, 2.00, st.session_state.visual_pres, 0.01, key="vi_pres", disabled=not disable)
            if st.toggle("Set stop", key="vi_stop_toggle", disabled=not disable):
                st.session_state.general_stop = []
                stop_str = st.text_input("Stop", st.session_state.visual_stop_str, key="vi_stop_str", disabled=not disable)
                st.session_state.visual_stop_str = stop_str
                submit_stop = st.button("Submit", "vi_submit_stop", disabled=not disable)
                if submit_stop and stop_str:
                    st.session_state.visual_stop.append(st.session_state.visual_stop_str)
                    st.session_state.visual_stop_str = ""
                    st.rerun()
                if st.session_state.visual_stop:
                    for stop_str in st.session_state.visual_stop:
                        st.markdown(f"`{stop_str}`")

        st.session_state.visual_sys = system_prompt
        st.session_state.visual_tokens = tokens
        st.session_state.visual_temp = temp
        st.session_state.visual_topp = topp
        st.session_state.visual_freq = freq
        st.session_state.visual_pres = pres

    image_type = ["PNG", "JPG", "JPEG"]
    uploaded_image: list = st.file_uploader("Upload an image", type=image_type, accept_multiple_files=True, key="uploaded_image", disabled=not disable)
    base64_image_list = []
    if uploaded_image is not None:
        from process_image import image_processor
        with st.expander("Image"):
            for i in uploaded_image:
                st.image(uploaded_image, output_format="PNG")
                base64_image_list.append(image_processor(i))

    for i in st.session_state.visual_cache:
        with st.chat_message(i["role"]):
            st.markdown(i["content"])
    
    if query := st.chat_input("Say something...", key="vi_query", disabled=base64_image_list==[]):
        with st.chat_message("user"):
            st.markdown(query)
        
        st.session_state.visual_msg.append({"role": "user", "content": query})

        if len(st.session_state.visual_msg) == 1:
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": []}
            ]
            for base64_img in base64_image_list:
                img_url_obj = {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_img}", "detail": "high"}}
                messages[1]["content"].append(img_url_obj)
            messages[1]["content"].append({"type": "text", "text": query})
        elif len(st.session_state.visual_msg) > 1:
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": []}
            ]
            for base64_img in base64_image_list:
                img_url_obj = {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_img}", "detail": "high"}}
                messages[1]["content"].append(img_url_obj)
            messages[1]["content"].append({"type": "text", "text": st.session_state.visual_msg[0]["content"]})
            messages += st.session_state.visual_msg[1:]
        
        with st.chat_message("assistant"):
            try:
                response = chat_completion(api_key, model, messages, tokens, temp, freq, pres, st.session_state.visual_stop)
                result = st.write_stream(chunk.choices[0].delta.content for chunk in response if chunk.choices[0].delta.content is not None)
                st.session_state.general_msg.append({"role": "assistant", "content": result})
            except Exception as e:
                st.error(f"Error occured: {e}")
        
        st.session_state.visual_cache = st.session_state.visual_msg
        st.rerun()

    if clear_btn:
        st.session_state.visual_sys = visual_default_prompt
        st.session_state.visual_tokens = 4096
        st.session_state.visual_temp = 0.50
        st.session_state.visual_topp = 0.70
        st.session_state.visual_freq = 0.00
        st.session_state.visual_pres = 0.00
        st.session_state.visual_msg = []
        st.session_state.visual_cache = []
        st.session_state.visual_stop = None
        st.rerun()

    if undo_btn:
        del st.session_state.visual_msg[-1]
        del st.session_state.visual_cache[-1]
        st.rerun()

    if retry_btn:
        st.session_state.visual_msg.pop()
        st.session_state.visual_cache = []
        st.session_state.visual_retry = True
        st.rerun()
    if st.session_state.visual_retry:
        for i in st.session_state.visual_msg:
            with st.chat_message(i["role"]):
                st.markdown(i["content"])

        if len(st.session_state.visual_msg) == 1:
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": []}
            ]
            for base64_img in base64_image_list:
                img_url_obj = {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_img}", "detail": "high"}}
                messages[1]["content"].append(img_url_obj)
            messages[1]["content"].append({"type": "text", "text": st.session_state.visual_msg[0]["content"]})
        elif len(st.session_state.visual_msg) > 1:
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": []}
            ]
            for base64_img in base64_image_list:
                img_url_obj = {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_img}", "detail": "high"}}
                messages[1]["content"].append(img_url_obj)
            messages[1]["content"].append({"type": "text", "text": st.session_state.visual_msg[0]["content"]})
            messages += st.session_state.visual_msg[1:]
        
        with st.chat_message("assistant"):
            try:
                response = chat_completion(api_key, model, messages, tokens, temp, freq, pres, st.session_state.visual_stop)
                result = st.write_stream(chunk.choices[0].delta.content for chunk in response if chunk.choices[0].delta.content is not None)
                st.session_state.general_msg.append({"role": "assistant", "content": result})
            except Exception as e:
                st.error(f"Error occured: {e}")
        
        st.session_state.visual_cache = st.session_state.visual_msg
        st.session_state.visual_retry = False
        st.rerun()
