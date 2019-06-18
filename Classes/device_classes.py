# __author__ = Yannic Falke

import sys
import visa  # for GPIB communication
import time  # for loop over time
import numpy as np
import os  # import OS
import matplotlib.pyplot as plt
import serial
import serial.tools.list_ports
import weakref
import datetime
import socket


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

    def read_source_voltage(self):
        voltage = float(self.keithley.ask('SOUR:VOLT:LEV?').strip())
        return voltage

    def read_current(self):
        self.read_values()
        return self.current

    def read_source_current(self):
        current = float(self.keithley.ask('SOUR:CURR:LEV?').strip())
        return current

    def read_resistance(self):
        self.read_values()
        return self.resistance

    def set_voltage(self, value):
        self.keithley.write(':SOUR:VOLT:LEV {}'.format(value))

    def set_current(self, value):
        self.keithley.write(':SOUR:CURR:LEV {}'.format(value))

    def slowly_to_target(self, target, voltage=False):
        if voltage:
            now_val = round(self.read_source_voltage(),8)
            steps = np.linspace(now_val, target, 20)
        else:
            now_val = round(self.read_source_current(),8)
            steps = np.linspace(now_val, target, 20)
        if now_val == target:
            return
        # Need to reverse steps if going downwards
        if now_val > abs(target):
            steps = steps[::-1]

        for i in steps:
            if voltage:
                self.set_voltage(i)
            else:
                self.set_current(i)
            time.sleep(0.2)

    def get_mode(self):
        mode = self.keithley.ask('SOUR:FUNC:MODE?').strip()
        return mode

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
            ':SOUR:FUNC VOLT',  # Set voltage mode
            ':SOUR:VOLT:MODE FIX',
            ':SOUR:VOLT:RANG 200',  # Set acceptable voltage range
            ':SENS:FUNC "CURR"',  # Set-up current measurement
            # Set current compliance 100uA
            ':SENS:CURR:PROT {}'.format(self.compliance),
            ':SOUR:VOLT:LEV 0',  # Set voltage source to 0V
            ':OUTP ON'
        ]

        for i in gate_setup:
            self.gate.write(i)

    # def set_voltage(self, value):
        # self.gate.write(':SOUR:VOLT:LEV {}'.format(value))

    # def set_current(self, value):
        # self.gate.write(':SOUR:CURR:LEV {}'.format(value))



