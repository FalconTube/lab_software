from korad_class import KoradSerial
import time
import numpy as np
import sys

class UseKorad(KoradSerial):
    def __init__(self):
        try:
            self.korad = KoradSerial('COM5')
            self.channel = self.korad.channels[0]
            self.korad.output.on()
        except:
            print('Cannot turn on the Korad. Exiting... ')
            sys.exit()
        
    def define_range(self):
        start = float(input('Insert STARTing current in Amp: '))
        end = float(input('Insert ENDing current in Amp: '))
        ptime = float(input('Insert time, that the process shall take'
        + ' in MINutes: '))
        ptime *= 60 # Conversion so seconds
        steps = np.linspace(start, end, ptime)
        return steps
    
    def round_value(self, value):
        if value >= 1.0:
            value = round(value,3) # Max sensitivity 
        else:
            value = round(value,4) # Max sensisivity 
        return value

    def run_range(self, steps):
        for i in steps:
            i = self.round_value(i)
            self.channel.current = i
            time.sleep(0.98)
    
    def run_amount(self):
        amount = int(input("How many ranges do you want to define? ") or 1)
        if amount == 1:
            testrange = self.define_range()
            self.run_range(testrange)
        else:
            runlist = []
            for n in range(amount):
                print("\nInput run number {}".format(n))
                testrange = self.define_range()
                runlist.append(testrange)
            
            for n in runlist:
                self.run_range(n)

    def finish(self):
        print('Turning off output and closing device.')
        self.korad.output.off()
        self.close()

    def set_constant_values(self):
        amount = int(input("How many steps do you want to define? ") or 1)
        currentlist = []
        timelist = []
        for n in range(amount):
            current = float(input("Set current for step {} in Amp: ".format(n)))
            wtime = float(input("Set time to wait after step {} in MIN: "\
            .format(n)))
            wtime *= 60
            currentlist.append(current)
            timelist.append(wtime)
        for i,j in currentlist,timelist:
            i = self.round_value(i)
            print('Setting current to {} Amp'.format(i))
            self.channel.current = i
            print('Waiting for {} Min'.format(j))
            time.sleep(j)

if __name__ == "__main__":
    k = UseKorad()
    meas = str(input('Do you want to set constant values (V) or' +
    ' some ranges (R)?: (V/R)'))
    meas = meas.lower()
    # if meas != 'r' or meas != 'v':
    if meas == 'r':            
        try:
            k.run_amount()
        except KeyboardInterrupt:
            k.finish()
        k.finish()
    if meas == 'v':            
        try:
            k.set_constant_values()
        except KeyboardInterrupt:
            k.finish()
        k.finish()
    else:
        print('Did not define measurement. Exiting... ')
        sys.exit()
    k.finish()
    