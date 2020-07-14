#!/usr/bin/python
# Filename: try_except.py

import sys

try:
    s = input('Enter something->')
except EOFError:
    print('\n Why did you do an EOF on me?')
    sys.exit()
except:
    print('\n Some error/exception occurred.')

print('Done')