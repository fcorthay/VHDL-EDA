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

schematics_file_spec = parser_arguments.input_file
VHDL_library = parser_arguments.library
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
schematics_name_parts = \
    os.path.basename(schematics_file_spec).rstrip('.sch').split('-')
library_name = schematics_name_parts.pop(0)
architecture_name = schematics_name_parts.pop()
symbol_name = '-'.join(schematics_name_parts)
vhdl_file_spec = os.path.join(vhdl_file_path, "%s-%s-%s.vhd" %
    (library_name, symbol_name, architecture_name)
)
if not VHDL_library :
    VHDL_library = library_name
                                                               # validity checks
if not os.path.isfile(schematics_file_spec) :
    print("schematics file %s not found" % schematics_file_spec)
    quit()

if not os.path.isdir(vhdl_file_path) :
    print("VHDL directory %s not found" % vhdl_file_path)
    quit()

if not os.path.isdir(scratch_directory) :
    print("scratch directory %s not found" % scratch_directory)
    quit()

# ==============================================================================
# functions
#
# ------------------------------------------------------------------------------
# aggregate unnamed nets to named nets
#
def aggregate_one_unnamed_net(nets_labelled, nets_not_labelled):
    super_verbose = False
    found_item = []
    for net_labelled in nets_labelled :
        net_label = net_labelled[0]
        if super_verbose :
            print(INDENT + net_label)
        for segment in range(1, len(net_labelled)-1) :
            segment_start_x = net_labelled[segment][0]
            segment_start_y = net_labelled[segment][1]
            segment_end_x = net_labelled[segment+1][0]
            segment_end_y = net_labelled[segment+1][1]
                                                             # vertical segments
            if segment_start_x == segment_end_x :
                segment_x = segment_start_x
                if super_verbose :
                    print(2*INDENT + "vertical segment %d - [%d, %s]" % (
                        segment_x, segment_start_y, segment_end_y
                    ))
                y_min = min(segment_start_y, segment_end_y)
                y_max = max(segment_start_y, segment_end_y)
                for net in range(len(nets_not_labelled)) :
                    if not found_item :
                        net_start_x = nets_not_labelled[net][0][0]
                        net_end_x = nets_not_labelled[net][1][0]
                        if net_start_x != net_end_x :
                            net_y = nets_not_labelled[net][0][1]
                                                         # test start of segment
                            if net_start_x == segment_x :
                                if (net_y >= y_min) and (net_y <= y_max) :
                                    if verbose :
                                        if super_verbose :
                                            print(INDENT, end='')
                                        else :
                                            print(INDENT + "net %s" % net_label)
                                        print(
                                            2*INDENT +
                                            "aggreagting net %d at [%d, %d]" % (
                                                net, segment_x, net_y
                                            )
                                        )
                                    nets_not_labelled.pop(net)
                                    found_item = [
                                        net_label,
                                        [net_start_x, net_y],
                                        [net_end_x, net_y]
                                    ]
                                                           # test end of segment
                            if net_end_x == segment_x :
                                if (net_y >= y_min) and (net_y <= y_max) :
                                    if verbose :
                                        if super_verbose :
                                            print(INDENT, end='')
                                        else :
                                            print(INDENT + "net %s" % net_label)
                                        print(
                                            2*INDENT +
                                            "aggreagting net %d at [%d, %d]" % (
                                                net, segment_x, net_y
                                            )
                                        )
                                    nets_not_labelled.pop(net)
                                    found_item = [
                                        net_label,
                                        [net_start_x, net_y],
                                        [net_end_x, net_y]
                                    ]
                                                           # horizontal segments
            if segment_start_y == segment_end_y :
                if super_verbose :
                    print(2*INDENT + "horizontal segment %d - [%d, %s]" % (
                        segment_start_y, segment_start_x, segment_end_x
                    ))
                x_min = min(segment_start_x, segment_end_x)
                x_max = max(segment_start_x, segment_end_x)
                for net in range(len(nets_not_labelled)) :
                    if not found_item :
                        net_start_y = nets_not_labelled[net][0][1]
                        net_end_y = nets_not_labelled[net][1][1]
                        if net_start_y != net_end_y :
                            net_x = nets_not_labelled[net][0][0]
                                                         # test start of segment
                            if net_start_y == segment_start_y :
                                if (net_x >= x_min) and (net_x <= x_max) :
                                    if verbose :
                                        if super_verbose :
                                            print(INDENT, end='')
                                        else :
                                            print(INDENT + "net %s" % net_label)
                                        print(
                                            2*INDENT +
                                            "aggreagting net %d at [%d, %d]" % (
                                                net, net_x, net_start_y
                                            )
                                        )
                                    nets_not_labelled.pop(net)
                                    found_item = [
                                        net_label,
                                        [net_x, net_start_y],
                                        [net_x, net_end_y]
                                    ]
                                                           # test end of segment
                            if net_end_y == segment_start_y :
                                if (net_x >= x_min) and (net_x <= x_max) :
                                    if verbose :
                                        if super_verbose :
                                            print(INDENT, end='')
                                        else :
                                            print(INDENT + "net %s" % net_label)
                                        print(
                                            2*INDENT +
                                            "aggreagting net %d at [%d, %d]" % (
                                                net, net_x, net_start_y
                                            )
                                        )
                                    nets_not_labelled.pop(net)
                                    found_item = [
                                        net_label,
                                        [net_x, net_start_y],
                                        [net_x, net_end_y]
                                    ]
    if found_item :
        nets_labelled.append(found_item)
    return(found_item)

