# encoding: utf-8
'''
将数据存储到数据库
'''

import sqlite3
import pandas as pd
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

if __name__ == "__main__":
    db = NewsDatabase()

    # 读取所有新闻数据
    all_news = db.read_data()
    print(all_news)

    # 读取特定日期的新闻数据
    specific_date_news = db.read_data("SELECT * FROM news WHERE 日期 = '2024-10-09'")

    # 读取原始HTML数据
    raw_html = db.read_data("SELECT * FROM raw_html")

    # 执行自定义查询
    db.execute_query("UPDATE news SET 热度 = '非常热门' WHERE 情感得分 > 0.8")

    # 获取自定义查询结果
    hot_news = db.fetch_data("SELECT 标题, 热度 FROM news WHERE 热度 = '非常热门'")