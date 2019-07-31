#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Import name suggestion
from Suggestions import prefixMax

# Define a class for the fields


class Field:

    def __init__(self, text, content='', suggestions=''):
        self.text = text
        self.content = content
        self.suggest = suggestions
        self.cursor = len(content)
        self.length = self.textLen() + self.cursor + 3

    def printOut(self, maxWidth, var={}):
        maxLen = maxWidth - 3 - self.textLen()
        if len(self.content) <= maxLen or \
           self.cursor > len(self.content) - maxLen:
            content = self.content[-maxLen:]
        elif self.cursor:
            content = self.content[self.cursor - 1: self.cursor + maxLen - 1]
        else:
            content = self.content[:maxLen]
        suggest = ''
        if self.suggest in var:
            suggest = prefixMax(self.content, var)[len(self.content): maxLen]
        return self.text + ' : ' + content, suggest

    def autoFill(self, var):
        if self.suggest in var:
            suggestion = prefixMax(self.content, var)
            self.content = suggestion
            self.cursor = len(suggestion)

    def addContent(self, ch):
        self.content = self.content[:self.cursor] + ch \
                        + self.content[self.cursor:]
        self.length += 1
        self.cursor += 1

    def moveCursorLeft(self):
        if self.cursor:
            self.cursor -= 1

    def moveCursorRight(self):
        if len(self.content) - self.cursor:
            self.cursor += 1

    def cursorPos(self, maxWidth):
        maxLen = maxWidth - 3 - self.textLen()
        base = self.textLen() + 3
        if len(self.content) <= maxLen:
            return base + self.cursor
        elif self.cursor > len(self.content) - maxLen:
            return base + self.cursor - len(self.content) + maxLen
        elif self.cursor:
            return base + 1
        else:
            return base

    def textLen(self):
        return len(self.text)

    def empty(self):
        return self.content == ''

    def delChar(self):
        if not self.empty() and self.cursor:
            self.content = self.content[:self.cursor - 1] \
                            + self.content[self.cursor:]
            self.length -= 1
            self.cursor -= 1

    def ans(self):
        return self.content
