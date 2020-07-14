#!/usr/bin/python
# Filename: objvar.py


class Person:
    '''Represent a person.'''
    population = 0  #类变量

    def __init__(self, name):  #name 为对象的变量
        '''Initializes the person's data.'''
        self.name = name
        print('(Initializing %s)' % self.name)
        Person.population += 1

    def __del__(self):#在对象消逝的时候被调用
        '''I am dying.'''
        print('%s says bye.' % self.name)
        Person.population -= 1

        if Person.population == 0:
            print('I am the last one')
        else:
            print('There are still %d people left.' % Person.population)

    def sayHi(self):
        '''Greeting by the person.
        
        Really,that's all it does.'''
        print('Hi,my name is %s.' % self.name)

    def howMany(self):
        '''Prints the current population.'''
        if Person.population == 1:
            print('I am the only person here.')
        else:
            print('We have %d person here.' % Person.population)


zhangsan = Person('zhangsan')
zhangsan.sayHi()
zhangsan.howMany()

kar = Person('kar')
kar.sayHi()
kar.howMany()

zhangsan.sayHi()
zhangsan.howMany()
