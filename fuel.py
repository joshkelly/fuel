#!/usr/bin/python3

import pdb
import getopt, sys, datetime, sqlite3, string, time
import json
import mkdb
from operator import itemgetter

conn = None
cur = None
debug=False
ltr_gal_conv = 4.54609 # liters in an imperial gallon
vehicles = []
fuel = []
summaries = []

vrec = {'vehicle_id' : None, 'reg_no' :'', 'make' :'', 'model' :'', 'year' : 0, 'purchase_price' : 0, 'purchase_date' :'', 'fuel_cap' : 0, 'fuel_type' :'', 'oil_cap' : 0, 'oil_type' :'', 'tyre_cap' : 0, 'tyre_type' :'', 'notes' :''}
frec = {'fuel_id':None, 'vehicle_id':0, 'date':'', 'litres':0, 'ppl':0, 'trip':0, 'odo':0, 'cost':0, 'mpg':0, 'notes':''}
srec = {'service_id':None, 'vehicle_id':0, 'date':'', 'cost':0, 'odo':0, 'item':'', 'notes':''}

forms={
    'vehicle':['reg_no', 'make', 'model', 'year', 'purchase_price', 'purchase_date', 'fuel_cap', 'fuel_type', 'oil_cap', 'oil_type', 'tyre_cap', 'tyre_type', 'notes'],
    'fuel':['vehicle_id', 'date', 'litres', 'ppl', 'trip', 'odo', 'cost', 'notes'],
    'service':['date', 'cost', 'odo', 'item', 'notes']
}

svg = '''
<svg xmlns="http://www.w3.org/2000/svg" version="1.1" width="800" height="600">
	<text x="400" y="25" text-anchor="middle" fill="black" stroke="none" font-weight='normal'>Fuel Economy for {0}</text>
	<line stroke="black" x1="50" y1="550" x2="750" y2="550"/><!-- xaxis 700 wide-->
	<line stroke="black" x1="50" y1="50"  x2="50"  y2="550"/><!-- yaxis 500 tall -->
    {1}
</svg>
'''

def to_date(secs):
    '''Convert seconds to date string'''
    return time.strftime("%Y/%m/%d", time.localtime(secs))

def to_seconds(date):
    '''Convert date string to seconds'''
    return time.mktime(time.strptime(date, "%Y/%m/%d"))

def query(tbl, record):
    '''
    Handler for data query.

    Uses form to order output
    '''
    global forms

    form = forms[tbl]
    for element in form:
        label = string.capwords(element.replace('_', ' '))
        e = input('{1} ({0}):'.format(record[element], label))
        if e:
            record[element] = e

def add_vehicle():
    '''
    Add new vehicle record
    '''
    global vehicles
    vehicle = vrec.copy()
    print('Add Vehicle:')
    query('vehicle', vehicle)
    save('vehicles', vehicle)
    vehicle_menu()

def edit_vehicle():
    '''
    Modify a vehicle record
    '''
    print('Modify Vehicle:')
    vehicle = choose_vehicle()
    query('vehicle', vehicle)

    save('vehicles', vehicle)

    vehicle_menu()

def list_vehicles():
    '''
    List known vehicles
    '''
    print('List Vehicles:')
    for v in vehicles:
        print('{0} {1} {2} {3} {4} litres'.format(v['year'], v['make'], v['model'], v['reg_no'], v['fuel_cap']))
    vehicle_menu()

def remove_vehicle():
    '''
    Remove vehicle from data
    '''
    global vehicles, cur
    print('Remove Vehicle:')
    vehicle = choose_vehicle()
    confirm = input('Remove {0}? [y/N]:'.format(vehicle['reg_no'])).lower()
    if confirm == 'y':
        cur.execute('delete from vehicles where reg_no="{0}"'.format(vehicle['reg_no']))
        load()
    vehicle_menu()

def load():
    '''
    Load data from DB.
    Establish connection and get cursor.
    '''
    global conn, cur, fuel, vehicles, service
    if conn == None:
        conn = mkdb.init()
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()

    # get data, copy to editable dictionary, inform user of record count
    cur.execute('select * from fuel')
    fuel = [dict(row) for row in cur]
    print('Loaded {} fuel records.'.format(len(fuel)))
    
    cur.execute('select * from vehicles')
    vehicles = [dict(row) for row in cur]
    print('Loaded {} vehicles.'.format(len(vehicles)))

    cur.execute('select * from service')
    service = [dict(row) for row in cur]
    print('Loaded {} service records.'.format(len(service)))

