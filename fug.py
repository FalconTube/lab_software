import sys
import time
import Classes.PID
from PyQt5 import QtCore, uic
from PyQt5.QtWidgets import (
    QMainWindow,
    QApplication
    )
from Classes.device_classes import *
# from Classes.measurement_class import Measurement
# from Classes.korad_class import KoradSerial


class GrapheneGrowth(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        self.UI = uic.loadUi('GrapheneUI.ui', self)
        self.init_box_values()
        self.flash_pid = PID(10, 1, 1)
        self.setup_buttons()
        self.show()

    def init_box_values(self):
        self.UI.FlashValueBox.setDecimals(1)
        self.UI.FlashValueBox.setMaximum(200)
        self.UI.FlashValueBox.setValue(130)
        self.UI.AnnealValueBox.setValue(80)
        self.UI.AnnealValueBox.setMaximum(200)

    def init_controllers(self):
        self.FUG = FUG()
        self.korad = KoradSerial('COM5')
        self.channel = self.korad.channels[0]
        self.korad.output.off()
        self.channel.current = 0.0

    def setup_buttons(self):
        self.UI.InitControllerButton.released.connect(self.init_controllers)
        self.UI.FlashButton.released.connect(self.flash)

    def round_value(self, value):
        if value >= 1.0:
            value = round(value, 3)  # Max sensitivity
        else:
            value = round(value, 4)  # Max sensisivity
        return value

    def ramp_to_current(self, target, time):
        ''' Ramps to target value over chosen time '''
        current_current = self.channel.current
        time.sleep(0.05)
        ramp_range = np.linspace(current_current, target, 40)
        for i in ramp_range:
            i = self.round_value(i)
            self.channel.current = i
            time.sleep(0.25*3)  # 30 sec ramp time each

    def flash(self):
        ''' Increase to flash value und hold for 10 sec '''
        # Set up PID
        target = self.UI.FlashValueBox.value()
        self.flash_pid.SetPoint(target)
        self.flash_pid.setSampleTime(0.5)
        # Initial current of Korad
        self.korad.set_current(3.3)
        self.korad.output.on()
        time.sleep(0.3)
        emission = self.FUG.read_emission()
        pid.update(emission)
        target_pwm = pid.output
        print('emission {}, target pwm {}'.format(emission, target_pwm))
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
