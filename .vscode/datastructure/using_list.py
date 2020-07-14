#!/usr/bin/python
# Filename: using_list.py

shoplist = ['apple', 'mango', 'carrot', 'banana']

print('I hava', len(shoplist), 'items to purchase')

for item in shoplist:
    print(item)

shoplist.append('rice')
print('my shopping list is now', shoplist)

shoplist.sort()
print('my shopping list is now', shoplist)

print('the first item i will buy is ', shoplist[0])
olditem = shoplist[0]
del shoplist[0]
print('i bought the', olditem)
print('my shopping list is now', shoplist)
