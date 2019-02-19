import time
import serial

# configure the serial connections (the parameters differs on the device you are connecting to)
ser = serial.Serial(
    port='COM7',
    baudrate=9600,
    parity=serial.PARITY_NONE,
    stopbits=serial.STOPBITS_ONE,
    bytesize=serial.EIGHTBITS,
    timeout=1,
    rtscts=False,
    dsrdtr=False
)
time.sleep(1)
ser.flushOutput()
ser.flushInput()
for _ in range(60):
    time.sleep(1)
    print(time.time())
    ser.write(b'*IDN?\r\n')
    answer = ser.readline().decode('utf-8')
    print(answer)
ser.close()

