#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Import necessary modules
import os
import decimal as dc
import datetime
import curses as crs

# Import Classes
from Record import Record
from Form_old import Form
from Field import Field

# Import suggestion functions
from Suggestions import addName, remName

#
# Basic functions
#


def isMoney(amount):
    listAmount = amount.split('.')
    b = 0 < len(listAmount) < 3
    for string in listAmount:
        b &= string.isnumeric()
    return b

#
# Initialize variables
#


def init():

    # Shortens the ESC delay
    os.environ.setdefault('ESCDELAY', '25')

    # Initialize the screen
    stdscr = crs.initscr()
    crs.noecho()
    crs.raw()
    crs.cbreak()
    crs.start_color()
    stdscr.keypad(True)

    # Set the color pairs
    if os.environ['TERM'] == 'linux':
        # If we are in a tty we can only use 8 colors
        crs.COLOR_PAIRS = 8
        crs.init_color(0,    0,    0,    0)  # Black
        crs.init_color(1, 1000,  336,  366)  # Red
        crs.init_color(2,  336, 1000,  336)  # Green
        crs.init_color(3,  336,  336, 1000)  # Blue
        crs.init_color(4, 1000, 1000,  336)  # Yellow
        crs.init_color(5,  336, 1000, 1000)  # Cyan
        crs.init_color(6, 1000,  336, 1000)  # Magenta
        crs.init_color(7,  664,  664,  664)  # Light Grey
        crs.init_pair(1, 1, 0)
        crs.init_pair(2, 2, 0)
        crs.init_pair(3, 3, 0)
        crs.init_pair(4, 4, 0)
        crs.init_pair(5, 5, 0)
        crs.init_pair(6, 6, 0)
        crs.init_pair(7, 7, 0)
    else:
        crs.COLORS = 32
        crs.COLOR_PAIRS = 32
        # Start at 20 so the original colors are unchanged
        crs.init_color(20,    0,    0,    0)  # Black
        crs.init_color(21, 1000, 1000, 1000)  # White
        crs.init_color(22, 1000,  336,  336)  # Red
        crs.init_color(23,  336, 1000,  336)  # Green
        crs.init_color(24,  336,  336, 1000)  # Blue
        crs.init_color(25, 1000, 1000,  336)  # Yellow
        crs.init_color(26,  336, 1000, 1000)  # Cyan
        crs.init_color(27, 1000,  336, 1000)  # Magenta
        crs.init_color(28,  336,  336,  366)  # Dark Grey
        crs.init_color(29,  664,  664,  664)  # Light Grey
        crs.init_pair(1,  22, 20)
        crs.init_pair(2,  23, 20)
        crs.init_pair(3,  24, 20)
        crs.init_pair(4,  25, 20)
        crs.init_pair(5,  26, 20)
        crs.init_pair(6,  27, 20)
        crs.init_pair(7,  28, 20)
        crs.init_pair(8,  29, 20)

    cwd = os.getcwd()
    dc.getcontext().prec = 50
    now = datetime.datetime.now()
    month = '%02d' % now.month
    year = str(now.year)

    months = ['01', '02', '03', '04', '05', '06',
              '07', '08', '09', '10', '11', '12']

    keyWords = {
            'load': _load,
            'add': _add,
            'mod': _mod,
            'exit': _exit,
            'save': _save,
            'rem': _rem,
            'debug': _debug,
            # 'reload': _reload,
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
            'names': {},  # var['names']['Toto'] = frequency of 'Toto'
            'stay': True,
            'cancelled': False,
            'cursor': [0, 0],  # var['cursor'] = [cursor.x, cursor.y]
            'alphabet': {'a': 'a', 'b': 'b', 'c': 'c', 'd': 'd', 'e': 'e',
                         'f': 'f', 'g': 'g', 'h': 'h', 'i': 'i', 'j': 'j',
                         'k': 'k', 'l': 'l', 'm': 'm', 'n': 'n', 'o': 'o',
                         'p': 'p', 'q': 'q', 'r': 'r', 's': 's', 't': 't',
                         'u': 'u', 'v': 'v', 'w': 'w', 'x': 'x', 'y': 'y',
                         'z': 'z', 'A': 'A', 'B': 'B', 'C': 'C', 'D': 'D',
                         'E': 'E', 'F': 'F', 'G': 'G', 'H': 'H', 'I': 'I',
                         'J': 'J', 'K': 'K', 'L': 'L', 'M': 'M', 'N': 'N',
                         'O': 'O', 'P': 'P', 'Q': 'Q', 'R': 'R', 'S': 'S',
                         'T': 'T', 'U': 'U', 'V': 'V', 'W': 'W', 'X': 'X',
                         'Y': 'Y', 'Z': 'Z', '0': '0', '1': '1', '2': '2',
                         '3': '3', '4': '4', '5': '5', '6': '6', '7': '7',
                         '8': '8', '9': '9', ' ': ' ', '-': '-', '_': '_',
                         '.': '.', ',': ',', '©': 'é', '¨': 'è',
                         },
            'chars': [crs.ACS_S9, crs.ACS_S7, crs.ACS_HLINE, crs.ACS_S3,
                      crs.ACS_S1],
            }

    return stdscr, var, keyWords


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

