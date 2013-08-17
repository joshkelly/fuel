#!/usr/bin/python3

import pdb
import getopt, sys, datetime, sqlite3, string
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

svg = '''
<svg xmlns="http://www.w3.org/2000/svg" version="1.1" width="800" height="600">
	<text x="400" y="25" text-anchor="middle" fill="black" stroke="none" font-weight='normal'>Fuel Economy for {0}</text>
	<line stroke="black" x1="50" y1="550" x2="750" y2="550"/><!-- xaxis 700 wide-->
	<line stroke="black" x1="50" y1="50"  x2="50"  y2="550"/><!-- yaxis 500 tall -->
    {1}
</svg>
'''

'''
Add new vehicle record
'''
def add_vehicle():
    global vehicles
    vehicle = vrec.copy()
    print('Add Vehicle:')
    for e in vehicle:
        query_vehicle(vehicle, e)
    vehicles.append(vehicle)
    save('vehicles', vehicle)
    vehicle_menu()

'''
Handler for data query
'''
def query_vehicle(vehicle, element):
    if element != 'vehicle_id': 
        label = string.capwords(element.replace('_', ' '))
        e = input('{1} ({0}):'.format(vehicle[element], label))
        if e:
            vehicle[element] = e

'''
Modify a vehicle record
'''
def edit_vehicle():
    print('Modify Vehicle:')
    num = 1

    for v in vehicles:
        print('{0}) {1}'.format(num, v['reg_no']))
        num +=1

    print('0) Back')
    option = int(input('Option? :'))
    if option != 0:
        vehicle = vehicles[option-1]
        for e in vehicle:
            query_vehicle(vehicle, e)

        save('vehicles', vehicle)

    vehicle_menu()

'''
List known vehicles
'''
def list_vehicles():
    print('List Vehicles:')
    for v in vehicles:
        print('{0} {1} {2} {3} {4} litres'.format(v['year'], v['make'], v['model'], v['reg_no'], v['fuel_cap']))
    vehicle_menu()

'''
Remove vehicle from data
'''
def remove_vehicle():
    global vehicles, cur
    print('Remove Vehicle:')
    num = 1
    for v in vehicles:
        print('{0}) {1}'.format(num, v['reg_no']))
        num +=1
    print('0) Back')
    option = input('Option? :')

    # check option is numeric
    if option.isnumeric():
        option = int(option)
    else:
        remove_vehicle()

    if option != 0:
        vehicle = vehicles[option-1]
        confirm = input('Remove {0}? [y/N]:'.format(vehicle['reg_no'])).lower()
        if confirm == 'y':
            cur.execute('delete from vehicles where reg_no="{0}"'.format(vehicle['reg_no']))
            load()
    vehicle_menu()

'''
Manage vehicles sub-main_menu
'''
def vehicle_menu():
    print('''Vehicles:
    1) Add
    2) Edit
    3) List
    4) Remove
    0) Back to Main Menu
    ''')
    option = input('Option? :')

    if(option):
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
            vehicle_menu()

'''
Load data from DB.
Establish connection and get cursor.
'''
def load():
    global conn, cur, fuel, vehicles
    if conn == None:
        #conn = sqlite3.connect('ldc_fuel.db')
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

def save(tbl, rec):
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
    else:
        print('Unrecognised table:', tbl)

    load()

'''
Commit and close DB connection
'''
def close():
    global conn
    conn.commit()
    conn.close()

'''
Choose vehicle by reg
'''
def choose_vehicle():
    global vehicles
    num = 1
    for v in vehicles:
        print('{0}) {1}'.format(num, v['reg_no']))
        num +=1
    print('0) Back')

    option = int(input('Vehicle? :'))

    # go ahead if option in range, else, re-build main_menu
    if option == 0:
        main_menu()
    elif (option > 0 and option <= len(vehicles)):
        return vehicles[option-1]
    else:
        choose_vehicle()

'''
Get vehicle record by registration
If no vehicle with that reg, warn and call main_menu
'''
def get_vehicle(reg):
    global vehicles
    vehicle = None
    for v in vehicles:
        if v['reg'] == reg:
            vehicle = v
            break
    if vehicle == None:
        print('No vehicle with that registration [{}]'.format(reg))
        main_menu()

    return vehicle

'''
Add new record, save to fuel.dat
'''
def add_record():
    record = {'date':'', 'litres':0.0, 'ppl':0.0, 'trip':0.0, 'odo':0, 'reg':'', 'notes':''}
    vehicle = choose_vehicle()
    print('\nAdd Record for {}:'.format(vehicle['reg_no']))
    update_record(vehicle)