def save(tbl, rec):
    '''
    Save data to DB.
    Check `tbl` to handle `rec` properly 
    '''
    global cur
    if tbl == 'fuel':
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
        cur.execute("insert or replace into fuel values (?,?,?,?,?,?,?,?,?,?)", [rec['fuel_id'], rec['vehicle_id'], rec['date'], rec['litres'], rec['ppl'], rec['trip'], rec['odo'], rec['cost'], rec['mpg'], rec['notes']])
    elif tbl == 'vehicles':
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
        cur.execute('insert or replace into vehicles values (?,?,?,?,?,?,?,?,?,?,?,?,?,?)', [rec['vehicle_id'], rec['reg_no'], rec['make'], rec['model'], rec['year'], rec['purchase_price'], rec['purchase_date'], rec['fuel_cap'], rec['fuel_type'], rec['oil_cap'], rec['oil_type'], rec['tyre_cap'], rec['tyre_type'], rec['notes']])
    elif tbl == 'service':
        # service_id integer, primary key and index
        # vehicle_id integer, fkey into vehicles
        # date text, date of service item
        # cost real, cost of item
        # odo integer, optional
        # item text, description of item
        # notes text, free text
        cur.execute('insert or replace into service values (?,?,?,?,?,?,?)', [rec['service_id'], rec['vehicle_id'], rec['date'], rec['cost'], rec['odo'], rec['item'], rec['notes']])
    else:
        print('Unrecognised table:', tbl)

    load()

def choose_vehicle():
    '''
    Choose vehicle by reg
    '''
    global vehicles
    num = 1
    for v in vehicles:
        print('{0}) {1}'.format(num, v['reg_no']))
        num +=1
    print('0) Back')

    processed = False
    option = None
    option = input('Vehicle? :')

    if not option:
        choose_vehicle()

    # check option is numeric
    if option.isnumeric():
        processed = True
        option = int(option)
        # go ahead if option in range, else, re-build main_menu
        if option == 0:
            main_menu()
        elif (option > 0 and option <= len(vehicles)):
            return vehicles[option-1]
        else:
            processed = False

    if not processed:
        print ('Invalid option [{0}]'.format(option))
        choose_vehicle()

def add_fuel():
    '''
    Add new record.
    '''
    vehicle = choose_vehicle()
    print('\nAdd Record for {}:'.format(vehicle['reg_no']))
    update_fuel(vehicle)

def choose_fuel():
    '''
    Get vehicle record.
    Choose vehicle, display fuel by date (10 at a time?), on choice, get new values, save
    '''
    vehicle = choose_vehicle()
    print('\nEdit Record for {}:'.format(vehicle['reg_no']))
    # get date-sorted list of fuel for the selected vehicle
    recs = get_fuel(vehicle)

    num=1
    print('X) yyyy/mm/dd Odometer Trip Litres Mpg')
    for r in recs:
        print('{0}) {1} {2} {3} {4:.2f} {5:.2f}'.format(num, to_date(r['date']), r['odo'], r['trip'], r['litres'], r['mpg']))
        num = num +1
    print('0) Back')

    option = input('Record? :')

    try:
        option = int(option)
        # go ahead if option in range, else, re-build menu
        if option == 0:
            main_menu()
        elif (option > 0 and option <= len(recs)):
            update_fuel(vehicle, recs[option-1])
        else:
            choose_fuel()
    except Exception as err:
        print('Bad Value passed to menu')
        print(err)
        choose_fuel()

def update_fuel(vehicle=None, rec=None):
    '''
    Create or update a fuel record
    '''
    record = frec.copy()
    last = None
    isNew = True

    # did they pass us a vehicle?
    if (vehicle == None):
        vehicle = choose_vehicle()

    # set reg for record
    record['vehicle_id']=vehicle['vehicle_id']
       
    # are we adding a new one or updating an old one?
    if (rec == None):
        # adding new, so get the previous value.
        last = last_fuel(vehicle)
        rec = record
        rec['vehicle_id'] = vehicle['vehicle_id']
    else:
        record = rec
        isNew = False

    value = input('Date ({}):'.format(to_date(record['date'])))
    if value:
        record['date'] = to_seconds(value)

    value = input('Litres ({}):'.format(record['litres']))
    if value:
        record['litres'] = float(value)

    value = input('Price per Litre ({}):'.format(record['ppl']))
    if value:
        record['ppl'] = float(value)

    value = input('Odometer ({}):'.format(record['odo']))
    if value:
        record['odo'] = int(value)

    calc_trip = record['trip'] 
    if last:
        calc_trip = record['odo'] - last['odo']
    trip = input('Trip ({0}):'.format(calc_trip))
    if trip:
        record['trip'] = float(trip)
    else:
        record['trip'] = calc_trip

    value = input('Notes ({}):'.format(record['notes']))
    if value:
        record['notes'] = value

    calc_mpg(record, False)
    print('\n Calculated MPG: {0}'.format(record['mpg']))

    # update database
    save('fuel', record)

    # generate graph
    graph(vehicle)
    main_menu()