class Meter(Keithley):
    def __init__(self, gpibnum, source_val=0.00001, four_wire=True,
                 set_source_voltage=False, speed=6):
        if four_wire == True:
            self.fwire_str = 'ON'
        else:
            self.fwire_str = 'OFF'
        self.source_val = source_val
        self.set_source_voltage = set_source_voltage
        self.speed = speed
        self._initialize_keithley(gpibnum)
        self._initialize_meter()
        pass

    def _initialize_meter(self):
        self.meter = self.keithley
        
        if not self.set_source_voltage:
            max_curr = 1
            range_val = 5*self.source_val if 5*self.source_val < max_curr else max_curr
            #range_val = 50*self.source_val if 50*self.source_val < 200 else 200
            meter_setup = [
                '*RST',
                '*CLS',
                ':OUTP OFF',
                ':SOUR:FUNC CURR',  # Set current mode
                ':SOUR:CURR:MODE FIX',
                ':SOUR:CURR:RANG {}'.format(range_val),  # Set acceptable current range to 100uA
                # ':SOUR:CURR:RANG 0.200',  # Set acceptable current range to 100uA
                ':SENS:FUNC "VOLT"',  # Set-up voltage measurement
                ':SENS:VOLT:PROT 120.0',  # Set voltage compliance
                # Turn on 4-wire sensing
                ':SYST:RSEN {}'.format(self.fwire_str),
                # Set current source to 10 uA
                'SENS:VOLT:NPLCycles 6', 
                # ':SOUR:CURR:LEV {}'.format(self.source_val),
                'SENSE:VOLT:NPLCycles {}'.format(self.speed), # Set integration time
                ':OUTP ON'
            ]

            for i in meter_setup:
                self.meter.write(i)
            self.slowly_to_target(self.source_val, voltage=False)
        else:
            max_volts = 200
            range_val = 5*self.source_val if 5*self.source_val < max_volts else max_volts
            meter_setup = [
                '*RST',
                '*CLS',
                ':OUTP OFF',
                ':SOUR:FUNC VOLT',  # Set voltage mode
                ':SOUR:VOLT:MODE FIX',
                ':SOUR:VOLT:RANG {}'.format(range_val),  # Set acceptable current range to 100uA
                # ':SOUR:VOLT:RANG {}'.format(50*self.source_val),  # Set acceptable current range to 100uA
                # ':SOUR:VOLT:RANG 200',  # Set acceptable voltage range
                ':SENS:FUNC "CURR"',  # Set-up current measurement
                # Turn on 4-wire sensing
                ':SYST:RSEN {}'.format(self.fwire_str),
                # Set current compliance 100uA
                # ':SENS:CURR:PROT {}'.format(self.compliance),
                # Set voltage source to 0V
                # ':SOUR:VOLT:LEV {}'.format(self.source_val),
                'SENSE:CURR:NPLCycles {}'.format(self.speed), # Set integration time
                ':OUTP ON'
            ]

            for i in meter_setup:
                self.meter.write(i)

            self.slowly_to_target(self.source_val, voltage=True)
            

    def set_range(self, value, is_volts=True):
        if is_volts:
            self.meter.write(':SOUR:VOLT:RANG {}'.format(value))
        else:
            self.meter.write(':SOUR:CURR:RANG {}'.format(value))

    def switch_source_sign(self, is_voltmode):
        if is_voltmode:
            current_volt = self.read_source_voltage()
            print(current_volt)
            self.set_voltage(-1 * current_volt)
        else:
            current_current = self.read_source_current()
            print(current_current)
            self.set_current(-1 * current_current)




