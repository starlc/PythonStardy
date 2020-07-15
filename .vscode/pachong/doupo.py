import requests
import re
import time
tmp_dir = r'D:\PythonWork\doupo.txt'
f = open(tmp_dir,'a+')
def get_info(url):
    res = requests.get(url)
    if res.status_code == 200:
        contents = re.findall('<p>(.*?)</p>',res.content.decode('utf-8'),re.S)
        for content in contents:
            f.write(content+'\n')
        else:
            pass
if __name__ =='__main__':
    urls = ['https://www.5atxt.com/24_24752/{}.html'.format(str(i)) for i in range(20066785,21488000)]
    for url in urls:
        get_info(url)
        time.sleep(1)
f.close()