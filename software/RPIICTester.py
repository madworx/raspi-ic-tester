# pylint: disable=invalid-name
"""Raspberry PI IC Tester.
Repository: https://github.com/madworx/raspi-ic-tester
"""

import csv
import re
import time

import adafruit_mcp230xx
import board
import busio
import digitalio

class RPIICTester(object):
    """Main class for the Raspiberry PI IC Tester.
    Relies on the 'expander-netlist.csv' file to figure out which
    pins are connected to which pads.
    """
    def __init__(self):
        self._i2c = busio.I2C(board.SCL, board.SDA)
        self._mcps = {}
        self._pins = {}
        self._load_expander_netlist()

    def _load_expander_netlist(self):
        with open('expander-netlist.csv', 'r') as csvfile:
            mapreader = csv.reader(csvfile, delimiter=';')
            for row in mapreader:
                if len(row) == 3:
                    if row[0] not in self._mcps:
                        self._mcps[row[0]] = adafruit_mcp230xx.MCP23017(
                            self._i2c, address=int(row[0], base=16))
                    self._pins[row[2]] = self._mcps[row[0]].get_pin(
                        self._decode_padname_to_pin(row[1]))
                elif len(row) == 1 and row[0][0] == '#':
                    pass
                else:
                    raise AssertionError("Unable to parse row from netlist file.")

    @staticmethod
    def _decode_padname_to_pin(padname):
        matches = re.match(r'^GP([AB])([0-9])$', padname)
        if matches:
            return (ord(matches.group(1))-65)*8 + int(matches.group(2))
        else:
            raise AssertionError("Could not grok padname [{0}]".format(padname))

    def _get_pin(self, name):
        return self._pins[name]

    def zero_all_pins(self):
        """Put all pins into input mode with no pull-up."""
        for pinname in self._pins:
            pin = self._get_pin(pinname)
            pin.direction = digitalio.Direction.INPUT
            pin.pull = None

    def read_pin(self, name):
        """Configure the given pin (e.g. "ZIF03") as an input pin,
        and read the value from it."""
        pin = self._get_pin(name)
        pin.direction = digitalio.Direction.INPUT
        return pin.value

    def set_pin(self, name, value=True):
        """Configure the given pin (e.g. "ZIF24") as an output pin,
        and set it to the specified value."""
        pin = self._get_pin(name)
        pin.direction = digitalio.Direction.OUTPUT
        pin.value = value

    def set_led_ok(self, value=True):
        """Set the "OK" LED"""
        self.set_pin('LED_OK', value)

    def set_led_fail(self, value=True):
        """Set the "FAIL" LED"""
        self.set_pin('LED_FAIL', value)

    def set_led_ready(self, value=True):
        """Set the "READY" LED"""
        self.set_pin('LED_RDY', value)

    def wait_for_press(self):
        """Wait until the "Press to test" button has been pressed"""
        self._get_pin('SW_TEST').pull = digitalio.Pull.UP
        while self.read_pin('SW_TEST'):
            time.sleep(0.05)