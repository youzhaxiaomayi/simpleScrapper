#-*-coding:utf-8-*-
import requests
import sys
import os

from contextlib import closing
from bs4 import BeautifulSoup
import chardet
import downloader



class chengZiScrap():
    def __init__(self, netID='https://czsp3.com/video/8'):
        self.Headers = {
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36'
            }

        self.session = requests.Session()
        self.netId = netID 
        self.video_format = 'https://czsp3.com/api/?d=pc&c=video&m=detail&timestamp={}&id={}&invite='
        self.down_root = 'https://dl-orange.tom331.com'
        self.video_list_format = 'https://czsp3.com/api/?d=pc&c=video&m=lists&timestamp=1586249020343&tag_id=8&page={}&page_size=24'


    def getVideoListPage(self, pageId):
        video_list_ip = self.video_list_format.format(pageId)
        print('list_ip:', video_list_ip)
        response = self.session.get(video_list_ip, headers=self.Headers)
        video_ids = []
        try:
            video_list = response.json()['data']['data']
            for video in video_list:
                video_id = video['id']
                video_ids.append(video_id)
        except KeyError as e:
            pass

        return video_ids

    def getVideoDownloadUrl(self, timestamp, video_id):
        video_ip = self.video_format.format(timestamp, video_id)
        print('video_ip', video_ip)
        #import ipdb;ipdb.set_trace()
        response = self.session.get(video_ip, headers=self.Headers)
        try:
            title = response.json()['data']['show_title']
            down_url = response.json()['data']['download_url']
        except  KeyError as e:
            down_url = None 
            title = ''
            print('no key')
        return down_url, title


    def run(self):
        for i in range(1,10):
            video_ids = self.getVideoListPage(i)
            for video_id in video_ids:
                timestamp = '1586245827168' 
                down_url, title = self.getVideoDownloadUrl(timestamp, video_id)
                if down_url:
                    url = self.down_root + down_url
                    print("url:", url)
                    down = downloader.DownLoader(url, title + '.mp4', 8)
                    down.run()



if __name__ == "__main__":
    """
    Headers = {
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36'
    }

    session = requests.Session()
    
    rootUrl = 'https://czsp3.com/video/detail/14539'
    rootUrl = 'https://czsp3.com/api/?d=pc&c=video&m=relation_movies&timestamp=1586244208142&video_id=14539'
    rootUrl = 'https://czsp3.com/api/?d=pc&c=video&m=detail&timestamp=1586245827168&id=14539&invite='
    response = session.get(rootUrl, headers=Headers)
    #response.encoding='utf-8'
    #response.encoding='unicode_escape'
    title = response.json()['data']['show_title']
    down_url = response.json()['data']['download_url']
    down_root = 'https://dl-orange.tom331.com'
    url = down_root + down_url
    print("url:", url)
    down = downloader.DownLoader(url, title + '.mp4')
    down.run()
    """
    

    video_net = chengZiScrap()
    video_net.run()

