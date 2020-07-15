import requests
import re
import time
tmp_dir = r'D:\PythonWork\doupo.html'
f = open(tmp_dir,'a+')
def get_info(url):
    res = requests.get(url)
    if res.status_code == 200:
        contents = re.findall('<div id="content" deep="3">(.*?)</div>',res.content.decode('utf-8'),re.S)
        for content in contents:
            f.write(content+'\n')
        else:
            pass
if __name__ =='__main__':
    urls = ['https://www.5atxt.com/24_24752/{}.html'.format(str(i)) for i in range(20066785,20066787)]
    for url in urls:
        get_info(url)
        time.sleep(1)
f.close()