# ==============================================================================
# main script
#
print("Converting %s to %s" % (schematics_file_spec, vhdl_file_spec))

# ------------------------------------------------------------------------------
                                                                    # parse file
if verbose :
    print("\nParsing schematics file")
done = False
discard_next_read = False
processing_component_start = False
processing_component = False
processing_net_start = False
processing_net = False
processing_text = False
components = []
nets_not_labelled = []
nets_labelled = []
signals = []
component_location = [0, 0]
net_start = [0, 0]
net_end = [0, 0]
text_blocks = []

schematics_file = open(schematics_file_spec, 'r')
while not done :
                                                                # read next line
    if not discard_next_read :
        line = schematics_file.readline().rstrip("\r\n")
    else :
        discard_next_read = False
                                                         # pre-process component
    if processing_component_start :
        if line.startswith('{') :
            processing_component = True
        processing_component_start = False
                                                               # pre-process net
    elif processing_net_start :
        if line.startswith('{') :
            processing_net = True
        else :
            nets_not_labelled.append([net_start.copy(), net_end.copy()])
            if verbose :
                print(INDENT + "net")
                print(2*INDENT + "[%d, %d] - [%d, %d]" %
                    (net_start[0], net_start[1], net_end[0], net_end[1])
                )
        processing_net_start = False
                                                                     # component
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
                'generics' : component_generics,
                'location' : component_location.copy()
            })
            processing_component = False
                                                                           # net
    elif processing_net :
        value = line[line.find('=')+1:]
                                                                      # net name
        if line.startswith('netname') :
            net_name = value
            if verbose :
                print(INDENT + "net %s" % net_name)
                print(2*INDENT + "[%d, %d] - [%d, %d]" %
                    (net_start[0], net_start[1], net_end[0], net_end[1])
                )
                                                                      # net type
        if line.startswith('signaltype') :
            net_type = value
            if verbose :
                print(2*INDENT + net_type)
                                                                     # net range
        if line.startswith('signalrange') :
            net_range = value
            if verbose :
                print(2*INDENT + "(%s)" % net_range)
                                                             # net wrap together
        if line.startswith('}') :
            nets_labelled.append([net_name, net_start.copy(), net_end.copy()])
            signals.append([net_name, net_type, net_range])
            processing_net = False
                                                                          # text
    elif processing_text :
        if re.search('\A[A-Z]\s', line) or not line :
            text_block = text_block[:-1]
            text_blocks.append(text_block)
            if verbose :
                print(INDENT + "text")
                print(text_block)
            discard_next_read = True
            processing_text = False
        text_block = text_block + line + "\n"
    else :
                                                            # schematics element
        if line.startswith('C ') :
            component_info = line.split(' ')
            component_location[0] = int(component_info[1])
            component_location[1] = int(component_info[2])
            component_name = component_info[-1].rstrip('.sym')
            component_label = ''
            component_generics = []
            if verbose :
                print(INDENT + "at [%d, %d] : %s" % (
                    component_location[0], component_location[0], component_name
                ))
            processing_component_start = True
        elif line.startswith('N ') or line.startswith('U ') :
            net_info = line.split(' ')
            net_start[0] = int(net_info[1])
            net_start[1] = int(net_info[2])
            net_end[0] = int(net_info[3])
            net_end[1] = int(net_info[4])
            net_type = ''
            net_range = ''
            processing_net_start = True
        elif line.startswith('T ') :
            text_block = ''
            processing_text = True
    if not line :
        done = True

print(components)
# ------------------------------------------------------------------------------
                                                                # aggregate nets
