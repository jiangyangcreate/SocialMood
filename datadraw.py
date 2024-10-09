# encoding: utf-8
from PIL import Image
from wordcloud import WordCloud, STOPWORDS
from imageio import imread
import jieba
import os
jieba.setLogLevel(jieba.logging.INFO)
"""
绘制词云图（剔除标点符号。剔除无意义的词，如：的得地）

按照不同的信息来源，绘制出情绪综合得分的柱状图（积极的红色、消极的绿色）

爬取多次，绘制出综合舆情走向折线图

绘制一个有效信息来源的饼图
"""
class getcouldword():

    def getcouldword(self,contents):

        logo_path = os.path.join(os.path.abspath(__file__).split('.')[0][:-12],
                            'logo.png')  # logo地址
        bw_path = os.path.join(os.path.abspath(__file__).split('.')[0][:-12],
                            'bw_logo.png') # 二值化logo地址
        ttf_path = os.path.join(os.path.abspath(__file__).split('.')[0][:-12],
                            'simhei.ttf') # 字体
        wordcloud_path = os.path.join(os.path.abspath(__file__).split('.')[0][:-12],
                            'wordcloud.png') # 字体

        img = Image.open(logo_path)
        Img = img.convert('L')# 模式L”为灰色图像，它的每个像素用8个bit表示，0表示黑，255表示白，其他数字表示不同的灰度。
        threshold = 195# 自定义灰度界限，大于这个值为黑色，小于这个值为白色

        table = []
        for i in range(256):
            if i < threshold:
                table.append(0)
            else:
                table.append(1)
        photo = Img.point(table, '1') # 图片二值化
        photo.save(bw_path)# 二值化logo地址

        content = ''
        for i in contents:
            content +=i[0]
            
        contents_cut = jieba.cut(content)# 使用jieba分词，获取词的列表
        contents_cut = [word for word in contents_cut if len(word)>1] #剔除单字
        contents_list = " ".join(contents_cut)
        
        # 制作wordcloud
        wc = WordCloud(stopwords=STOPWORDS.add(" "), #设置屏蔽空格
                    collocations=True,  # 是否包括两个词的搭配
                    background_color="white",  #背景颜色
                    font_path=ttf_path, #设置字体路径，不要更改
                    width=400, height=300, random_state=None, #图片大小
                    mask=imread(bw_path,pilmode="RGB"))
        wc.generate(contents_list)
        wc.to_file(wordcloud_path)
        return wordcloud_path