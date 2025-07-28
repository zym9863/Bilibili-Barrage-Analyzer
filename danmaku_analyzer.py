"""
Bilibili弹幕数据分析模块
提供词频统计、情感分析、时间分布分析等功能
"""

import re
import jieba
import pandas as pd
import numpy as np
from collections import Counter
from typing import List, Dict, Tuple, Optional
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import seaborn as sns
from wordcloud import WordCloud


class DanmakuAnalyzer:
    """弹幕数据分析器"""
    
    def __init__(self):
        # 设置中文字体
        plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'DejaVu Sans']
        plt.rcParams['axes.unicode_minus'] = False
        
        # 停用词列表
        self.stop_words = {
            '的', '了', '在', '是', '我', '有', '和', '就', '不', '人', '都', '一', '一个', '上', '也', '很', '到', '说', '要', '去', '你', '会', '着', '没有', '看', '好', '自己', '这', '那', '来', '可以', '时候', '什么', '这个', '那个', '这样', '那样', '现在', '知道', '只是', '还是', '比较', '觉得', '应该', '可能', '已经', '如果', '因为', '所以', '但是', '虽然', '然后', '或者', '而且', '不过', '当然', '其实', '确实', '真的', '哈哈', '呵呵', '嘿嘿', '哇', '啊', '呀', '哦', '嗯', '额', '吧', '呢', '吗', '哟', '咦', '唉', '哎', '嗨', '喂', '嘛', '呗', '咯', '啦', '哪', '怎么', '为什么', '多少', '几个', '什么时候', '哪里', '怎样', '如何'
        }
        
        # 情感词典（简化版）
        self.positive_words = {
            '好', '棒', '赞', '牛', '厉害', '优秀', '精彩', '完美', '漂亮', '帅', '美', '爱', '喜欢', '开心', '高兴', '快乐', '幸福', '满意', '惊艳', '震撼', '感动', '温暖', '治愈', '可爱', '萌', '有趣', '搞笑', '幽默', '机智', '聪明', '天才', '神', '绝了', '太好了', '太棒了', '太牛了', '666', '6666', '牛逼', 'nb', 'yyds', '永远的神', '绝绝子', '爱了爱了', '慕了', '羡慕', '佩服', '崇拜', '膜拜', '跪了', '服了', '强', '猛', '狠', '顶', '支持', '加油', '冲', '奥利给'
        }
        
        self.negative_words = {
            '差', '烂', '垃圾', '糟糕', '失望', '无聊', '难看', '丑', '讨厌', '恶心', '恶心', '烦', '气', '怒', '愤怒', '生气', '郁闷', '沮丧', '难过', '伤心', '痛苦', '绝望', '崩溃', '抑郁', '焦虑', '害怕', '恐惧', '担心', '紧张', '尴尬', '羞耻', '后悔', '遗憾', '可惜', '浪费', '白费', '没用', '无用', '废物', '智障', '脑残', '傻', '蠢', '笨', '白痴', '弱智', '低能', '菜', '辣鸡', '拉胯', '翻车', '凉了', '完了', '死了', '毁了', '坏了', '错了', '假的', '骗人', '骗子', '黑', '喷', '骂', '滚', '滚蛋', '去死', '闭嘴'
        }
    
    def clean_text(self, text: str) -> str:
        """
        清理文本数据
        
        Args:
            text: 原始文本
            
        Returns:
            str: 清理后的文本
        """
        # 移除特殊字符和数字
        text = re.sub(r'[^\u4e00-\u9fa5a-zA-Z\s]', '', text)
        # 移除多余空格
        text = re.sub(r'\s+', ' ', text).strip()
        return text
    
    def extract_keywords(self, texts: List[str], top_n: int = 50) -> List[Tuple[str, int]]:
        """
        提取关键词和词频
        
        Args:
            texts: 文本列表
            top_n: 返回前N个关键词
            
        Returns:
            List[Tuple[str, int]]: 关键词和频次的列表
        """
        all_words = []
        
        for text in texts:
            # 清理文本
            cleaned_text = self.clean_text(text)
            if not cleaned_text:
                continue
                
            # 分词
            words = jieba.lcut(cleaned_text)
            
            # 过滤停用词和短词
            filtered_words = [
                word for word in words 
                if len(word) >= 2 and word not in self.stop_words
            ]
            
            all_words.extend(filtered_words)
        
        # 统计词频
        word_counts = Counter(all_words)
        return word_counts.most_common(top_n)
    
    def analyze_sentiment(self, texts: List[str]) -> Dict[str, float]:
        """
        分析情感倾向
        
        Args:
            texts: 文本列表
            
        Returns:
            Dict[str, float]: 情感分析结果
        """
        positive_count = 0
        negative_count = 0
        neutral_count = 0
        
        for text in texts:
            cleaned_text = self.clean_text(text)
            words = jieba.lcut(cleaned_text)
            
            pos_score = sum(1 for word in words if word in self.positive_words)
            neg_score = sum(1 for word in words if word in self.negative_words)
            
            if pos_score > neg_score:
                positive_count += 1
            elif neg_score > pos_score:
                negative_count += 1
            else:
                neutral_count += 1
        
        total = len(texts)
        if total == 0:
            return {'positive': 0, 'negative': 0, 'neutral': 0}
        
        return {
            'positive': positive_count / total,
            'negative': negative_count / total,
            'neutral': neutral_count / total
        }
    
    def analyze_time_distribution(self, danmaku_data: List[Dict], interval_seconds: int = 60) -> pd.DataFrame:
        """
        分析弹幕时间分布
        
        Args:
            danmaku_data: 弹幕数据列表
            interval_seconds: 时间间隔（秒）
            
        Returns:
            pd.DataFrame: 时间分布数据
        """
        if not danmaku_data:
            return pd.DataFrame()
        
        # 创建DataFrame
        df = pd.DataFrame(danmaku_data)
        
        # 按时间间隔分组
        df['time_group'] = (df['timestamp'] // interval_seconds) * interval_seconds
        
        # 统计每个时间段的弹幕数量
        time_dist = df.groupby('time_group').agg({
            'text': 'count',
            'timestamp': 'mean'
        }).reset_index()
        
        time_dist.columns = ['time_start', 'count', 'time_avg']
        time_dist['time_end'] = time_dist['time_start'] + interval_seconds
        
        return time_dist
    
    def analyze_length_distribution(self, texts: List[str]) -> Dict[str, float]:
        """
        分析弹幕长度分布
        
        Args:
            texts: 文本列表
            
        Returns:
            Dict[str, float]: 长度分布统计
        """
        lengths = [len(text) for text in texts if text]
        
        if not lengths:
            return {}
        
        return {
            'mean_length': np.mean(lengths),
            'median_length': np.median(lengths),
            'max_length': np.max(lengths),
            'min_length': np.min(lengths),
            'std_length': np.std(lengths)
        }
    
    def find_hot_moments(self, danmaku_data: List[Dict], window_seconds: int = 30, threshold_percentile: int = 90) -> List[Dict]:
        """
        找出弹幕热点时刻
        
        Args:
            danmaku_data: 弹幕数据列表
            window_seconds: 时间窗口（秒）
            threshold_percentile: 阈值百分位数
            
        Returns:
            List[Dict]: 热点时刻列表
        """
        if not danmaku_data:
            return []
        
        # 创建DataFrame
        df = pd.DataFrame(danmaku_data)
        
        # 按时间窗口分组统计
        df['time_window'] = (df['timestamp'] // window_seconds) * window_seconds
        window_counts = df.groupby('time_window').size()
        
        # 计算阈值
        threshold = np.percentile(window_counts.values, threshold_percentile)
        
        # 找出热点时刻
        hot_moments = []
        for time_window, count in window_counts.items():
            if count >= threshold:
                # 获取该时间段的弹幕
                window_danmaku = df[df['time_window'] == time_window]['text'].tolist()
                
                hot_moments.append({
                    'time_start': time_window,
                    'time_end': time_window + window_seconds,
                    'count': count,
                    'sample_danmaku': window_danmaku[:5]  # 取前5条作为样本
                })
        
        # 按弹幕数量排序
        hot_moments.sort(key=lambda x: x['count'], reverse=True)
        
        return hot_moments
    
    def generate_summary_report(self, danmaku_data: List[Dict]) -> Dict:
        """
        生成弹幕分析总结报告
        
        Args:
            danmaku_data: 弹幕数据列表
            
        Returns:
            Dict: 分析报告
        """
        if not danmaku_data:
            return {'error': '没有弹幕数据'}
        
        texts = [item['text'] for item in danmaku_data if item.get('text')]
        
        # 基本统计
        total_count = len(danmaku_data)
        unique_count = len(set(texts))
        
        # 关键词分析
        keywords = self.extract_keywords(texts, 20)
        
        # 情感分析
        sentiment = self.analyze_sentiment(texts)
        
        # 长度分析
        length_stats = self.analyze_length_distribution(texts)
        
        # 时间分布
        time_dist = self.analyze_time_distribution(danmaku_data)
        
        # 热点时刻
        hot_moments = self.find_hot_moments(danmaku_data)
        
        return {
            'basic_stats': {
                'total_count': total_count,
                'unique_count': unique_count,
                'duplicate_rate': 1 - (unique_count / total_count) if total_count > 0 else 0
            },
            'keywords': keywords,
            'sentiment': sentiment,
            'length_stats': length_stats,
            'time_distribution': time_dist.to_dict('records') if not time_dist.empty else [],
            'hot_moments': hot_moments[:10]  # 取前10个热点时刻
        }
    
    def format_time(self, seconds: float) -> str:
        """
        格式化时间显示
        
        Args:
            seconds: 秒数
            
        Returns:
            str: 格式化的时间字符串
        """
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        
        if hours > 0:
            return f"{hours:02d}:{minutes:02d}:{secs:02d}"
        else:
            return f"{minutes:02d}:{secs:02d}"


# 便捷函数
def analyze_danmaku(danmaku_data: List[Dict]) -> Dict:
    """
    便捷函数：分析弹幕数据
    
    Args:
        danmaku_data: 弹幕数据列表
        
    Returns:
        Dict: 分析结果
    """
    analyzer = DanmakuAnalyzer()
    return analyzer.generate_summary_report(danmaku_data)