def calc_mpg(record, doSave):
    '''
    Calculate MPG for record.
    '''
    record['gallons'] = record['litres']/ltr_gal_conv
    record['mpg'] = record['trip']/record['gallons']

def last_fuel(vehicle):
    '''
    Get last record for this vehicle
    '''
    curr = None
    for record in fuel:
        if record['vehicle_id'] == vehicle['vehicle_id']:
            if curr == None:
                curr = record
            else:
                if curr['date'] < record['date']:
                    curr = record

    return curr

def add_service():
    '''
    Add new service record
    '''
    service = srec.copy()
    vehicle = choose_vehicle()
    service['vehicle_id']=vehicle['vehicle_id']
    print('Add Service Record:')
    query('service', service)
    save('service', service)
    main_menu()

def edit_service():
    '''
    Modify a service record
    '''
    vehicle = choose_vehicle()
    service = choose_service(vehicle)
    
    if service:
        print('now here')
        query('service', service)
        save('service', service)

    main_menu()

def choose_service(vehicle=None):
    '''
    Get vehicle record.
    Choose vehicle, display fuel by date (10 at a time?), on choice, get new values, save
    '''
    if not vehicle:
        vehicle = choose_vehicle()
    print('\nEdit Service Record for {}:'.format(vehicle['reg_no']))
    # get date-sorted list of fuel for the selected vehicle
    cur.execute('select * from service where vehicle_id="{0}" order by date asc'.format(vehicle['vehicle_id']))
    recs = [dict(row) for row in cur]

    num=1
    print('X) yyyy/mm/dd Item Cost')
    for r in recs:
        print('{0}) {1} {2} {3}'.format(num, r['date'], r['item'], r['cost']))
        num = num +1
    print('0) Back')

    processed = False
    option = None
    option = input('Service? :')

    if not option:
        choose_service(vehicle)

    # check option is numeric
    if option.isnumeric():
        processed = True

        option = int(option)
        # go ahead if option in range, else, re-build menu
        if option == 0:
            main_menu()
        elif (option > 0 and option <= len(recs)):
            return recs[option-1]
        else:
            processed = False

    if not processed:
        print('Invalid option [{0}]'.format(option))
        choose_service(vehicle)

def get_summary(vehicle):
    '''
    Get summary record.
    If one exists in collection return that, else, generate a new one
    '''
    sum_rec = None
    for s in summaries:
        if s['reg_no'] == vehicle['reg_no']:
            sum_rec = s
            break

    if sum_rec == None:
        sum_rec = summary(vehicle)

    return sum_rec

def summary(v=None):
    '''
    Create/update summary fuel for a vehicle
    if no vehicle passed, prompt user to choose, calculate, save and display results
    if vehicle passed, calculate, save and return results
    '''
    vehicle=None
    if v == None:
        vehicle = choose_vehicle()
    else:
        vehicle = v

    sum_rec = {
        'mpg':{'avg':0.0, 'min':float('inf'), 'max':0.0},
        'trip':{'avg':0.0, 'min':float('inf'), 'max':0.0, 'total':0.0},
        'ppl':{'avg':0.0, 'min':float('inf'), 'max':0.0},
        'cost':{'avg':0.0, 'min':float('inf'), 'max':0.0, 'total':0.0}
    }

    sql = "select min({0}) as min, max({0}) as max, avg({0}) as avg, sum({0}) as sum from fuel where vehicle_id='{1}'"

    for s in sum_rec:
        cur.execute(sql.format(s, vehicle['vehicle_id']))
        recs = [dict(row) for row in cur]
        sum_rec[s]['avg']=recs[0]['avg']
        sum_rec[s]['min']=recs[0]['min']
        sum_rec[s]['max']=recs[0]['max']
        if s == 'trip' or s == 'cost':
            sum_rec[s]['total']=recs[0]['sum']

    sum_rec['reg_no']=vehicle['reg_no']
    
    sql = "select sum(cost) from service where vehicle_id='{0}'"
    cur.execute(sql.format(vehicle['vehicle_id']))
    sum_rec['cost']


    if v == None:
        print('\nSummary for {0}:'.format(vehicle['reg_no']))
        print('Mpg  Min {:.2f}, Avg {:.2f}, Max {:.2f}'.format(sum_rec['mpg']['min'], sum_rec['mpg']['avg'], sum_rec['mpg']['max']))
        print('Trip Min {:.1f}, Avg {:.1f}, Max {:.1f}'.format(sum_rec['trip']['min'], sum_rec['trip']['avg'], sum_rec['trip']['max']))
        print('PPL  Min {:.3f}, Avg {:.3f}, Max {:.3f}'.format(sum_rec['ppl']['min'], sum_rec['ppl']['avg'], sum_rec['ppl']['max']))
        print('Cost Min {:.2f}, Avg {:.2f}, Max {:.2f}'.format(sum_rec['cost']['min'], sum_rec['cost']['avg'], sum_rec['cost']['max']))
        print('Total miles:\t\t {:.1f}'.format(sum_rec['trip']['total']))
        print('Running cost:\t\t {:.2f}'.format(sum_rec['cost']['total']))
        print('Total cost:\t\t {:.2f}'.format(sum_rec['cost']['total'] + vehicle['purchase_price']))
        print('Running cost/mile:\t {:.2f}'.format(sum_rec['cost']['total']/sum_rec['trip']['total']))
        print('Total cost/mile:\t {:.2f}'.format((sum_rec['cost']['total'] + vehicle['purchase_price'])/sum_rec['trip']['total']))
   
        main_menu()
    else:
        return sum_rec

