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
    
    def run_range(self, steps):
        for i in steps:
            if i >= 1.0:
                i = round(i,3) # Maximal sensisivity 
            else:
                i = round(i,4) # Maximal sensisivity 
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


if __name__ == "__main__":
    k = UseKorad()
    try:
        k.run_amount()
    except KeyboardInterrupt:
        k.finish()
    k.finish()
    