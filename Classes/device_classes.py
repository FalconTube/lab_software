# __author__ = Yannic Falke

import sys 
import visa # for GPIB communication
import time  # for loop over time
import numpy as np
import os # import OS
import tkinter
import tkinter.messagebox as mbox
import matplotlib.pyplot as plt
import serial
import weakref

rm = visa.ResourceManager()

class Keithley():
    ''' Class for all Keithley devices '''
    instances = []
    def __init__(self, gpibnum):
        self.__class__.instances.append(weakref.proxy(self))
        self._initialize_keithley(gpibnum)
        pass

    def _initialize_keithley(self, gpibnum):
        rm = visa.ResourceManager()
        print("GPIB::{}".format(gpibnum))
        self.keithley = rm.open_resource("GPIB::{}".format(gpibnum))
        print('Initialized Keithley number {}'.format(gpibnum))
    
    def close(self):
        self.keithley.close()
    
    def read_values(self):
        # values = self.keithley.query_ascii_values(':READ?')
        values = self.keithley.ask(':READ?')
        values = values.split(',')
        self.voltage = float(values[0].strip())
        self.current = float(values[1].strip())
        self.resistance = float(values[2].strip())
    
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
    def __init__(self, gpibnum, compliance=0.0010):
        self.compliance = compliance
        self._initialize_keithley(gpibnum)
        self._initialize_gate()
        pass
    
    def _initialize_gate(self):
        self.gate = self.keithley
        gate_setup = [
        '*RST',
        '*CLS',
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
        '*RST',
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
    ''' Class for all Lakeshore devices '''
    instances = []
    def  __init__(self):
        self.__class__.instances.append(weakref.proxy(self))
        rm = visa.ResourceManager()
        self.lakeshore = rm.open_resource('GPIB::12')
        self.lakeshore.write("*RST; status:preset; *ClS")
    
    def read_temp(self):
        temp = self.lakeshore.query("KRDG? B")
        return float(temp)
    
    def set_temp(self, value):
        ask_temp = self.lakeshore.query("SETP? 1")
        print('Current temperature of lakeshore is: {}'.format(ask_temp))
        print('Setting temperature of lakeshore to: {}'.format(value))
        self.lakeshore.write("SETP 1, {}".format(value))
        print('Current temperature of lakeshore is: {}'.format(ask_temp))

    def close(self):
        self.lakeshore.close()

class InficonSQM160(object):
    """ Driver for Inficon SQM160 QCM controller """
    def __init__(self, port='COM7'):
        self.serial = serial.Serial(port=port,
                                    baudrate=19200,
                                    timeout=2,
                                    bytesize=serial.EIGHTBITS,
                                    xonxoff=True)

    def measure_rate(self, channel=1):
        command = 'L1'
        length = chr(len(command) + 34)
        crc = self.crc_calc(length + command)
        command = '!' + length + command + crc[0] + crc[1]
        command_bytes = bytearray()
        for i in range(0, len(command)):
            command_bytes.append(ord(str(command[i])))
        self.serial.write(command_bytes)
        time.sleep(0.1)
        reply = self.serial.read(self.serial.inWaiting())
        rate = float(reply[3:-2].decode("utf-8"))
        if rate < 1.5:
            return float(rate)
        else:
            return 0


    @staticmethod
    def crc_calc(input_string):
        """ Calculate crc value of command """
        command_string = []
        for i in range(0, len(input_string)):
            command_string.append(ord(input_string[i]))
        crc = int('3fff', 16)
        mask = int('2001', 16)
        for command in command_string:
            crc = command ^ crc
            for i in range(0, 8):
                old_crc = crc
                crc = crc >> 1
                if old_crc % 2 == 1:
                    crc = crc ^ mask
        crc1_mask = int('1111111', 2)
        crc1 = chr((crc & crc1_mask) + 34)
        crc2 = chr((crc >> 7) + 34)
        return(crc1, crc2)

class Lockin():
    def __init__(self):
        self.lockin = rm.open_resource("GPIB::8")
        self.lockin.write('OUTX 1') # Sets device to talk over GPIB

    
    def set_freq(self, value : float):
        self.lockin.write('FREQ {}'.format(value))
    
    def set_amp(self, value : float):
        self.lockin.write('SLVL {}'.format(value))

    def set_phase(self, value : float):
        self.lockin.write('PHAS {}'.format(value))
    
    def set_phase_plus_90(self, value : float):
        value = value + 90
        self.lockin.write('PHAS {}'.format(value))

    def set_phase_minux_90(self, value : float):
        value = value - 90
        self.lockin.write('PHAS {}'.format(value))
    
    def set_signal_input(self, inputstring : str):
        inputstring = inputstring.strip()
        thisdict = {
            'A' : 0,
            'A-B' : 1,
            'IE6' : 2,
            'IE8' : 3,
        }
        if inputstring not in thisdict:
            print('Given Signal Input is not known. Use one of the following:\n {} \n Exiting ...'\
            .format(thisdict))
            sys.exit()
        else:
            corresp_value = thisdict[inputstring]
            self.lockin.write('ISRC {}'.format(corresp_value))

    def set_ACDC(self, signal : str):
        signal = signal.upper().strip()
        if signal == 'AC':
            self.lockin.write('ICPL 0')
        if signal == 'DC':
            self.lockin.write('ICPL 1')
        else:
            print('Signal for ACDC not known. Set AC or DC as string value. Exiting ...')
            sys.exit()
    
    def set_shield(self, signal : str):
        signal = signal.lower().strip()
        if signal == 'float':
            self.lockin.write('IGND 0')
        if signal == 'ground':
            self.lockin.write('IGND 1')
        else:
            print('Signal for shield not known. Set float or ground as string value. Exiting ...')
            sys.exit()
    
    def set_sensitivity(self, value : float):
        # TODO Think of a nice way to define all sensi values
        pass

    def set_time_const(self, value : float):
        # TODO Think of a nice way to define all sensi values
        pass

    def read_chann_one_display(self):
        self.lockin.write('OUTR? 1')

    def read_chann_two_display(self):
        self.lockin.write('OUTR? 2')
    
    def set_chann_one_display(self, inputstring):
        print(self.lockin.write('DDEF1,0,0'))

if __name__ == '__main__':
    print('\
    This is the file holding the Device classes.\
    Calling this directly is of no use.\
    Exiting ...')
    sys.exit()