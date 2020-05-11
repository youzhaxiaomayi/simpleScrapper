import requests
import sys
import os
import threading
from contextlib import closing
from bs4 import BeautifulSoup




class pornHubScrap():
    def __init__(self):
        self.loginHeaders = {
            'User-Agent': 'user-agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36',
            'Cookie': 'ua=4f952e038b86eb344127af3e609009f8; platform_cookie_reset=pc; platform=pc; bs=vdig0396mh5imq3ujm917sqg7djxbd83; ss=817376292243735576; RNLBSERVERID=ded6856; _ga=GA1.2.2146896728.1584331095; _gid=GA1.2.2145374250.1584331095; il=v113v8Hklp3wsCLbtlAzWsS1WkPEaKVy7vsRX8iXJRtPYxNTg0NDIyMTY2SHp5LUJ6amNhcUE0ZHRiZFNQLVppMVJIbUR0NjJTQ0ZqWXo3SGNPSQ..; expiredEnterModalShown=1; _gat=1',
        }
        self.downloadHeaders = {
            'User-Agent': 'user-agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36',
        }
        self.session = requests.Session()
        self.rootUrl = 'https://www.pornhub.com'
    def loginPornhub(self):
        response = self.session.get(self.rootUrl, headers=self.loginHeaders)
        #print(response.status_code)
        #print(response.text)
        return response


    def getRencentVideoPage(self, pageId):
        assert pageId > 0
        if pageId == 1:
            pageUrl = self.rootUrl + "/video"
        else:
            pageUrl = self.rootUrl + "/video?page=" + str(pageId)

        response = self.session.get(pageUrl, headers=self.loginHeaders)
        return response

    def getVideoDownloadUrl(self, playUrl):
        response = self.session.get(playUrl, headers=self.loginHeaders)
        soup = BeautifulSoup(response.text, "lxml")
        downloadUrl = soup.find_all('a', class_="downloadBtn greyButton")
        if len(downloadUrl) == 0:
            print("can not find download url")
            return None

        return downloadUrl[0]['href']
    def getVideoPlayUrl(self, response):
        soup = BeautifulSoup(response.text, "lxml")
        #import ipdb;ipdb.set_trace()
        videols = soup.find_all(class_="pcVideoListItem js-pop videoblock videoBox")
        videoUrls = []
        for video in videols:
            subURl = video.find_all('a')[0]['href']
            videoUrls.append(self.rootUrl + subURl)

        return videoUrls

    def run(self):
        self.loginPornhub()
        for pageId in range(1,1000):
            try:
                response = self.getRencentVideoPage(pageId)
                videoPlayUrls = self.getVideoPlayUrl(response)
                for i in range(len(videoPlayUrls)):
                    downloadUrl = self.getVideoDownloadUrl(videoPlayUrls[i])
                    if downloadUrl is not None:
                        video_down = DownLoader(downloadUrl, str(i) + ".mp4", 32)
                        #self.video_downloader(downloadUrl, video_name=str(i) + ".mp4")
                        video_down.run()
            except Exception as e:
                print(e)


    def video_downloader(self, video_url, video_name="123.mp4"):
        """
        视频下载
        Parameters:
            video_url: 带水印的视频地址
            video_name: 视频名
        Returns:
            无
        """
        size = 0
        with closing(requests.get(video_url, headers=self.downloadHeaders, stream=True, verify=False)) as response:
            chunk_size = 1024
            content_size = int(response.headers['content-length'])
            if response.status_code == 200:
                sys.stdout.write('  [文件大小]:%0.2f MB\n' % (content_size / chunk_size / 1024))
                video_name = os.path.join("", video_name)
                with open(video_name, 'wb') as file:
                    for data in response.iter_content(chunk_size = chunk_size):
                        file.write(data)
                        size += len(data)
                        file.flush()

                        print('  [下载进度]:%.2f%%' % float(size / content_size * 100) + '\r',  end='')
                        #sys.stdout.flush()
                        if size / content_size == 1:
                            print('\n')
            else:
                print('链接异常')


#html = requests.get(url,headers=biliHeaders, verify = False)

if __name__ == "__main__":
    pornhub = pornHubScrap()
    pornhub.run()



