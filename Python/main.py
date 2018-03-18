# Import necessary modules
import os
import decimal as dc
import datetime
import curses


# Define a class for the records

class Record:

    def __init__(self, key, date, name, amount, nature):
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


def init():

    # Initialize the screen
    stdscr = curses.initscr()
    curses.noecho()
    curses.cbreak()
    stdscr.keypad(True)

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
            'stay': True
            }

    return var, strings, keyWords


#
# All the function handling files
#

# Open the requested file and return the file, its path and if it was created

def openFile(fileName, year, cwd):
    filePath = os.path.join(cwd, '..', 'Files', year, '') + fileName
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
        filePath = os.path.join(cwd, '..', 'Files', year, '') + fileName
        if os.path.isfile(filePath):
            file = open(filePath, 'rt')
            line = file.readline().strip('\n')
            prevMonth = dc.Decimal(line.split(';')[1])
            file.close()
    else:
        pYear = str(int(year) - 1)
        if os.path.isdir(os.path.join(cwd, '..', 'Files', pYear, '')):
            fileName = '12_' + pYear + '.sav'
            filePath = os.path.join(cwd, '..', 'Files', pYear, '') + fileName
            if os.path.isfile(filePath):
                file = open(filePath, 'rt')
                line = file.readline().strip('\n')
                prevMonth = dc.Decimal(line.split(';')[1])
                file.close()
    if prevMonth == dc.Decimal(0) and not created:
        fileName = month + '_' + year + '.sav'
        filePath = os.path.join(cwd, '..', 'Files', year, '') + fileName
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
    path = os.path.join(cwd, '..', 'Files', year)
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

def _load(var, strings, args=[]):
    n = len(args)
    orYear = var['orYear']
    orMonth = var['orMonth']
    year = var['year']
    loaded = var['loaded']

    if not loaded:
        selection = 'y'
        var['loaded'] = True

    if n == 1 and args[0] in ['y', 'm']:
        selection = args[0]
        month = '0'
    else:
        loading = True
        while loading:
            ans = input("\n" + strings['selectLoad'] + "\n> ")
            if ans.isnumeric():
                if int(ans) in range(1, 13):
                    selection = 'm'
                    month = "%02d" % int(ans)
                    loading = False
                elif ans == '0':
                    selection = 'y'
                    loading = False
            elif not ans:
                selection = 'y'
                loading = False

    if selection == 'y':
        loading = True
        while loading:
            ans = input("\n" + strings['selectYear'] + orYear + "\n> ")
            if not ans:
                year = orYear
                loading = False
            elif ans.isnumeric():
                year = ans
                loading = False
        var['year'] = year
        loadYear(var)

    elif selection == 'm':
        if month == '0':
            loading = True
            while loading:
                ans = input("\n" + strings['selectMonth'] + orMonth + "\n> ")
                if ans.isnumeric():
                    if int(ans) in range(1, 13):
                        selection = 'm'
                        month = "%02d" % int(ans)
                        loading = False
                    elif not ans:
                        month = orMonth
                        loading = False
        var['month'] = month
        loadMonth(var)


def _add(var, strings, args=[]):
    loaded = var['loaded']
    month = var['month']
    year = var['year']
    data = var['data'][month][0]
    if loaded:
        ok = True
        while ok:
            day = input("Select the day :\n")
            if day.isnumeric():
                day = str("%02d" % int(day))
                ok = False
        date = [day, month, year]
        print("Date selected : " + '/'.join(date))
        name = input(strings['selectName'] + "\n> ")
        ok = True
        while ok:
            nature = input(strings['selectNat'] + "\n> ")
            if nature == '':
                nature = 1
                ok = False
            elif nature.isnumeric():
                nature = bool(int(nature))*1
                ok = False
        amount = ''
        while not amount:
            amount = input(strings['selectAmount'] + "\n> ")
            amount = dc.Decimal(amount)
            key = createKey(data)
        record = Record(key, date, name, amount, nature)
        record.add(data)
        var['data'][month][0] = data
        print("Record added :\n")
        record.show()
        _save(var, strings)


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


def _save(var, strings, args=[]):
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


def _exit(var, strings, args=[]):
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


def main():
    var, strings, keyWords = init()

    # The main loop
    while var['stay']:
        command = input("\n> ").split(' ')
        action = command.pop(0)
        stdscr.refresh()
        if action in keyWords:
            keyWords[action](var, strings, args=command)


# Start the program
main()
