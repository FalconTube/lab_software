import serial
import time

class Manipulator():
    def __init__(self):
        '''Initializes Manipulator in ARPES Lab via RS232'''
        self.ser = serial.Serial(port='COM2', #Remember to check if the instrument is on COM2 or not
                    baudrate=9600,
                    timeout=3,
                    bytesize=serial.EIGHTBITS,
                    xonxoff=False)


    def write(self, input):
        writestr = "\x02" + str(input) + "\x03\r\n"
        self.ser.write(writestr.encode())

    def ask(self, instr):
        time.sleep(0.05)
        self.ser.flushInput()
        self.ser.flushOutput()
        self.write(instr)
        value = self.ser.readline().decode('utf-8')
        value = value[2:-3].strip()

        return value

    def go_to_absolute(self):
        pass

    def close(self):
        self.ser.close()

    def readVal(self, ax):
        ''' Reads Value of ax
        Returns
        -------
        str value
        '''
        self.ser.flushInput()
        self.ser.flushOutput()
        self.write(f'{ax}P21R')
        value = self.ser.readline().decode('utf-8')
        value = value[2:-3].strip()

        return value

    def getPossiblePositions(self, position):

        possible_coords = {
            'Gamma': {
                'X': -4,
                'Y': 0.0,
                # 'Z': -14.3,
            },
            'Insert': {
                'X': 34.8,
                'Y': -19.0,
                'Z': 26,
            }
        }


        possible_coords_old = {
            'Gamma': {
                'X': -414.0,
                'Y': 17.675,
                'Z': -25.5,
            },
            'Insert': {
                'X': -387.1,
                'Y': 0.7,
                'Z': -11.2,
            }
        }

        return possible_coords[position]