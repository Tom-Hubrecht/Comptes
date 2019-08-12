#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Define a class for the date fields


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
            self.date[self.crs] = cnt[:self.crs] + ch + cnt[self.crs:]
            self.move_right()

    def cursor_pos(self):
        return 3 + len(self.text) + self.crs

    def get_answer(self):
        return self.date
