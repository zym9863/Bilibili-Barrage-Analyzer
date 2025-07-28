"""
测试脚本 - 验证Bilibili弹幕分析器的核心功能
"""

import sys
import traceback
from datetime import date

# 导入自定义模块
from danmaku_fetcher import DanmakuFetcher, fetch_danmaku, fetch_video_info
from danmaku_analyzer import DanmakuAnalyzer, analyze_danmaku
from danmaku_visualizer import DanmakuVisualizer, create_visualizations


def test_bv_extraction():
    """测试BV号提取功能"""
    print("🧪 测试BV号提取功能...")
    
    fetcher = DanmakuFetcher()
    
    test_cases = [
        "BV1P24y1a7Lt",
        "https://www.bilibili.com/video/BV1P24y1a7Lt",
        "https://www.bilibili.com/video/BV1P24y1a7Lt?p=1",
        "https://b23.tv/BV1P24y1a7Lt"
    ]
    
    for test_case in test_cases:
        try:
            bv_id = fetcher.extract_bv_id(test_case)
            print(f"✅ {test_case} -> {bv_id}")
        except Exception as e:
            print(f"❌ {test_case} -> 错误: {e}")
    
    print()


def test_video_info():
    """测试视频信息获取"""
    print("🧪 测试视频信息获取...")
    
    # 使用一个知名的Bilibili视频进行测试
    test_bv = "BV1P24y1a7Lt"  # 这是示例中的BV号
    
    try:
        video_info = fetch_video_info(test_bv)
        
        if video_info:
            print("✅ 视频信息获取成功:")
            print(f"   标题: {video_info.get('title', '未知')[:50]}...")
            print(f"   时长: {video_info.get('duration', 0)}秒")
            print(f"   播放量: {video_info.get('view', 0)}")
            print(f"   弹幕数: {video_info.get('danmaku', 0)}")
            print(f"   分P数: {video_info.get('pages', 1)}")
        else:
            print("❌ 未获取到视频信息")
            
    except Exception as e:
        print(f"❌ 获取视频信息失败: {e}")
        print(f"详细错误: {traceback.format_exc()}")
    
    print()


def test_danmaku_fetching():
    """测试弹幕获取功能"""
    print("🧪 测试弹幕获取功能...")
    
    # 使用一个知名的Bilibili视频进行测试
    test_bv = "BV1P24y1a7Lt"
    
    try:
        print("正在获取弹幕数据（可能需要一些时间）...")
        
        # 测试protobuf接口
        danmaku_data = fetch_danmaku(test_bv, page=0, use_protobuf=True)
        
        if danmaku_data:
            print(f"✅ 成功获取 {len(danmaku_data)} 条弹幕")
            
            # 显示前几条弹幕作为示例
            print("前5条弹幕示例:")
            for i, danmaku in enumerate(danmaku_data[:5], 1):
                text = danmaku.get('text', '')
                timestamp = danmaku.get('timestamp', 0)
                print(f"   {i}. [{timestamp:.1f}s] {text}")
                
            return danmaku_data
        else:
            print("❌ 未获取到弹幕数据")
            return []
            
    except Exception as e:
        print(f"❌ 获取弹幕失败: {e}")
        print(f"详细错误: {traceback.format_exc()}")
        return []
    
    print()


def test_danmaku_analysis(danmaku_data):
    """测试弹幕分析功能"""
    print("🧪 测试弹幕分析功能...")
    
    if not danmaku_data:
        print("❌ 没有弹幕数据可供分析")
        return None
    
    try:
        analyzer = DanmakuAnalyzer()
        analysis_result = analyzer.generate_summary_report(danmaku_data)
        
        if analysis_result and 'error' not in analysis_result:
            print("✅ 弹幕分析成功:")
            
            # 基本统计
            if 'basic_stats' in analysis_result:
                stats = analysis_result['basic_stats']
                print(f"   总弹幕数: {stats.get('total_count', 0)}")
                print(f"   独特弹幕数: {stats.get('unique_count', 0)}")
                print(f"   重复率: {stats.get('duplicate_rate', 0):.1%}")
            
            # 关键词
            if 'keywords' in analysis_result and analysis_result['keywords']:
                print("   热门关键词:")
                for i, (word, count) in enumerate(analysis_result['keywords'][:5], 1):
                    print(f"     {i}. {word} ({count}次)")
            
            # 情感分析
            if 'sentiment' in analysis_result:
                sentiment = analysis_result['sentiment']
                print(f"   情感分析: 积极{sentiment.get('positive', 0):.1%}, "
                      f"消极{sentiment.get('negative', 0):.1%}, "
                      f"中性{sentiment.get('neutral', 0):.1%}")
            
            # 热点时刻
            if 'hot_moments' in analysis_result and analysis_result['hot_moments']:
                print(f"   发现 {len(analysis_result['hot_moments'])} 个热点时刻")
                
            return analysis_result
        else:
            print(f"❌ 分析失败: {analysis_result.get('error', '未知错误')}")
            return None
            
    except Exception as e:
        print(f"❌ 分析过程出错: {e}")
        print(f"详细错误: {traceback.format_exc()}")
        return None
    
    print()


def test_visualization(analysis_result):
    """测试可视化功能"""
    print("🧪 测试可视化功能...")
    
    if not analysis_result:
        print("❌ 没有分析结果可供可视化")
        return
    
    try:
        visualizer = DanmakuVisualizer()
        figures = visualizer.create_dashboard(analysis_result)
        
        if figures:
            print("✅ 可视化图表生成成功:")
            for chart_name in figures.keys():
                print(f"   - {chart_name}")
        else:
            print("❌ 未生成任何图表")
            
    except Exception as e:
        print(f"❌ 可视化生成失败: {e}")
        print(f"详细错误: {traceback.format_exc()}")
    
    print()


def main():
    """主测试函数"""
    print("🚀 开始测试Bilibili弹幕分析器...")
    print("=" * 50)
    
    # 测试1: BV号提取
    test_bv_extraction()
    
    # 测试2: 视频信息获取
    test_video_info()
    
    # 测试3: 弹幕获取（这可能需要较长时间）
    print("⚠️  注意: 弹幕获取可能需要较长时间，请耐心等待...")
    danmaku_data = test_danmaku_fetching()
    
    # 测试4: 弹幕分析
    analysis_result = test_danmaku_analysis(danmaku_data)
    
    # 测试5: 可视化
    test_visualization(analysis_result)
    
    print("=" * 50)
    print("🎉 测试完成!")
    
    if danmaku_data and analysis_result:
        print("✅ 所有核心功能测试通过")
    else:
        print("⚠️  部分功能可能存在问题，请检查网络连接或API状态")


if __name__ == "__main__":
    main()
