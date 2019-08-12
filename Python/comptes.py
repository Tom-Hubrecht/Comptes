#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Import necessary modules
import curses as crs
import datetime as dt
import os
import sqlite3 as sql


# Import Classes
from Form import Form


#
# Basic functions
#

def log(message, err):
    var['log'].append((message, err))


def get_money(s, t):
    l = s.strip(" ").replace(",", ".").split(".")
    if t == "Crédit":
        m = 1
    elif t == "Débit":
        m = -1

    if len(l) == 1 and l[0].isdigit():
        return m * (100 * int(l[0]))
    elif len(l) == 2 and (not l[0] or l[0].isdigit()) and l[1].isdigit():
        return m * (100 * int("0" + l[0]) + int(l[1][:2].ljust(2, '0')))
    else:
        log("Montant incorrect '{0}'.".format(s), 1)
        return None


#
# Initialize variables
#

def init():

    # Shortens the ESC delay
    os.environ.setdefault('ESCDELAY', '25')

    # Initialize the screen
    global stdscr
    stdscr = crs.initscr()
    crs.noecho()
    crs.raw()
    crs.cbreak()
    crs.start_color()
    stdscr.keypad(True)

    # Set the color pairs
    crs.COLOR_PAIRS = 8
    crs.init_color(0,  125,  125,  125)  # Black
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

    # Checks if the necessary directories exist and if not create them
    u_path = os.path.expanduser("~/")
    a_path = u_path + ("comptes/")
    c_path = u_path + (".config/comptes/")

    first_launch = False

    if not os.path.isdir(a_path):
        os.mkdir(a_path)
        first_launch = True

    if not os.path.isdir(c_path):
        os.mkdir(c_path)

    global now
    now = dt.date.today()
    month = '%02d' % now.month
    year = str(now.year)

    months = ['01', '02', '03', '04', '05', '06',
              '07', '08', '09', '10', '11', '12']

    global keyWords
    keyWords = {
            'load': _load,
            'add': _add,
            'create': _create,
            # 'mod': _mod,
            'exit': _exit,
            # 'save': _save,
            # 'rem': _rem,
            # 'debug': _debug,
            # 'reload': _reload,
            # 'help': _help
            }

    global var
    var = {
            'log': [],
            'fst_launch': first_launch,
            'app_path': a_path,
            'opened_db': "",
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
            }


#
# Database-related functions
#

def open_database(db_name):
    db_path = var['app_path'] + db_name

    if os.path.exists(db_path):
        file_db = sql.connect(db_path + "/data.db")
        var['opened_db'] = db_name
        log("Ouverture de {0}.".format(db_name), 0)

        return file_db
    else:
        log("Le fichier '{0}' n'existe pas.".format(db_name), 1)

        return None


def close_database(f_db):
    log("Fermeture de '{0}'.".format(var['opened_db']), 0)

    # Save the opened database
    save_database(f_db)

    # Close the files
    f_db.close()

    var['opened_db'] = ""


def save_database(f_db):
    f_db.commit()
    log("Sauvegarde de '{0}'.".format(var['opened_db']), 0)


def create_database(db_name):
    db_path = var['app_path'] + db_name

    if os.path.exists(db_path):
        log("Le fichier '{0}' existe déjà.".format(db_name), 1)

        return None
    else:
        os.mkdir(db_path)
        f_db = sql.connect(db_path + "/data.db")
        var['opened_db'] = db_name

        # Initialise databases
        db = f_db.cursor()
        db.execute("""CREATE TABLE payments (
                        id integer PRIMARY KEY,
                        date text,
                        name text,
                        recurring integer,
                        amount integer
        )""")

        db.execute("""CREATE TABLE total (
                        date text PRIMARY KEY,
                        amount integer
        )""")

        # Save the databases
        f_db.commit()

        return f_db


def next_id(db):
    db.execute("SELECT MAX(id) FROM payments")
    (n_id,) = db.fetchone()
    if n_id is None:
        n_id = 0

    return n_id + 1


