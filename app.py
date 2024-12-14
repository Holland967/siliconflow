import streamlit as st
import os

from text_chat import text_chatting
from vision_chat import vision_chatting
from reasoning_chat import reasoning_chatting
from image_generation import image_generator

api_key: str = ""

with st.sidebar:
    api_key_input: str = st.text_input("API KEY", "", key="api_key", type="password")
    if api_key_input == "":
        password: str = st.text_input("Password", "", key="password", type="password")
        if password == os.environ.get("PASSWORD"):
            api_key: str = os.environ.get("API_KEY")
    elif api_key_input != "":
        api_key: str = api_key_input

base_url: str = "https://api.siliconflow.cn/v1"

def main() -> None:
    function_list: list = ["Text Chat", "Vision Chat", "Reasoning Chat", "Image Generation"]
    function_selector: str = st.sidebar.selectbox("Function", function_list, 0, key="func_", disabled=not api_key)

    if function_selector == "Text Chat":
        text_chatting(api_key=api_key, base_url=base_url)
    elif function_selector == "Vision Chat":
        vision_chatting(api_key=api_key, base_url=base_url)
    elif function_selector == "Reasoning Chat":
        reasoning_chatting(api_key=api_key, base_url=base_url)
    elif function_selector == "Image Generation":
        image_generator(api_key=api_key)

if __name__ == "__main__":
    main()
