#!/usr/bin/python
# -*- coding: utf-8 -*-
from json import loads


try:
    filename = "keys.keys"
    with open(filename) as file:
        keys = (True, loads(file.read()))
except BaseException as err:
    keys = (False, err)
    
    
def get_key(keyname):
    if keys[0]:
        return (True, keys[1][keyname])
    else:
        return keys
    
    
if __name__ == "__main__":
    print("Available keys:")
    for key in keys[1].keys():
        print("KEYNAME:", key)