def insert_payment(db, a_form):
    p_id = next_id(db)
    p_date, p_name, p_type, p_amount = a_form.retrieve()
    p_date = p_date.split("/")
    p_date.reverse()
    p_date = "-".join(p_date)
    p_rec = 0
    p_amount = get_money(p_amount, p_type)

    if p_amount is not None:
        db.execute("""INSERT INTO payments VALUES (?, ?, ?, ?, ?)""",
                   (p_id, p_date, p_name, p_rec, p_amount))
        update_day(db, p_date, p_amount)


def update_day(db, p_date, p_amount):
    db.execute("SELECT amount FROM total WHERE date = ?", (p_date,))
    c_a = db.fetchone()

    if c_a is None:
        db.execute("INSERT INTO total VALUES (?, ?)", (p_date, p_amount))
    else:
        u_a = p_amount + c_a[0]
        db.execute("UPDATE total SET amount = ? WHERE date = ?", (u_a, p_date))


#
# Drawing functions
#

def draw_background(key=False):

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

        stdscr.addstr(my - 2, 1, ">")


def draw_payments(db, offset=0):
    my, mx = stdscr.getmaxyx()

    # Add titles
    stdscr.addstr(1, 4, "Date")
    stdscr.addstr(1, 17, "Nom de l'opération")
    stdscr.addstr(1, mx - 22, "Montant")
    stdscr.addstr(1, mx - 9, "Solde")

    # Gather all payments
    nb_max = my - 13
    db.execute("""SELECT * FROM payments ORDER BY date DESC, name ASC
                    LIMIT ? OFFSET ?""", (nb_max, offset))
    payments = db.fetchall()

    # Get current amount
    db.execute("""SELECT amount FROM total
                    WHERE date = (SELECT MAX(date) FROM payments)""")
    current = db.fetchone()
    if current is None:
        current = 0
    else:
        current = current[0]

    pos = 3
    for p in payments:
        # Print the date
        l_d = p[1].split("-")
        l_d.reverse()
        stdscr.addstr(pos, 2, "/".join(l_d))

        # Print the name
        stdscr.addstr(pos, 16, p[2])

        # Print the associated total amount
        s_c = "{:7.2f}".format(current/100).strip()
        stdscr.addstr(pos, mx - 3 - len(s_c), s_c)
        current += p[4]

        # Print the amount
        if p[4] >= 0:
            s_a = "{:7.2f}".format(p[4]/100).strip()
            stdscr.addstr(pos, mx - 15 - len(s_a), s_a, crs.color_pair(2))
        elif p[4] < 0:
            s_a = "{:7.2f}".format(p[4]/100).strip()
            stdscr.addstr(pos, mx - 15 - len(s_a), s_a, crs.color_pair(1))

        pos += 1


def draw_info(db):
    my, mx = stdscr.getmaxyx()
    now = dt.date.today()

    # Add the text
    stdscr.addstr(my - 9, mx - 19, now.strftime("%d/%m/%Y"))
    stdscr.addstr(my - 7, mx - 28, "Mois précédent:")
    stdscr.addstr(my - 6, mx - 28, "Solde actuel:")

    # Get current amount
    db.execute("""SELECT amount FROM total
                    WHERE date = (SELECT MAX(date) FROM payments
                            WHERE date <= ?)""", (now.strftime("%Y-%m-%d"),))
    c_a = db.fetchone()
    if c_a is None:
        c_a = "0.00"
    else:
        c_a = "{:7.2f}".format(c_a[0]/100).strip()

    # Get previous month's amount
    p_m = now.replace(day=1) - dt.timedelta(days=1)
    db.execute("""SELECT amount FROM total
                    WHERE date = (SELECT MAX(date) FROM payments
                            WHERE date <= ?)""", (p_m.strftime("%Y-%m-%d"),))
    p_a = db.fetchone()
    if p_a is None:
        p_a = "0.00"
    else:
        p_a = "{:7.2f}".format(p_a[0]/100).strip()

    # Display the amounts
    stdscr.addstr(my - 7, mx - 11, p_a, crs.color_pair(3))
    if p_a > c_a:
        stdscr.addstr(my - 6, mx - 11, c_a, crs.color_pair(1))
    else:
        stdscr.addstr(my - 6, mx - 11, c_a, crs.color_pair(2))


