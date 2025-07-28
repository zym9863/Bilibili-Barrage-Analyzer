# 📺 Bilibili Barrage Analyzer

[中文文档 (README.md)](README.md)

A powerful Bilibili barrage (danmaku) data analysis tool supporting barrage fetching, data analysis, and visualization.

## ✨ Features

- 📥 **Barrage Fetching**: Fetch barrage data from Bilibili videos, compatible with both protobuf and XML interfaces
- 📊 **Data Analysis**: Provides word frequency statistics, sentiment analysis, time distribution analysis, and more
- 📈 **Visualization**: Generates word clouds, time distribution charts, sentiment analysis charts, and other intuitive graphs
- 🔍 **Hotspot Detection**: Automatically identifies hotspot moments in barrages to discover exciting clips
- 🌐 **Web Interface**: User-friendly interface based on Streamlit, simple and intuitive operation
- 💾 **Data Export**: Supports exporting analysis results and raw data in CSV format

## 🛠️ Tech Stack

- **Python 3.12+**: Main programming language
- **uv**: Modern Python package manager
- **Streamlit**: Web application framework
- **bilibili-api-python**: Bilibili API library
- **jieba**: Chinese text segmentation library
- **pandas**: Data processing library
- **plotly**: Interactive chart library
- **wordcloud**: Word cloud generation library

## 🚀 Quick Start

### Requirements

- Python 3.12 or higher
- uv package manager

### Installation

1. **Clone the project**
   ```bash
   git clone https://github.com/zym9863/Bilibili-Barrage-Analyzer.git
   cd Bilibili-Barrage-Analyzer
   ```

2. **Install dependencies**
   ```bash
   uv sync
   ```

3. **Run the application**
   ```bash
   uv run streamlit run main.py
   ```

4. **Access the app**

   Open your browser and visit `http://localhost:8501`

### Usage

1. **Enter Video Information**
   - Input Bilibili video URL or BV number in the sidebar
   - Supported formats:
     - Full URL: `https://www.bilibili.com/video/BV1P24y1a7Lt`
     - Short link: `https://b23.tv/xxxxx`
     - BV number: `BV1P24y1a7Lt`

2. **Configure Analysis Options**
   - Choose Protobuf or XML interface (Protobuf recommended)
   - Set part number (for multi-part videos)
   - Optional date filter

3. **Start Analysis**
   - Click the "🚀 Start Barrage Analysis" button
   - Wait for data fetching and analysis to complete

4. **View Results**
   - Browse basic statistics
   - View various visualization charts
   - Download analysis results and raw data

## 📊 Analysis Features

### Basic Statistics
- Total barrage count
- Unique barrage count
- Duplicate rate statistics
- Average barrage length

### Keyword Analysis
- Hot keyword extraction
- Word frequency ranking
- Stopword filtering

### Sentiment Analysis
- Positive sentiment ratio
- Negative sentiment ratio
- Neutral sentiment ratio

### Time Distribution Analysis
- Barrage time distribution chart
- Hotspot moment detection
- Interaction peak discovery

### Visualization Charts
- Sentiment analysis pie chart
- Keyword bar chart
- Time distribution line chart
- Length distribution chart
- Hotspot moment scatter plot

## 🧪 Testing

Run the test script to verify functionality:

```bash
uv run python test_app.py
```

Test coverage includes:
- BV number extraction
- Video info fetching
- Barrage data fetching
- Data analysis
- Visualization generation

## 📁 Project Structure

```
Bilibili-Barrage-Analyzer/
├── main.py                 # Streamlit main app
├── danmaku_fetcher.py      # Barrage fetching module
├── danmaku_analyzer.py     # Data analysis module
├── danmaku_visualizer.py   # Visualization module
├── test_app.py             # Test script
├── pyproject.toml          # Project config
├── uv.lock                 # Dependency lock file
└── README.md               # Project documentation
```

## ⚠️ Notes

1. **Network Connection**: Requires stable network to access Bilibili API
2. **Request Frequency**: Avoid excessive requests to prevent API rate limiting
3. **Data Volume**: Popular videos may have large barrage data, fetching may take longer
4. **Font Support**: Word cloud feature requires Chinese font support

## 🤝 Contributing

Feel free to submit Issues and Pull Requests to improve the project!

## 📄 License

This project is licensed under the MIT License. See LICENSE for details.

## 🙏 Acknowledgements

- [bilibili-api-python](https://github.com/Nemo2011/bilibili-api) - Bilibili API library
- [Streamlit](https://streamlit.io/) - Excellent web app framework
- [jieba](https://github.com/fxsjy/jieba) - Chinese text segmentation tool
