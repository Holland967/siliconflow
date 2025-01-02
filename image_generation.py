import streamlit as st
import requests

from model_config import image_model_list

url = "https://api.siliconflow.cn/v1/images/generations"

flux_image_size = [
    "1024x1024",
    "960x1280",
    "768x1024",
    "720x1440",
    "720x1280",
    "others"
]

sd_image_size = [
    "1024x1024",
    "512x1024",
    "768x512",
    "768x512",
    "1024x576",
    "576x1024"
]

def flux_image_generator(api_key: str, prompt: str, image_size: str, seed: int, step: int, prompt_enhancement: bool):
    if seed is not None:
        payload = {
            "model": "black-forest-labs/FLUX.1-dev",
            "prompt": prompt,
            "image_size": image_size,
            "seed": seed,
            "num_inference_steps": step,
            "prompt_enhancement": prompt_enhancement
        }
    elif seed is None:
        payload = {
            "model": "black-forest-labs/FLUX.1-dev",
            "prompt": prompt,
            "image_size": image_size,
            "num_inference_steps": step,
            "prompt_enhancement": prompt_enhancement
        }
    
    headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
    }

    response = requests.request("POST", url, json=payload, headers=headers)
    if response.status_code == 200:
        response_object = response.json()
        response_data = response_object["images"]
        response_url = response_data[0]["url"]
        return response_url

def sd_image_generator(api_key: str, prompt: str, negative_prompt: str, image_size: str, seed: int, step: int, guidance_scale: int, prompt_enhancement: bool):
    if seed is not None:
        payload = {
            "model": "stabilityai/stable-diffusion-3-5-large",
            "prompt": prompt,
            "negative_prompt": negative_prompt,
            "image_size": image_size,
            "batch_size": 1,
            "seed": seed,
            "num_inference_steps": step,
            "guidance_scale": guidance_scale,
            "prompt_enhancement": prompt_enhancement
        }
    else:
        payload = {
            "model": "stabilityai/stable-diffusion-3-5-large",
            "prompt": prompt,
            "negative_prompt": negative_prompt,
            "image_size": image_size,
            "batch_size": 1,
            "num_inference_steps": step,
            "guidance_scale": guidance_scale,
            "prompt_enhancement": prompt_enhancement
        }
    
    headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
    }

    response = requests.request("POST", url, json=payload, headers=headers)
    if response.status_code == 200:
        response_object = response.json()
        response_data = response_object["images"]
        response_url = response_data[0]["url"]
        return response_url

def imageGeneration(api_key: str):
    if "image_url" not in st.session_state:
        st.session_state.image_url = ""
    if "generate_state" not in st.session_state:
        st.session_state.generate_state = False

    with st.sidebar:
        reset_btn = st.button("Reset", "img_reset_btn", type="primary", use_container_width=True, disabled=st.session_state.image_url=="")
        model_list = image_model_list
        model = st.selectbox("Model", model_list, 0, key="img_model", disabled=st.session_state.image_url!="")
    
    if model == "black-forest-labs/FLUX.1-dev":
        with st.sidebar:
            image_size = st.selectbox("Image Size", flux_image_size, 0, key="flux_img_size")
            if image_size == "others":
                length = st.text_input("Length", "", key="length")
                width = st.text_input("Width", "", key="width")
                if length and width and "." not in length and "." not in width:
                    if length[0]!="0" and width[0]!="0":
                        image_size = f"{length}x{width}"
                        st.session_state.generate_state = False
                        st.markdown(f"Custom Image Size: `{image_size}`")
                    elif length[0]=="0" or width[0]=="0":
                        st.session_state.generate_state = True
                        st.warning("Please input an integer!")
                elif "." in length or "." in width:
                    st.session_state.generate_state = True
                    st.warning("Please input an integer!")

            step = st.slider("Inference Steps", 1, 50, 50, 1, key="flux_step")
            seed_input = st.text_input("Seed", "", key="flux_seed")
            if seed_input and "." not in seed_input:
                try:
                    seed = int(seed_input)
                    st.session_state.generate_state = False
                except Exception as e:
                    st.session_state.generate_state = True
                    st.error(f"Error occured: {e}")
            elif seed_input and "." in seed_input:
                st.session_state.generate_state = True
                st.warning("Please input an integer!")
            elif not seed_input:
                st.session_state.generate_state = False
                seed = None
            prompt_enhancement = st.toggle("Prompt Enhancement", False, key="flux_enhancement")

        prompt = st.text_area("Prompt", "", key="flux_prompt", disabled=st.session_state.generate_state)
        generate_btn = st.button("Generate", "flux_generate", type="primary", disabled=prompt=="")

        if generate_btn:
            try:
                with st.spinner("Generating..."):
                    st.session_state.image_url = flux_image_generator(api_key, prompt, image_size, seed, step, prompt_enhancement)
                    st.rerun()
            except Exception as e:
                st.error(f"Error occured: {e}")
        
        if st.session_state.image_url != "":
            st.image(st.session_state.image_url, output_format="PNG")
    
    elif model == "stabilityai/stable-diffusion-3-5-large":
        with st.sidebar:
            image_size = st.selectbox("Image Size", sd_image_size, 0, key="sd_img_size")
            step = st.slider("Inference Steps", 1, 50, 50, 1, key="sd_step")
            guidance_scale = st.slider("Guidance Scale", 0.0, 20.0, 4.5, 0.1, key="sd_guidance")
            seed_input = st.text_input("Seed", "", key="sd_seed")
            if seed_input and "." not in seed_input:
                try:
                    seed = int(seed_input)
                    st.session_state.generate_state = False
                except Exception as e:
                    st.session_state.generate_state = True
                    st.error(f"Error occured: {e}")
            elif seed_input and "." in seed_input:
                st.session_state.generate_state = True
                st.warning("Please input an integer!")
            elif not seed_input:
                st.session_state.generate_state = False
                seed = None
            prompt_enhancement = st.toggle("Prompt Enhancement", False, key="sd_enhancement")

        prompt = st.text_area("Prompt", "", key="sd_prompt", disabled=st.session_state.generate_state)
        negative_prompt = st.text_area("Negative Prompt", "", key="negative_prompt", disabled=st.session_state.generate_state)
        generate_btn = st.button("Generate", "sd_generate", type="primary", disabled=prompt=="")

        if generate_btn:
            try:
                with st.spinner("Generating..."):
                    st.session_state.image_url = sd_image_generator(api_key, prompt, negative_prompt, image_size, seed, step, guidance_scale, prompt_enhancement)
                    st.rerun()
            except Exception as e:
                st.error(f"Error occured: {e}")
        
        if st.session_state.image_url != "":
            st.image(st.session_state.image_url, output_format="PNG")
    
    if reset_btn:
        st.session_state.image_url = ""
        st.rerun()
