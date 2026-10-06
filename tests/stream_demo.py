

import os

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
print(os.getenv("DEEPSEEK_API_KEY"))
client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url=os.getenv("DEEPSEEK_BASE_URL"),
    timeout=60
)



user_input = "用户输入问题：请详细的介绍一下你自己!包括你有哪些优点等"

response = client.chat.completions.create(
    model=os.getenv("DEEPSEEK_MODEL"),
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": user_input}
    ],
    max_tokens=2048,
    temperature=0,
    stream=True
)

for chunk in response:
    
    delta = chunk.choices[0].delta
    if chunk.choices and delta.content:
        print(delta.content, end="", flush=True)
       




    
