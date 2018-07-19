# __author__ = Yannic Falke

from keithley_class import *


class Gatesweep():
    def __init__(self):
        self.gate = Gate(2)
        self.meter = Meter(1)
        self.lakeshore = Lakeshore()
        savestring = \
        '# gatevoltage(V), temp(K), voltage(V), current(A), R_4pt(W), I_gate(A)'
        self.create_savefile(savestring)
        self.ask_parameters()
        self.init_ramp_parameters()
        try:
            self.start_gatesweep()            
        except KeyboardInterrupt:
            self.finish_measurement()
            sys.exit()

    def init_ramp_parameters(self):
        ''' Initializes counters, necessary for self.ramp_gatevoltage() '''
        self.gatevoltage = 0
        self.lastvoltage = 0
        self.finishedcounter = 0
        self.maxcounter = 0

    def ramp_gatevoltage(self):
        ''' Increments the gatevoltage and finishes the measurement,
        when it is over
        '''
        if self.gatevoltage < self.maxvoltage and \
        self.gatevoltage >= self.lastvoltage:
            self.lastvoltage = self.gatevoltage
            self.gatevoltage += self.stepsize
        elif self.gatevoltage == self.maxvoltage:
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

    def finish_measurement(self):
        ''' Close all Keithleys or Lakeshore devices, close savefile '''
        print("Finished measurement successfully. Closing all devices\
        and savefile.")
        # keithley2.write(':SOUR:CURR:LEV 0.00000')  #Set current source to 0 uA
        # keithley1.write(':SOUR:VOLT:LEV 0.00000')
        self.savefile.close()
        for i in Keithley.instances:
            i.close()
        self.lakeshore.close()
        print('Successfully closed everything. Exiting...')
        sys.exit()

    def create_savefile(self,savestring):
        ''' Creates savefile based savestring '''
        savefolder = str(input('Input name of DIRECTORY: ') or 'testfolder') 
        savename = str(input('Input name of FILENAME: ') or 'testfile')
        if not savename[-4] == '.':
            savename += ".dat"
        if not os.path.exists(savefolder):
            os.makedirs(savefolder)
        os.chdir(savefolder)
        if os.path.isfile(savename):
            choice = str(input("File already exists. Do you want to rename? [y/n] ")\
            or "n")
            if choice == 'y':
                savename = input("New filename: ")
                if not "." in savename:
                    savename += ".dat"
            if choice == 'n':
                i = 1
                save_tmp = savename.split('.')[0]
                while os.path.isfile(save_tmp + "_{}.dat".format(i)):
                    i += 1
                savename = save_tmp + "_{}.dat".format(i)
        print("savename is: {}".format(savename))
        thefile = open(savename, "w")
        thefile.write(savestring + "\n")
        self.savefile = thefile
        

    def ask_parameters(self):
        ''' Define measurement range based on CLI user input '''
        self.maxvoltage = float(input('Set MAXvoltage (standard is 40, if not defined): ') or 40)
        self.minvoltage = float(input('Set MINvoltage (standard is -40, if not defined): ') or -40)
        self.stepsize = float(input('Set stepsize (standard is 0.5, if not defined): ') or 0.5)



    def start_gatesweep(self):
        # benchslope = False
        x = []
        y = []
        r = []
        fig = plt.figure()
        plt.xlabel("Gatevoltage [V]")
        plt.ylabel("Current / Resistance")
        while 1:
            # Set gatevoltage and measure values
            print('Gatevoltage = {}'.format(self.gatevoltage))
            self.gate.set_gatevoltage(self.gatevoltage)  #Set voltage 
            time.sleep(0.1)
            meterV = self.meter.read_voltage()      #first measurement is voltage
            meterI = self.meter.read_current()     #second measurement is current
            temp=self.lakeshore.read_temp()

            # Plot values in real time
            time.sleep(0.1)
            x.append(self.gatevoltage)
            y.append(meterI)
            r.append(meterV/meterI)
            plt.plot(x, y, 'k.',label='Current')
            plt.plot(x, r, 'r.',label='Resistance')
            plt.legend()
            plt.draw()
            plt.pause(0.01)

            # Write values to file
            writedict = {
            'Gatevoltage' : self.gatevoltage,
            'T': temp,
            'V': meterV,
            'I': meterI,
            'R': meterV/meterI,
            # 'I_gate': gatecurrent,
            }
            for i in writedict:
                self.savefile.write('{} ,'.format(str(writedict[i]).strip()))
            self.savefile.write("\n")

            # Set gatevoltage to next value
            self.ramp_gatevoltage()

            
if __name__ == '__main__':
    gs = Gatesweep()


    
