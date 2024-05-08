v 20200319 2
C 10500 9500 1 0 0 I2S-deserializer.sym
{
T 10500 9000 5 10 1 1 0 0 1
refdes=I_DUT
T 11100 10900 5 10 0 1 0 0 1
device=none
T 10492 8800 5 10 1 1 0 0 1
generic1=bitNb : positive := signalBitNb
T 12000 9200 5 10 1 1 0 0 1
source=I2S-deserializer-rtl.vhd
}
C 6000 5500 1 0 0 I2S_test-deserializer_tester.sym
{
T 6000 5000 5 10 1 1 0 0 1
refdes=I_tester
T 6600 6900 5 10 0 1 0 0 1
device=none
T 5992 4800 5 10 1 1 0 0 1
generic1=bitNb : positive := signalBitNb
T 8600 5200 5 10 1 1 0 0 1
source=I2S_test-deserializer_tester-sim.vhd
}
N 9500 8000 9500 10000 4
{
T 9450 8000 5 10 1 1 90 0 1
netname=reset
}
N 9500 10000 10000 10000 4
N 9000 8000 9000 10500 4
{
T 8950 8000 5 10 1 1 90 0 1
netname=clock
}
N 9000 10500 10000 10500 4
N 8000 8000 8000 11500 4
{
T 7950 8000 5 10 1 1 90 0 1
netname=SD
}
N 8000 11500 10000 11500 4
N 7500 8000 7500 12000 4
{
T 7450 8000 5 10 1 1 90 0 1
netname=WS
}
N 7500 12000 10000 12000 4
N 7000 8000 7000 12500 4
{
T 6950 8000 5 10 1 1 90 0 1
netname=SCK
}
N 7000 12500 10000 12500 4
U 15000 12500 16500 12500 10 0
U 16500 12500 16500 8000 10 0
{
T 16550 8000 5 10 1 1 90 2 1
netname=signalLeft
}
N 15000 11500 15500 11500 4
N 15500 11500 15500 8000 4
{
T 15550 8000 5 10 1 1 90 2 1
netname=sampleValid
}
U 15000 12000 16000 12000 10 0
U 16000 12000 16000 8000 10 0
{
T 16050 8000 5 10 1 1 90 2 1
netname=signalRight
}
T 500 16000 9 10 1 0 0 0 2
pre-begin:
constant bitNb : positive := 24;
C 0 0 0 0 0 title-A2.sym
