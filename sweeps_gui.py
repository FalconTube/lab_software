# __author__ = Yannic Falke

import sys
import pyqtgraph as pg
from PyQt5 import QtCore, uic
from PyQt5.QtMultimedia import QMediaPlayer, QMediaPlaylist, QMediaContent
from PyQt5.QtWidgets import (
    QMainWindow,
    QApplication,
    QLabel,
    QFileDialog,
    )
from Classes.device_classes import *
from Classes.measurement_class import Measurement

class MainWindow(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        self.UI = uic.loadUi('Sweeps_gui.ui', self)
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
        # for i in Lakeshore.instances:
            # i.close()
        print('Closed Controllers. Goodbye!')


    def init_graph(self, axes, single=False):
        self.graphicsview = self.UI.GSView
        xlabel, y_uplabel, y_lowlabel = axes
        try:
            self.graphicsview.removeItem(self.graph)
            self.graphicsview.removeItem(self.graph_lower)
        except:
            pass
        p = pg.mkPen(color=(63, 117, 204), width=2)
        self.graph = self.graphicsview.addPlot(row=1, col=1)
        self.plot = self.graph.plot(pen=p)
        self.graph.setAutoVisible(y=True)
        self.graph.enableAutoRange('x')
        self.graph.enableAutoRange('y')
        #self.graph.showGrid(y=True,x=True)
        self.graph.showAxis("right")
        self.graph.getAxis("right").tickStrings = lambda x,y,z: ["" for value in x]
        self.graph.showAxis("top")
        #self.graph.getAxis("top").tickStrings = lambda x,y,z: ["" for value in x]
        #self.graph.setTitle('Gatesweep')
        self.graph.setLabel("left", y_uplabel)
        self.graph.setLabel("bottom", xlabel)

        if not single:
            self.graph_lower = self.graphicsview.addPlot(row=2, col=1)
            self.plot_lower = self.graph_lower.plot(pen=p)
            self.graph_lower.setAutoVisible(y=True)
            self.graph_lower.enableAutoRange('x')
            self.graph_lower.enableAutoRange('y')
            #self.graph_lower.showGrid(y=True,x=True)
            self.graph_lower.showAxis("right")
            self.graph_lower.getAxis("right").tickStrings = lambda x,y,z: ["" for value in x]
            self.graph_lower.showAxis("top")
            self.graph_lower.getAxis("top").tickStrings = lambda x,y,z: ["" for value in x]
            #self.graph_lower.setTitle('Leakage')
            self.graph_lower.setLabel("left", y_lowlabel)
            self.graph_lower.setLabel("bottom", xlabel)

    def init_save(self, savepath=None):
        ''' Connects save button and sets default savename '''
        if savepath == None:
            savefolder = 'testfolder/'
            if not os.path.isdir(savefolder):
                os.mkdir(savefolder)
            savepath = savefolder + 'testfile.dat'
        if os.path.isfile(savepath):
            i = 1
            save_tmp = savepath.split('.')[0]
            while os.path.isfile(save_tmp + "_{}.dat".format(i)):
                i += 1
            savepath = save_tmp + "_{}.dat".format(i)
        self.savename = savepath
        self.UI.SavenameLabel.setText(savepath)

    def choose_savename(self):
        old_name = self.savename
        self.savename = QFileDialog.getSaveFileName(
                self, 'Choose Savename', '.', self.tr("Text Files (*.dat)"))[0]
        if self.savename == '':
            self.savename = old_name
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
        self.UI.StartSweepButton.released.connect(self.start_sweep)
        self.UI.SavenameButton.released.connect(self.choose_savename)
        self.UI.StartResButton.released.connect(self.start_resmeas)
        self.UI.AutoGainButton.released.connect(self.set_autogain_time)
        self.UI.FixedGateBox.valueChanged.connect(self.change_gate_voltage)

    def label_init(self, label):
        label.setText('Initializing...')
        label.setStyleSheet('color: blue')

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
        QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)
        port = self.UI.GatePortBox.currentText()
        compliance = self.UI.GateComplianceBox.value()
        fixed_volt = self.UI.FixedGateBox.value()
        try:
            self.label_init(self.UI.GateLabel)
            self.gate = Gate(port, compliance)
            self.gate.slowly_to_target(fixed_volt, voltage=True)
            self.label_connected(self.UI.GateLabel)
        except ValueError:
            self.label_failed(self.UI.GateLabel)
        QApplication.restoreOverrideCursor()

    def init_kmeter(self):
        QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)
        port = self.UI.KMeterPortBox.currentText()
        fwire = True if self.UI.WireCheckBox.isChecked() else False
        source_volt = True if self.UI.SourceVoltsRadio.isChecked() else False
        source_val = self.UI.SourceValBox.value()
        speed = self.UI.SpeedBox.value()
        try:
            self.meter.close()
            self.label_idle(self.UI.LMeterLabel)
        except:
            pass
        try:
            self.label_init(self.UI.KMeterLabel)
            self.meter = Meter(port, source_val, fwire, source_volt, speed)
            self.label_connected(self.UI.KMeterLabel)
        except ValueError:
            self.label_failed(self.UI.KMeterLabel)
        QApplication.restoreOverrideCursor()

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


    def start_sweep(self):
        minvoltage = self.UI.MinSweepBox.value()
        maxvoltage = self.UI.MaxSweepBox.value()
        stepsize = self.UI.StepsizeBox.value()
        waittime = self.UI.WaittimeBox.value()
        wait_max = True if self.UI.MaxCheckbox.isChecked() else False
        wait_max_time = self.UI.WaitmaxBox.value()
        fwire = True if self.UI.WireCheckBox.isChecked() else False
        # Check if file exists again, user could not have changed old one
        self.init_save(self.savename)
        savefile = self.savename
        benny_hill = True if self.UI.BennyHillBox.isChecked() else False
        if self.UI.SweepGateRadio.isChecked():
            if fwire:
                axes = ['GateV', 'Resistance', 'GateI']
                self.init_graph(axes)
                self.gs = Sweep(self.gate, self.meter, minvoltage, maxvoltage,
                        stepsize, waittime, wait_max, wait_max_time, savefile,
                        self.plot, self.plot_lower, 'GateV',
                        'Resistance', 'GateI', benny_hill, False)
            else:
                # Then we Plot current on y axis
                axes = ['GateV', 'MeterI', 'GateI']
                self.init_graph(axes)
                self.gs = Sweep(self.gate, self.meter, minvoltage, maxvoltage,
                        stepsize, waittime, wait_max, wait_max_time, savefile,
                        self.plot, self.plot_lower, 'GateV',
                        'MeterI', 'GateI', benny_hill, False)

        else:
            # Then we sweep the meter, so change gate and meter
            axes = ['MeterV', 'MeterI', 'GateI']
            self.init_graph(axes)
            self.gs = Sweep(self.gate, self.meter, minvoltage, maxvoltage,
                stepsize, waittime, wait_max, wait_max_time, savefile,
                self.plot, self.plot_lower, 'MeterV',
                'MeterI', 'GateI', benny_hill, True)

        # Also connect abort button now
        self.UI.StopSweepButton.released.connect(self.gs.stop)
        self.start_in_thread(self.gs)

    def start_in_thread(self, target):
        self.thread = QtCore.QThread(self)
        target.finished_sweep.connect(self.sweep_callback)
        target.moveToThread(self.thread)
        self.thread.started.connect(target.start)
        self.UI.SweepLabel.setText('Measuring!')
        self.UI.SweepLabel.setStyleSheet('color: red')
        self.thread.start()

    def start_resmeas(self):
        gain_time = 60
        meterI = 1E-5
        axes = ['Time [s]', 'Resistance [Ohm]', 'Temperature [K]']
        self.init_graph(axes)
        # Check if file exists again, user could not have changed old one
        self.init_save(self.savename)
        savefile = self.savename
        self.res = ResLogger(self.meter, self.savename, self.plot, self.plot_lower)
        # Also connect abort button now
        self.UI.StopResButton.released.connect(self.res.stop)
        self.start_in_thread(self.res)


    def set_autogain_time(self):
        auto_gain = self.UI.GainTimeBox.value()
        try:
            self.res.set_autogain_time(auto_gain)
        except:
            pass

    def sweep_callback(self):
        self.UI.SweepLabel.setText('Idle')
        self.UI.SweepLabel.setStyleSheet('color: black')

    def change_gate_voltage(self):
        gateval = self.UI.FixedGateBox.value()
        try:
            measuring = self.sweep.get_measuring()
            if not measuring:
                self.gate.slowly_to_target(gateval, self.gate, True)
        except:
            try:
                self.gate.slowly_to_target(gateval, self.gate, True)
            except:
                pass
            pass

