# -*- coding: utf-8 -*-
"""
@author: Jonathan Reiter
@version: 1.05
"""

import os
import sys
import time
import curses
import argparse
import subprocess
from bwhelper import *




BLK = "\033[30m"       # black
RED = "\033[31m"       # red
GRN = "\033[32m"       # green
YLW = "\033[33m"       # yellow
BLU = "\033[34m"       # blue
PNK = "\033[35m"       # pink
CYN = "\033[36m"       # cyan
WHT = "\033[37m"       # white
NC  = "\033[0;39m"     # reset




THRESHOLD = 0



def printBar(iteration, total, prefix='Progress:', suffix='Complete', decimals=1, bar_length=30):
    """
    @params:
        Name            Required?       Description
        iteration       yes             current iteration (Int)
        total           yes             total iterations (Int)
        prefix          optional        prefix string (str)
        suffix          optional        suffix string (str)
        decimals        optional        positive real number of decimals in %complete (Int)
        bar_length      optional        char length of bar (Int)
    """

    str_format = '{0:.' + str(decimals) + 'f}'
    percents = str_format.format(100 * (iteration / float(total)))
    filled_length = int(round(bar_length * iteration / float(total)))
    fill = '%s█%s' % (GRN, NC) * filled_length + '-' * (bar_length - filled_length)
    fill2 = '%s█%s' % (RED, NC) * filled_length + '-' * (bar_length - filled_length)
    done = '%s█%s' % (RED, NC) * 30


    # change the color of the bar when the number of packets < 75% of the total cap allowed
    if iteration < int(total) * .75:
        sys.stdout.write('\r%s|%s| %s%s %s' % (prefix, fill, percents, '%', suffix)),
        sys.stdout.flush()

    if iteration > int(total) * .75 and iteration < int(total):
        sys.stdout.write('\r%s|%s| %s%s %s' % (prefix, fill2, percents, '%', suffix)),
        sys.stdout.flush()

    if iteration >= int(total):
        sys.stdout.write('\r%s|%s| %s%s %s' % (prefix, done, '100.0', '%', 'Done')),
        sys.stdout.flush()




def verboseBar(obj):
    """
    This will display the initial progress bar
    """
    formats = '{0:.1f}'
    current = runNetstatOut() - SND_BYTES_ORIGINAL[0]
    percent = formats.format(100 * ((current) / float(THRESHOLD)))
    completed_so_far = int(round(30 * (current) / float(THRESHOLD)))
    progress = '=' * completed_so_far + '-' * (30 - completed_so_far)

    if current == THRESHOLD:
        return 'THRESHOLD met!!'

    return progress



