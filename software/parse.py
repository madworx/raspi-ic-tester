#!/usr/bin/env python

import re

def parse_file(fname):
    state = ""
    sections = {}
    with open(fname, 'r') as content_file:
        content = content_file.read()
        lines = re.split( r'\n', content)
        for line in lines:
            if state == 'PARSE_TABLE':
                if re.match(r'^[|]', line):
                    state = 'PARSE_TABLE_DATA'
                    rows = []
                    headers = [] #map(lambda x: x.strip(" |"), filter( lambda x: x, line.split("| ")))
                    for col in line.split("| "):
                        headers.append(col.strip(" |"))
                    headers = headers[1:]
                else:
                    #print("Ignoring noise [{}]".format(line))
                    continue
            elif state == 'PARSE_TABLE_DATA':
                if re.match(r'^[|]', line):
                    if not re.match(r'^[|]-',line):
                        row = []
                        for col in line.split("| "):
                            row.append(col.strip(" |"))
                        row = row[1:]
                        #row = map(str.strip, re.findall(r'[|]\s+([^|]+)',line))
                        rows.append(dict(zip(headers,row)))
                else:
                    state = ''
                    sections[last_section] = rows
                    #print(rows)
            else:
                m = re.match( r'^#\s*([^#]+)', line)
                if m:
                    last_section = m.group(1)
                    state = 'PARSE_TABLE'
                else:
                    print("Could not grok [{}]".format(line))
        return sections
#            print "[{0}]".format(line)

class IC():
    def __init__(self, icdata):
        self.properties = {}
        self.pins = {}
        self.tests = {}
        #print(icdata['General'])
        for icprop in icdata['General']:
            if 'Value' in icprop:
                self.properties[icprop['Property']] = icprop['Value']
        for pins in icdata['Pin definitions']:
            if 'Pin' in pins:
                self.pins[pins['Pin']] = []
                self.pins[pins['Pin']].append( pins['Direction'] )
                self.pins[pins['Pin']].append( pins['Name'] )
        self.template = icdata['Template']
        for test in list(filter(lambda sect: re.match(r'^Test .+',sect),icdata.keys())):
            self.tests[test] = {}
            for testline in icdata[test]:
                if 'Value' in testline:
                    self.tests[test][testline['Pin']] = testline['Value']
        if not self.tests:
            # Generate implicit test from template:
            self.tests['Test template'] = {}
            for tpl in self.template[0]:
                if tpl != 'Description':
                    self.tests['Test template'][tpl] = tpl
    def __repr__(self):
        return self.properties['NAME']

    def get_zif_padname(self,pin):
        max_pin = max([int(x) for x in self.pins.keys()])
        assert max_pin % 2 == 0
        return "ZIF{0:02d}".format(40-(max_pin-int(pin)) if int(pin)>max_pin/2 else int(pin))
