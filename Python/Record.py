#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import curses

# Define a class for the records


class Record:

    def __init__(self, key, date, name, amount, nature):
        self.__class__ = Record
        self.key = key
        self.date = date
        self.day = int(date[0]) - 1
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
        self.updateHistory(data)
        data[self.key] = self

    def mod(self, data):
        record = data.pop(self.key)
        if record.nature:
            data['currMonth'] += record.amount
        else:
            data['currMonth'] -= record.amount
        self.updateHistory(data, 0)
        self.add(data)

    def rem(self, data):
        if self.nature:
            data['currMonth'] += self.amount
        else:
            data['currMonth'] -= self.amount
        self.updateHistory(data, 0)
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

    def updateHistory(self, data, eps=1):
        if self.nature == eps:
            for i in range(self.day, 31):
                data['history'][i] -= self.amount
        else:
            for i in range(self.day, 31):
                data['history'][i] += self.amount

    def calcAmount(self):
        am = '-'*self.nature + ('%7.2f' % self.amount).strip()
        return am

    def printOut(self, stdscr, pos, current, key=False):
        _, mx = stdscr.getmaxyx()
        amount = self.calcAmount()
        cle = str(self.key)
        current = ('%7.2f' % current).strip()
        stdscr.addstr(pos, 2, '/'.join(self.date))
        stdscr.addstr(pos, 16 + 6 * key, self.name)
        if key:
            stdscr.addstr(pos, 18 - len(cle), cle)
        if self.nature:
            stdscr.addstr(pos, mx - 15 - len(amount), amount,
                          curses.color_pair(1))
        else:
            stdscr.addstr(pos, mx - 15 - len(amount), amount,
                          curses.color_pair(2))
        stdscr.addstr(pos, mx - 3 - len(current), current)
