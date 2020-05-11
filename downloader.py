#-*-coding:utf-8-*-
import os
import sys
import requests
from requests.adapters import HTTPAdapter
import threading
from threading import Lock
from contextlib import closing
from bs4 import BeautifulSoup
import time 


class DownLoader:
    def __init__(self, url, save_path, thre_num=8):
        self.url = url
        self.num = thre_num
        self.name = save_path
        session = requests.session()
        request_retry = requests.adapters.HTTPAdapter(max_retries=3)
        session.mount('https://', request_retry) 
        session.mount('http://', request_retry)
        #r = requests.head(self.url, timeout=10)
        r = session.head(self.url, timeout=10)
        # 获取文件大小
        self.total = int(r.headers['Content-Length'])
        self.process_lock = Lock()
        self.downloaded_size = 0
        self.thread_over_n = 0

        
        print('file size:{}'.format(self.size_format(self.total)))

    def size_format(self, size):
        for unit in ('', 'k', 'M', 'G'): 
            if size >= 1024:
                size /= 1024
            else:
                break
        return ('{:.2f}{}' if unit else '{}{}').format(size, unit)

    # 获取每个线程下载的区间
    def get_range(self):
        ranges = []
        offset = int(self.total // self.num)
        for i in range(self.num):
            if i == self.num-1:
                #ranges.append((i*offset,''))
                ranges.append((i*offset, self.total))
            else:
                ranges.append((i*offset,(i+1)*offset))
        return ranges  # [(0,100),(100,200),(200,"")]

    # 通过传入开始和结束位置来下载文件
    def download1(self,start,end):
        headers = {'Range':'Bytes=%d-%d'%(start,end),'Accept-Encoding':'*'}
        print(headers)
        try:
            session = requests.session()
            request_retry = requests.adapters.HTTPAdapter(max_retries=8)
            session.mount('https://', request_retry) 
            session.mount('http://', request_retry)
            #res = requests.get(self.url,headers=headers, stream=True, timeout=60)
            res = session.get(self.url,headers=headers, stream=True, timeout=120)
            code = res.status_code
        except requests.exceptions.RequestException as e:
            print(e)
        except requests.exceptions.ConnectionError as e:
            print(e)
        # 将文件指针移动到传入区间开始的位置
        tmp_story = bytes()
        chunk_size = 0
        try:
            for chunk in res.iter_content(chunk_size=1024):
                tmp_story = tmp_story + chunk
                chunk_size += len(chunk)
                self.process_lock.acquire()
                self.downloaded_size += len(chunk)
                self.process_lock.release()
                if chunk_size > 1024 * 1024:
                    # print(headers)
                    # print("start write")
                    self.lock.acquire()
                    self.fd.seek(start)
                    self.fd.write(tmp_story)
                    self.fd.flush()
                    # print("end write")
                    start += chunk_size
                    chunk_size = 0
                    tmp_story = bytes()
                    self.lock.release()

        except requests.exceptions.RequestException as e:
            print(e)
        except requests.exceptions.ConnectionError as e:
            print(e)
        else:
            self.lock.acquire()
            self.fd.seek(start)
            self.fd.write(tmp_story)
            self.lock.release()
            print("%s-%s download success"%(start,end))


    def download(self,start,end):
       
        step = (end - start) // 32
        time_stamp = [i for i in range(start, end, step)]
        if time_stamp[-1] < end:
            time_stamp.append(end)
        # time_stamp = [start, start + (end - start) // 2  , end]
        # print(time_stamp)
        ind = 0
        while ind < len(time_stamp) - 1:
            sub_start = time_stamp[ind]
            sub_end = time_stamp[ind + 1]
            headers = {'Range':'Bytes=%d-%d'%(sub_start, sub_end),'Accept-Encoding':'*'}
            # print(headers)
            # print(type(self.fd))
            ind += 1
            try:
                session = requests.session()
                request_retry = requests.adapters.HTTPAdapter(max_retries=8)
                session.mount('https://', request_retry) 
                session.mount('http://', request_retry)
                #res = requests.get(self.url,headers=headers, stream=True, timeout=60)
                res = session.get(self.url,headers=headers, stream=True, timeout=60)
                code = res.status_code
                # 将文件指针移动到传入区间开始的位置
                tmp_story = bytes()
                chunk_size = 0
                for chunk in res.iter_content(chunk_size=1024):
                    tmp_story = tmp_story + chunk
                    chunk_size += len(chunk)
                    self.process_lock.acquire()
                    self.downloaded_size += len(chunk)
                    self.process_lock.release()
                    if chunk_size > 10 * 1024:
                        # print(headers)
                        # print("start write")
                        self.lock.acquire()
                        self.fd.seek(sub_start)
                        self.fd.write(tmp_story)
                        # print(len(tmp_story))
                        # print("end write")
                        sub_start += chunk_size
                        chunk_size = 0
                        tmp_story = bytes()
                        self.lock.release()

            except requests.exceptions.RequestException as e:
                time.sleep(5)
                print(e)
            except requests.exceptions.ConnectionError as e:
                time.sleep(5)
                print(e)
            else:
                self.lock.acquire()
                self.fd.seek(sub_start)
                self.fd.write(tmp_story)
                self.lock.release()
        # print("%s-%s download success"%(start,end))
        self.thread_over_n += 1


    def run(self):
        self.fd = open(self.name,"wb")
        self.lock = Lock() 

        thread_list = []
        n = 0

        for ran in self.get_range():
         
            # 获取每个线程下载的数据块
            start,end = ran
            n += 1
            thread = threading.Thread(target=self.download,args=(start,end))
            thread.start()
            thread_list.append(thread)

        thread = threading.Thread(target=self.display_processed)
        thread.start()
        thread_list.append(thread)
        for i in thread_list:
            # 设置等待，避免上一个数据块还没写入，下一数据块对文件seek，会报错
            i.join()

        self.fd.close()
    
    def display_processed(self):
        while True:
            self.process_lock.acquire()
            dow_percent = self.downloaded_size / self.total 
            self.process_lock.release()
            if  self.thread_over_n == self.num: 
                break;
            print('\r{:.2f}'.format(dow_percent), end='', flush=True)
            #print(dow_percent)
            time.sleep(5)

if __name__ == '__main__':
    url = 'http://ok.renzuida.com/2003/DA%E8%B5%A2%E5%AE%B6.HD1280%E9%AB%98%E6%B8%85%E5%9B%BD%E8%AF%AD%E4%B8%AD%E5%AD%97%E7%89%88.mp4'
    # url = 'http://vip.zuiku8.com/1808/%E4%B8%80%E7%94%9F%E6%89%80%E7%88%B1%20%E9%A5%AD%E5%88%B6%E7%89%88%20-%20%E5%91%A8%E6%98%9F%E9%A9%B0%E6%9C%B1%E8%8C%B5.mp4'
    downloader = DownLoader(url, './test2.mp4', 16)
    downloader.run()



