import streamlit as st
from urllib.request import urlopen
from bs4 import BeautifulSoup
import jieba
from collections import Counter
from pyecharts.charts import WordCloud, Bar, Pie, Line, Scatter, Radar, HeatMap
from pyecharts import options as opts
import re
from streamlit.components.v1 import html

# Streamlit界面
st.title("文章词频分析器")
url = st.text_input('请输入文章URL:', '')

def st_pyechart(chart):
    """辅助函数：将pyecharts图表嵌入Streamlit"""
    chart_html = chart.render_embed()
    html(chart_html, height=600)

if url:
    # 抓取文本内容
    try:
        response = urlopen(url)
        if 'text/html' in response.getheader('Content-Type'):
            html_bytes = response.read()
            html_str = html_bytes.decode('utf-8')  # 将 bytes 转换为字符串
            soup = BeautifulSoup(html_str, features="html.parser")

            # 移除脚本和样式元素
            for script in soup(["script", "style"]):
                script.extract()

            # 获取纯文本
            text = soup.get_text(separator=' ')
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = '\n'.join(chunk for chunk in chunks if chunk)

            # 分词和统计词频
            words = jieba.lcut(text)
            stop_words = set()  # 加载停用词表（这里简化为一个空集合）
            filtered_words = [word for word in words if len(word) > 1 and word not in stop_words]
            word_counts = Counter(filtered_words)

            # 显示前20个高频词
            top_20 = word_counts.most_common(20)
            st.write("最高频率20词:")
            st.table(top_20)

            # 绘制词云
            word_cloud = WordCloud()
            word_cloud.add("", top_20, word_size_range=[20, 100], shape="circle")
            st_pyechart(word_cloud)

            # 构建侧边栏进行图型筛选
            chart_type = st.sidebar.selectbox("选择图表类型", ["词云", "柱状图", "饼图", "折线图", "散点图", "雷达图", "热力图"])

            # 交互过滤低频词
            min_freq = st.sidebar.slider('选择最低频率', 1, max(word_counts.values()), 1)
            filtered_word_counts = {k: v for k, v in word_counts.items() if v >= min_freq}

            # 根据chart_type显示相应的图表
            if chart_type == "柱状图":
                bar = Bar()
                bar.add_xaxis([item[0] for item in top_20])
                bar.add_yaxis("", [item[1] for item in top_20])
                st_pyechart(bar)
            elif chart_type == "饼图":
                pie = Pie()
                pie.add("", top_20, radius=["30%", "75%"])
                st_pyechart(pie)
            elif chart_type == "折线图":
                line = Line()
                line.add_xaxis([item[0] for item in top_20])
                line.add_yaxis("", [item[1] for item in top_20])
                st_pyechart(line)
            elif chart_type == "散点图":
                scatter = Scatter()
                scatter.add_xaxis([item[0] for item in top_20])
                scatter.add_yaxis("", [item[1] for item in top_20])
                st_pyechart(scatter)
            elif chart_type == "雷达图":
                radar = Radar()
                schema = [{"name": item[0], "max": max(word_counts.values())} for item in top_20]
                radar.add_schema(schema)
                radar.add("", [[item[1] for item in top_20]])
                st_pyechart(radar)
            elif chart_type == "热力图":
                heatmap = HeatMap()
                data = [[i, j, item[1]] for i, item in enumerate(top_20) for j in range(len(top_20))]
                heatmap.add_xaxis([item[0] for item in top_20])
                heatmap.add_yaxis("Heatmap", [item[0] for item in top_20], data)
                st_pyechart(heatmap)

            # 更新词云以反映过滤后的结果
            filtered_top_20 = Counter(filtered_word_counts).most_common(20)
            word_cloud_filtered = WordCloud()
            word_cloud_filtered.add("", filtered_top_20, word_size_range=[20, 100], shape="circle")
            st_pyechart(word_cloud_filtered)

    except Exception as e:
        st.error(f"发生错误: {e}")
        st.error(f"URL: {url}")
        st.error(f"HTML Content-Type: {response.getheader('Content-Type') if 'response' in locals() else 'N/A'}")