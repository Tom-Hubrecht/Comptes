#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Import curses module
import curses as crs

# Import fields classes
from Fields import Carousel, Datefield, Textfield


class Form:

    def __init__(self, title):
        self.title = title
        self.items = []
        self.length = 0
        self.width = max(48, len(title) + 4)
        self.cursor = 0
        self.filled = False
        self.cancelled = False
        self.win = crs.newwin(5, 48)

    def _update(self):
        self.win.resize(self.length + 4, self.width)
        self.win.clear()
        self.win.border()
        self._draw_title()
        self._draw_items()

    def _draw_title(self):
        self.win.addch(0, 1, crs.ACS_RTEE)
        self.win.addch(0, 2 + len(self.title), crs.ACS_LTEE)
        self.win.addstr(0, 2, self.title)

    def _draw_items(self):
        pos = 0
        for field in self.items:
            self.win.addstr(pos + 2, 3, field.get_str())
            pos += 1

    def _draw_cursor(self, stdscr):
        my, mx = stdscr.getmaxyx()
        px, py = (mx - 48) // 2, (my - (self.length + 4)) // 2
        pc_y = 2 + py + self.cursor
        pc_x = 3 + px + self.items[self.cursor].cursor_pos()
        stdscr.move(pc_y, pc_x)

    def _display(self, stdscr):
        my, mx = stdscr.getmaxyx()
        px, py = (mx - 48) // 2, (my - (self.length + 4)) // 2
        self.win.mvwin(py, px)
        self.win.overwrite(stdscr)
        self._draw_cursor(stdscr)

    def _resize(self, n):
        self.width = n + 4
        for field in self.items:
            if field.nature == "text":
                field.new_width(n)

    def _move_cursor(self, d):
        # 0: Down, 1: Up, 2: Left, 3: Right
        if d == 0 and self.cursor < (self.length - 1):
            self.cursor += 1
        elif d == 1 and self.cursor > 0:
            self.cursor -= 1
        elif d == 2:
            self.items[self.cursor].move_left()
        elif d == 3:
            self.items[self.cursor].move_right()

    def add_carousel(self, text, items):
        car = Carousel(text, items)
        if car.req_width() > self.width - 4:
            self._resize(car.req_width())

        self.items.append(car)
        self.length += 1
        self._update()

    def add_date(self, text, date):
        dat = Datefield(text, date)
        if dat.req_width() > self.width - 4:
            self._resize(dat.req_width())

        self.items.append(dat)
        self.length += 1
        self._update()

    def add_text(self, text, content='', suggestions=''):
        tex = Textfield(text, content, suggestions)
        if tex.req_width() > self.width - 4:
            self._resize(tex.req_width)
        else:
            tex.new_width(self.width - 4)

        self.items.append(tex)
        self.length += 1
        self._update()

    def fill(self, stdscr):
        self.filled = False
        ch = ""

        self._display(stdscr)

        while not (self.filled or self.cancelled):
            ch = stdscr.get_wch()

            if type(ch) is int:
                if ch == 263:
                    c = self.cursor
                    if self.items[c].nature == "text":
                        self.items[c].del_char()
                elif ch == 261:
                    self._move_cursor(3)
                elif ch == 260:
                    self._move_cursor(2)
                elif ch == 259:
                    self._move_cursor(1)
                elif ch == 258:
                    self._move_cursor(0)
            elif type(ch) is str:
                if ch == "\n":
                    if self.cursor == (self.length - 1):
                        self.filled = True
                    else:
                        self._move_cursor(0)
                elif ch == "\x1b":
                    self.cancelled = True
                elif ch == "\t":
                    # TODO : implement suggestions
                    self._move_cursor(0)
                elif ch.isalnum() or ch in "!#$%&'()*+, -./:;<=>?@[]^_`{|}~":
                    c = self.cursor
                    if self.items[c].nature in ["text", "date"]:
                        self.items[c].add_char(ch)

            if not (self.filled or self.cancelled):
                self._update()
                self._display(stdscr)

    def retrieve(self):
        if self.cancelled:
            return ['' for field in self.items]
        else:
            return [field.get_answer() for field in self.items]
