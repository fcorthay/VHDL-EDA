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
                                                                # VHDL directory
parser.add_argument(
    '-d', '--directory',
    help = 'VHDL files directory'
)
                                                                # verbose output
parser.add_argument(
    '-v', '--verbose', action='store_true',
    help = 'Verbose display'
)
                                                             # process arguments
parser_arguments = parser.parse_args()

symbol_file_spec = parser_arguments.input_file
VHDL_directory = parser_arguments.directory
verbose = parser_arguments.verbose

symbol_file_path = os.path.dirname(symbol_file_spec)
if VHDL_directory :
    vhdl_file_path = VHDL_directory
else :
    path_list = symbol_file_path.split(os.sep)
    path_list[-1] = 'Description'
    vhdl_file_path = os.sep.join(path_list)
symbol_file_name = os.path.basename(symbol_file_spec).rstrip('.sym')
vhdl_file_spec = os.path.join(vhdl_file_path, symbol_file_name + '.vhd')

if not os.path.isfile(symbol_file_spec) :
    print("file %s not found" % symbol_file_spec)
    quit()

if not os.path.isdir(vhdl_file_path) :
    print("directory %s not found" % vhdl_file_path)
    quit()

# ==============================================================================
# main script
#
print("Converting %s to %s\n" % (symbol_file_spec, vhdl_file_spec))
                                                                    # parse file

done = False
processing_port = False
symbol_file = open(symbol_file_spec, 'r')
while not done :
    line = symbol_file.readline().rstrip("\r\n")
    if not processing_port :
        if line.startswith('P ') :
            port_location_text = line.split(' ')[1:3]
            port_location = []
            for location in port_location_text :
                port_location.append(int(location))
            if verbose :
                print("at [%d, %d] :" %(port_location[0], port_location[0]))
            port_name = ''
            port_type = 'std_ulogic'
            port_range = ''
            port_direction = 'in'
            processing_port = True
    else :
        value = (line + '= ').split('=')[1]
        if line.startswith('pinlabel') :
            port_name = value
            if verbose :
                print(INDENT + "port %s" % port_name)
        if line.startswith('porttype') :
            port_type = value
            if verbose :
                print(INDENT + "type %s" % port_type)
        if line.startswith('portrange') :
            port_range = value
            if verbose :
                print(INDENT + "range %s" % port_range)
        if line.startswith('portdirection') :
            port_direction = value
            if verbose :
                print(INDENT + "direction %s" % port_direction)
        if line.startswith('}') :
            processing_port = False
    if not line :
        done = True
symbol_file.close()