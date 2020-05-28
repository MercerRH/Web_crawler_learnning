# -*- coding=utf-8 -*-
from lxml import etree
import requests
import re
import threading


CHAPTER_DICT = {}
THREAD_POSITION = 1  # 爬取码，表示当前处理的章节
mutex = threading.Lock()


class Dict_Thread(threading.Thread):
    """对字典中的章节进行处理的线程"""
    def __init__(self, url, novel_id, headers, thread_id):
        self.url = url
        self.novel_id = novel_id
        self.headers = headers
        self.thread_id = thread_id
        super(Dict_Thread, self).__init__()

    def run(self):
        """设置同时对多章节进行爬取"""
        global CHAPTER_DICT, THREAD_POSITION
        for i in range(len(CHAPTER_DICT)):  # 设置字典判断次数，其实设为字典长度除以线程数即可
            if THREAD_POSITION < len(CHAPTER_DICT):  # 防止字典越界
                mutex.acquire()  # 锁定资源
                # 获取章节信息
                title, url = CHAPTER_DICT[THREAD_POSITION]
                # 拼接章节url
                chapter_url = self.url + 'book_' + self.novel_id + '/' + url
                # 发送请求，获取响应
                content_response = requests.get(chapter_url, headers=self.headers)
                # 将响应转为utf-8字符串
                response_element = etree.HTML(content_response.content)
                novel_str = response_element.xpath(
                    '//*[@id="htmlContent"]/text()')  # 返回值为一个列表，每段为列表的一个元素，段与段之间存在\r\n
                self.save_content(title, novel_str)
                THREAD_POSITION += 1  # 将爬取码+1，让其他多线程调用
                mutex.release()

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
        print(">>> " + str(self.thread_id) + title + ' 下载完成')
        # 下面是错误代码：
        # 由于忘记在xpath语句内写/text()来获取内容，导致将返回的html对象进行解码
        # 而原网页使用的编码方式为ISO-8859-1编码，导致转码时出现问题
        # novel_str = etree.tostring(novel_element, encoding='utf-8').decode('utf-8')  # 注意这里的编码解码


class BQG_spider(object):
    """爬取笔趣阁网站小说，并保存为阅读格式"""
    def __init__(self, novel_id):
        self.novel_id = str(novel_id)
        self.url = "https://www.bqg34.com/"
        self.headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, "
                                      "like Gecko) Chrome/83.0.4103.61 Safari/537.36"}

    def send_request(self):
        """发送爬虫请求"""
        request_url = self.url + 'book_' + self.novel_id
        response = requests.get(request_url, headers=self.headers)
        return response

    def get_chapter_dict(self, response):
        """获取章节url列表"""
        global CHAPTER_DICT
        response_element = etree.HTML(response.content)
        li_list = response_element.xpath('/html/body/div[4]/div/ul/li')
        for i in range(len(li_list)):
            if len(li_list[i]) != 0:
                chapter_title = li_list[i].xpath('./a/text()')[0]
                chapter_url = li_list[i].xpath('./a/@href')[0]
                CHAPTER_DICT[i] = (chapter_title, chapter_url)
        print(">>> 获取章节列表成功")

    def thread_schedule(self):
        """对线程进行调度的方法，将dict_list分发给所有线程进行处理"""
        for i in range(10):
            t = Dict_Thread(self.url, self.novel_id, self.headers, i)
            t.start()
            t.join()
            print(">>> 线程 %d 开始运行" % i)

    def run(self):
        """运行爬虫"""
        # 1 发送请求，获取响应
        response = self.send_request()
        # 2 对获取的响应进行处理，提取章节url列表
        self.get_chapter_dict(response)
        # 3 对提取的章节列表进行处理，使用多线程循环提取章节名及章节内容
        self.thread_schedule()


def main():
    n_id = input("请输入想要爬取的小说id:")
    b = BQG_spider(n_id)
    b.run()


if __name__ == "__main__":
    main()
