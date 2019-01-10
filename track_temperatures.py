from Classes.measurement_class import Measurement


import time
import numpy as np
import sys


class TempTracker(Measurement):
    def __init__(self):
        pass

    def track_it(self):
        self.ask_savename()
        with open(self.savename, 'a') as f:
            f.write('# Elapsed time [s] Temperature [C]\n')
            starttime = time.time()
            f.write('# Starttime: {}\n'.format(starttime))
            writemode = True
            while writemode == True:
                temp = float(input('Current Temperature: (exit by writing 999) '))
                if temp == float(999):
                    writemode = False
                else:
                    now = time.time()
                    elapsed = now - starttime
                    f.write('{}, {}\n'.format(elapsed, temp))
        

if __name__ == '__main__':
    tt = TempTracker()
    tt.track_it()
    print('Finished TempTracker. Exiting...')
    sys.exit()
