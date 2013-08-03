#!/usr/bin/python3

import sys, sqlite3

conn = None
cur = None

def create_economy():
    print('create_economy')
    global cur
    cur.execute('''create table if not exists fuel_records (reg text, date text, litres real, ppl real, trip real, odo integer, notes text, primary key(reg, odo))''')
    
def create_vehicles():
    global cur
    print ('create_vehicles')
    cur.execute('''create table if not exists vehicles (reg text, make text, model real, year integer, price real, capacity real)''')

def create_misc():
    global cur
    print('create_misc')
    cur.execute('''create table if not exists misc_records (reg text, date text, type text, cost real, odo integer, notes text)''')

def init():
    global conn, cur
    # open/create db file
    conn = sqlite3.connect('ldc_fuel.db')
    cur = conn.cursor()

    create_economy()
    create_vehicles()
    create_misc()

    conn.commit()
    return conn