def readFile(file, var, created):
    cwd = var['cwd']
    year = var['year']
    month = var['month']
    data = {}
    data['prevMonth'] = findPrev(month, year, created, cwd)
    data['currMonth'] = data['prevMonth']
    data['history'] = [data['currMonth']]*31
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
            addName(name, var)
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
        if key not in ['prevMonth', 'currMonth', 'history']:
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
        data = readFile(file, var, created)
        file.close()
    # Look for older files for the previous amount if we created the file
    else:
        data = {}
        prevMonth = findPrev(month, year, created, cwd)
        # If no older files are found, findPrev returns '0', wich is the right
        # value that is requested
        data['prevMonth'] = prevMonth
        data['currMonth'] = prevMonth
        data['history'] = [prevMonth]*31
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

# Load a Year or a Month

def _load(var, stdscr, args=[]):
    month = var['month']
    year = var['year']
    loaded = var['loaded']

    # Create and fill the Form
    yearF = Field('Selectionner l\'année', content=str(year))
    monthF = Field('Selectionner le mois', content=str(month))
    loadForm = Form('Load Data', var, [yearF, monthF])
    loadForm.fill(stdscr, var)

    # Retrieve Form data
    if loadForm.cancelled:
        var['cancelled'] = True
    else:
        var['cancelled'] = True
        aYear, aMonth = loadForm.retrieve()
        aYear = aYear.strip()
        aMonth = aMonth.strip()

        if aMonth.isnumeric() and int(aMonth) in range(1, 13):
            month = "%02d" % int(aMonth)
            if (year != aYear or not loaded) and aYear.isnumeric():
                year = aYear
                var['year'] = year
                var['month'] = month
                var['loaded'] = True
                var['names'] = {}
                loadYear(var)
            elif loaded:
                var['month'] = month
                loadMonth(var)


# Add a new Record

def _add(var, stdscr, args=[]):
    month = var['month']
    year = var['year']
    data = var['data'][month][0]

    # Create and fill the Form
    dayF = Field('Jour de l\'opération')
    nameF = Field('Nom de l\'opération', suggestions='names')
    natF = Field('c -> Crédit, d -> Débit', content='d')
    amountF = Field('Montant de l\'opération')
    addForm = Form('Add Record', var, [dayF, nameF, natF, amountF])
    addForm.fill(stdscr, var)

    # Retrieve Form data
    if addForm.cancelled:
        var['cancelled'] = True
    else:
        aDay, aName, aNat, aAmount = addForm.retrieve()
        if aDay.isnumeric() and aNat in ['d', 'c'] and isMoney(aAmount):
            aDay = str("%02d" % int(aDay))
            date = [aDay, month, year]
            aNat = (aNat == 'd')*1
            aAmount = dc.Decimal(aAmount)
            key = createKey(data)
            record = Record(key, date, aName, aAmount, aNat)
            record.add(data)
            addName(aName, var)
            var['data'][month][0] = data
            _save(var, stdscr)


# Change an existing Record

