from bs4 import BeautifulSoup as Bs
from pathlib import Path
import requests as Req
import json as Json
import os as Os
import threading as Th
import time as Time

CTX = 'https://vk.com'
MAX_ACT_THREADS =  20

class DownloadThread (Th.Thread):
    def __init__(self, p, dest):
        Th.Thread.__init__(self)
        self.p = p
        self.dest = dest
    def run(self):
        getPhoto(self.p, self.dest)
        
class GetAlbumThread (Th.Thread):
    def __init__(self, album):
        Th.Thread.__init__(self)
        self.album = album
    def run(self):
        doGetAlbum(self.album)

def doGet(url):
    response = Req.get(url)
    response.encoding = 'utf-8'
    return Bs(response.text, features = 'lxml')
    
def doPost(url, data):
    response = Req.post(url, data)
    json = Json.loads(response.text[4:])
    return Bs(json['payload'][1][1], features = 'lxml')
        
def getPhotoList(url, offset):
    data = data = {'al':1,'al_ad':0,'offset':offset,'part':1,'rev':''}
    soup = doPost(url, data)
    photoList = []
    for a in soup.findAll(name = 'a'):
        photoList.append(a['href'])
    return photoList
    
def doDownload(url, dest):
    url = url.split('|')[0]
    filename = url.split('/')[-1]
    path = dest + filename
    print('开始下载: ', path)
    file = Path(path)
    if not file.exists():
        r = Req.get(url, stream = True)
        with open(path, 'wb') as f:
            for chunk in r.iter_content(chunk_size = 1024):
                if chunk:
                    f.write(chunk)
                    f.flush()
        
def getPhoto(p, dest):
    soup = doGet(CTX + p)
    doDownload(soup.find(name = 'a', attrs = {'class':'mva_item'})['href'], dest)

def createDest(dest):
    file = Path(dest)
    if not file.exists():
        Os.makedirs(file)
    
def doAnalyze(photoList, dest):
    createDest(dest)
    for p in photoList:
        s = 0
        while Th.active_count() > MAX_ACT_THREADS:
            print('活跃线程数量大于', MAX_ACT_THREADS, ', 等待一秒, 现在是第', s, '秒')
            s+=1
            Time.sleep(1)
#        Th.Thread(target = getPhoto, args = (p, dest)).start()
        DownloadThread(p, dest).start() #改为启动一个线程获取照片
        
def getAlbumName(url): #获取相册名
    soup = doGet(url)
    return soup.find(name = 'h4', attrs = {'class':'slim_header'}).get_text()
        
def doGetAlbum(album):
    url = CTX + '/' + album
    albumName = getAlbumName(url)
    print('相册名: ', albumName)
    dest = albumName + '/'
    offset = 0
    photoList = getPhotoList(url, 0)
    offset += len(photoList)
    doAnalyze(photoList, dest)
    while len(photoList) != 0:
        photoList = getPhotoList(url, offset)
        offset += len(photoList)
        doAnalyze(photoList, dest)

#在这里输入相册地址,示例: ['album00_00', 'album11_11]
albums = []
for album in albums:
    doGetAlbum(album)
#    GetAlbumThread(album).start()