'''
Get vehicle record.
Choose vehicle, display fuel by date (10 at a time?), on choice, get new values, save
'''
def choose_record():
    vehicle = choose_vehicle()
    print('\nEdit Record for {}:'.format(vehicle['reg_no']))
    # get date-sorted list of fuel for the selected vehicle
    recs = get_fuel(vehicle)

    num=1
    print('X) yyyy/mm/dd Odometer Trip Litres Mpg')
    for r in recs:
        print('{0}) {1} {2} {3} {4:.2f} {5:.2f}'.format(num, r['date'], r['odo'], r['trip'], r['litres'], r['mpg']))
        num = num +1
    print('0) Back')

    option = input('Record? :')

    try:
        option = int(option)
        # go ahead if option in range, else, re-build menu
        if option == 0:
            main_menu()
        elif (option > 0 and option <= len(recs)):
            update_record(vehicle, recs[option-1])
        else:
            choose_record()
    except Exception as err:
        print('Bad Value passed to menu')
        print(err)
        choose_record()

'''
Create or update a fuel record
'''
def update_record(vehicle=None, rec=None):
    record = frec.copy()#{'date':'yyyy/mm/dd', 'litres':0.0, 'ppl':0.0, 'trip':0.0, 'odo':0, 'reg':'', 'notes':''}
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
        last = last_record(vehicle)
        rec = record
        rec['vehicle_id'] = vehicle['vehicle_id']
    else:
        record = rec
        isNew = False

    value = input('Date ({}):'.format(record['date']))
    if value:
        record['date'] = value

    value = input('Litres {}:'.format(record['litres']))
    if value:
        record['litres'] = float(value)

    value = input('Price per Litre {}:'.format(record['ppl']))
    if value:
        record['ppl'] = float(value)

    value = input('Odometer {}:'.format(record['odo']))
    if value:
        record['odo'] = int(value)

    calc_trip = record['trip'] 
    if last:
        calc_trip = record['odo'] - last['odo']
    trip = input('Trip: ({0})'.format(calc_trip))
    if trip:
        record['trip'] = float(trip)
    else:
        record['trip'] = calc_trip

    value = input('Notes {}:'.format(record['notes']))
    if value:
        record['notes'] = value

    calc_mpg(record, False)
    print('\n Calculated MPG: {0}'.format(record['mpg']))
    print(record)

    # update database
    save('fuel', record)

    # generate graph
    graph(vehicle)
    main_menu()

'''
Calculate MPG for record.
If `doSave`, then update fuel file
'''
def calc_mpg(record, doSave):
    #if not 'mpg' in record:
    record['gallons'] = record['litres']/ltr_gal_conv
    record['mpg'] = record['trip']/record['gallons']

    #if doSave:
    #    save(rdat, fuel)

'''
Get last record for this vehicle
'''
def last_record(vehicle):
    curr = None
    for record in fuel:
        if record['vehicle_id'] == vehicle['vehicle_id']:
            if curr == None:
                curr = record
            else:
                if curr['date'] < record['date']:
                    curr = record

    return curr

'''
Get summary record.
If one exists in collection return that, else, generate a new one
'''
def get_summary(vehicle):
    sum_rec = None
    for s in summaries:
        if s['reg_no'] == vehicle['reg_no']:
            sum_rec = s
            break

    if sum_rec == None:
        sum_rec = summary(vehicle)

    return sum_rec

'''
Create/update summary fuel for a vehicle
if no vehicle passed, prompt user to choose, calculate, save and display results
if vehicle passed, calculate, save and return results
'''
def summary(v=None):
    vehicle=None
    if v == None:
        vehicle = choose_vehicle()
    else:
        vehicle = v

    mpg={'avg':0.0, 'min':float('inf'), 'max':0.0}
    trip={'avg':0.0, 'min':float('inf'), 'max':0.0, 'total':0.0}
    ppl={'avg':0.0, 'min':float('inf'), 'max':0.0}
    sum_rec = None

