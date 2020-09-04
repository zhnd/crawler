import json
import time
from urllib import parse
from urllib.error import HTTPError

import requests


class Kuwo(object):

    def __init__(self, url, referer):
        self.url = url
        self.referer = referer

    def request(self, method, url, **kwargs):
        try:
            return requests.request(method, url, **kwargs)
        except HTTPError as error:
            print('HTTPError:', error)
        except ConnectionError as error:
            print('ConnectionError:', error)

    def get_page(self, url):
        headers = {
            'Accept': 'application/json, text/plain, */*',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Referer': self.referer,
            'Cookie': 'Hm_lvt_cdb524f42f0ce19b169a8071123a4797=1597292954,1597918999; Hm_lpvt_cdb524f42f0ce19b169a8071123a4797=1597918999; kw_token=1W8P67W22WF',
            'csrf': '1W8P67W22WF',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.87 Safari/537.36'
        }
        response = self.request('get', url, headers=headers)
        response.encoding = 'utf-8'
        return response.text

    def get_audio_url(self, rid, br):
        t = int(time.time())
        url = 'http://www.kuwo.cn/url?format=mp3&rid=%d&response=url&type=convert_url3&br=%s&from=web&t=%d&httpsStatus=1' % (
            rid, br, t)
        page = self.get_page(url)
        data = json.loads(page)
        return data['url']

    def start(self):
        page = self.get_page(self.url)
        data = json.loads(page)
        music_list = data['data']['list']
        for music in music_list:
            filename = '%s - %s.mp3' % (music['artist'], music['name'])
            rid = music['rid']
            br = '320kmp3'
            audio_url = self.get_audio_url(rid, br)
            print(filename)
            print(audio_url)


def main():
    # http://www.kuwo.cn/search/list?key=%E8%B0%AA%E4%BB%99
    # http://www.kuwo.cn/api/www/search/searchMusicBykeyWord?key=%E8%B0%AA%E4%BB%99&pn=1&rn=3
    # http://www.kuwo.cn/url?format=mp3&rid=89560911&response=url&type=convert_url3&br=128kmp3&from=web&t=1597996584179&httpsStatus=1
    # 128k: https://ef-sycdn.kuwo.cn/b4063c6036fd4fc318bc3b77aacf9561/5f3f792f/resource/n2/79/13/2564778015.mp3
    # 320k: https://ef-sycdn.kuwo.cn/816d797dbfc389930ddf5ed4626973da/5f3f83d7/resource/n2/82/69/1433435136.mp3
    key = '谪仙'
    key = parse.quote(key)
    pn = 1
    rn = 3
    url = 'http://www.kuwo.cn/api/www/search/searchMusicBykeyWord?key=%s&pn=%d&rn=%d' % (key, pn, rn)
    referer = 'http://www.kuwo.cn/search/list?key=%s' % key
    kuwo = Kuwo(url, referer)
    kuwo.start()


if __name__ == '__main__':
    main()
