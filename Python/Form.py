#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Module for the Form class"""


# Import curses module
import curses as crs

# Import fields classes
from Fields import Carousel, Datefield, Textfield


class Form(object):
    """Forms with Textfields, Datefields or Carousels"""
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
        m_y, m_x = stdscr.getmaxyx()
        p_x, p_y = (m_x - 48) // 2, (m_y - (self.length + 4)) // 2
        pc_y = 2 + p_y + self.cursor
        pc_x = 3 + p_x + self.items[self.cursor].cursor_pos()
        stdscr.move(pc_y, pc_x)

    def _display(self, stdscr):
        m_y, m_x = stdscr.getmaxyx()
        p_x, p_y = (m_x - 48) // 2, (m_y - (self.length + 4)) // 2
        self.win.mvwin(p_y, p_x)
        self.win.overwrite(stdscr)
        self._draw_cursor(stdscr)

    def _resize(self, _n):
        self.width = _n + 4
        for field in self.items:
            if field.nature == "text":
                field.new_width(_n)

    def _move_cursor(self, _d):
        # 0: Down, 1: Up, 2: Left, 3: Right
        if _d == 0 and self.cursor < (self.length - 1):
            self.cursor += 1
        elif _d == 1 and self.cursor > 0:
            self.cursor -= 1
        elif _d == 2:
            self.items[self.cursor].move_left()
        elif _d == 3:
            self.items[self.cursor].move_right()

    def add_carousel(self, text, items):
        """Add a Carousel to the Form"""
        car = Carousel(text, items)
        if car.req_width() > self.width - 4:
            self._resize(car.req_width())

        self.items.append(car)
        self.length += 1
        self._update()

    def add_date(self, text, date):
        """Add a Datefield to the Form"""
        dat = Datefield(text, date)
        if dat.req_width() > self.width - 4:
            self._resize(dat.req_width())

        self.items.append(dat)
        self.length += 1
        self._update()

    def add_text(self, text, content='', suggestions=''):
        """Add a Textfield to the Form"""
        tex = Textfield(text, content, suggestions)
        if tex.req_width() > self.width - 5:
            self._resize(tex.req_width)
        else:
            tex.new_width(self.width - 5)

        self.items.append(tex)
        self.length += 1
        self._update()

    def fill(self, stdscr):
        """Draws the Form and allows it to be filled"""
        self.filled = False
        _ch = ""

        self._display(stdscr)

        while not (self.filled or self.cancelled):
            _ch = stdscr.get_wch()

            if isinstance(_ch, int):
                if _ch == 263:
                    _c = self.cursor
                    if self.items[_c].nature == "text":
                        self.items[_c].del_char()
                elif _ch == 261:
                    self._move_cursor(3)
                elif _ch == 260:
                    self._move_cursor(2)
                elif _ch == 259:
                    self._move_cursor(1)
                elif _ch == 258:
                    self._move_cursor(0)
            elif isinstance(_ch, str):
                if _ch == "\n":
                    if self.cursor == (self.length - 1):
                        self.filled = True
                    else:
                        self._move_cursor(0)
                elif _ch == "\x1b":
                    self.cancelled = True
                elif _ch == "\t":
                    # TODO : implement suggestions
                    self._move_cursor(0)
                elif _ch.isalnum() or _ch in "!#$%&'()*+, -./:;<=>?@[]^_`{|}~":
                    _c = self.cursor
                    if self.items[_c].nature in ["text", "date"]:
                        self.items[_c].add_char(_ch)

            if not (self.filled or self.cancelled):
                self._update()
                self._display(stdscr)

    def retrieve(self):
        """Returns the answers of the Forms in a list"""
        if self.cancelled:
            return ['' for field in self.items]

        return [field.get_answer() for field in self.items]
