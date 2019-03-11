# __author__ = Yannic Falke

import pyqtgraph as pg
from PyQt5 import QtCore, uic
from PyQt5.QtWidgets import (
    QMainWindow,
    QApplication,
    QLabel
    )
from Classes.device_classes import *
from Classes.measurement_class import Measurement

class MainWindow(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        self.UI = uic.loadUi('Gatesweep.ui')
        self.init_port_selection()
        self.init_connect_buttons()
        #GS = Gatesweep(Measurement)
        self.show()

    def init_save(self):
        ''' Connects save button and sets default savename '''
        self.UI.SavenameButton.connect(self.choose_savename)
        savefolder = 'testfolder'
        os.chdir(savefolder)
        savename = 'testfile'
        if os.path.isfile(savename):
            i = 1
            save_tmp = savename.split('.')[0]
            while os.path.isfile(save_tmp + "_{}.dat".format(i)):
                i += 1
            savename = save_tmp + "_{}.dat".format(i)
        os.chdir('../')
        savepath = savefolder + '/' + savename
        self.savename = savepath
        self.UI.SavenameLabel.setText(savepath)

    def choose_savename(self):
        self.savename = QFileDialog.getSaveFileName(self, 'Choose Savename')

    def init_port_selection(self):
        ports = serial.tools.list_ports_windows.comports()
        #ports = serial.list_ports
        for port in ports:
            self.UI.GatePortBox.addItem(port)
            self.UI.KMeterPortBox.addItem(port)
            self.UI.LMeterPortBox.addItem(port)

    def init_connect_buttons(self):
        self.UI.GateConnectButton.connect(self.init_gate)
        self.UI.KMeterConnectButton.connect(self.init_kmeter)
        self.UI.LMeterConnectButton.connect(self.init_lmeter)

    def label_connected(self, label):
        label.setText('Connected')
        label.setStyleSheet('color: green')

    def label_failed(self, label):
        label.setText('Failed')
        label.setStyleSheet('color: red')

    def label_idle(self, label):
        label.setText('Disconnected')
        label.setStyleSheet('color: black')

    def init_gate(self):
        port = self.UI.GatePortBox.currentText()
        try:
            self.gate = Gate(port)
            self.label_connected(self.UI.GateLabel)
        except:
            self.label_failed(self.UI.GateLabel)

    def init_kmeter(self):
        port = self.UI.KMeterPortBox.currentText()
        try:
            self.meter.close()
            self.label_idle(self.UI.LMeterLabel)
        except:
            pass
        try:
            self.meter = Meter(port)
            self.label_connected(self.UI.KMeterLabel)
        except:
            self.label_failed(self.UI.KMeterLabel)

    def init_lmeter(self):
        port = self.UI.LMeterPortBox.currentText()
        try:
            self.meter.close()
            self.label_idle(self.UI.KMeterLabel)
        except:
            pass
        try:
            self.meter = Lockin(port)
            self.label_connected(self.UI.LMeterLabel)
        except:
            self.label_failed(self.UI.LMeterLabel)

    def init_gs_buttons(self):
        self.UI.StartGSButton.connect(self.start_gatesweep)

    def start_gatesweep(self):
        minvoltage = self.UI.MingateBox.value()
        maxvoltage = self.UI.MaxgateBox.value()
        stepsize = self.UI.StepsizeBox.value()
        waittime = self.UI.WaittimeBox.value()
        wait_max = True if self.UI.MaxCheckbox.isChecked() else False
        wait_max_time = self.UI.WaitmaxBox.value()
        savefile = self.savename
        #self.gs = Gatesweep(self.gate, self.meter, minvoltage, maxvoltage,
                #stepsize, waittime, wait_max, wait_max_time, savefile)

class Gatesweep(Measurement):
    def __init__(self, gate, meter, minvoltage, maxvoltage, stepsize, waittime,
            wait_max, wait_max_time, savefile):
        self.gate = gate
        self.meter = meter
        self.lakeshore = Lakeshore()
        self.minvoltage = minvoltage
        self.maxvoltage = maxvoltage
        self.stepsize = stepsize
        self.waittime = waittime
        self.wait_max = wait_max
        self.wait_max_time = wait_max_time
        self.savefile = savefile
        savestring = \
            '# gatevoltage(V), temp(K), voltage(V), current(A), R_4pt(W)'
        self.create_savefile(savestring)
        self.init_ramp_parameters()
        try:
            self.start_gatesweep()
        except KeyboardInterrupt:
            self.finish_measurement()

    def create_savefile(self, savestring):
        ''' Creates savefile and generates header '''
        self.savefile = open(self.savename, "w")
        self.savefile.write(savestring + "\n")

    def finish_measurement(self):
        ''' Close all Keithleys or Lakeshore devices, close savefile '''
        self.gate.set_gatevoltage(0)
        print("Finished measurement successfully. Closing all devices\
        and savefile.")
        self.savefile.close()
        for i in Keithley.instances:
            i.close()
        for i in Lakeshore.instances:
            i.close()
        if plt.get_fignums():
            # If plots exists, then save them
            print('Saving a PNG of the measurement...')
            plt.savefig(self.savename_png)
        else:
            pass

    def init_ramp_parameters(self):
        ''' Initializes counters, necessary for self.ramp_gatevoltage() '''
        self.gatevoltage = 0
        self.lastvoltage = 0
        self.finishedcounter = 0
        self.maxcounter = 0

    def ramp_gatevoltage(self):
        ''' Increments the gatevoltage and finishes the measurement '''
        if self.gatevoltage < self.maxvoltage and \
                self.gatevoltage >= self.lastvoltage:
            self.lastvoltage = self.gatevoltage
            self.gatevoltage += self.stepsize
        elif self.gatevoltage == self.maxvoltage:
            if self.wait_max:
                time.sleep(self.wait_max_time) # wait at max voltage
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
        if self.gatevoltage == 0:
            self.finishedcounter += 1
            if self.finishedcounter == 2:
                self.finish_measurement()

    def start_gatesweep(self):
        x = []
        y = []
        r = []
        gc = []
        fig = plt.figure()
        ax = fig.add_subplot(211)
        ax1 = fig.add_subplot(212)
        while 1:
            # Set gatevoltage and measure values
            print('Gatevoltage = {}'.format(self.gatevoltage))
            self.gate.set_gatevoltage(self.gatevoltage)
            time.sleep(self.waittime)
            meterV = self.meter.read_voltage()
            meterI = self.meter.read_current()
            temp = self.lakeshore.read_temp()
            gatecurrent = self.gate.read_current()

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
                'Gatevoltage': self.gatevoltage,
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
    qApp = QApplication(sys.argv)
    aw = MainWindow()
    aw.show()
    sys.exit(qApp.exec_())
