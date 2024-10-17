import re
import os 
from datetime import datetime

import jieba
import numpy as np
import pandas as pd
from bs4 import BeautifulSoup
from nltk.sentiment import SentimentIntensityAnalyzer
from playwright.sync_api import sync_playwright
from sklearn.linear_model import LinearRegression
from snownlp import SnowNLP
from pyecharts.charts import Bar, Line, Pie, WordCloud, Page
from pyecharts import options as opts

from database import NewsDatabase

class ChartGenerator:
    def create_bar_chart(self, data , y_label="Sentiment",title="Sentiment Scores by Source") -> Bar:
        """Generate a bar chart with positive, negative, and absolute sentiment scores."""

        x_data, y_data_positive, y_data_negative, y_data_absolute = zip(*data)
        bar = (
            Bar()
            .add_xaxis(x_data)
            .add_yaxis("Positive Sentiment", y_data_positive, stack="stack1", category_gap="50%")
            .add_yaxis("Negative Sentiment", y_data_negative, stack="stack2", category_gap="50%")
            .add_yaxis("Absolute Sentiment", y_data_absolute, stack="stack3", category_gap="50%")
            .set_global_opts(
                title_opts=opts.TitleOpts(title=title, pos_left="center"),
                xaxis_opts=opts.AxisOpts(name="Source"),
                yaxis_opts=opts.AxisOpts(name="Sentiment Score"),
                legend_opts=opts.LegendOpts(pos_top="10%", pos_right="10%"),
            )
        )
        return bar

    def create_line_chart(self,data,y_label="Weighted Sentiment Score Sum",title="Sum of Weighted Sentiment Scores Over Time") -> Line:
        """Generate a line chart."""
        x_data, y_data = zip(*data) 
        line = (
            Line()
            .add_xaxis(x_data)
            .add_yaxis(y_label, y_data, is_smooth=True)
            .set_global_opts(
                title_opts=opts.TitleOpts(title=title, pos_left="center"),
                xaxis_opts=opts.AxisOpts(name="Date", axislabel_opts=opts.LabelOpts(rotate=45)),
                yaxis_opts=opts.AxisOpts(name=y_label),
                legend_opts=opts.LegendOpts(pos_bottom="0%")
            )
        )
        return line

    def create_pie_chart(self, data_pairs, title="Information Source Heat") -> Pie:
        """Generate a pie chart."""
        pie = (
            Pie()
            .add("", data_pairs)
            .set_global_opts(
                title_opts=opts.TitleOpts(title=title, pos_left="center"),
                legend_opts=opts.LegendOpts(pos_bottom="0%")  # Move legend to the bottom
            )
            .set_series_opts(label_opts=opts.LabelOpts(formatter="{b}: {d}%"))
        )
        return pie

    def create_wordcloud(self, words, title="Word Cloud") -> WordCloud:
        """Generate a word cloud."""
        wordcloud = (
            WordCloud()
            .add("", words, word_size_range=[20, 100],shape="circle")
            .set_global_opts(title_opts=opts.TitleOpts(title=title, pos_left="center"))
        )
        return wordcloud

    def render_charts(self, charts, output_file=None):
        """Render multiple charts to a single HTML file."""
        if output_file is None:
            output_file = os.path.join("html", "charts.html")

        page = Page(layout=Page.SimplePageLayout)
        page.add(*charts)
        page.render(output_file)


class WebScraper:
    def __init__(self, url="https://tophub.today/"):
        self.url = url

    def fetch_webpage_content(self) -> str:
        """获取网页内容"""
        with sync_playwright() as p:
            browser = p.firefox.launch(headless=False)
            page = browser.new_page()
            page.goto(self.url)
            content = page.content()
            browser.close()
        return content

