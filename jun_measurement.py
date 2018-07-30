# __author__ = Yannic Falke

from device_classes import *
from measurement_class import Measurement


class TwoPt_Jun(Measurement):
    def __init__(self):
        self.gate = Gate(1)
        self.meter = Meter(2, four_wire=False)
        self.lakeshore = Lakeshore()
        self.ask_savename()
        savestring = \
        '# Time [s], Temperature [K], Resistance [Ohm]'
        self.create_savefile(savestring)
        try:
            self.log_data()            
        except KeyboardInterrupt:
            self.finish_measurement()

    def log_data(self):
        r = []
        t = []
        start_time = time.time()
        fig = plt.figure()
        ax = fig.add_subplot(211)
        ax1 = fig.add_subplot(212)
        ax.xlabel("Time [s]")
        ax.ylabel("Resistance [Ohm]")
        ax1.ylabel("Temperature [K]")
        while 1:
            time.sleep(1)
            time_elapsed = time.time() - start_time
            meterV = self.meter.read_voltage() 
            meterI = self.meter.read_current() 
            temp = self.lakeshore.read_temp()

            # Plot values in real time
            r.append(meterV/meterI)
            ax.plot(t, r, 'r.')
            ax1.plot(t, temp, 'k.')
            
            plt.tight_layout()
            plt.draw()
            plt.pause(0.01)

            self.savefile.write('{}, {}, {} \n'.format(time_elapsed, temp, r))


            
if __name__ == '__main__':
    gs = TwoPt_Jun()


    
