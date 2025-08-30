"""
Bilibili弹幕获取模块
支持从Bilibili API获取弹幕数据，包括protobuf和xml两种格式
"""

import asyncio
import re
import os
import tempfile
from typing import List, Dict, Optional, Union
from datetime import datetime, date
import pandas as pd

from bilibili_api import video, ass, sync
from bilibili_api.exceptions import *
from config import config, NetworkException, ValidationException


class DanmakuFetcher:
    """Bilibili弹幕获取器"""
    
    def __init__(self):
        self.video_obj = None
        self.bv_id = None
        
    def extract_bv_id(self, url_or_bv: str) -> str:
        """
        从URL或直接输入中提取BV号
        
        Args:
            url_or_bv: Bilibili视频URL或BV号
            
        Returns:
            str: BV号
            
        Raises:
            ValueError: 无效的URL或BV号
        """
        # 如果直接是BV号
        if url_or_bv.startswith('BV'):
            return url_or_bv
            
        # 从URL中提取BV号
        patterns = [
            r'bilibili\.com/video/(BV[a-zA-Z0-9]+)',
            r'b23\.tv/([a-zA-Z0-9]+)',
            r'(BV[a-zA-Z0-9]+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url_or_bv)
            if match:
                bv_id = match.group(1)
                if bv_id.startswith('BV'):
                    return bv_id
                    
        raise ValueError(f"无法从输入中提取有效的BV号: {url_or_bv}")
    
    def initialize_video(self, url_or_bv: str) -> bool:
        """
        初始化视频对象
        
        Args:
            url_or_bv: Bilibili视频URL或BV号
            
        Returns:
            bool: 是否成功初始化
        """
        try:
            self.bv_id = self.extract_bv_id(url_or_bv)
            self.video_obj = video.Video(self.bv_id)
            return True
        except Exception as e:
            print(f"初始化视频对象失败: {e}")
            return False
    
    async def get_video_info(self) -> Dict:
        """
        获取视频基本信息
        
        Returns:
            Dict: 视频信息
        """
        if not self.video_obj:
            raise ValueError("视频对象未初始化")
            
        try:
            info = await self.video_obj.get_info()
            return {
                'title': info.get('title', ''),
                'desc': info.get('desc', ''),
                'duration': info.get('duration', 0),
                'view': info.get('stat', {}).get('view', 0),
                'danmaku': info.get('stat', {}).get('danmaku', 0),
                'like': info.get('stat', {}).get('like', 0),
                'coin': info.get('stat', {}).get('coin', 0),
                'favorite': info.get('stat', {}).get('favorite', 0),
                'share': info.get('stat', {}).get('share', 0),
                'pubdate': info.get('pubdate', 0),
                'pages': len(info.get('pages', []))
            }
        except Exception as e:
            print(f"获取视频信息失败: {e}")
            return {}
    
    async def _fetch_danmaku_with_ass(self, ass_generator_func, page: int = 0, date_filter: Optional[date] = None, interface_type: str = "unknown") -> List[Dict]:
        """
        使用ASS文件方式获取弹幕数据的通用方法
        
        Args:
            ass_generator_func: ASS文件生成函数
            page: 分P号，从0开始
            date_filter: 日期过滤器（仅protobuf接口使用）
            interface_type: 接口类型，用于错误提示
            
        Returns:
            List[Dict]: 弹幕数据列表
        """
        if not self.video_obj:
            raise ValueError("视频对象未初始化")
            
        temp_path = None
        try:
            # 创建临时文件
            with tempfile.NamedTemporaryFile(mode='w', suffix='.ass', delete=False, encoding='utf-8') as temp_file:
                temp_path = temp_file.name
            
            # 根据接口类型调用不同的ASS生成函数
            if date_filter is not None:  # protobuf接口支持日期过滤
                await ass_generator_func(
                    obj=self.video_obj,
                    page=page,
                    out=temp_path,
                    date=date_filter
                )
            else:  # XML接口不支持日期过滤
                await ass_generator_func(
                    obj=self.video_obj,
                    page=page,
                    out=temp_path
                )
            
            # 解析ASS文件获取弹幕数据
            danmaku_list = self._parse_ass_file(temp_path)
            
            return danmaku_list
            
        except Exception as e:
            print(f"获取{interface_type}弹幕失败: {e}")
            return []
        finally:
            # 确保清理临时文件
            if temp_path and os.path.exists(temp_path):
                try:
                    os.unlink(temp_path)
                except Exception as cleanup_error:
                    print(f"清理临时文件失败: {cleanup_error}")

    async def fetch_danmaku_protobuf(self, page: int = 0, date_filter: Optional[date] = None) -> List[Dict]:
        """
        使用protobuf接口获取弹幕数据
        
        Args:
            page: 分P号，从0开始
            date_filter: 日期过滤器
            
        Returns:
            List[Dict]: 弹幕数据列表
        """
        return await self._fetch_danmaku_with_ass(
            ass_generator_func=ass.make_ass_file_danmakus_protobuf,
            page=page,
            date_filter=date_filter,
            interface_type="protobuf"
        )
    
    async def fetch_danmaku_xml(self, page: int = 0) -> List[Dict]:
        """
        使用XML接口获取弹幕数据
        
        Args:
            page: 分P号，从0开始
            
        Returns:
            List[Dict]: 弹幕数据列表
        """
        return await self._fetch_danmaku_with_ass(
            ass_generator_func=ass.make_ass_file_danmakus_xml,
            page=page,
            date_filter=None,  # XML接口不支持日期过滤
            interface_type="XML"
        )
    
    def _parse_ass_file(self, file_path: str) -> List[Dict]:
        """
        解析ASS文件获取弹幕数据
        
        Args:
            file_path: ASS文件路径
            
        Returns:
            List[Dict]: 弹幕数据列表
        """
        danmaku_list = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 解析ASS格式的弹幕
            lines = content.split('\n')
            for line in lines:
                if line.startswith('Dialogue:'):
                    parts = line.split(',', 9)
                    if len(parts) >= 10:
                        # 提取时间和文本
                        start_time = parts[1]
                        end_time = parts[2]
                        text = parts[9].strip()
                        
                        # 清理文本中的ASS标签
                        text = re.sub(r'\{[^}]*\}', '', text)
                        
                        if text:
                            danmaku_list.append({
                                'time': start_time,
                                'text': text,
                                'timestamp': self._time_to_seconds(start_time)
                            })
                            
        except Exception as e:
            print(f"解析ASS文件失败: {e}")
            
        return danmaku_list
    
    def _time_to_seconds(self, time_str: str) -> float:
        """
        将时间字符串转换为秒数
        
        Args:
            time_str: 时间字符串 (格式: H:MM:SS.ss)
            
        Returns:
            float: 秒数
        """
        try:
            parts = time_str.split(':')
            hours = int(parts[0])
            minutes = int(parts[1])
            seconds = float(parts[2])
            return hours * 3600 + minutes * 60 + seconds
        except (ValueError, IndexError) as e:
            # 处理时间格式错误或分割失败的情况
            print(f"时间格式转换失败: {time_str}, 错误: {e}")
            return 0.0
    
    def get_danmaku_sync(self, url_or_bv: str, page: int = 0, use_protobuf: bool = True, date_filter: Optional[date] = None) -> List[Dict]:
        """
        同步方式获取弹幕数据
        
        Args:
            url_or_bv: Bilibili视频URL或BV号
            page: 分P号，从0开始
            use_protobuf: 是否使用protobuf接口
            date_filter: 日期过滤器
            
        Returns:
            List[Dict]: 弹幕数据列表
        """
        if not self.initialize_video(url_or_bv):
            return []
        
        try:
            if use_protobuf:
                return sync(self.fetch_danmaku_protobuf(page, date_filter))
            else:
                return sync(self.fetch_danmaku_xml(page))
        except Exception as e:
            print(f"获取弹幕数据失败: {e}")
            return []
    
    def get_video_info_sync(self, url_or_bv: str) -> Dict:
        """
        同步方式获取视频信息
        
        Args:
            url_or_bv: Bilibili视频URL或BV号
            
        Returns:
            Dict: 视频信息
        """
        if not self.initialize_video(url_or_bv):
            return {}
        
        try:
            return sync(self.get_video_info())
        except Exception as e:
            print(f"获取视频信息失败: {e}")
            return {}


# 便捷函数
def fetch_danmaku(url_or_bv: str, page: int = 0, use_protobuf: bool = True, date_filter: Optional[date] = None) -> List[Dict]:
    """
    便捷函数：获取弹幕数据
    
    Args:
        url_or_bv: Bilibili视频URL或BV号
        page: 分P号，从0开始
        use_protobuf: 是否使用protobuf接口
        date_filter: 日期过滤器
        
    Returns:
        List[Dict]: 弹幕数据列表
    """
    fetcher = DanmakuFetcher()
    return fetcher.get_danmaku_sync(url_or_bv, page, use_protobuf, date_filter)


def fetch_video_info(url_or_bv: str) -> Dict:
    """
    便捷函数：获取视频信息
    
    Args:
        url_or_bv: Bilibili视频URL或BV号
        
    Returns:
        Dict: 视频信息
    """
    fetcher = DanmakuFetcher()
    return fetcher.get_video_info_sync(url_or_bv)
