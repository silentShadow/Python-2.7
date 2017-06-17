# -*- coding: utf-8 -*-

import os
import sys
import time
import subprocess



BLK = "\033[30m"       # black
RED = "\033[31m"       # red
GRN = "\033[32m"       # green
YLW = "\033[33m"       # yellow
BLU = "\033[34m"       # blue
PNK = "\033[35m"       # pink
CYN = "\033[36m"       # cyan
WHT = "\033[37m"       # white
NC  = "\033[0;39m"     # reset



class GetBandWidth():
    def __init__(self, iface='eth0', logfolder='.bwcheck', rxstats='/statistics/rx_bytes', txstats='/statistics/tx_bytes'):

        # determine the os and get a list of all available interfaces on the system
        # the user will have to choose an interface to get stats from or the
        # first interface in the list will be chosen
        #
        # could just get stats on ALL interfaces and display to user but that could
        # be overload if some systems have many NICs like systems that host VMs
        #
        self.iface = iface
        self.rxstats = os.path.join(self.iface, rxstats)                                # join the two locations
        self.txstats = os.path.join(self.iface, txstats)                                # join the two locations
        self.os = self.determineOS()                                                    # get the os
        self.user_rxstats = "rx_stats"                                                  # set the user location
        self.user_txstats = "tx_stats"                                                  # set the user location
        self.logfolder = logfolder                                                      # set the logfolder name .bwcheck
        self.homedir = os.getenv('HOME')                                                # os independent
        self.full_logfolder_path = os.path.join(self.homedir, self.logfolder)           # os independent
        self.bwcheck_rx_path = os.path.join(self.full_logfolder_path, self.rxstats)     # os independent
        self.bwcheck_tx_path = os.path.join(self.full_logfolder_path, self.txstats)     # os independent

        # this section of conditionals tests to see what the OS is
        # and then return a list of available interfaces
        #
        if self.os == 'macintosh':
            self.interfaces = self.getInterfaces('macintosh')

        if self.os == 'linux':
            self.interfaces = self.getInterfaces('linux')
            self.full_rx_path = os.path.join("/sys/class/net", self.rxstats)
            self.full_tx_path = os.path.join("/sys/class/net", self.txstats)

        if self.os == 'windows':
            self.interfaces = self.getInterfaces('windows')




    def getInterfaces(self, ostype):
        """This function will return a list of interfaces available on the system"""
        if ostype == 'macintosh':
            return subprocess.check_output(['ifconfig', '-l']).strip().split()

        if ostype == 'linux':
            return os.listdir('/sys/class/net').strip().split()

        if ostype == 'windows':
            return subprocess.check_output(['ipconfig', '/all'])



    def convertBytes(self, size, precision = 2):
        """
        Given the size in bytes, iterate over a list of formats
        until the size is no longer > 1024
        once that is found there should be a match for the correct conversion

        example:  convertBytes(19256520) returns 18.26Mb (Str)
        """
        formats = ['B', 'Kb', 'Mb', 'Gb', 'Tb']
        index = 0

        while size > 1024 and index < 4:
            index += 1
            size /= 1024.0

        return "%.*f %s" % (precision, size, formats[index])


    def runNetstatOut(self):
        """
        Run the netstat command looking for the last line of results for
        the primary interface

        returns an Int

        pass the results to the convertBytes function for a more human-readble value
        """
        # check the os type
        if self.os == 'macintosh':
            # on the Mac, the bytes out is the next to the last column 
            # of the netstat -b command
            # the -b on Mac shows the bytes in and out on a chosen interface specified by -I
            # the -n is to not resolve numbers
            #
            results = subprocess.check_output(['netstat', '-I', self.iface, '-n', '-b']).splitlines()[-1].split()[-2]

        if self.os == 'windows':
            results = subprocess.check_output(['netstat']).splitlines()

        return int(results)


    def runNetstatIn(self):
        """
        run the netstat command looking for the last line of results for
        the primary interface

        pass the results to the convertBytes function for a more human-readble value
        """
        # check the os type
        if self.os == 'macintosh':
            # on the Mac, the bytes out is the 5th column from the last column
            # of the netstat -b command
            # the -b on Mac shows the bytes in and out on a chosen interface specified by -I
            # the -n is to not resolve numbers
            #
            results = subprocess.check_output(['netstat', '-I', self.iface, '-n', '-b']).splitlines()[-1].split()[-5]

        if self.os == 'windows':
            results = subprocess.check_output(['netstat']).splitlines()


        #last_line = results.splitlines()[1]

        #in_bytes   = int(last_line.split()[3])

        return int(results)



    def determineOS(self):
        """
        This function will attempt to determine the OS in order
        to change how this program functions and gets its information
        """
        platform = sys.platform

        if platform.startswith('darwin'):
            return 'macintosh'
        if platform.startswith('linux'):
            return 'linux'
        if platform.startswith('win'):
            return 'windows'
        return 'Unknown OS'



    def getRecvBytes(self):
        """
        This function will get the bytes sent and returns an Int
        This is for Linux OS only!
        """
        #print("[DEBUG]: running getRecvBytes()")
        #print("\t[DEBUG]: iface: " + self.iface)
        #print("\t[DEBUG]: logfolder: " + self.logfolder)
        #print("\t[DEBUG]: iface_path: " + self.iface_path)
        #print("\t[DEBUG]: full_rx_path: " + self.full_rx_path)

        with open(self.full_rx_path, 'r') as rx:
            bytes_in = rx.readline()
        #print("\t[DEBUG]: Getting bytes in for: %s: %d\n\n" % (self.iface, bytes_in))

        return int(bytes_in)



    def getSendBytes(self):
        """
        This function will get the bytes sent and returns an Int
        This is for Linux OS only!
        """
        #print("[DEBUG]: running getSendBytes()")
        #print("\t[DEBUG]: iface: " + self.iface)
        #print("\t[DEBUG]: logfolder: " + self.logfolder)
        #print("\t[DEBUG]: iface_path: " + self.iface_path)
        #print("\t[DEBUG]: full_rx_path: " + self.full_rx_path)

        with open(self.full_tx_path, 'r') as tx:
            bytes_out = tx.readline()
        #print("\t[DEBUG]: Getting bytes in for: %s: %d\n\n" % (self.iface, bytes_out))

        return int(bytes_out)



    def copyTXFiles(self):
        """This function will copy over the tx and rx files into the progam's main folder to survive reboot"""
        #test to see if the files are already there
        #print("[DEBUG]: running copyTXFiles()")
        #print("\t[DEBUG]: iface: " + self.iface)
        #print("\t[DEBUG]: logfolder: " + self.logfolder)
        #print("\t[DEBUG]: iface_path: " + self.iface_path)
        #print("\t[DEBUG]: full_rx_path: " + self.full_rx_path)
        #print("\t[DEBUG]: full_tx_path: " + self.full_tx_path)
        #print("\t[DEBUG]: full_log_path: " + self.full_logfolder_path)

        # this check is universal as every OS should have a HOME environment variable
        # this script will create a .bwcheck folder in that HOME folder to store logs and other files
        #
        if not os.path.exists(self.full_logfolder_path):
            print("{}[!]{} The {}.bwcheck{} folder does not exist... creating it{}".format(RED, YLW, CYN, YLW, NC))
            time.sleep(.6)
            try:
                if os.mkdir(self.full_logfolder_path):
                    print("{}[+]{} The {}.bwcheck{} folder has been created{}".format(GRN, YLW, CYN, YLW, NC))
                    time.sleep(.6)
            except:
                print("[DEBUG]: .bwcheck was not created")

        # on Mac and Windows, there will be no rx/tx_bytes files to copy over from the /proc
        # need to find out where netstat is pulling its data from and copy those files
        #
        if self.os == 'macintosh' or 'windows':
            print("{}[!]{} This is a {}{}{}, there are no files to copy{}".format(RED, YLW, CYN, self.os, YLW, NC))
            time.sleep(.6)

        # on the Linux systems, copy over the rx/tx_bytes files from the /proc
        # into the .bwcheck folder created earlier
        #
        if self.os == 'linux' and not os.path.exists(self.bwcheck_rx_path):
            print("{}[!]{} The rx_bytes file has not been copied to {}.bwcheck{}".format(RED, YLW, CYN, NC))
            time.sleep(.6)
            if os.system('cp ' + self.full_rx_path + " " + self.bwcheck_rx_path):
                print("{}[+]{} Copied rx files to {}.bwcheck{}".format(GRN, YLW, CYN, NC))

            if not os.path.exists(self.bwcheck_tx_path):
                print("{}[!]{} The tx_bytes file has not been copied to {}.bwcheck{}".format(RED, YLW, CYN, NC))
                time.sleep(.6)
                if os.system('cp ' + self.full_tx_path + " " + self.bwcheck_tx_path):
                    print("{}[+]{} Copied tx files to {}.bwcheck{}".format(GRN, YLW, CYN, NC))

        print("{}[+]{} Your environment is setup{}".format(GRN, YLW, NC))
        time.sleep(.6)


    def checkConfigs(self):
        """This will check the initial configs at first run and returns a boolean value"""
        print("{}[+]{} Your home folder is {}{}{}".format(GRN, YLW, CYN, self.homedir, NC))
        time.sleep(.6)

        # return false if the .bwcheck folder isn't already made
        #
        if not os.path.exists(self.full_logfolder_path):
            print("{}[+]{} Looking for appropriate folder and files...  [ {}{}{} ]{}".format(GRN, YLW, RED, 'FAILED', YLW, NC))
            return False

        print("{}[+]{} Looking for appropriate folder and files...  [ {}{}{} ]{}".format(GRN, YLW, GRN, "OK", YLW, NC))
        print("{}[+]{} Folder found at {}{}{}".format(GRN, YLW, CYN, self.full_logfolder_path, NC))

        time.sleep(.6)

        return True
