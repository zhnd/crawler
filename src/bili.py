import json
import os
import re
import sys
from urllib.error import HTTPError
from xml.dom import minidom

import requests


class Bili(object):

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
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Cache-Control': 'max-age=0',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.87 Safari/537.36'
        }
        response = self.request('get', url, headers=headers)
        response.encoding = 'utf-8'
        return response.text

    def get_video_data(self):
        return None

    def get_title(self, page):
        title = ''
        pattern = re.compile('<title data-vue-meta="true">(.*?)_哔哩哔哩')
        result = re.search(pattern, page)
        if result:
            title = result.group(1).strip()
        return title

    def get_cid(self, page):
        cid = ''
        pattern = re.compile('cid=(.*?)&')
        result = re.search(pattern, page)
        if result:
            cid = result.group(1).strip()
        return cid

    def get_bvid(self, page):
        bvid = ''
        pattern = re.compile('bvid=(.*?)&')
        result = re.search(pattern, page)
        if result:
            bvid = result.group(1).strip()
        return bvid

    # https://api.bilibili.com/x/player/playurl?cid=2555264&bvid=BV1Bx411P7DC&fnval=16
    def get_mp4_info(self, cid, bvid):
        url = 'https://api.bilibili.com/x/player/playurl?cid=%s&bvid=%s&fnval=16' % (cid, bvid)
        page = self.get_page(url)
        play_info = json.loads(page)
        video_url = play_info['data']['dash']['video'][0]['base_url']
        audio_url = play_info['data']['dash']['audio'][0]['base_url']
        return video_url, audio_url

    def download(self, url, filepath):
        headers = {
            'Referer': self.url,
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.87 Safari/537.36'
        }
        size = 0
        response = self.request('get', url, headers=headers, stream=True, verify=False)
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

    # https://comment.bilibili.com/2555264.xml
    def get_danmaku(self, cid):
        url = 'https://comment.bilibili.com/%s.xml' % cid
        page = self.get_page(url)
        file = open('danmaku.xml', 'w+', encoding='utf-8')
        file.write(page)
        DOMTree = minidom.parse('danmaku.xml')
        i = DOMTree.documentElement
        ds = i.getElementsByTagName('d')
        file = open('danmaku.txt', 'w+', encoding='utf-8')
        for d in ds:
            childNodes = d.childNodes
            if childNodes.length > 0:
                file.write(childNodes[0].data + '\n')

    def start(self):
        page = self.get_page(self.url)
        title = self.get_title(page)
        print(title)
        cid = self.get_cid(page)
        bvid = self.get_bvid(page)
        video_url, audio_url = self.get_mp4_info(cid, bvid)
        path = os.path.join(os.getcwd(), title)
        if not os.path.exists(path):
            os.makedirs(path)
        filename = 'video.m4s'
        filepath = os.path.join(path, filename)
        self.download(video_url, filepath)
        filename = 'audio.m4s'
        filepath = os.path.join(path, filename)
        self.download(audio_url, filepath)
        # ffmpeg -i video.m4s -i audio.m4s -vcodec copy -acodec copy output.mp4


def main():
    url = 'https://www.bilibili.com/video/BV1Bx411P7DC'
    bili = Bili(url)
    bili.start()


if __name__ == '__main__':
    main()
