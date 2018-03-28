#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Import necessary modules
import curses


# Define a class for the records

class Record:

    def __init__(self, key, date, name, amount, nature):
        self.__class__ = Record
        self.key = key
        self.date = date
        self.name = name
        self.amount = amount
        # 0 : Credit
        # 1 : Debit
        self.nature = nature

    def __repr__(self):
        rep = '/'.join(self.date) + ' | ' + self.name.ljust(30)
        rep += "\t| Amount : " + '-'*self.nature + str(self.amount).ljust(5)
        rep += "\t| Key : " + str(self.key)
        return rep

    def add(self, data):
        if self.nature:
            data['currMonth'] -= self.amount
        else:
            data['currMonth'] += self.amount
        data[self.key] = self

    def mod(self, data):
        record = data.pop(self.key)
        if record.nature:
            data['currMonth'] += record.amount
        else:
            data['currMonth'] -= record.amount
        self.add(data)

    def rem(self, data):
        if self.nature:
            data['currMonth'] += self.amount
        else:
            data['currMonth'] -= self.amount
        del data[self.key]

    def save(self):
        key = str(self.key)
        date = '_'.join(self.date)
        name = self.name
        amount = str(self.amount)
        nature = str(self.nature)
        attr = [key, date, name, amount, nature]
        return ';'.join(attr)

    def show(self, key=False):
        rep = '/'.join(self.date) + ' | ' + self.name.ljust(30)
        rep += "\t| " + [' ', '-'][self.nature] + str(self.amount).ljust(5)
        if key:
            rep += "\t| Key : " + str(self.key)
        print(rep)

    def printOut(self, stdscr, pos, current):
        my, mx = stdscr.getmaxyx()
        stdscr.addstr(pos, 2, '/'.join(self.date))
        stdscr.addstr(pos, 16, self.name)
        stdscr.addstr(pos, mx - 21 - self.nature,
                      '-'*self.nature + str(self.amount))
        stdscr.addstr(pos, mx - 9, str(current))


class Form:

    def __init__(self, title, items=[]):
        self.title = title
        self.items = []
        self.length = 0
        self.cursor = 0
        self.filled = False
        self.win = curses.newwin(5, 48)
        for item in items:
            if type(item) is Button:
                self.addButton(item)
            elif type(item) is Field:
                self.addField(item)

    def _update(self):
        self.win.resize(self.length + 4, 48)
        self.win.clear()
        self.win.border()
        self.win.addstr(self.length + 2, 44, 'Ok')
        self._printTitle()
        pos = 0
        for item in self.items:
            if type(item) in [Button, Field]:
                self.win.addstr(pos + 2, 2, str(item))
            pos += 1

    def addButton(self, button):
        self.items += [button]
        self.length += 1
        self._update()

    def addField(self, field):
        self.items += [field]
        self.length += 1
        self._update()

    def changeTitle(self, newTitle):
        self.title = newTitle

    def _display(self, stdscr):
        my, mx = stdscr.getmaxyx()
        px, py = (mx - 48) // 2, (my - (self.length + 4)) // 2
        self.win.mvwin(py, px)
        self.win.overwrite(stdscr)
        self._printCursor(stdscr)

    def _moveCursor(self, val=1):
        self.cursor += val
        self.cursor %= self.length + 1

    def _printCursor(self, stdscr):
        my, mx = stdscr.getmaxyx()
        px, py = (mx - 48) // 2, (my - (self.length + 4)) // 2
        pc = self.cursor
        if pc == self.length:
            stdscr.move(py + pc + 2, px + 46)
        else:
            length = self.items[pc].length()
            stdscr.move(py + pc + 2, px + length + 2)

    def _printTitle(self):
        st = 25 - (len(self.title) // 2)
        en = st + len(self.title)
        self.win.addch(0, st - 1, curses.ACS_RTEE)
        self.win.addch(0, en, curses.ACS_LTEE)
        self.win.addstr(0, st, self.title)

    def fill(self, stdscr, chars):
        self.filled = False
        self.cursor = 0
        ch = ''
        self._display(stdscr)
        while not self.filled:
            ch = stdscr.getkey()
            c = self.cursor
            if ch == '\n':
                if c == self.length:
                    self.filled = True
                else:
                    self._moveCursor()
            elif ch == 'KEY_UP':
                self._moveCursor(val=-1)
            elif ch == 'KEY_DOWN' or ch == '\t':
                self._moveCursor()
            elif ch in chars and (self.length - c):
                self.items[c].addContent(ch)
            elif ch == 'KEY_BACKSPACE' and (self.length - c):
                self.items[c].delChar()
            if not self.filled:
                self._update()
                self._display(stdscr)

    def retrieve(self):
        results = []
        for field in self.items:
            results.append(field.ans())
        return results


class Field:

    def __init__(self, text, content=''):
        self.text = text
        self.content = content

    def __str__(self):
        return self.text + ' : ' + self.content

    def length(self):
        return len(self.content) + len(self.text) + 3

    def addContent(self, ch):
        self.content += ch

    def empty(self):
        return self.content == ''

    def delChar(self):
        if not self.empty():
            self.content = self.content[:-1]

    def ans(self):
        return self.content


class Button:

    def __init__(self, name, entries):
        self.name = name
        self.entries = entries
        self.length = len(entries)
        self.pos = 0

    def __str__(self):
        return '<' + self.entries[self.pos] + '>'

    def prev(self):
        self.pos = (self.pos - 1) % self.length()

    def suiv(self):
        self.pos = (self.pos + 1) % self.length()

    def addEntry(self, entry):
        self.entries += entry
        self.length += 1

    def ans(self):
        return self.entries[self.pos]
