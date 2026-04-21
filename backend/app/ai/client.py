import httpx
import asyncio
from typing import Dict, List, Any, Optional
from ..models import AIModelConfig


class UnifiedAIClient:
    """统一 AI 客户端"""
    
    def __init__(self):
        self.http_client = httpx.Client(timeout=60.0)
        self.config_cache: Dict[str, AIModelConfig] = {}
    
    def load_config(self, config: AIModelConfig):
        """加载配置"""
        self.config_cache[config.model_type] = config
    
    def _get_llm_config(self) -> Optional[AIModelConfig]:
        """获取 LLM 配置"""
        return self.config_cache.get("llm")
    
    def _get_embedding_config(self) -> Optional[AIModelConfig]:
        """获取向量化配置"""
        return self.config_cache.get("embedding")
    
    def set_default_configs(self, llm_config: AIModelConfig = None, embedding_config: AIModelConfig = None):
        """设置默认配置"""
        if llm_config:
            self.config_cache["llm"] = llm_config
        if embedding_config:
            self.config_cache["embedding"] = embedding_config
    
    def chat(self, prompt: str, system_prompt: str = None, **kwargs) -> str:
        """LLM 对话"""
        config = self._get_llm_config()
        if not config:
            raise ValueError("LLM 模型未配置")
        
        if config.provider == "dashscope":
            return self._dashscope_chat(prompt, system_prompt, config, **kwargs)
        elif config.provider in ["openai", "custom"]:
            return self._openai_compat_chat(prompt, system_prompt, config, **kwargs)
        elif config.provider == "local":
            return self._local_chat(prompt, system_prompt, config, **kwargs)
        else:
            raise ValueError(f"不支持的 provider: {config.provider}")
    
    def _dashscope_chat(self, prompt: str, system_prompt: str, config: AIModelConfig, **kwargs) -> str:
        """通义千问对话"""
        import dashscope
        dashscope.api_key = config.api_key
        
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        response = dashscope.Generation.call(
            model=config.model_name,
            messages=messages,
            result_format='text',
            **config.extra_config
        )
        
        if response.status_code == 200:
            return response.output.text
        else:
            raise Exception(f"通义千问调用失败：{response.code}")
    
    def _openai_compat_chat(self, prompt: str, system_prompt: str, config: AIModelConfig, **kwargs) -> str:
        """OpenAI 兼容接口对话"""
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        response = self.http_client.post(
            f"{config.base_url}/chat/completions",
            headers={"Authorization": f"Bearer {config.api_key}"},
            json={
                "model": config.model_name,
                "messages": messages,
                **config.extra_config
            }
        )
        
        if response.status_code == 200:
            return response.json()["choices"][0]["message"]["content"]
        else:
            raise Exception(f"API 调用失败：{response.status_code}")
    
    def _local_chat(self, prompt: str, system_prompt: str, config: AIModelConfig, **kwargs) -> str:
        """本地模型对话（Ollama）"""
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        response = self.http_client.post(
            f"{config.base_url}/api/chat",
            json={
                "model": config.model_name,
                "messages": messages,
                "stream": False
            }
        )
        
        if response.status_code == 200:
            return response.json()["message"]["content"]
        else:
            raise Exception(f"本地模型调用失败：{response.status_code}")
    
    def embed(self, texts: List[str]) -> List[List[float]]:
        """文本向量化"""
        config = self._get_embedding_config()
        if not config:
            config = self._get_llm_config()
        
        if not config:
            raise ValueError("未配置向量化模型")
        
        if config.provider == "dashscope":
            return self._dashscope_embedding(texts, config)
        else:
            return self._openai_embedding(texts, config)
    
    def _dashscope_embedding(self, texts: List[str], config: AIModelConfig) -> List[List[float]]:
        """通义千问向量化"""
        import dashscope
        from dashscope import TextEmbedding
        
        dashscope.api_key = config.api_key
        
        embeddings = []
        for text in texts:
            response = TextEmbedding.call(
                model=config.model_name or "text-embedding-v2",
                input=text
            )
            if response.status_code == 200:
                embeddings.append(response.output["embeddings"][0]["embedding"])
            else:
                raise Exception(f"向量化失败：{response.code}")
        
        return embeddings
    
    def _openai_embedding(self, texts: List[str], config: AIModelConfig) -> List[List[float]]:
        """OpenAI 兼容向量化"""
        response = self.http_client.post(
            f"{config.base_url}/embeddings",
            headers={"Authorization": f"Bearer {config.api_key}"},
            json={
                "model": config.model_name,
                "input": texts
            }
        )
        
        if response.status_code == 200:
            return [item["embedding"] for item in response.json()["data"]]
        else:
            raise Exception(f"向量化失败：{response.status_code}")
    
    def test_connection(self, model_type: str) -> Dict[str, Any]:
        """测试连接"""
        try:
            if model_type == "llm":
                result = self.chat("你好", "你是一个 AI 助手，只需要回复'你好'即可")
                return {"success": True, "message": "连接成功", "response": result[:100]}
            elif model_type == "embedding":
                result = self.embed(["测试文本"])
                return {"success": True, "message": f"连接成功，向量维度：{len(result[0])}"}
            else:
                return {"success": False, "message": "未知的模型类型"}
        except Exception as e:
            return {"success": False, "message": str(e)}
    
    def close(self):
        """关闭客户端"""
        self.http_client.close()


# 全局 AI 客户端实例
ai_client = UnifiedAIClient()
