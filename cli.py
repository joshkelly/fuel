'''
Command line interface to `fuel`

Handles menus, user input and formats output.
'''
import functions

class CLI:
    def __init__(self):
        print('init cli')

    def main_menu(self):
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
            self.main_menu()

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
                funcitons.graph()
                self.main_menu()
            elif option == 8:
                vehicle_menu()
            elif option == 3:
                add_service()
            elif option == 4:
                edit_service()
            elif option == 0:
                functions.exit()
            else:
                processed = False

        if not processed:
            print('Invalid option [{0}]'.format(option))
            self.main_menu()
