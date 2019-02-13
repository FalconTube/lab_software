# __author__ = Yannic Falke

from Classes.device_classes import *
from Classes.measurement_class import Measurement


class Gatesweep(Measurement):
    def __init__(self):
        self.gate = Gate(1)
        self.meter = Meter(2, four_wire=False, set_source_voltage=True)
        self.lakeshore = Lakeshore()
        self.ask_savename()
        self.ask_parameters()
        self.wait_max = self.ask_wait_at_maxvals()
        savestring = \
            '# gatevoltage(V), temp(K), voltage(V), current(A), R(Ohm), Gatecurrent(A)'
        self.create_savefile(savestring)
        self.init_ramp_parameters()
        try:
            self.start_gatesweep()
        except KeyboardInterrupt:
            self.gate.set_gatevoltage(0)
            self.finish_measurement()

    def init_ramp_parameters(self):
        ''' Initializes counters, necessary for self.ramp_gatevoltage() '''
        self.metervoltage = 0
        self.lastvoltage = 0
        self.finishedcounter = 0
        self.maxcounter = 0

    def ramp_gatevoltage(self):
        ''' Increments the gatevoltage and finishes the measurement '''
        self.metervoltage = round(self.metervoltage, self.precision)
        if self.metervoltage < self.maxvoltage and \
                self.metervoltage >= self.lastvoltage:
            self.lastvoltage = self.metervoltage
            self.metervoltage += self.stepsize
        elif self.metervoltage == self.maxvoltage:
            if self.wait_max:
                time.sleep(30)  # wait at max voltage
            self.lastvoltage = self.metervoltage
            self.metervoltage -= self.stepsize
            self.maxcounter += 1
        elif self.metervoltage > self.minvoltage and \
                self.metervoltage < self.lastvoltage:
            self.lastvoltage = self.metervoltage
            self.metervoltage -= self.stepsize
        elif self.metervoltage == self.minvoltage:
            self.lastvoltage = self.metervoltage
            self.metervoltage += self.stepsize
            self.maxcounter += 1
        if self.maxvoltage >= 0 and self.minvoltage >= 0:
            if self.maxcounter == 2:
                self.finish_measurement()
        if self.metervoltage == 0:
            self.finishedcounter += 1
            if self.finishedcounter == 2:
                self.finish_measurement()
        self.metervoltage = round(self.metervoltage, self.precision)

    def benchmark_slope(self, x, y):
        """ Uses first few measurement points to generate initial slope.
            CURRENTLY NOT IN USE
        """
        x = np.asarray(x)
        y = np.asarray(y)
        if len(x) > 5:
            slope, b = np.polyfit(x[:5], y[:5], 1)
            plt.plot(x[:5], self.linear(x[:5], slope, b), 'g-')
            return slope
        else:
            return False

    def linear(self, x, m, b):
        ''' Return linear function '''
        return m*x + b

    def check_slope(self, x, y, benchslope, saveval):
        """ Checks, if the slope exceeds a given value. If this is the case,
            it stops the program and prompts user to take action.
            CURRENTLY NOT IN USE
        """
        slope, b = np.polyfit(x[-2:], y[-2:], 1)
        if slope > saveval*benchslope:
            print("Measured slope exceeds save value. Stopping Program...")
            # plt.plot(x[-2:], linear(x[-2:], slope, b), 'r-')
            return False
        else:
            return True

    def ask_parameters(self):
        ''' Define measurement range based on CLI user input '''
        self.gate_voltage = float(self._cache.cache_input(
            'Set GATEvoltage (standard is 10, if not defined): ', 10))
        self.maxvoltage = float(self._cache.cache_input(
            'Set MAXvoltage (standard is 40, if not defined): ', 40))
        self.minvoltage = float(self._cache.cache_input(
            'Set MINvoltage (standard is -40, if not defined): ', -40))
        self.stepsize = float(self._cache.cache_input(
            'Set stepsize (standard is 0.5, if not defined): ', 0.5))
        self.waittime = float(self._cache.cache_input(
            'Set wait time after each step (standard is 0 sec, if not defined): ', 0))
        # Calculate total time, that measurement will take in SEC
        self.precision = len(str(self.stepsize).split('.')[-1])
        if self.minvoltage < 0:
            total_time_sec = ((self.maxvoltage/self.stepsize) +
                              (self.maxvoltage - self.minvoltage)/self.stepsize +
                              (abs(self.minvoltage)/self.stepsize)
                              )*self.waittime
        else:
            total_time_sec = ((self.maxvoltage/self.stepsize) +
                              (self.maxvoltage - self.minvoltage)/self.stepsize
                              )*self.waittime
        total_time_min = round(total_time_sec/60, 3)
        print('This measurement will take {} minutes.'.format(total_time_min))

    def ask_wait_at_maxvals(self):
        ''' Should max voltage be kept for certain time? '''
        wait_max = str(self._cache.cache_input(
            'Do you want to hold the maximum voltage for 30 sec? (y/n): ', 'n').lower())
        if wait_max == 'y':
            print('I will wait at Gatevoltage = {}'.format(self.maxvoltage))
            return True
        else:
            return False

    def start_gatesweep(self):
        # benchslope = False
        x = []
        y = []
        r = []
        gc = []
        fig = plt.figure()
        ax = fig.add_subplot(211)
        ax.set_xlabel('Meter Voltage [V]')
        ax.set_ylabel('Resistance [Ohm]')
        ax1 = fig.add_subplot(212)
        ax1.set_ylabel('Gatecurrent [A]')
        self.gate.set_gatevoltage(self.gate_voltage)
        plt.tight_layout()
        while 1:
            # Set gatevoltage and measure values
            print('Gatevoltage = {}'.format(self.metervoltage))
            self.meter.set_voltage(self.metervoltage)
            time.sleep(self.waittime)
            meterV = self.meter.read_voltage()
            meterI = self.meter.read_current()
            temp = self.lakeshore.read_temp()
            gatecurrent = self.gate.read_current()

            # Plot values in real time
            x.append(self.metervoltage)
            y.append(meterV)
            r.append(meterV/meterI)
            gc.append(gatecurrent)
            

            ax.plot(x, r, 'k.')
            ax1.plot(x, gc, 'k.')
            plt.draw()
            plt.pause(0.01)
            # Write values to file
            writedict = {
                'Gatevoltage': self.gate_voltage,
                'T': temp,
                'V': meterV,
                'I': meterI,
                'R': meterV/meterI,
                'I_gate': gatecurrent,
            }
            for i in writedict:
                self.savefile.write('{} ,'.format(str(writedict[i]).strip()))
            self.savefile.write("\n")

            # Set gatevoltage to next value
            self.ramp_gatevoltage()
        # save figure file as png
        # figname = fn.split('.')[0] + '_mobility.png'
        # plt.savefig(self.savename_png)


if __name__ == '__main__':
    gs = Gatesweep()