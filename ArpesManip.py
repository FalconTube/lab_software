import sys
import os
import time
from Classes.ManipClass import Manipulator
from PyQt5 import QtCore, uic
from PyQt5.QtWidgets import (
    QMainWindow,
    QApplication,
    QLabel,
    QErrorMessage,
    QMessageBox,
    QWidget
    )
from inputs import get_gamepad


class ManipInterface(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        os.chdir('C:/Users/ARPES01/Documents/lab_software/')
        self.UI = uic.loadUi('ArpesManip.ui', self)
        self.init_manip()
        self.init_buttons()
        self.init_labels()
        self.init_radiobuttons()
        self.AXIS = 'X'
        self.assi=['X','Y','Z']
        self.show()
        "changed to dev for testing"


    def init_manip(self):
        self.manip = Manipulator()

    def init_buttons(self):
        '''Connect the buttons to functions e.g.
        self.UI.buttonname.released.connect(self.function)'''
        # Up Button
        self.UI.MoveUpRelativeButton.released.connect(self.moveUpRelative)
        self.UI.MoveUpHoldButton.pressed.connect(self.moveUpHold)
        self.UI.MoveUpHoldButton.released.connect(self.stopMovement)
        self.UI.MoveUpHoldButton.released.connect(self.set_watch_move_false)
        # Down Button
        self.UI.MoveDownRelativeButton.released.connect(self.moveDownRelative)
        self.UI.MoveDownHoldButton.pressed.connect(self.moveDownHold)
        self.UI.MoveDownHoldButton.released.connect(self.stopMovement)
        self.UI.MoveDownHoldButton.released.connect(self.set_watch_move_false)

        self.UI.StopButton.released.connect(self.stopMovement)
        self.UI.MoveAbsoluteButton.released.connect(self.absMovement)
        self.UI.GoToGamma.released.connect(self.goToGamma)
        self.UI.GoToInsert.released.connect(self.goToInsert)

    def init_labels(self):
        self.UI.ComLabel.setText('No error')
        self.UI.ComLabel.setStyleSheet('color: green')
        axes_dict = {
            'X': self.UI.ZValueLabel,
            'Y': self.UI.PolarValueLabel,
            'Z': self.UI.AziValueLabel,
        }
        for x in axes_dict:
            outval = self.manip.readVal(x)
            this_label = axes_dict[x]
            this_label.setText(outval)

    def init_radiobuttons(self):
        self.radio_dict = {
            'X': self.UI.ZRadio,
            'Y': self.UI.PolarRadio,
            'Z': self.UI.AziRadio,
        }


    def set_watch_move_false(self):
        self.need_watching = False

    def movementWatcherAndAziStop(self):
        # Start on pressed, Kill on released
        time.sleep(0.02)
        while self.need_watching:
            self.readVal()
            if self.AXIS == 'Z':
                try:
                    outval = float(self.manip.readVal(self.AXIS))
                except:
                    outval = outval
                if outval >= 40 or outval <= -180:
                    self.manip.write('XSN')
                    self.UI.ComLabel.setText('Azi at minimal value!')
                    self.UI.ComLabel.setStyleSheet('color: red')

#SELECT AXIS
    def getMoveAxis(self):
        if self.UI.ZRadio.isChecked():
            ax = 'X'
        if self.UI.PolarRadio.isChecked():
            ax = 'Y'
        if self.UI.AziRadio.isChecked():
            ax = 'Z'
        self.AXIS = ax
#Move-Hold buttons
    def moveUpHold(self):
        ''' Moves UP until stop signal is received '''
        self.need_watching = True
        self.getMoveAxis()
        self.UI.ComLabel.setText('No error')
        self.UI.ComLabel.setStyleSheet('color: green')
        self.manip.write(f'{self.AXIS}L-')
        self.movementWatcherAndAziStop()


    def moveDownHold(self):
        ''' Moves DOWN until stop signal is received '''
        self.need_watching = True
        self.getMoveAxis()
        self.UI.ComLabel.setText('No error')
        self.UI.ComLabel.setStyleSheet('color: green')
        self.manip.write(f'{self.AXIS}L+')
        self.movementWatcherAndAziStop()

#Move-Relative buttons
    def moveUpRelative(self):
        steps = self.UI.MoveRelativeBox.value()
        self.getMoveAxis()
        self.UI.ComLabel.setText('No error')
        self.forbidAziRelative("up")
        self.manip.write(f'{self.AXIS}-{steps}')
        self.checkMoving()


    def moveDownRelative(self):
        steps = self.UI.MoveRelativeBox.value()
        self.getMoveAxis()
        self.UI.ComLabel.setText('No error')
        self.forbidAziRelative("down")
        self.manip.write(f'{self.AXIS}+{steps}')
        self.checkMoving()

    def forbidAziRelative(self, direction):
        if direction=="down":
            steps = self.UI.MoveRelativeBox.value()
            if self.AXIS=='Z':
                currval=self.manip.readVal(self.AXIS)
                stopval=float(currval)+steps
                print(str(stopval))
                if stopval>=40:
                    self.UI.ComLabel.setText('I will not move is not safe')
                    self.manip.write('XSN')
        if direction=="up":
            steps = self.UI.MoveRelativeBox.value()
            if self.AXIS=='Z':
                currval=self.manip.readVal(self.AXIS)
                stopval=float(currval)-steps
                print(str(stopval))
                if stopval<=-180.81:
                    self.UI.ComLabel.setText('I will not move is not safe')
                    self.manip.write('XSN')


#Absolute movement
    def absMovement(self):
        self.getMoveAxis()
        self.UI.ComLabel.setText('No error')
        absPos=self.UI.MoveAbsoluteBox.value()
        currPosition=float(self.manip.readVal(self.AXIS))
        steps=currPosition-absPos
        self.forbidAziAbsolute()

        if steps>0:
            self.manip.write(f'{self.AXIS}-{round(abs(steps),2)}')

        if steps<0:
            self.manip.write(f'{self.AXIS}+{round(abs(steps),2)}')

        self.checkMoving()


    def forbidAziAbsolute(self):
        if self.AXIS=='Z':
            arrivalPosition=float(self.UI.MoveAbsoluteBox.value())

            if arrivalPosition<=-187.81:
                self.UI.ComLabel.setText('Azi beyond maximal value!')
                self.manip.write('XSN')

            if arrivalPosition>40:
                self.UI.ComLabel.setText('Azi beyond minimal value!')
                self.manip.write('XSN')

    def goToGamma(self):
        self.goToPosition('Gamma')

    def goToInsert(self):
        self.goToPosition('Insert')

    def goToPosition(self, position):


        axes_coord = self.manip.getPossiblePositions(position)


        for x in axes_coord:
            self.radio_dict[x].setChecked(True)

            QApplication.processEvents()
            currPosition=float(self.manip.readVal(x))
            steps=currPosition-axes_coord[x]
            if steps>0:
                self.manip.write(f'{x}-{round(abs(steps),2)}')

            if steps<0:
                self.manip.write(f'{x}+{round(abs(steps),2)}')

            time.sleep(0.2)
            self.checkMoving()




#Read movement, stop movement, check motor status
    def stopMovement(self):
        self.manip.write('XSN')

    def readVal(self):
        ''' Reads the position of the current axis and updates
        label accordingly '''
        #self.getMoveAxis()
        for x in self.assi:

            outval = self.manip.readVal(x)

            axes_dict = {
                'X': self.UI.ZValueLabel,
                'Y': self.UI.PolarValueLabel,
                'Z': self.UI.AziValueLabel,
             }

            this_label = axes_dict[x]
            this_label.setText(outval)

        QApplication.processEvents()

    def checkMoving(self):

        for x in self.assi:

            value = self.manip.ask(f'{x}=H') #X=H check if the axis is still
            while value=='N':#X=E means true; X=N menas false
                self.readVal()
                QApplication.processEvents()
                time.sleep(0.01)
                value = self.manip.ask(f'{x}=H')
            self.readVal()



#Gamepad
    # def gamePadMove(self):
    #     self.events = get_gamepad()
    #     print(event.ev_type, event.code, event.state)


if __name__ == '__main__':
    qApp = QApplication(sys.argv)
    aw = ManipInterface()
    aw.show()
    sys.exit(qApp.exec_())

