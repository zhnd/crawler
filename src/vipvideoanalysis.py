import re
from urllib import parse
from urllib.error import HTTPError

import requests
from hyper.contrib import HTTP20Adapter


class Parser(object):

    def __init__(self, url):
        self.url = url

    def request(self, method, url, **kwargs):
        try:
            return requests.request(method, url, **kwargs)
        except HTTPError as error:
            print('HTTPError:', error)
        except ConnectionError as error:
            print('ConnectionError:', error)

    def get_page(self, url):
        headers = {
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
            'accept-encoding': 'gzip, deflate, br',
            'accept-language': 'zh-CN,zh;q=0.9',
            'cache-control': 'max-age=0',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.87 Safari/537.36'
        }
        session = requests.session()
        result = parse.urlparse(url)
        prefix = result.scheme + '://' + result.netloc
        session.mount(prefix, HTTP20Adapter())
        response = session.request('get', url, headers=headers)
        response.encoding = 'utf-8'
        return response.text

    def get_urls(self, page):
        urls = ''
        pattern = re.compile('var urls = "(.*?)";')
        result = re.search(pattern, page)
        if result:
            urls = result.group(1).strip()
        return urls

    def start(self):
        page = self.get_page(self.url)
        urls = self.get_urls(page)
        print(urls)


def main():
    url = 'https://v.qq.com/x/cover/rm3tmmat4li8uul/z0025x6k0aq.html'
    url = 'http://api.52jiexi.top/?url=%s' % url
    parser = Parser(url)
    parser.start()


if __name__ == '__main__':
    main()
