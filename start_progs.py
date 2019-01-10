import os
import sys
from PyQt5 import QtGui, uic
from PyQt5.QtWidgets import QMainWindow, QApplication


version = sys.version[0]
if version == '3':
    if sys.platform == 'Windows':
        py_version = 'python'
    else:
        py_version = 'python3'
else:
    py_version = 'python'

Programs = {
        'Gatesweep' : 'gatesweep.py',
        'Test_Button' : 'calc_mobility.py',
        }

pwd = os.getcwd()
print(pwd)

class MyWindow(QMainWindow):
    def __init__(self):
        super(MyWindow, self).__init__()
        UI = uic.loadUi('Starter.ui', self)
        UI.Gatesweep.released.connect(self.start_selection)
        UI.Test_Button.released.connect(self.start_selection)
        self.show()

    def start_selection(self):
        btn = self.sender()
        text = btn.text().strip('&')
        selection = str(Programs[text])
        os.system('{} {}'.format(py_version, selection))

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MyWindow()
    sys.exit(app.exec_())
