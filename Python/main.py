#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Import necessary modules
import os
import decimal as dc
import datetime
import curses
from Classes import Record, Form, Field


def init():
    # Initialize variables
    cwd = os.getcwd()
    dc.getcontext().prec = 50
    now = datetime.datetime.now()
    month = '%02d' % now.month
    year = str(now.year)

    months = ['01', '02', '03', '04', '05', '06',
              '07', '08', '09', '10', '11', '12']

    strings = {
        'changeKey': 'Enter the key you want to change',
        'changeAmount': 'Change the amount of the operation : ',
        'changeNature': 'Change the nature of the operation : ',
        'changeName': 'Change the name of the operation : ',
        'removeKey': 'Enter the key you want to remove, leave void to cancel',
        'removeRecord': 'Record to remove :',
        'selectName': 'Enter the name of the operation :',
        'selectNat': 'Enter the nature, default is 1:\n0 : Credit\n1 : Debit',
        'selectAmount': 'Enter the Amount of the operation : ',
        'selectYear': 'Enter the requested year, default is : ',
        'selectMonth': 'Enter the requested month, default is : ',
        'selectLoad': 'Enter what you want to load, default is 0 :\n0 : Year'
        + '\n1-12 : Month',
            }

    keyWords = {
            'load': _load,
            'add': _add,
            'mod': _mod,
            'exit': _exit,
            'show': _show,
            'save': _save,
            'rem': _rem,
            'debug': _debug,
            # 'help': _help
            }

    var = {
            'cwd': cwd,
            'orYear': year,
            'year': year,
            'orMonth': month,
            'month': month,
            'months': months,
            'loaded': False,
            'data': {},
            'stay': True,
            'alphabet': ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k',
                         'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v',
                         'w', 'x', 'y', 'z', 'A', 'B', 'C', 'D', 'E', 'F', 'G',
                         'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R',
                         'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z', '0', '1', '2',
                         '3', '4', '5', '6', '7', '8', '9', ' ', '-', '_', '.',
                         ',',
                         ],
            }

    return var, strings, keyWords


#
# All the function handling files
#

# Open the requested file and return the file, its path and if it was created

def openFile(fileName, year, cwd):
    filePath = os.path.join(cwd, 'Files', year, '') + fileName
    created = False
    if os.path.isfile(filePath):
        file = open(filePath, 'rt')
    else:
        file = open(filePath, 'xt')
        created = True
    return file, filePath, created


# Read the file and return the data associated with it

def readFile(file, month, year, created, cwd):
    data = {}
    data['prevMonth'] = findPrev(month, year, created, cwd)
    data['currMonth'] = data['prevMonth']
    for line in file:
        line = line.strip('\n')
        content = line.split(";")
        if len(content) == 5:
            key, date, name, amount, nature = content
            key = int(key)
            date = date.split('_')
            amount = dc.Decimal(amount)
            nature = int(nature)
            record = Record(key, date, name, amount, int(nature))
            record.add(data)
    file.close()
    return data


# Writes and closes the file

def closeFile(filePath, data):
    prevMonth, currMonth, sortedData = sortData(data)

    os.remove(filePath)
    file = open(filePath, 'xt')

    file.write(str(prevMonth) + ';' + str(currMonth) + '\n')
    for record in sortedData:
        file.write(record.save() + '\n')
    file.close()


# Find the previous amounts

def findPrev(month, year, created, cwd):
    prevMonth = dc.Decimal(0)
    if month != '01':
        pMonth = '%02d' % (int(month) - 1)
        fileName = pMonth + '_' + year + '.sav'
        filePath = os.path.join(cwd, 'Files', year, '') + fileName
        if os.path.isfile(filePath):
            file = open(filePath, 'rt')
            line = file.readline().strip('\n')
            prevMonth = dc.Decimal(line.split(';')[1])
            file.close()
    else:
        pYear = str(int(year) - 1)
        if os.path.isdir(os.path.join(cwd, 'Files', pYear, '')):
            fileName = '12_' + pYear + '.sav'
            filePath = os.path.join(cwd, 'Files', pYear, '') + fileName
            if os.path.isfile(filePath):
                file = open(filePath, 'rt')
                line = file.readline().strip('\n')
                prevMonth = dc.Decimal(line.split(';')[1])
                file.close()
    if prevMonth == dc.Decimal(0) and not created:
        fileName = month + '_' + year + '.sav'
        filePath = os.path.join(cwd, 'Files', year, '') + fileName
        if os.path.isfile(filePath):
            file = open(filePath, 'rt')
            line = file.readline().strip('\n')
            prevMonth = dc.Decimal(line.split(';')[0])
            file.close()
    return prevMonth


# Sort the records in chronological order

def sortData(data):
    prevMonth = data['prevMonth']
    currMonth = data['currMonth']

    # Transfom the data into a list
    listData = []
    for key in data:
        if key not in ['prevMonth', 'currMonth']:
            listData.append(data[key])

    sortedData = sorted(listData, key=lambda record: record.date[0])

    return prevMonth, currMonth, sortedData