def draw_log():
    my, _ = stdscr.getmaxyx()
    display_log = var['log'][-6:]
    d_p = 0

    for line in display_log:
        stdscr.addstr(my - 9 + d_p, 1, line[0], crs.color_pair(line[1]))
        d_p += 1


def draw_window():
    draw_background()
    if var['opened_db'] != "":
        draw_info(var['f_db'].cursor())
        draw_payments(var['f_db'].cursor())
    draw_log()


#
# Different actions
#

def _create():
    c_form = Form("Création")
    c_form.add_text("Nom du compte")

    c_form.fill(stdscr)

    if c_form.cancelled:
        var['cancelled'] = True
    else:
        db_name, = c_form.retrieve()
        if var['opened_db'] != "":
            close_database(var['f_db'])

        var['f_db'] = create_database(db_name)


def _load():
    l_form = Form("Ouverture")
    l_form.add_text("Nom du compte")

    l_form.fill(stdscr)

    if l_form.cancelled:
        var['cancelled'] = True
    else:
        db_name, = l_form.retrieve()
        if var['opened_db'] != "":
            close_database(var['f_db'])

        var['f_db'] = open_database(db_name)
        var['cancelled'] = True


def _add():
    now = dt.date.today()
    a_form = Form("Ajout d'un paiement")
    a_form.add_date("Jour de l'opération", now.strftime("%d/%m/%Y"))
    a_form.add_text("Nom de l'opération")
    a_form.add_carousel("Type d'opération", ["Débit", "Crédit"])
    a_form.add_text("Montant de l'opération")

    a_form.fill(stdscr)

    if a_form.cancelled:
        var['cancelled'] = True
    else:
        insert_payment(var['f_db'].cursor(), a_form)
        var['f_db'].commit()


def _exit():
    if var['opened_db'] != "":
        close_database(var['f_db'])

    var['stay'] = False


def getCommand(com=''):
    ch = ""
    command = ""
    cx = 0

    draw_window()
    y, x = stdscr.getmaxyx()

    while ch not in ['\n', '\x11']:
        my, mx = stdscr.getmaxyx()

        if mx > 63 and my > 19:
            if ch == 263 and cx:
                command = command[:cx - 1] + command[cx:]
                cx -= 1
            elif ch == 260:
                if cx:
                    cx -= 1
            elif ch == 261:
                if len(command) - cx:
                    cx += 1
            elif ch == '\x1b':
                command = ''
                cx = 0
            elif type(ch) is str and ch != "":
                command = command[:cx] + ch + command[cx:]
                cx += 1

        log(str(ch), 0)
        draw_log()

        stdscr.addstr(my - 2, 3, ' '*(mx - 5))
        stdscr.addstr(my - 2, 3, command[-(mx - 5):])
        stdscr.move(my - 2, 3 + cx)

        ch = stdscr.get_wch()

        if (my, mx) != (y, x):
            draw_window()
            y, x = my, mx

    if ch == '\x11':
        var['stay'] = False

    return command.split(' ')


# The main loop

def main():
    init()

    action = ''
    command = ['']

    # Load current month
    draw_window()
    _create()

    # The main loop
    while var['stay']:
        var['cancelled'] = False

        command = getCommand()

        # Get the input
        action = command.pop(0)

        if action in keyWords:
            while (not var['cancelled']) and var['stay']:
                keyWords[action]()
                draw_window()

    # Clean up before exiting
    crs.nocbreak()
    stdscr.keypad(False)
    crs.echo()
    crs.endwin()


# Start the program
main()
