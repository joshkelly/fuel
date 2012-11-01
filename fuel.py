#!/usr/bin/python

import json

conversion = 4.54609 # liters in an imperial gallon
vdat = 'vehicles.dat'
vehicles = []

rdat = 'records.dat'
records = []

def add_vehicle():
    vehicle = {'make':'', 'model':'', 'year':'', 'reg':''}
    print 'Add Vehicle:'
    vehicle['make'] = raw_input('Make:')
    vehicle['model'] = raw_input('Model:')
    vehicle['year'] = raw_input('Year:')
    vehicle['reg'] = raw_input('Reg. No.:')
    vehicles.append(vehicle)
    save(vdat, vehicles)

def modify_vehicle():
    print 'Modify Vehicle:'
    num = 1
    for v in vehicles:
        print '{0}) {1}'.format(num, v['reg'])
        num +=1
    print '0) Back'
    option = int(raw_input('Option? :'))
    if option == 0:
        manage_vehicles()
    else:
        vehicle = vehicles[option-1]
        e= raw_input('Make ({0}):'.format(vehicle['make']))
        if e:
            vehicle['make'] = e
        e = raw_input('Model ({0}):'.format(vehicle['model']))
        if e:
            vehicle['model'] = e
        e = raw_input('Year ({0}):'.format(vehicle['year']))
        if e:
            vehicle['year'] = e
        e = raw_input('Reg. No. ({0}):'.format(vehicle['reg']))
        if e:
            vehicle['reg'] = e

        save(vdat, vehicles)
        manage_vehicles()

def list_vehicles():
    print 'List Vehicle:'
    for v in vehicles:
        print '{0} {1} {2} {3}'.format(v['year'], v['make'], v['model'], v['reg'])

def remove_vehicle():
    print 'Remove Vehicle:'
    num = 1
    for v in vehicles:
        print '{0}) {1}'.format(num, v['reg'])
        num +=1
    print '0) Back'
    option = int(raw_input('Option? :'))
    if option == 0:
        manage_vehicles()
    else:
        vehicle = vehicles[option-1]
        confirm = raw_input('Remove {0}? [y/n]:'.format(vehicle['reg'])).lower()
        if confirm == 'y':
            del vehicles[option-1]
            save(vdat, vehicles)
        manage_vehicles()

def manage_vehicles():
    print '''Vehicles:
    1) Add
    2) Modify
    3) Delete
    4) List
    0) Back
    '''
    option = int(raw_input('Option? :'))
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
            print e
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
        print '{0}) {1}'.format(num, v['reg'])
        num +=1

    option = int(raw_input('Vehicle? :'))
    return vehicles[option-1]['reg']

def add_record():
    record = {'date':'', 'litres':0.0, 'ppl':0.0, 'trip':0.0, 'odo':0, 'reg':'', 'notes':''}
    print 'Add Record:'
    record['reg'] = choose_vehicle()
    record['date'] = raw_input('Date (yyyy/mm/dd):')
    record['litres'] = float(raw_input('Litres:'))
    record['ppl'] = float(raw_input('Price per Litre:'))
    record['trip'] = float(raw_input('Trip:'))
    record['odo'] = int(raw_input('Odometer:'))
    record['notes'] = raw_input('Notes:')
    summarise(record, False)
    print 'MPG: {0}'.format(record['mpg'])
    records.append(record)
    save(rdat, records)
    menu()

def summarise(record, doSave):
    if not 'mpg' in record:
        record['gallons'] = record['litres']/conversion
        record['mpg'] = record['trip']/record['gallons']

        if doSave:
            save(rdat, records)

def summary():
    reg = choose_vehicle()
    mpg={'avg':0.0, 'low':float('inf'), 'high':0.0}
    trip={'avg':0.0, 'low':float('inf'), 'high':0.0, 'total':0.0}
    ppl={'avg':0.0, 'low':float('inf'), 'high':0.0}
    print 'Summary for {0}:'.format(reg)

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

    print 'Mpg  Low {:.2f}, Avg {:.2f}, High {:.2f}'.format(mpg['low'], mpg['avg'], mpg['high'])
    print 'Trip Low {:.1f}, Avg {:.1f}, High {:.1f}'.format(trip['low'], trip['avg'], trip['high'])
    print 'PPL  Low {:.3f}, Avg {:.3f}, High {:.3f}'.format(ppl['low'], ppl['avg'], ppl['high'])
    print 'Total miles: {:.2f}'.format(trip['total'])

    menu()

def menu():
    print '''Fuel Economy
    1) Add Record
    2) Show Summary
    9) Vehicles
    0) Quit
    '''
    option = int(raw_input('Option? :'))

    if option == 1:
        add_record()
    elif option == 2:
        summary()
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
    menu() 

#call main
main()
