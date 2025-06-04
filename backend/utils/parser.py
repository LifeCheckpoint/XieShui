import re
import xml.etree.ElementTree as ET
from typing import Dict, Optional, Union

def parse_trailing_xml(text: str) -> Optional[Dict[str, Union[str, Dict]]]:
    """
    解析文本末尾的工具调用XML段落，转换为指定字典格式
    
    参数:
        text: 包含可能XML段落的文本
        
    返回:
        解析后的字典 (格式: {"name": root_tag, "parameters": {child_tags}})
        或 None (当无有效XML时)
        
    异常:
        ValueError: XML结构不符合要求时
    """
    # 防御性检查：处理空文本
    if not text.strip():
        return None
    
    # 使用正则定位文本末尾的XML段落
    xml_pattern = re.compile(r'(<(\w+)>(.*?)</\2>)\s*$', re.DOTALL)
    match = xml_pattern.search(text)
    
    if not match:
        return None
    
    xml_str = match.group(1)
    root_tag = match.group(2)
    inner_content = match.group(3).strip()
    
    try:
        # 使用ElementTree安全解析XML
        root = ET.fromstring(xml_str)
    except ET.ParseError as e:
        raise ValueError(f"无法将文本解析为 XML 格式: {str(e)}")
    
    # 验证XML结构
    if len(root) == 0 and not inner_content:
        return {"name": root_tag, "parameters": {}}  # 空标签处理
    
    # 检查多层嵌套
    for child in root:
        if len(child) > 0 or list(child):
            raise ValueError("Multi-level nested XML detected")
        if child.text is None:
            raise ValueError("Empty XML element content")
    
    # 构建参数字典
    params = {child.tag: child.text for child in root}
    
    return {"name": root_tag, "parameters": params}
