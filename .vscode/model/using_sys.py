#!/usr/bin/python
# Filename: using_sys.py

import sys

print('The command line args are')
for i in sys.argv:
    print(i)
print('\n\nThe PYTHONPATH is',sys.path,'\n')