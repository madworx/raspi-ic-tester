#!/usr/bin/python3

import glob
import re
import sys
import time
import random

import ICDefinitionParser
import RPIICTester

r = RPIICTester.RPIICTester()

ics = []
print("Loading IC definitions.")
# glob the glob....
for icdef in glob.glob('*.md'):
    icdata = ICDefinitionParser.parse_file(icdef)
    ics.append(ICDefinitionParser.IC(icdata))

print("Putting all pins into passive state.")
r.zero_all_pins()

while True:
    print("")
    ic_id_to_test = input("Enter IC name/number to test> ")
    matching_ics = [x for x in ics if re.match(x.properties['NAME'], ic_id_to_test)]
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
        print("")
        selected = input("   >>> ")
        ic_to_test = match[int(selected)]
    else:
        ic_to_test = matching_ics[0]

    iterations = input("Iterations (1)> ")
    if iterations == "":
        iterations = 1
    else:
        iterations = int(iterations)

    ic = ic_to_test
    print("Testing IC [{0}]".format(ic_to_test))
    print("")
    r.set_led_ready()
    print("Waiting for button press...")
    r.wait_for_press()
    r.set_led_ready(False)

    for pin in ic.pins.keys():
        zifname = ic.get_zif_padname(pin)
        if ic.pins[pin][0] == 'I':
            print("Pin {0} ({1}) set to INPUT".format(pin, zifname))
            r.set_pin(zifname, False)
        elif ic.pins[pin][0] == 'O':
            print("Pin {0} ({1}) set to OUTPUT".format(pin, zifname))
            r.read_pin(zifname)
        elif ic.pins[pin][0] == '0':
            print("Pin {0} ({1}) set to STATIC LOW".format(pin, zifname))
            r.set_pin(zifname, False)
        elif ic.pins[pin][0] == '1':
            print("Pin {0} ({1}) set to STATIC HIGH".format(pin, zifname))
            r.set_pin(zifname, True)
        elif ic.pins[pin][0] == 'VCC':
            print("Pin {0} ({1}) set to EXTERNAL POWER".format(pin, zifname))
            r.read_pin(zifname)
        elif ic.pins[pin][0] == 'GND':
            print("Pin {0} ({1}) set to EXTERNAL GROUND".format(pin, zifname))
            r.read_pin(zifname)
        else:
            raise AssertionError("Don't understand {0}".format(ic.pins[pin][0]))

    # Sleep for 0.1 second to allow power supply to stabilize:
    time.sleep(0.1)

    ok = True
    print("Running tests")
    ready_led = False
    last_time = 0
    while iterations > 0:
        for test in ic.tests.keys():
            _set_pins = {}
            if iterations == 1:
                print(" * {} (Mapped: {})".format(test, ic.tests[test]))
            for template_row in ic.template:
                now_time = time.time()
                if (now_time - last_time > 0.3):
                    ready_led = not ready_led
                    r.set_led_ready(ready_led)
                    last_time = now_time
                if iterations == 1:
                    print("   * {}".format(template_row['Description']))

                # Set all IC inputs correctly (RPI outputs)
                for template_column in template_row:
                    if template_column != 'Description':
                        # Lookup actual pin in test case:
                        ic_pin_name = [x for x in ic.tests[test] if ic.tests[test][x] == template_column][0]
                        ic_pin_num  = [x for x in ic.pins if ic.pins[x][1] == ic_pin_name][0]
                        if ic.pins[ic_pin_num][0] == 'I':
                            if template_row[template_column]=='1':
                                value_to_set = True
                            elif template_row[template_column]=='0':
                                value_to_set = False
                            elif template_row[template_column]=='R':
                                value_to_set = random.choice([True, False])
                            r.set_pin(ic.get_zif_padname(ic_pin_num),
                                      value_to_set)
                            _set_pins[ic_pin_num] = value_to_set

                # Set possible left-overs: ("Variable" expansion)
                for template_column in template_row:
                    if template_column != 'Description':
                        # Lookup actual pin in test case:
                        ic_pin_name = [x for x in ic.tests[test] if ic.tests[test][x] == template_column][0]
                        ic_pin_num  = [x for x in ic.pins if ic.pins[x][1] == ic_pin_name][0]
                        if ic.pins[ic_pin_num][0] == 'I':
                            if template_row[template_column] not in ['1','0','R']:
                                # Might be a reference to the set value of an input:
                                lookup_input = [x for x in ic.pins if ic.pins[x][1] == template_row[template_column]][0]
                                if lookup_input:
                                    r.set_pin(ic.get_zif_padname(ic_pin_num),_set_pins[lookup_input])
                                else:
                                    raise AssertionError("Don't understand {0}".format(template_row[template_column]))

                # Validate all IC outputs correctly (RPI inputs)
                for template_column in template_row:
                    if template_column != 'Description':
                        # Lookup actual pin in test case:
                        ic_pin_name = [x for x in ic.tests[test] if ic.tests[test][x] == template_column][0]
                        ic_pin_num  = [x for x in ic.pins if ic.pins[x][1] == ic_pin_name][0]
                        if ic.pins[ic_pin_num][0] == 'O' and template_row[template_column]!='x':
                            expect = (True if template_row[template_column]=='1' else False)
                            if r.read_pin(ic.get_zif_padname(ic_pin_num)) != expect:
                                print( "       ! Incorrect result (Expected pin {} to be {})!".format(ic_pin_num, expect))
                                ok = False
            if iterations == 1:
                print("")
        if iterations == 1:
            print("")
        iterations = iterations - 1

    r.set_led_ready(False)
    r.zero_all_pins()
    r.set_led_ok(ok)
    r.set_led_fail(not ok)
    time.sleep(2)
    r.zero_all_pins()