def _mod(var, stdscr, args=[]):
    month = var['month']
    year = var['year']
    data = var['data'][month][0]

    # Draw Screen with the keys
    drawscreen(stdscr, var, True)

    # Create Form to select item to be removed
    keyF = Field('Clé de l\'item à changer')
    selForm = Form('Choose Record', var, [keyF])
    selForm.fill(stdscr, var)
    if selForm.cancelled:
        var['cancelled'] = True
    else:
        key = selForm.retrieve()[0]

        if key.isnumeric() and int(key) in data:
            rc = data[int(key)]
            remName(rc.name, var)
            # Create and fill the Form
            dayF = Field('Jour de l\'opération', str(rc.day + 1))
            nameF = Field('Nom de l\'opération', rc.name, 'names')
            natF = Field('c -> Crédit, d -> Débit', 'd' if rc.nature else 'c')
            amountF = Field('Montant de l\'opération', str(rc.amount))
            modForm = Form('Change Record', var, [dayF, nameF, natF, amountF])
            modForm.fill(stdscr, var)

            # Retrieve Form data
            if modForm.cancelled:
                var['cancelled'] = True
            else:
                mDay, mName, mNat, mAmount = modForm.retrieve()
                if mDay.isdigit() and mNat in ['d', 'c'] and isMoney(mAmount):
                    mDay = str("%02d" % int(mDay))
                    date = [mDay, month, year]
                    mNat = (mNat == 'd')*1
                    mAmount = dc.Decimal(mAmount)
                    record = Record(int(key), date, mName, mAmount, mNat)
                    record.mod(data)
                    addName(mName, var)
                    var['data'][month][0] = data
                    _save(var, stdscr)


# Remove an existing Record

def _rem(var, stdscr, args=[]):
    month = var['month']
    data = var['data'][month][0]

    # Draw Screen with the keys
    drawscreen(stdscr, var, True)

    # Create Form to select item to be removed
    keyF = Field('Clé de l\'item à changer')
    selForm = Form('Choose Record', var, [keyF])
    selForm.fill(stdscr, var)

    if selForm.cancelled:
        var['cancelled'] = True
    else:
        key = selForm.retrieve()[0]

        if key.isnumeric() and int(key) in data:
            record = data[int(key)]
            record.rem(data)
            remName(record.name, var)


# Save the current Month

def _save(var, stdscr, args=[]):
    month = var['month']
    loaded = var['loaded']
    if loaded:
        (data, path, _) = var['data'][month]
        closeFile(path, data)


# Exit the main loop

def _exit(var, stdscr, args=[]):
    if var['loaded']:
        months = var['months']
        data = var['data']
        for month in months:
            monthData = data[month][0]
            monthPath = data[month][1]
            closeFile(monthPath, monthData)
    var['stay'] = False


def _reload(var, stdscr, args=[]):
    _exit(var, stdscr, args=[])

    main()


def _debug(var, stdscr, args=[]):
    print(var)


# Draw the GUI

def drawscreen(stdscr, var, key=False):

    my, mx = stdscr.getmaxyx()

    # Do not draw if the screen is too small
    if my > 19 and mx > 63:

        vline = crs.ACS_VLINE
        hline = crs.ACS_HLINE
        plus = crs.ACS_PLUS
        ltee = crs.ACS_LTEE
        rtee = crs.ACS_RTEE
        btee = crs.ACS_BTEE
        ttee = crs.ACS_TTEE

        month = var['month']
        year = var['year']

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
        if key:
            stdscr.vline(1, 19, vline, my - 11)
        stdscr.vline(my - 10, mx - 30, vline, 8)
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
        stdscr.addch(my - 10, mx - 30, ttee)
        stdscr.addch(my - 3, mx - 30, btee)
        if key:
            stdscr.addch(0, 19, ttee)
            stdscr.addch(2, 19, plus)
            stdscr.addch(my - 10, 19, btee)

        # Add the text
        stdscr.addstr(1, 4, 'Date')
        stdscr.addstr(1, 17 + 6 * key, 'Nom de l\'opération')
        stdscr.addstr(1, mx - 22, 'Montant')
        stdscr.addstr(1, mx - 9, 'Solde')
        if key:
            stdscr.addstr(1, 15, 'Clé')
        stdscr.addstr(my - 9, mx - 19, month + '/' + year)
        stdscr.addstr(my - 7, mx - 28, 'Solde précédent:')
        stdscr.addstr(my - 6, mx - 28, 'Solde actuel:')
        stdscr.addstr(my - 2, 1, '>')

        printRecords(stdscr, var, key)
        # drawGraph(stdscr, var)


