#!/usr/bin/python
# Filename: simplestclass.py

class Person:
    def sayHi(self):
        print('Hello, My name is %s ,how are you'%self.name)

    def __init__(self, name):
        self.name = name

p = Person('zhangsan')
print(p)
p.sayHi()