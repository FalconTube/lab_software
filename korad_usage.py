from korad_class import KoradSerial
import time
import numpy as np
import sys

class UseKorad(KoradSerial):
    def __init__(self):
        try:
            self.korad = KoradSerial('COM5')
            self.channel = self.korad.channels[0]
            self.korad.output.off()
            self.channel.current = 0.0
            if self.ask_voltage():
                setvoltage = float(\
                input("Set new voltage value [default = 17]: ") or 17.0)
                self.channel.voltage = setvoltage
            else:
                pass
            self.korad.output.on()
            # print('Would put output on now.')
        except:
            print('Cannot turn on the Korad. Exiting... ')
            sys.exit()

    def ask_voltage(self):
        choice = str(input("Do you want to switch the voltage?: (y/n)") or 'n')
        choice = choice.lower()
        if choice == 'y':
            return True
        if choice == 'n':
            return False
        else:
            print('Please input a valid choice. Exiting...')
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
        init_step = self.round_value(steps[0])
        self.ramp_to_current(init_step)
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

    def ramp_to_current(self, target):
        ''' Ramps to target value over approx 10 seconds '''
        current_current = self.channel.current
        print('current current {}'.format(current_current))
        time.sleep(0.05)
        ramp_range = np.linspace(current_current, target, 40)
        for i in ramp_range:
            i = self.round_value(i)
            self.channel.current = i
            time.sleep(0.25)

    def finish(self):
        print('Turning off output and closing device.')
        self.channel.current = 0.0
        self.korad.output.off()
        self.korad.close()
        sys.exit()

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
        for i,j in zip(currentlist,timelist):
            i = self.round_value(i)
            print('Setting current to {} Amp'.format(i))
            self.ramp_to_current(i)
            print('Waiting for {} Min\n from this time on: {}'\
            .format(j/60, time.ctime()))
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
    