import re
from urllib.error import HTTPError

import requests


class Weibo(object):

    def __init__(self, oid):
        self.oid = oid

    def request(self, method, url, **kwargs):
        try:
            return requests.request(method, url, **kwargs)
        except HTTPError as error:
            print('HTTPError:', error)
        except ConnectionError as error:
            print('ConnectionError:', error)

    def get_page(self, url):
        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Cookie': 'SUB=_2AkMoNj-lf8NxqwJRmPESyGnhbY9-zArEieKeas5-JRMxHRl-yT9jqn0ftRB6A7YRSqQK3GBfE7arEdbwJfKi2yJEFlQd; SUBP=0033WrSXqPxfM72-Ws9jqgMF55529P9D9WWjUsQG7rxHlJRNZjzmZFag; login_sid_t=06285119b28f7ff61be186b90f7cf6c6; cross_origin_proto=SSL; YF-V5-G0=f5a079faba115a1547149ae0d48383dc; WBStorage=70753a84f86f85ff|undefined; _s_tentry=passport.weibo.com; wb_view_log=1280*7201.5; Apache=3069660627429.9907.1600827544355; SINAGLOBAL=3069660627429.9907.1600827544355; ULV=1600827544362:1:1:1:3069660627429.9907.1600827544355:; Ugrow-G0=1ac418838b431e81ff2d99457147068c; YF-Page-G0=761bd8cde5c9cef594414e10263abf81|1600827613|1600827616',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.87 Safari/537.36'
        }
        response = self.request('get', url, headers=headers)
        response.encoding = 'utf-8'
        return response.text

    def start(self):
        url = 'https://weibo.com/u/%d' % self.oid
        page = self.get_page(url)
        pattern = re.compile('<title>(.*?)的微博_微博</title>')
        result = re.search(pattern, page)
        if result is None:
            return
        nickname = result.group(1).strip()
        print(nickname)
        pattern = re.compile('<strong class=\\\\"W_f12\\\\">(.*?)<')
        result = re.findall(pattern, page)
        following = int(result[0])
        followers = int(result[1])
        weibo_num = int(result[2])
        print('关注：%d    粉丝：%d    微博：%d' % (following, followers, weibo_num))


def main():
    # Dear-迪丽热巴 1669879400
    oid = 1669879400
    weibo = Weibo(oid)
    weibo.start()


if __name__ == '__main__':
    main()
