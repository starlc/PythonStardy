#!/usr/bin/python
# Filename: using_dict.py

abc = {
    'key1':'val1',
    'key2':'val2',
    'key3':'val3',
}

print("abc's key1 is %s"%abc['key1'])
abc['key4']= 'val4'

del abc['key3']
for name,address in abc.items():
    print('key is %s,value is %s'%(name,address))


for key,value in abc.items():
    print('key is %s,value is %s'%(key,value))

if 'key1' in abc:
    print('\nkey1\'s value is %s'%abc['key1'])


print(abc['key1'])