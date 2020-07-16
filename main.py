import requests
import os
from pyquery import PyQuery as pq


class Video(object):
    def __init__(self):
        self.category = ''
        self.video_collect = ''
        self.video_name = ''
        self.thumb = ''
        self.link = ''
        self.deleted = 0

    def __repr__(self):
        name = self.__class__.__name__
        properties = ('{}: ({})'.format(k, v) for k, v in self.__dict__.items())
        beautiful = '\n<{} \n {}>'.format(name, '\n '.join(properties))
        return beautiful


def html_for_url(url):
    headers = {
        'user-agent': """Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 \
                                (KHTML, like Gecko) Chrome/57.0.2987.98 Safari/537.36""",
    }
    r = requests.get(url, headers=headers)
    return r.content


def videos_for_url(div):
    pass


def collect_for_url(url):
    pass


def category_for_url(url):
    e = html_for_url(url)


def download_img(url):
    pass


def main():
    video = Video()
    original_url = 'https://www.culturedc.cn/vod.html'
    # 通过原始地址获得一个列表,其中是name,link键的字典
    category_list = category_for_url(original_url)
    for category in category_list:
        video.category = category.get('name', None)
        collect_dict = collect_for_url(category.get('link', None))
        # collect_list是一个内含多个字典的列表
        # collect为其字典,有name,thumb,link三个键
        for collect in collect_list:
            video.video_collect = collect.get('name', None)
            video.thumb = collect.get('thumb', None)
            for video_info in videos_for_url(collect.get('link', None)):
                video.video_name = video_info.get('name', None)
                video.link = video_info.get('link', None)
                print(video)




if __name__ == '__main__':
    main()
