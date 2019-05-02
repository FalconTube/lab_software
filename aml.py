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

<<<<<<< HEAD
    def init_port(self):
        self.ser.port='COM4'
        self.ser.baudrate=9600
        self.ser.parity=serial.PARITY_NONE
        self.ser.stopbits=serial.STOPBITS_ONE
        self.ser.bytesize=serial.EIGHTBITS
        self.ser.write_timeout=3
        self.ser.timeout=3
        self.ser.rts=1,
        self.ser.dtr=1,
        self.ser.open()
        now = datetime.datetime.now()
        print('Sucessfully opened connection! {}'.format(now))
        time.sleep(1)


    def _readline(self):
        eol = b'\n'
        leneol = len(eol)
        line = bytearray()
        while True:
            c = self.ser.read(1)
            if c:
                line += c
                if line[-leneol:] == eol:
                    break
            else:
                break
        return bytes(line).decode('utf-8').strip()
    
    def read_value(self):
        connection_open = self.ser.is_open
        while not connection_open:
            time.sleep(60)
            try:
                self.init_port()
            except:
                print('Could not open connection to AML... {}'\
                        .format(datetimme.datetime.now()))
            connection_open = self.ser.is_open
        is_avail = False
        self.ser.reset_input_buffer()
        time.sleep(20)
        self.ser.write(b'*S0')
        #self.ser.flushOutput()

        time.sleep(1)
        while not is_avail:
            #answer = self.ser.read_until().decode('utf-8')
            try:
                answer = self.ser.readline().decode('utf-8')
            except:
                answer = ''
            if not 'GI1' in answer:
                print('TIMED OUT! Restarting connection...')
                self.ser.close()
                time.sleep(1)
                self.init_port()
                self.ser.write(b'*S0')
                time.sleep(1)
                is_avail = False
            else:
                is_avail = True
        self.ser.reset_input_buffer()
        return answer


    def convert_value(self, instring):
        out = instring.split('1A@')[-1].split(',')[0]
        out = out.strip()
        return float(out)
    
=======
>>>>>>> a7a7c8db7042bf8db579998ada1d287a8d9cb8d9
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
        first = self.aml.read_value()
        self.curr_pressure = self.aml.convert_value(first)
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
