*** Settings ***
Library        KiCadLibrary    pcb=../ic-tester.kicad_pcb    schema=../ic-tester.sch
Library        Collections
Library        OperatingSystem
Suite Setup    Setup

*** Variables ***
${OUTPUT_EXPANDER_NETLIST}      ../software/expander-netlist.csv

*** Test Cases ***
Extract expander netlist
    Create File       ${OUTPUT_EXPANDER_NETLIST}
    Append To File    ${OUTPUT_EXPANDER_NETLIST}    \# This is an auto-generated file - DO NOT EDIT!\n
    ${mods}=        Find Modules     value=MCP23017.*
    FOR    ${mod}   IN               @{mods}
    \      ${exp_addr}=              Get Expander I2C Address                     ${mod}
    \      ${mapped_pins}=           Get Expander GPIO Pins Mapped To Netnames    ${mod}
    \      Write Pins to CSV File    ${OUTPUT_EXPANDER_NETLIST}                   ${exp_addr}    ${mapped_pins}

*** Keywords ***
Get Expander I2C Address
    [Arguments]       ${mod}
    [Documentation]   Return the (hex) address of the given module.
    ${netnames}=      Get Pad Netnames For Pins                 ${mod}           A0    A1    A2
    ${netnames}=      Replace Known Netnames With Logic Level   @{netnames}
    ${address}=       Evaluate    0x20 + (${netnames[0]}<<0) + (${netnames[1]}<<1) + (${netnames[2]}<<2)
    ${address}=       Convert To Hex    ${address}    prefix=0x
    [Return]          ${address}

Get Expander GPIO Pins Mapped To Netnames
    [Arguments]         ${module}
    ${pad_netnames}=    Get Pad Netnames For Module    ${module}
    ${cpins}=           Get Component Pins For Module  ${module}    GP[AB][0-7]
    ${mupp}=            Get Pins Mapped To Netnames    ${cpins}     ${pad_netnames}
    [Return]            ${mupp}

Get Pins Mapped To Netnames
    [Arguments]       ${cpins}    ${pad_netnames}
    ${out_pins}=      Create Dictionary
    FOR    ${cpin}     IN    @{cpins}
    \      Set To Dictionary    ${out_pins}    ${cpins["${cpin}"]['name']}  ${pad_netnames["${cpin}"]}
    [Return]    ${out_pins}

Write pins to CSV file
    [Arguments]    ${file}   ${address}    ${pins}
    FOR    ${pin}    IN    @{pins}
    \      Append To File    ${file}    ${address};${pin};${pins["${pin}"]}\n

Setup
    Add Component Library Path    ../.libs
    # Fixme: Why didn't absolute path work?
    # Fixme 2: I shouldn't need to - I'm loading schema!
    Load Component Library        MCP23017-E_SP
