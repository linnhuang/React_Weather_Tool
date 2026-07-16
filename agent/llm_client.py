import os
import time
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

class LLMClient:
    def __init__(self, model="deepseek-v4-flash", api_key=None, base_url=None):
        """
        初始化 LLM 客户端
        :param model: 模型名称，如 gpt-3.5-turbo, gpt-4, claude-3-opus 等
        :param api_key: API密钥，默认从环境变量读取
        :param base_url: 自定义API端点，用于代理或本地模型
        """
        self.model = model or os.getenv("MODEL")
        # print(self.model)
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        # print(self.api_key)
        self.base_url = base_url or os.getenv("BASE_URL")
        # print(self.base_url)
        
        # 初始化客户端
        self.client = OpenAI(
            api_key=self.api_key,
            base_url=self.base_url
        )

    def get_response(self, messages, temperature=0, stop=None, **kwargs):
        """获取模型回复文本"""
        try:
            start = time.perf_counter()
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                stop=stop,
                **kwargs
            )
            latency_ms = (
                time.perf_counter() - start
                ) * 1000
            # print(f"API调用成功，耗时: {latency_ms:.2f} ms")
            # print(f"响应内容: {response.choices[0].message.content}")
            return response.choices[0].message.content, latency_ms
        except Exception as e:
            print(f"API调用失败: {e}")
            return None, None
    
    def create_messages(self, system_prompt=None, user_query=None, history=None):
        """构建标准消息格式"""
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        if history:
            messages.extend(history)
        if user_query:
            messages.append({"role": "user", "content": user_query})
        return messages
