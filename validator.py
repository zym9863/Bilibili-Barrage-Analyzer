# -*- coding: utf-8 -*-
"""
输入验证模块
提供各种输入数据的验证功能，确保数据安全和格式正确
"""

import re
from typing import Optional, Dict, Any
from urllib.parse import urlparse
from config import ValidationException


class InputValidator:
    """输入验证器"""
    
    @staticmethod
    def validate_bilibili_url(url: str) -> Dict[str, Any]:
        """
        验证B站视频URL并提取相关信息
        
        Args:
            url: 视频URL
            
        Returns:
            Dict包含验证结果和提取的信息
            
        Raises:
            ValidationException: URL格式不正确或不是B站URL
        """
        if not url or not isinstance(url, str):
            raise ValidationException("URL不能为空", error_code="EMPTY_URL")
        
        # 去除首尾空格
        url = url.strip()
        
        # 检查URL长度
        if len(url) > 2000:
            raise ValidationException("URL长度过长", error_code="URL_TOO_LONG")
        
        # 检查是否包含危险字符
        dangerous_chars = ['<', '>', '"', "'", '&', '\n', '\r', '\t']
        if any(char in url for char in dangerous_chars):
            raise ValidationException("URL包含非法字符", error_code="INVALID_CHARACTERS")
        
        try:
            parsed = urlparse(url)
        except Exception as e:
            raise ValidationException(f"URL格式错误: {e}", error_code="INVALID_FORMAT")
        
        # 检查是否是有效的HTTP(S) URL
        if parsed.scheme not in ['http', 'https']:
            raise ValidationException("URL必须以http://或https://开头", error_code="INVALID_SCHEME")
        
        # 检查是否是B站域名
        valid_domains = [
            'bilibili.com',
            'www.bilibili.com', 
            'm.bilibili.com',
            'b23.tv'
        ]
        
        if not any(parsed.netloc.endswith(domain) for domain in valid_domains):
            raise ValidationException("只支持B站视频链接", error_code="INVALID_DOMAIN")
        
        # 提取BV号或AV号
        bv_match = re.search(r'BV[A-Za-z0-9]+', url)
        av_match = re.search(r'av(\d+)', url)
        
        result = {
            'url': url,
            'domain': parsed.netloc,
            'bvid': bv_match.group() if bv_match else None,
            'avid': av_match.group(1) if av_match else None
        }
        
        if not result['bvid'] and not result['avid']:
            raise ValidationException("无法从URL中提取视频ID", error_code="NO_VIDEO_ID")
        
        return result
    
    @staticmethod
    def validate_date_input(date_input: Any) -> Optional[str]:
        """
        验证日期输入
        
        Args:
            date_input: 日期输入（可以是字符串、date对象或None）
            
        Returns:
            格式化的日期字符串或None
            
        Raises:
            ValidationException: 日期格式不正确
        """
        if date_input is None:
            return None
        
        if hasattr(date_input, 'strftime'):
            # 是date或datetime对象
            return date_input.strftime('%Y-%m-%d')
        
        if isinstance(date_input, str):
            # 验证字符串格式
            date_pattern = r'^\d{4}-\d{2}-\d{2}$'
            if not re.match(date_pattern, date_input):
                raise ValidationException("日期格式必须为YYYY-MM-DD", error_code="INVALID_DATE_FORMAT")
            
            # 进一步验证日期的有效性
            try:
                from datetime import datetime
                datetime.strptime(date_input, '%Y-%m-%d')
            except ValueError:
                raise ValidationException("日期值无效", error_code="INVALID_DATE_VALUE")
            
            return date_input
        
        raise ValidationException("不支持的日期类型", error_code="UNSUPPORTED_DATE_TYPE")
    
    @staticmethod
    def validate_number_input(value: Any, min_val: float = None, max_val: float = None, 
                            field_name: str = "数值") -> float:
        """
        验证数字输入
        
        Args:
            value: 输入值
            min_val: 最小值
            max_val: 最大值
            field_name: 字段名称（用于错误消息）
            
        Returns:
            验证后的数字
            
        Raises:
            ValidationException: 数字格式不正确或超出范围
        """
        try:
            num_value = float(value)
        except (ValueError, TypeError):
            raise ValidationException(f"{field_name}必须是数字", error_code="INVALID_NUMBER")
        
        if min_val is not None and num_value < min_val:
            raise ValidationException(
                f"{field_name}不能小于{min_val}",
                error_code="NUMBER_TOO_SMALL"
            )
        
        if max_val is not None and num_value > max_val:
            raise ValidationException(
                f"{field_name}不能大于{max_val}",
                error_code="NUMBER_TOO_LARGE"
            )
        
        return num_value
    
    @staticmethod
    def validate_text_input(text: str, max_length: int = None, min_length: int = None,
                          field_name: str = "文本") -> str:
        """
        验证文本输入
        
        Args:
            text: 输入文本
            max_length: 最大长度
            min_length: 最小长度
            field_name: 字段名称
            
        Returns:
            验证后的文本
            
        Raises:
            ValidationException: 文本格式不正确或长度超出范围
        """
        if not isinstance(text, str):
            raise ValidationException(f"{field_name}必须是字符串", error_code="INVALID_TEXT_TYPE")
        
        # 去除首尾空格
        text = text.strip()
        
        if min_length is not None and len(text) < min_length:
            raise ValidationException(
                f"{field_name}长度不能小于{min_length}个字符",
                error_code="TEXT_TOO_SHORT"
            )
        
        if max_length is not None and len(text) > max_length:
            raise ValidationException(
                f"{field_name}长度不能大于{max_length}个字符",
                error_code="TEXT_TOO_LONG"
            )
        
        # 检查是否包含危险内容（基本的XSS防护）
        dangerous_patterns = [
            r'<script[^>]*>',
            r'javascript:',
            r'on\w+\s*=',
            r'<iframe[^>]*>',
            r'<object[^>]*>',
            r'<embed[^>]*>'
        ]
        
        for pattern in dangerous_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                raise ValidationException(
                    f"{field_name}包含不安全内容",
                    error_code="UNSAFE_CONTENT"
                )
        
        return text
    
    @staticmethod
    def sanitize_error_message(error_msg: str) -> str:
        """
        清理错误消息，避免暴露敏感信息
        
        Args:
            error_msg: 原始错误消息
            
        Returns:
            清理后的错误消息
        """
        # 移除可能的文件路径
        error_msg = re.sub(r'[A-Za-z]:[\\\/][^\s]*', '[路径已隐藏]', error_msg)
        
        # 移除IP地址
        error_msg = re.sub(r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b', '[IP已隐藏]', error_msg)
        
        # 移除可能的密钥信息
        error_msg = re.sub(r'key[=:]\s*[A-Za-z0-9+/=]+', 'key=[已隐藏]', error_msg, flags=re.IGNORECASE)
        
        # 限制错误消息长度
        if len(error_msg) > 200:
            error_msg = error_msg[:200] + "..."
        
        return error_msg


# 全局验证器实例
validator = InputValidator()