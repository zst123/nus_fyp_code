#!/usr/bin/python3
import simulator
import numpy as np

class CbaDriver:
    def __init__(self, wordline, bitline):
        self.io = dict()

        self.io['WORD'] = np.zeros(shape=(wordline))
        self.io['BIT'] = np.zeros(shape=(bitline))
        self.io['G'] = np.zeros(shape=(wordline, bitline))

        self.bitline = bitline
        self.wordline = wordline

        self._invalidate_simulation_cache()

    def _simulation_setup(self, exe, dir, netlist, spice='ltspice', sim_id=7):
        if spice == 'ltspice':
            simulator.set_ltspice(exe=exe, dir=dir)
        elif spice == 'hspice':
            simulator.set_hspice(exe=exe, dir=dir)
        self.simulator_netlist = netlist
        self.simulator_id = sim_id

    def _simulation_execute(self):
        if not self.cache_result:
            self.cache_result = simulator.simulate_netlist(
                wordline=self.wordline,
                bitline=self.bitline,
                io=self.io,
                netlist=self.simulator_netlist,
                tmp_id=self.simulator_id)
        return self.cache_result

    def _invalidate_simulation_cache(self):
        self.cache_result = None

    def program_resistance_state(self, states):
        self._invalidate_simulation_cache()
        assert self.wordline == len(states)
        assert self.bitline == len(states[0])
        self.io['G'] = np.array(states)

    def drive_bit_voltage(self, array):
        self._invalidate_simulation_cache()
        assert self.bitline == len(array)
        self.io['BIT'] = np.array(array)

    def drive_word_voltage(self, array):
        self._invalidate_simulation_cache()
        assert self.wordline == len(array)
        self.io['WORD'] = np.array(array)

    def read_word_voltage(self):
        return self.io['WORD']

    def read_bit_voltage(self):
        return self.io['BIT']

    def read_word_current(self):
        result = self._simulation_execute()
        return np.array(result['word_current'])

    def read_bit_current(self):
        result = self._simulation_execute()
        return np.array(result['bit_current'])


class CbaRuntime:
    def __init__(self, CBA_PARAMETERS, SIM_PARAMETERS, CIRCUIT_PARAMETERS):
        # CBA1 holds positive weights
        self.cba1 = CbaDriver(wordline=CBA_PARAMETERS['wordline'],
                              bitline=CBA_PARAMETERS['bitline'])
        self.cba1._simulation_setup(exe=SIM_PARAMETERS['exe'],
                                    dir=SIM_PARAMETERS['dir'],
                                    spice=SIM_PARAMETERS['spice'],
                                    netlist=CIRCUIT_PARAMETERS['wrapper'],
                                    sim_id=1)

        # CBA2 holds negative weights
        self.cba2 = CbaDriver(wordline=CBA_PARAMETERS['wordline'],
                              bitline=CBA_PARAMETERS['bitline'])
        self.cba2._simulation_setup(exe=SIM_PARAMETERS['exe'],
                                    dir=SIM_PARAMETERS['dir'],
                                    spice=SIM_PARAMETERS['spice'],
                                    netlist=CIRCUIT_PARAMETERS['wrapper'],
                                    sim_id=2)
        # Midpoint bias
        self.bias_voltage = CBA_PARAMETERS.get('bias_voltage', 0)

    def program_memory(self, states):
        # Split the positive and negative values onto two arrays
        cba1_state = np.multiply(states > 0, states*+1)
        cba2_state = np.multiply(states < 0, states*-1)

        # Represent on the crossbar
        self.cba1.program_resistance_state(cba1_state)
        self.cba2.program_resistance_state(cba2_state)

    def set_wordline(self, word_array):
        # Center around bias voltage
        cba1_word = self.bias_voltage + np.array(word_array)
        cba2_word = self.bias_voltage - np.array(word_array)
        # Drive both wordlines
        self.cba1.drive_word_voltage(cba1_word)
        self.cba2.drive_word_voltage(cba2_word)

    def set_bitline(self, bit_array):
        # Center around bias voltage
        cba1_bit = self.bias_voltage + np.array(bit_array)
        cba2_bit = self.bias_voltage - np.array(bit_array)
        # Drive both bitlines
        self.cba1.drive_bit_voltage(cba1_bit)
        self.cba2.drive_bit_voltage(cba2_bit)

    def read_bitline(self):
        # Read result
        result1 = self.cba1.read_bit_current()
        result2 = self.cba2.read_bit_current()
        result = result1+result2
        return result

    def read_wordline(self):
        # Read result
        result1 = self.cba1.read_word_current()
        result2 = self.cba2.read_word_current()
        result = result1+result2
        return result
