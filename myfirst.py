#from bs4 import BeautifulSoup as Bs
import requests as Req
import json as Json
import time as Time

def doGet(url):
    response = Req.get(url)
    if response.status_code == 200:
#        response.encoding = response.apparent_encoding
        response.encoding = 'utf-8'
        return response
    else:
        print('警告: 状态码不为200 OK')
        return response
    
def doDownload(url, dest):
    filename = url.split('/')[-1]
    fileFormat = url.split('.')[-1]
    r = Req.get(url, stream = True)
    with open(dest + filename, 'wb') as f:
        for chunk in r.iter_content(chunk_size = 1024):
            if chunk:
                f.write(chunk)
                f.flush()
    
def doAnalyze(json):
    for itor in json['data']['recommend']:
         print('昵称:', itor['uname'], ', 标题:', itor['title'])
         doDownload(url = itor['pic'], dest = 'pic/')
         print('下载直播间封面完成')
         doDownload(url = itor['face'], dest = 'face/')
         print('下载头像完成')
         
    
def main():
    #url = 'https://www.baidu.com'
    url = 'https://api.live.bilibili.com/room/v1/RoomRecommend/biliIndexRecList'
    response = doGet(url)
    json = Json.loads(response.text)
    if json['code'] == 0:
        print('获取正在直播列表成功, code:', json['code'], ', message:', json['message'], ', msg:', json['msg'])
        doAnalyze(json)
    else:
        print('获取正在直播列表失败, code:', json['code'], ', message:', json['message'], ', msg:', json['msg'])
    #html = response.text
    #soup = Bs(html, features = 'lxml')
    #print(soup.prettify())
    
if __name__ == '__main__':
    while True:
        main()
        print('让我睡半分钟...')
        Time.sleep(30)