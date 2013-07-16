#!/usr/bin/python3

import sys, sqlite3, json

conn = None
cur = None

vdat = 'vehicles.dat'
vehicles = []

rdat = 'records.dat'
records = []

vehicle = {'make':'', 'model':'', 'year':'', 'reg':'', 'ftc':0}
record = {'date':'', 'litres':0.0, 'ppl':0.0, 'trip':0.0, 'odo':0, 'reg':'', 'notes':''}

def load(fname, data):
    if len(data) == 0:
        f=0
        try:
            with open(fname) as f: 
                f.close
        except IOError as e:
            print(e)
            f = open(fname, 'w')
            f.close()
            
        f = open(fname)
        for line in f:
            data.append(json.loads(line))


def create_economy():
    print('create_economy')
    global cur
    cur.execute('''create table if not exists fuel_records (reg text, date text, litres real, ppl real, trip real, odo integer, notes text)''')
    
    cur.execute('''select * from fuel_records''')
    data = cur.fetchall()

    if not data:
        for v in records:
            cur.execute("insert into fuel_records values ('{0}', '{1}', {2}, {3}, {4}, {5}, '{6}')".format(v['reg'], v['date'], v['litres'], v['ppl'], v['trip'], v['odo'], v['notes']))


def create_vehicles():
    global cur
    print ('create_vehicles')
    cur.execute('''create table if not exists vehicles (reg text, make text, model real, year integer, price real, capacity real)''')

    cur.execute('''select * from vehicles''')
    data = cur.fetchall()

    if not data:
        for v in vehicles:
            cur.execute("insert into vehicles values ('{0}', '{1}', '{2}', {3}, 0, {4})".format(v['reg'], v['make'], v['model'], v['year'], v['ftc']))

def create_misc():
    global cur
    print('create_misc')
    cur.execute('''create table if not exists misc_records (reg text, date text, type text, cost real, odo integer, notes text)''')

def main():
    global conn, cur
    # open/create db file
    conn = sqlite3.connect('ldc_fuel.db')
    cur = conn.cursor()

    load(rdat, records)
    load(vdat, vehicles)

    create_economy()
    create_vehicles()
    create_misc()

    conn.commit()
    conn.close()

if __name__ == "__main__":
    main()
