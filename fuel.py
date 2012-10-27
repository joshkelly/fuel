import json

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
    3) Quit
    '''
    option = int(raw_input('Option? :'))

    if option == 1:
        add()
    elif option == 2:
        summary()
    elif option == 3:
        exit()
    else:
        menu()

menu()
