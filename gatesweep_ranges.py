# __author__ = Yannic Falke

from Classes.device_classes import *
from Classes.measurement_class import Measurement


class Gatesweep(Measurement):
    def __init__(self):
        self.gate = Gate(1)
        self.meter = Meter(2)
        self.lakeshore = Lakeshore()
        self.ask_savename()
        self.ask_parameters()
        self.wait_max = self.ask_wait_at_maxvals()
        savestring = \
        '# gatevoltage(V), temp(K), voltage(V), current(A), R_4pt(W)'
        self.create_savefile(savestring)
        self.init_ramp_parameters()
        try:
            self.start_gatesweep()            
        except KeyboardInterrupt:
            self.finish_measurement()

    def init_ramp_parameters(self):
        ''' Initializes counters, necessary for self.ramp_gatevoltage() '''
        self.gatevoltage = 0
        self.lastvoltage = 0
        self.finishedcounter = 0
        self.maxcounter = 0
        self.reached_max = False

    def ramp_gatevoltage(self):
        ''' Increments the gatevoltage and finishes the measurement '''
        if self.gatevoltage < self.maxvoltage and \
        self.gatevoltage >= self.lastvoltage:
            self.lastvoltage = self.gatevoltage
            self.gatevoltage += self.stepsize
        elif self.gatevoltage == self.maxvoltage:
            if self.wait_max:
                time.sleep(30)
            self.lastvoltage = self.gatevoltage
            self.gatevoltage -= self.stepsize
            self.maxcounter += 1
        elif self.gatevoltage > self.minvoltage and \
        self.gatevoltage < self.lastvoltage:
            self.lastvoltage = self.gatevoltage
            self.gatevoltage -= self.stepsize
        elif self.gatevoltage == self.minvoltage:
            self.lastvoltage = self.gatevoltage
            self.gatevoltage += self.stepsize
            self.maxcounter += 1
        if self.maxvoltage >= 0 and self.minvoltage >= 0:
            if self.maxcounter == 2:
                self.finish_measurement()
        if self.gatevoltage == 0 :
            self.finishedcounter += 1
            if self.finishedcounter == 2:
                self.finish_measurement()
    
    def ramp_range(self):
        if self.reached_max == False:
            if self.gatevoltage < self.maxvoltage:
                self.gatevoltage += self.stepsize
            if self.gatevoltage >= self.maxvoltage:
                self.reached_max = True
        if self.reached_max == True:
            if self.maxcounter == 0:
                self.gatevoltage = 0
                self.maxcounter += 1
                print('Sleeping for 20 seconds at 0 Voltage')
                time.sleep(10)
                print('Setting Gate to {}'.format(self.maxvoltage))
                self.gatevoltage = self.maxvoltage
            else:
                if self.gatevoltage > self.minvoltage:
                    self.gatevoltage -= self.stepsize
                if self.gatevoltage <= self.minvoltage:
                    self.finish_measurement()

 

    def benchmark_slope(self, x,y):
        """ Uses first few measurement points to generate initial slope.
            CURRENTLY NOT IN USE   
        """
        x = np.asarray(x)
        y = np.asarray(y)
        if len(x) > 5:
            slope, b = np.polyfit(x[:5],y[:5],1) 
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
        slope, b = np.polyfit(x[-2:],y[-2:],1)
        if slope > saveval*benchslope:
            print("Measured slope exceeds save value. Stopping Program...")
            # plt.plot(x[-2:], linear(x[-2:], slope, b), 'r-')
            return False
        else:
            return True

    def ask_parameters(self):
        ''' Define measurement range based on CLI user input '''
        self.maxvoltage = float(input('Set MAXvoltage (standard is 40, if not defined): ') or 40)
        self.minvoltage = float(input('Set MINvoltage (standard is -40, if not defined): ') or -40)
        self.stepsize = float(input('Set stepsize (standard is 0.5, if not defined): ') or 0.5)
        self.waittime = float(input('Set wait time after each step (standard is 10 sec, if not defined): ') or 10)
        # Calculate total time, that measurement will take in SEC
        if self.minvoltage < 0:
            total_time_sec =\
             ((self.maxvoltage/self.stepsize) +\
             (self.maxvoltage - self.minvoltage)/self.stepsize +\
             (abs(self.minvoltage)/self.stepsize)
             )*self.waittime
        else:
            total_time_sec =\
             ((self.maxvoltage/self.stepsize) +\
             (self.maxvoltage - self.minvoltage)/self.stepsize\
             )*self.waittime 
        total_time_min = round(total_time_sec/60,2)
        print('This measurement will take {} minutes.'.format(total_time_min))


    def ask_wait_at_maxvals(self):
        ''' Should max voltage be kept for certain time? '''
        wait_max = str(input('Do you want to hold the maximum voltage for 30 sec? (y/n): ') or 'n').lower()
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
        ax1 = fig.add_subplot(212)
        ax1.set_xlabel("Gatevoltage [V]")
        ax.set_ylabel("Resistance [Ohm]")
        ax1.set_ylabel("Gatecurrent [A]")
        print('Setting Gatevoltage to {}'.format(self.minvoltage))
        self.gatevoltage = self.minvoltage
        self.gate.set_voltage(self.gatevoltage)
        while 1:
            # Set gatevoltage and measure values
            print('Gatevoltage = {}'.format(self.gatevoltage))
            self.gate.set_voltage(self.gatevoltage)  
            time.sleep(self.waittime)
            meterV = self.meter.read_voltage() 
            meterI = self.meter.read_current() 
            temp=self.lakeshore.read_temp()
            gatecurrent = self.gate.read_current()

            # Plot values in real time
            # time.sleep(0.1)
            x.append(self.gatevoltage)
            y.append(meterV)
            r.append(meterV/meterI)
            gc.append(gatecurrent)

            ax.plot(x, r, 'k.')
            ax1.plot(x, gc, 'k.')
            plt.draw()
            plt.pause(0.01)

            # Write values to file
            writedict = {
            'Gatevoltage' : self.gatevoltage,
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
            self.ramp_range()

            
if __name__ == '__main__':
    gs = Gatesweep()


    
