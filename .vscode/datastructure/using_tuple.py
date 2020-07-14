#!/usr/bin/python
# Filename: using_list.py

zoo = ('wolf','elephant','penguin')
print('The number of animals in the zoo is',len(zoo))

zoo_new = ('monkey','dolphin',zoo)
print('The number of animals in the zoo is',len(zoo_new))

print("all animail in new zoo are",zoo_new)

print("animail brought from old zoo are",zoo_new[2])

print("last animail brought from old zoo is",zoo_new[2][2])