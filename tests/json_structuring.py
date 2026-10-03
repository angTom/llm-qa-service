
import json
import os
import re

from dotenv import load_dotenv
from openai import OpenAI


class JsonStructuring:
    """
    JSON 结构化输出
    让模型从一段商品描述中提取出商品信息 (商品名称, 商品价格, 商品卖点),并返回JSON

    """
    SYSTEM_PROMPT = """
    # 定义角色
    你是一个商品信息提取专家，请分析商品描述并从中提取相关信息，返回JSON格式。
    # 输出
    必须严格按照以下JSON格式返回：
    {
        "name": "商品名称",
        "price": 浮点类型的数字,列如: 123.45 (商品价格),
        "sell_point": "商品卖点(50字以内)"
    }
    # 示例
    输入：
    商品描述：
    iPhone 13 Pro Max 5G手机 售价为9999.99元，采用最新工艺,512G内存，6.7英寸屏幕，支持5G网络，支持指纹识别，支持人脸识别，支持蓝牙5.0，支持Wi-Fi 6，支持NFC，支持GPS，支持双频，支持双卡，支持双卡插槽，支持双卡双待，支持双卡双待插槽，支持双卡双待插槽，支持双卡双待插槽，支持双卡双待插槽，支持双卡双待插槽，支持双卡双待插槽，支持双卡双待插
    # 输出：
    {
        "name": "iPhone 13 Pro Max 5G手机",
        "price": 9999.99,
        "sell_point": "512G内存,6.7英寸屏幕,支持5G网络,支持指纹识别"
    """
    
    def __init__(self,api_key: str,base_url: str,timeout: int=60):
        self.client = OpenAI(
            api_key=api_key, 
            base_url=base_url,
            timeout=timeout
        )
    def get_completions(self,user_info: str, model: str="gpt-3.5-turbo-0301"):
        """
        获取模型输出
        :param user_info: 用户输入
        :param model: 模型名称
        :return: 模型输出
        """
        user_prompt = f"用户输入：{user_info}"
        try: 
            response = self.client.chat.completions.create(
                model= model,
                messages=[
                    {
                        "role": "system",
                        "content": JsonStructuring.SYSTEM_PROMPT,
                    },
                    {
                        "role": "user",
                        "content": user_prompt,
                    },
                ],
                temperature=0.0,
                response_format={"type": "json_object"}, # 指定返回的格式为JSON对象
            )
            resp = response.choices[0].message.content
            json_data = self.parse_llm_json(resp)
            return json_data
        except json.JSONDecodeError as e:
            print(f"JSON 解析错误 {e}")  
            return resp
        except Exception as e:
            print(f"未知错误: {e}")
            return None


    def parse_llm_json(self,data: str):
        """
        清洗模型返回的```json代码块，直接返回python对象，失败抛异常
        :param data: json代码块
        """
        # 定义正则模式
        pattern = r"```(?:json)?\n?(.*?)\n?```"
        # re.search 在整个文本里搜索，找到第一个匹配上面正则的片段
        # re.DOTALL 让 . 可以匹配换行符（否则.*只能匹配单行文本）
        match = re.search(pattern, data, re.DOTALL)
        if match:
            # 取出捕获到的json文本,strip()去除字符串首尾空格
            raw_json = match.group(1).strip()
        else:
            # 没有匹配到json代码块，返回原始数据
            raw_json = data.strip()  
        try:
            json_data = json.loads(raw_json)
            return json_data
        except json.JSONDecodeError as e:
            # 如果解析json失败，抛出ValueError异常
            raise ValueError(f"JSON 解析失败,清洗后的文本为：{raw_json}, error: {e}") from e


if __name__ == '__main__':
    # 读取.env文件
    load_dotenv()    
    api_key = os.getenv("DEEPSEEK_API_KEY")
    base_url = os.getenv("DEEPSEEK_BASE_URL")
    model = os.getenv("DEEPSEEK_MODEL")
    
    # 创建JsonStructuring对象
    json_structuring = JsonStructuring(api_key, base_url)
    # 用户输入
    # user_input = "这款轻量化折叠遮阳伞，售价 59 元。伞骨采用高韧性玻纤，晴雨两用，伞面能阻隔 99% 紫外线，收纳后只有手掌大小"
    # user_input = "静音无线鼠标，定价 79 元。支持蓝牙 + 2.4G 双模式连接，续航长达 6 个月，按键无声，适配笔记本、平板多设备。"
    # user_input = "高硼硅玻璃冷水壶，价格 45 元。大容量 1.8L，耐高温可直接倒入开水，防爆耐冷热冲击，带防尘密封盖子。" 
    # user_input = "纯棉透气运动短袖，售价 89 元。新疆长绒棉面料，吸汗速干，宽松版型不束缚，多色可选不易掉色。"
    # user_input = "桌面多功能快充插排，99 元。4 个 USB 快充口 + 3 个五孔插座，带过载保护，线身加粗，可手机电脑同时充电。"
    # user_input = "冻干纯猫零食，售价 36 元。100% 鸡胸肉无添加，0 谷物 0 诱食剂，帮助猫咪磨牙，增肥发腮，幼猫成猫通用。"
    # user_input = "不锈钢保温杯，价格 129 元。316 食品级内胆，24 小时长效保温，一键开盖，防漏设计，车载便携。"
    user_input = "硅藻泥防滑浴室地垫，售价 49 元。吸水速度快，踩上去瞬间干爽，防霉不易滋生细菌，可水洗反复使用。"
    json_data = json_structuring.get_completions(user_input,model)
    print(json.dumps(json_data, indent=4, ensure_ascii=False))

