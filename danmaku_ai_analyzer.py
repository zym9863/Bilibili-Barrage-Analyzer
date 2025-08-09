"""
Bilibili弹幕AI分析模块
使用Pollinations API进行智能分析
"""

import requests
import urllib.parse
import json
import time
from typing import List, Dict, Optional
import streamlit as st


class DanmakuAIAnalyzer:
    """弹幕AI分析器"""
    
    def __init__(self):
        self.base_url = "https://text.pollinations.ai"
        self.default_params = {
            "model": "openai",
            "seed": 42,
        }
    
    def _call_ai_api(self, prompt: str, system_prompt: str = None, max_retries: int = 3) -> str:
        """
        调用Pollinations AI API
        
        Args:
            prompt: 用户提示词
            system_prompt: 系统提示词
            max_retries: 最大重试次数
            
        Returns:
            str: AI分析结果
        """
        encoded_prompt = urllib.parse.quote(prompt)
        url = f"{self.base_url}/{encoded_prompt}"
        
        # 设置请求参数
        params = self.default_params.copy()
        if system_prompt:
            params["system"] = system_prompt
        
        for attempt in range(max_retries):
            try:
                response = requests.get(url, params=params, timeout=30)
                response.raise_for_status()
                return response.text.strip()
                
            except requests.exceptions.RequestException as e:
                if attempt == max_retries - 1:
                    raise Exception(f"API调用失败: {str(e)}")
                time.sleep(2 ** attempt)  # 指数退避
        
        return ""
    
    def analyze_sentiment_ai(self, danmaku_texts: List[str], sample_size: int = 50) -> Dict:
        """
        使用AI进行情感分析
        
        Args:
            danmaku_texts: 弹幕文本列表
            sample_size: 采样大小
            
        Returns:
            Dict: AI情感分析结果
        """
        if not danmaku_texts:
            return {"error": "没有弹幕数据"}
        
        # 采样弹幕（避免过长的请求）
        sample_texts = danmaku_texts[:sample_size] if len(danmaku_texts) > sample_size else danmaku_texts
        
        # 构建提示词
        danmaku_sample = "\n".join([f"- {text}" for text in sample_texts])
        
        prompt = f"""请分析以下弹幕的整体情感倾向和观众反应：

弹幕内容：
{danmaku_sample}

请从以下几个维度进行分析：
1. 整体情感倾向（积极/消极/中性的比例）
2. 主要情绪类型（兴奋、惊讶、感动、不满等）
3. 观众反应特点
4. 热门话题或关注点

请用中文回答，格式简洁明了。"""

        system_prompt = "你是一个专业的弹幕情感分析师，能够准确识别中文弹幕中的情感倾向和观众反应。"
        
        try:
            result = self._call_ai_api(prompt, system_prompt)
            return {"analysis": result, "sample_count": len(sample_texts)}
        except Exception as e:
            return {"error": f"AI情感分析失败: {str(e)}"}
    
    def analyze_content_themes_ai(self, danmaku_texts: List[str], sample_size: int = 100) -> Dict:
        """
        使用AI分析弹幕内容主题
        
        Args:
            danmaku_texts: 弹幕文本列表
            sample_size: 采样大小
            
        Returns:
            Dict: AI主题分析结果
        """
        if not danmaku_texts:
            return {"error": "没有弹幕数据"}
        
        # 采样弹幕
        sample_texts = danmaku_texts[:sample_size] if len(danmaku_texts) > sample_size else danmaku_texts
        
        # 构建提示词
        danmaku_sample = "\n".join([f"- {text}" for text in sample_texts])
        
        prompt = f"""请分析以下弹幕内容的主要话题和主题：

弹幕内容：
{danmaku_sample}

请从以下几个方面进行分析：
1. 主要讨论话题（按重要性排序）
2. 观众关注的重点内容
3. 出现频率较高的梗或流行语
4. 弹幕反映的视频内容特点
5. 观众群体特征分析

请用中文回答，条理清晰。"""

        system_prompt = "你是一个内容分析专家，擅长从弹幕中提取和总结主要话题、观众兴趣点和内容特征。"
        
        try:
            result = self._call_ai_api(prompt, system_prompt)
            return {"analysis": result, "sample_count": len(sample_texts)}
        except Exception as e:
            return {"error": f"AI主题分析失败: {str(e)}"}
    
    def analyze_hot_moments_ai(self, hot_moments: List[Dict]) -> Dict:
        """
        使用AI分析热点时刻
        
        Args:
            hot_moments: 热点时刻数据
            
        Returns:
            Dict: AI热点分析结果
        """
        if not hot_moments:
            return {"error": "没有热点时刻数据"}
        
        # 构建热点时刻信息
        moments_info = []
        for i, moment in enumerate(hot_moments[:5], 1):  # 取前5个热点
            time_start = self._format_time(moment['time_start'])
            sample_danmaku = "; ".join(moment['sample_danmaku'][:3])
            moments_info.append(f"热点{i}: {time_start} (弹幕数:{moment['count']}) - 样本弹幕: {sample_danmaku}")
        
        moments_text = "\n".join(moments_info)
        
        prompt = f"""请分析以下视频的弹幕热点时刻：

热点时刻信息：
{moments_text}

请分析：
1. 每个热点时刻可能对应的视频内容
2. 观众在这些时刻的主要反应
3. 热点形成的可能原因
4. 这些热点反映的视频特色
5. 对内容创作者的建议

请用中文回答，分析要有逻辑性。"""

        system_prompt = "你是一个视频内容分析专家，能够从弹幕热点数据中推断视频内容特点和观众反应模式。"
        
        try:
            result = self._call_ai_api(prompt, system_prompt)
            return {"analysis": result, "hot_moments_count": len(hot_moments)}
        except Exception as e:
            return {"error": f"AI热点分析失败: {str(e)}"}
    
    def generate_comprehensive_report_ai(self, analysis_result: Dict, danmaku_texts: List[str]) -> Dict:
        """
        生成综合AI分析报告
        
        Args:
            analysis_result: 基础分析结果
            danmaku_texts: 弹幕文本列表
            
        Returns:
            Dict: 综合AI分析报告
        """
        if not danmaku_texts:
            return {"error": "没有弹幕数据"}
        
        # 提取关键统计信息
        basic_stats = analysis_result.get('basic_stats', {})
        keywords = analysis_result.get('keywords', [])
        sentiment = analysis_result.get('sentiment', {})
        hot_moments = analysis_result.get('hot_moments', [])
        
        # 构建统计摘要
        stats_summary = f"""
基本统计：
- 总弹幕数：{basic_stats.get('total_count', 0)}
- 独特弹幕数：{basic_stats.get('unique_count', 0)}
- 重复率：{basic_stats.get('duplicate_rate', 0):.1%}

热门关键词：{', '.join([kw[0] for kw in keywords[:10]])}

情感分布：积极 {sentiment.get('positive', 0):.1%}, 消极 {sentiment.get('negative', 0):.1%}, 中性 {sentiment.get('neutral', 0):.1%}

热点时刻数：{len(hot_moments)}
"""
        
        # 弹幕样本
        sample_danmaku = danmaku_texts[:30] if len(danmaku_texts) > 30 else danmaku_texts
        danmaku_sample = "\n".join([f"- {text}" for text in sample_danmaku])
        
        prompt = f"""基于以下弹幕数据统计和样本，请生成一份专业的视频弹幕分析报告：

统计数据：
{stats_summary}

弹幕样本：
{danmaku_sample}

请生成一份包含以下内容的分析报告：
1. 视频内容推测和类型判断
2. 观众群体特征分析
3. 观众参与度和互动质量评估
4. 弹幕文化现象观察
5. 视频传播潜力和受欢迎程度分析
6. 对内容创作者的建议和改进方向

报告要求：
- 语言专业但易懂
- 结构清晰，分点叙述
- 基于数据进行合理推测
- 提供实用的建议"""

        system_prompt = "你是一个专业的新媒体内容分析师，擅长从弹幕数据中分析视频内容特点、观众行为和传播效果。"
        
        try:
            result = self._call_ai_api(prompt, system_prompt)
            return {
                "comprehensive_report": result,
                "stats_used": basic_stats,
                "sample_count": len(sample_danmaku)
            }
        except Exception as e:
            return {"error": f"AI综合分析失败: {str(e)}"}
    
    def _format_time(self, seconds: float) -> str:
        """格式化时间显示"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        
        if hours > 0:
            return f"{hours:02d}:{minutes:02d}:{secs:02d}"
        else:
            return f"{minutes:02d}:{secs:02d}"


# 便捷函数
def analyze_danmaku_with_ai(analysis_result: Dict, danmaku_texts: List[str]) -> Dict:
    """
    便捷函数：使用AI分析弹幕数据
    
    Args:
        analysis_result: 基础分析结果
        danmaku_texts: 弹幕文本列表
        
    Returns:
        Dict: AI分析结果
    """
    ai_analyzer = DanmakuAIAnalyzer()
    
    # 执行各种AI分析
    results = {}
    
    # 情感分析
    results['sentiment_ai'] = ai_analyzer.analyze_sentiment_ai(danmaku_texts)
    
    # 主题分析
    results['themes_ai'] = ai_analyzer.analyze_content_themes_ai(danmaku_texts)
    
    # 热点分析
    if analysis_result.get('hot_moments'):
        results['hot_moments_ai'] = ai_analyzer.analyze_hot_moments_ai(analysis_result['hot_moments'])
    
    # 综合报告
    results['comprehensive_ai'] = ai_analyzer.generate_comprehensive_report_ai(analysis_result, danmaku_texts)
    
    return results