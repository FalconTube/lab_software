import time
import serial
import visdom
import numpy as np

class AML():
    def __init__(self):
        self.reading = True
        self.ser = serial.Serial()
        time.sleep(1)
        self.ser.port='COM8'
        self.ser.baudrate=9600
        self.ser.parity=serial.PARITY_NONE
        self.ser.stopbits=serial.STOPBITS_ONE
        self.ser.bytesize=serial.EIGHTBITS
        self.ser.write_timeout=3
        self.ser.timeout=3
        self.ser.open()
        time.sleep(1)
        #self.ser.timeout = 5
        self.v = visdom.Visdom()
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
                    print('break EOL')
                    break
            else:
                print('break no line')
                break
        return bytes(line).decode('utf-8').strip()
    
    def read_value(self):
        self.ser.flushInput()
        time.sleep(10)
        self.ser.write(b'*S0')
        #print('wrote')
        self.ser.flush()
        #print('flushed')

        time.sleep(1)
        answer = self.ser.read_until()
        answer = answer.decode('utf-8')
        #print('answer {}'.format(answer))
        # answer = self._readline()
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