def predict(vehicle=None):
    '''
    Based on chosen vehicle's average MPG, calculate max distance travelable
    '''
    if vehicle == None:
        vehicle = choose_vehicle()

    print('Prediction for {0}'.format(vehicle['reg_no']))
    sum_rec = get_summary(vehicle)

    ftcg = vehicle['fuel_cap'] / ltr_gal_conv
    prediction = sum_rec['mpg']['avg'] * ftcg
    print('{:.2f} miles'.format(prediction))
    main_menu()

def get_fuel(vehicle):
    '''
    Get all fuel record this vehicle
    '''
    # extract fuel for this vehicle, store in temporary
    mpg_min=99999999
    mpg_max = 0
    recs = []
    num = 0
    dmin=999999999999
    dmax=0
    drange = 0
    for r in fuel:
        if r['vehicle_id'] == vehicle['vehicle_id']:
            m = r['mpg']
            dmax = max(dmax, r['date'])
            dmin = min(dmin, r['date'])
            mpg_max = max(mpg_max, m)
            mpg_min = min(mpg_min, m)

            recs.append(r)
            num += 1

    drange = dmax - dmin
    mpg_range = mpg_max - mpg_min
    recs = sorted(recs, key=itemgetter('date'))
    return recs

def graph(vehicle=None):
    '''
    For a vehicle, create an SVG graph showing the MPG over time.
    Include average MPG.
    '''
    global fuel
    if vehicle == None:
        vehicle = choose_vehicle()
    sum_rec = get_summary(vehicle)
    mpg_avg = sum_rec['mpg']['avg']
    mpg_min=99999999
    mpg_max = 0

    scalex = 400
    scaley = 400

    # extract fuel for this vehicle, store in temporary
    recs = []
    num = 0
    dmin=999999999999
    dmax=0
    drange = 0
    for r in fuel:
        if r['vehicle_id'] == vehicle['vehicle_id']:
            dmax = max(dmax, r['date'])
            dmin = min(dmin, r['date'])
            mpg_max = max(mpg_max, r['mpg'])
            mpg_min = min(mpg_min, r['mpg'])

            recs.append(r)
            num += 1

    drange = dmax - dmin
    mpg_range = mpg_max - mpg_min
    newlist = sorted(recs, key=itemgetter('date'))

    inner_svg = ''

    tick_dist = scalex / num
    offset=50
    for i in range(num):
        #print(i, num)
        x = (i * tick_dist) + 50
        #inner_svg += '<line x1="{}" y1="{}" x2="{}" y2="{}" stroke="grey"/>\n'.format(x, 550, x, 560)
        #inner_svg += '<text x="{}" y="{}" text-anchor="middle" font-size="8" stroke="black">{}</text>\n'.format(x, 575, recs[i]['date'])

    yscale = mpg_max
    xscale = dmax

    path = None
    x=None
    y=None
    for r in newlist:
        x=r['date']
        y=r['mpg']

        # generate x coordinate
        x = dmax - x
        x /= drange
        x *= scalex
        x = scalex -x
        x += 50

        # generate y coordinate
        y = mpg_max - y
        y /= mpg_range
        y *= scaley
        y += 50

        inner_svg += '<circle cx="{:.2f}" cy="{:.2f}" r="3" fill="black"/>'.format(x,y)

        if path == None:
            path = 'M{:.2f},{:.2f}'
        else:
            path += ' L{:.2f},{:.2f}'
        path=path.format(x,y)

        y -= 5
        inner_svg += '<text x="{:.2f}" y="{:.2f}" text-anchor="middle" font-size="10" stroke="none" fill="black">{:.2f}</text>'.format(x,y,r['mpg'])

    inner_svg += '<path d="{}" fill="none" stroke="red" stroke-width="0.5"/>'.format(path)

    # where does the average line go?
    y = mpg_max - mpg_avg
    y /= mpg_range
    y *= scaley
    y += 50
    inner_svg += '<line x1="50" y1="{0}" x2="750" y2="{0}" stroke="grey"/>\n'.format(y)
    inner_svg += '<text x="45" y="{}" dominant-baseline="central" text-anchor="end" font-size="10" stroke="none" fill="blue">{:.2f}</text>'.format(y,mpg_avg)


    #print(inner_svg)
    svg_fname = 'mpg-{}.svg'.format(vehicle['reg_no'])
    f = open(svg_fname, 'w')
    f.write(svg.format(vehicle['reg_no'], inner_svg)+'\n')
    f.close()
    print('File at ',svg_fname)

