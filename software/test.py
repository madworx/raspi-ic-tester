#!/usr/bin/python3

import mistune

# Tanke: Kan vi pulla informationen från KiCads libraries?
# https://mil.ufl.edu/3701/pinouts/7400.html
# http://www.kingswood-consulting.co.uk/giicm/

import adafruit_mcp230xx
import board
import busio
import digitalio

i2c = busio.I2C(board.SCL, board.SDA)
mcp = adafruit_mcp230xx.MCP23017(i2c)

pin0 = mcp.get_pin(0)
pin0.direction = Direction.OUTPUT
pin0.value = True  # GPIO0 / GPIOA0 to high logic level
pin0.value = False # GPIO0 / GPIOA0 to low logic level

pin1 = mcp.get_pin(1)
pin1.direction = digitalio.Direction.INPUT

# How to handle if we don't want it to pull up? Pull-down isn't supported in the hardware.
pin1.pull = digitalio.Pull.UP
