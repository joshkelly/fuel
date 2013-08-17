#!/usr/bin/python3

import sys, sqlite3, json, mkdb, math

conn = None
cur = None

vdat = 'vehicles.dat'
vehicles = []

rdat = 'records.dat'
records = []

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


def create_fuel():
    global cur
    
    cur.execute('''select * from vehicles''')
    vdata = cur.fetchall()

    cur.execute('''select * from fuel''')
    data = cur.fetchall()

    if not data:
        # fuel_id integer, primary key
        # vehicle_id integer, use reg as look up into vdata
        # date text, map to date
        # litres real, map to 'litres'
        # ppl real, map to 'ppl'
        # trip real, map to 'trip'
        # odo integer, map to 'odo'
        # cost real, calculate as (ppl * litres), store to 2 d.p.
        # mpg real, map to 'mpg'
        # notes text, map to 'notes'
        sql = "insert into fuel values (NULL, {0}, '{1}', {2}, {3}, {4}, {5}, {6}, {7}, '{8}')"
        for v in records:
            vehicleID = None
            for i in vdata:
                if i['reg_no'] == v['reg']:
                    vehicleID = i['vehicle_id']
                    break

            if vehicleID == None:
                print('Warning: no vehicle record for reg:', v['reg'])

            cost = v['ppl'] * v['litres']
            cost = math.floor(cost*100)/100
            cur.execute(sql.format(vehicleID, v['date'], v['litres'], v['ppl'], v['trip'], v['odo'], cost, v['mpg'], v['notes']))


def create_vehicles():
    global cur

    cur.execute('''select * from vehicles''')
    data = cur.fetchall()

    if not data:
        # vehicle_id integer, no data, unique key
        # reg_no text, map to 'reg'
        # make text, map to 'make' 
        # model text, map to 'model'
        # year integer, map to 'year'
        # purchase_price real, no data, 0
        # purchase_date text, no data, 2013/08/16
        # fuel_cap real, map to 'ftc'
        # fuel_type text, no data, ''
        # oil_cap real,no data, 0
        # oil_type text, no data, ''
        # tyre_cap real,no data, 0
        # tyre_type text,no data, ''
        # notes text, no data, ''
        sql = "insert into vehicles values (NULL, '{0}', '{1}', '{2}', {3}, 0, '2013/08/16', {4}, '', 0, '', 0, '', '')"
        for v in vehicles:
            cur.execute(sql.format(v['reg'], v['make'], v['model'], v['year'], v['ftc']))

def create_misc():
    global cur

def main():
    global conn, cur
    # open/create db file
    conn = mkdb.init()
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    load(rdat, records)
    load(vdat, vehicles)

    create_vehicles()
    create_fuel()
    create_misc()

    mkdb.close()
if __name__ == "__main__":
    main()
