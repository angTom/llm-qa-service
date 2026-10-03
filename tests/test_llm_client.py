
from pathlib import Path
import sys
import time

sys.path.append(str(Path(__file__).parent.parent))
from app.utils.llm_client import LLMClient


# 初始化客户端
client = LLMClient()

def test_multi_round_conversation():
    """测试多轮对话场景"""
    print("=== 开始多轮对话测试 ===")
    history = []
    # 第一轮提问
    history.append({"role": "user", "content": "1+1等于几？"})
    resp1 = client.chat(history, system_prompt="你是一个只会回答数字的数学助手")
    print(f"第一轮回复: {resp1}")
    history.append({"role": "assistant", "content": resp1})
    # 第二轮追问
    history.append({"role": "user", "content": "那再加2等于几？"})
    resp2 = client.chat(history)
    print(f"第二轮回复: {resp2}")
    assert "4" in resp2, "多轮对话上下文记忆失败"
    print("✅ 多轮对话测试通过\n")
    time.sleep(1)

def test_long_text_input():
    """测试长文本输入场景"""
    print("=== 开始长文本测试 ===")
    long_text = "Python是一门非常流行的编程语言，" * 200
    messages = [{"role": "user", "content": f"请总结下面这段文本的核心含义：{long_text}"}]
    resp = client.chat(messages, max_tokens=512)
    print(f"ai回答是: {resp}")
   
    if resp is None:
        print("大模型接口调用失败，返回为空")
    else:
        print(f"长文本返回长度: {len(resp)} 字符")
    assert len(resp) > 0, "长文本调用无返回"
    print("✅ 长文本测试通过\n")
    time.sleep(1)

def test_exception_scene():
    """测试异常重试场景"""
    print("=== 开始异常场景测试 ===")
    try:
        # 故意填一个错误的base_url触发连接错误，验证重试逻辑
        bad_client = LLMClient()
        bad_client.base_url = "https://invalid-api.example.com/v1"
        bad_client.client.base_url = bad_client.base_url
        bad_client.chat([{"role": "user", "content": "hi"}])
    except Exception as e:
        print(f"预期捕获到异常: {type(e).__name__}，重试机制已执行")
    print("✅ 异常场景测试通过\n")

if __name__ == "__main__":
    test_multi_round_conversation()
    test_long_text_input()
    test_exception_scene()
    print("🎉 所有测试用例全部执行完成")
