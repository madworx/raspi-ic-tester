# pylint: disable=invalid-name
"""Parser of markdown-style IC defintion files"""
from __future__ import print_function
import re

def parse_file(fname):
    """Attempt to parse the given file as a
    markdown IC-definition file."""
    state = None
    sections = {}
    with open(fname, 'r') as content_file:
        content = content_file.read()
        lines = re.split(r'\n', content)
        for line in lines:
            if state is None:
                matches = re.match(r'^##?\s*([^#]+)', line)
                if matches:
                    last_section = matches.group(1)
                    state = 'PARSE_TABLE'
                else:
                    print("Could not grok [{}]".format(line))
            elif state == 'PARSE_TABLE':
                if re.match(r'^[|]', line):
                    state = 'PARSE_TABLE_DATA'
                    table_rows = []
                    table_headers = []
                    for col in line.split("| "):
                        table_headers.append(col.strip(" |"))
                    table_headers = table_headers[1:]
                #else:
                    #print("Ignoring noise [{}]".format(line))
            elif state == 'PARSE_TABLE_DATA':
                if re.match(r'^[|]', line):
                    if not re.match(r'^[|]-', line):
                        row = []
                        for col in line.split("| "):
                            row.append(col.strip(" |"))
                        row = row[1:]
                        table_rows.append(dict(zip(table_headers, row)))
                else:
                    state = None
                    sections[last_section] = table_rows
        return sections

class IC(object):
    """Represents a parsed IC definition."""
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
                self.pins[pins['Pin']].append(pins['Direction'])
                self.pins[pins['Pin']].append(pins['Name'])
        self.template = icdata['Template']
        tests = [x for x in icdata.keys() if re.match(r'^Test .+', x)]
        for test in tests:
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

    def get_zif_padname(self, pin):
        """Return the ZIF padname (e.g. "ZIF14") for the given
        pin number for this IC."""
        max_pin = max([int(x) for x in self.pins])
        assert max_pin % 2 == 0
        return "ZIF{0:02d}".format(40-(max_pin-int(pin))
                                   if int(pin) > max_pin/2 else int(pin))
