"""
测试AI分析功能的脚本
"""

import sys
import os

# 添加当前目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from danmaku_ai_analyzer import DanmakuAIAnalyzer

def test_ai_analyzer():
    """测试AI分析器"""
    print("🤖 测试AI分析功能...")
    
    # 创建测试数据
    test_danmaku_texts = [
        "这个视频太好看了！",
        "哈哈哈笑死我了",
        "主播好厉害啊",
        "666666",
        "这操作牛逼",
        "爱了爱了",
        "太感动了",
        "这是什么神仙视频",
        "弹幕护体",
        "前方高能预警"
    ]
    
    test_analysis_result = {
        'basic_stats': {'total_count': 100, 'unique_count': 80, 'duplicate_rate': 0.2},
        'keywords': [('好看', 10), ('厉害', 8), ('666', 6)],
        'sentiment': {'positive': 0.7, 'negative': 0.1, 'neutral': 0.2},
        'hot_moments': [
            {
                'time_start': 60,
                'time_end': 90,
                'count': 25,
                'sample_danmaku': ['太好看了', '666', '哈哈哈']
            }
        ]
    }
    
    # 创建AI分析器
    ai_analyzer = DanmakuAIAnalyzer()
    
    # 测试情感分析
    print("\n📊 测试AI情感分析...")
    try:
        sentiment_result = ai_analyzer.analyze_sentiment_ai(test_danmaku_texts, sample_size=5)
        if 'analysis' in sentiment_result:
            print("✅ AI情感分析成功")
            print(f"分析结果: {sentiment_result['analysis'][:100]}...")
        else:
            print(f"❌ AI情感分析失败: {sentiment_result.get('error', '未知错误')}")
    except Exception as e:
        print(f"❌ AI情感分析异常: {str(e)}")
    
    # 测试主题分析
    print("\n🎯 测试AI主题分析...")
    try:
        theme_result = ai_analyzer.analyze_content_themes_ai(test_danmaku_texts, sample_size=5)
        if 'analysis' in theme_result:
            print("✅ AI主题分析成功")
            print(f"分析结果: {theme_result['analysis'][:100]}...")
        else:
            print(f"❌ AI主题分析失败: {theme_result.get('error', '未知错误')}")
    except Exception as e:
        print(f"❌ AI主题分析异常: {str(e)}")
    
    # 测试热点分析
    print("\n🔥 测试AI热点分析...")
    try:
        hot_result = ai_analyzer.analyze_hot_moments_ai(test_analysis_result['hot_moments'])
        if 'analysis' in hot_result:
            print("✅ AI热点分析成功")
            print(f"分析结果: {hot_result['analysis'][:100]}...")
        else:
            print(f"❌ AI热点分析失败: {hot_result.get('error', '未知错误')}")
    except Exception as e:
        print(f"❌ AI热点分析异常: {str(e)}")
    
    print("\n🎉 AI分析功能测试完成!")

if __name__ == "__main__":
    test_ai_analyzer()