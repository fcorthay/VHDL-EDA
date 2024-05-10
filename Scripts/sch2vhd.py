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
component_location = [0, 0]
net_start = [0, 0]
net_end = [0, 0]
text_block = ''
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
                                                             # net wrap together
        if line.startswith('}') :
            nets_labelled.append([net_name, net_start.copy(), net_end.copy()])
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
            processing_net_start = True
        elif line.startswith('T ') :
            text_block = ''
            processing_text = True
    if not line :
        done = True
schematics_file.close()

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
port_locations = []
for component in components :
    component_name = component['name']
    component_location = component['location']
    if verbose :
        print(INDENT + component_name)
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
        if len(location_list) == 3 :
            port_name = location_list[0]
            port_coordinates = [
                component_location[0] + int(location_list[1]),
                component_location[1] + int(location_list[2])
            ]
            for net in nets_labelled :
                net_name = net[0]
                net_start = net[1]
                net_end = net[2]
                if \
                    (net_start == port_coordinates) or \
                    (net_end == port_coordinates)      \
                :
                    if verbose :
                        print(2*INDENT + "%s - %s" % (port_name, net_name))
                    port_locations.append([component_name, port_name, net_name])
#print(port_locations)

#    print(2*INDENT, end='') ; print(component)

# ------------------------------------------------------------------------------
                                                            # write architecture
# if verbose :
#     print("\nWriting architecture")
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
