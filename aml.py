import time
import serial
import visdom
import numpy as np
import datetime
from Classes.device_classes import AML

class PressureLogging:
    ''' Logging pressure of AML and writing to visdom plot '''
    def __init__(self, interval):
        self.aml = AML('COM4')
        self.v = visdom.Visdom()
        # self.start_time = time.time()
        self.interval = interval
        self.reading = True

    def init_vis_plot(self):
        curr_time = datetime.datetime.now()
        #curr_time = time.time()
        y = np.array([self.curr_pressure])
        self.pressure_plot = self.v.line(y, X=np.array([curr_time]),
                opts={'layoutopts':{
                    'plotly':
                    {'xaxis':{
                        # 'rangeslider' : {
                            # 'visible' : 'False'},
                    'type':'date'},
                    'yaxis': {'tickformat':'.1e'},
                    #'rangeslider':{'visible':'true'}
                    }}}
                    )

    def update_vis_plot(self):
        now = datetime.datetime.now()
        #now = time.time() 
        y = np.array([self.curr_pressure])
        self.v.line(y, X=np.array([now]), win=self.pressure_plot,
                update='append',
                    )

    def measure(self):
        self.curr_pressure = self.aml.read_value()
        # self.curr_pressure = self.aml.convert_value(first)
        self.init_vis_plot()
        while self.reading:
            self.curr_pressure = self.aml.read_value()
            self.update_vis_plot()
            time.sleep(self.interval)
            # if 'GI1' in answer:
                # try:
                    # self.curr_pressure = self.aml.convert_value(answer)
                    # self.update_vis_plot()
                # except:
                    # pass
        self.ser.close()

if __name__ == '__main__':
    P = PressureLogging(20)
    P.measure()
