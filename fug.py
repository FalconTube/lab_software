import sys
import time
import Classes.PID
from PyQt5 import QtCore, uic
from PyQt5.QtWidgets import (
    QMainWindow,
    QApplication,
    QLabel
    )
from Classes.device_classes import *
# from Classes.measurement_class import Measurement
# from Classes.korad_class import KoradSerial


class GrapheneGrowth(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        self.UI = uic.loadUi('GrapheneUI.ui', self)
        self.init_box_values()
        self.setup_buttons()
        self.init_crystal_values()
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

    # def init_controllers(self):
        # self.FUG = FUG()
        # self.korad = KoradSerial('COM5')
        # self.channel = self.korad.channels[0]
        # self.korad.output.off()
        # self.channel.current = 0.0

    def setup_buttons(self):
        #self.UI.InitControllerButton.released.connect(self.init_controllers)
        self.UI.FlashButton.released.connect(self.use_flash)
        self.UI.AnnealButton.released.connect(self.use_anneal)
        #self.UI.GrowButton.released.connect(self.use_grow)
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
        self.GrowCycle = GrowCycle(heatval)
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
        self.Annealing = Annealing()
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
        self.Flashing = Flashing()
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


class Heating:
    def __init__(self, target, hold_time):
        self.target = target
        self.hold_time = hold_time
        self.init_controllers()

    def init_controllers(self):
        self.FUG = FUG()
        self.korad = KoradSerial('COM5')
        self.channel = self.korad.channels[0]
        self.korad.output.off()
        self.channel.current = 0.0

    def close_controllers(self):
        self.channel.current = 0.0
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
            if emission < percentage_neg(target, perc):
                current += current_step
                self.korad.set_current(current)
                self.changed_korad = True
            if emission > percentage_pos(target, perc):
                current -= current_step
                self.korad.set_current(current)
                self.changed_korad = True

    def run(self):
        ''' Starts the actual heating to given target '''

        # Declare heating variables
        #self.target = 50
        #tolerance = 0.1
        #self.duration = 2
        # Declare heating steps
        korad_steps = {
                0.50 : 0.1,
                0.30 : 0.05,
                0.20 : 0.03,
                0.10 : 0.01,
                0.05 : 0.005,
                }
        start = time.time()
        passed = time.time() - start
        while passed < self.duration:
            self.changed_korad = False
            passed = time.time() - start
            emission = self.FUG.read_emission()
            current = self.korad.get_current()
            if in_tolerance(emission, self.target, tolerance=0.05):
                time.sleep(1)
                continue
            for percentage, stepsize in korad_steps.items():
                if not self.changed_korad:
                    self.emission_step(emission, self.target, percentage, current,
                            stepsize)
            time.sleep(0.2)
        self.close_controllers()


class GrowCycle(Heating):
    ''' Grow for chosen Crystal '''
    def __init__(self, target=10, duration=10, crystal):
        super().__init__(self, target, duration)
        self.crystal = crystal
        grow_finished = QtCore.pyqtSignal(bool)

    @QtCore.pyqtSlot()
    def do_grow(self):
        self.run()
        self.grow_finished.emit(True)

class Annealing(QtCore.QObject):
    ''' Perform annealing procedure heating  '''
    anneal_finished = QtCore.pyqtSignal(bool)

    @QtCore.pyqtSlot()
    def do_anneal(self):
        for i in range(2):
            time.sleep(1)
            print('{}'.format(i))
        self.anneal_finished.emit(True)

class Flashing(QtCore.QObject):
    ''' Increase to flash value und hold for 10 sec '''
    flash_finished = QtCore.pyqtSignal(bool)

    @QtCore.pyqtSlot()
    def do_flash(self):
        for i in range(2):
            time.sleep(1)
            print('{}'.format(i))
        self.flash_finished.emit(True)
    # Set up PID
    # target = self.UI.FlashValueBox.value()
    # self.flash_pid.SetPoint(target)
    # self.flash_pid.setSampleTime(0.5)
    # # Initial current of Korad
    # self.korad.set_current(3.3)
    # self.korad.output.on()
    # time.sleep(0.3)
    # emission = self.FUG.read_emission()
    # pid.update(emission)
    # target_pwm = pid.output
    # print('emission {}, target pwm {}'.format(emission, target_pwm))
    # start_time = time.time()
    # curr_time = time.time() - start_time
    # while curr_time < 10:
        # curr_time = time.time() - start_time
        # self.flash_pid()
        # pass

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
