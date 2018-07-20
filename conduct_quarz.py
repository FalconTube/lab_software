# __author__ = Yannic Falke

from device_classes import *
from measurement_class import Measurement

import time

class Quarz(Measurement):
    def __init__(self):
        self.ask_savename()
        self.savename = 't.dat'
        savestring = '#Time [s], Temperature [K], Resistance [Ohm], Deposit rate [Angstrom/s]'
        self.create_savefile(savestring)
        self.meter = Meter(2)
        self.lakeshore = Lakeshore()
        self.quarz = InficonSQM160()
        try:
            self.run_measurement()            
        except KeyboardInterrupt:
            self.finish_measurement()
        finally:
            self.finish_measurement()

    def run_measurement(self):
        counter = 0
        fig = plt.figure()
        ax = fig.add_subplot(211)
        ax1 = fig.add_subplot(212)
        start_time = time.time()
        x = [] # times
        T = [] # Temperatures
        R = [] # Resistances
        Depot = [] # Deposit rate
        while 1:
            counter += 1
            time_elapsed = time.time() - start_time
            temp =   self.lakeshore.read_temp()
            meterV = self.meter.read_voltage()
            meterI = self.meter.read_current()
            resist = meterV/meterI
            deposit_rate = self.quarz.measure_rate()
            x.append(time_elapsed)
            T.append(temp)
            R.append(resist)
            Depot.append(deposit_rate)
            absolute_deposit = np.array(x)*np.array(T)
            self.savefile.write('{}, {}, {}, {} \n'\
            .format(time_elapsed, temp, resist, deposit_rate))
            time.sleep(1)
            # Plot in real time
            ax.plot(x, T, 'k.')
            ax.plot(x, R, 'r.')
            ax.plot(x, absolute_deposit, 'b.')
            ax.set_xlabel('Time [s]')
            ax.set_ylabel('Values')

            ax1.plot(absolute_deposit, R, 'k.')
            ax1.set_xlabel('Absolute Deposit [A]')
            ax1.set_ylabel('Resistance [Ohm]')
            # plt.xlabel('test, test')
            plt.tight_layout()
            plt.draw()
            plt.pause(0.01)

if __name__ == '__main__':
    q = Quarz()