class Sweep(QtCore.QObject):
    finished_sweep = QtCore.pyqtSignal(bool)
    def __init__(self, gate, meter, minvoltage, maxvoltage, stepsize,
            waittime, wait_max, wait_max_time, savename, plot, plot_lower,
            x_name, yup_name, ylow_name, enable_music, is_sd_sweep):
        QtCore.QObject.__init__(self)
        # Music implementation for fun
        self.playlist = QMediaPlaylist()
        path_to_music = os.path.abspath('benny_hill.mp3')
        self.url = QtCore.QUrl.fromLocalFile(path_to_music)
        self.playlist.addMedia(QMediaContent(self.url))
        #self.playlist.setPlaybackMode(QMediaPlaylist.Loop)
        self.music = QMediaPlayer()
        self.music.setPlaylist(self.playlist)
        # End of Music section
        self.gate = gate
        self.meter = meter
        self.minvoltage = minvoltage
        self.maxvoltage = maxvoltage
        self.stepsize = stepsize
        self.waittime = waittime
        self.wait_max = wait_max
        self.wait_max_time = wait_max_time
        self.savename = savename
        self.plot = plot
        self.plot_lower = plot_lower
        self.x_name = x_name
        self.yup_name = yup_name
        self.ylow_name = ylow_name
        self.is_sd_sweep = is_sd_sweep
        self.enable_music = enable_music
        # End of parameters
        self.init_ramp_parameters()
        self.init_measure_values()
        self.select_plot_values()

        self.gate = gate
        self.meter = meter
        self.lakeshore = Lakeshore()
        savestring = \
                '# Gatevoltage[V], Temp[K], Metervoltage[V], Metercurrent[A],'+\
                ' R[Ohm], Gatecurrent[A]'
        self.create_savefile(savestring)
        self.init_ramp_parameters()


    def start_sweep(self):
        if self.is_sd_sweep:
            self.meter.set_range(self.maxvoltage)
        if self.enable_music:
            self.music.play()
        self.measuring = True
        while self.measuring:
            # Set gatevoltage and measure values
            if not self.is_sd_sweep:
                self.gate.set_voltage(self.sweepvoltage)
            else:
                self.meter.set_voltage(self.sweepvoltage)
            time.sleep(self.waittime)
            meterV = self.meter.read_voltage()
            meterI = self.meter.read_current()
            temp = self.lakeshore.read_temp()
            gatecurrent = self.gate.read_current()

            self.x.append(self.sweepvoltage)
            self.y.append(meterV)
            self.r.append(meterV/meterI)
            self.mI.append(meterI)
            self.gc.append(gatecurrent)

            # Write values to file
            writedict = {
                    'Gatevoltage': self.sweepvoltage,
                    'T': temp,
                    'V': meterV,
                    'I': meterI,
                    'R': meterV/meterI,
                    'I_gate': gatecurrent,
                    }
            for i in writedict:
                self.savefile.write('{} , '.format(str(writedict[i]).strip()))
            self.savefile.write("\n")
            self.savefile.flush()
            # Plot values
            self.plot.setData(self.plotx, self.plot_yup)
            self.plot_lower.setData(self.plotx, self.plot_ylow)
            QApplication.processEvents()
            # Set gatevoltage to next value
            self.ramp_sweepvoltage()
        QApplication.restoreOverrideCursor()
        self.music.stop()
        self.finish_sweep(self.x, self.y, self.gc, self.x_name, self.yup_name, self.ylow_name)

    def create_savefile(self, savestring):
        ''' Creates savefile and generates header '''
        self.savefile = open(self.savename, "w")
        self.savefile.write(savestring + "\n")

    def init_measure_values(self):
        self.x = []
        self.y = []
        self.r = []
        self.mI = []
        self.gc = []
        self.plotdict = {
                'GateV' : self.x,
                'MeterV' : self.y,
                'Resistance' : self.r,
                'MeterI': self.mI,
                'GateI' : self.gc,
                }


    def select_plot_values(self):
        self.plotx, self.plot_yup, self.plot_ylow = \
                self.plotdict[self.x_name], self.plotdict[self.yup_name],\
                self.plotdict[self.ylow_name]


    def init_ramp_parameters(self):
        ''' Initializes counters, necessary for self.ramp_sweepvoltage() '''
        self.sweepvoltage = 0
        self.lastvoltage = 0
        self.finishedcounter = 0
        self.maxcounter = 0

    def ramp_sweepvoltage(self):
        ''' Increments the sweepvoltage and finishes the measurement '''
        if self.sweepvoltage < self.maxvoltage and \
                self.sweepvoltage >= self.lastvoltage:
            self.lastvoltage = self.sweepvoltage
            self.sweepvoltage += self.stepsize
        elif self.sweepvoltage >= self.maxvoltage:
            if self.wait_max:
                time.sleep(self.wait_max_time) # wait at max voltage
            self.lastvoltage = self.sweepvoltage
            self.sweepvoltage -= self.stepsize
            self.maxcounter += 1
        elif self.sweepvoltage > self.minvoltage and \
                self.sweepvoltage < self.lastvoltage:
            self.lastvoltage = self.sweepvoltage
            self.sweepvoltage -= self.stepsize
        elif self.sweepvoltage <= self.minvoltage:
            self.lastvoltage = self.sweepvoltage
            self.sweepvoltage += self.stepsize
            self.maxcounter += 1
        if self.maxvoltage >= 0 and self.minvoltage >= 0:
            if self.maxcounter == 2:
                self.stop()
        if round(self.sweepvoltage,2) == 0:
            self.finishedcounter += 1
            if self.finishedcounter == 2:
                self.stop()

    def stop(self):
        QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)
        self.measuring = False
        QApplication.restoreOverrideCursor()

    def get_measuring(self):
        if self.measuring:
            return True
        return False

    def slowly_to_target(self, target, device, voltage=False):
        if voltage:
            now_val = round(device.read_voltage(),8)
            steps = np.linspace(now_val, target, 20)
        else:
            now_val = round(device.read_current(),8)
            steps = np.linspace(now_val, target, 20)
        if now_val == target:
            return
        # Need to reverse steps if going downwards
        # if now_val > abs(target):
            # steps = steps[::-1]

        for i in steps:
            if voltage:
                device.set_voltage(i)
            else:
                device.set_current(i)
            time.sleep(0.2)

    def finish_sweep(self, x, y_up, y_low, xlabel='', y_uplabel='', y_lowlabel=''):
        # Here the measurement is aborted or finished
        try:
            self.slowly_to_target(0, self.gate, voltage=True)
            # self.slowly_to_voltage(0, meter)
        except ValueError:
            pass
        if self.is_sd_sweep:
            self.slowly_to_target(0, self.meter, voltage=True)


        self.savefile.close()
        # After finishing, plot it once in mpl
        fig = plt.figure()
        ax = fig.add_subplot(211)
        ax1 = fig.add_subplot(212)
        basename = os.path.basename(self.savename)
        fig.suptitle(os.path.splitext(basename))
        ax.set_ylabel(y_uplabel)
        ax1.set_xlabel(xlabel)
        ax1.set_ylabel(y_lowlabel)
        ax.plot(x, y_up, 'k.')
        ax1.plot(x, y_low, 'k.')
        # save figure file as png
        savename_png = os.path.splitext(self.savename)[0] + '.png'
        fig.tight_layout()
        fig.savefig(savename_png)

    @QtCore.pyqtSlot()
    def start(self):
        self.start_sweep()
        self.finished_sweep.emit(True)



