# encoding: utf-8
'''
将数据存储到数据库
'''

import sqlite3
import pandas as pd
from collections import Counter
import json

class NewsDatabase:
    def __init__(self, db_name='news.db'):
        self.db_name = db_name
        self.create_tables()

    def create_tables(self):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        cursor.execute('''CREATE TABLE IF NOT EXISTS news
                          (id INTEGER PRIMARY KEY AUTOINCREMENT,
                           日期 TEXT,
                           时间 TEXT,
                           信息来源 TEXT,
                           标题 TEXT,
                           排名 INTEGER,
                           热度 TEXT,
                           处理后热度 TEXT,
                           链接 TEXT,
                           情感得分 REAL,
                           加权情感得分 REAL,
                           分词 TEXT)''')
        
        cursor.execute('''CREATE TABLE IF NOT EXISTS raw_html
                          (id INTEGER PRIMARY KEY AUTOINCREMENT,
                           日期 TEXT,
                           时间 TEXT,
                           内容 TEXT)''')
        
        conn.commit()
        conn.close()

    def save_data(self, df: pd.DataFrame, table_name='news'):
        conn = sqlite3.connect(self.db_name)
        
        if table_name == 'news':
            df['分词'] = df['分词'].apply(json.dumps)
        
        df.to_sql(table_name, conn, if_exists='append', index=False)
        
        conn.close()

    def save_raw_html(self, html_content: str):
        df = pd.DataFrame({
            '日期': [pd.Timestamp.now().strftime('%Y-%m-%d')],
            '时间': [pd.Timestamp.now().strftime('%H:%M:%S')],
            '内容': [html_content]
        })
        self.save_data(df, 'raw_html')

    def read_data(self, query="SELECT * FROM news"):
        conn = sqlite3.connect(self.db_name)
        
        df = pd.read_sql_query(query, conn)
        if '分词' in df.columns:
            df['分词'] = df['分词'].apply(json.loads)
        
        conn.close()
        return df

    def execute_query(self, query, params=None):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        
        conn.commit()
        conn.close()

    def fetch_data(self, query, params=None):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        
        rows = cursor.fetchall()
        conn.close()
        return rows

    def delete_table(self,table_name:str):
        """删除news子表"""
        conn = sqlite3.connect(self.db_name)
        try:
            with conn:
                conn.execute(f"DROP TABLE IF EXISTS {table_name}")
            print("news表已成功删除")
        except sqlite3.Error as e:
            print(f"删除news表时发生错误：{e}")

    def clear_table(self, table_name):
        """清空指定表的所有数据"""
        conn = sqlite3.connect(self.db_name)
        try:
            with conn:
                conn.execute(f"DELETE FROM {table_name}")
            print(f"{table_name}表已成功清空")
        except sqlite3.Error as e:
            print(f"清空{table_name}表时发生错误：{e}")

    def export_word_cloud_data(self, output_file, query="SELECT 分词 FROM news WHERE 日期 = (SELECT MAX(日期) FROM news)"):
        """导出词云数据"""
        rows = self.fetch_data(query)
        words = []
        for row in rows:
            words.extend(eval(row[0]))  # 使用 eval 来解析字符串列表
        word_counts = Counter(words)
        word_cloud_data = [{"name": word, "value": count} for word, count in word_counts.items()]
        self._write_to_js_file(output_file, "wordCloudData", word_cloud_data)

    def export_pie_chart_data(self, output_file, query="SELECT 信息来源, SUM(CAST(处理后热度 AS INTEGER)) FROM news WHERE 日期 = (SELECT MAX(日期) FROM news) GROUP BY 信息来源"):
        """导出饼图数据"""
        rows = self.fetch_data(query)
        pie_chart_data = [{"name": row[0], "value": row[1]} for row in rows]
        self._write_to_js_file(output_file, "pieChartData", pie_chart_data)

    def export_line_chart_data(self, output_file):
        """导出折线图数据"""
        query = """
        SELECT 日期, SUM(加权情感得分) as total_sentiment
        FROM news
        GROUP BY 日期
        ORDER BY 日期
        """
        rows = self.fetch_data(query)
        line_chart_data = [{"date": row[0], "value": row[1]} for row in rows]
        self._write_to_js_file(output_file, "lineChartData", line_chart_data)

    def export_bar_chart_data(self, output_file, query="""
        SELECT 信息来源, 加权情感得分
        FROM news
        WHERE 日期 = (SELECT MAX(日期) FROM news)
    """):
        """导出柱状图数据"""
        rows = self.fetch_data(query)
        bar_chart_data = {}
        for row in rows:
            source = row[0]
            sentiment_score = row[1]
            if source not in bar_chart_data:
                bar_chart_data[source] = {"positive": 0, "negative": 0}
            if sentiment_score > 0:
                bar_chart_data[source]["positive"] += sentiment_score
            elif sentiment_score < 0:
                bar_chart_data[source]["negative"] += abs(sentiment_score)
        
        formatted_data = [{"category": source, "positive": data["positive"], "negative": data["negative"]} 
                          for source, data in bar_chart_data.items()]
        self._write_to_js_file(output_file, "barChartData", formatted_data)

    def _write_to_js_file(self, output_file, variable_name, data):
        """将数据写入 JavaScript 文件"""
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(f"export const {variable_name} = ")
            json.dump(data, f, ensure_ascii=False, indent=2)
            f.write(";")

if __name__ == "__main__":
    db = NewsDatabase()
    import os
    data_path = os.path.join(os.path.dirname(__file__), '..', 'vue', 'src', 'data')
    # db.export_word_cloud_data(os.path.join(data_path, 'wordCloudData.js'))
    # db.export_pie_chart_data(os.path.join(data_path,'pieChartData.js'))
    db.export_line_chart_data(os.path.join(data_path,'lineChartData.js'))
    # db.export_bar_chart_data(os.path.join(data_path,'barChartData.js'))