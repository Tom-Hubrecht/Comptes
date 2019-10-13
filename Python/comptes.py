#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Import necessary modules
import curses as crs
import configparser as cfg
import datetime as dt
import os
import sqlite3 as sql


# Import Classes
from Form import Form


# TODO: Add graphing ability and suggestions

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


def get_date(s):
    l = s.split("/")

    if len(l) == 3 and l[1] in var['months'] \
       and int(l[0]) in range(1, var['months'][l[1]] + 1):
        l.reverse()
        return "-".join(l)
    else:
        log("Date incorrecte '{0}'.".format(s), 1)
        return None


def scroll_up():
    if var['selected'] > 0:
        var['selected'] -= 1
    elif var['selected'] == 0:
        if var['offset'] > 0:
            var['offset'] -= 1


def scroll_down():
    my, _ = stdscr.getmaxyx()
    m_sel = min(my - 13, len(var['id_list'])) - 1

    if var['opened_db'] != "" and var['id_list'] != []:
        db = var['f_db'].cursor()
        db.execute("SELECT COUNT(*) FROM payments")

        m_scroll = db.fetchone()[0] - len(var['id_list']) - var['offset']
    else:
        m_scroll = 0

    if var['selected'] < m_sel:
        var['selected'] += 1
    elif var['selected'] == m_sel:
        if m_scroll > 0:
            var['offset'] += 1


def verif_scroll():
    my, _ = stdscr.getmaxyx()
    m_sel = min(my - 13, len(var['id_list'])) - 1

    if var['selected'] > m_sel:
        var['selected'] = m_sel

    if len(var['id_list']) < my - 14:
        var['offset'] = max(0, var['offset'] - (my - 13 - len(var['id_list'])))


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
    c_path = u_path + (".config/comptes.ini")

    first_launch = False

    if not os.path.isdir(a_path):
        os.mkdir(a_path)
        first_launch = True

    if not os.path.isfile(c_path):
        config = init_config(c_path)
    else:
        config = read_config(c_path)

    months = {'01': 31, '02': 29, '03': 31, '04': 30, '05': 31, '06': 30,
              '07': 31, '08': 31, '09': 30, '10': 31, '11': 30, '12': 31}

    global keyWords
    keyWords = {
        ':l': _load,
        ':a': _add,
        ':i': _create,
        ':d': _del,
        ':q': _exit,
        ':s': _save,
        ':c': _close,
        }

    global var
    var = {
        'log': [],
        'fst_launch': first_launch,
        'cfg_path': c_path,
        'app_path': a_path,
        'opened_db': "",
        'months': months,
        'stay': True,
        'cancelled': False,
        'debug': False,
        'mode': "global",
        'selected': 0,
        'id_list': [],
        'offset': 0,
        'changed': False,
        'config': config
        }


def init_config(c_path):
    config = cfg.ConfigParser()
    config['GENERAL'] = {'last_opened': ""}

    with open(c_path, "w") as f_config:
        config.write(f_config)

    return config


def read_config(c_path):
    config = cfg.ConfigParser()
    config.read(c_path)

    return config


def save_config(c_path):
    with open(c_path, "w") as f_config:
        var['config'].write(f_config)


#
# Database-related functions
#

def open_database(db_name):
    db_path = var['app_path'] + db_name

    if os.path.exists(db_path):
        file_db = sql.connect(db_path + "/data.db")
        var['opened_db'] = db_name
        log("Ouverture de '{0}'.".format(db_name), 0)

        return file_db
    else:
        log("Le fichier '{0}' n'existe pas.".format(db_name), 1)

        return None


def close_database(f_db):
    log("Fermeture de '{0}'.".format(var['opened_db']), 0)

    # Save the opened database
    f_db.commit()

    # Close the files
    f_db.close()

    var['config']['GENERAL']['last_opened'] = var['opened_db']
    var['opened_db'] = ""


