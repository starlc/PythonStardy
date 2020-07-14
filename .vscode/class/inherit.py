#!/usr/bin/python
# Filename: inherit.py

class SchoolMember:
    '''Represents any school member.'''

    def ___init__(self,name,age):
        self.name = name
        self.age = age
        print('(Initialized SchoolMember: %s)'%self.name)

    def tell(self):
        '''Tell my details.'''
        print('Name:"%s" Age:"%s"'%(self.name,self.age))

class Teacher(SchoolMember):
    '''Represents a teacher.'''
    def __init__(self,name,age,salary):
        SchoolMember.___init__(self,name,age)
        self.salary = salary
        print('(Initialized Teacher: %s)'%self.name)

    def tell(self):
        SchoolMember.tell(self)
        print('Salary:"%d"'%self.salary)

class Student(SchoolMember):
    '''Represents a student.'''
    def __init__(self,name,age,marks):
        SchoolMember.___init__(self,name,age)
        self.marks = marks
        print('(Initialized Student: %s)'%self.name)

    def tell(self):
        SchoolMember.tell(self)
        print('Marks:"%d"'%self.marks)



t = Teacher('teacher_zhang',30,20000)
s = Student('student_wang',20,75)

members = [t,s]
for member in members:
    member.tell()