#!/usr/bin/env python3
#
#https://gist.github.com/lchi/7f749b60c64f271fb564fcf1a1f5ac07/f39ea558bff858615b65de82359d281ffa691d8c

import requests
import bs4 as bs
import lxml
import sys
import argparse
import logging

def arg_handler():
    parser = argparse.ArgumentParser()
    parser.add_argument('line', type=str, help='Transit line to get status of. ' +
                        'Use "list" to see the list of valid transit lines.')
    parser.add_argument('--debug', action='store_true')
    return parser.parse_args()

def sauce():
    Url = r'http://web.mta.info/status/serviceStatus.txt'
    logging.debug('Getting ' + Url)
    sauce = requests.get(Url, timeout=5)
    if sauce.status_code != 200:
        print(r'Failed to open url. Received: ' + str(sauce.status_code))
        sys.exit(2)
    return bs.BeautifulSoup(sauce.content, 'lxml')

def dict_maker(content):
    logging.debug('Building associative array of lines and their current status.')
    lines_dict = {}
    lines = content.find_all('line')
    for line in lines:
        lines_dict[line.find('name').text] = line.find('status').text
    return lines_dict

def transit_lines(myDict):
    logging.debug('Printing line names from array')
    return ( key for key in myDict.keys() )

def line_status(line,myDict):
    logging.debug('Formatting line status for Nagios.')
    status_d = {'GOOD SERVICE':'OK - No delays', 'DELAYS':'CRITICAL - Delays',
                'PLANNED WORK':'CRITICAL - Planned Work',
                'SERVICE CHANGE':'CRITICAL - Service Change'}
    return status_d[myDict[line]]

def status_response(line,myDict):
    if line in myDict.keys():
        logging.debug('Found ' + line + '. Displaying status.')
        print(line_status(line,myDict))
    elif line == 'list':
        [ print(line) for line in transit_lines(myDict) ]
    else:
        print(line + ' is not a MTA transit line. \nUse "' + sys.argv[0] +
        ' list" to view valid lines.')
        sys.exit(2)

def main():
    args = arg_handler()
    if args.debug: logging.basicConfig(level=logging.DEBUG)
    soup = sauce()
    lines_d = dict_maker(soup)
    status_response(args.line,lines_d)

if __name__ == '__main__':
    main()
