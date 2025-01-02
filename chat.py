from openai import OpenAI

def chat_completion(
    api_key: str,
    model: str,
    messages: list,
    tokens: int,
    temp: float,
    topp: float,
    freq: float,
    pres: float,
    stop: list):
    api_key = api_key
    base_url = "https://api.siliconflow.cn/v1"
    client = OpenAI(api_key=api_key, base_url=base_url)
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        max_tokens=tokens,
        temperature=temp,
        top_p=topp,
        frequency_penalty=freq,
        presence_penalty=pres,
        stop=stop,
        stream=True
    )
    return response
