#!/usr/bin/python

import adafruit_mcp230xx
import board
import busio
import digitalio

class Raspberry_IC_Tester(object):
    def __init__(self):
        i2c = busio.I2C(board.SCL, board.SDA)
        self.ic1 = adafruit_mcp230xx.MCP23017(i2c, address=0x20)
        self.ic2 = adafruit_mcp230xx.MCP23017(i2c, address=0x21)
        self.ic3 = adafruit_mcp230xx.MCP23017(i2c, address=0x22)
