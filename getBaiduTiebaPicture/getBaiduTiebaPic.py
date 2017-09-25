# -*- coding: UTF-8 -*-
import urllib.request as u
from urllib.parse import quote
import re,os
from bs4 import BeautifulSoup

HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36'}

def get_now_tieba_urls(url):
    reg = r'class="red_text">(.+?)</span>'
    pat = re.compile(reg)
    tieCount = re.findall(pat,get_html_content(url))[0]
    page = int(tieCount)//50 + 1
    tieIdsList = []
    print("收集主题帖链接中...\n")
    for i in range(page):
        '''
        <a href="/p/****" title="*" target="_blank" class="j_th_tit ">
        '''
        reg = r'<a href="/p/(.+?)"'
        pat = re.compile(reg)
        tieIds = re.findall(pat,get_html_content(url+"&pn="+str(i*50)))#获取帖子id
        tieIdsList[len(tieIdsList):len(tieIdsList)] = tieIds
    return tieIdsList

def get_all_page_url(url):
    print("收集图片链接中...")
    soup = BeautifulSoup(get_html_content(url),'lxml')
    pageInputList = soup.find_all('input',attrs={'class':'jump_input_bright'})
    pages = 0
    if pageInputList == []:
        pages = 1
    else:
        pages = str(pageInputList[0]).split("max-page=\"")[1].split("\"")[0]
    urls = []
    for i in range(int(pages)):
        urls.append(url+"?pn="+str(i+1))
    
    return urls

def get_html_content(url):
    print("正在处理->"+url)
    # quote(url, safe='/:?=&')转换url解决其中含中文问题
    req = u.Request(url=quote(url, safe='/:?=&'),headers=HEADERS)
    html = u.urlopen(req)
    content = html.read()
    html.close()
    return str(content)

def get_image_to_save(info,name_index,tieId):
    '''
    <img class="BDE_Image" 
    src="http://imgsrc.baidu.com/forum/w%3D580/sign=aac8530f43540923aa696376a259d1dc/019f9782b9014a90d17aeb91a3773912b21beeda.jpg" 
    size="44337" changedsize="true" width="560" height="315"  
    style="cursor: url(&quot;http://tb2.bdstatic.com/tb/static-pb/img/cur_zin.cur&quot;), pointer;">
    '''
    save_path = os.path.join('tieBa',"pic_" + tieId)
    if not os.path.exists(save_path):
        os.makedirs(save_path)
    #1:BeautifulSoup方式
    soup = BeautifulSoup(info,'lxml')
    allImage = soup.find_all('img',attrs={'class':'BDE_Image'})
    for img in allImage:
        imageUrl = img['src']
        if imageUrl.find("baidu.com") != -1: #精确，为了去掉广告图片

            #网络命名方式
            imgName = imageUrl.split("/")[-1]
            imgPath = os.path.join(save_path,imgName)
            if os.path.isfile(imgPath):
                print("File already exists: " + imgPath)
            else:
                u.urlretrieve(imageUrl,imgPath)

            #自定义命名方式
            # imgPath = os.path.join(save_path,str(name_index) + ".jpg")
            # if os.path.isfile(imgPath):
            #     print("File already exists: " + imgPath)
            # else:
            #     u.urlretrieve(imageUrl,imgPath)

            name_index+=1

    return name_index

    #2:正则匹配方式
    # reg = r'class="BDE_Image" src="(.+?\.jpg)"'
    # pat = re.compile(reg)
    # images_url = re.findall(pat,info)
    # print(images_url)

    # for url in images_url:
    #     u.urlretrieve(url,"getBaiduTiebaPicture/Timage/%s.jpg" % i)
    #     i+=1

def main():
    tieIdsList = []
    name_index = 1
    fileDirName = ""
    selected = input("请选择你的操作:\n1、获取整个贴吧所有图片\n2、获取某个主题帖的所有图片\n")

    if selected == '1':
        tieBaName = input("请输入贴吧名字:")
        fileDirSelected = input("请选择文件夹命名方式:\n1、按贴吧命名\n2、按主题帖命名\n")
        if fileDirSelected == '1':
            fileDirName = tieBaName
        else:
            pass
        tieIdsList = get_now_tieba_urls("http://tieba.baidu.com/f?kw="+tieBaName)

    elif selected == '2':
        tieId = input("请输入帖子id：")
        tieIdsList.append(tieId)
    else:
        print("\n没有此项选择")
        exit()
       
    for tieId in tieIdsList:
        urls = get_all_page_url("http://tieba.baidu.com/p/"+tieId)
        if fileDirName != "":
            for url in urls:
                info = get_html_content(url)
                name_index = get_image_to_save(info,name_index,fileDirName)
        else:
            for url in urls:
                info = get_html_content(url)
                name_index = get_image_to_save(info,name_index,tieId)

    print("下载完毕！")
    exit()

if __name__ == "__main__":
    main()