

import os
from dotenv import load_dotenv
from openai import OpenAI



# 读取 .env 文件中的Key, 发送一条消息,答=打印回复
load_dotenv()  # 加载 .env 文件
api_key = os.getenv("DEEPSEEK_API_KEY")
base_url = os.getenv("DEEPSEEK_BASE_URL")
model = os.getenv("DEEPSEEK_MODEL")
client = OpenAI(
    api_key=api_key,
    base_url=base_url,
    timeout=60
)

response = client.chat.completions.create(
    model=model,
    messages=[
        {"role": "system", "content": "你是一个ai客服助手"},
        {"role": "user", "content": "都买了两天了,我的鞋子怎么还没到啊?"},
    ],
    stream=False,
    temperature=0.0,
    # reasoning_effort="high", # 推理效率
    # extra_body={"thinking": {"type": "enabled"}}, # 推理过程
    # max_tokens=50
)
resp = response.choices[0].message.content
usage = response.usage
print(resp)
print(f"usage: {usage}")