def moreVerbose(obj, limit):
    """
    when this function is called more details about the stats will be printed
    to the screen
    """
    BLACK_ON_YELLOW = curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_YELLOW)
    WHITE_ON_RED = curses.init_pair(2, curses.COLOR_WHITE, curses.COLOR_RED)
    CYAN_ON_BLACK = curses.init_pair(3, curses.COLOR_CYAN, curses.COLOR_BLACK)

    verbose = curses.initscr()      # initialize the screen
    curses.start_color()            # enable use of colors
    curses.use_default_colors()     # enable use of colors

    curses.flash()                  # flash the screen
    x_by_y = verbose.getmaxyx()     # this returns a tuple of the terminals window size

    p_out_msg    = "current bytes out:"
    p_in_msg     = "current bytes in:"
    or_p_in_msg  = "original bytes in:"
    or_p_out_msg = "original bytes out:"

    SND_BYTES_ORIGINAL = []
    RCV_BYTES_ORIGINAL = []

    try:
        #for x in range(THRESHOLD):
        while True:
            verbose.nodelay(True)
            char = verbose.getch()
            curses.flushinp()
            verbose.erase()
            verbose.border("|", "|")

            if char == ord('b'):
                mainScreen(obj, limit)
            if char == ord('h'):
                showHelpMenu(obj, verbose, x_by_y, limit)
            if char == ord('q'):
                sys.exit()

            # print some static messages near the top left corner of the window
            #
            verbose.addstr(1, 2, "%s" % p_out_msg)
            verbose.addstr(2, 2, "%s" % p_in_msg)
            verbose.addstr(3, 2, "%s" % or_p_out_msg)
            verbose.addstr(4, 2, "%s" % or_p_in_msg)

            # fill the gap with some dots
            # OS independent
            #
            verbose.addstr(1, len(p_out_msg)    + 2, "." * (x_by_y[1] / 2 - len(p_out_msg)    - 2))
            verbose.addstr(2, len(p_in_msg)     + 2, "." * (x_by_y[1] / 2 - len(p_in_msg)     - 2))
            verbose.addstr(3, len(or_p_out_msg) + 2, "." * (x_by_y[1] / 2 - len(or_p_out_msg) - 2))
            verbose.addstr(4, len(or_p_in_msg)  + 2, "." * (x_by_y[1] / 2 - len(or_p_in_msg)  - 2))

            # the stats should be in the middle of the windows
            #
            if obj.os == 'linux':
                # most Linux distros will not support curses.color attributes
                # add the initial numbers to the list
                #
                SND_BYTES_ORIGINAL.append(obj.getSendBytes())
                RCV_BYTES_ORIGINAL.append(obj.getRecvBytes())

                verbose.addstr(1, x_by_y[1] / 2, "%d B (%s)" % (obj.getSendBytes(), \
                    obj.convertBytes(obj.getSendBytes())), \
                    curses.A_BOLD)

                verbose.addstr(2, x_by_y[1] / 2, "%d B (%s)" % (obj.getRecvBytes(), \
                    obj.convertBytes(obj.getRecvBytes())), \
                    curses.A_BOLD)

                verbose.addstr(3, x_by_y[1] / 2, "%d B (%s)" % (SND_BYTES_ORIGINAL[0], \
                    obj.convertBytes(SND_BYTES_ORIGINAL[0])), \
                    curses.A_BOLD)

                verbose.addstr(4, x_by_y[1] / 2, "%d B (%s)" % (RCV_BYTES_ORIGINAL[0], \
                    obj.convertBytes(RCV_BYTES_ORIGINAL[0])), \
                    curses.A_BOLD)

                # calculate the differences
                #
                diff_out = (obj.getSendBytes() - SND_BYTES_ORIGINAL[0])
                diff_percent = 100 * ((obj.getSendBytes() - SND_BYTES_ORIGINAL[0]) / float(limit))

                # format the percentage of completion
                #
                formats = '{0:.1f}'
                percent = formats.format(100 * ((obj.getSendBytes() - SND_BYTES_ORIGINAL[0]) / float(limit)))

                # display the differences for more information
                #
                verbose.addstr(8, 2, 'Difference:...')
                verbose.addstr(8, 17, '%s' % (obj.convertBytes((obj.getSendBytes()) - SND_BYTES_ORIGINAL[0])), CYAN_ON_BLACK)


            if obj.os == 'macintosh':
                SND_BYTES_ORIGINAL.append(obj.runNetstatIn())
                RCV_BYTES_ORIGINAL.append(obj.runNetstatOut())

                verbose.addstr(1, x_by_y[1] / 2, "%d B (%s)" % (obj.runNetstatOut(), \
                    obj.convertBytes(obj.runNetstatOut())), \
                    curses.A_BOLD)

                verbose.addstr(2, x_by_y[1] / 2, "%d B (%s)" % (obj.runNetstatIn(), \
                    obj.convertBytes(obj.runNetstatIn())), \
                    curses.A_BOLD)

                verbose.addstr(3, x_by_y[1] / 2, "%d B (%s)" % (SND_BYTES_ORIGINAL[0], \
                    obj.convertBytes(SND_BYTES_ORIGINAL[0])), \
                    curses.A_BOLD)

                verbose.addstr(4, x_by_y[1] / 2, "%d B (%s)" % (RCV_BYTES_ORIGINAL[0], \
                    obj.convertBytes(RCV_BYTES_ORIGINAL[0])), \
                    curses.A_BOLD)

                # calculate the differences
                diff_out = (obj.runNetstatOut() - SND_BYTES_ORIGINAL[0])
                diff_percent = 100 * ((obj.runNetstatOut() - SND_BYTES_ORIGINAL[0]) / float(limit))

                # format the percentage of completion
                formats = '{0:.1f}'
                percent = formats.format(100 * ((obj.runNetstatOut() - SND_BYTES_ORIGINAL[0]) / float(limit)))

                if float(percent) < 100.0:
                    verbose.addstr(6, 2, "Progress: |", CYAN_ON_BLACK)
                    verbose.addstr(6, 43, "| %.1f%s Complete" % (float(percent) , '%'), curses.A_BOLD | CYAN_ON_BLACK)

                    verbose.addstr(6, 13, '%s' % verboseBar(obj))

                if float(percent) >= 100.0:
                    done = '=' * 13 + 'DONE' + '=' * 13
                    verbose.addstr(6, 2, "Progress: |", curses.A_BOLD | CYAN_ON_BLACK)
                    verbose.addstr(6, 13, done, curses.A_BLINK | WHITE_ON_RED)
                    verbose.addstr(6, 43, "| 100% Complete", curses.A_BOLD | CYAN_ON_BLACK)



            # show the full path of the log file
            # and the number of bytes being written to it each loop
            path = showLogs(obj)[0]
            num_of_bytes = showLogs(obj)[1]
            verbose.addstr(10, 2, '%s', path, curses.A_DIM | CYAN_ON_BLACK)
            verbose.addstr(11, 2, '%s', str(num_of_bytes), curses.A_DIM | CYAN_ON_BLACK)

            verbose.refresh()
            time.sleep(.1)

    except KeyboardInterrupt:
        curses.endwin()
    finally:
        curses.endwin()

    sys.exit(0)



