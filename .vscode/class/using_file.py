#!/usr/bin/python
# Filename: using_file.py

poem = '''\
Programing is fun
When the work is done
if you wanna make your work also fun:
        Use Python!
'''
dir = r'D:\Python\workspace\.vscode\class\poem.txt'

f = open(dir, 'r')
while True:
    line = f.readline()
    if len(line) == 0:
        break
    print(line)
f.close()

f = open(dir, 'a')
f.write(poem)
f.close()

f = open(dir, 'r')
while True:
    line = f.readline()
    if len(line) == 0:
        break
    print(line)
f.close()