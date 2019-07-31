#!/usr/bin/env python3
# -*- coding: utf-8 -*-


# Prefix and name suggestions


# Check if x is a prefix of s

def isPrefix(x, s):
    return x == s[:len(x)]


# Return the most frequent name for the year with x as a prefix

def prefixMax(x, var):
    names = var['names']
    nameIter = filter(lambda s: isPrefix(x, s), names)
    freq = 0
    result = ''
    for name in nameIter:
        if names[name] > freq:
            freq = names[name]
            result = name
    return result


# Add a name to the names dict

def addName(name, var):
    if name in var['names']:
        var['names'][name] += 1
    else:
        var['names'][name] = 1


# Remove a name from the dict

def remName(name, var):
    if var['names'][name] == 1:
        del var['names'][name]
    else:
        var['names'][name] -= 1
