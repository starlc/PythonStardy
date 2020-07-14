#!/usr/bin/python
# Filename: backup_ver2.py

import os
import time


source_list = [
    r'D:\Python\workspace\.vscode\model\mymodule_demo.py',
    r'D:\Python\workspace\.vscode\model\mymodule_demo2.py'
]

target_dir = r'D:\temp\backup-'
count = 0
for source in source_list:
    count += 1
    today = target_dir+time.strftime('%Y%m%d')
    now = time.strftime('%Y%m%d')
    if not os.path.exists(today):
        os.mkdir(today)
        print('Successfully created dir',today)
    target = today + os.sep + now +str(count) + '.zip'
    print('Target is %s' % target)
    #target_dir + time.strftime('%Y%m%d%H%M%S') + '.zip'

    zip_command = "makecab  " + source + "  " + target
    #"Info-Zip -qr '%s' %s" % (target, ' '.join(source))

    if (os.system(zip_command).bit_length()) == 0:
        print("成功备份到", target)

    else:
        print("备份失败")
