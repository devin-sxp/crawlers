#! /usr/bin/python3
#coding:utf-8

#  修改自：
#  https://github.com/ningshu/weiboPicDownloader

import os
import requests
import json
import threading
from concurrent import futures

NICKNAMES_FILE = './weibo_nicknames.txt' #please set this txt as utf-8

HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36'}

def init_data():
    nicknames = []
    with open(NICKNAMES_FILE, 'r', encoding="utf-8") as f:
        data = f.readlines()
        for line in data:
            if(line.split(":")[0].split("(")[0] == "userThreads"):
                userThreads = line.split(":")[1]
            elif(line.split(":")[0].split("(")[0] == "downloadThreads"):
                downloadThreads = line.split(":")[1]
            elif(line.split(":")[0].split("(")[0] == "nicknames"):
                nicknames.extend(line.split(":")[1].split(","))

    return int(userThreads),int(downloadThreads),nicknames

def get(url,stream=False,allow_redirects=True):
    print(url)
    return requests.get(url=url,headers=HEADERS,allow_redirects=allow_redirects)

#保存图片
def save_image(nickname,url):
    save_path = os.path.join('WeiboAlbum',"WeiboAlbum_" + nickname)
    if not os.path.exists(save_path):
        os.makedirs(save_path)
    image_path = os.path.join(save_path,nickname+'_'+url.split('/')[-1]) #list[-x]从后向前取
    if os.path.isfile(image_path):
        print("File already exists: " + image_path)
        return
    response = get(url=url, stream=True)
    image = response.content
    try:
        with open(image_path, "wb") as f:
            f.write(image)
            return
    except IOError:
        print("IO Error\n")
        return

#获取图片url地址
def get_urls(containerid,page):
    url = "https://m.weibo.cn/api/container/getIndex?count=25&page={}&containerid={}".format(page,containerid);
    resp_text = get(url=url).text
    json_data = json.loads(resp_text)
    cards = json_data['cards']
    if not cards:
        return None
    photos = []
    for card in cards:
        mblog = card.get('mblog')
        if mblog:
            pics = mblog.get('pics')
            if pics:
                photos.extend([pic.get('large').get('url') for pic in pics])
    return photos

#通过昵称获取id
def nickname_to_containerid(nickname):
    url = "http://m.weibo.com/n/{}".format(nickname)
    resp = get(url,allow_redirects=False)
    cid = resp.headers['Location'][27:]
    return '107603{}'.format(cid)

def handle_user(nickname,downloadThreads):
    print(nickname + "用户数据初始化中...")
    cid = nickname_to_containerid(nickname)
    if not cid:
        return
    all = [] #存放所有的图片地址
    page = 0
    has_more = True
    while has_more:
        page += 1
        urls = get_urls(containerid=cid,page=page)
        has_more = bool(urls) #bool():空字符串返回false 否则返回true
        if has_more:
            all.extend(urls)
    count = len(all)
    index = 0
    for url in all:
        index += 1
        if(downloadThreads > 1):
            thread_pool = futures.ThreadPoolExecutor(max_workers=downloadThreads)
            future = thread_pool.submit(save_image,nickname,url)
        else:
            save_image(nickname,url)
        print('{} {}/{}'.format(nickname,index,count))        

def main():
    userThreads,downloadThreads,nicknames = init_data()

    if(userThreads == 0):
        thread_list = [] #存放线程
        for nickname in nicknames:
            t = threading.Thread(target=handle_user,args=(nickname,downloadThreads,))
            t.start()
            thread_list.append(t)
        for i in range(len(thread_list)):
            thread_list[i].join()
    else:
        for nickname in nicknames:
            
            if(userThreads > 1):
                thread_pool = futures.ThreadPoolExecutor(max_workers=userThreads)
                thread_pool.submit(handle_user,nickname,downloadThreads)
            elif(userThreads == 1):
                handle_user(nickname,downloadThreads)
    
    exit()
if __name__ == '__main__':
    main()