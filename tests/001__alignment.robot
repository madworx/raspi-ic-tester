*** Settings ***
Library    KiCadLibrary    pcb=../ic-tester.kicad_pcb    schema=../ic-tester.sch

*** Test Cases ***
Edge cuts should be on grid
    Edge Cuts Should Be On Grid    25 mil

Module pads should be on grid
    Module Pads Should Be On Grid    25 mil    reference=.*$
