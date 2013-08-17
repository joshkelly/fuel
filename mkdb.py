import sys, sqlite3

conn = None
cur = None

def create_fuel():
    '''
    Create fuel table and index:
    fuel_id integer, primary key and index
    vehicle_id integer, use reg as look up into vdata
    date text, date of fuelling 
    litres real, litres filled
    ppl real, price per litre
    trip real, distance between fills
    odo integer, odometer reading
    cost real, cost of fill
    mpg real, calculated miles per gallon
    notes text, free text
    '''
    #print('create fuel')
    global cur
    cur.execute('''create table if not exists fuel (fuel_id integer, vehicle_id integer, date text, litres real, ppl real, trip real, odo integer, cost real, mpg real, notes text, primary key (fuel_id asc))''')
    cur.execute('''create unique index if not exists fuel_index on fuel (fuel_id)''')

def create_vehicles():
    ''' 
    Create vehicle table and index:
    vehicle_id integer, primary key and index
    reg_no text, registration number
    make text, 
    model text, 
    year integer, 
    purchase_price real, 
    purchase_date text, 
    fuel_cap real, 
    fuel_type text, 
    oil_cap real,
    oil_type text, 
    tyre_cap real,
    tyre_type text,
    notes text, 
    '''
    global cur
    #print ('create vehicles')
    cur.execute('''create table if not exists vehicles (vehicle_id integer, reg_no text, make text, model text, year integer, purchase_price real, purchase_date text, fuel_cap real, fuel_type text, oil_cap real, oil_type text, tyre_cap real, tyre_type text, notes text, primary key(vehicle_id asc))''')
    cur.execute('''create unique index if not exists vehicle_index on vehicles (vehicle_id)''')

def create_service():
    '''
    Create service table and index
    service_id integer, primary key and index
    vehicle_id integer, fkey into vehicles
    date text, date of service item
    cost real, cost of item
    odo integer, optional
    item text, description of item
    notes text, free text
    '''
    global cur
    #print('create service')
    cur.execute('''create table if not exists service (service_id integer, vehicle_id integer, date text, cost real, odo integer, item text, notes text, primary key (service_id asc))''')
    cur.execute('''create unique index if not exists service_index on service (service_id)''')

def init():
    '''
    Initialise db, connection and cursor.
    Call table create functions.
    Returns connection object
    '''
    global conn, cur
    # open/create db file
    conn = sqlite3.connect('ldc_fuel.db')
    cur = conn.cursor()

    create_fuel()
    create_vehicles()
    create_service()

    conn.commit()
    return conn
