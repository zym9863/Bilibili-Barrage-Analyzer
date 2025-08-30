"""
Bilibili弹幕分析器 - Streamlit Web应用
"""

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, date
import time
import traceback
from config import config

# 导入自定义模块
from danmaku_fetcher import DanmakuFetcher, fetch_danmaku, fetch_video_info
from danmaku_analyzer import DanmakuAnalyzer, analyze_danmaku
from danmaku_visualizer import DanmakuVisualizer, create_visualizations
from danmaku_ai_analyzer import DanmakuAIAnalyzer, analyze_danmaku_with_ai
from utils import progress_callback, data_cache
from validator import validator


def main():
    """主函数"""
    # 页面配置
    st.set_page_config(
        page_title="Bilibili弹幕分析器",
        page_icon="📺",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # 标题和描述
    st.title("📺 Bilibili弹幕分析器")
    st.markdown("---")
    st.markdown("### 🎯 功能介绍")
    st.markdown("""
    - 📥 **弹幕获取**: 支持从Bilibili视频获取弹幕数据
    - 📊 **数据分析**: 词频统计、情感分析、时间分布分析
    - 📈 **可视化**: 词云图、时间分布图、情感分析图等
    - 🔍 **热点发现**: 自动识别弹幕热点时刻
    - 🤖 **AI智能分析**: 使用AI深度分析弹幕内容和观众反应
    """)

    # 侧边栏
    with st.sidebar:
        st.header("⚙️ 设置")

        # 视频URL输入
        st.subheader("📺 视频信息")
        video_input = st.text_input(
            "请输入Bilibili视频URL或BV号:",
            placeholder="例如: https://www.bilibili.com/video/BV1P24y1a7Lt 或 BV1P24y1a7Lt",
            help="支持完整URL或直接输入BV号"
        )

        # 分析选项
        st.subheader("🔧 分析选项")
        use_protobuf = st.checkbox("使用Protobuf接口", value=True, help="推荐使用，数据更完整")
        page_number = st.number_input("分P号", min_value=0, value=0, help="多P视频的分集号，从0开始")

        # AI分析选项
        st.subheader("🤖 AI分析")
        enable_ai_analysis = st.checkbox("启用AI智能分析", value=False, help="使用AI进行深度内容分析（需要网络连接）")
        
        if enable_ai_analysis:
            st.info("🔍 AI分析将提供情感分析、主题识别、热点解读和综合报告")

        # 高级选项
        with st.expander("🔬 高级选项"):
            date_filter = st.date_input(
                "日期过滤 (可选)",
                value=None,
                help="只获取指定日期的弹幕，留空表示获取所有"
            )

            ui_settings = config.ui_settings
            keyword_count = st.slider(
                "关键词数量", 
                ui_settings['keyword_count_min'], 
                ui_settings['keyword_count_max'], 
                ui_settings['keyword_count_default'], 
                help="显示的热门关键词数量"
            )
            time_interval = st.slider(
                "时间间隔 (秒)", 
                ui_settings['time_interval_min'], 
                ui_settings['time_interval_max'], 
                ui_settings['time_interval_default'], 
                help="时间分布分析的时间间隔"
            )

    # 主内容区域
    if video_input:
        # 验证输入
        try:
            validated_input = validator.validate_bilibili_url(video_input)
            # 验证分P号
            validated_page = validator.validate_page_number(page_number)
            # 验证分析参数
            validated_time_interval, validated_keyword_count = validator.validate_analysis_parameters(time_interval, keyword_count)
        except (ValueError, TypeError) as e:
            st.error(f"❌ 输入验证失败: {validator.sanitize_error_message(str(e))}")
            return
            
        # 获取视频信息
        with st.spinner("正在获取视频信息..."):
            try:
                video_info = fetch_video_info(video_input)

                if video_info:
                    # 显示视频信息
                    ui_config = config.ui_display_settings
                    video_columns = ui_config.get('video_info_columns', [2, 1, 1])
                    col1, col2, col3 = st.columns(video_columns)

                    with col1:
                        st.subheader("📹 视频信息")
                        st.write(f"**标题**: {video_info.get('title', '未知')}")
                        st.write(f"**时长**: {format_duration(video_info.get('duration', 0))}")
                        if video_info.get('pages', 1) > 1:
                            st.write(f"**分P数**: {video_info.get('pages', 1)}")

                    with col2:
                        st.metric("👀 播放量", format_number(video_info.get('view', 0)))
                        st.metric("💬 弹幕数", format_number(video_info.get('danmaku', 0)))

                    with col3:
                        st.metric("👍 点赞", format_number(video_info.get('like', 0)))
                        st.metric("⭐ 收藏", format_number(video_info.get('favorite', 0)))

                    st.markdown("---")

                    # 开始分析按钮
                    if st.button("🚀 开始分析弹幕", type="primary", use_container_width=True):
                        analyze_danmaku_data(
                            validated_input['url'], 
                            validated_page, 
                            use_protobuf, 
                            date_filter, 
                            validated_keyword_count, 
                            validated_time_interval, 
                            enable_ai_analysis
                        )

                else:
                    st.error("❌ 无法获取视频信息，请检查URL或BV号是否正确")

            except (ConnectionError, TimeoutError) as e:
                st.error(f"❌ 网络连接问题: {str(e)}")
                st.error("请检查网络连接或稍后重试")
            except (ValueError, KeyError) as e:
                st.error(f"❌ 数据解析错误: {str(e)}")
                st.error("请检查URL或BV号是否正确")
            except Exception as e:
                st.error(f"❌ 获取视频信息时出错: {str(e)}")
                st.error("请检查网络连接或稍后重试")

    else:
        # 显示使用说明
        st.info("👆 请在左侧输入Bilibili视频URL或BV号开始分析")

        # 示例展示
        st.subheader("📖 使用说明")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("""
            **支持的输入格式:**
            - 完整URL: `https://www.bilibili.com/video/BV1P24y1a7Lt`
            - 短链接: `https://b23.tv/xxxxx`
            - BV号: `BV1P24y1a7Lt`
            """)

        with col2:
            st.markdown("""
            **分析功能:**
            - 🔤 关键词提取和词频统计
            - 😊 情感倾向分析
            - ⏰ 弹幕时间分布
            - 🔥 热点时刻识别
            - 🤖 AI智能内容分析
            """)


def fetch_danmaku_data_step(video_input, page_number, use_protobuf, date_filter):
    """
    步骤1: 获取弹幕数据
    
    Args:
        video_input: 视频输入
        page_number: 分P号
        use_protobuf: 是否使用protobuf
        date_filter: 日期过滤器
        
    Returns:
        List[Dict]: 弹幕数据列表，如果失败则返回None
    """
    try:
        danmaku_data = fetch_danmaku(
            video_input,
            page=page_number,
            use_protobuf=use_protobuf,
            date_filter=date_filter
        )
        
        if not danmaku_data:
            st.error("❌ 未获取到弹幕数据，可能是视频没有弹幕或网络问题")
            return None
            
        return danmaku_data
        
    except Exception as e:
        st.error(f"❌ 获取弹幕数据失败: {str(e)}")
        return None


def analyze_danmaku_step(danmaku_data, time_interval):
    """
    步骤2: 分析弹幕数据
    
    Args:
        danmaku_data: 弹幕数据
        time_interval: 时间间隔
        
    Returns:
        分析结果字典，如果失败则返回None
    """
    try:
        analyzer = DanmakuAnalyzer()
        analysis_result = analyzer.generate_summary_report(danmaku_data, time_interval)
        return analysis_result
        
    except Exception as e:
        st.error(f"❌ 弹幕数据分析失败: {str(e)}")
        return None


def perform_ai_analysis_step(analysis_result, danmaku_data, enable_ai_analysis):
    """
    步骤3: AI智能分析
    
    Args:
        analysis_result: 基础分析结果
        danmaku_data: 弹幕数据
        enable_ai_analysis: 是否启用AI分析
        
    Returns:
        AI分析结果，如果未启用或失败则返回None
    """
    if not enable_ai_analysis:
        return None
        
    try:
        danmaku_texts = [item['text'] for item in danmaku_data if item.get('text')]
        ai_results = analyze_danmaku_with_ai(analysis_result, danmaku_texts)
        return ai_results
        
    except (ConnectionError, TimeoutError) as e:
        st.warning("⚠️ AI分析网络超时: 网络连接问题，请稍后重试")
        return None
    except (ValueError, KeyError) as e:
        st.warning("⚠️ AI分析数据错误: 数据格式问题")
        return None
    except Exception as e:
        st.warning(f"⚠️ AI分析失败: {str(e)}")
        return None


def generate_visualization_step(analysis_result):
    """
    步骤4: 生成可视化图表
    
    Args:
        analysis_result: 分析结果
        
    Returns:
        可视化图表字典，如果失败则返回None
    """
    try:
        visualizer = DanmakuVisualizer()
        figures = visualizer.create_dashboard(analysis_result)
        return figures
        
    except Exception as e:
        st.error(f"❌ 生成可视化图表失败: {str(e)}")
        return None


def analyze_danmaku_data(video_input, page_number, use_protobuf, date_filter, keyword_count, time_interval, enable_ai_analysis=False):
    """
    分析弹幕数据的主控制函数
    
    Args:
        video_input: 视频输入
        page_number: 分P号
        use_protobuf: 是否使用protobuf接口
        date_filter: 日期过滤器
        keyword_count: 关键词数量
        time_interval: 时间间隔
        enable_ai_analysis: 是否启用AI分析
    """
    # 创建进度条和状态显示
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    # 获取UI显示配置
    ui_config = config.ui_display_settings

    try:
        # 步骤1: 获取弹幕数据
        status_text.text("📥 正在获取弹幕数据...")
        progress_bar.progress(ui_config.get('progress_fetch_data', 20))
        
        danmaku_data = fetch_danmaku_data_step(video_input, page_number, use_protobuf, date_filter)
        if danmaku_data is None:
            return
            
        progress_bar.progress(ui_config.get('progress_analyze_data', 40))

        # 步骤2: 分析数据
        status_text.text("🔍 正在分析弹幕数据...")
        
        analysis_result = analyze_danmaku_step(danmaku_data, time_interval)
        if analysis_result is None:
            return
            
        progress_bar.progress(ui_config.get('progress_ai_analysis', 60))

        # 步骤3: AI分析（如果启用）
        if enable_ai_analysis:
            status_text.text("🤖 正在进行AI智能分析...")
            
        ai_results = perform_ai_analysis_step(analysis_result, danmaku_data, enable_ai_analysis)
        progress_bar.progress(ui_config.get('progress_visualization', 80))

        # 步骤4: 生成可视化
        status_text.text("📊 正在生成可视化图表...")
        
        figures = generate_visualization_step(analysis_result)
        if figures is None:
            return

        progress_bar.progress(ui_config.get('progress_complete', 100))
        status_text.text("✅ 分析完成!")

        time.sleep(ui_config.get('progress_complete_delay', 1))
        progress_bar.empty()
        status_text.empty()

        # 显示分析结果
        display_analysis_results(analysis_result, figures, danmaku_data, ai_results)

    except (ConnectionError, TimeoutError) as e:
        progress_bar.empty()
        status_text.empty()
        st.error("❌ 网络连接超时，请检查网络连接或稍后重试")
        st.error(f"详细信息: {str(e)}")
    except (ValueError, KeyError) as e:
        progress_bar.empty()
        status_text.empty()
        st.error("❌ 数据处理错误，请检查输入或稍后重试")
        st.error(f"详细信息: {str(e)}")
    except MemoryError as e:
        progress_bar.empty()
        status_text.empty()
        st.error("❌ 内存不足，请尝试分析更小的视频或重启应用")
        st.error("建议: 选择较短的视频或关闭其他应用释放内存")
    except Exception as e:
        progress_bar.empty()
        status_text.empty()
        st.error(f"❌ 分析过程中出错: {str(e)}")
        st.error("详细错误信息:")
        st.code(traceback.format_exc())


def display_analysis_results(analysis_result, figures, danmaku_data, ai_results=None):
    """显示分析结果"""

    st.markdown("---")
    st.header("📊 分析结果")

    # 基本统计
    if 'basic_stats' in analysis_result:
        st.subheader("📈 基本统计")
        
        ui_config = config.ui_display_settings
        stats_columns_count = ui_config.get('stats_columns_count', 4)
        col1, col2, col3, col4 = st.columns(stats_columns_count)

        stats = analysis_result['basic_stats']

        with col1:
            st.metric("总弹幕数", stats.get('total_count', 0))

        with col2:
            st.metric("独特弹幕数", stats.get('unique_count', 0))

        with col3:
            duplicate_rate = stats.get('duplicate_rate', 0)
            st.metric("重复率", f"{duplicate_rate:.1%}")

        with col4:
            avg_length = analysis_result.get('length_stats', {}).get('mean_length', 0)
            st.metric("平均长度", f"{avg_length:.1f}字")

    # AI分析结果
    if ai_results:
        st.markdown("---")
        st.subheader("🤖 AI智能分析")
        
        # 创建AI分析标签页
        ai_tab1, ai_tab2, ai_tab3, ai_tab4 = st.tabs(["😊 AI情感分析", "🎯 主题分析", "🔥 热点解读", "📋 综合报告"])
        
        with ai_tab1:
            if 'sentiment_ai' in ai_results and 'analysis' in ai_results['sentiment_ai']:
                st.write("**AI情感分析结果:**")
                st.write(ai_results['sentiment_ai']['analysis'])
                if 'sample_count' in ai_results['sentiment_ai']:
                    st.caption(f"基于 {ai_results['sentiment_ai']['sample_count']} 条弹幕样本分析")
            elif 'sentiment_ai' in ai_results and 'error' in ai_results['sentiment_ai']:
                st.error(f"情感分析失败: {ai_results['sentiment_ai']['error']}")
            else:
                st.info("暂无AI情感分析数据")
        
        with ai_tab2:
            if 'themes_ai' in ai_results and 'analysis' in ai_results['themes_ai']:
                st.write("**AI主题分析结果:**")
                st.write(ai_results['themes_ai']['analysis'])
                if 'sample_count' in ai_results['themes_ai']:
                    st.caption(f"基于 {ai_results['themes_ai']['sample_count']} 条弹幕样本分析")
            elif 'themes_ai' in ai_results and 'error' in ai_results['themes_ai']:
                st.error(f"主题分析失败: {ai_results['themes_ai']['error']}")
            else:
                st.info("暂无AI主题分析数据")
        
        with ai_tab3:
            if 'hot_moments_ai' in ai_results and 'analysis' in ai_results['hot_moments_ai']:
                st.write("**AI热点时刻分析:**")
                st.write(ai_results['hot_moments_ai']['analysis'])
                if 'hot_moments_count' in ai_results['hot_moments_ai']:
                    st.caption(f"基于 {ai_results['hot_moments_ai']['hot_moments_count']} 个热点时刻分析")
            elif 'hot_moments_ai' in ai_results and 'error' in ai_results['hot_moments_ai']:
                st.error(f"热点分析失败: {ai_results['hot_moments_ai']['error']}")
            else:
                st.info("暂无AI热点分析数据")
        
        with ai_tab4:
            if 'comprehensive_ai' in ai_results and 'comprehensive_report' in ai_results['comprehensive_ai']:
                st.write("**AI综合分析报告:**")
                st.write(ai_results['comprehensive_ai']['comprehensive_report'])
                if 'sample_count' in ai_results['comprehensive_ai']:
                    st.caption(f"基于 {ai_results['comprehensive_ai']['sample_count']} 条弹幕样本分析")
            elif 'comprehensive_ai' in ai_results and 'error' in ai_results['comprehensive_ai']:
                st.error(f"综合分析失败: {ai_results['comprehensive_ai']['error']}")
            else:
                st.info("暂无AI综合分析数据")

    # 可视化图表
    if figures:
        st.markdown("---")
        st.subheader("📊 数据可视化")

        # 创建标签页
        tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(["☁️ 词云图", "😊 情感分析", "🔤 热门关键词", "⏰ 时间分布", "📏 长度分布", "🔥 热点时刻"])

        with tab1:
            if 'wordcloud' in figures:
                st.plotly_chart(figures['wordcloud'], use_container_width=True)
            else:
                st.info("暂无词云数据")

        with tab2:
            if 'sentiment' in figures:
                st.plotly_chart(figures['sentiment'], use_container_width=True)
            else:
                st.info("暂无情感分析数据")

        with tab3:
            if 'keywords' in figures:
                st.plotly_chart(figures['keywords'], use_container_width=True)
            else:
                st.info("暂无关键词数据")

        with tab4:
            if 'time_distribution' in figures:
                st.plotly_chart(figures['time_distribution'], use_container_width=True)
            else:
                st.info("暂无时间分布数据")

        with tab5:
            if 'length_distribution' in figures:
                st.plotly_chart(figures['length_distribution'], use_container_width=True)
            else:
                st.info("暂无长度分布数据")

        with tab6:
            if 'hot_moments' in figures:
                st.plotly_chart(figures['hot_moments'], use_container_width=True)
            else:
                st.info("暂无热点时刻数据")

    # 详细数据
    with st.expander("📋 详细数据"):

        # 热点时刻详情
        if 'hot_moments' in analysis_result and analysis_result['hot_moments']:
            st.subheader("🔥 热点时刻详情")
            
            ui_config = config.ui_display_settings
            hot_moments_limit = ui_config.get('hot_moments_display_limit', 5)
            sample_limit = ui_config.get('sample_danmaku_display_limit', 3)
            detail_columns = ui_config.get('hot_moment_detail_columns', [1, 3])

            for i, moment in enumerate(analysis_result['hot_moments'][:hot_moments_limit], 1):
                with st.container():
                    col1, col2 = st.columns(detail_columns)

                    with col1:
                        st.write(f"**#{i}**")
                        st.write(f"时间: {format_duration(moment['time_start'])}")
                        st.write(f"弹幕数: {moment['count']}")

                    with col2:
                        st.write("**样本弹幕:**")
                        for j, text in enumerate(moment['sample_danmaku'][:sample_limit], 1):
                            st.write(f"{j}. {text}")

                    st.markdown("---")

        # 原始数据下载
        if danmaku_data:
            st.subheader("💾 数据下载")

            # 转换为DataFrame
            df = pd.DataFrame(danmaku_data)
            
            ui_config = config.ui_display_settings
            preview_rows = ui_config.get('dataframe_preview_rows', 10)

            # 显示数据预览
            st.write("**数据预览:**")
            st.dataframe(df.head(preview_rows), use_container_width=True)

            # 下载按钮
            csv = df.to_csv(index=False, encoding='utf-8-sig')
            st.download_button(
                label="📥 下载完整弹幕数据 (CSV)",
                data=csv,
                file_name=f"danmaku_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )


def format_duration(seconds):
    """
    格式化时长显示
    
    Args:
        seconds: 秒数
        
    Returns:
        str: 格式化后的时长字符串
    """
    ui_config = config.ui_display_settings
    hour_threshold = ui_config.get('time_format_hour_threshold', 3600)
    minute_threshold = ui_config.get('time_format_minute_threshold', 60)
    
    if seconds < minute_threshold:
        return f"{seconds}秒"
    elif seconds < hour_threshold:
        minutes = seconds // minute_threshold
        secs = seconds % minute_threshold
        return f"{minutes}分{secs}秒"
    else:
        hours = seconds // hour_threshold
        minutes = (seconds % hour_threshold) // minute_threshold
        return f"{hours}小时{minutes}分钟"


def format_number(num):
    """
    格式化数字显示
    
    Args:
        num: 要格式化的数字
        
    Returns:
        str: 格式化后的字符串
    """
    ui_config = config.ui_display_settings
    billion_threshold = ui_config.get('number_format_billion_threshold', 100000000)
    wan_threshold = ui_config.get('number_format_wan_threshold', 10000)
    
    if num >= billion_threshold:  # 1亿
        return f"{num/billion_threshold:.1f}亿"
    elif num >= wan_threshold:  # 1万
        return f"{num/wan_threshold:.1f}万"
    else:
        return str(num)


if __name__ == "__main__":
    main()
