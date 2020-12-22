import os
import re
import sys
from multiprocessing import Pool
from urllib import parse
from urllib.error import HTTPError

import requests
import urllib3
from hyper.contrib import HTTP20Adapter


class Aiqiyi(object):

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

    def get_title(self, page):
        title = ''
        pattern = re.compile('<title>(.*?)-电影')
        result = re.search(pattern, page)
        if result:
            title = result.group(1).strip()
        return title

    def get_m3u8_url(self):
        m3u8_url = ''
        return m3u8_url

    def download(self, url, filepath):
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.87 Safari/537.36'
        }
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        response = self.request('get', url, headers=headers, stream=True, verify=False)
        size = 0
        chunk_size = 1024
        if response.status_code == 200:
            content_length = int(response.headers['Content-Length'])
            sys.stdout.write('文件大小: %0.2fMB\n' % (content_length / chunk_size / 1024))
            with open(filepath, 'wb') as file:
                for data in response.iter_content(chunk_size=chunk_size):
                    file.write(data)
                    size += len(data)
                    file.flush()
                    sys.stdout.write('下载进度: %.2f%%\r' % float(size / content_length * 100))
                    if size / content_length == 1:
                        print('\n')
        else:
            print('下载出错')
            if os.path.exists(filepath):
                os.remove(filepath)

    def crawl_video(self, title):
        path = os.path.join(os.getcwd(), title)
        if not os.path.exists(path):
            os.makedirs(path)
        m3u8_url = self.get_m3u8_url()
        if m3u8_url == '':
            return
        print(m3u8_url)
        content = self.get_page(m3u8_url)
        if '#EXTM3U' not in content:
            raise BaseException('非m3u8链接')
        if '#EXT-X-STREAM-INF' in content:
            lines = content.split('\n')
            for line in lines:
                if '.m3u8' in line:
                    m3u8_url = m3u8_url.rsplit('/', 1)[0] + '/' + line
                    content = self.get_page(m3u8_url)
        lines = content.split('\n')
        urls = []
        for index, line in enumerate(lines):
            if '#EXTINF' in line:
                ts_url = m3u8_url.rsplit('/', 1)[0] + '/' + lines[index + 1]
                urls.append(ts_url)
        pool = Pool(32)
        for url in urls:
            filename = os.path.basename(url)
            if filename.find('?') > -1:
                filename = filename[0:filename.find('?')]
            filepath = os.path.join(path, filename)
            pool.apply_async(self.download, args=(url, filepath))
        pool.close()
        pool.join()
        # copy /b *.ts new.mp4

    def start(self):
        page = self.get_page(self.url)
        title = self.get_title(page)
        if title == '':
            return
        print(title)
        self.crawl_video(title)


def main():
    url = 'https://www.iqiyi.com/v_19rri0vxp0.html'
    aiqiyi = Aiqiyi(url)
    aiqiyi.start()


if __name__ == '__main__':
    main()
