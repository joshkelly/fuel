#!/usr/bin/python3

from operator import itemgetter
import json

ltr_gal_conv = 4.54609 # liters in an imperial gallon
vdat = 'vehicles.dat'
vehicles = []

rdat = 'records.dat'
records = []

sdat = 'summaries.dat'
summaries = []

svg = ''' <svg xmlns="http://www.w3.org/2000/svg" version="1.1" width="800" height="600">
	<text x="300" y="25" text-anchor="middle" stroke="black" font-weight='normal'>Fuel Economy</text>
	<line stroke="black" x1="50" y1="50" x2="50" y2="550"/>
    {0}
	<line stroke="black" x1="50" y1="550" x2="750" y2="550"/>
</svg>
'''

def add_vehicle():
    vehicle = {'make':'', 'model':'', 'year':'', 'reg':'', 'ftc':0}
    print('Add Vehicle:')
    vehicle['make'] = input('Make:')
    vehicle['model'] = input('Model:')
    vehicle['year'] = input('Year:')
    vehicle['reg'] = input('Reg. No.:')
    vehicle['ftc'] = input('Fuel Tank Capacity (litres):')
    vehicles.append(vehicle)
    save(vdat, vehicles)

def modify_vehicle():
    print('Modify Vehicle:')
    num = 1
    for v in vehicles:
        print('{0}) {1}'.format(num, v['reg']))
        num +=1
    print('0) Back')
    option = int(input('Option? :'))
    if option == 0:
        manage_vehicles()
    else:
        vehicle = vehicles[option-1]
        if not 'ftc' in vehicle:
            vehicle['ftc']=0
        e= input('Make ({0}):'.format(vehicle['make']))
        if e:
            vehicle['make'] = e
        e = input('Model ({0}):'.format(vehicle['model']))
        if e:
            vehicle['model'] = e
        e = input('Year ({0}):'.format(vehicle['year']))
        if e:
            vehicle['year'] = e
        e = input('Reg. No. ({0}):'.format(vehicle['reg']))
        if e:
            vehicle['reg'] = e
        e = input('Fuel Tank Capacity ({0}):'.format(vehicle['ftc'] or 0))
        if e:
            vehicle['ftc'] = int(e)

        save(vdat, vehicles)
        manage_vehicles()

def list_vehicles():
    print('List Vehicle:')
    for v in vehicles:
        print('{0} {1} {2} {3} {4} litres'.format(v['year'], v['make'], v['model'], v['reg'], v['ftc']))

def remove_vehicle():
    print('Remove Vehicle:')
    num = 1
    for v in vehicles:
        print('{0}) {1}'.format(num, v['reg']))
        num +=1
    print('0) Back')
    option = int(input('Option? :'))
    if option == 0:
        manage_vehicles()
    else:
        vehicle = vehicles[option-1]
        confirm = input('Remove {0}? [y/n]:'.format(vehicle['reg'])).lower()
        if confirm == 'y':
            del vehicles[option-1]
            save(vdat, vehicles)
        manage_vehicles()

def manage_vehicles():
    print('''Vehicles:
    1) Add
    2) Modify
    3) Delete
    4) List
    0) Back
    ''')
    option = int(input('Option? :'))
    if option == 0:
        menu()
    elif option == 1:
        add_vehicle()
        manage_vehicles()
    elif option == 2:
        modify_vehicle()
        manage_vehicles()
    elif option == 3:
        remove_vehicle()
        manage_vehicles()
    elif option == 4:
        list_vehicles()
        manage_vehicles()
    else:
        menu()

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

def save(fname, data):
    f = open(fname, 'w')
    for v in data:
        s = json.dumps(v)
        f.write(s+'\n')
    f.close()

def choose_vehicle():
    num = 1
    for v in vehicles:
        print('{0}) {1}'.format(num, v['reg']))
        num +=1

    option = int(input('Vehicle? :'))
    return vehicles[option-1]['reg']

def add_record():
    record = {'date':'', 'litres':0.0, 'ppl':0.0, 'trip':0.0, 'odo':0, 'reg':'', 'notes':''}
    print('Add Record:')
    record['reg'] = choose_vehicle()

    last = prev_record(record['reg'])

    record['date'] = input('Date (yyyy/mm/dd):')
    record['litres'] = float(input('Litres:'))
    record['ppl'] = float(input('Price per Litre:'))
    record['odo'] = int(input('Odometer:'))
    #record['trip'] = float(input('Trip: ({0})'.format((record['odo'] - last['odo']))))
    calc_trip = record['odo'] - last['odo']
    trip = input('Trip: ({0})'.format(calc_trip))
    if trip:
        record['trip'] = float(trip)
    else:
        record['trip'] = calc_trip

    record['notes'] = input('Notes:')
    summarise(record, False)
    print('MPG: {0}'.format(record['mpg']))
    records.append(record)
    save(rdat, records)
    menu()

