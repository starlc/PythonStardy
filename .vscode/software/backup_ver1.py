#!/usr/bin/python
# Filename: backup_ver1.py
import os
import time
source_list = [
    r'D:\Python\workspace\.vscode\model\mymodule_demo.py',
    r'D:\Python\workspace\.vscode\model\mymodule_demo2.py'
]

target_dir = 'D:/temp/backup'
target_dir = r'D:\temp\backup'
count = 0
for source in source_list:
    count += 1
    target = target_dir + time.strftime('%Y%m%d%H%M%S') + str(count) + '.zip'
    print('Target is %s' % target)
    #target_dir + time.strftime('%Y%m%d%H%M%S') + '.zip'

    zip_command = "makecab  " + source + "  " + target
    #"Info-Zip -qr '%s' %s" % (target, ' '.join(source))

    if (os.system(zip_command).bit_length()) == 0:
        print("成功备份到", target)

    else:
        print("备份失败")


count +=1
target = target_dir + time.strftime('%Y%m%d%H%M%S') + str(count) + '.zip'
zip_command = "makecab  " + ','.join(source_list) + "  " + target
print("备份命令", zip_command)
if (os.system(zip_command).bit_length()) == 0:
    print("成功备份到", target)
else:
    print("备份失败")