# Print the records for the selected month

def printRecords(stdscr, var, key=False):
    pos = 3
    my, mx = stdscr.getmaxyx()
    month = var['month']
    loaded = var['loaded']
    if loaded:
        data = var['data'][month][0]
        prevMonth, _, sortedData = sortData(data)
        current = prevMonth

        for record in sortedData:
            current += (1 - 2*record.nature) * record.amount
            record.printOut(stdscr, pos, current, key)
            pos += 1

        stdscr.addstr(my - 7, mx - 11, str(prevMonth), crs.color_pair(3))
        if prevMonth > current:
            stdscr.addstr(my - 6, mx - 11, str(current), crs.color_pair(1))
        else:
            stdscr.addstr(my - 6, mx - 11, str(current), crs.color_pair(2))


# Draw the graph for the current Month

def drawGraph(stdscr, var):
    month = var['month']
    loaded = var['loaded']
    my, mx = stdscr.getmaxyx()
    chars = var['chars']
    if loaded:
        data = var['data'][month][0]
        history = data['history']
        solMax, solMin = max(history), min(history)
        delSol = solMax - solMin
        if not delSol:
            delSol = 20
        # Vertical position of the line
        pos = [int((29 * (sol - solMin)) / delSol) for sol in history]
        date = [int((30 * x) / (mx - 32)) for x in range(1, mx - 30)]
        ticks = [date.index(5*i - 1) for i in range(1, 7)]

        for x in range(1, mx - 30):
            d = max(date[x - 1], 0)  # date[0] can be -1
            d = min(d, 30)  # In case d = 31 which throws IndexError
            ch = chars[pos[d] % 5]
            y = my - 4 - (pos[d] // 5)
            stdscr.addch(y, x, ch, crs.color_pair(4))
        for x in ticks:
            stdscr.addch(my - 3, x + 1, crs.ACS_BTEE)


# Retrieve the entered command

def getCommand(stdscr, var, com=''):
    ch = ''
    command = com
    cx = len(command)

    drawscreen(stdscr, var)
    y, x = stdscr.getmaxyx()

    while ch not in ['\n', '\x11']:
        my, mx = stdscr.getmaxyx()

        if mx > 63 and my > 19:
            if ch == 'KEY_BACKSPACE' and cx:
                command = command[:cx - 1] + command[cx:]
                cx -= 1
            elif ch == 'KEY_LEFT':
                if cx:
                    cx -= 1
            elif ch == 'KEY_RIGHT':
                if len(command) - cx:
                    cx += 1
            elif ch == '\x1b':
                command = ''
                cx = 0
            elif ch in var['alphabet']:
                command = command[:cx] + var['alphabet'][ch] + command[cx:]
                cx += 1

        stdscr.addstr(my - 2, 3, ' '*(mx - 5))
        stdscr.addstr(my - 2, 3, command[-(mx - 5):])
        stdscr.move(my - 2, 3 + cx)

        ch = stdscr.getkey()

        if (my, mx) != (y, x):
            drawscreen(stdscr, var)
            y, x = my, mx

    if ch == '\x11':
        var['stay'] = False

    return command.split(' ')


# The main loop

def main():

    stdscr, var, keyWords = init()
    action = ''
    command = ['']

    # Load current month
    loadYear(var)
    var['loaded'] = True

    # The main loop
    while var['stay']:
        var['cancelled'] = False

        command = getCommand(stdscr, var)

        # Get the input
        action = command.pop(0)

        if action in keyWords:
            while not var['cancelled'] and var['stay']:
                keyWords[action](var, stdscr, args=command)
                drawscreen(stdscr, var)

    # Clean up before exiting
    crs.nocbreak()
    stdscr.keypad(False)
    crs.echo()
    crs.endwin()


# Start the program
main()
