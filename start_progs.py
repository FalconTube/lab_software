import os
import sys
import signal
import subprocess
from PyQt5 import QtGui, uic
from PyQt5.QtWidgets import QMainWindow, QApplication, QPushButton


version = sys.version[0]
if version == '3':
    if 'win' in sys.platform.lower():
        py_version = 'python'
    else:
        py_version = 'python3'
else:
    py_version = 'python'

Programs = {
        'Gatesweep' : 'gatesweep.py',
        'Gatesweep Lockin' : 'gatesweep_lockin.py',
        'Resistance vs time' : 'resist_temp_time.py',
        'Use Korad Heating' : 'korad_usage.py',
        'Sweep Meter' : 'sweep_meter.py',
        }

pwd = os.getcwd()
print(pwd)

class MyWindow(QMainWindow):
    def __init__(self):
        super(MyWindow, self).__init__()
        #signal.signal(signal.SIGINT, self.handle_ctrl_c)
        signal.signal(signal.SIGINT, signal.SIG_IGN)
        UI = uic.loadUi('Starter.ui', self)
        for button in UI.AllButtonsBox.findChildren(QPushButton):
            button.released.connect(self.start_selection)
        self.show()

    def start_selection(self):
        btn = self.sender()
        text = btn.text().strip('&')
        selection = str(Programs[text])
        if 'win' in sys.platform.lower():
            subprocess.call('start /wait python {}'.format(selection), shell=True)
        else:
            os.system('{} {}'.format(py_version, selection))

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MyWindow()
    sys.exit(app.exec_())
