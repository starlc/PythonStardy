#!/usr/bin/python
# Filename: pickling.py

import pickle as p

#shoplistfile = 'shoplist.data'
data = ['aa', 'bb', 'cc'] 
dir = r'D:\Python\workspace\.vscode\class\poem.txt'
f = open(dir,'wb')
p.dump(data,f)
f.close()

del data

f = open(dir,'rb')
storedlist = p.load(f)
print(storedlist)