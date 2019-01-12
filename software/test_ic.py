#!/usr/bin/env python3

import natsort
import glob
import re
import parse
import sys

ic = parse.IC(parse.parse_file('74ls00.md'))
print("Properties")
print(ic.properties)
print("")
print("Pins")
print(ic.pins)
print("")
print("Template")
print(ic.template)
print("Tests")
print(ic.tests)
print("")

for pin in ic.pins.keys():
    if ic.pins[pin][0] == 'I':
        print("Pin {0} set to INPUT".format(pin))
    elif ic.pins[pin][0] == 'O':
        print("Pin {0} set to OUTPUT".format(pin))
    elif ic.pins[pin][0] == '0':
        print("Pin {0} set to STATIC LOW".format(pin))
    elif ic.pins[pin][0] == '1':
        print("Pin {0} set to STATIC HIGH".format(pin))
    else:
        raise AssertionError("Don't understand {0}".format(ic.pins[pin][0]))

sys.exit(1)

ics = []
for icdef in glob.glob('*.md'):
    icdata = parse.parse_file(icdef)
    print(parse.IC(icdata))
    ics.append(parse.IC(icdata))

while True:
    ic_id_to_test = input("Enter IC name/number to test> ")
    matching_ics = filter( lambda x: re.match( '^' + ic_id_to_test + '.*$', x.properties['NAME']), ics )
    if not matching_ics:
        print("Error: No matching IC defintions found.")
        continue
    elif len(matching_ics) > 1:
        print("")
        print("Multiple IC defintion matches found. Please select one:")
        print("")
        match = dict(enumerate(matching_ics, 1))
        for icid in match.keys():
            print("    [{0}] {1}".format( icid, match[icid]))
        selected = raw_input("   >>> ")
        ic_to_test = match[int(selected)]
    else:
        ic_to_test = matching_ics[0]
    print("Testing IC [{0}]".format(matching_ics[0]))
    print("")