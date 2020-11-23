#!/usr/bin/python
# Filename: xiaoao.py
import requests
import re
import time
save_file = r'D:\Python\workspace\xiaoao1.html'
menu_url = 'https://www.5atxt.com/24_24752/'
context_url = 'https://www.5atxt.com/24_24752/{}.html'
reg_context = '<div id="content" deep="3">(.*?)<p>(.*?)</p>(.*?)<div align="center">(.*?)</div>'
reg_context = '<div id="content" deep="3">(.*?)<p>(.*?)</p>(.*?)<div align="center">'
f = open(save_file, 'a+')


def get_info(url, count):
    res = requests.get(url)
    if res.status_code == 200:
        contents = re.findall(reg_context, res.content.decode('utf-8'), re.S)
        #print(contents)
        for content in contents:
            #print(content[2]+'\n')
            f.write(titles[count] + '\n')
            f.write(content[2] + '\n')
        else:
            pass


titles = []


def get_menu(url):
    res = requests.get(url)
    urls = []
    reg_menu = '<dd>(.*?)</dd>'
    reg_menu = '<a.*?href="(.+)".*?>(.*?)</a>'
    reg_menu = '<a style="" href="/24_24752/(.*?).html">(.*?)</a>'
    if res.status_code == 200:
        contents = re.findall(reg_menu, res.content.decode('utf-8'), re.S)
        for content in contents:
            #f.write(content+'\n')
            urls.append(context_url.format(content[0]))
            titles.append(content[1])
        else:
            pass
    print('本次共获取%s个章节' % len(urls))
    return urls


if __name__ == '__main__':
    urls = get_menu(menu_url)
    count = 0
    for url in urls:
        get_info(url, count)
        time.sleep(1)
        count += 1
        # if count==1:break

print('获取结束')
f.close()