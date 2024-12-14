import requests

url = "https://api.siliconflow.cn/v1/models"

reasoning_chat_model_list: list = [
    "Qwen/QwQ-32B-Preview",
    "AIDC-AI/Marco-o1"
]

vision_chat_model_list: list = [
    "Qwen/Qwen2-VL-72B-Instruct",
    "Pro/Qwen/Qwen2-VL-7B-Instruct",
    "OpenGVLab/InternVL2-Llama3-76B",
    "OpenGVLab/InternVL2-26B",
    "Pro/OpenGVLab/InternVL2-8B",
    "TeleAI/TeleMM"
]

trash_model_list: list = [
    "01-ai/Yi-1.5-6B-Chat",
    "01-ai/Yi-1.5-9B-Chat-16K",
    "01-ai/Yi-1.5-34B-Chat-16K",
    "internlm/internlm2_5-7b-chat",
    "internlm/internlm2_5-20b-chat",
    "Qwen/Qwen2.5-Math-72B-Instruct",
    "nvidia/Llama-3.1-Nemotron-70B-Instruct",
    "Pro/Qwen/Qwen2-1.5B-Instruct",
    "Pro/Qwen/Qwen2-7B-Instruct",
    "Qwen/Qwen2-72B-Instruct",
    "Vendor-A/Qwen/Qwen2-72B-Instruct",
    "Pro/Qwen/Qwen2-1.5B-Instruct",
    "Pro/Qwen/Qwen2-7B-Instruct",
    "deepseek-ai/DeepSeek-V2-Chat",
    "Tencent/Hunyuan-A52B-Instruct",
    "THUDM/chatglm3-6b",
    "THUDM/glm-4-9b-chat",
    "google/gemma-2-9b-it",
    "Pro/google/gemma-2-9b-it",
    "TeleAI/TeleChat2",
    "TheDrummer/Rocinante-12B-v1.1/cm2jg6s0g01rxa1ixn16nzr5o"
]

excluded_model_list: list = reasoning_chat_model_list + vision_chat_model_list + trash_model_list

def text_chat_models(api_key: str) -> list:
    model_list: list = []
    querystring = {"type":"text", "sub_type":"chat"}
    headers = {"Authorization": f"Bearer {api_key}"}
    response = requests.request("GET", url, params=querystring, headers=headers)
    if response.status_code == 200:
        response_object: dict = response.json()
        data: list = response_object["data"]
        for model_data in data:
            if model_data["id"] not in excluded_model_list:
                model_list.append(model_data["id"])
    
    import re

    def extract_param_size(model):
        match = re.search(r'(\d+)([BKM])', model)
        if match:
            size = match.group(1)
            unit = match.group(2)
            if unit == 'B':
                return int(size)
            elif unit == 'K':
                return int(size) * 1e3
            elif unit == 'M':
                return int(size) * 1e6
        return 0
    
    def sort_key(model):
        # 优先级：Qwen > Llama > deepseek-ai > 其他 > Pro > LoRA
        if 'Pro' in model:
            return (4, -extract_param_size(model), model)
        elif 'LoRA' in model:
            return (5, -extract_param_size(model), model)
        elif 'Qwen' in model:
            return (0, -extract_param_size(model), model)
        elif 'Llama' in model or 'meta-llama' in model:
            return (1, -extract_param_size(model), model)
        elif 'deepseek-ai' in model:
            return (2, -extract_param_size(model), model)
        else:
            return (3, -extract_param_size(model), model)
    
    model_list: list = sorted(model_list, key=sort_key)

    return model_list

image_model_list: list = [
    "black-forest-labs/FLUX.1-dev",
    "stabilityai/stable-diffusion-3-5-large"
]
