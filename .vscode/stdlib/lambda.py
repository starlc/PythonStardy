#!/usr/bin/python
# Filename: lambda.py


def make_repeater(n):
    return lambda s: s * n


twice = make_repeater(2)

print(twice('word'))
print(twice(5))

exec('print(\'helloworld\')')  #python语句
print(eval("2*3"))  #有效的Python表达式

mylist = ['a']
assert len(mylist) >= 1
mylist.pop()
#assert len(mylist)>=1

i = []
i.append('item1')
print(repr(i))  #eval(repr(obj))==obj
