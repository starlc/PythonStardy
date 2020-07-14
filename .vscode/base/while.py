#!/usr/bin/python
# Filename: while.py

number = 23
running = True
while running:
    guess = int(input('Enter an integer:'))
    if guess == number:
        print('get it')
        running = False
    elif guess < number:
        print('big more')
    else:
        print('a little')
        pass
else:
    print("结束循环")