def summarise(record, doSave):
    if not 'mpg' in record:
        record['gallons'] = record['litres']/ltr_gal_conv
        record['mpg'] = record['trip']/record['gallons']

        if doSave:
            save(rdat, records)

def prev_record(reg):
    curr = None
    for record in records:
        if record['reg'] == reg:
            if curr == None:
                curr = record
            else:
                if curr['date'] < record['date']:
                    curr = record
#            print('record date: {0} vs curr {1}'.format(record['date'], curr['date']))

    return curr

def summary():
    reg = choose_vehicle()
    mpg={'avg':0.0, 'low':float('inf'), 'high':0.0}
    trip={'avg':0.0, 'low':float('inf'), 'high':0.0, 'total':0.0}
    ppl={'avg':0.0, 'low':float('inf'), 'high':0.0}
    print('Summary for {0}:'.format(reg))

    num=0 #number of matching records
    for record in records:
        if record['reg'] == reg:
            summarise(record, True)
            num+=1
            mpg['low']=min(mpg['low'], record['mpg'])
            mpg['high']=max(mpg['high'], record['mpg'])
            mpg['avg'] += record['mpg']
            trip['low']=min(trip['low'], record['trip'])
            trip['high']=max(trip['high'], record['trip'])
            trip['total'] += record['trip']
            ppl['low']=min(ppl['low'], record['ppl'])
            ppl['high']=max(ppl['high'], record['ppl'])
            ppl['avg'] += record['ppl']

    mpg['avg'] /= num
    trip['avg'] = trip['total']/num
    ppl['avg'] /= num

    print('Mpg  Low {:.2f}, Avg {:.2f}, High {:.2f}'.format(mpg['low'], mpg['avg'], mpg['high']))
    print('Trip Low {:.1f}, Avg {:.1f}, High {:.1f}'.format(trip['low'], trip['avg'], trip['high']))
    print('PPL  Low {:.3f}, Avg {:.3f}, High {:.3f}'.format(ppl['low'], ppl['avg'], ppl['high']))
    print('Total miles: {:.2f}'.format(trip['total']))
   
    summaries.append({'mpg':mpg, 'trip':trip, 'ppl':ppl, 'reg':reg})
    save(sdat, summaries)
    menu()

def predict():
    reg = choose_vehicle()
    print('Prediction for {0}'.format(reg))
    vehicle=None
    sum_rec = None
    for v in vehicles:
        if v['reg'] == reg:
            vehicle = v
            break

    for s in summaries:
        if s['reg'] == reg:
            sum_rec = s
            break

    ftcg = vehicle['ftc'] / ltr_gal_conv
    prediction = sum_rec['mpg']['avg'] * ftcg
    print('{:.2f} miles'.format(prediction))
    menu()

def svg_output():
    reg = choose_vehicle()
    vehicle = None
    for v in vehicles:
        if v['reg'] == reg:
            vehicle = v
            break

    for s in summaries:
        if s['reg'] == reg:
            sum_rec = s
            break

    min_mpg = s['mpg']['low']
    max_mpg = s['mpg']['high']
    mpg_range = max_mpg - min_mpg

    # extract records for this vehicle, store in temporary
    recs = []
    num = 0
    for r in records:
        if r['reg'] == reg:
            recs.append(r)
            num += 1
    newlist = sorted(recs, key=itemgetter('date')) 
    print(newlist)

    inner_svg = ''

    tick_dist = 700 / num
    offset=50
    for i in range(num):
        print(i, num)
        x = (i * tick_dist) + 50
        inner_svg += '<line x1="{}" y1="{}" x2="{}" y2="{}" stroke="black"/>\n'.format(x, 550, x, 575)
        inner_svg += '<text x="{}" y="{}" text-anchor="middle" font-size="8" stroke="black">{}</text>\n'.format(x, 575, recs[i]['date'])

    print(inner_svg)
    svg_fname = 'mpg.svg'
    f = open(svg_fname, 'w')
    f.write(svg.format(inner_svg)+'\n')
    f.close()

def menu():
    print('''\nFuel Economy
    1) Add Record
    2) Show Summary
    3) Predict
    4) Graph
    9) Vehicles
    0) Quit
    ''')
    option = int(input('Option? :'))

    if option == 1:
        add_record()
    elif option == 2:
        summary()
    elif option == 3:
        predict()
    elif option == 4:
        svg_output()
    elif option == 9:
        manage_vehicles()
    elif option == 0:
        exit()
    else:
        menu()

'''
load record data
load vehicle data
show main menu
'''
def main():
    load(rdat, records)
    load(vdat, vehicles)
    load(sdat, summaries)
    menu() 

#call main
main()
