#!/bin/bash
                                                                         # setup
compileList="I2S_test-deserializer_testbench-struct-compile_list.txt"
topLevel="I2S_test_deserializer_tester"
compileOnly="false"
                                                          # exit script on error
set -e
                                                     # work in scratch directory
cd /tmp
rm -f *.cf
                                                             # analyse all files
while read -r vhdlFileSpec ; do
  echo "$vhdlFileSpec"
  ghdl -a $vhdlFileSpec
done < "$compileList"
                                                              # test if continue
if [ "$compileOnly" = true ] ; then
  exit 0
fi
                                                               # simulate design
ghdl -e $topLevel
ghdl -r $topLevel --vcd=$topLevel.vcd
