#!/usr/bin/python
# Filename: list_com.py

listone = [2, 3, 4, 8]
listtwo = [2 * i for i in listone if i > 2]
print(listtwo)


def powersum(power, *args):
    '''Return the sum of each argument raised to specified power.'''
    total = 0
    for i in args:
        total += pow(i, power)
    return total

#*用来标识 参数存储在元祖 **则标识字典的键值对
print(powersum(2, 3, 4))
print(powersum(2, 10))

