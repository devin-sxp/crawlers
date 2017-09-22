import urllib.request as u
import re,os
from bs4 import BeautifulSoup

HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36'}

tieId = "5331063916"

def get_all_page_url(url):
    print("初始化中...")
    soup = BeautifulSoup(get_html_content(url),'lxml')
    pageInput = soup.find_all('input',attrs={'class':'jump_input_bright'})[0]
    pages = str(pageInput).split("max-page=\"")[1].split("\"")[0]
    urls = []
    for i in range(int(pages)):
        urls.append(url+"?pn="+str(i+1))
    
    return urls

def get_html_content(url):
    print("正在处理->"+url)
    req = u.Request(url=url,headers=HEADERS)
    html = u.urlopen(req)
    content = html.read()
    html.close()
    return str(content)

def get_image_to_save(info,name_index):
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
    tieId = input("请输入帖子id：")
    name_index = 1
    urls = get_all_page_url("http://tieba.baidu.com/p/"+tieId)

    for url in urls:
        info = get_html_content(url)
        name_index = get_image_to_save(info,name_index)
    exit()

if __name__ == "__main__":
    main()