#!/usr/bin/python

import json

vdat = 'vehicles.dat'
vehicles = []

def load_vehicles():
    if len(vehicles) == 0:
        f=0
        try:
            with open(vdat) as f: 
                f.close
        except IOError as e:
            print e
            f = open(vdat, 'w')
            f.close()
            
        f = open(vdat)
        for line in f:
            vehicles.append(json.loads(line))

    print (vehicles)

def save_vehicles():
    f = open(vdat, 'w')
    for v in vehicles:
        s = json.dumps(v)
        f.write(s+'\n')
    f.close()

def add_vehicle():
    vehicle = {'make':'', 'model':'', 'year':'', 'reg':''}
    print 'Add Vehicle:'
    vehicle['make'] = raw_input('Make:')
    vehicle['model'] = raw_input('Model:')
    vehicle['year'] = raw_input('Year:')
    vehicle['reg'] = raw_input('Reg. No.:')
    vehicles.append(vehicle)
    save_vehicles()

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

        save_vehicles()
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
            save_vehicles()
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

def add():
    print 'Add Record'
    menu()

def summary():
    print 'Summary'
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
        add()
    elif option == 2:
        summary()
    elif option == 9:
        manage_vehicles()
    elif option == 0:
        exit()
    else:
        menu()

'''
load vehicle data
show main menu
'''
def main():
    load_vehicles()
    menu() 


#call main
main()
