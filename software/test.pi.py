#!/usr/bin/python3

import time

import csv
import sys
import adafruit_mcp230xx
import board
import busio
import digitalio
import re
import parse


i2c = busio.I2C(board.SCL, board.SDA)

class RPIICTester(object):
  def __init__(self):
    self._mcps = {}
    self._pins = {}
    self._load_expander_netlist()

  def _load_expander_netlist(self):
    with open('expander-netlist.csv', 'r') as csvfile:
        mapreader = csv.reader(csvfile,delimiter=';')
        for row in mapreader:
          if len(row) == 3:
            if row[0] not in self._mcps:
              self._mcps[row[0]] = adafruit_mcp230xx.MCP23017(i2c, address=int(row[0], base=16))
            self._pins[row[2]] = self._mcps[row[0]].get_pin(self._decode_padname_to_pin(row[1]))

  def _decode_padname_to_pin(self,padname):
    m = re.match(r'^GP([AB])([0-9])$',padname)
    if m:
      return (ord(m.group(1))-65)*8 + int(m.group(2))
    else:
      raise AssertionError("Could not grok padname [{0}]".format(padname))

  def _get_pin(self,name):
    return self._pins[name]

  def read_pin(self,name):
    pin = self._get_pin(name)
    pin.direction = digitalio.Direction.INPUT
    pin.pull = digitalio.Pull.UP
    return pin.value

  def set_pin(self,name,value=True):
    pin = self._get_pin(name)
    pin.direction = digitalio.Direction.OUTPUT
    pin.value = value

  def set_led_ok(self,value=True):
    self.set_pin('LED_OK',value)

  def set_led_fail(self,value=True):
    self.set_pin('LED_FAIL',value)

  def set_led_ready(self,value=True):
    self.set_pin('LED_RDY',value)

  def wait_for_press(self):
    while self.read_pin('SW_TEST') == True:
      time.sleep(0.05)

r = RPIICTester()

ic = parse.IC(parse.parse_file('74ls00.md'))
#print("Properties")
#print(ic.properties)
#print("")
#print("Pins")
#print(ic.pins)
#print("")
#print("Template")
#print(ic.template)

r.set_led_ready()
print("Waiting for button press")
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
    else:
        raise AssertionError("Don't understand {0}".format(ic.pins[pin][0]))

ok = True
print("Tests")
for test in ic.tests.keys():
  print(" * {}".format(test))
  for template_row in ic.template:
    print("   * {} (Mapped: {})".format(template_row['Description'], ic.tests[test]))
    for template_column in template_row:
      if template_column != 'Description':
        # Lookup actual pin in test case:
        ic_pin_name = [x for x in ic.tests[test] if ic.tests[test][x] == template_column][0]
        ic_pin_num  = [x for x in ic.pins if ic.pins[x][1] == ic_pin_name][0]
        if ic.pins[ic_pin_num][0] == 'I':
          #print( "      Setting {} to {}".format(ic_pin_name, template_row[template_column]))
          r.set_pin(ic.get_zif_padname(ic_pin_num), True if template_row[template_column]=='1' else False)
    for template_column in template_row:
      if template_column != 'Description':
        # Lookup actual pin in test case:
        ic_pin_name = [x for x in ic.tests[test] if ic.tests[test][x] == template_column][0]
        ic_pin_num  = [x for x in ic.pins if ic.pins[x][1] == ic_pin_name][0]
        if ic.pins[ic_pin_num][0] == 'O':
          if r.read_pin(ic.get_zif_padname(ic_pin_num)) != (True if template_row[template_column]=='1' else False):
            print( "     ERROR!")
            ok = False
          #print( "      Reading {}: {} ({})".format(ic_pin_name, 
          #                                          r.read_pin(ic.get_zif_padname(ic_pin_num)),
          #                                          True if template_row[template_column]=='1' else False ))
  print("")
print("")

r.set_led_ok(ok)
r.set_led_fail(not ok)

sys.exit(1)