# Create a new key, the smallest possible

def createKey(data):
    key = 1
    while key in data:
        key += 1
    return key


# Load a month, returns its data, path, whether it was created

def loadMonth(var):
    cwd = var['cwd']
    year = var['year']
    month = var['month']
    fileName = month + '_' + year + '.sav'
    file, filePath, created = openFile(fileName, year, cwd)
    if not created:
        data = readFile(file, month, year, created, cwd)
        file.close()
    # Look for older files for the previous amount if we created the file
    else:
        data = {}
        prevMonth = findPrev(month, year, created, cwd)
        # If no older files are found, findPrev returns '0', wich is the right
        # value that is requested
        data['prevMonth'] = prevMonth
        data['currMonth'] = prevMonth
        file.write(str(prevMonth) + ';' + str(prevMonth))
        file.close()
    var['data'][month] = [data, filePath, created]


# Load all months in a given Year

def loadYear(var):
    cwd = var['cwd']
    year = var['year']
    months = var['months']
    month = var['month']
    path = os.path.join(cwd, 'Files', year)
    if not os.path.isdir(path):
        os.makedirs(path)
    for m in months:
        var['month'] = m
        loadMonth(var)
    var['month'] = month


#
# Functions for the main loop
#

# Load a Year or a month

def _load(var, strings, stdscr, args=[]):
    orYear = var['orYear']
    orMonth = var['orMonth']
    year = var['year']
    loaded = var['loaded']

    # Create and fill the Form
    yearF = Field('Selectionner l\'année', content=str(orYear))
    monthF = Field('Selectionner le mois', content=str(orMonth))
    loadForm = Form('Load Data', items=[yearF, monthF])
    loadForm.fill(stdscr, var['alphabet'])

    # Retrieve Form data
    aYear, aMonth = loadForm.retrieve()
    aYear = aYear.strip()
    aMonth = aMonth.strip()

    if aMonth.isnumeric() and int(aMonth) in range(1, 13):
        month = "%02d" % int(aMonth)
        if (year != aYear or not loaded) and aYear.isnumeric():
            year = aYear
            var['year'] = year
            var['loaded'] = True
            loadYear(var)
        elif loaded:
            var['month'] = month
            loadMonth(var)


def _add(var, strings, stdscr, args=[]):
    month = var['month']
    year = var['year']
    data = var['data'][month][0]

    # Create and fill the Form
    dayF = Field('Jour de l\'opération')
    nameF = Field('Nom de l\'opération')
    natF = Field('c -> Crédit, d -> Débit', content='d')
    amountF = Field('Montant de l\'opération')
    addForm = Form('Add Record', items=[dayF, nameF, natF, amountF])
    addForm.fill(stdscr, var['alphabet'])

    # Retrieve Form data
    aDay, aName, aNat, aAmount = addForm.retrieve()
    if aDay.isnumeric():
        aDay = str("%02d" % int(aDay))
        date = [aDay, month, year]
        if aNat in ['d', 'c']:
            aNat = (aNat == 'd')*1
            aAmount = dc.Decimal(aAmount)
            key = createKey(data)
            record = Record(key, date, aName, aAmount, aNat)
            record.add(data)
            var['data'][month][0] = data
            _save(var, strings, stdscr)


def _mod(var, strings, args=[]):
    month = var['month']
    year = var['year']
    data = var['data'][month][0]
    print("Month selected : " + month + '/' + year)
    _show(var, strings, situation=False, key=True)
    key = input(strings['changeKey'] + "\n> ")
    if key.isnumeric():
        key = int(key)
        if key in data:
            record = data[key]
            day = input("Change the day : " + record.date[0] + "\n")
            print()
            if day.isnumeric() and int(day) in range(1, 32):
                day = "%02d" % int(day)
                record.date[0] = day
            print("Date selected : " + '/'.join(record.date))
            name = input(strings['changeName'] + record.name + "\n> ")
            if name:
                record.name = name
            nature = input(strings['changeNature'] + str(record.nature)
                           + "\n0 : Credit\n1 : Debit\n> ")
            if nature:
                record.nature = int(nature)
            amount = input(strings['changeAmount'] + str(record.amount)
                           + "\n> ")
            if amount:
                record.amount = dc.Decimal(amount)
            record.mod(data)
            var['data'][month][0] = data
            _save(var, strings)
        else:
            print("Invalid key")


def _rem(var, strings, args=[]):
    month = var['month']
    year = var['year']
    data = var['data'][month][0]
    print("Month selected : " + month + '/' + year)
    _show(var, strings, situation=False, key=True)
    key = input(strings['removeKey'] + "\n> ")
    if key.isnumeric():
        key = int(key)
        if key in data:
            record = data[key]
            print(strings['removeRecord'])
            record.show()
            record.rem(data)
            var['data'][month][0] = data
            _save(var, strings)
        else:
            print("Invalid key")


def _save(var, strings, stdscr, args=[]):
    month = var['month']
    loaded = var['loaded']
    if loaded:
        (data, path, created) = var['data'][month]
        closeFile(path, data)


