"""
Bilibili弹幕分析器 - Streamlit Web应用
"""

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, date
import time
import traceback

# 导入自定义模块
from danmaku_fetcher import DanmakuFetcher, fetch_danmaku, fetch_video_info
from danmaku_analyzer import DanmakuAnalyzer, analyze_danmaku
from danmaku_visualizer import DanmakuVisualizer, create_visualizations


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

        # 高级选项
        with st.expander("🔬 高级选项"):
            date_filter = st.date_input(
                "日期过滤 (可选)",
                value=None,
                help="只获取指定日期的弹幕，留空表示获取所有"
            )

            keyword_count = st.slider("关键词数量", 10, 100, 30, help="显示的热门关键词数量")
            time_interval = st.slider("时间间隔 (秒)", 10, 100, 60, help="时间分布分析的时间间隔")

    # 主内容区域
    if video_input:
        # 获取视频信息
        with st.spinner("正在获取视频信息..."):
            try:
                video_info = fetch_video_info(video_input)

                if video_info:
                    # 显示视频信息
                    col1, col2, col3 = st.columns([2, 1, 1])

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
                        analyze_danmaku_data(video_input, page_number, use_protobuf, date_filter, keyword_count, time_interval)

                else:
                    st.error("❌ 无法获取视频信息，请检查URL或BV号是否正确")

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
            """)


def analyze_danmaku_data(video_input, page_number, use_protobuf, date_filter, keyword_count, time_interval):
    """分析弹幕数据"""

    # 创建进度条
    progress_bar = st.progress(0)
    status_text = st.empty()

    try:
        # 步骤1: 获取弹幕数据
        status_text.text("📥 正在获取弹幕数据...")
        progress_bar.progress(20)

        danmaku_data = fetch_danmaku(
            video_input,
            page=page_number,
            use_protobuf=use_protobuf,
            date_filter=date_filter
        )

        if not danmaku_data:
            st.error("❌ 未获取到弹幕数据，可能是视频没有弹幕或网络问题")
            return

        progress_bar.progress(50)

        # 步骤2: 分析数据
        status_text.text("🔍 正在分析弹幕数据...")

        analyzer = DanmakuAnalyzer()
        analysis_result = analyzer.generate_summary_report(danmaku_data, time_interval)

        progress_bar.progress(80)

        # 步骤3: 生成可视化
        status_text.text("📊 正在生成可视化图表...")

        visualizer = DanmakuVisualizer()
        figures = visualizer.create_dashboard(analysis_result)

        progress_bar.progress(100)
        status_text.text("✅ 分析完成!")

        time.sleep(1)
        progress_bar.empty()
        status_text.empty()

        # 显示分析结果
        display_analysis_results(analysis_result, figures, danmaku_data)

    except Exception as e:
        progress_bar.empty()
        status_text.empty()
        st.error(f"❌ 分析过程中出错: {str(e)}")
        st.error("详细错误信息:")
        st.code(traceback.format_exc())


def display_analysis_results(analysis_result, figures, danmaku_data):
    """显示分析结果"""

    st.markdown("---")
    st.header("📊 分析结果")

    # 基本统计
    if 'basic_stats' in analysis_result:
        st.subheader("📈 基本统计")

        col1, col2, col3, col4 = st.columns(4)

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

    # 可视化图表
    if figures:
        st.markdown("---")
        st.subheader("📊 数据可视化")

        # 创建标签页
        tab1, tab2, tab3, tab4, tab5 = st.tabs(["😊 情感分析", "🔤 热门关键词", "⏰ 时间分布", "📏 长度分布", "🔥 热点时刻"])

        with tab1:
            if 'sentiment' in figures:
                st.plotly_chart(figures['sentiment'], use_container_width=True)
            else:
                st.info("暂无情感分析数据")

        with tab2:
            if 'keywords' in figures:
                st.plotly_chart(figures['keywords'], use_container_width=True)
            else:
                st.info("暂无关键词数据")

        with tab3:
            if 'time_distribution' in figures:
                st.plotly_chart(figures['time_distribution'], use_container_width=True)
            else:
                st.info("暂无时间分布数据")

        with tab4:
            if 'length_distribution' in figures:
                st.plotly_chart(figures['length_distribution'], use_container_width=True)
            else:
                st.info("暂无长度分布数据")

        with tab5:
            if 'hot_moments' in figures:
                st.plotly_chart(figures['hot_moments'], use_container_width=True)
            else:
                st.info("暂无热点时刻数据")

    # 详细数据
    with st.expander("📋 详细数据"):

        # 热点时刻详情
        if 'hot_moments' in analysis_result and analysis_result['hot_moments']:
            st.subheader("🔥 热点时刻详情")

            for i, moment in enumerate(analysis_result['hot_moments'][:5], 1):
                with st.container():
                    col1, col2 = st.columns([1, 3])

                    with col1:
                        st.write(f"**#{i}**")
                        st.write(f"时间: {format_duration(moment['time_start'])}")
                        st.write(f"弹幕数: {moment['count']}")

                    with col2:
                        st.write("**样本弹幕:**")
                        for j, text in enumerate(moment['sample_danmaku'][:3], 1):
                            st.write(f"{j}. {text}")

                    st.markdown("---")

        # 原始数据下载
        if danmaku_data:
            st.subheader("💾 数据下载")

            # 转换为DataFrame
            df = pd.DataFrame(danmaku_data)

            # 显示数据预览
            st.write("**数据预览:**")
            st.dataframe(df.head(10), use_container_width=True)

            # 下载按钮
            csv = df.to_csv(index=False, encoding='utf-8-sig')
            st.download_button(
                label="📥 下载完整弹幕数据 (CSV)",
                data=csv,
                file_name=f"danmaku_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )


def format_duration(seconds):
    """格式化时长显示"""
    if seconds < 60:
        return f"{seconds}秒"
    elif seconds < 3600:
        minutes = seconds // 60
        secs = seconds % 60
        return f"{minutes}分{secs}秒"
    else:
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        return f"{hours}小时{minutes}分钟"


def format_number(num):
    """格式化数字显示"""
    if num >= 100000000:  # 1亿
        return f"{num/100000000:.1f}亿"
    elif num >= 10000:  # 1万
        return f"{num/10000:.1f}万"
    else:
        return str(num)


if __name__ == "__main__":
    main()
