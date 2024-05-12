-- library I2S_test;

architecture sim of I2S_test_deserializer_tester is
                                                              -- reset and clock
  constant clockPeriod : time := 1.0/clockFrequency * 1 sec;
  signal clock_int : std_ulogic := '1';

begin
                                                              -- reset and clock
  reset <= '1', '0' after 2*clockPeriod;
  clock_int <= not clock_int after clockPeriod;
  clock <= transport clock_int after 9/10*clockPeriod;
                                                            -- end of simulation
  process
  begin
    wait for 10 us;
    assert false report "end of test" severity failure;

    wait;
  end process;

end architecture sim;
