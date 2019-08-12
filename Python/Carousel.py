#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Define a class for the carousels


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