class Lakeshore():
    ''' Class for all Lakeshore devices '''
    instances = []

    def __init__(self):
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
        self.serial.close()

    def use_command(self, command):
        length = chr(len(command) + 34)
        crc = self.crc_calc(length + command)
        command = '!' + length + command + crc[0] + crc[1]
        command_bytes = bytearray()
        for i in range(0, len(command)):
            command_bytes.append(ord(str(command[i])))
        self.serial.write(command_bytes)
        time.sleep(0.1)
        reply = self.serial.read(self.serial.inWaiting())
        return reply

    def measure_rate(self, channel=1):
        command = 'L1'
        reply = self.use_command(command)
        rate = float(reply[3:-2].decode("utf-8"))
        if rate < 1.5:
            return float(rate)
        else:
            return 0

    def measure_thickness(self, channel=1):
        command = 'N1'
        reply = self.use_command(command)
        thickness = float(reply[3:-2].decode("utf-8"))
        return thickness

    def measure_frequency(self, channel=1):
        command = 'P1'
        reply = self.use_command(command)
        frequency = float(reply[3:-2].decode("utf-8"))
        return frequency

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
    instances = []
    def __init__(self, gpib_number=8):
        self.__class__.instances.append(weakref.proxy(self))
        rm = visa.ResourceManager()
        self.lockin = rm.open_resource("GPIB::{}".format(gpib_number))
        print('Initialized Lockin on GPIB::{}'.format(gpib_number))
        # self.lockin.write("")
        self.lockin.write('OUTX 1')  # Sets device to talk over GPIB
        self.tauset = {
            0: "10mus",
            1: "30mus",
            2: "100mus",
            3: "300mus",
            4: "1ms",
            5: "3ms",
            6: "10ms",
            7: "30ms",
            8: "100ms",
            9: "300ms",
            10: "1s",
            11: "3s",
            12: "10s",
            13: "30s",
            14: "100s",
            15: "300s",
            16: "1ks",
            17: "3ks",
            18: "10ks",
            19: "30ks"}
        self.sensset = {
            0: "2nV",
            1: "5nV",
            2: "10nV",
            3: "20nV",
            4: "50nV",
            5: "100nV",
            6: "200nV",
            7: "500nV",
            8: "1muV",
            9: "2muV",
            10: "5muV",
            11: "10muV",
            12: "20muV",
            13: "50muV",
            14: "100muV",
            15: "200muV",
            16: "500muV",
            17: "1mV",
            18: "2mV",
            19: "5mV",
            20: "10mV",
            21: "20mV",
            22: "50mV",
            23: "100mV",
            24: "200mV",
            25: "500mV",
            26: "1V"}

    def set_freq(self, value: float):
        self.lockin.write('FREQ {}'.format(value))

    def set_amp(self, value: float):
        self.lockin.write('SLVL {}'.format(value))

    def set_phase(self, value: float):
        self.lockin.write('PHAS {}'.format(value))

    def set_phase_plus_90(self, value: float):
        value = value + 90
        self.lockin.write('PHAS {}'.format(value))

    def set_phase_minus_90(self, value: float):
        value = value - 90
        self.lockin.write('PHAS {}'.format(value))

    def set_signal_input(self, inputstring: str):
        inputstring = inputstring.strip()
        thisdict = {
            'A': 0,
            'A-B': 1,
            'IE6': 2,
            'IE8': 3,
        }
        if not inputstring in thisdict:
            raise ValueError('Given Signal Input is not known. Use one of the following:\n {}'
                             .format(thisdict.keys()))
        else:
            corresp_value = thisdict[inputstring]
            self.lockin.write('ISRC {}'.format(corresp_value))

    def set_ACDC(self, signal: str):
        signal = signal.upper().strip()
        if signal == 'AC':
            self.lockin.write('ICPL 0')
        if signal == 'DC':
            self.lockin.write('ICPL 1')
        else:
            raise ValueError(
                'Signal for ACDC not known. Set AC or DC as string value.')

    def set_shield(self, signal: str):
        signal = signal.lower().strip()
        if signal == 'float':
            self.lockin.write('IGND 0')
        if signal == 'ground':
            self.lockin.write('IGND 1')
        else:
            raise ValueError('Signal for shield not known.' +
                             'Set FLOAT or GROUND as string value.')

    def set_sensitivity(self, value: str):
        if not value in self.sensset:
            raise ValueError('Signal for sensitivity not known. Use one of' +
                             'the following: {}'.format(self.sensset.keys()))
        else:
            sensval = int(self.sensset[value])
            self.lockin.write('SENS {}'.format(sensval))

    def set_time_const(self, value: str):
        if not value in self.tauset:
            raise ValueError('Signal for sensitivity not known. Use one of' +
                             'the following: {}'.format(self.tauset.keys()))
        else:
            tauval = int(self.tauset[value])
            self.lockin.write('OFLT {}'.format(tauval))

    def read_chann_one_display(self):
        self.lockin.ask('OUTR? 1')

    def read_chann_two_display(self):
        self.lockin.ask('OUTR? 2')

    def set_chann_one_display(self, inputstring):
        self.lockin.ask('DDEF1,0,0')

    def read_voltage(self):
        return(self.lockin.ask('OUTR? 1'))
    
    def auto_gain(self):
        self.lockin.write('AGAN')

    def auto_gain(self):
        print("Auto gaining... ")
        gainer = self.lockin.write('AGAN')

    def close(self):
        self.lockin.close()

    def read_current(self):
        return 1E-5


