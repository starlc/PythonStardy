#!/usr/bin/python
# Filename: seq.py

shoplist=['apple','mango','carrot','banana','moneky']
b = 0
for i in range(0,4):
    print('item %s is %s'%(b,shoplist[b]))
    b +=1

# 切片 从第一个参数位置开始 到底二个参数前结束
print('item 1 to 3 is',shoplist[1:3])
print('item 2 to end is',shoplist[2:])
print('item 1 to -1 is',shoplist[1:-1])
print('item start to end is',shoplist[:])


