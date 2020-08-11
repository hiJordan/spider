import requests
import os.path
import time
import json
import pymysql
from random import randint
from pyquery import PyQuery as pq
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC


browser = webdriver.Firefox()


def log(*args, **kwargs):
    # time.time() 返回 unix time
    # 如何把 unix time 转换为普通人类可以看懂的格式呢？
    date_format = '%H:%M:%S'
    value = time.localtime(int(time.time()))
    dt = time.strftime(date_format, value)
    with open('log.txt', 'a', encoding='utf-8') as f:
        print(dt, *args, file=f, **kwargs)


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
        except Exception as e:
            print(f'连接数据库{db_name}失败.\n异常信息:{e}')

    @staticmethod
    def save(db, cursor, sql, *args):
        try:
            print('尝试执行sql语句存储数据.\n')
            if cursor.execute(sql, tuple(args[0])):
                db.commit()
                print(f'执行成功,数据{args[0]}成功存储到db_spider的video表中.\n')
        except Exception as e:
            db.rollback()
            print(f'数据{args[0]}存储失败,已回滚.\n异常信息: {e}')
        finally:
            print(f'关闭数据库db_spider.\n')
            db.close()

    @classmethod
    def new(cls, *args, **kwargs):
        print('开始存储数据.\n')
        if args:
            # 获取数据库相关信息
            db_name = 'db_spider'
            table = 'book'
            db, cursor = cls.load(db_name)
            print(f'获得数据库连接与游标,数据库名称:{db_name}与表名:{table}.\n')
            # 根据video对象信息生成sql语句,设置要增加到数据库的信息
            object_dict = args[0].__dict__
            fields = ', '.join(object_dict.keys())
            values = object_dict.values()
            placeholder = ', '.join(['%s'] * len(object_dict))
            sql = f'insert into {table}({fields}) values({placeholder})'
            print(f'生成sql语句: {sql}成功.\n')
            cls.save(db, cursor, sql, values)

    def __repr__(self):
        name = self.__class__.__name__
        properties = ('{}: ({})'.format(k, v) for k, v in self.__dict__.items())
        beautiful = '\n<{} \n {}>'.format(name, '\n '.join(properties))
        return beautiful


class Book(Model):
    def __init__(self):
        self.id = None
        self.location_thumb = ''
        self.remote_thumb = ''
        self.name = ''
        self.author = ''
        self.category = ''
        self.intro = ''
        self.location_book = ''
        self.remote_book = ''


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
    # random_time = randint(1, 5)
    # time.sleep(random_time)
    browser.get(url)
    time.sleep(5)
    r = browser.page_source
    return r


def book_for_url(url):
    """
    :功能:
        获取视频集中播放列表各视频的链接-名称-简介(无简介用名称代替)
    :参数:
        -url: 该视频集的地址
    :返回值:
        -videos: 以dict为元素的list,元素中有name,link,brief三个键
    """
    collect = {}
    host = 'https://haidian2.hanyastar.com.cn/'
    page = page_for_url(url)
    e = pq(page)
    name = e('.headline').text()
    author = e('#author').text()
    link = host + e('#openRead').attr('value')
    intro = name
    collect.update({'name': name, 'author': author, 'link': link, 'intro': intro})
    return collect


def collect_for_url(url, category_name):
    # collect为其字典,有name,thumb,link三个键
    collects = []
    host_url = 'https://www.culturedc.cn/'
    page = page_for_url(url)
    e = pq(page)

    if category_name == '热门推荐':
        hot_vod_div_list = e('#vod4user .pure-u-1-4')
        more_recomment_div_list = e('#moreRecomment .pure-u-1-4')

        for vod in hot_vod_div_list.items():
            collect = {}
            collect['name'] = vod('.headline a').text()
            collect['link'] = host_url + vod('a.object').attr.href
            collect['thumb'] = vod('img.img-responsive').attr('src')
            # print(collect)
            collects.append(collect)

        for vod in more_recomment_div_list.items():
            collect = {}
            collect['name'] = vod('.headline a').text()
            collect['link'] = host_url + vod('a.object').attr.href
            collect['thumb'] = vod('img.img-responsive').attr('src')
            # print(collect)
            collects.append(collect)

        return collects
    else:
        browser.get(url)
        while True:
            time.sleep(3)
            r = browser.page_source
            e = pq(r)
            home = e('#moreRecomment .pure-u-1-4')
            # print('home\'s li: ', home, '\n')
            for item in home.items():
                # print('item', item)
                name = item('.headline a').text()
                thumb = item('.column-inner img').attr.src
                link = host_url + 'resId,' + item('.object').attr('data-target') + '@vod-detail.html'
                # print('home\'s name, thumb, link', name, thumb, link)
                collects.append({'name': name, 'link': link, 'thumb': thumb})
            # 数据提取占位
            click_next = browser.find_element_by_css_selector('.next > a:nth-child(1)')
            # print(click_next)
            click_next.click()
            time.sleep(2)
            try:
                browser.switch_to.alert.accept()
                print('break!!')
                break
            except:
                pass
        return collects


