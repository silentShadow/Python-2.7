# BWcheck
BWcheck will simply provide an user with the visibility of the amount of traffic going to and from their box on a chosen interface.  

A limit (Mb) can be set to notify the user when that threshold has been met.


## Future features:
- An option should be provided to display stats for all interfaces without a limit
- An audible alert should be made when traffic is nearing it's limit

#### usage: testing-bwcheck.py [-h]  [--help]  [-l]  [-I]  [-i INTERFACE]  [-L LIMIT]

This is a bandwidth progam that will monitor the amount of traffic to and from
the system on a chosen interface

optional arguments:</br>
  -h, --help            show this help message and exit</br>
  -I, --init            explicit initial run of the program to setup the program environment</br>
  -l, --list            list available interfaces found</br>
  -i INTERFACE, --interface INTERFACE
                        specify an interface</br>
  -L LIMIT, --limit LIMIT
                        set a bandwidth limit in Mb</br>
