'''
Command line interface to `fuel`

Handles menus, user input and formats output.
'''
import functions as FN

class CLI:
    running = True;
    def __init__(self):
        print('init cli')

    def predict(self, vehicle):
        print('Prediction for {0}: {1:.2f} miles'.format(vehicle['reg_no'], FN.predict(vehicle)))

    def show_summary(self, vehicle):
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
            7) Economy Graph
            8) Vehicle Management
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
                    add_fuel()
                elif option == 5:
                    r = self.choose_vehicle()
                    if r[0]:
                        self.show_summary(r[1])
                elif option == 2:
                    choose_fuel()
                elif option == 6:
                    r = self.choose_vehicle()
                    if r[0]:
                        self.predict(r[1])
                elif option == 7:
                    r = self.choose_vehicle()
                    if r[0]:
                        FN.graph(r[1])
                elif option == 8:
                    vehicle_menu()
                elif option == 3:
                    add_service()
                elif option == 4:
                    edit_service()
                elif option == 0:
                    FN.exit()
                    self.running=False
                else:
                    processed = False

            if not processed:
                print('Invalid option [{0}]'.format(option))