def books_for_click(url, category):
    """
    :param
        -url: 地址信息
        -category: 分类名称
    :return:
        -thumb
        -book_link
    """
    collect = []
    count = 0
    host = 'https://www.culturedc.cn/'
    r = page_for_url(url)
    click_item = browser.find_element_by_partial_link_text(category)
    print(category, click_item)
    click_item.click()
    time.sleep(5)
    r = browser.page_source
    e = pq(r)
    # 存在分页
    if e('#pager').attr('style') != 'display: none;':
        count_sum = e('#pager .news-number > i:nth-child(1)').text()
        print('总页数: ', count_sum)
        while True:
            for item in e('.pure-u-1-5').items():
                count += 1
                thumb = item('a.object img').attr('src')
                book_link = host + item('a.object').attr('href')
                collect.append({'thumb': thumb, 'book_link': book_link})

            if int(count_sum) == count:
                print('翻页结束')
                break

            click_next = browser.find_element_by_css_selector('.next > a:nth-child(1)')
            click_next.click()
            time.sleep(2)
            r = browser.page_source
            e = pq(r)
    else:
        for item in e('.pure-u-1-5').items():
            thumb = item('a.object img').attr('src')
            book_link = host + item('a.object').attr('href')
            collect.append({'thumb': thumb, 'book_link': book_link})

    return collect


# 返回值为元素为字典的列表,字典有name与link为一键对,分别存储分类名称以及链接地址
def category_for_url(url):
    category = []

    page = page_for_url(url)
    # print('页面原始信息: ', page)
    e = pq(page)
    category_items = e('#categoryData a')
    # print('得到的页面: ', category_items)
    for item in category_items.items():
        name = item.text()
        if name == '全部':
            continue

        category.append({'name': name, })

    return category


def cached_url(url, name, category):
    root_folder = 'library'
    category_folder = 'book'
    child_folder = category
    folder = os.path.join(root_folder, category_folder, child_folder)
    filename = name + '.pdf'
    path = os.path.join(folder, filename)

    if os.path.exists(path):
        # with open(path, 'rb') as f:
        #     return f.read()
        print(f'文件{path}已存在')
        return path
    else:
        if not os.path.exists(folder):
            os.makedirs(folder)
        headers = {
                    'user-agent': """Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 \
                                    (KHTML, like Gecko) Chrome/57.0.2987.98 Safari/537.36""",
                  }
        r = requests.get(url, headers=headers)
        with open(path, 'wb') as f:
            f.write(r.content)
        print(f'写入文件{path}')
        # return r.content
        return path


def download_img(url, name, category):
    root_folder = 'library'
    category_folder = 'covers'
    child_folder = category
    folder = os.path.join(root_folder, category_folder, child_folder)
    filename = name + '.jpeg'
    path = os.path.join(folder, filename)

    if os.path.exists(path):
        print(f'图像{path}已存在')
        return path
    else:
        if not os.path.exists(folder):
            os.makedirs(folder)
        headers = {
            'user-agent': """Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 \
                            (KHTML, like Gecko) Chrome/57.0.2987.98 Safari/537.36""",
        }
        r = requests.get(url, headers=headers)
        with open(path, 'wb') as f:
            f.write(r.content)
        print(f'图像{path} written successfully')
        return path


def main():
    original_url = 'https://www.culturedc.cn/digital-letter-archive.html'
    # 通过原始地址获得一个列表,其中是name,link键的字典
    # category_list = category_for_url(original_url)
    category_list = [{'name': '文学'}]
    print(f'采集到分类信息: {category_list}\n')
    for category in category_list:
        print(f'采集视频分类: {category["name"]}')
        books = books_for_click(original_url, category["name"])
        print('分类中书籍数量: ', len(books), books)
        # for book in books:
        #     print('采集到书籍信息: ', book)
        #     single_book = book_for_url(book['book_link'])
        #     book_info = Book()
        #     book_info.name = single_book.get('name')
        #     book_info.author = single_book.get('author')
        #     book_info.intro = single_book.get('intro')
        #     book_info.remote_book = single_book.get('link')
        #     book_info.remote_thumb = book.get('thumb')
        #     book_info.category = category["name"]
        #
        #     book_info.location_book = cached_url(book_info.remote_book, book_info.name, book_info.category)
        #     book_info.location_thumb = download_img(book_info.remote_thumb, book_info.name, book_info.category)
        #     print('书籍对象信息; ', book_info)
        #     Book.new(book_info)


main()
