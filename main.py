#!/usr/bin/python3

import pdb
import getopt, sys, datetime, sqlite3, string, time, math
import dbi
import functions
from cli import CLI
from operator import itemgetter

debug = False

def usage():
    print('Usage: fuel.py [options]')
    print('-c, --cli use command line interface [default]')
    print('-h, --help print this message and exit')
    print('-d, --debug turn on debug mode, extra output, no saving')

def main():
    '''
    load record data
    load vehicle data
    show main menu
    '''
    global debug, gui
    useCli = True
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hdc", ["help", "debug", "cli"])
    except getopt.GetoptError as err:
        # print help information and exit:
        print(err) # will print something like "option -a not recognized"
        usage()
        sys.exit(2)


    for o,a in opts:
        if o in ("-d", "--debug"):
            debug=True
        elif o in ("-c", "--cli"):
            useCli = True
        elif o in ("-h", "--help"):
            usage()
            exit()
        else:
            assert False, "unhandled option"

    if debug:
        print('#### DEBUG MODE ####')

    if useCli:
        gui = CLI()

    functions.load()
    for v in functions.vehicles:
        functions.graph(v)
    functions.index()
    gui.main_menu() 

#call main
if __name__ == "__main__":
    main()