def _show(var, strings, args=[], situation=True, key=False):
    month = var['month']
    loaded = var['loaded']
    if loaded:
        data = var['data'][month][0]
        prevMonth, currMonth, sortedData = sortData(data)
        if situation:
            print('Previous month amount : ' + str(prevMonth))
            print('Current month amount : ' + str(currMonth))
            print()
        for record in sortedData:
            record.show(key=key)
    else:
        print("\nNo file loaded")


def _exit(var, strings, stdscr, args=[]):
    if var['loaded']:
        months = var['months']
        data = var['data']
        for month in months:
            monthData = data[month][0]
            monthPath = data[month][1]
            closeFile(monthPath, monthData)
    var['stay'] = False


def _debug(var, strings, args=[]):
    print(var)


def drawscreen(stdscr):
    vline = curses.ACS_VLINE
    hline = curses.ACS_HLINE
    # s1 = curses.ACS_S1
    # s3 = curses.ACS_S3
    # s7 = curses.ACS_S7
    # s9 = curses.ACS_S9
    plus = curses.ACS_PLUS
    ltee = curses.ACS_LTEE
    rtee = curses.ACS_RTEE
    btee = curses.ACS_BTEE
    ttee = curses.ACS_TTEE

    my, mx = stdscr.getmaxyx()

    stdscr.clear()

    # Draw the border
    stdscr.border()

    # Draw the table
    # +----------------------------------+
    # | Date | Nom     | Montant | Solde |
    # |------|---------|---------|-------|
    # |      |         |         |       |
    # |----------------------------------|
    # |                      |           |
    #

    # Main lines
    stdscr.vline(1, 13, vline, my - 11)
    stdscr.vline(1, mx - 25, vline, my - 11)
    stdscr.vline(1, mx - 13, vline, my - 11)
    stdscr.hline(2, 1, hline, mx - 2)
    stdscr.hline(my - 10, 1, hline, mx - 2)
    stdscr.hline(my - 3, 1, hline, mx - 2)

    # Pretty things up
    stdscr.addch(0, 13, ttee)
    stdscr.addch(0,  mx - 25, ttee)
    stdscr.addch(0, mx - 13, ttee)
    stdscr.addch(2, 0, ltee)
    stdscr.addch(2, 13, plus)
    stdscr.addch(2, mx - 25, plus)
    stdscr.addch(2, mx - 13, plus)
    stdscr.addch(2, mx - 1, rtee)
    stdscr.addch(my - 10, 0, ltee)
    stdscr.addch(my - 10, 13, btee)
    stdscr.addch(my - 10, mx - 25, btee)
    stdscr.addch(my - 10, mx - 13, btee)
    stdscr.addch(my - 10, mx - 1, rtee)
    stdscr.addch(my - 3, 0, ltee)
    stdscr.addch(my - 3, mx - 1, rtee)

    # Add the text
    stdscr.addstr(1, 4, 'Date')
    stdscr.addstr(1, 17, 'Nom de l\'opération')
    stdscr.addstr(1, mx - 22, 'Montant')
    stdscr.addstr(1, mx - 9, 'Solde')
    stdscr.addstr(my - 2, 1, '>')


def printRecords(stdscr, var):
    pos = 3
    month = var['month']
    loaded = var['loaded']
    if loaded:
        data = var['data'][month][0]
        prevMonth, currMonth, sortedData = sortData(data)
        current = prevMonth

        for record in sortedData:
            current += (1 - 2*record.nature) * record.amount
            record.printOut(stdscr, pos, current)
            pos += 1


def getCommand(stdscr, var):
    ch = ''
    command = ''

    while ch not in ['\n', '\x11']:
        drawscreen(stdscr)
        printRecords(stdscr, var)
        my, mx = stdscr.getmaxyx()

        if ch == 'KEY_BACKSPACE':
            stdscr.addch(my - 2, 2 + len(command), ' ')
            command = command[:-1]
        elif ch in var['alphabet']:
            command += ch

        stdscr.addstr(my - 2, 3, command)
        ch = stdscr.getkey()

    if ch == '\x11':
        var['stay'] = False

    return command.split(' ')


def test(stdscr, var):
    chars = var['alphabet']
    form = Form('Load Data')
    year = Field('Select the Year')
    form.addField(year)
    form.fill(stdscr, chars)
    month = Field('Select the Month')
    form.addField(month)
    form.fill(stdscr, chars)


def main():

    # Initialize the screen
    stdscr = curses.initscr()
    curses.noecho()
    curses.raw()
    curses.cbreak()
    stdscr.keypad(True)

    var, strings, keyWords = init()
    action = ''

    # Load current month
    loadYear(var)
    var['loaded'] = True

    # The main loop
    while var['stay']:

        command = getCommand(stdscr, var)

        # Get the input
        action = command.pop(0)

        if action in keyWords:
            keyWords[action](var, strings, stdscr, args=command)

    # Clean up before exiting
    curses.nocbreak()
    stdscr.keypad(False)
    curses.echo()
    curses.endwin()


# Start the program
main()
