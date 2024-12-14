import streamlit as st

from session_state import set_session_state
from component import set_component

def vision_chatting(api_key: str, base_url: str) -> None:
    from model_config import vision_chat_model_list
    from chat_completion import ChatCompletion
    from template import vision_chat_default_prompt
    from image_processor import process_image
    from vision_messages import vision_msg

    mode: str = "vision_chat"
    model_list: list = vision_chat_model_list

    chat = ChatCompletion(api_key=api_key, base_url=base_url)

    set_session_state(
        mode=mode,
        prompt=vision_chat_default_prompt,
        tokens=4096,
        temp=0.20)
    
    if "imgs" not in st.session_state:
        st.session_state.imgs = []
    
    if "base64_image" not in st.session_state:
        st.session_state.base64_image = []
    
    clear_btn, undo_btn, retry_btn, model, system_prompt, max_tokens, \
        temperature, top_p, frequency_penalty, presence_penalty = set_component(
            mode=mode,
            disable_1=st.session_state[f"{mode}_msg"]==[],
            disable_2=st.session_state[f"{mode}_msg"]!=[],
            model_list=model_list,
            prompt=st.session_state[f"{mode}_sys"],
            max_token_limit=4096,
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

    img_type: list = ["PNG", "JPG", "JPEG"]
    uploaded_images = st.file_uploader("Upload an image", type=img_type, accept_multiple_files=True, key="image_uploader")
    if uploaded_images == []:
        image_url: str = st.text_input("Image Url", "", key="image_url")
    
    if st.button("Submit", "submit", type="primary", disabled=st.session_state[f"{mode}_msg"]!=[]):
        st.session_state.imgs = []
        st.session_state.base64_image = []
        if uploaded_images != []:
            for uploaded_image in uploaded_images:
                st.session_state.imgs.append(uploaded_image)
                st.session_state.base64_image.append(process_image(uploaded_image))
        elif uploaded_images == []:
            if image_url != "":
                st.session_state.imgs.append(image_url)

                import requests
                from io import BytesIO

                response = requests.get(image_url, stream=True)
                if response.status_code == 200:
                    image_file = BytesIO(response.content)
                st.session_state.base64_image.append(process_image(image_file))
        st.rerun()
    
    with st.expander("Image", False):
        for img in st.session_state.imgs:
            st.image(img, output_format="PNG")
    
    for i in st.session_state[f"{mode}_cache"]:
        with st.chat_message(i["role"]):
            st.markdown(i["content"])
    
    if query := st.chat_input("Say something", key=f"{mode}_query", disabled=not uploaded_images!=[] and not image_url!=""):
        st.session_state[f"{mode}_msg"].append({"role": "user", "content": query})
        with st.chat_message("user"):
            st.markdown(query)

        user_msg: dict = vision_msg(st.session_state.base64_image, st.session_state[f"{mode}_msg"][0]["content"])
        if len(st.session_state[f"{mode}_msg"]) == 1:
            messages: list = [{"role": "system", "content": system_prompt}, user_msg]
        elif len(st.session_state[f"{mode}_msg"]) > 1:
            messages: list = [{"role": "system", "content": system_prompt}, user_msg] + st.session_state[f"{mode}_msg"][1:]
        
        with st.chat_message("assistant"):
            response = chat.chat_completions(model, messages, max_tokens, temperature, top_p, frequency_penalty, presence_penalty)
            result: str = st.write_stream(chunk.choices[0].delta.content for chunk in response if chunk.choices[0].delta.content is not None)
        
        st.session_state[f"{mode}_msg"].append({"role": "assistant", "content": result})
        st.session_state[f"{mode}_cache"] = st.session_state[f"{mode}_msg"]
        st.rerun()

    if clear_btn:
        st.session_state[f"{mode}_sys"] = vision_chat_default_prompt
        st.session_state[f"{mode}_msg"] = []
        st.session_state[f"{mode}_cache"] = []
        st.session_state[f"{mode}_tokens"] = 4096
        st.session_state[f"{mode}_temp"] = 0.20
        st.session_state[f"{mode}_topp"] = 0.90
        st.session_state[f"{mode}_freq"] = 0.00
        st.session_state[f"{mode}_pres"] = 0.00
        st.session_state.imgs = []
        st.session_state.base64_image = []
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

        user_msg: dict = vision_msg(st.session_state.base64_image, st.session_state[f"{mode}_msg"][0]["content"])
        if len(st.session_state[f"{mode}_msg"]) == 1:
            messages: list = [{"role": "system", "content": system_prompt}, user_msg]
        elif len(st.session_state[f"{mode}_msg"]) > 1:
            messages: list = [{"role": "system", "content": system_prompt}, user_msg] + st.session_state[f"{mode}_msg"][1:]
        
        with st.chat_message("assistant"):
            response = chat.chat_completions(model, messages, max_tokens, temperature, top_p, frequency_penalty, presence_penalty)
            result: str = st.write_stream(chunk.choices[0].delta.content for chunk in response if chunk.choices[0].delta.content is not None)
        
        st.session_state[f"{mode}_msg"].append({"role": "assistant", "content": result})
        st.session_state[f"{mode}_cache"] = st.session_state[f"{mode}_msg"]

        st.session_state[f"{mode}_retry"] = False
        st.rerun()