if verbose :
    print("\nAggregating nets")
unlabelled_id = 0
done_unlabelled = False
while not done_unlabelled :
                                                       # aggregate labelled nets
    continue_search = True
    while continue_search :
        continue_search = aggregate_one_unnamed_net(
            nets_labelled, nets_not_labelled
        )
                                                    # label first unlabelled net
    if nets_not_labelled :
        nets_labelled.append([
            "net%d" % unlabelled_id,
            nets_not_labelled[0][0],
            nets_not_labelled[0][1]
        ])
        nets_not_labelled.pop(0)
        unlabelled_id = unlabelled_id + 1
    else :
        done_unlabelled = True

# ------------------------------------------------------------------------------
                                                            # connect components
if verbose :
    print("\nConnecting components")
port_connections = []
for component in components :
    component_name = component['name']
    component_location = component['location']
    if verbose :
        print(INDENT + component_name)
                                                 # read port locations from file
    port_locations_file_spec = os.sep.join([
        scratch_directory,component_name + "-port_locations.txt"
    ])
    if not os.path.isfile(port_locations_file_spec) :
        print("port location file %s not found" % port_locations_file_spec)
        quit()
    port_locations_file = open(port_locations_file_spec, 'r')
    locations = port_locations_file.read().replace("\r", "\n").split("\n")
    port_locations_file.close()
    for location in locations :
        location_trimmed = location.replace('[', '').replace(']', '')
        location_trimmed = location_trimmed.replace(',', '')
        location_list = location_trimmed.split(' ')
        if len(location_list) >= 4 :
            port_name = location_list[0]
            port_type = ' '.join(location_list[1:-2])
            port_coordinates = [
                component_location[0] + int(location_list[-2]),
                component_location[1] + int(location_list[-1])
            ]
            for net in nets_labelled :
                net_name = net[0]
                net_start = net[1]
                net_end = net[2]
                                          # test if net and port locations match
                if \
                    (net_start == port_coordinates) or \
                    (net_end == port_coordinates)      \
                :
                    if verbose :
                        print(2*INDENT + "%s - %s" % (port_name, net_name))
                    port_connections.append(
                        [component_name, port_name, net_name]
                    )
                                  # test if signal needs type and rage from port
                    for signal in signals :
                        if signal[0] == net_name :
                            if not signal[1] :
                                type_list = port_type.split('(')
                                signal_type = type_list[0]
                                signal[1] = signal_type
                                if not signal[2] :
                                    signal_range = ''
                                    if len(type_list) > 1 :
                                        signal_range = type_list[1].rstrip(')')
                                    signal[2] = signal_range

# ------------------------------------------------------------------------------
                                                            # write architecture
if verbose :
    print("\nWriting architecture")
vhdl_file = open(vhdl_file_spec, 'w')
                                                                     # libraries
vhdl_file.write("library %s;\n" % VHDL_library)
use_1164 = False
use_numeric_std = False
for signal in signals :
    signal_type = signal[1].lower()
    if signal_type.startswith('std_logic') :
        use_1164 = True
    if signal_type.startswith('std_ulogic') :
        use_1164 = True
    if signal_type == 'unsigned' :
        use_numeric_std = True
    if signal_type == 'signed' :
        use_numeric_std = True
if use_1164 or use_numeric_std :
    vhdl_file.write("library ieee;\n")
if use_1164 :
    vhdl_file.write(INDENT + "use ieee.std_logic_1164.all;\n")
if use_numeric_std :
    vhdl_file.write(INDENT + "use ieee.numeric_std.all;\n")
vhdl_file.write("\n")
                                                            # architecture start
vhdl_file.write(
    "architecture %s of %s_%s is\n" %
    (architecture_name, library_name, symbol_name)
)
                                                        # pre-begin declarations
remaining_text_blocks = []
for embedded_text in text_blocks :
    if embedded_text.startswith('architecture start') :
        vhdl_file.write("\n")
        start_code = embedded_text.split("\n")
        for line in start_code[1:] :
            vhdl_file.write(INDENT + line + "\n")
    else :
        remaining_text_blocks.append(embedded_text)
if verbose :
    if len(remaining_text_blocks) < len(text_blocks) :
        print(INDENT + 'start code')
text_blocks = remaining_text_blocks
                                                                       # signals
