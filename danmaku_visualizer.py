"""
Bilibili弹幕数据可视化模块
提供词云、时间分布图、情感分析图等可视化功能
"""

import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from wordcloud import WordCloud
from typing import List, Dict, Tuple, Optional
import streamlit as st
from io import BytesIO
import base64


class DanmakuVisualizer:
    """弹幕数据可视化器"""
    
    def __init__(self):
        # 设置中文字体
        plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'DejaVu Sans']
        plt.rcParams['axes.unicode_minus'] = False
        
        # 设置颜色主题
        self.colors = {
            'primary': '#00A6D6',
            'secondary': '#FF6B9D', 
            'success': '#4CAF50',
            'warning': '#FF9800',
            'danger': '#F44336',
            'info': '#2196F3',
            'light': '#F5F5F5',
            'dark': '#333333'
        }
        
        # 设置图表样式
        sns.set_style("whitegrid")
        sns.set_palette("husl")
    
    def create_wordcloud(self, keywords: List[Tuple[str, int]], width: int = 800, height: int = 400) -> WordCloud:
        """
        创建词云图
        
        Args:
            keywords: 关键词和频次列表
            width: 图片宽度
            height: 图片高度
            
        Returns:
            WordCloud: 词云对象
        """
        if not keywords:
            return None
        
        # 构建词频字典
        word_freq = dict(keywords)
        
        # 创建词云
        wordcloud = WordCloud(
            width=width,
            height=height,
            background_color='white',
            font_path='simhei.ttf',  # 中文字体路径，可能需要调整
            max_words=100,
            colormap='viridis',
            relative_scaling=0.5,
            random_state=42
        ).generate_from_frequencies(word_freq)
        
        return wordcloud
    
    def plot_wordcloud_matplotlib(self, keywords: List[Tuple[str, int]]) -> plt.Figure:
        """
        使用matplotlib绘制词云图
        
        Args:
            keywords: 关键词和频次列表
            
        Returns:
            plt.Figure: matplotlib图形对象
        """
        wordcloud = self.create_wordcloud(keywords)
        
        if wordcloud is None:
            fig, ax = plt.subplots(figsize=(10, 6))
            ax.text(0.5, 0.5, '没有足够的数据生成词云', ha='center', va='center', fontsize=16)
            ax.set_xlim(0, 1)
            ax.set_ylim(0, 1)
            ax.axis('off')
            return fig
        
        fig, ax = plt.subplots(figsize=(12, 8))
        ax.imshow(wordcloud, interpolation='bilinear')
        ax.axis('off')
        ax.set_title('弹幕词云图', fontsize=16, fontweight='bold', pad=20)
        
        plt.tight_layout()
        return fig
    
    def plot_sentiment_pie(self, sentiment_data: Dict[str, float]) -> go.Figure:
        """
        绘制情感分析饼图
        
        Args:
            sentiment_data: 情感分析数据
            
        Returns:
            go.Figure: plotly图形对象
        """
        labels = ['积极', '消极', '中性']
        values = [
            sentiment_data.get('positive', 0),
            sentiment_data.get('negative', 0),
            sentiment_data.get('neutral', 0)
        ]
        colors = [self.colors['success'], self.colors['danger'], self.colors['info']]
        
        fig = go.Figure(data=[go.Pie(
            labels=labels,
            values=values,
            hole=0.3,
            marker_colors=colors,
            textinfo='label+percent',
            textfont_size=12
        )])
        
        fig.update_layout(
            title={
                'text': '弹幕情感分析',
                'x': 0.5,
                'xanchor': 'center',
                'font': {'size': 18}
            },
            showlegend=True,
            height=400
        )
        
        return fig
    
    def plot_time_distribution(self, time_data: List[Dict]) -> go.Figure:
        """
        绘制时间分布图
        
        Args:
            time_data: 时间分布数据
            
        Returns:
            go.Figure: plotly图形对象
        """
        if not time_data:
            fig = go.Figure()
            fig.add_annotation(
                text="没有时间分布数据",
                xref="paper", yref="paper",
                x=0.5, y=0.5, xanchor='center', yanchor='middle',
                showarrow=False, font=dict(size=16)
            )
            return fig
        
        df = pd.DataFrame(time_data)
        
        # 格式化时间显示
        df['time_label'] = df['time_start'].apply(self._format_time)
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=df['time_start'],
            y=df['count'],
            mode='lines+markers',
            name='弹幕数量',
            line=dict(color=self.colors['primary'], width=2),
            marker=dict(size=6),
            hovertemplate='时间: %{customdata}<br>弹幕数: %{y}<extra></extra>',
            customdata=df['time_label']
        ))
        
        fig.update_layout(
            title={
                'text': '弹幕时间分布',
                'x': 0.5,
                'xanchor': 'center',
                'font': {'size': 18}
            },
            xaxis_title='时间 (秒)',
            yaxis_title='弹幕数量',
            hovermode='x unified',
            height=400
        )
        
        return fig
    
    def plot_keywords_bar(self, keywords: List[Tuple[str, int]], top_n: int = 15) -> go.Figure:
        """
        绘制关键词柱状图
        
        Args:
            keywords: 关键词和频次列表
            top_n: 显示前N个关键词
            
        Returns:
            go.Figure: plotly图形对象
        """
        if not keywords:
            fig = go.Figure()
            fig.add_annotation(
                text="没有关键词数据",
                xref="paper", yref="paper",
                x=0.5, y=0.5, xanchor='center', yanchor='middle',
                showarrow=False, font=dict(size=16)
            )
            return fig
        
        # 取前N个关键词
        top_keywords = keywords[:top_n]
        words, counts = zip(*top_keywords)
        
        fig = go.Figure(data=[
            go.Bar(
                x=list(counts),
                y=list(words),
                orientation='h',
                marker_color=self.colors['secondary'],
                text=counts,
                textposition='outside'
            )
        ])
        
        fig.update_layout(
            title={
                'text': f'热门关键词 Top {len(top_keywords)}',
                'x': 0.5,
                'xanchor': 'center',
                'font': {'size': 18}
            },
            xaxis_title='出现次数',
            yaxis_title='关键词',
            height=max(400, len(top_keywords) * 25),
            yaxis={'categoryorder': 'total ascending'}
        )
        
        return fig
    
    def plot_length_distribution(self, length_stats: Dict[str, float]) -> go.Figure:
        """
        绘制弹幕长度分布图
        
        Args:
            length_stats: 长度统计数据
            
        Returns:
            go.Figure: plotly图形对象
        """
        if not length_stats:
            fig = go.Figure()
            fig.add_annotation(
                text="没有长度统计数据",
                xref="paper", yref="paper",
                x=0.5, y=0.5, xanchor='center', yanchor='middle',
                showarrow=False, font=dict(size=16)
            )
            return fig
        
        metrics = ['平均长度', '中位数长度', '最大长度', '最小长度']
        values = [
            length_stats.get('mean_length', 0),
            length_stats.get('median_length', 0),
            length_stats.get('max_length', 0),
            length_stats.get('min_length', 0)
        ]
        
        fig = go.Figure(data=[
            go.Bar(
                x=metrics,
                y=values,
                marker_color=[self.colors['primary'], self.colors['info'], 
                             self.colors['warning'], self.colors['success']],
                text=[f'{v:.1f}' for v in values],
                textposition='outside'
            )
        ])
        
        fig.update_layout(
            title={
                'text': '弹幕长度分布统计',
                'x': 0.5,
                'xanchor': 'center',
                'font': {'size': 18}
            },
            xaxis_title='统计指标',
            yaxis_title='字符数',
            height=400
        )
        
        return fig
    
    def plot_hot_moments(self, hot_moments: List[Dict]) -> go.Figure:
        """
        绘制热点时刻图
        
        Args:
            hot_moments: 热点时刻数据
            
        Returns:
            go.Figure: plotly图形对象
        """
        if not hot_moments:
            fig = go.Figure()
            fig.add_annotation(
                text="没有热点时刻数据",
                xref="paper", yref="paper",
                x=0.5, y=0.5, xanchor='center', yanchor='middle',
                showarrow=False, font=dict(size=16)
            )
            return fig
        
        # 准备数据
        times = []
        counts = []
        labels = []
        
        for moment in hot_moments[:10]:  # 只显示前10个
            time_start = moment['time_start']
            count = moment['count']
            sample_text = '、'.join(moment['sample_danmaku'][:3])
            
            times.append(time_start)
            counts.append(count)
            labels.append(f"{self._format_time(time_start)}: {sample_text[:50]}...")
        
        fig = go.Figure(data=[
            go.Scatter(
                x=times,
                y=counts,
                mode='markers',
                marker=dict(
                    size=[c/max(counts)*50 + 10 for c in counts],  # 根据弹幕数量调整点的大小
                    color=counts,
                    colorscale='Reds',
                    showscale=True,
                    colorbar=dict(title="弹幕数量")
                ),
                text=labels,
                hovertemplate='%{text}<br>弹幕数: %{y}<extra></extra>'
            )
        ])
        
        fig.update_layout(
            title={
                'text': '弹幕热点时刻',
                'x': 0.5,
                'xanchor': 'center',
                'font': {'size': 18}
            },
            xaxis_title='时间 (秒)',
            yaxis_title='弹幕数量',
            height=400
        )
        
        return fig
    
    def _format_time(self, seconds: float) -> str:
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
    
    def create_dashboard(self, analysis_result: Dict) -> Dict[str, go.Figure]:
        """
        创建完整的分析仪表板
        
        Args:
            analysis_result: 分析结果数据
            
        Returns:
            Dict[str, go.Figure]: 包含所有图表的字典
        """
        figures = {}
        
        # 情感分析饼图
        if 'sentiment' in analysis_result:
            figures['sentiment'] = self.plot_sentiment_pie(analysis_result['sentiment'])
        
        # 关键词柱状图
        if 'keywords' in analysis_result:
            figures['keywords'] = self.plot_keywords_bar(analysis_result['keywords'])
        
        # 时间分布图
        if 'time_distribution' in analysis_result:
            figures['time_distribution'] = self.plot_time_distribution(analysis_result['time_distribution'])
        
        # 长度分布图
        if 'length_stats' in analysis_result:
            figures['length_distribution'] = self.plot_length_distribution(analysis_result['length_stats'])
        
        # 热点时刻图
        if 'hot_moments' in analysis_result:
            figures['hot_moments'] = self.plot_hot_moments(analysis_result['hot_moments'])
        
        return figures


# 便捷函数
def create_visualizations(analysis_result: Dict) -> Dict[str, go.Figure]:
    """
    便捷函数：创建可视化图表
    
    Args:
        analysis_result: 分析结果
        
    Returns:
        Dict[str, go.Figure]: 图表字典
    """
    visualizer = DanmakuVisualizer()
    return visualizer.create_dashboard(analysis_result)