def mainScreen(obj, limit):
    """
    stuff
    """

    stdscrn = curses.initscr()
    x_by_y = stdscrn.getmaxyx()
    curses.start_color()
    curses.use_default_colors()
    curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_YELLOW)
    curses.init_pair(2, curses.COLOR_WHITE, curses.COLOR_RED)
    curses.init_pair(3, curses.COLOR_CYAN, curses.COLOR_BLACK)
    stdscrn.erase()

    SND_BYTES_ORIGINAL = []
    RCV_BYTES_ORIGINAL = []

    # get the initial values in/out for comparison
    if obj.os == 'macintosh':
        SND_BYTES_ORIGINAL.append(obj.runNetstatOut())
        RCV_BYTES_ORIGINAL.append(obj.runNetstatIn())
    if obj.os == 'linux':
        SND_BYTES_ORIGINAL.append(obj.getRecvBytes())
        RCV_BYTES_ORIGINAL.append(obj.getSendBytes())

    try:
        printBar(0, limit)
        stdscrn.clear()
        #for start in range(limit):
        while True:
            stdscrn.nodelay(True)
            char = stdscrn.getch()
            curses.flushinp()
            stdscrn.clear()

            if char == ord('h'):
                showHelpMenu(obj, stdscrn, x_by_y, limit)
            if char == ord('v'):
                moreVerbose(obj, limit)
            if char == ord('q'):
                sys.exit()

            if obj.os == 'macintosh':
                #SND_BYTES_ORIGINAL.append(obj.runNetstatOut())
                stdscrn.addstr(0, 0, "bytes out: %d\nbytes in:  %d\n" % (obj.runNetstatOut(), obj.runNetstatIn()))
                stdscrn.addstr(2, 0, "out diff: %d\nin diff:  %d\n" % (obj.runNetstatOut() - SND_BYTES_ORIGINAL[0], obj.runNetstatIn() - RCV_BYTES_ORIGINAL[0]))
                stdscrn.addstr(4, 0, "limit: %d\n" % limit)
                printBar( obj.runNetstatOut() - SND_BYTES_ORIGINAL[0], limit)


            if obj.os == 'linux':
                #SND_BYTES_ORIGINAL.append(obj.getRecvBytes())
                stdscrn.addstr(0, 0, "bytes out: %d\nbytes in:  %d\n" % (obj.getSendBytes(), obj.getRecvBytes()))
                printBar( obj.getSendBytes() - SND_BYTES_ORIGINAL[0], limit)


            time.sleep(.1)

    finally:
        curses.endwin()






def showHelpMenu(obj, window, x_by_y, limit):
    """
    this function will display the help menu as the stats are still
    being displayed live in the upper left hand corner
    """

    # find the center of the screen
    center_x = x_by_y[1] / 2
    center_y = x_by_y[0] / 2

    help_msg = "Help Menu"

    try:
        for i in range(limit):
            # make this NON-BLOCKING so loop doesn't hang and wait
            # for user input
            window.nodelay(True)        # this is the NON-BLOCKING enabler
            char = window.getch()       # this is to get a single char from STDIN
            curses.flushinp()           # if user enters more keys then flush all from the list
            window.erase()              # erase the entire screen for live updates

            # this series of if statements will be looking for keypresses
            # from the user during run time.  once matched program execution
            # will jump to specified function
            if char == ord('b'):
                mainScreen(obj, limit)
            if char == ord('h'):
                showHelpMenu(obj, window, x_by_y, limit)
            if char == ord('l'):
                showLogs(obj)
            if char == ord('v'):
                moreVerbose(obj, limit)
            if char == ord('q'):
                sys.exit()
            #if char == ord('r'):
            #    pass

            # make a box around the help menu
            window.hline(center_y - 17, center_x - 15, '*', 30)
            window.hline(center_y - 9, center_x - 15, '*', 30)
            window.vline(center_y - 17, center_x - 17, '*', 9)
            window.vline(center_y - 17, center_x + 16, '*', 9)

            if obj.os == 'macintosh':
                window.addstr(center_y - 16, center_x - len(help_msg) / 2, help_msg, curses.A_BLINK | curses.color_pair(3))

            if obj.os == 'linux':
                window.addstr(center_y - 16, center_x - len(help_msg) / 2, help_msg, curses.A_BOLD)

            window.addstr(center_y - 15, center_x - 14, 'b - show fancy progress bar')
            window.addstr(center_y - 14, center_x - 14, 'h - show this help menu')
            window.addstr(center_y - 13, center_x - 14, 'l - show logging information')
            window.addstr(center_y - 12, center_x - 14, 'q - quit this program')
            #window.addstr(center_y - 11, center_x - 14, 'r - read from a log file')
            window.addstr(center_y - 11, center_x - 14, 'v - show verbose stats')

    except:
        curses.endwin()
    finally:
        curses.endwin()



