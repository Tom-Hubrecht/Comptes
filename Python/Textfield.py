#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Import name suggestion
from Suggestions import prefixMax

# Define a class for the text fields


class Textfield:

    def __init__(self, text, content='', suggestions=''):
        self.text = text
        self.content = content
        self.suggest = suggestions
        self.crs = len(content)
        self.nature = "text"
        self.max_width = self.req_width()
        self.s_c = max(0, self.crs - self.max_len())

    def get_str(self):
        max_len = self.max_len()

        # What part of the answer to show
        content = self.content[self.s_c: self.s_c + max_len]

        return self.text + " : " + content

    def get_suggestion(self):
        suggest = ""

        return suggest

    def max_len(self):
        return self.max_width - 3 - len(self.text)

    def req_width(self):
        return 13 + len(self.text)

    def new_width(self, n):
        self.max_width = n

    def move_left(self):
        if self.crs > 0:
            if self.s_c == self.crs:
                self.s_c -= 1
            self.crs -= 1

    def move_right(self):
        if self.crs < len(self.content):
            if self.s_c + self.max_len() == self.crs:
                self.s_c += 1
            self.crs += 1

    def add_char(self, ch):
        cnt = self.content
        self.content = cnt[:self.crs] + ch + cnt[self.crs:]
        self.move_right()

    def del_char(self):
        if self.crs > 0:
            cnt = self.content
            self.content = cnt[:self.crs - 1] + cnt[self.crs:]
            self.move_left

    def cursor_pos(self):
        return 3 + len(self.text) + self.crs - self.s_c

    def get_answer(self):
        return self.content

    def add_str(self, s):
        self.content += s
        self.crs = len(self.content)
        self.s_c = max(0, self.crs - self.max_len())