if signals :
    if verbose :
        print(INDENT + "signals :")
    vhdl_file.write("\n")
    for signal in signals :
        signal_name = signal[0]
        signal_type = signal[1]
        if signal[2] :
            signal_type = "%s(%s)" % (signal_type, signal[2])
        if verbose :
            print(2*INDENT + "%s : %s" % (signal_name, signal_type))
        vhdl_file.write(
            INDENT + "signal %s : %s;\n" % (signal_name, signal_type)
        )
                                                                    # components
if components :
    if verbose :
        print(INDENT + "component declarations :")
    vhdl_file.write("\n")
    for component in components :
        component_name = component['name']
        vhdl_component_name = component_name.replace('-', '_')
        if verbose :
            print(2*INDENT + component_name)
                                                                     # component
        component_name = component['name']
        vhdl_file.write(INDENT + "component %s\n" % vhdl_component_name)
                                                                      # generics
        component_generics = component['generics']
        if component_generics :
            separator = ';'
            vhdl_file.write(2*INDENT + "generic(\n")
            for index in range(len(component_generics)) :
                if index == len(component_generics)-1 :
                    separator = ''
                vhdl_file.write(
                    3*INDENT + "%s%s\n" % (component_generics[index], separator)
                )
            vhdl_file.write(2*INDENT + ");\n")
                                                                         # ports
        ports_file_spec = os.sep.join([
            scratch_directory,component_name + "-port_locations.txt"
        ])
        ports_file = open(ports_file_spec, 'r')
        ports = ports_file.read().replace("\r", "\n").split("\n")
        ports_file.close()
        while (len(ports) > 0) and (not ports[-1]) :
            ports.pop()
        if ports :
            separator = ';'
            vhdl_file.write(2*INDENT + "port(\n")
            for index in range(len(ports)) :
                port_code = ports[index].split('[', 1)[0].rstrip(' ')
                port_code = port_code.replace(' ', ' : ', 1)
                if index == len(ports)-1 :
                    separator = ''
                vhdl_file.write(3*INDENT + "%s%s\n" % (port_code, separator))
            vhdl_file.write(2*INDENT + ");\n")

                                                                           # end
        vhdl_file.write(INDENT + "end component %s;\n\n" % vhdl_component_name)
                                                            # architecture begin
vhdl_file.write("begin\n")
                                                             # component mapping
if components :
    if verbose :
        print(INDENT + "component mappings :")
    vhdl_file.write("\n")
    for component in components :
        component_name = component['name']
        vhdl_component_name = component_name.replace('-', '_')
        if verbose :
            print(2*INDENT + component_name)
                                                                         # label
        component_label = component['label']
        vhdl_file.write(INDENT)
        if component_label :
            vhdl_file.write(component_label + ' : ')
                                                                     # component
        vhdl_file.write("%s\n" % vhdl_component_name)
                                                               # generic mapping
        component_generics = component['generics']
        if component_generics :
            separator = ','
            vhdl_file.write(2*INDENT + "generic map(\n")
            for index in range(len(component_generics)) :
                generics_info = component_generics[index].split(':')
                generic_name = generics_info[0].rstrip(' ')
                generic_mapping = generics_info[-1].lstrip('= ')
                if index == len(component_generics)-1 :
                    separator = ''
                vhdl_file.write(
                    3*INDENT + "%s => %s%s\n" %
                    (generic_name, generic_mapping, separator)
                )
            vhdl_file.write(2*INDENT + ")\n")
                                                                  # port mapping
        if ports :
            separator = ','
            vhdl_file.write(2*INDENT + "port map(\n")
            for index in range(len(ports)) :
                port_name = ports[index].split(' ', 1)[0]
                connected_signal = ''
                for port_connection in port_connections :
                    if \
                        (port_connection[0] == component_name) and \
                        (port_connection[1] == port_name)          \
                    :
                        connected_signal = port_connection[2]
                    if not connected_signal :
                        connected_signal = 'open'
                if index == len(ports)-1 :
                    separator = ''
                vhdl_file.write(
                    3*INDENT + "%s => %s%s\n" %
                    (port_name, connected_signal, separator)
                )
            vhdl_file.write(2*INDENT + ");\n")
        vhdl_file.write("\n")
                                                                 # embedded code
found_embedded_code = False
if text_blocks :
    for embedded_text in text_blocks :
        if embedded_text.startswith('embedded code') :
            start_code = embedded_text.split("\n")
            for line in start_code[1:] :
                vhdl_file.write(INDENT + line + "\n")
            vhdl_file.write("\n")
            found_embedded_code = True
if found_embedded_code :
    if verbose :
        print(INDENT + 'embedded code')
                                                              # architecture end
vhdl_file.write("end %s;\n" % architecture_name)
vhdl_file.close()
