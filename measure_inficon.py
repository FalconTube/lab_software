from Classes.device_classes import InficonSQM160

import time

infi = InficonSQM160()

for i in range(10):
    deposit_rate = infi.measure_rate()
    thickness = infi.measure_thickness()
    freq = infi.measure_frequency()
    print(deposit_rate, thickness, freq)
    time.sleep(0.5)

# measuring = True
# savename = 'Rate_vs_time_YF04.dat'
# with open(savename, 'w') as f:
#     header = '# Time    Deposit\n'
#     init_time = '# {}'.format(time.time())
#     f.write(header)
#     f.write(init_time)
#     init_time = time.time()
#     try:
#         while measuring == True:
#             time.sleep(2)
#             deposit_rate = infi.measure_rate()
#             now = time.time()
#             elapsed = now - init_time
#             f.write('{} {} \n'.format(elapsed, deposit_rate))
#             print('Time {}, Rate {}'.format(elapsed, deposit_rate))
#     except KeyboardInterrupt:
#         measuring = False
#         pass

    