class ResLogger(QtCore.QObject):
    finished_sweep = QtCore.pyqtSignal(bool)
    def __init__(self, meter, savename, plot, plot_lower):
        QtCore.QObject.__init__(self)
    #def __init__(self, meter, savename, plot, autogain_time, meterI):
        # self.gate = Gate(1)
        # self.meter = Meter(2, four_wire=False, curr_source=1E-6)
        self.meter = meter
        self.lakeshore = Lakeshore()
        self.savename = savename
        self.plot = plot
        self.plot_lower = plot_lower
        self.gain_time = 0# in SEC
        self.meterI = 1

        savestring = "# time[s], Voltage[V], R[Ohms], temperature[K]"
        self.create_savefile(savestring)
        self.measuring = True

    def finish_sweep(self, x, y_up, y_low, xlabel='', y_uplabel='', y_lowlabel=''):
        # Here the measurement is aborted or finished

        self.savefile.close()
        # After finishing, plot it once in mpl
        fig = plt.figure()
        ax = fig.add_subplot(211)
        ax1 = fig.add_subplot(212)
        basename = os.path.basename(self.savename)
        fig.suptitle(os.path.splitext(basename))
        ax.set_ylabel(y_uplabel)
        ax1.set_xlabel(xlabel)
        ax1.set_ylabel(y_lowlabel)
        ax.plot(x, y_up, 'k.')
        ax1.plot(x, y_low, 'k.')
        # save figure file as png
        savename_png = os.path.splitext(self.savename)[0] + '.png'
        fig.tight_layout()
        fig.savefig(savename_png)


    def set_gain_time(self, gain_time):
        self.gain_time = gain_time

    def create_savefile(self, savestring):
        ''' Creates savefile and generates header '''
        self.savefile = open(self.savename, "w")
        self.savefile.write(savestring + "\n")

    def start(self):
        r = []
        t = []
        v = []
        temps = []
        start_time = time.time()
        #four_point_fac = np.pi * 2 / ln(2)
        reset_start = time.time()
        while self.measuring:
            time.sleep(1)
            time_elapsed = time.time() - start_time
            reset_time = time.time() - reset_start
            if self.gain_time != 0:
                if reset_time >= self.gain_time:
                    self.meter.auto_gain()
                    time.sleep(10)
                    reset_start = time.time()
            meterV = float(self.meter.read_voltage())
            meterI = self.meter.read_current()
            temperature = self.lakeshore.read_temp()
            resistance = meterV / meterI                             #without van der pauw geometrie

            temps.append(temperature)
            t.append(time_elapsed)
            r.append(resistance)
            v.append(meterV)
            # Plot values in real time
            self.plot.setData(t, r)
            self.plot_lower.setData(t, temps)
            self.savefile.write(
                "{}, {}, {}, {} \n".format(time_elapsed, meterV, resistance, temperature)
            )
            print(
                    "Time: {:.1f}, Voltage: {}, R: {}, Temp: {}".format(
                    time_elapsed, meterV, resistance, temperature
                )
            )
            QApplication.processEvents()
        self.finish_sweep(t, r, temps, 'Time [s]', r'Resistance [$\Omega$]',
                'Temperature [K]')
        self.finished_sweep.emit(True)
        # self.finish_sweep(t, r, temps, 'Time [s]', r'Resistance [$\Omega$]',
                # 'Temperature [K]')

    def stop(self):
        QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)
        self.measuring = False
        QApplication.restoreOverrideCursor()


if __name__ == '__main__':
    qApp = QApplication(sys.argv)
    aw = MainWindow()
    aw.show()
    sys.exit(qApp.exec_())
