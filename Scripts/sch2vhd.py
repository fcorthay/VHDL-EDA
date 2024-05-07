#! /usr/bin/env python3
#
# sch2vhd.py
#       Script to convert gEDA schematics to their VHDL architecture equivalent.
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
                                                             # scratch directory
parser.add_argument(
    '-s', '--scratch', default='/tmp',
    help = 'VHDL files directory'
)
                                                                # verbose output
parser.add_argument(
    '-v', '--verbose', action='store_true',
    help = 'Verbose display'
)
                                                             # process arguments
parser_arguments = parser.parse_args()

schematics_file_spec = parser_arguments.input_file
VHDL_directory = parser_arguments.directory
scratch_directory = parser_arguments.scratch
verbose = parser_arguments.verbose

schematics_file_path = os.path.dirname(schematics_file_spec)
if VHDL_directory :
    vhdl_file_path = VHDL_directory
else :
    path_list = schematics_file_path.split(os.sep)
    path_list[-1] = 'Description'
    vhdl_file_path = os.sep.join(path_list)
symbol_name_parts = \
    os.path.basename(schematics_file_spec).rstrip('.sch').split('-')
library_name = symbol_name_parts.pop(0)
architecture_name = symbol_name_parts.pop()
symbol_name = '-'.join(symbol_name_parts)
vhdl_file_spec = os.path.join(vhdl_file_path, "%s-%s-%s.vhd" %
    (library_name, symbol_name, architecture_name)
)
                                                               # validity checks
if not os.path.isfile(schematics_file_spec) :
    print("symbol file %s not found" % schematics_file_spec)
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
print("Converting %s to %s" % (schematics_file_spec, vhdl_file_spec))
                                                                    # parse file
if verbose :
    print("\nParsing schematics file")
done = False
processing_component_start = False
processing_component = False
processing_text = False
components = []
component_location = [0, 0]
schematics_file = open(schematics_file_spec, 'r')
while not done :
    line = schematics_file.readline().rstrip("\r\n")
    if processing_component_start :
        if line.startswith('{') :
            processing_component = True
        processing_component_start = False

    if processing_component :
        value = '='.join((line + '= ').split('=')[1:-1])
                                                               # component label
        if line.startswith('refdes') :
            component_label = value
            if verbose :
                print(2*INDENT + "label %s" % component_label)
                                                              # component source
        if line.startswith('source') :
            component_source = value
            if verbose :
                print(2*INDENT + "source %s" % component_source)
                                                            # component generics
        if line.startswith('generic') :
            component_generics.append(value)
            if verbose :
                print(2*INDENT + "generic %s" % value)
                                                       # component wrap together
        if line.startswith('}') :
            components.append({
                'name' : component_name,
                'label' : component_label,
                'source' : component_source,
                'generics' : component_generics
            })
            processing_component = False
    elif processing_text :
                                                                      # generics
        if line.startswith('generic') :
            (label, generic) = line.split('=', 1)
            generics.append(generic)
            if verbose :
                print(INDENT + 'generic : ' + generic)
        processing_text = False
    else :
                                                            # schematics element
        if line.startswith('C ') :
            component_info = line.split(' ')
            component_location[0] = int(component_info[1])
            component_location[1] = int(component_info[2])
            component_name = component_info[-1]
            component_label = ''
            component_generics = []
            if verbose :
                print(INDENT + "at [%d, %d] : %s" % (
                    component_location[0], component_location[0], component_name
                ))
            processing_component_start = True
        if line.startswith('T ') :
            processing_text = True
    if not line :
        done = True
schematics_file.close()
                                                            # write architecture
# if verbose :
#     print("\nWriting entity")
# vhdl_file = open(vhdl_file_spec, 'w')
#                                                                   # entity start
# vhdl_file.write("entity %s is\n" % symbol_name)
#                                                                       # generics
# if generics :
#     separator = ';'
#     if verbose :
#         print(INDENT + "generics :")
#     vhdl_file.write(INDENT + "generic (\n")
#     for index in range(len(generics)) :
#         generic = generics[index]
#         if index == len(generics)-1 :
#             separator = ''
#         if verbose :
#             generic_name = generic.split(':')[0]
#             print(2*INDENT + generic_name)
#         vhdl_file.write(2*INDENT + generic + separator + "\n")
#     vhdl_file.write(INDENT + ");\n")
#                                                                          # ports
# if ports :
#     separator = ';'
#     if verbose :
#         print(INDENT + "ports :")
#     vhdl_file.write(INDENT + "port (\n")
#     for index in range(len(ports)) :
#         port_dictionary = ports[index]
#         if index == len(ports)-1 :
#             separator = ''
#         if verbose :
#             print(2*INDENT + port_dictionary['name'])
#         vhdl_file.write(2*INDENT + "%s : %s %s%s%s\n" % (
#             port_dictionary['name'],
#             port_dictionary['direction'],
#             port_dictionary['type'],
#             port_dictionary['range'],
#             separator
#         ))
#     vhdl_file.write(INDENT + ");\n")
#                                                                     # entity end
# vhdl_file.write("end %s;\n" % symbol_name)
# vhdl_file.close()
#                                                                   # write entity
# if ports :
#     if verbose :
#         print("\nWriting port locations to %s" % port_locations_file_spec)
#     port_locations_file = open(port_locations_file_spec, 'w')
#     for port in ports :
#         port_locations_file.write("%s [%s, %s]\n" % (
#             port['name'],
#             port['location'][0],
#             port['location'][1]
#         ))
#     port_locations_file.close()
