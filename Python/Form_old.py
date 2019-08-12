#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Import necessary modules
import curses as crs

# Import Field class
from Field import Field


class Form:

    def __init__(self, title, var={}, items=[]):
        self.title = title
        self.items = []
        self.length = 0
        self.width = 48
        self.cursor = 0
        self.filled = False
        self.cancelled = False
        self.win = crs.newwin(5, 48)
        for item in items:
            if type(item) is Field:
                self.addField(item, var)

    def _update(self, var={}):
        self.win.resize(self.length + 4, self.width)
        self.win.clear()
        self.win.border()
        self.win.addstr(self.length + 2, self.width - 4, 'Ok')
        self._printTitle()
        pos = 0
        for item in self.items:
            if type(item) is Field:
                text, suggestion = item.printOut(self.width - 4, var)
                self.win.addstr(pos + 2, 2, text)
                self.win.addstr(pos + 2, 2 + len(text), suggestion,
                                crs.color_pair(4))
            pos += 1

    def addButton(self, button, var={}):
        self.items += [button]
        self.length += 1
        self._update(var)

    def addField(self, field, var={}):
        self.items += [field]
        # Guarantee at least 10 chars for the answer
        self.width = max(self.width, field.textLen() + 17)
        self.length += 1
        self._update(var)

    def changeTitle(self, newTitle):
        self.title = newTitle

    def _display(self, stdscr):
        my, mx = stdscr.getmaxyx()
        px, py = (mx - 48) // 2, (my - (self.length + 4)) // 2
        self.win.mvwin(py, px)
        self.win.overwrite(stdscr)
        self._printCursor(stdscr)

    def _moveCursor(self, var={}, auto=False, val=1):
        if self.length - self.cursor and auto:
            self.items[self.cursor].autoFill(var)
        self.cursor += val
        self.cursor %= self.length + 1

    def _printCursor(self, stdscr):
        my, mx = stdscr.getmaxyx()
        px, py = (mx - 48) // 2, (my - (self.length + 4)) // 2
        pc = self.cursor
        if pc == self.length:
            stdscr.move(py + pc + 2, px + self.width - 2)
        else:
            length = self.items[pc].cursorPos(self.width - 4)
            stdscr.move(py + pc + 2, px + length + 2)

    def _printTitle(self):
        st = 25 - (len(self.title) // 2)
        en = st + len(self.title)
        self.win.addch(0, st - 1, crs.ACS_RTEE)
        self.win.addch(0, en, crs.ACS_LTEE)
        self.win.addstr(0, st, self.title)

    def fill(self, stdscr, var={}):
        self.filled = False
        self.cursor = 0
        ch = ''
        chars = var['alphabet']
        self._display(stdscr)
        while not self.filled:
            ch = stdscr.getkey()
            c = self.cursor
            if ch == '\n':
                if c == self.length:
                    self.filled = True
                else:
                    self._moveCursor(var, True)
            elif ch == '\x1b':
                self.cancelled = True
                self.filled = True
            elif ch == 'KEY_LEFT' and (self.length - c):
                self.items[c].moveCursorLeft()
            elif ch == 'KEY_RIGHT' and (self.length - c):
                self.items[c].moveCursorRight()
            elif ch == 'KEY_UP':
                self._moveCursor(var, val=-1)
            elif ch == 'KEY_DOWN':
                self._moveCursor(var)
            elif ch == '\t':
                self._moveCursor(var, True)
            elif ch in chars and (self.length - c):
                self.items[c].addContent(chars[ch])
            elif ch == 'KEY_BACKSPACE' and (self.length - c):
                self.items[c].delChar()
            if not self.filled:
                self._update(var)
                self._display(stdscr)

    def retrieve(self):
        if self.cancelled:
            return ['' for field in self.items]
        else:
            return [field.ans() for field in self.items]
