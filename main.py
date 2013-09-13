#!/usr/bin/python3

import pdb
import getopt, sys, datetime, sqlite3, string, time, math
import dbi
import functions as FN
from cli.cli import CLI
from gtk.gui import GUI
from operator import itemgetter

debug = False

def usage():
    print('Usage: fuel.py [options]')
    print('-c, --cli use command line interface [default]')
    print('-g, --gtk use gtk gui')
    print('-h, --help print this message and exit')
    print('-d, --debug turn on debug mode, extra output, no saving')

def main():
    '''
    load record data
    load vehicle data
    show main menu
    '''
    global debug, gui
    guiType = 0
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hdcg", ["help", "debug", "cli", "gtk"])
    except getopt.GetoptError as err:
        # print help information and exit:
        print(err) # will print something like "option -a not recognized"
        usage()
        sys.exit(2)


    for o,a in opts:
        if o in ("-d", "--debug"):
            debug=True
        elif o in ("-c", "--cli"):
            guiType = 0
        elif o in ("-g", "--gtk"):
            guiType = 1
        elif o in ("-h", "--help"):
            usage()
            exit()
        else:
            assert False, "unhandled option"

    if debug:
        print('#### DEBUG MODE ####')

    if guiType == 0:
        gui = CLI()
    elif guiType == 1:
        gui = GUI()

    FN.load()
    for v in FN.vehicles:
        FN.fuel_graph(v)
    FN.index()
    gui.start() 

#call main
if __name__ == "__main__":
    main()
