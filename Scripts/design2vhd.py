#! /usr/bin/env python3
#
# design2vhd.py
#       Script to convert a gEDA hierarchical design to VHDL code.
#
# https://lepton-eda.github.io/lepton-manual.html/gEDA-file-format.html
#
import os
import sys
import argparse
import re
                                                                     # constants
INDENT = 2 * ' '
                                                               # script location

script_location = os.path.dirname(os.path.realpath(sys.argv[0]))

# ==============================================================================
# command line arguments
#
                                                             # specify arguments
parser = argparse.ArgumentParser(
  description='Convert a gEDA symbol to a VHDL entity'
)
                                                                    # input file
parser.add_argument('input_file')
                                                                    # gafrc file
parser.add_argument(
    '-g', '--gafrc', default = os.sep.join([script_location, '..', 'gafrc']),
    help = 'gafrc (directory mappings) file'
)
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

top_architecture_file_spec = parser_arguments.input_file
gafrc_file_spec = parser_arguments.gafrc
VHDL_directory = parser_arguments.directory
scratch_directory = parser_arguments.scratch
verbose = parser_arguments.verbose

VHDL_library = parser_arguments.library
vhdl_file_path = VHDL_directory

top_symbol_file_spec = top_architecture_file_spec.replace(
    'Schematics', 'Symbols'
)
top_symbol_file_spec = '-'.join(top_symbol_file_spec.split('-')[:-1]) + '.sym'
                                                               # validity checks
if not os.path.isfile(top_architecture_file_spec) :
    print("schematics file %s not found" % top_architecture_file_spec)
    quit()

if not os.path.isfile(top_symbol_file_spec) :
    print("symbol file %s not found" % top_symbol_file_spec)
    quit()

if not os.path.isdir(scratch_directory) :
    print("scratch directory %s not found" % scratch_directory)
    quit()

# ==============================================================================
# functions
#
# ------------------------------------------------------------------------------
# find symbol and component paths
#
def find_paths():
                                                                    # parse file
    symbol_paths = []
    schematics_paths = []
    definitions = []
    end_of_file = False
    gafrc_file = open(gafrc_file_spec, 'r')
    while not end_of_file :
                                                           # read and strip line
        line = gafrc_file.readline()
        if not line :
            end_of_file = True
        comment_index = line.find(';')
        if comment_index >= 0 :
            line = line[:comment_index]
        line = line.lstrip(' ')
        line = line.rstrip(" \r\n")
        if (line.startswith('(')) and line.endswith(')') :
            line = line[1:-1]
        else :
            line = ''
        if line :
                                                             # apply definitions
            for definition in definitions :
                line = re.sub(definition[0], definition[1], line)
                                                              # find definitions
            if line.startswith('define ') :
                definition = line.split(' ', 3)[1:]
                if verbose :
                    print(INDENT + "%s = %s" % (definition[0], definition[1]))
                definitions.append(definition)
                                                                   # build paths
            match_list = re.search('\(build-path .*\)', line)
            while match_list :
                sub_target = '\\' + match_list.group()[:-1] + '\\)'
                path_to_build = \
                    match_list.group().lstrip('(').rstrip(')').split(' ')[1:]
                sub_replacement = os.sep.join(path_to_build)
                sub_replacement = sub_replacement.replace('"', '')
                line = re.sub(sub_target, sub_replacement, line)
                match_list = re.search('\(build-path .*\)', line)
                                                           # update symbol paths
            if line.startswith('component-library-search ') :
                path = line.split(' ')[1]
                if verbose :
                    print(INDENT + "symbols in %s" % path)
                symbol_paths.append(path)
                                                        # update component paths
            if line.startswith('source-library ') :
                path = line.split(' ')[1]
                if verbose :
                    print(INDENT + "schematics in %s" % path)
                schematics_paths.append(path)
    gafrc_file.close()

    return(symbol_paths, schematics_paths)

# ------------------------------------------------------------------------------
# find components in a schematic
#
def find_components(schematics_file_spec):
                                                                # validity check
    if not os.path.isfile(schematics_file_spec) :
        print("schematics file %s not found" % schematics_file_spec)
        quit()
    if verbose :
        print(INDENT + schematics_file_spec)
                                                                    # parse file
    components = []
    search_for_component_info = False
    line = ' '
    schematics_file = open(schematics_file_spec, 'r')
    while line :
        line = schematics_file.readline().rstrip("\r\n")
        if search_for_component_info:
            if line.startswith('source=') :
                component_source = line.split('=')[-1]
                if verbose :
                    print(3*INDENT + component_source)
            elif line.startswith('}') :
                if component_source :
                    components.append(component_symbol)
                    components.append(component_source)
                search_for_component_info = False
        elif line.startswith('C ') :
            component_symbol = line.split(' ')[-1]
            component_source = ''
            if verbose :
                print(2*INDENT + component_symbol)
            search_for_component_info = True
    schematics_file.close()

    return(components)

# ==============================================================================
# main script
#
print("Converting %s to VHDL" % top_architecture_file_spec)

# ------------------------------------------------------------------------------
                                                                    # file paths
if not os.path.isfile(gafrc_file_spec) :
    print("paths file %s not found" % gafrc_file_spec)
    quit()
if verbose :
    print("\nreading %s" % gafrc_file_spec)
(symbol_paths, schematics_paths) = find_paths()

# ------------------------------------------------------------------------------
                                                                   # parse files
if verbose :
    print("\nbuilding component list")
to_parse = [top_architecture_file_spec]
symbols_to_convert = [os.path.realpath(top_symbol_file_spec)]
schematics_to_convert = [os.path.realpath(top_architecture_file_spec)]
while to_parse :
                                                               # parse component
    components = find_components(to_parse[0])
    for component in components :
                                                           # update symbols list
        if component.endswith('.sym') :
            symbol_file_spec = ''
            for symbol_path in symbol_paths :
                test_spec = os.sep.join([symbol_path, component])
                if os.path.isfile(test_spec) :
                    symbol_file_spec = test_spec
            if symbol_file_spec :
                symbols_to_convert.append(symbol_file_spec)
            else :
                print("symbol file %s not found" % component)
                quit()
                                                        # update schematics list
        if component.endswith('.sch') :
            schematic_file_spec = ''
            for schematics_path in schematics_paths :
                test_spec = os.sep.join([schematics_path, component])
                if os.path.isfile(test_spec) :
                    schematic_file_spec = test_spec
            if schematic_file_spec :
                schematics_to_convert.append(schematic_file_spec)
                to_parse.append(schematic_file_spec)
            else :
                print("schematics file %s not found" % component)
                quit()

    to_parse.pop(0)

# ------------------------------------------------------------------------------
                                                               # convert symbols
if verbose :
    print("\nconverting symbols")
command = os.sep.join([script_location, 'sym2vhd.py'])
if VHDL_library :
    command = command + ' -l ' + VHDL_library
if vhdl_file_path :
    command = command + ' -d ' + vhdl_file_path
for symbol in symbols_to_convert :
    if verbose :
        print(INDENT + symbol)
    os.system("%s %s > /dev/null" % (command, symbol))

# ------------------------------------------------------------------------------
                                                            # convert schematics
if verbose :
    print("\nconverting schematics")
command = os.sep.join([script_location, 'sch2vhd.py'])
if VHDL_library :
    command = command + ' -l ' + VHDL_library
if vhdl_file_path :
    command = command + ' -d ' + vhdl_file_path
for schematics in schematics_to_convert :
    if verbose :
        print(INDENT + schematics)
    os.system("%s %s > /dev/null" % (command, schematics))
