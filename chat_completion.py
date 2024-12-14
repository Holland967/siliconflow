from openai import OpenAI

class ChatCompletion:
    def __init__(self, api_key: str, base_url: str):
        self.api_key: str = api_key
        self.base_url: str = base_url
    
    def chat_completions(
        self,
        model: str,
        messages: list,
        max_tokens: int = 4096,
        temperature: float = 0.70,
        top_p: float = 0.90,
        frequency_penalty: float = 0.00,
        presence_penalty: float = 0.00):
        client = OpenAI(api_key=self.api_key, base_url=self.base_url)
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature,
            top_p=top_p,
            frequency_penalty=frequency_penalty,
            presence_penalty=presence_penalty,
            stop=None,
            stream=True)
        return response
