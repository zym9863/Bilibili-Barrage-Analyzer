# -*- coding: utf-8 -*-
"""
配置文件管理模块
管理应用程序的所有配置项，包括停用词、情感词典、界面参数等
"""

import os
import json
from typing import Dict, List, Any, Optional

class Config:
    """应用程序配置管理类"""
    
    def __init__(self):
        """初始化配置"""
        self.config_file = "app_config.json"
        self._config = self._load_default_config()
        self._load_config_file()
    
    def _load_default_config(self) -> Dict[str, Any]:
        """加载默认配置"""
        return {
            "stop_words": [
                '的', '了', '在', '是', '我', '有', '和', '就', '不', '人', '都', '一', '个', '这',
                '没', '会', '么', '说', '把', '你', '也', '要', '到', '用', '他', '好', '那', '多',
                '能', '还', '时', '很', '看', '来', '只', '被', '对', '上', '去', '可', '两', '啊',
                '什', '吗', '吧', '吧', '还', '怎', '然', '呢', '这样', '但', '而', '或', '已经'
            ],
            "sentiment_words": {
                "positive": ["好", "棒", "赞", "牛", "优秀", "精彩", "厉害", "给力", "完美", "喜欢"],
                "negative": ["差", "烂", "垃圾", "无聊", "失望", "讨厌", "难看", "糟糕", "不行", "坑"]
            },
            "ui_settings": {
                "time_interval_min": 10,
                "time_interval_max": 100,
                "time_interval_default": 60,
                "keyword_count_min": 10,
                "keyword_count_max": 100,
                "keyword_count_default": 30
            },
            "network_settings": {
                "timeout": 30,
                "max_retries": 3,
                "retry_delay": 1,
                "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            },
            "analysis_settings": {
                "max_danmaku_count": 10000,
                "min_keyword_length": 2,
                "wordcloud_width": 800,
                "wordcloud_height": 400
            },
            "ui_display_settings": {
                # 进度条进度值
                "progress_fetch_data": 20,
                "progress_analyze_data": 40,
                "progress_ai_analysis": 60,
                "progress_visualization": 80,
                "progress_complete": 100,
                
                # 数据显示限制
                "hot_moments_display_limit": 5,
                "sample_danmaku_display_limit": 3,
                "dataframe_preview_rows": 10,
                
                # 页面布局
                "video_info_columns": [2, 1, 1],
                "hot_moment_detail_columns": [1, 3],
                "main_columns_count": 2,
                "stats_columns_count": 4,
                
                # 数字格式化阈值
                "number_format_billion_threshold": 100000000,  # 1亿
                "number_format_wan_threshold": 10000,  # 1万
                
                # 时间格式化阈值
                "time_format_hour_threshold": 3600,  # 1小时
                "time_format_minute_threshold": 60,   # 1分钟
                
                # 界面延时
                "progress_complete_delay": 1  # 完成后延迟秒数
            }
        }
    
    def _load_config_file(self):
        """从配置文件加载配置"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    file_config = json.load(f)
                    self._config.update(file_config)
            except (json.JSONDecodeError, IOError) as e:
                print(f"加载配置文件失败: {e}，使用默认配置")
    
    def save_config(self):
        """保存配置到文件"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self._config, f, ensure_ascii=False, indent=4)
        except IOError as e:
            print(f"保存配置文件失败: {e}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """获取配置值"""
        keys = key.split('.')
        value = self._config
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        return value
    
    def set(self, key: str, value: Any):
        """设置配置值"""
        keys = key.split('.')
        config = self._config
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        config[keys[-1]] = value
    
    @property
    def stop_words(self) -> List[str]:
        """获取停用词列表"""
        return self.get('stop_words', [])
    
    @property
    def positive_words(self) -> List[str]:
        """获取积极情感词列表"""
        return self.get('sentiment_words.positive', [])
    
    @property
    def negative_words(self) -> List[str]:
        """获取消极情感词列表"""
        return self.get('sentiment_words.negative', [])
    
    @property
    def ui_settings(self) -> Dict[str, int]:
        """获取UI设置"""
        return self.get('ui_settings', {})
    
    @property
    def network_settings(self) -> Dict[str, Any]:
        """获取网络设置"""
        return self.get('network_settings', {})
    
    @property
    def analysis_settings(self) -> Dict[str, Any]:
        """获取分析设置"""
        return self.get('analysis_settings', {})
    
    @property
    def ui_display_settings(self) -> Dict[str, Any]:
        """获取UI显示设置"""
        return self.get('ui_display_settings', {})


# 全局配置实例
config = Config()


class CustomException(Exception):
    """自定义异常基类"""
    def __init__(self, message: str, error_code: Optional[str] = None):
        self.message = message
        self.error_code = error_code
        super().__init__(self.message)


class NetworkException(CustomException):
    """网络相关异常"""
    pass


class DataProcessingException(CustomException):
    """数据处理相关异常"""
    pass


class ValidationException(CustomException):
    """数据验证异常"""
    pass