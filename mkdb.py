#!/usr/bin/python3

import sys, sqlite3

conn = None
cur = None

def create_economy():
    print('create fuel')
    global cur
    cur.execute('''create table if not exists fuel (vehicle_id integer, date text, litres real, ppl real, trip real, odo integer, cost real, mpg real, notes text)''')
    
def create_vehicles():
    global cur
    print ('create vehicles')
    cur.execute('''create table if not exists vehicles (vehicle_id integer, reg_no text, make text, model text, year integer, purchase_price real, purchase_date text, fuel_cap real, fuel_type text, oil_cap real, oil_type text, tyre_cap real, tyre_type text, notes text, primary key(vehicle_id asc))''')

def create_misc():
    global cur
    print('create service')
    cur.execute('''create table if not exists service (vehicle_id integer, date text, cost real, odo integer, item text, notes text)''')

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
