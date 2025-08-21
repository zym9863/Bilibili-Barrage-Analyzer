# -*- coding: utf-8 -*-
"""
网络请求工具模块
提供带重试机制的HTTP请求功能，用于提高网络请求的稳定性
"""

import asyncio
import httpx
import time
from typing import Optional, Dict, Any, Callable
from config import config, NetworkException
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RetryClient:
    """带重试机制的HTTP客户端"""
    
    def __init__(self):
        """初始化客户端"""
        self.network_settings = config.network_settings
        self.timeout = self.network_settings.get('timeout', 30)
        self.max_retries = self.network_settings.get('max_retries', 3)
        self.retry_delay = self.network_settings.get('retry_delay', 1)
        self.user_agent = self.network_settings.get('user_agent', '')
    
    async def _exponential_backoff(self, attempt: int) -> None:
        """指数退避延迟"""
        delay = self.retry_delay * (2 ** attempt)
        await asyncio.sleep(delay)
    
    async def request_with_retry(
        self,
        method: str,
        url: str,
        headers: Optional[Dict[str, str]] = None,
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Any] = None,
        json: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> httpx.Response:
        """
        执行带重试机制的HTTP请求
        
        Args:
            method: HTTP方法
            url: 请求URL
            headers: 请求头
            params: URL参数
            data: 请求数据
            json: JSON数据
            **kwargs: 其他httpx参数
            
        Returns:
            httpx.Response: HTTP响应对象
            
        Raises:
            NetworkException: 网络请求异常
        """
        if headers is None:
            headers = {}
        
        # 设置用户代理
        if 'User-Agent' not in headers and self.user_agent:
            headers['User-Agent'] = self.user_agent
        
        last_exception = None
        
        for attempt in range(self.max_retries + 1):
            try:
                async with httpx.AsyncClient(timeout=self.timeout) as client:
                    response = await client.request(
                        method=method,
                        url=url,
                        headers=headers,
                        params=params,
                        data=data,
                        json=json,
                        **kwargs
                    )
                    
                    # 如果响应状态码表示需要重试的错误，则重试
                    if response.status_code in [500, 502, 503, 504, 429]:
                        raise NetworkException(
                            f"服务器错误: {response.status_code}",
                            error_code=str(response.status_code)
                        )
                    
                    return response
                    
            except (httpx.TimeoutException, httpx.ConnectTimeout, httpx.ReadTimeout) as e:
                last_exception = NetworkException(f"请求超时: {e}", error_code="TIMEOUT")
                logger.warning(f"请求超时，第{attempt + 1}次尝试: {url}")
                
            except (httpx.ConnectError, httpx.NetworkError) as e:
                last_exception = NetworkException(f"网络连接错误: {e}", error_code="NETWORK_ERROR")
                logger.warning(f"网络连接错误，第{attempt + 1}次尝试: {url}")
                
            except NetworkException as e:
                last_exception = e
                logger.warning(f"服务器错误，第{attempt + 1}次尝试: {url} - {e.message}")
                
            except Exception as e:
                last_exception = NetworkException(f"未知错误: {e}", error_code="UNKNOWN")
                logger.error(f"未知错误，第{attempt + 1}次尝试: {url} - {e}")
            
            # 如果还有重试机会，则等待后重试
            if attempt < self.max_retries:
                await self._exponential_backoff(attempt)
        
        # 所有重试都失败了，抛出最后一个异常
        raise last_exception or NetworkException("所有重试都失败了", error_code="MAX_RETRIES_EXCEEDED")
    
    async def get(self, url: str, **kwargs) -> httpx.Response:
        """GET请求"""
        return await self.request_with_retry('GET', url, **kwargs)
    
    async def post(self, url: str, **kwargs) -> httpx.Response:
        """POST请求"""
        return await self.request_with_retry('POST', url, **kwargs)


# 全局重试客户端实例
retry_client = RetryClient()


def progress_callback(current: int, total: int, message: str = "") -> None:
    """
    进度回调函数，用于显示处理进度
    
    Args:
        current: 当前进度
        total: 总进度
        message: 进度消息
    """
    try:
        import streamlit as st
        
        # 计算百分比
        percentage = int((current / total) * 100) if total > 0 else 0
        
        # 显示进度条
        progress_bar = st.progress(percentage / 100)
        
        # 显示详细信息
        if message:
            st.write(f"进度: {current}/{total} ({percentage}%) - {message}")
        else:
            st.write(f"进度: {current}/{total} ({percentage}%)")
            
    except ImportError:
        # 如果不在Streamlit环境中，使用控制台输出
        percentage = int((current / total) * 100) if total > 0 else 0
        print(f"进度: {current}/{total} ({percentage}%)" + (f" - {message}" if message else ""))


class DataCache:
    """简单的数据缓存类"""
    
    def __init__(self, max_size: int = 100):
        """初始化缓存"""
        self.cache = {}
        self.max_size = max_size
        self.access_times = {}
    
    def get(self, key: str) -> Optional[Any]:
        """获取缓存数据"""
        if key in self.cache:
            self.access_times[key] = time.time()
            return self.cache[key]
        return None
    
    def set(self, key: str, value: Any) -> None:
        """设置缓存数据"""
        # 如果缓存已满，删除最旧的数据
        if len(self.cache) >= self.max_size:
            oldest_key = min(self.access_times, key=self.access_times.get)
            self.remove(oldest_key)
        
        self.cache[key] = value
        self.access_times[key] = time.time()
    
    def remove(self, key: str) -> None:
        """删除缓存数据"""
        if key in self.cache:
            del self.cache[key]
            del self.access_times[key]
    
    def clear(self) -> None:
        """清空缓存"""
        self.cache.clear()
        self.access_times.clear()


# 全局缓存实例
data_cache = DataCache()