import streamlit as st
import requests

def image_generator(api_key: str) -> None:
    from model_config import image_model_list

    url = "https://api.siliconflow.cn/v1/images/generations"

    def flux_image(
        model: str,
        prompt: str,
        image_size: str,
        num_inference_steps: int=35,
        prompt_enhancement: bool=False) -> str:
        payload: dict = {
            "model": model,
            "prompt": prompt,
            "image_size": image_size,
            "num_inference_steps": num_inference_steps,
            "prompt_enhancement": prompt_enhancement}
        headers: dict = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"}
        response = requests.request("POST", url, json=payload, headers=headers)
        if response.status_code == 200:
            response_object: dict = response.json()
            image_data: list = response_object["images"]
            image_url: str = image_data[0]["url"]
        return image_url

    def sd_image(
        model: str,
        prompt: str,
        negative_prompt: str,
        image_size: str,
        num_inference_steps: int=35,
        guidance_scale: float=4.5,
        prompt_enhancement: bool=False) -> str:
        payload = {
            "model": model,
            "prompt": prompt,
            "negative_prompt": negative_prompt,
            "image_size": image_size,
            "batch_size": 1,
            "num_inference_steps": num_inference_steps,
            "guidance_scale": guidance_scale,
            "prompt_enhancement": prompt_enhancement}
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"}
        response = requests.request("POST", url, json=payload, headers=headers)
        if response.status_code == 200:
            response_object: dict = response.json()
            image_data: list = response_object["images"]
            image_url: str = image_data[0]["url"]
        return image_url
    
    if "image_url" not in st.session_state:
        st.session_state.image_url = ""

    model_list: list = image_model_list
    model: str = st.sidebar.selectbox("Model", model_list, 0, key="image_model")

    if model == "black-forest-labs/FLUX.1-dev":
        image_size_list: list = ["1024x1024", "960x1280", "768x1024", "720x1440", "720x1280", "others"]
    elif model == "stabilityai/stable-diffusion-3-5-large":
        image_size_list: list = ["1024x1024", "512x1024", "768x512", "768x1024", "1024x576", "576x1024"]
    image_size: str = st.sidebar.selectbox("Image Size", image_size_list, 0, key="image_size")
    if image_size == "others":
        length_: str = st.sidebar.text_input("Length", "", key="length_")
        width_: str = st.sidebar.text_input("Width", "", key="width_")
        image_size: str = f"{length_}x{width_}"
    
    num_inference_steps: int = st.sidebar.slider("Inference Steps", 1, 50, 35, 1, key="num_inference_steps")

    if model == "stabilityai/stable-diffusion-3-5-large":
        guidance_scale: float = st.sidebar.slider("Guidance Scale", 0.0, 20.0, 4.5, 0.1, key="guidance_scale")
        negative_prompt: str = st.sidebar.text_area("Negative Prompt", "", key="negative_prompt")

    prompt_enhancement: bool = st.sidebar.toggle("Prompt Enhancement", False, key="prompt_enhancement")

    clear_btn: bool = st.sidebar.button("Clear", "image_clear")

    prompt: str = st.text_area("Prompt", "", key="image_prompt")

    generate: bool = st.button("Generate", "generate", type="primary")

    if model == "black-forest-labs/FLUX.1-dev":
        if generate:
            st.session_state.image_url = ""
            try:
                with st.spinner("Generating..."):
                    st.session_state.image_url = flux_image(
                        model=model,
                        prompt=prompt,
                        image_size=image_size,
                        num_inference_steps=num_inference_steps,
                        prompt_enhancement=prompt_enhancement)
            except Exception as e:
                st.error(f"Error occured: {e}")
            st.rerun()
        
        if st.session_state.image_url != "":
            st.image(st.session_state.image_url, output_format="PNG")

    elif model == "stabilityai/stable-diffusion-3-5-large":
        if generate:
            st.session_state.image_url = ""
            try:
                with st.spinner("Generating..."):
                    st.session_state.image_url = sd_image(
                        model=model,
                        prompt=prompt,
                        negative_prompt=negative_prompt,
                        image_size=image_size,
                        num_inference_steps=num_inference_steps,
                        guidance_scale=guidance_scale,
                        prompt_enhancement=prompt_enhancement)
            except Exception as e:
                st.error(f"Error occured: {e}")
            st.rerun()
        
        if st.session_state.image_url != "":
            st.image(st.session_state.image_url, output_format="PNG")
    
    if clear_btn:
        st.session_state.image_url = ""
        st.rerun()
