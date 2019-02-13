import time
import serial
import visdom
import numpy as np

class AML():
    def __init__(self):
        self.reading = True
        self.ser = serial.Serial(
            port='COM8',
            baudrate=9600,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            bytesize=serial.EIGHTBITS,
            writeTimeout=2,
        )
        #self.ser.timeout = 5
        self.v = visdom.Visdom()
        time.sleep(1)
        self.start_time = time.time()


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
        time.sleep(3)
        self.ser.write(b'*S0\r\n')
        self.ser.flush()
        time.sleep(1)
        answer = self._readline()
        # for i in range(6):
            # time.sleep(0.1)
            # if i == 0:
                # answer = self._readline()
            # else:
                # garbage = self._readline()
        return answer


    def convert_value(self, instring):
        out = instring.split('1A@')[-1].split(',')[0]
        out = out.strip()
        return float(out)
    
    def init_vis_plot(self):
        curr_time = time.time() - self.start_time
        y = np.array([self.curr_pressure])
        self.pressure_plot = self.v.line(y, X=np.array([curr_time]),
                opts=dict(ytickformat='%.1E'))

    def update_vis_plot(self):
        now = time.time() - self.start_time
        y = np.array([self.curr_pressure])
        self.v.line(y, X=np.array([now]), win=self.pressure_plot,
                update='append')

    def measure(self):
        first = self.read_value()
        self.curr_pressure = self.convert_value(first)
        self.init_vis_plot()
        while self.reading:
            answer = self.read_value()
            if 'GI1' in answer:
                self.curr_pressure = self.convert_value(answer)
                print(self.curr_pressure)
                self.update_vis_plot()
        self.ser.close()


if __name__ == '__main__':
    A = AML()
    A.measure()
