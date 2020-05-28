# -*- coding=utf-8 -*-
from lxml import etree
import requests
import re


class BQG_spider(object):
    """爬取笔趣阁网站小说，并保存为阅读格式"""
    def __init__(self, novel_id):
        self.novel_id = str(novel_id)
        self.url = "https://www.bqg34.com/"
        self.headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, "
                                      "like Gecko) Chrome/83.0.4103.61 Safari/537.36"}
        self.chapter_dict = {}

    def send_request(self):
        """发送爬虫请求"""
        request_url = self.url + 'book_' + self.novel_id
        response = requests.get(request_url, headers=self.headers)
        return response

    def get_chapter_dict(self, response):
        """获取章节url列表"""
        response_element = etree.HTML(response.content)
        li_list = response_element.xpath('/html/body/div[4]/div/ul/li')
        for i in range(len(li_list)):
            if len(li_list[i]) != 0:
                chapter_title = li_list[i].xpath('./a/text()')[0]
                chapter_url = li_list[i].xpath('./a/@href')[0]
                self.chapter_dict[i] = (chapter_title, chapter_url)
        print(">>>获取章节列表成功")

    def get_chapter_content(self):
        """获取章节文本内容"""
        for key in self.chapter_dict:
            # 获取章节信息
            title, url = self.chapter_dict[key]
            # 拼接章节url
            chapter_url = self.url + 'book_' + self.novel_id + '/' + url
            # 发送请求，获取响应
            content_response = requests.get(chapter_url, headers=self.headers)
            # 将响应转为utf-8字符串
            response_element = etree.HTML(content_response.content)
            novel_str = response_element.xpath('//*[@id="htmlContent"]/text()')  # 返回值为一个列表，每段为列表的一个元素，段与段之间存在\r\n
            self.save_content(title, novel_str)

    def save_content(self, title, novel_str):
        """对字符串进行处理，提取文本内容"""
        # 添加章节标题
        with open(self.novel_id + '.txt', 'a', encoding='utf-8') as f:
            f.write('\r\n{}\r\n'.format(title))
            f.close()
        # 写入章节内容
        for i in novel_str:
            i = re.sub('/s', '', i)  # 取出字符串周年的\r\n以及/x0a等等
            i = i.replace(u"一秒记住【笔趣阁小说网 www.bqg34.com】，精彩小说无弹窗免费阅读！", u'')  # 替换广告
            i = i.replace(u"                ", u'')  # 替换空白
            with open(self.novel_id + '.txt', 'a', encoding='utf-8') as f:
                f.write(i)
                f.close()
        print(title + ' 下载完成')
        # 下面是错误代码：
        # 由于忘记在xpath语句内写/text()来获取内容，导致将返回的html对象进行解码
        # 而原网页使用的编码方式为ISO-8859-1编码，导致转码时出现问题
        # novel_str = etree.tostring(novel_element, encoding='utf-8').decode('utf-8')  # 注意这里的编码解码

    def run(self):
        """运行爬虫"""
        # 1 发送请求，获取响应
        response = self.send_request()
        # 2 对获取的响应进行处理，提取章节url列表
        self.get_chapter_dict(response)
        # 3 对提取的章节列表进行处理，循环提取章节名及章节内容（可能用到多进程）
        self.get_chapter_content()


def main():
    n_id = input("请输入想要爬取的小说id:")
    b = BQG_spider(n_id)
    b.run()


if __name__ == "__main__":
    main()
