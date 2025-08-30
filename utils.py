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
    """数据缓存类，支持TTL过期、统计信息和分析结果缓存"""
    
    def __init__(self, max_size: int = 100, default_ttl: int = 3600):
        """
        初始化缓存
        
        Args:
            max_size: 最大缓存条目数
            default_ttl: 默认TTL（秒），默认1小时
        """
        self.cache = {}
        self.max_size = max_size
        self.default_ttl = default_ttl
        self.access_times = {}
        self.expire_times = {}
        self.hit_count = 0
        self.miss_count = 0
    
    def _is_expired(self, key: str) -> bool:
        """检查键是否已过期"""
        if key not in self.expire_times:
            return False
        return time.time() > self.expire_times[key]
    
    def _cleanup_expired(self) -> None:
        """清理过期的缓存项"""
        current_time = time.time()
        expired_keys = [
            key for key, expire_time in self.expire_times.items() 
            if current_time > expire_time
        ]
        
        for key in expired_keys:
            self.remove(key)
    
    def _evict_lru(self) -> None:
        """使用LRU策略清理最少使用的缓存项"""
        if not self.access_times:
            return
            
        oldest_key = min(self.access_times, key=self.access_times.get)
        self.remove(oldest_key)
    
    def get(self, key: str) -> Optional[Any]:
        """
        获取缓存数据
        
        Args:
            key: 缓存键
            
        Returns:
            缓存的数据，如果不存在或已过期则返回None
        """
        # 先清理过期项
        self._cleanup_expired()
        
        if key in self.cache and not self._is_expired(key):
            self.access_times[key] = time.time()
            self.hit_count += 1
            logger.debug(f"缓存命中: {key}")
            return self.cache[key]
        else:
            self.miss_count += 1
            logger.debug(f"缓存未命中: {key}")
            return None
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """
        设置缓存数据
        
        Args:
            key: 缓存键
            value: 缓存值
            ttl: 生存时间（秒），如果为None则使用默认TTL
        """
        # 如果缓存已满，先清理过期项，如果还是满的则使用LRU清理
        if len(self.cache) >= self.max_size:
            self._cleanup_expired()
            
            if len(self.cache) >= self.max_size:
                self._evict_lru()
        
        # 设置缓存
        self.cache[key] = value
        current_time = time.time()
        self.access_times[key] = current_time
        
        # 设置过期时间
        ttl_to_use = ttl if ttl is not None else self.default_ttl
        self.expire_times[key] = current_time + ttl_to_use
        
        logger.debug(f"缓存设置: {key}, TTL: {ttl_to_use}秒")
    
    def remove(self, key: str) -> None:
        """删除缓存数据"""
        if key in self.cache:
            del self.cache[key]
            if key in self.access_times:
                del self.access_times[key]
            if key in self.expire_times:
                del self.expire_times[key]
            logger.debug(f"缓存删除: {key}")
    
    def clear(self) -> None:
        """清空缓存"""
        self.cache.clear()
        self.access_times.clear()
        self.expire_times.clear()
        self.hit_count = 0
        self.miss_count = 0
        logger.info("缓存已清空")
    
    def get_stats(self) -> Dict[str, Any]:
        """
        获取缓存统计信息
        
        Returns:
            包含缓存统计信息的字典
        """
        total_requests = self.hit_count + self.miss_count
        hit_rate = (self.hit_count / total_requests * 100) if total_requests > 0 else 0
        
        return {
            'size': len(self.cache),
            'max_size': self.max_size,
            'hit_count': self.hit_count,
            'miss_count': self.miss_count,
            'hit_rate': round(hit_rate, 2),
            'expired_count': len([
                key for key in self.expire_times.keys() 
                if self._is_expired(key)
            ])
        }
    
    def set_analysis_result(self, video_id: str, page: int, analysis_result: Dict[str, Any], 
                          ttl: Optional[int] = None) -> None:
        """
        缓存分析结果
        
        Args:
            video_id: 视频ID (BV号或AV号)
            page: 分P号
            analysis_result: 分析结果
            ttl: 生存时间（秒）
        """
        cache_key = f"analysis:{video_id}:page{page}"
        # 分析结果默认缓存2小时
        analysis_ttl = ttl if ttl is not None else 7200
        self.set(cache_key, analysis_result, analysis_ttl)
    
    def get_analysis_result(self, video_id: str, page: int) -> Optional[Dict[str, Any]]:
        """
        获取缓存的分析结果
        
        Args:
            video_id: 视频ID
            page: 分P号
            
        Returns:
            分析结果或None
        """
        cache_key = f"analysis:{video_id}:page{page}"
        return self.get(cache_key)
    
    def set_danmaku_data(self, video_id: str, page: int, use_protobuf: bool, 
                        danmaku_data: list, ttl: Optional[int] = None) -> None:
        """
        缓存弹幕数据
        
        Args:
            video_id: 视频ID
            page: 分P号
            use_protobuf: 是否使用protobuf接口
            danmaku_data: 弹幕数据
            ttl: 生存时间（秒）
        """
        interface_type = "protobuf" if use_protobuf else "xml"
        cache_key = f"danmaku:{video_id}:page{page}:{interface_type}"
        # 弹幕数据默认缓存30分钟
        danmaku_ttl = ttl if ttl is not None else 1800
        self.set(cache_key, danmaku_data, danmaku_ttl)
    
    def get_danmaku_data(self, video_id: str, page: int, use_protobuf: bool) -> Optional[list]:
        """
        获取缓存的弹幕数据
        
        Args:
            video_id: 视频ID
            page: 分P号
            use_protobuf: 是否使用protobuf接口
            
        Returns:
            弹幕数据或None
        """
        interface_type = "protobuf" if use_protobuf else "xml"
        cache_key = f"danmaku:{video_id}:page{page}:{interface_type}"
        return self.get(cache_key)
    
    def set_video_info(self, video_id: str, video_info: Dict[str, Any], 
                      ttl: Optional[int] = None) -> None:
        """
        缓存视频信息
        
        Args:
            video_id: 视频ID
            video_info: 视频信息
            ttl: 生存时间（秒）
        """
        cache_key = f"video_info:{video_id}"
        # 视频信息默认缓存10分钟
        info_ttl = ttl if ttl is not None else 600
        self.set(cache_key, video_info, info_ttl)
    
    def get_video_info(self, video_id: str) -> Optional[Dict[str, Any]]:
        """
        获取缓存的视频信息
        
        Args:
            video_id: 视频ID
            
        Returns:
            视频信息或None
        """
        cache_key = f"video_info:{video_id}"
        return self.get(cache_key)
    
    def get_cache_keys_by_prefix(self, prefix: str) -> list:
        """
        获取指定前缀的所有缓存键
        
        Args:
            prefix: 键前缀
            
        Returns:
            匹配的键列表
        """
        self._cleanup_expired()
        return [key for key in self.cache.keys() if key.startswith(prefix)]
    
    def remove_by_prefix(self, prefix: str) -> int:
        """
        删除指定前缀的所有缓存项
        
        Args:
            prefix: 键前缀
            
        Returns:
            删除的项目数量
        """
        keys_to_remove = self.get_cache_keys_by_prefix(prefix)
        for key in keys_to_remove:
            self.remove(key)
        
        logger.info(f"删除了{len(keys_to_remove)}个缓存项，前缀: {prefix}")
        return len(keys_to_remove)


# 全局缓存实例
data_cache = DataCache()