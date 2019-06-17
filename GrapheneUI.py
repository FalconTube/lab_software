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
        self.init_crystal_dropdown()
        self.show()

    def init_crystal_values(self):
        self.crystal_dict = {
                'Crystal 1' : 73,
                'Crystal 2' : 50,
                'Crystal 3' : 80,
                'Free' : 0,
                }


    def update_crystal_val(self):
        crystal = self.UI.CrystalBox.currentText()
        self.UI.GrowthTargetBox.setValue(self.crystal_dict[crystal])
        if crystal == 'Free':
            self.UI.GrowthTargetBox.setReadOnly(False)
        else:
            self.UI.GrowthTargetBox.setReadOnly(True)

    def init_crystal_dropdown(self):
        crystal = self.UI.CrystalBox.currentText()
        self.UI.GrowthTargetBox.setValue(self.crystal_dict[crystal])
        self.UI.CrystalBox.currentIndexChanged.connect(self.update_crystal_val)

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
    
    def init_controllers(self):
        fug_port = self.UI.FugPortBox.currentText()
        korad_port = self.UI.KoradPortBox.currentText()
        print(fug_port, korad_port)
        self.FUG = FUG(fug_port)
        self.korad = KoradSerial(korad_port)
        self.channel = self.korad.channels[0]
        self.channel.current = 0.0
        self.korad.output.on()
        self.FUG.set_maxima()
        self.FUG.output_on()
        time.sleep(0.5)


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

    def update_graph(self):
        x, y = self.experiment.get_data()
        self.plot.setData(x, y)

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
        duration = self.UI.GrowthDurationBox.value()
        self.UI.GrowthTargetBox.setValue(heatval)

        self.experiment = GrowCycle(target=heatval, duration=duration,
                sleep_time=0.2, crystal=crystal)
        self.start_in_thread(grow_callback, 'Growing!')

    def grow_callback(self):
        self.UI.StatusLabel.setText('Finished Grow')
        self.UI.StatusLabel.setStyleSheet('color: black')

    def use_anneal(self):
        target = self.UI.AnnealValueBox.value()
        duration = self.UI.AnnealTimeBox.value() # in min
        duration *= 60
        self.init_controllers()
        self.experiment = Annealing(target, duration, 0.5, self.FUG, self.korad)
        self.start_in_thread(self.anneal_callback, 'Annealing!')

    def anneal_callback(self):
        self.UI.StatusLabel.setText('Finished Anneal')
        self.UI.StatusLabel.setStyleSheet('color: black')

    def use_flash(self):
        target = self.UI.FlashValueBox.value()
        duration = self.UI.FlashTimeBox.value() # in SEC
        self.init_controllers()
        self.experiment = Flashing(target, duration, 0.1, self.FUG, self.korad)
        self.start_in_thread(self.flash_callback, 'Flashing!')

    def flash_callback(self):
        self.UI.StatusLabel.setText('Finished Flash')
        self.UI.StatusLabel.setStyleSheet('color: black')
        curr_cycle = int(self.UI.CycleLabel.text())
        curr_cycle += 1
        self.UI.CycleLabel.setText(str(curr_cycle))

    def start_in_thread(self, callback, statustext):
        try:
            self.StopButton.disconnect()
        except:
            pass
        self.StopButton.released.connect(self.experiment.stop)
        self.thread = QtCore.QThread(self)
        self.experiment.experiment_finished.connect(callback)
        self.experiment.moveToThread(self.thread)
        self.experiment.new_data_available.connect(self.update_graph)
        self.thread.started.connect(self.experiment.do_expemiment)
        self.UI.StatusLabel.setText(statustext)
        self.UI.StatusLabel.setStyleSheet('color: red')
        QApplication.processEvents()
        self.thread.start()


class Heating(QtCore.QObject):
    experiment_finished = QtCore.pyqtSignal(bool)
    new_data_available = QtCore.pyqtSignal(bool)
    def __init__(self, target, hold_time, sleep_time=0.3, FUG=None, Korad=None):
        QtCore.QObject.__init__(self)
        self.target = target
        self.duration = hold_time
        self.sleep_time = sleep_time
        self.FUG = FUG
        self.korad = Korad

    def close_controllers(self):
        self.korad.set_current(0.0)
        self.korad.output.off()
        self.FUG.close()
        self.korad.close()

    def in_tolerance(self, value, target, tolerance=0.01):
        lower = target - target * tolerance
        upper = target + target * tolerance
        return True if lower <= value <= upper else False

    def percentage_pos(self, value, perc):
        return value + value * perc

    def percentage_neg(self, value, perc):
        return value - value * perc

    def emission_step(self, emission, target, perc, current, current_step):
        if not self.changed_korad:
            if emission < self.percentage_neg(target, perc):
                current += current_step
                self.korad.set_current(current)
                self.changed_korad = True
            if emission > self.percentage_pos(target, perc):
                self.korad.set_current(current)
                self.changed_korad = True

    def run(self):
        ''' Starts the actual heating to given target '''
        # Plotting
        self.xdat = []
        self.yemis = []
        self.ykorad = []
        xstart = time.time()
        # Declare heating steps
        korad_steps = {
                0.50 : 0.05,
                0.30 : 0.03,
                0.20 : 0.02,
                0.10 : 0.01,
                0.05 : 0.005,
                0.04 : 0.004,
                0.03 : 0.003,
                0.02 : 0.002,
                0.01 : 0.001,
                }

        start = time.time()
        passed = time.time() - start
        reached_target = False
        # Good value before emission starts
        self.korad.set_current(2.2)
        while passed < self.duration:
            self.changed_korad = False
            passed = time.time() - start
            emission = self.FUG.read_emission()
            current = self.korad.get_current()
            now = time.time()
            self.xdat.append(now - xstart)
            self.yemis.append(emission)
            self.ykorad.append(current)
            if self.in_tolerance(emission, self.target, tolerance=0.01):
                reached_target = True
                self.new_data_available.emit(True)
            else:
                # if not at target
                for percentage, stepsize in korad_steps.items():
                    if not self.changed_korad:
                        self.emission_step(emission, self.target, percentage, current,
                                stepsize)
            time.sleep(self.sleep_time)
            if not reached_target:
                start = time.time()
            self.new_data_available.emit(True)
        self.close_controllers()

    def do_expemiment(self):
        self.run()
        self.experiment_finished.emit(True)

    def get_data(self):
        return self.xdat, self.yemis

    def stop(self):
        self.duration = 0

class GrowCycle(Heating):
    ''' Grow for chosen Crystal '''
    def __init__(self, target, duration, sleep_time, crystal, FUG, Korad):
        super().__init__(target, duration, sleep_time, FUG, Korad)
        # self.target = target
        # self.duration = duration
        self.crystal = crystal


class Annealing(Heating):
    ''' Perform annealing procedure heating  '''
    def __init__(self, target, duration, sleep_time, FUG, Korad):
        super().__init__(target, duration, sleep_time, FUG, Korad)
        # self.target = target
        # self.duration = duration


class Flashing(Heating):
    ''' Increase to flash value und hold for 10 sec '''
    def __init__(self, target, duration, sleep_time, FUG, Korad):
        super().__init__(target, duration, sleep_time, FUG, Korad)

if __name__ == '__main__':
    qApp = QApplication(sys.argv)
    aw = GrapheneGrowth()
    aw.show()
    sys.exit(qApp.exec_())
