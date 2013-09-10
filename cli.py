'''
Command line interface to `fuel`

Handles menus, user input and formats output.
'''
import string
import functions as FN

class CLI:
    running = True;
    def __init__(self):
        print('init cli')


    def query(self, tbl, record):
        '''
        Handler for data query.

        Uses form to order output
        '''
        form = FN.forms[tbl]
        for element in form:
            label = string.capwords(element.replace('_', ' '))
            if element == 'date':
                e = input('{1} ({0}):'.format(FN.to_date(record[element]), label))
            else:
                e = input('{1} ({0}):'.format(record[element], label))

            if e:
                if element == 'date':
                    record[element] = FN.to_date(e)
                else:
                    record[element] = e

    def update_service(self, title, vehicle, service=None):
        '''
        Create/update a service record
        '''
        print('\n{} Service Record for {}'.format(title, vehicle['reg_no']))
        if not service:
            service = FN.srec.copy()
            service['vehicle_id']=vehicle['vehicle_id']
            service['date'] = FN.time_now()

        self.query('service', service)
        FN.update_service(service)

    def choose_service(self, vehicle):
        '''
        Get vehicle record.

        Choose vehicle, display fuel by date (10 at a time?), on choice, get new values, save
        '''
        recs = FN.get_service(vehicle)

        print('\nChoose Service Record to edit')
        while True:
            num=1
            print('X) yyyy/mm/dd Item Cost')
            for r in recs:
                print('{0}) {1} {2} {3}'.format(num, FN.to_date(r['date']), r['item'], r['cost']))
                num = num +1
            print('0) Back')

            processed = False
            option = input('Service Record? :')

            # check option is numeric
            if option and option.isnumeric():
                processed = True

                option = int(option)
                # go ahead if option in range, else, re-build menu
                if option == 0:
                    return [False]
                elif (option > 0 and option <= len(recs)):
                    self.update_service("Edit", vehicle, recs[option-1])
                    break
                else:
                    processed = False

            if not processed:
                print('Invalid option [{0}]'.format(option))

    def choose_fuel(self, vehicle):
        '''
        Get vehicle record.

        Choose vehicle, display fuel by date (10 at a time?), on choice, call update_record
        '''
        print('\nChoose Fuel Record to edit')
        # get date-sorted list of fuel for the selected vehicle
        recs = FN.get_fuel(vehicle)

        while True:
            num=1
            print('X) yyyy/mm/dd Odometer Trip Litres Mpg')
            for r in recs:
                print('{0}) {1} {2} {3} {4:.2f} {5:.2f}'.format(num, FN.to_date(r['date']), r['odo'], r['trip'], r['litres'], r['mpg']))
                num = num +1
            print('0) Back')

            processed = False
            option = input('Fuel Record? :')

            if option and option.isnumeric():
                processed = True
                option = int(option)
                # go ahead if option in range, else, re-build menu
                if option == 0:
                    return [False]
                elif (option > 0 and option <= len(recs)):
                    self.update_fuel('Edit', vehicle, recs[option-1])
                    break
                else:
                    processed = False

            if not processed:
                print ('Invalid option [{0}]'.format(option))

    def choose_vehicle(self):
        '''
        Choose vehicle by reg
        '''
        while True:
            num = 1
            print('Choose Vehicle:')
            for v in FN.vehicles:
                print('{0}) {1}'.format(num, v['reg_no']))
                num +=1
            print('0) Back')

            processed = False
            option = None
            option = input('Vehicle? :')

            # check option is numeric
            if option and option.isnumeric():
                processed = True
                option = int(option)

                # go ahead if option in range, else, re-build main_menu
                if option == 0:
                    return [False]
                elif (option > 0 and option <= len(FN.vehicles)):
                    return [True, FN.vehicles[option-1]]
                else:
                    processed = False

            if not processed:
                print ('Invalid option [{0}]'.format(option))

    def update_fuel(self, title, vehicle=None, record=None):
        '''
        Create or update a fuel record
        '''
        print('\n{} Fuel Record for {}:'.format(title, vehicle['reg_no']))
        last = None

        # are we adding a new one or updating an old one?
        if (record == None):
            # adding new, so get the previous value.
            last = FN.last_fuel(vehicle)
            record = FN.frec.copy()
            # set reg for record
            record['vehicle_id'] = vehicle['vehicle_id']
            record['date'] = FN.time_now()

        print(record)
        value = input('Date ({}):'.format(FN.to_date(record['date'])))
        if value:
            record['date'] = FN.to_seconds(value)

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

        mpg = FN.update_fuel(vehicle, record)

        print('\nCalculated MPG: {:.2f}'.format(mpg))

    def predict(self, vehicle):
        '''
        Display predicted range of vehicle
        '''
        print('Prediction for {0}: {1:.2f} miles'.format(vehicle['reg_no'], FN.predict(vehicle)))

    def show_summary(self, vehicle):
        '''
        Print summary about chosen vehicle
        '''
        summary = FN.get_summary(vehicle)
        print('\nSummary for {0}:'.format(vehicle['reg_no']))
        print('Mpg  Min {:.2f}, Avg {:.2f}, Max {:.2f}'.format(summary['mpg']['min'], summary['mpg']['avg'], summary['mpg']['max']))
        print('Trip Min {:.1f}, Avg {:.1f}, Max {:.1f}'.format(summary['trip']['min'], summary['trip']['avg'], summary['trip']['max']))
        print('PPL  Min {:.3f}, Avg {:.3f}, Max {:.3f}'.format(summary['ppl']['min'], summary['ppl']['avg'], summary['ppl']['max']))
        print('Cost Min {:.2f}, Avg {:.2f}, Max {:.2f}'.format(summary['cost']['min'], summary['cost']['avg'], summary['cost']['max']))
        print('Total miles:\t\t {:.1f}'.format(summary['trip']['total']))
        print('Running cost:\t\t {:.2f}'.format(summary['cost']['total']))
        print('Total cost:\t\t {:.2f}'.format(summary['cost']['total'] + vehicle['purchase_price']))
        print('Running cost/mile:\t {:.2f}'.format(summary['cost']['total']/summary['trip']['total']))
        print('Total cost/mile:\t {:.2f}'.format((summary['cost']['total'] + vehicle['purchase_price'])/summary['trip']['total']))
       
    def update_vehicle(self, title, vehicle=None):
        '''
        Modify a vehicle record
        '''
        print('{} Vehicle:'.format(title))
        if not vehicle:
            vehicle = FN.vrec.copy()

        self.query('vehicle', vehicle)

        FN.update_vehicle(vehicle)

    def list_vehicles(self):
        '''
        List known vehicles
        '''
        print('List Vehicles:')
        for v in FN.vehicles:
            print('{0} {1} {2} {3} {4} litres'.format(v['year'], v['make'], v['model'], v['reg_no'], v['fuel_cap']))

    def remove_vehicle(self, vehicle):
        '''
        Remove vehicle from data
        '''
        print('Remove Vehicle:')
        confirm = input('Remove {0}? [y/N]:'.format(vehicle['reg_no'])).lower()
        if confirm == 'y':
            FN.remove_vehicle(vehicle)

    def vehicle_menu(self):
        '''
        Manage vehicles sub-main_menu
        '''
        while True:
            print('''Vehicles:
            1) Add
            2) Edit
            3) List
            4) Remove
            0) Back to Main Menu
            ''')
            processed = False
            option = input('Option? :')

            # check option is numeric
            if option and option.isnumeric():
                processed = True
                option = int(option)

                if option == 0:
                    break
                elif option == 1:
                    self.update_vehicle('Add')
                elif option == 2:
                    r = self.choose_vehicle()
                    if r[0]:
                        self.update_vehicle(r[1])
                elif option == 3:
                    self.list_vehicles()
                elif option == 4:
                    r = self.choose_vehicle()
                    if r[0]:
                        self.remove_vehicle(r[1])
                else:
                    processed = False

            if not processed:
                print('Invalid option [{0}]'.format(option))

    def main_menu(self):
        '''
        Print main menu
        '''
        while self.running:
            print('''\nFuel Economy and Service Records
            1) Add Fuel Record
            2) Edit Fuel Record
            3) Add Service Record
            4) Edit Service Record
            5) Show Summary
            6) Predict Range
            7) Vehicle Management
            8) Help
            0) Quit
            ''')
            processed = False
            option = None
            option = input('Option? :')

            # check option is numeric
            if option and option.isnumeric():
                processed = True
                option = int(option)

                if option == 1:
                    r = self.choose_vehicle()
                    if r[0]:
                        self.update_fuel('Add', r[1])
                elif option == 2:
                    r = self.choose_vehicle()
                    if r[0]:
                        self.choose_fuel(r[1])
                elif option == 3:
                    r = self.choose_vehicle()
                    if r[0]:
                        self.update_service('Add', r[1])
                elif option == 4:
                    r = self.choose_vehicle()
                    if r[0]:
                        self.choose_service(r[1])
                elif option == 5:
                    r = self.choose_vehicle()
                    if r[0]:
                        self.show_summary(r[1])
                elif option == 6:
                    r = self.choose_vehicle()
                    if r[0]:
                        self.predict(r[1])
                elif option == 7:
                    self.vehicle_menu()
                elif option == 8:
                    self.help()
                elif option == 0:
                    FN.exit()
                    self.running=False
                else:
                    processed = False

            if not processed:
                print('Invalid option [{0}]'.format(option))

    def help(self):
        '''Print help'''
        print('Insert Help Here')

    def start(self):
        self.main_menu()
