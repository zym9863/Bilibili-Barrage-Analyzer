# 📺 Bilibili弹幕分析器

一个功能强大的Bilibili弹幕数据分析工具，支持弹幕获取、数据分析和可视化展示。

## ✨ 功能特性

- 📥 **弹幕获取**: 支持从Bilibili视频获取弹幕数据，兼容protobuf和xml两种接口
- 📊 **数据分析**: 提供词频统计、情感分析、时间分布分析等多维度分析
- 📈 **可视化展示**: 生成词云图、时间分布图、情感分析图等直观图表
- 🔍 **热点发现**: 自动识别弹幕热点时刻，发现精彩片段
- 🌐 **Web界面**: 基于Streamlit的用户友好界面，操作简单直观
- 💾 **数据导出**: 支持分析结果和原始数据的CSV格式导出

## 🛠️ 技术栈

- **Python 3.12+**: 主要开发语言
- **uv**: 现代Python包管理器
- **Streamlit**: Web应用框架
- **bilibili-api-python**: Bilibili API接口库
- **jieba**: 中文分词库
- **pandas**: 数据处理库
- **plotly**: 交互式图表库
- **wordcloud**: 词云生成库

## 🚀 快速开始

### 环境要求

- Python 3.12 或更高版本
- uv包管理器

### 安装步骤

1. **克隆项目**
   ```bash
   git clone https://github.com/zym9863/Bilibili-Barrage-Analyzer.git
   cd Bilibili-Barrage-Analyzer
   ```

2. **安装依赖**
   ```bash
   uv sync
   ```

3. **运行应用**
   ```bash
   uv run streamlit run main.py
   ```

4. **访问应用**

   打开浏览器访问 `http://localhost:8501`

### 使用方法

1. **输入视频信息**
   - 在左侧边栏输入Bilibili视频URL或BV号
   - 支持的格式：
     - 完整URL: `https://www.bilibili.com/video/BV1P24y1a7Lt`
     - 短链接: `https://b23.tv/xxxxx`
     - BV号: `BV1P24y1a7Lt`

2. **配置分析选项**
   - 选择使用Protobuf或XML接口（推荐Protobuf）
   - 设置分P号（多P视频）
   - 可选择日期过滤器

3. **开始分析**
   - 点击"🚀 开始分析弹幕"按钮
   - 等待数据获取和分析完成

4. **查看结果**
   - 浏览基本统计信息
   - 查看各种可视化图表
   - 下载分析结果和原始数据

## 📊 分析功能详解

### 基本统计
- 总弹幕数量
- 独特弹幕数量
- 重复率统计
- 平均弹幕长度

### 关键词分析
- 热门关键词提取
- 词频统计排序
- 停用词过滤

### 情感分析
- 积极情感比例
- 消极情感比例
- 中性情感比例

### 时间分布分析
- 弹幕时间分布图
- 热点时刻识别
- 互动高峰发现

### 可视化图表
- 情感分析饼图
- 关键词柱状图
- 时间分布折线图
- 长度分布统计图
- 热点时刻散点图

## 🧪 测试

运行测试脚本验证功能：

```bash
uv run python test_app.py
```

测试内容包括：
- BV号提取功能
- 视频信息获取
- 弹幕数据获取
- 数据分析功能
- 可视化生成

## 📁 项目结构

```
Bilibili-Barrage-Analyzer/
├── main.py                 # Streamlit主应用
├── danmaku_fetcher.py      # 弹幕获取模块
├── danmaku_analyzer.py     # 数据分析模块
├── danmaku_visualizer.py   # 可视化模块
├── test_app.py            # 测试脚本
├── pyproject.toml         # 项目配置
├── uv.lock               # 依赖锁定文件
└── README.md             # 项目说明
```

## ⚠️ 注意事项

1. **网络连接**: 需要稳定的网络连接访问Bilibili API
2. **请求频率**: 避免过于频繁的请求，以免被API限制
3. **数据量**: 热门视频的弹幕数据可能较大，获取时间较长
4. **字体支持**: 词云功能需要中文字体支持

## 🤝 贡献指南

欢迎提交Issue和Pull Request来改进项目！

## 📄 许可证

本项目采用MIT许可证，详见LICENSE文件。

## 🙏 致谢

- [bilibili-api-python](https://github.com/Nemo2011/bilibili-api) - 提供Bilibili API接口
- [Streamlit](https://streamlit.io/) - 优秀的Web应用框架
- [jieba](https://github.com/fxsjy/jieba) - 中文分词工具