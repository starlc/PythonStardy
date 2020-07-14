#!/usr/bin/python
# Filename: func_return.py

#没有返回值 等价于 return None  
# pass 表示空语句块
def maximun(x,y):
    if x>y:
        return x
    else:
        return y

print('the max val is:',maximun(3,5))