def showLogs(obj):
    """
    This function will show some log output and create a log file
    This function will return a tuple of the log folder path and size of bytes written
    """
    home_dir = os.getenv('HOME')
    log_file = 'bwcheck.log'
    log_file_full_path = os.path.join(obj.full_logfolder_path, log_file)


    with open( log_file_full_path, 'w') as logs:

        if obj.os == 'macintosh':
            logs.write(time.asctime() + ":" + obj.runNetstatIn() + ":" + obj.runNetstatOut() + "\n")
            return log_file_full_path, sys.getsizeof(time.asctime() + ":" + obj.runNetstatIn() + ":" + obj.runNetstatOut() + "\n")

        if obj.os == 'linux':
            logs.write(time.asctime() + ":" + obj.getRecvBytes() + ":" + obj.getSendBytes() + "\n")
            return log_file_full_path, sys.getsizeof(time.asctime() + ":" + obj.getRecvBytes() + ":" + obj.getSendBytes() + "\n" )
    



    
def firstRun(obj):
    """This will check the initial setup"""
    if not obj.checkConfigs():
        print("%s[+]%s This is the first run time%s" % (GRN, YLW, NC))
        print("%s[+]%s Setting up your environment...%s" % (GRN, YLW, NC))
        return False
    return True




def main():
    """
    doc string here
    """
    bw_msg = "This is a bandwidth progam that will monitor the amount of traffic to and from the system"
    parser = argparse.ArgumentParser(description=bw_msg)
    parser.add_argument("--eth0", help="Choose the eth0 interface", action="store_true", dest="eth0")
    parser.add_argument("-I", "--init", help="This is the explicit initial run of the program", action="store_true", dest="init")
    parser.add_argument("-l", "--list", help="List available interfaces found", action="store_true", dest="list")
    parser.add_argument("-i", "--interface", help="Specify an interface", dest="interface")
    parser.add_argument("-L", "--limit", help="Set a bandwidth limit in Mb", dest="limit", type=int, default=15)

    args = parser.parse_args()

    interface_object = GetBandWidth()
    first_iface = interface_object.interfaces[0]

    ready_to_run = False

    if args.limit:
        args.limit = int(args.limit) * 1024 * 1024
        print("{}[+]{} Limit set to {}{} B{}".format(GRN, YLW, CYN, THRESHOLD, NC))

    if args.list:
        # if the list flag is present then list all interfaces available on the system
        print("{}[+]{} Available interfaces on this system{}".format(GRN, YLW, NC))
        for index, iface in enumerate(interface_object.interfaces):
            form = "\t{0}{1:<4}{2}{3:>" + str(len(iface) + 2) + "}{4}"
            print(form.format(CYN, index, YLW, iface, NC))
        sys.exit()

    if args.interface:
        # if a specific interface is chosen show the user their choice and move to initCheck()
        # make sure valid interface was chosen!
        if args.interface not in interface_object.interfaces:
            print("{}[!] Not a valid interface{}".format(RED, NC))
            sys.exit()
        print("{}[+] {}Interface{} {}{} selected{}".format(GRN, YLW, CYN, args.interface, YLW, NC))
        interface_object.iface = args.interface
        ready_to_run = True

        # run the first check to make sure environment is setup and proper functions for os are ran
        if not firstRun(interface_object):
            interface_object.copyTXFiles()
            ready_to_run = True

    if args.eth0:
        interface_object.iface = 'eth0'
        if not firstRun(eth0):
            interface_object.copyTXFiles()
            ready_to_run = True

    if args.init and not args.interface:
        print("{0}[!]{1}{2} {3}chosen for you{4}".format(RED, CYN, first_iface, YLW, NC))
        if not firstRun(interface_object):
            interface_object.copyTXFiles()
            ready_to_run = True

    if ready_to_run:
        print("Running")
        mainScreen(interface_object, args.limit)




if __name__ == '__main__':
    main()
