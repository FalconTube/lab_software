import sys
import time
import pyqtgraph as pg
import Classes.PID
from PyQt5 import QtCore, uic
from PyQt5.QtWidgets import (
    QMainWindow,
    QApplication,
    QLabel
    )
from Classes.device_classes import *
#from Classes.measurement_class import Measurement
from Classes.korad_class import KoradSerial


class GrapheneGrowth(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        self.UI = uic.loadUi('GrapheneUI.ui', self)
        self.init_box_values()
        self.setup_buttons()
        self.init_crystal_values()
        self.init_graph()
        self.init_port_selection()
        self.show()

    def init_crystal_values(self):
        self.crystal_dict = {
                'Crystal 1' : 70,
                'Crystal 2' : 50,
                'Crystal 3' : 80,
                }

    def init_box_values(self):
        self.UI.FlashValueBox.setDecimals(1)
        self.UI.FlashValueBox.setMaximum(200)
        self.UI.FlashValueBox.setValue(130)
        self.UI.AnnealValueBox.setValue(80)
        self.UI.AnnealValueBox.setMaximum(200)

    def init_port_selection(self):
        ports = serial.tools.list_ports.comports()
        for port in ports:
            device = port.device
            self.UI.FugPortBox.addItem(device)
            self.UI.KoradPortBox.addItem(device)

    def init_graph(self):
        self.graph = self.UI.EmissionView
        p = pg.mkPen(color=(63, 117, 204), width=2)
        self.plot = self.graph.plot(pen=p)
        self.graph.setAutoVisible(y=True)
        self.graph.enableAutoRange('x')
        self.graph.enableAutoRange('y')
        #self.graph.showGrid(y=True,x=True)
        self.graph.showAxis("right")
        self.graph.getAxis("right").tickStrings = lambda x,y,z: ["" for value in x]
        self.graph.showAxis("top")
        self.graph.getAxis("top").tickStrings = lambda x,y,z: ["" for value in x]
        self.graph.setTitle("Emission Current")
        self.graph.setLabel("left", "Current [mA]")
        self.graph.setLabel("bottom", "Passed time [s]")

    # def init_controllers(self):
        # self.FUG = FUG()
        # self.korad = KoradSerial('COM5')
        # self.channel = self.korad.channels[0]
        # self.korad.output.off()
        # self.channel.current = 0.0

    def setup_buttons(self):
        self.UI.FlashButton.released.connect(self.use_flash)
        self.UI.AnnealButton.released.connect(self.use_anneal)
        self.UI.GrowButton.released.connect(self.use_grow)
        #self.UI.GrowButton.released.connect(self.go_emission)

    def ramp_to_current(self, target, time):
        ''' Ramps to target value over chosen time '''
        current_current = self.channel.current
        time.sleep(0.05)
        ramp_range = np.linspace(current_current, target, 40)
        for i in ramp_range:
            i = self.round_value(i)
            self.channel.current = i
            time.sleep(0.25*3)  # 30 sec ramp time each

    def use_grow(self):
        crystal = self.UI.CrystalBox.currentText()
        heatval = self.crystal_dict[crystal]
        print(heatval)
        self.GrowCycle = GrowCycle(target=heatval, duration=10*60,
                sleep_time=0.2, plot=self.plot, crystal=crystal)
        self.thread = QtCore.QThread(self)
        self.GrowCycle.grow_finished.connect(self.grow_callback)
        self.GrowCycle.moveToThread(self.thread)
        self.thread.started.connect(self.GrowCycle.do_grow)
        self.UI.StatusLabel.setText('Growing!')
        self.UI.StatusLabel.setStyleSheet('color: red')
        self.thread.start()

    def grow_callback(self):
        self.UI.StatusLabel.setText('Finished Grow')
        self.UI.StatusLabel.setStyleSheet('color: black')

    def use_anneal(self):
        target = self.UI.AnnealValueBox.value()
        self.Annealing = Annealing(target, 15*60, 0.5, self.plot)
        self.thread = QtCore.QThread(self)
        self.Annealing.anneal_finished.connect(self.anneal_callback)
        self.Annealing.moveToThread(self.thread)
        self.thread.started.connect(self.Annealing.do_anneal)
        self.UI.StatusLabel.setText('Annealing!')
        self.UI.StatusLabel.setStyleSheet('color: red')
        self.thread.start()

    def anneal_callback(self):
        self.UI.StatusLabel.setText('Finished Anneal')
        self.UI.StatusLabel.setStyleSheet('color: black')

    def use_flash(self):
        target = self.UI.FlashValueBox.value()
        self.Flashing = Flashing(target, 10, 0.1, self.plot)
        self.thread = QtCore.QThread(self)
        self.Flashing.flash_finished.connect(self.flash_callback)
        self.Flashing.moveToThread(self.thread)
        self.thread.started.connect(self.Flashing.do_flash)
        self.UI.StatusLabel.setText('Flashing!')
        self.UI.StatusLabel.setStyleSheet('color: red')
        self.thread.start()

    def flash_callback(self):
        self.UI.StatusLabel.setText('Finished Flash')
        self.UI.StatusLabel.setStyleSheet('color: black')
        curr_cycle = int(self.UI.CycleLabel.text())
        curr_cycle += 1
        self.UI.CycleLabel.setText(str(curr_cycle))


class Heating(QtCore.QObject):
    def __init__(self, target, hold_time, sleep_time=0.3, plot=None):
        QtCore.QObject.__init__(self)
        self.UI = uic.loadUi('GrapheneUI.ui', self)
        self.target = target
        self.duration = hold_time
        self.sleep_time = sleep_time
        self.plot = plot
        self.init_controllers()

    def init_controllers(self):
        fug_port = self.UI.FugPortBox.currentText()
        korad_port = self.UI.KoradPortBox.currentText()
        print(fug_port, korad_port)
        self.FUG = FUG(fug_port)
        self.korad = KoradSerial(korad_port)
        self.channel = self.korad.channels[0]
        self.channel.current = 0.0
        self.korad.output.on()
        self.FUG.output_on()
        time.sleep(0.5)

    def close_controllers(self):
        self.channel.current = 0.0
        self.korad.output.off()
        self.FUG.close()
        self.korad.close()

    def in_tolerance(self, value, target, tolerance=0.01):
        lower = target - target * tolerance
        upper = target + target * tolerance
        print(lower, value, upper)
        return True if lower <= value <= upper else False

    def percentage_pos(self, value, perc):
        return value + value * perc

    def percentage_neg(self, value, perc):
        return value - value * perc

    def emission_step(self, emission, target, perc, current, current_step):
        print('Changing with stepsize {}'.format(current_step))
        if not self.changed_korad:
            if emission < self.percentage_neg(target, perc):
                current += current_step
                self.korad.set_current(current)
                self.changed_korad = True
            if emission > self.percentage_pos(target, perc):
                current -= current_step
                self.korad.set_current(current)
                self.changed_korad = True

    def run(self):
        ''' Starts the actual heating to given target '''
        # Plotting
        xdat = []
        yemis = []
        ykorad = []
        xstart = time.time()
        # Declare heating steps
        korad_steps = {
                0.50 : 0.05,
                0.30 : 0.03,
                0.20 : 0.02,
                0.10 : 0.01,
                0.05 : 0.003,
                }

        start = time.time()
        passed = time.time() - start
        reached_target = False
        self.korad.set_current(2.2)
        while passed < self.duration:
            self.changed_korad = False
            passed = time.time() - start
            emission = self.FUG.read_emission()
            current = self.korad.get_current()
            xdat.append(time.time() - xstart)
            yemis.append(emission)
            ykorad.append(current)
            if self.in_tolerance(emission, self.target, tolerance=0.01):
                reached_target = True
                self.plot.setData(xdat, yemis)
                time.sleep(1)
                continue
            # if not at target
            for percentage, stepsize in korad_steps.items():
                if not self.changed_korad:
                    self.emission_step(emission, self.target, percentage, current,
                            stepsize)
            time.sleep(self.sleep_time)
            if not reached_target:
                start = time.time()
            self.plot.setData(xdat, yemis)
        self.close_controllers()


class GrowCycle(Heating):
    ''' Grow for chosen Crystal '''
    grow_finished = QtCore.pyqtSignal(bool)
    def __init__(self, target, duration, sleep_time, plot, crystal):
        super().__init__(target, duration, sleep_time, plot)
        # self.target = target
        # self.duration = duration
        self.crystal = crystal

    @QtCore.pyqtSlot()
    def do_grow(self):
        self.run()
        self.grow_finished.emit(True)

class Annealing(Heating):
    ''' Perform annealing procedure heating  '''
    anneal_finished = QtCore.pyqtSignal(bool)
    def __init__(self, target, duration, sleep_time, plot):
        super().__init__(target, duration, sleep_time, plot)
        # self.target = target
        # self.duration = duration

    @QtCore.pyqtSlot()
    def do_anneal(self):
        self.run()
        self.anneal_finished.emit(True)

class Flashing(Heating):
    ''' Increase to flash value und hold for 10 sec '''
    flash_finished = QtCore.pyqtSignal(bool)
    def __init__(self, target, duration, sleep_time, plot):
        super().__init__(target, duration, sleep_time, plot)

    @QtCore.pyqtSlot()
    def do_flash(self):
        self.run()
        self.flash_finished.emit(True)

# for _ in range(60):
    # time.sleep(1)
    # print(time.time())
    # ser.write(b'*IDN?\r\n')
    # answer = ser.readline().decode('utf-8')
    # print(answer)
# ser.close()

if __name__ == '__main__':
    qApp = QApplication(sys.argv)
    aw = GrapheneGrowth()
    aw.show()
    sys.exit(qApp.exec_())