def vehicle_menu():
    '''
    Manage vehicles sub-main_menu
    '''
    print('''Vehicles:
    1) Add
    2) Edit
    3) List
    4) Remove
    0) Back to Main Menu
    ''')
    processed = False
    option = None
    option = input('Option? :')

    if not option:
        vehicle_menu()

    # check option is numeric
    if option.isnumeric():
        processed = True
        option = int(option)

        if option == 0:
            main_menu()
        elif option == 1:
            add_vehicle()
        elif option == 2:
            edit_vehicle()
        elif option == 3:
            list_vehicles()
        elif option == 4:
            remove_vehicle()
        else:
            processed = False

    if not processed:
        print('Invalid option [{0}]'.format(option))
        vehicle_menu()

def main_menu():
    '''
    Print main menu
    '''
    print('''\nFuel Economy and Service Records
    1) Add Fuel Record
    2) Edit Fuel Record
    3) Add Service Record
    4) Edit Service Record
    5) Show Summary
    6) Predict Range
    7) Economy Graph
    8) Vehicle Management
    0) Quit
    ''')
    processed = False
    option = None
    option = input('Option? :')

    if not option:
        main_menu()

    # check option is numeric
    if option.isnumeric():
        processed = True
        option = int(option)

        if option == 1:
            add_fuel()
        elif option == 5:
            summary()
        elif option == 2:
            choose_fuel()
        elif option == 6:
            predict()
        elif option == 7:
            graph()
            main_menu()
        elif option == 8:
            vehicle_menu()
        elif option == 3:
            add_service()
        elif option == 4:
            edit_service()
        elif option == 0:
            mkdb.close()
            exit()
        else:
            processed = False

    if not processed:
        print('Invalid option [{0}]'.format(option))
        main_menu()

def usage():
    print('Usage: fuel.py [options]')
    print('-h, --help print this message and exit')
    print('-d, --debug turn on debug mode, extra output, no saving')

def index():
    global vehicles

    html = '''<html>
    <head>
    <title>Fuel Economy and Service Records</title>
    </head>
    <body>
    <h1>Fuel Economy and Service Records</h1>
    {0}
    </body>
    </html>
    '''
    links = ''
    link = '''<a href="mpg-{0}.svg">Graph for {0}</a><p/>'''
    for v in vehicles:
        links+=link.format(v['reg_no'])
    f = open('index.html', 'w')
    f.write(html.format(links))
    f.close()
    
def main():
    '''
    load record data
    load vehicle data
    show main menu
    '''
    global debug, vehicles
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hd", ["help", "debug"])
    except getopt.GetoptError as err:
        # print help information and exit:
        print(err) # will print something like "option -a not recognized"
        usage()
        sys.exit(2)


    for o,a in opts:
        if o in ("-d", "--debug"):
            debug=True
        elif o in ("-h", "--help"):
            usage()
            exit()
        else:
            assert False, "unhandled option"

    if debug:
        print('#### DEBUG MODE ####')

    load()
    for v in vehicles:
        graph(v)
    index()
    main_menu() 

#call main
if __name__ == "__main__":
    main()
