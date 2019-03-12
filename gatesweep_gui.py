# __author__ = Yannic Falke

import sys
import pyqtgraph as pg
from PyQt5 import QtCore, uic
from PyQt5.QtWidgets import (
    QMainWindow,
    QApplication,
    QLabel,
    QFileDialog
    )
from Classes.device_classes import *
from Classes.measurement_class import Measurement

class MainWindow(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        start = time.time()
        self.UI = uic.loadUi('Gatesweep.ui', self)
        print('loaded ui in {}'.format(time.time() - start))
        self.init_port_selection()
        self.init_connect_buttons()
        self.init_save()
        #GS = Gatesweep(Measurement)
        self.show()

    def closeEvent(self, event):
        for i in Keithley.instances:
            i.close()
        for i in Lockin.instances:
            i.close()
        for i in Lakeshore.instances:
            i.close()
        print('Closed Controllers. Goodbye!')

    def init_graph(self):
        self.graphicsview = self.UI.GSView
        p = pg.mkPen(color=(63, 117, 204), width=2)
        self.graph = self.graphicsview.addPlot(row=1, col=1)
        self.graph_lower = self.graphicsview.addPlot(row=2, col=1)
        self.plot = self.graph.plot(pen=p)
        self.plot_lower = self.graph_lower.plot(pen=p)
        self.graph.setAutoVisible(y=True)
        self.graph.enableAutoRange('x')
        self.graph.enableAutoRange('y')
        #self.graph.showGrid(y=True,x=True)
        self.graph.showAxis("right")
        self.graph.getAxis("right").tickStrings = lambda x,y,z: ["" for value in x]
        self.graph.showAxis("top")
        self.graph.getAxis("top").tickStrings = lambda x,y,z: ["" for value in x]
        self.graph.setTitle('Gatesweep')
        self.graph.setLabel("left", "Resistance [Ohm]")
        self.graph.setLabel("bottom", "Gatevoltage [V]")

        self.graph_lower.setAutoVisible(y=True)
        self.graph_lower.enableAutoRange('x')
        self.graph_lower.enableAutoRange('y')
        #self.graph_lower.showGrid(y=True,x=True)
        self.graph_lower.showAxis("right")
        self.graph_lower.getAxis("right").tickStrings = lambda x,y,z: ["" for value in x]
        self.graph_lower.showAxis("top")
        self.graph_lower.getAxis("top").tickStrings = lambda x,y,z: ["" for value in x]
        self.graph_lower.setTitle('Leakage')
        self.graph_lower.setLabel("left", "Gatecurrent [A]")
        self.graph_lower.setLabel("bottom", "Gatevoltage [V]")
    def init_save(self):
        ''' Connects save button and sets default savename '''
        self.UI.SavenameButton.released.connect(self.choose_savename)
        savefolder = 'testfolder'
        if not os.path.isdir(savefolder):
            os.mkdir(savefolder)
        os.chdir(savefolder)
        savename = 'testfile.dat'
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
        self.savename = QFileDialog.getSaveFileName(
                self, 'Choose Savename', '.', self.tr("Text Files (*.dat)"))[0]
        self.UI.SavenameLabel.setText(self.savename)

    def init_port_selection(self):
        rm = visa.ResourceManager()
        ports = rm.list_resources()
        for port in ports:
            if 'GP' in port:
                add = port.split('::')[1]
                self.UI.GatePortBox.addItem(add)
                self.UI.KMeterPortBox.addItem(add)
                self.UI.LMeterPortBox.addItem(add)

        # Set standard values
        gateind = self.UI.GatePortBox.findText('1')
        if gateind != -1:
            self.UI.GatePortBox.setCurrentIndex(gateind)

        lockinind = self.UI.LMeterPortBox.findText('8')
        if lockinind != -1:
            self.UI.LMeterPortBox.setCurrentIndex(lockinind)

        kmeterind = self.UI.KMeterPortBox.findText('2')
        if kmeterind != -1:
            self.UI.KMeterPortBox.setCurrentIndex(kmeterind)

    def init_connect_buttons(self):
        self.UI.GateConnectButton.released.connect(self.init_gate)
        self.UI.KMeterConnectButton.released.connect(self.init_kmeter)
        self.UI.LMeterConnectButton.released.connect(self.init_lmeter)
        self.UI.StartGSButton.released.connect(self.start_gatesweep)

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


    def start_gatesweep(self):
        self.init_graph()
        minvoltage = self.UI.MinGateBox.value()
        maxvoltage = self.UI.MaxGateBox.value()
        stepsize = self.UI.StepsizeBox.value()
        waittime = self.UI.WaittimeBox.value()
        wait_max = True if self.UI.MaxCheckbox.isChecked() else False
        wait_max_time = self.UI.WaitmaxBox.value()
        savefile = self.savename
        self.gs = Gatesweep(self.gate, self.meter, minvoltage, maxvoltage,
                stepsize, waittime, wait_max, wait_max_time, savefile,
                self.plot, self.plot_lower)
        # Also connect abort button now
        self.UI.StopGSButton.released.connect(self.gs.stop_gs)

        self.thread = QtCore.QThread(self)
        self.gs.finished_gs.connect(self.gs_callback)
        self.gs.moveToThread(self.thread)
        self.thread.started.connect(self.gs.start)
        self.UI.GatesweepLabel.setText('Measuring!')
        self.UI.GatesweepLabel.setStyleSheet('color: red')
        self.thread.start()

    def gs_callback(self):
        self.UI.GatesweepLabel.setText('Idle')
        self.UI.GatesweepLabel.setStyleSheet('color: black')


class Gatesweep(QtCore.QObject):
    finished_gs = QtCore.pyqtSignal(bool)
    def __init__(self, gate, meter, minvoltage, maxvoltage, stepsize, waittime,
            wait_max, wait_max_time, savename, plot, plot_lower):
        QtCore.QObject.__init__(self)
        self.gate = gate
        self.meter = meter
        self.lakeshore = Lakeshore()
        self.minvoltage = minvoltage
        self.maxvoltage = maxvoltage
        self.stepsize = stepsize
        self.waittime = waittime
        self.wait_max = wait_max
        self.wait_max_time = wait_max_time
        self.savename = savename
        self.plot = plot
        self.plot_lower = plot_lower
        savestring = \
                '# gatevoltage(V), temp(K), voltage(V), current(A), R_4pt(W)'
        self.create_savefile(savestring)
        self.init_ramp_parameters()

    def create_savefile(self, savestring):
        ''' Creates savefile and generates header '''
        self.savefile = open(self.savename, "w")
        self.savefile.write(savestring + "\n")


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

    @QtCore.pyqtSlot()
    def start(self):
        self.start_gatesweep()
        self.finished_gs.emit(True)

    def start_gatesweep(self):
        self.measuring = True
        x = []
        y = []
        r = []
        gc = []
        while self.measuring:
            # Set gatevoltage and measure values
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

            self.plot.setData(x, r)
            self.plot_lower.setData(x, gc)

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

        # After finishing, plot it once in mpl
        fig = plt.figure()
        basename = os.path.basename(self.savename)
        plt.title(basename)
        ax = fig.add_subplot(211)
        ax1 = fig.add_subplot(212)
        ax.set_ylabel(r'Resistance [$\Omega$]')
        ax1.set_xlabel('Gatevoltage [V]')
        ax1.set_ylabel('Gatecurrent [A]')
        ax.plot(x, r, 'k.')
        ax1.plot(x, gc, 'k.')
        # save figure file as png
        savename_png = os.path.splitext(self.savename)[0] + '.png'
        plt.savefig(savename_png)

    def stop_gs(self):
        self.measuring = False


if __name__ == '__main__':
    qApp = QApplication(sys.argv)
    aw = MainWindow()
    aw.show()
    sys.exit(qApp.exec_())
