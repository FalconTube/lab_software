# __author__ = Yannic Falke

import sys 
import visa # for GPIB communication
import time  # for loop over time
import numpy as np
import os # import OS
import tkinter
import tkinter.messagebox as mbox
import matplotlib.pyplot as plt
import weakref

class Keithley():
    ''' Keithley class

    '''
    instances = []
    def __init__(self, gpibnum):
        self.__class__.instances.append(weakref.proxy(self))
        self._initialize_keithley(gpibnum)
        pass

    def _initialize_keithley(self, gpibnum):
        rm = visa.ResourceManager()
        self.keithley = rm.open_resource("GPIB::{}".format(gpibnum))
        print('Initialized Keithley number {}'.format(gpibnum))
    
    def close(self):
        self.keithley.close()
    
    def read_values(self):
        values = self.keithley.query_ascii_values(':READ?')
        self.voltage = values[0]
        self.current = values[1]
        self.resistance = values[2]
    
    def read_voltage(self):
        self.read_values()    
        return self.voltage
    
    def read_current(self):
        self.read_values()    
        return self.current
    
    def read_resistance(self):
        self.read_values()    
        return self.resistance

class Gate(Keithley):
    def __init__(self, gpibnum, compliance=0.000010):
        self.compliance = compliance
        self._initialize_keithley(gpibnum)
        self._initialize_gate()
        pass
    
    def _initialize_gate(self):
        self.gate = self.keithley
        gate_setup = [
        # '*RST',
        '*CLS'
        ':OUTP OFF',
        ':SOUR:FUNC VOLT',       #Set voltage mode
        ':SOUR:VOLT:MODE FIX',
        ':SOUR:VOLT:RANG 200',   #Set acceptable voltage range
        ':SENS:FUNC "CURR"',     #Set-up current measurement
        ':SENS:CURR:PROT {}'.format(self.compliance),    #Set current compliance 100uA
        ':SOUR:VOLT:LEV 0',  #Set voltage source to 0V
        ':OUTP ON'
        ]
        
        for i in gate_setup:
            self.gate.write(i)
    
    def set_gatevoltage(self, value):
        self.gate.write(':SOUR:VOLT:LEV {}'.format(value))


class Meter(Keithley):
    def __init__(self, gpibnum, curr_source=0.00001, four_wire=True):
        if four_wire == True:
            self.fwire_str = 'ON'
        else:
            self.fwire_str = 'OFF'
        self.curr_source = curr_source
        self._initialize_keithley(gpibnum)
        self._initialize_meter()
        pass
    
    def _initialize_meter(self):
        self.meter = self.keithley
        meter_setup = [
        # '*RST',
        '*CLS',
        ':OUTP OFF',
        ':SOUR:FUNC CURR',       #Set current mode
        ':SOUR:CURR:MODE FIX',
        ':SOUR:CURR:RANG 0.000100',   #Set acceptable current range to 100uA
        ':SENS:FUNC "VOLT"',     #Set-up voltage measurement
        ':SENS:VOLT:PROT 1.0',    #Set voltage compliance 
        ':SYST:RSEN {}'.format(self.fwire_str),     #Turn on 4-wire sensing
        ':SOUR:CURR:LEV {}'.format(self.curr_source),  #Set current source to 10 uA
        ':OUTP ON'
        ]
        
        for i in meter_setup:
            self.meter.write(i)

class Lakeshore():
    def  __init__(self):
        rm = visa.ResourceManager()
        self.ls = rm.open_resource('GPIB::12')
        self.ls.write("*RST; status:preset; *CLS")
    
    def read_temp(self):
        temp = self.ls.query("KRDG? B")
        return temp
    
    def close(self):
        self.ls.close()


if __name__ == '__main__':
    print('\
    This is the file holding the Keithley class.\
    Calling this directly is of no use.\
    Exiting ...')
    sys.exit()