import requests
import os
import time
import pymysql
from random import randint
from pyquery import PyQuery as pq
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait

browser = webdriver.Firefox()


class Model(object):
    @staticmethod
    def load(db_name):
        try:
            print(f'尝试与{db_name}建立连接.\n')
            db = pymysql.connect(host='localhost', user='root',
                                 password='123456', port=3306, db=db_name)
            cursor = db.cursor()
            print(f'成功连接到MySql数据库{db_name}, 创建游标成功.\n')
            return db, cursor
        except:
            print(f'连接数据库{db_name}失败.\n')

    @staticmethod
    def save(db, cursor, sql, *args):
        try:
            print('尝试执行sql语句存储数据.\n')
            if cursor.execute(sql, tuple(args[0])):
                cursor.commit()
                print(f'执行成功,数据{args[0]}成功存储到db_spider的video表中.\n')
        except:
            db.rollback()
            print(f'数据{args[0]}存储失败,已回滚.\n')
        finally:
            print(f'关闭数据库db_spider.\n')
            db.close()

    @classmethod
    def new(cls, *args, **kwargs):
        print('开始存储数据.\n')
        if args:
            # 获取数据库相关信息
            db_name = 'db_spider'
            table = 'video'
            db, cursor = cls.load(db_name)
            print(f'获得数据库连接与游标,数据库名称:{db_name}与表名:{table}.\n')
            # 根据video对象信息生成sql语句,设置要增加到数据库的信息
            object_dict = args[0].__dict__
            fields = ', '.join(object_dict.keys())
            values = object_dict.values()
            placeholder = ', '.join(['%s'] * len(object_dict))
            sql = f'insert into {table}({fields}) values({placeholder})'
            print(f'生成sql语句成功.\n')
            cls.save(db, cursor, sql, values)

    def __repr__(self):
        name = self.__class__.__name__
        properties = ('{}: ({})'.format(k, v) for k, v in self.__dict__.items())
        beautiful = '\n<{} \n {}>'.format(name, '\n '.join(properties))
        return beautiful


class Video(Model):
    def __init__(self):
        self.id = None
        self.category = ''
        # 存储心声.FM时,其视频集属性以名称_二级分类名组成.
        self.video_collect = ''
        self.video_name = ''
        self.thumb = ''
        self.link = ''


# url解析,返回协议类型--端口--域名--路径
def parse_url(url):
    # 提取协议与uri
    protocol = url.split('://')[0]
    if protocol == 'http':
        protocol = 'http'
        uri = url.split('://')[1]
    elif protocol == 'https':
        protocol = 'https'
        uri = url.split('://')[1]
    else:
        uri = url

    # 提取主机地址
    index = uri.find('/')
    if index == -1:
        host = uri
    else:
        host = uri.split('/')[0]

    # 提取端口号
    http_ports = {
        'http': 80,
        'https': 443,
    }
    if protocol in http_ports:
        port = http_ports[protocol]
    else:
        port = uri.split(':')[1]

    # 提取路径
    if index == -1:
        path = '/'
    else:
        path = '/' + uri.split('/')[1]

    return {'protocol': protocol, 'host': host, 'port': port, 'path': path}


def page_for_url(url):
    # 通过随机数, 设置数据采集的时间间隔
    random_time = randint(1, 10)
    time.sleep(random_time)

    user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:78.0) Gecko/20100101 Firefox/78.0'
    browser.get(url)
    # try:
    #     paging = browser.find_element_by_id('pager')
    #     if paging:
    #         while True:
    #             click_next = browser.find_element_by_css_selector('.pagination li.item:nth-child(12) ')
    #             yield browser.page_source
    # except:
    #     pass
    wait = WebDriverWait(browser, 2)
    r = browser.page_source
    browser.close()
    return r


def videos_for_url(div):
    pass


# collect为其字典,有name,thumb,link三个键
def collect_for_url(url, category_name):
    collects = []
    page = page_for_url(url)
    e = pq(page)

    try:
        hot_vod_div_list = e('#vod4user .column-inner')
        moreRecomment_div_list = e('#moreRecomment .column-inner')
        for vod in hot_vod_div_list.items():
            name = vod('.headline a').text()
            link = vod('a.object').attr.href
            thumb = vod('img.img-responsive').attr('src')
        for vod in hot_vod_div_list.items():
            name = vod('.headline a').text()
            link = vod('a.object').attr.href
            thumb = vod('img.img-responsive').attr('src')
    except:
        try:
            paging = e('#pager')
            if paging:
                while True:
                    # 数据提取占位
                    click_next = browser.find_element_by_css_selector('.pagination li.item:nth-child(12) ')
                    click_next.click()
                    WebDriverWait(browser, 3)
                    if browser.switch_to.alert:
                        break
                    page = browser.page_source
            else:
                pass
        except:
            pass


# 返回值为元素为字典的列表,字典有name与link为一键对,分别存储分类名称以及链接地址
def category_for_url(url):
    category = []

    url_info = parse_url(url)
    page = page_for_url(url)
    e = pq(page)
    category_items = e('#category a')
    # print('得到的页面: ', category_items)
    for item in category_items.items():
        name = item.text()
        if name == '热门推荐':
            link = url
        else:
            protocol = url_info.get('protocol', None) + '://'
            host = url_info.get('host', None) + '/'
            link = protocol + host + item.attr.href
        category.append({'name': name, 'link': link})

    return category


def download_img(url):
    pass


def main():
    video = Video()
    original_url = 'https://www.culturedc.cn/vod.html'
    # 通过原始地址获得一个列表,其中是name,link键的字典
    category_list = category_for_url(original_url)

    for category in category_list:
        print(f'采集视频分类: {category["name"]} -- 链接: {category["link"]}\n')
        video.category = category.get('name', None)
        collect_dict = collect_for_url(category.get('link', None), video.category)
        # # collect_list是一个内含多个字典的列表
        # # collect为其字典,有name,thumb,link三个键
        # for collect in collect_list:
        #     video.video_collect = collect.get('name', None)
        #     video.thumb = collect.get('thumb', None)
        #     # 通过collect获取视频集地址link,解析出视频的link,name,数据结构为以字典为元素的列表
        #     for video_info in videos_for_url(collect.get('link', None)):
        #         video.video_name = video_info.get('name', None)
        #         video.link = video_info.get('link', None)
        #         # 测试视频属性信息,并存储到数据库
        #         print(video)


if __name__ == '__main__':
    main()
