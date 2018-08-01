from korad_class import KoradSerial
import time
import numpy as np
import sys

class UseKorad(KoradSerial):
    def __init__(self):
        try:
            self.korad = KoradSerial('COM5')
            self.korad.output.on()
        except:
            print('Cannot turn on the Korad. Exiting... ')
            sys.exit()
        self.channel = self.korad.channels[0]
        testrange = self.define_range()
        try:
            self.run_range(testrange)
        except KeyboardInterrupt:
            self.finish()
        self.finish()
        

    def define_range(self):
        start = float(input('Insert STARTing current in Amp: '))
        end = float(input('Insert ENDing current in Amp: '))
        ptime = float(input('Insert time, that the process shall take in MINutes: '))
        ptime *= 60 # Conversion so seconds
        steps = np.linspace(start, end, ptime)
        return steps
    
    def run_range(self, steps):
        for i in steps:
            if i >= 1.0:
                i = round(i,3) # Maximal sensisivity 
            else:
                i = round(i,4) # Maximal sensisivity 
            self.channel.current = i
            time.sleep(0.98)
    
    def finish(self):
        print('Turning off output and closing device.')
        self.korad.output.off()
        self.close()


# class KoradSerialTest(TestCase):
#     def __init__(self):
#         self.setUp()
#         self.test_channel1()

#     def setUp(self):
#         self.device = KoradSerial('COMX', True)
#         self.overrideSkippedTests = False

#     def test_channel1(self):
#         """ Test Channel 1's functionality.
#         This test assumes a small load (perhaps 100 ohm) is on the power supply so a small amount of current is drawn.
#         """
#         channel = self.device.channels[0]

#         # Turn off output and ensure that it's reading zeroes.
#         self.device.output.off()
#         time.sleep(1)
#         self.assertEqual(0, channel.output_voltage)
#         self.assertEqual(0, channel.output_current)

#         # Set the current and voltage and ensure it's reporting back correctly.
#         channel.voltage = 1.34
#         channel.current = 0.1234
#         self.assertAlmostEqual(1.34, channel.voltage, 2)
#         self.assertAlmostEqual(0.1234, channel.current, 4)

#         # Set a different current and voltage to ensure that we're not reading old data.
#         channel.voltage = 1.30
#         channel.current = 0.123
#         self.assertAlmostEqual(1.30, channel.voltage, 2)
#         self.assertAlmostEqual(0.123, channel.current, 3)

#         # Turn on the output and ensure that current is flowing across the small load.
#         self.device.output.on()
#         time.sleep(1)
#         self.assertAlmostEqual(1.30, channel.output_voltage, 2)
#         self.assertLess(0, channel.output_current)

#         self.device.output.off()
#     # channel.voltage = 0.1
#     # print(channel.output_voltage)

if __name__ == "__main__":
    k = UseKorad()