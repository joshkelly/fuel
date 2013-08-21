#!/usr/bin/python3

import sys, sqlite3, json, mkdb, math, time

conn = None
cur = None

vehicles = []
fuel = []
service = []

def get_version(name):
    global cur, versions
    cur.execute("select version from versions where name=?", (name,))
    version = cur.fetchone()
    assert version != None
    return version[0]
    
def update_fuel():
    global cur

    version = get_version('fuel')
    
    print('fuel ', version)

    try:
        if version < 2:
            # convert date column to real (drop & re-create table)
            # convert data using strptime
            cur.execute('''select * from fuel''')
            rows = [dict(row) for row in cur]

            cur.execute('''drop table fuel''')
            mkdb.create_fuel()

            for r in rows:
                tm = time.strptime(r['date'], "%Y/%m/%d")
                r['date']=time.mktime(tm)
                cur.execute("insert or replace into fuel values (?,?,?,?,?,?,?,?,?,?)", [r['fuel_id'], r['vehicle_id'], r['date'], r['litres'], r['ppl'], r['trip'], r['odo'], r['cost'], r['mpg'], r['notes']])
    except Exception as err:
        print('Bad Value passed to menu')
        print(err)
        

def update_vehicles():
    global cur

    version = get_version('vehicles')
    
    print('vehicles ', version)

    try:
        if version < 2:
            # convert date column to real (drop & re-ceate table)
            # convert data using strptime
            cur.execute('''select * from vehicles''')
            rows = [dict(row) for row in cur]

            cur.execute('''drop table vehicles''')
            mkdb.create_vehicles()

            for r in rows:
                tm = time.strptime(r['purchase_date'], "%Y/%m/%d")
                r['purchase_date']=time.mktime(tm)
                r['tyre_front_cap']=r['tyre_cap']
                r['tyre_front_type']=r['tyre_type']
                r['tyre_rear_cap']=r['tyre_cap']
                r['tyre_rear_type']=r['tyre_type']
                cur.execute('insert or replace into vehicles values (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)', [r['vehicle_id'], r['reg_no'], r['make'], r['model'], r['year'], r['purchase_price'], r['purchase_date'], r['fuel_cap'], r['fuel_type'], r['oil_cap'], r['oil_type'], r['tyre_front_cap'], r['tyre_front_type'], r['tyre_rear_cap'], r['tyre_rear_type'], r['notes']])
    except Exception as err:
        print(err)
        

def update_service():
    global cur

    version = get_version('service')
    
    print('service ', version)

    try:
        if version < 2:
            # convert date column to real (drop & re-ceate table)
            # convert data using strptime
            cur.execute('''select * from service''')
            rows = [dict(row) for row in cur]

            cur.execute('''drop table service''')
            mkdb.create_service()

            for r in rows:
                tm = time.strptime(r['date'], "%Y/%m/%d")
                r['date']=time.mktime(tm)
                cur.execute('insert or replace into service values (?,?,?,?,?,?,?)', [r['service_id'], r['vehicle_id'], r['date'], r['cost'], r['odo'], r['item'], r['notes']])
    except Exception as err:
        print(err)
        

def main():
    global conn, cur
    # open/create db file
    conn = mkdb.init()
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    update_vehicles()
    update_fuel()
    update_service()

    mkdb.close()
if __name__ == "__main__":
    main()
