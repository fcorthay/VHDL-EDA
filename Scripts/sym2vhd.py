#! /usr/bin/env python3
#
# sym2vhd.py
#       Script to convert gEDA symbols to their VHDL entity equivalent.
#
# https://lepton-eda.github.io/lepton-manual.html/gEDA-file-format.html
#
import os
import argparse
import re
                                                                     # constants
INDENT = 2 * ' '

# ==============================================================================
# command line arguments
#
                                                             # specify arguments
parser = argparse.ArgumentParser(
  description='Convert a gEDA symbol to a VHDL entity'
)
                                                                    # input file
parser.add_argument('input_file')
                                                                  # VHDL library
parser.add_argument(
    '-l', '--library',
    help = 'VHDL library'
)
                                                                # VHDL directory
parser.add_argument(
    '-d', '--directory',
    help = 'VHDL files directory'
)
                                                             # scratch directory
parser.add_argument(
    '-s', '--scratch', default='/tmp',
    help = 'scratch directory'
)
                                                                # verbose output
parser.add_argument(
    '-v', '--verbose', action='store_true',
    help = 'Verbose display'
)
                                                             # process arguments
parser_arguments = parser.parse_args()

symbol_file_spec = parser_arguments.input_file
VHDL_library = parser_arguments.library
VHDL_directory = parser_arguments.directory
scratch_directory = parser_arguments.scratch
verbose = parser_arguments.verbose

symbol_name = os.path.basename(symbol_file_spec).rstrip('.sym')
if not VHDL_library :
    VHDL_library = symbol_name.split('-', 1)[0]
symbol_file_path = os.path.dirname(symbol_file_spec)
if VHDL_directory :
    vhdl_file_path = VHDL_directory
else :
    path_list = symbol_file_path.split(os.sep)
    path_list[-1] = 'Description'
    vhdl_file_path = os.sep.join(path_list)
vhdl_file_spec = os.path.join(vhdl_file_path, symbol_name + '.vhd')
port_locations_file_spec = os.path.join(
    scratch_directory, symbol_name + '-port_locations.txt'
)
                                                               # validity checks
if not os.path.isfile(symbol_file_spec) :
    print("symbol file %s not found" % symbol_file_spec)
    quit()

if not os.path.isdir(vhdl_file_path) :
    print("VHDL directory %s not found" % vhdl_file_path)
    quit()

if not os.path.isdir(scratch_directory) :
    print("scratch directory %s not found" % scratch_directory)
    quit()

# ==============================================================================
# main script
#
print("Converting %s to %s" % (symbol_file_spec, vhdl_file_spec))

# ------------------------------------------------------------------------------
                                                                    # parse file
if verbose :
    print("\nParsing symbol file")
done = False
processing_port = False
processing_text = False
generics = []
ports = []
port_location = [0, 0]
symbol_file = open(symbol_file_spec, 'r')
while not done :
                                                                # read next line
    line = symbol_file.readline().rstrip("\r\n")
    # print(10*' ' + line)
                                                                  # process port
    if processing_port :
        value = (line + '= ').split('=')[1]
                                                                     # port name
        if line.startswith('pinlabel') :
            port_name = value
            if verbose :
                print(2*INDENT + "port %s" % port_name)
                                                                     # port type
        if line.startswith('porttype') :
            port_type = value
            if verbose :
                print(2*INDENT + "type %s" % port_type)
                                                                    # port range
        if line.startswith('portrange') :
            port_range = value
            if verbose :
                print(2*INDENT + "range %s" % port_range)
                                                                # port direction
        if line.startswith('portdirection') :
            port_direction = value
            if verbose :
                print(2*INDENT + "direction %s" % port_direction)
        if line.startswith('}') :
            ports.append({
                'name' : port_name,
                'type' : port_type,
                'range' : port_range,
                'direction' : port_direction,
                'location' : port_location.copy()
            })
            processing_port = False
                                                                  # process text
    elif processing_text :
                                                                      # generics
        if line.startswith('generic') :
            (label, generic) = line.split('=', 1)
            if verbose :
                print(INDENT + 'generic :')
                print(2*INDENT + generic)
            generics.append(generic)
        processing_text = False
    else :
                                                            # schematics element
        if line.startswith('P ') :
            port_location_string = line.split(' ')[1:3]
            for index in range(len(port_location_string)) :
                port_location[index] = int(port_location_string[index])
            if verbose :
                print(
                    INDENT +
                    "at [%d, %d] :" % (port_location[0], port_location[0])
                )
            port_name = ''
            port_type = 'std_ulogic'
            port_range = ''
            port_direction = 'in'
            processing_port = True
                                                                          # text
        if line.startswith('T ') :
            processing_text = True
    if not line :
        done = True
symbol_file.close()

# ------------------------------------------------------------------------------
                                                                  # write entity
if verbose :
    print("\nWriting entity")
vhdl_file = open(vhdl_file_spec, 'w')
                                                                     # libraries
vhdl_file.write("library %s;\n" % VHDL_library)
use_1164 = False
use_numeric_std = False
for port in ports :
    port_type = port['type'].lower()
    if port_type.startswith('std_logic') :
        use_1164 = True
    if port_type.startswith('std_ulogic') :
        use_1164 = True
    if port_type == 'unsigned' :
        use_numeric_std = True
    if port_type == 'signed' :
        use_numeric_std = True
if use_1164 or use_numeric_std :
    vhdl_file.write("library ieee;\n")
if use_1164 :
    vhdl_file.write(INDENT + "use ieee.std_logic_1164.all;\n")
if use_numeric_std :
    vhdl_file.write(INDENT + "use ieee.numeric_std.all;\n")
vhdl_file.write("\n")
                                                                  # entity start
vhdl_symbol_name = symbol_name.replace('-', '_')
vhdl_file.write("entity %s is\n" % vhdl_symbol_name)
                                                                      # generics
if generics :
    separator = ';'
    if verbose :
        print(INDENT + "generics :")
    vhdl_file.write(INDENT + "generic (\n")
    for index in range(len(generics)) :
        generic = generics[index]
        if index == len(generics)-1 :
            separator = ''
        if verbose :
            generic_name = generic.split(':')[0]
            print(2*INDENT + generic_name)
        vhdl_file.write(2*INDENT + generic + separator + "\n")
    vhdl_file.write(INDENT + ");\n")
                                                                         # ports
if ports :
    separator = ';'
    if verbose :
        print(INDENT + "ports :")
    vhdl_file.write(INDENT + "port (\n")
    for index in range(len(ports)) :
        port_dictionary = ports[index]
        if index == len(ports)-1 :
            separator = ''
        if verbose :
            print(2*INDENT + port_dictionary['name'])
        vhdl_file.write(2*INDENT + "%s : %s %s%s%s\n" % (
            port_dictionary['name'],
            port_dictionary['direction'],
            port_dictionary['type'],
            port_dictionary['range'],
            separator
        ))
    vhdl_file.write(INDENT + ");\n")
                                                                    # entity end
vhdl_file.write("end %s;\n" % vhdl_symbol_name)
vhdl_file.close()
                                                                  # write entity
if ports :
    if verbose :
        print("\nWriting port locations to %s" % port_locations_file_spec)
    port_locations_file = open(port_locations_file_spec, 'w')
    for port in ports :
        if verbose :
            print(INDENT + port['name'])
        port_locations_file.write("%s %s [%s, %s]\n" % (
            port['name'],
            port['type'] + port['range'],
            port['location'][0],
            port['location'][1]
        ))
    port_locations_file.close()