def delete_database(f_db):
    log("Suppression de '{0}'.".format(var['opened_db']), 0)

    db_dir = var['app_path'] + var['opened_db']
    db_file = db_dir + "/data.db"

    f_db.close()

    os.remove(db_file)
    os.rmdir(db_dir)

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
    p_date = get_date(p_date)
    p_rec = 0
    p_amount = get_money(p_amount, p_type)

    if p_amount is not None and p_date is not None:
        db.execute("""INSERT INTO payments VALUES (?, ?, ?, ?, ?)""",
                   (p_id, p_date, p_name, p_rec, p_amount))
        update_day(db, p_date, p_amount)


def delete_payment(db, r_id):
        db.execute("SELECT date, amount FROM payments WHERE id = ?", (r_id,))
        r_date, r_amount = db.fetchone()

        update_day(db, r_date, -r_amount)

        db.execute("DELETE FROM payments WHERE id = ?", (r_id,))


def change_payment(db, m_id, m_form, o_date, o_amount):
    m_date, m_name, m_type, m_amount = m_form.retrieve()
    m_date = get_date(m_date)
    m_amount = get_money(m_amount, m_type)

    if m_amount is not None and m_date is not None:
        db.execute("""UPDATE payments SET date = ?, name = ?, amount = ?
                      WHERE id = ?""", (m_date, m_name, m_amount, m_id))
        update_day(db, m_date, m_amount)
        update_day(db, o_date, -o_amount)


def update_day(db, p_date, p_amount):
    db.execute("""SELECT amount, date FROM total
                  WHERE date = (SELECT MAX(date) FROM total
                                WHERE date <= ?)""", (p_date,))
    c_a = db.fetchone()
    if var['debug']:
        log("Jour précédent : " + str(c_a), 4)

    if c_a is None:
        db.execute("INSERT INTO total VALUES (?, ?)", (p_date, 0))
    else:
        if p_date != c_a[1]:
            db.execute("INSERT INTO total VALUES (?, ?)", (p_date, c_a[0]))

    db.execute("UPDATE total SET amount = amount + ? WHERE date >= ?",
               (p_amount, p_date))


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


