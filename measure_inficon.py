from device_classes import InficonSQM160


infi = InficonSQM160(port='COM7')
deposit_rate = infi.measure_rate()
print(deposit_rate)