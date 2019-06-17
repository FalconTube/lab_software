import time
import socket
import serial

enable_msg = b'E\r'
goto_msg = b'G4000\r'
# Will go to pos x*25 4E3 * 25 = 1E5
def do_tcp():
    TCP_IP = '134.95.66.95'
    TCP_PORT = 1512
    BUFF_SIZE = 80

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(3.0)
    s.connect((TCP_IP, TCP_PORT))
    time.sleep(2)
    s.send(b'S\r')
    time.sleep(2)
    s.send(enable_msg)
    time.sleep(2)
    s.send(goto_msg)
    time.sleep(5)
    # data = s.recv(BUFF_SIZE)
    # s.close()

def do_usb():
    s = serial.Serial('COM8', 19200, parity=serial.PARITY_EVEN, timeout=3)
    time.sleep(1)
    s.write(msg)
    time.sleep(1)
    s.close()

# do_usb()
do_tcp()
