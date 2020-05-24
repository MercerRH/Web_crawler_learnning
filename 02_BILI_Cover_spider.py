from lxml import etree
import requests


class Request_Error(Exception):
    """自定义异常：在url请求失败时使用"""
    # print("url请求错误")
    pass


class BiliCover(object):
    """爬取B站视频封面"""
    def __init__(self, BV_id):
        self.BV_id = BV_id
        self.headers = {
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.61 Safari/537.36"
        }
        self.base_url = "https://www.bilibili.com/video/"

    def send_request(self):
        print(">>>开始发送请求")
        url = self.base_url + self.BV_id
        response = requests.get(url, headers=self.headers)
        if response.status_code == 200:
            print(">>>发送请求成功")
            return response.content.decode()
        else:
            raise Request_Error('url错误，状态码为%d' % response.status_code)

    def extract_img(self, url_str_content):
        print(">>>开始接收图片请求")
        html_elements = etree.HTML(url_str_content)
        html_get_elements = html_elements.xpath("/html/head/meta[11]/@content")  # 返回一个只有一个元素的列表，该元素为图片路径
        print(">>>接收图片请求成功")
        return html_get_elements[0]

    def save_img(self, cover_url):
        response = requests.get(cover_url, headers=self.headers)
        img_url_content = response.content
        with open('cover.jpg', 'wb') as f:
            print(">>>开始下载")
            f.write(img_url_content)
            f.close()
            print(">>>下载完成")

    def run(self):
        # 1、获取url地址，发送请求，接收响应
        url_str_content = self.send_request()
        # 2、对响应进行处理，提取图片url
        cover_url = self.extract_img(url_str_content)
        # 3、从url中获取并保存图片
        self.save_img(cover_url)


def main():
    b_id = input('请输入BV号：')
    b = BiliCover(b_id)
    b.run()


if __name__ == "__main__":
    main()
