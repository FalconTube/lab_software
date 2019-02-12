import time
import serial

class AML():
    def __init__(self):
        self.reading = True
        self.ser = serial.Serial(
            port='COM8',
            baudrate=9600,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            bytesize=serial.EIGHTBITS,
            timeout=5,
        )
        time.sleep(1)


    def _readline(self):
        eol = b'\r\n'
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

    def get_value(self, instring):
        out = instring.split('1A@')[-1].split(',')[0]
        return float(out)

    def measure(self):
        while self.reading:
            self.ser.write(b'*S0')
            self.ser.flush()
            time.sleep(1)
            answer = self._readline()
            if 'GI1' in answer:
                pressure = self.get_value(answer)
                print(pressure)
            self.reading = False
        self.ser.close()
if __name__ == '__main__':
    A = AML()
    A.measure()