class FUG():
    def __init__(self, port):
        try:
            self.ser = serial.Serial(
                port=port,
                baudrate=9600,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
                bytesize=serial.EIGHTBITS,
                timeout=1,
                rtscts=False,
                dsrdtr=False
            )
            time.sleep(1)
            self.ser.flushOutput()
            self.ser.flushInput()
            print('Successfully opened FUG! ')
        except:
            print('Could not open FUG. Exiting... ')
            sys.exit()

    def set_maxima(self):
        self.ser.flushOutput()
        self.ser.flushInput()
        self.ser.write(b'>S0 1000\r\n')
        self.ser.flushOutput()
        self.ser.flushInput()
        self.ser.write(b'>S1 0.14\r\n')

    def read_emission(self):
        self.ser.flushOutput()
        self.ser.flushInput()
        self.ser.write(b'>M1?\r\n')
        answer = self.ser.readline().decode('utf-8')
        value = float(answer.split(':')[-1].strip())
        value = round(value * 1E3, 1) # Conversion from A to mA
        return value

    def output_off(self):
        self.ser.write(b'F0\r\n')

    def output_on(self):
        time.sleep(0.3)
        self.ser.write(b'F1\r\n')

    def close(self):
        self.ser.write(b'F0\r\n')
        self.ser.close()

class AML:
    def __init__(self, comport):
        self.comport = comport
        self.ser = serial.Serial()
        self.init_port()

    def init_port(self):
        self.ser.port=self.comport
        self.ser.baudrate=9600
        self.ser.parity=serial.PARITY_NONE
        self.ser.stopbits=serial.STOPBITS_ONE
        self.ser.bytesize=serial.EIGHTBITS
        self.ser.write_timeout=3
        self.ser.timeout=3
        self.ser.rts=1,
        self.ser.dtr=1,
        self.ser.open()
        now = datetime.datetime.now()
        print('Sucessfully opened connection! {}'.format(now))

    def read_value(self):
        connection_open = self.ser.is_open
        while not connection_open:
            time.sleep(1)
            try:
                self.init_port()
            except:
                print('Could not open connection to AML... {}'\
                        .format(datetime.datetime.now()))
            connection_open = self.ser.is_open
        is_avail = False
        self.ser.reset_input_buffer()
        self.ser.write(b'*S0')

        time.sleep(0.2)
        while not is_avail:
            try:
                answer = self.ser.readline().decode('utf-8')
            except:
                answer = ''
            # Catches Connection problems
            if not 'GI1' in answer:
                print('TIMED OUT! Restarting connection...')
                self.ser.close()
                time.sleep(1)
                self.init_port()
                self.ser.write(b'*S0')
                time.sleep(1)
                is_avail = False
            else:
                try:
                    # Catches AML being turned off
                    answer = self.convert_value(answer)
                    is_avail = True
                except:
                    is_avail = False
        self.ser.reset_input_buffer()
        self.ser.close()
        return answer


    def convert_value(self, instring):
        out = instring.split('1A@')[-1].split(',')[0]
        out = out.strip()
        return float(out)

class Nenion:
    ''' Class for communication with Nenion valve over TCP/IP '''
    def __init__(self, ip='134.95.66.95', port=1512):
        self.IP = ip
        self.PORT = port
        self.init_tcp()

    def init_tcp(self):
        ''' Initialized TCP/IP connection on given IP and PORT '''
        BUFFER_SIZE = 80  # Normally 1024, but we want fast response
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.settimeout(3.0)
        self.s.connect((self.IP, self.PORT))
        time.sleep(2)

    def write(self, msg):
        msg = msg.strip() + '\r'
        ''' Sends message as bytecode with <enter> in the end'''
        self.s.send(msg.encode())

    def goto_pos(self, pos):
        self.write('H')
        time.sleep(0.2)
        actual_pos = int(pos/25) # Need to convert from 1E6 steps to 40k steps
        msg = 'G{}'.format(actual_pos)
        self.write(msg)

    def close_pos(self):
        self.write('H')
        time.sleep(0.2)
        self.write('G0')


if __name__ == '__main__':
    print('\
    This is the file holding the Device classes.\
    Calling this directly is of no use.\
    Exiting ...')
    sys.exit()