def draw_payments(db):
    my, mx = stdscr.getmaxyx()
    now = dt.date.today()
    offset = var['offset']
    var['id_list'] = []

    # Add titles
    stdscr.addstr(1, 4, "Date")
    stdscr.addstr(1, 17, "Nom de l'opération")
    stdscr.addstr(1, mx - 22, "Montant")
    stdscr.addstr(1, mx - 9, "Solde")

    # Gather all payments
    nb_max = my - 13
    db.execute("""SELECT * FROM payments ORDER BY date DESC, id DESC
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
        var['id_list'] += [p[0]]
        if p[1] > now.strftime("%Y-%m-%d"):
            col = crs.color_pair(6)
        else:
            col = crs.color_pair(7)

        # Print the date
        l_d = p[1].split("-")
        l_d.reverse()
        s_d = " " + "/".join(l_d) + " "
        if var['mode'] == "edit" and var['selected'] + 3 == pos:
            stdscr.addstr(pos, 1, s_d, (col + crs.A_REVERSE))
        else:
            stdscr.addstr(pos, 1, s_d, col)

        # Print the name
        s_n = "  {0:<{1}}".format(p[2], mx - 41)
        if var['mode'] == "edit" and var['selected'] + 3 == pos:
            stdscr.addstr(pos, 14, s_n, (col + crs.A_REVERSE))
        else:
            stdscr.addstr(pos, 14, s_n, col)

        # Print the associated total amount
        s_c = " {0:>9.2f} ".format(current/100)
        if var['mode'] == "edit" and var['selected'] + 3 == pos:
            stdscr.addstr(pos, mx - 12, s_c, (col + crs.A_REVERSE))
        else:
            stdscr.addstr(pos, mx - 12, s_c, col)
        current -= p[4]

        # Print the amount
        s_a = " {0:>9.2f} ".format(p[4]/100)
        if var['mode'] == "edit" and var['selected'] + 3 == pos:
            stdscr.addstr(pos, mx - 24, s_a, (col + crs.A_REVERSE))
        else:
            if p[4] >= 0:
                stdscr.addstr(pos, mx - 24, s_a, crs.color_pair(2))
            elif p[4] < 0:
                stdscr.addstr(pos, mx - 24, s_a, crs.color_pair(1))

        pos += 1


def draw_info(db):
    my, mx = stdscr.getmaxyx()
    now = dt.date.today()

    # Add the text
    stdscr.addstr(my - 9, mx - 28, var['opened_db'])
    stdscr.addstr(my - 7, mx - 28, "Mois précédent :")
    stdscr.addstr(my - 6, mx - 28, "Solde actuel :")
    stdscr.addstr(my - 4, mx - 19, now.strftime("%d/%m/%Y"))

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
    if float(c_a) <= 0:
        stdscr.addstr(my - 6, mx - 11, c_a, crs.color_pair(1))
    elif float(p_a) > float(c_a):
        stdscr.addstr(my - 6, mx - 11, c_a, crs.color_pair(4))
    else:
        stdscr.addstr(my - 6, mx - 11, c_a, crs.color_pair(2))


def draw_log():
    my, mx = stdscr.getmaxyx()
    display_log = var['log'][-6:]
    d_p = 6 - len(display_log)

    for line in display_log:
        stdscr.addstr(my - 9 + d_p, 1, "{0:<{1}}".format(line[0], mx - 31),
                      crs.color_pair(line[1]))
        d_p += 1


def draw_command(command, c_x):
    my, mx = stdscr.getmaxyx()
    stdscr.addstr(my - 2, 1, ' '*(mx - 2))
    stdscr.addstr(my - 2, 1, "(" + var['mode'].upper() + ")",
                  crs.color_pair(5))
    stdscr.addstr(my - 2, 10, command[-(mx - 5):])
    stdscr.move(my - 2, 10 + c_x)


def draw_window(b=True, i=True, p=True, l=True, c=True, cm="", c_x=0):
    if b:
        draw_background()
    if var['opened_db'] != "":
        if i:
            draw_info(var['f_db'].cursor())
        if p:
            draw_payments(var['f_db'].cursor())
    if l:
        draw_log()
    if c:
        draw_command(cm, c_x)


#
# Different actions
#

def _create():
    c_form = Form("Création")
    c_form.add_text("Nom du compte")

    c_form.fill(stdscr)

    if not c_form.cancelled:
        db_name, = c_form.retrieve()
        if var['opened_db'] != "":
            close_database(var['f_db'])

        var['f_db'] = create_database(db_name)

    var['cancelled'] = True


def _load():
    l_form = Form("Ouverture")
    l_form.add_text("Nom du compte")

    l_form.fill(stdscr)

    if not l_form.cancelled:
        db_name, = l_form.retrieve()
        if var['opened_db'] != "":
            close_database(var['f_db'])

        var['f_db'] = open_database(db_name)

    var['cancelled'] = True


def _save():
    if var['opened_db'] != "":
        save_database(var['f_db'])
        save_config(var['cfg_path'])
    else:
        log("Sauvegarde impossible, pas de compte ouvert.", 1)

    var['cancelled'] = True


def _close():
    if var['opened_db'] != "":
        close_database(var['f_db'])
    else:
        log("Fermeture impossible, pas de compte ouvert.", 1)

    var['cancelled'] = True


def _del():
    if var['opened_db'] != "":
        d_form = Form("Suppression")
        d_form.add_carousel("Supprimer " + var['opened_db'], ["Non", "Oui"])

        d_form.fill(stdscr)

        if not d_form.cancelled:
            confirmation, = d_form.retrieve()
            if confirmation == "Oui":
                delete_database(var['f_db'])
    else:
        log("Suppression impossible, pas de compte ouvert.", 1)

    var['cancelled'] = True


def _add():
    if var['opened_db'] != "":
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
    else:
        log("Ajout impossible, pas de compte ouvert.", 1)
        var['cancelled'] = True


def _remove():
    if var['opened_db'] != "" and var['id_list'] != []:
        r_id = var['id_list'][var['selected']]
        db = var['f_db'].cursor()
        db.execute("SELECT name FROM payments WHERE id = ?", (r_id,))
        r_name, = db.fetchone()

        r_form = Form("Suppression d'un paiement")
        r_form.add_carousel("Supprimer '{0}' ?".format(r_name), ["Non", "Oui"])

        r_form.fill(stdscr)

        if not r_form.cancelled:
            confirmation, = r_form.retrieve()
            if confirmation == "Oui":
                delete_payment(db, r_id)
                var['f_db'].commit()
                var['changed'] = True
                var['id_list'].pop(var['selected'])


def _mod():
    if var['opened_db'] != "" and var['id_list'] != []:
        m_id = var['id_list'][var['selected']]
        db = var['f_db'].cursor()
        db.execute("SELECT * FROM payments WHERE id = ?", (m_id,))
        _, o_date, m_name, _, o_amount = db.fetchone()

        m_date = o_date.split("-")
        m_date.reverse()
        m_date = "/".join(m_date)

        m_form = Form("Modification d'un paiement")
        m_form.add_date("Jour de l'opération", m_date)
        m_form.add_text("Nom de l'opération", m_name)
        if o_amount > 0:
            m_form.add_carousel("Type d'opération", ["Crédit", "Débit"])
        else:
            m_form.add_carousel("Type d'opération", ["Débit", "Crédit"])
        m_form.add_text("Montant de l'opération",
                        "{0:9.2f}".format(abs(o_amount/100)).strip())

        m_form.fill(stdscr)

        if not m_form.cancelled:
            change_payment(db, m_id, m_form, o_date, o_amount)
            var['changed'] = True


def _exit():
    if var['opened_db'] != "":
        close_database(var['f_db'])
        save_config(var['cfg_path'])

    var['stay'] = False


def get_command(com=''):
    command = ""
    c_x = 0
    stay = True

    crs.curs_set(0)
    draw_window()

    while stay:
        ch = stdscr.get_wch()

        if ch == 410:  # Window resized
            verif_scroll()
            draw_window(cm=command, c_x=0)
        elif var['mode'] == "global":
            if ch == ":":
                var['mode'] = "command"
                command = ":"
                c_x = 1
            elif ch == "p":
                var['mode'] = "edit"
        elif var['mode'] == "command":
            if ch == 263 and c_x > 0:
                command = command[:c_x - 1] + command[c_x:]
                c_x -= 1
            elif ch == 260:
                if c_x > 0:
                    c_x -= 1
            elif ch == 261:
                if c_x < len(command):
                    c_x += 1
            elif ch == "\x1b":
                command = ""
                c_x = 0
                var['mode'] = "global"
            elif ch == "\n":
                return command.split(' ')
            elif type(ch) is str and ch != "":
                command = command[:c_x] + ch + command[c_x:]
                c_x += 1
        elif var['mode'] == "edit":
            if ch == 258:
                scroll_down()
            elif ch == 259:
                scroll_up()
            elif ch == "d":
                crs.curs_set(2)
                _remove()
            elif ch == "e":
                crs.curs_set(2)
                _mod()
            elif ch == "\x1b":
                var['mode'] = "global"

        if var['mode'] == "command":
            crs.curs_set(2)
            draw_window(False, False, False, True, True, command, c_x)
        elif var['mode'] == "edit":
            crs.curs_set(0)
            if var['changed']:
                verif_scroll()
                draw_window()
                var['changed'] = False
            else:
                draw_window(b=False, i=False)
        elif var['mode'] == "global":
            crs.curs_set(0)
            draw_window(b=False, i=False)

        if ch == '\x11':
            var['stay'] = False
            stay = False


# The main loop

def main():
    init()

    action = ''
    command = ['']

    # Load current month
    draw_window()
    if var['fst_launch']:
        _create()
    elif var['config']['GENERAL']['last_opened'] != "":
        var['f_db'] = open_database(var['config']['GENERAL']['last_opened'])

    # The main loop
    while var['stay']:
        var['cancelled'] = False

        command = get_command()

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
