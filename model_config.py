import requests
import re

url = "https://api.siliconflow.cn/v1/models"

visual_model_list = [
    "Qwen/Qwen2-VL-72B-Instruct",
    "OpenGVLab/InternVL2-26B",
    "TeleAI/TeleMM",
    "Pro/Qwen/Qwen2-VL-7B-Instruct",
    "Pro/OpenGVLab/InternVL2-8B"
]

reasoning_model_list = [
    "Qwen/QwQ-32B-Preview",
    "Qwen/QVQ-72B-Preview",
    "AIDC-AI/Marco-o1"
]

excluded_models = [
    "deepseek-ai/deepseek-vl2",
    "01-ai/Yi-1.5-6B-Chat"
]

image_model_list = [
    "black-forest-labs/FLUX.1-dev",
    "stabilityai/stable-diffusion-3-5-large"
]

qwen_pattern = re.compile(r'^Qwen/')
meta_llama_pattern = re.compile(r'^meta-llama/')
deepseek_ai_pattern = re.compile(r'^deepseek-ai/')
pro_lora_pattern = re.compile(r'^(Pro|LoRA)/')

def extract_version_and_params(model):
    version_match = re.search(r'(\d+(\.\d+)+)', model)
    version = float(version_match.group(1)) if version_match else 0.0
    
    params_match = re.search(r'(\d+(\.\d+)?)(B|b)', model)
    params = float(params_match.group(1)) if params_match else 0.0
    
    return version, params

def sort_models(model_list):
    return sorted(model_list, key=lambda x: extract_version_and_params(x), reverse=True)

def text_model(api_key: str) -> list:
    model_list = []

    querystring = {"type":"text","sub_type":"chat"}
    headers = {"Authorization": f"Bearer {api_key}"}
    response = requests.request("GET", url, params=querystring, headers=headers)

    if response.status_code == 200:
        response_object = response.json()
        response_data = response_object["data"]
        for i in response_data:
            if i["id"] not in visual_model_list and i["id"] not in reasoning_model_list and i["id"] not in excluded_models:
                model_list.append(i["id"])
    
    qwen_models = [model for model in model_list if qwen_pattern.search(model) and not pro_lora_pattern.search(model)]
    meta_llama_models = [model for model in model_list if meta_llama_pattern.search(model) and not pro_lora_pattern.search(model)]
    deepseek_ai_models = [model for model in model_list if deepseek_ai_pattern.search(model) and not pro_lora_pattern.search(model)]
    other_models = [model for model in model_list if not qwen_pattern.search(model) and not meta_llama_pattern.search(model) and not deepseek_ai_pattern.search(model) and not pro_lora_pattern.search(model)]
    pro_lora_models = [model for model in model_list if pro_lora_pattern.search(model)]

    qwen_models_sorted = sort_models(qwen_models)
    meta_llama_models_sorted = sort_models(meta_llama_models)
    deepseek_ai_models_sorted = sort_models(deepseek_ai_models)
    other_models_sorted = sort_models(other_models)
    pro_lora_models_sorted = sort_models(pro_lora_models)

    model_list = qwen_models_sorted + meta_llama_models_sorted + deepseek_ai_models_sorted + other_models_sorted + pro_lora_models_sorted

    return model_list


