#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Module for the Form fields classes"""


class Textfield(object):

    def __init__(self, text, content='', suggestions=''):
        self.text = text
        self.content = content
        self.suggest = suggestions
        self.crs = len(content)
        self.nature = "text"
        self.max_width = self.req_width()
        self.s_c = max(0, self.crs - self._max_len())

    def get_str(self):
        """Returns the content to show"""

        max_len = self._max_len()

        # What part of the answer to show
        content = self.content[self.s_c: self.s_c + max_len]

        return self.text + " : " + content

    def get_suggestion(self):
        """Returns the best suggestion given the content"""
        suggest = ""

        return suggest

    def _max_len(self):
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
            if self.s_c + self._max_len() == self.crs:
                self.s_c += 1
            self.crs += 1

    def add_char(self, ch):
        if ch == "©":
            ch = "é"

        cnt = self.content
        self.content = cnt[:self.crs] + ch + cnt[self.crs:]
        self.move_right()

    def del_char(self):
        if self.crs > 0:
            cnt = self.content
            self.content = cnt[:self.crs - 1] + cnt[self.crs:]
            self.move_left()

    def cursor_pos(self):
        return 3 + len(self.text) + self.crs - self.s_c

    def get_answer(self):
        return self.content

    def add_str(self, s):
        self.content += s
        self.crs = len(self.content)
        self.s_c = max(0, self.crs - self._max_len())


class Datefield:

    def __init__(self, text, date):
        self.text = text
        self.date = date
        self.crs = 0
        self.nature = "date"

    def get_str(self):
        return self.text + " : " + self.date

    def req_width(self):
        return 13 + len(self.text)

    def move_left(self):
        if self.crs > 0:
            self.crs -= 1
            if self.date[self.crs] == "/":
                self.crs -= 1

    def move_right(self):
        if self.crs < 9:
            self.crs += 1
            if self.date[self.crs] == "/":
                self.crs += 1

    def add_char(self, ch):
        if ch.isdigit():
            cnt = self.date
            self.date = cnt[:self.crs] + ch + cnt[self.crs + 1:]
            self.move_right()

    def cursor_pos(self):
        return 3 + len(self.text) + self.crs

    def get_answer(self):
        return self.date


class Carousel:

    def __init__(self, text, items):
        self.text = text
        self.pos = 0
        self.size = len(items)
        self.items = items
        self.nature = "carousel"

    def move_left(self):
        self.pos -= 1
        self.pos %= self.size

    def move_right(self):
        self.pos += 1
        self.pos %= self.size

    def get_str(self):
        return self.text + " : < " + self.items[self.pos] + " >"

    def cursor_pos(self):
        return 5 + len(self.text)

    def req_width(self):
        return 7 + len(self.text) + max([len(i) for i in self.items])

    def get_answer(self):
        return self.items[self.pos]