#    for s in summaries:
#        if s['reg'] == reg:
#            sum_rec = s
#            break

    num=0 #number of matching fuel
    for record in fuel:
        if record['vehicle_id'] == vehicle['vehicle_id']:
            #calc_mpg(record, True)
            num+=1
            mpg['min']=min(mpg['min'], record['mpg'])
            mpg['max']=max(mpg['max'], record['mpg'])
            mpg['avg'] += record['mpg']
            trip['min']=min(trip['min'], record['trip'])
            trip['max']=max(trip['max'], record['trip'])
            trip['total'] += record['trip']
            ppl['min']=min(ppl['min'], record['ppl'])
            ppl['max']=max(ppl['max'], record['ppl'])
            ppl['avg'] += record['ppl']

    mpg['avg'] /= num
    trip['avg'] = trip['total']/num
    ppl['avg'] /= num

    if sum_rec != None:
        sum_rec['mpg']=mpg
        sum_rec['trip']=trip
        sum_rec['ppl']=ppl
    else:
        sum_rec = {'mpg':mpg, 'trip':trip, 'ppl':ppl, 'reg_no':vehicle['reg_no']}
    
    if v == None:
        print('\nSummary for {0}:'.format(vehicle['reg_no']))
        print('Mpg  Min {:.2f}, Avg {:.2f}, Max {:.2f}'.format(mpg['min'], mpg['avg'], mpg['max']))
        print('Trip Min {:.1f}, Avg {:.1f}, Max {:.1f}'.format(trip['min'], trip['avg'], trip['max']))
        print('PPL  Min {:.3f}, Avg {:.3f}, Max {:.3f}'.format(ppl['min'], ppl['avg'], ppl['max']))
        print('Total miles: {:.2f}'.format(trip['total']))
   
        main_menu()
    else:
        return sum_rec

'''
Based on chosen vehicle's average MPG, calculate max distance travelable
'''
def predict(vehicle=None):
    if vehicle == None:
        vehicle = choose_vehicle()

    print('Prediction for {0}'.format(vehicle['reg_no']))
    sum_rec = get_summary(vehicle)

    ftcg = vehicle['fuel_cap'] / ltr_gal_conv
    prediction = sum_rec['mpg']['avg'] * ftcg
    print('{:.2f} miles'.format(prediction))
    main_menu()

def get_fuel(vehicle):
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
            d=datetime.datetime.strptime(r['date'], '%Y/%m/%d')
            d = (d-datetime.datetime(1970,1,1)).total_seconds()
            r['secs'] = d
            m = r['mpg']
            dmax = max(dmax, d)
            dmin = min(dmin, d)
            mpg_max = max(mpg_max, m)
            mpg_min = min(mpg_min, m)

            recs.append(r)
            num += 1

    drange = dmax - dmin
    mpg_range = mpg_max - mpg_min
    recs = sorted(recs, key=itemgetter('secs'))
    return recs

'''
For a vehicle, create an SVG graph showing the MPG over time.
Include average MPG.
'''
def graph(vehicle=None):
    global fuel
    if vehicle == None:
        vehicle = choose_vehicle()
    sum_rec = get_summary(vehicle)
    mpg_avg = sum_rec['mpg']['avg']
    #mpg_max = sum_rec['mpg']['max']
    #mpg_min = sum_rec['mpg']['min']
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
            d=datetime.datetime.strptime(r['date'], '%Y/%m/%d')
            d = (d-datetime.datetime(1970,1,1)).total_seconds()
            calc_mpg(r, False)
            r['secs'] = d
            m = r['mpg']
            dmax = max(dmax, d)
            dmin = min(dmin, d)
            mpg_max = max(mpg_max, m)
            mpg_min = min(mpg_min, m)

            recs.append(r)
            num += 1

    drange = dmax - dmin
    mpg_range = mpg_max - mpg_min
    newlist = sorted(recs, key=itemgetter('secs'))
    #print(newlist)

    inner_svg = ''

    tick_dist = scalex / num
    offset=50
    for i in range(num):
        #print(i, num)
        x = (i * tick_dist) + 50
        inner_svg += '<line x1="{}" y1="{}" x2="{}" y2="{}" stroke="grey"/>\n'.format(x, 550, x, 560)
        #inner_svg += '<text x="{}" y="{}" text-anchor="middle" font-size="8" stroke="black">{}</text>\n'.format(x, 575, recs[i]['date'])

    yscale = mpg_max
    xscale = dmax

    path = None
    x=None
    y=None
    for r in newlist:
        x=r['secs']
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

def main_menu():
    print('''\nFuel Economy and Service Records
    1) Add Fuel Record
    2) Edit Fuel Record
    3) Show Summary
    4) Predict Range
    5) Economy Graph
    6) Vehicle Management
    0) Quit
    ''')
    option = input('Option? :')

    #try:
    if(option):
        option = int(option)
        if option == 1:
            add_record()
        elif option == 3:
            summary()
        elif option == 2:
            choose_record()
        elif option == 4:
            predict()
        elif option == 5:
            graph()
            main_menu()
        elif option == 6:
            vehicle_menu()
        elif option == 0:
            close()
            exit()
        else:
            main_menu()
    #except Exception as e:
    #    print('Bad value passed to main_menu')
    #    print(e)
    #    main_menu()

def usage():
    print('hello')

'''
load record data
load vehicle data
show main menu
'''
def main():
    global debug
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
        else:
            assert False, "unhandled option"

    if debug:
        print('#### DEBUG MODE ####')

    load()
    main_menu() 

#call main
if __name__ == "__main__":
    main()