class DataProcessor:
    def __init__(self, html_content,data,time):
        self.html_content = html_content
        self.data = data
        self.time = time
        self.df = pd.DataFrame(
            columns=["日期", "时间", "信息来源", "标题", "排名", "热度", "链接"]
        )

    def clean_data(self):
        """清洗数据：删除特定类型的数据，处理热度"""
        # 删除电影、综艺等数据
        pattern = r"(电影|综艺|剧集|音乐|影视|节目|剧场版|动画|漫画|小说|图书|专辑)"
        self.df = self.df[~self.df["标题"].str.contains(pattern, regex=True)]

        # 处理热度数据
        def process_hot(hot):
            # 提取数字部分
            match = re.search(r"(\d+(\.\d+)?)", hot)
            if match:
                number = float(match.group(1))
                # 检查是否包含"万"（考虑可能的空格）
                if re.search(r"\s*万\s*(热度)?", hot):
                    return int(number * 10000)
                else:
                    return int(number)
            else:
                return None  # 如果没有找到数字，返回None

        # 在"热度"列后添加"处理后热度"列
        热度_index = self.df.columns.get_loc("热度")
        self.df.insert(热度_index + 1, "处理后热度", self.df["热度"].apply(process_hot))

    def parse_hot_list(self):
        """解析热门列表"""
        soup = BeautifulSoup(self.html_content, "lxml")
        data_infos = {
            "node-32": "虎嗅网",
            "node-1": "微博",
            "node-6": "知乎",
            "node-5": "微信",
            "node-19": "哔哩哔哩",
            "node-221": "抖音",
        }

        for info_id, info_from in data_infos.items():
            infos = soup.find(id=info_id)
            for info in infos.find_all('a', target="_blank"):
                url = info.get('href')
                title = info.find(class_="t").text.strip()
                rank = int(info.find(class_="s").text.strip())
                hot = info.find(class_="e").text.strip()
                self.df = pd.concat(
                    [
                        self.df,
                        pd.DataFrame(
                            [[self.data, self.time, info_from, title, rank, hot, url]],
                            columns=self.df.columns,
                        ),
                    ],
                    ignore_index=True,
                )

    @staticmethod
    def get_text_score(text: str) -> float:
        """获取文本的情感得分，范围从-1到1"""
        if re.search(r"[\u4e00-\u9fff]", text):  # 检测是否包含中文字符
            text = text.replace(" ", "")
            s = SnowNLP(text)
            return (s.sentiments - 0.5) * 2  # 将0-1范围转换为-1到1
        else:
            sia = SentimentIntensityAnalyzer()
            return sia.polarity_scores(text)["compound"]

    @staticmethod
    def get_word_split(text: str) -> list:
        """分词函数"""
        if len(text) <= 2:
            return text
        if re.search(r"[\u4e00-\u9fff]", text):  # 检测是否包含中文字符
            text = text.replace(" ", "")
            contents_cut = jieba.cut(text)  # 使用jieba分词，获取词的列表
            contents_cut = [word for word in contents_cut if len(word) > 1]  # 剔除单字
            return contents_cut
        else:
            return text.split()

    def process_data(self):
        """处理数据：添加情感得分和分词"""
        self.df["情感得分"] = self.df["标题"].apply(self.get_text_score)
        self.df["分词"] = self.df["标题"].apply(self.get_word_split)

    def sentiment_analysis(self):
        情感得分_index = self.df.columns.get_loc("情感得分")
        self.df.insert(
            情感得分_index + 1,
            "加权情感得分",
            self.df["情感得分"]
            * (self.df["处理后热度"] ** 0.5)  # 热度平方根处理
            * (
                1
                - (
                    (self.df["排名"] / self.df["排名"].max()) ** 1.5
                )  # 排名归一化并加权处理
            ),
        )

    def run(self):
        """运行整个数据处理流程"""
        self.parse_hot_list()
        self.clean_data()  # 在解析和处理之间添加清洗步骤
        self.estimate_missing_heat()  # 估算缺失的热度值
        self.process_data()  # 计算情感得分、分词
        self.sentiment_analysis()  # 情感分析加权计算
        return self.df

    def estimate_missing_heat(self):
        """估算缺失的热度值"""
        features = ["排名"]
        target = "处理后热度"

        def impute_group(group):
            X = group[features]
            y = group[target]

            # 如果没有缺失值，直接返回原始组
            if not y.isnull().any():
                return group

            # 幂律分布拟合（通过对数变换实现）
            X_train = X[y.notnull()]
            y_train = y[y.notnull()]

            # 将 X_train 转换为浮点数类型
            X_train = X_train.astype(float)

            # 对X和y进行对数变换，处理可能的零值
            log_X_train = np.log(X_train + 1)
            log_y_train = np.log(y_train + 1)

            lr = LinearRegression()
            lr.fit(log_X_train, log_y_train)

            # 获取拟合的系数
            slope = lr.coef_[0]
            intercept = lr.intercept_
            # print(f"拟合的幂律方程为: y = {np.exp(intercept):.2f} * x^{slope:.2f}")

            # 预测缺失值
            X_missing = X[y.isnull()]
            if not X_missing.empty:
                # 将 X_missing 转换为浮点数
                X_missing = X_missing.astype(float)
                log_X_missing = np.log(X_missing + 1)
                log_predictions = lr.predict(log_X_missing)
                predictions = np.exp(log_predictions) - 1  # 反向变换

                # 确保预测值不小于0
                predictions = np.maximum(predictions, 0)

                # 确保预测值符合排名顺序
                for i, pred in enumerate(predictions):
                    rank = X_missing.iloc[i]["排名"]
                    higher_ranks = y[(X["排名"] < rank) & y.notnull()]
                    lower_ranks = y[(X["排名"] > rank) & y.notnull()]

                    if len(higher_ranks) > 0:
                        pred = min(pred, higher_ranks.min())
                    if len(lower_ranks) > 0:
                        pred = max(pred, lower_ranks.max())

                    predictions[i] = pred

                group.loc[y.isnull(), target] = predictions

            return group

        # 对每个信息来源分别进行缺失值填充
        self.df = self.df.groupby("信息来源").apply(impute_group)

        # 删除仍然为None的行（如果有的话）
        self.df = self.df.dropna(subset=["处理后热度"])
        self.df["处理后热度"] = self.df["处理后热度"].astype(int)


def main(debug=True):
    db = NewsDatabase()
    if not debug:
        scraper = WebScraper()
        html_content = scraper.fetch_webpage_content()
        db.save_raw_html(html_content)  # 保存原始HTML
    else:
        db.delete_table("news")
        db = NewsDatabase()

    html_contents = db.read_data("SELECT * FROM raw_html")

    for _, row in html_contents.iterrows():
        html_content = row["内容"]
        date = row["日期"]
        time = row["时间"]
        processor = DataProcessor(html_content, date, time)
        result_df = processor.run()
        db.save_data(result_df)
    
    # 调用绘图方法
    chart_gen = ChartGenerator()

    # 获取数据
    word_cloud_data = db.export_word_cloud_data()
    pie_chart_data = db.export_pie_chart_data()
    line_chart_data = db.export_line_chart_data()
    bar_chart_data = db.export_bar_chart_data()

    # 创建图表
    word_cloud = chart_gen.create_wordcloud(word_cloud_data)
    pie_chart = chart_gen.create_pie_chart(pie_chart_data)
    line_chart = chart_gen.create_line_chart(line_chart_data)
    bar_chart = chart_gen.create_bar_chart(bar_chart_data)

    # 渲染图表
    charts = [word_cloud, 
              pie_chart, 
              line_chart,
              bar_chart
              ]
    chart_gen.render_charts(charts)
if __name__ == "__main__":
    main(debug=True)
