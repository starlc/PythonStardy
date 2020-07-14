#!/usr/bin/python
# Filename: continue.py

while True:
    s = input("Enter something:")
    if s=='quit':
        break
    if len(s)<3:
        continue
    print('length of the string is',len(s))

print('done')