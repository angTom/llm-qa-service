import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"), 
    base_url=os.getenv("DEEPSEEK_BASE_URL"),
    timeout=60
)
messages = []
system_message = {
        "role": "system",
        "content": "你是一个专业的电商售后客服，回答不超过50字，不知道就说不知道",
    }
messages.append(system_message)
def chat(message):
    response = client.chat.completions.create(
        model=os.getenv("DEEPSEEK_MODEL"),
        messages=messages
        
    )
    messages.append({"role": "user", "content": message})
    resp = response.choices[0].message.content
    messages.append({"role": "assistant", "content": resp})
    print(f"ai回答是: {resp}")
    print(f"消息列表: {messages}")


if __name__ == "__main__":
    while True:
        print("===========欢迎来到智能客服系统==========")
        user_message = input("请输入您的问题：")
        chat(user_message)
       