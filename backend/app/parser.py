from pathlib import Path
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)


class MarkItDownParser:
    """使用 MarkItDown 统一解析各类文档"""
    
    @staticmethod
    def parse(file_path: str) -> Dict[str, Any]:
        """解析文档，返回 Markdown 格式内容"""
        try:
            from markitdown import MarkItDown
            
            md = MarkItDown()
            result = md.convert(file_path)
            
            return {
                "raw_text": result.text_content,
                "markdown": result.markdown,
                "file_type": Path(file_path).suffix.lower(),
                "file_path": str(file_path),
                "metadata": {
                    "title": getattr(result, "title", None),
                    "author": getattr(result, "author", None),
                }
            }
        except ImportError:
            raise ImportError("请安装 MarkItDown：pip install markitdown")
        except Exception as e:
            logger.error(f"文档解析失败：{e}")
            raise Exception(f"文档解析失败：{str(e)}")
    
    @staticmethod
    def parse_to_structured(file_path: str) -> Dict[str, Any]:
        """解析文档并提取结构化信息"""
        result = MarkItDownParser.parse(file_path)
        markdown = result["markdown"]
        
        return {
            "markdown": markdown,
            "raw_text": result["raw_text"],
            "file_type": result["file_type"],
            "parsed": False
        }
