from Classes.device_classes import InficonSQM160

import time

infi = InficonSQM160()
deposit_rate = infi.measure_rate()
print(deposit_rate)

measuring = True
savename = 'Rate_vs_time_YF04.dat'
with open(savename, 'w') as f:
    header = '# Time    Deposit\n'
    init_time = '# {}'.format(time.time())
    f.write(header)
    f.write(init_time)
    init_time = time.time()
    try:
        while measuring == True:
            time.sleep(2)
            deposit_rate = infi.measure_rate()
            now = time.time()
            elapsed = now - init_time
            f.write('{} {} \n'.format(elapsed, deposit_rate))
            print('Time {}, Rate {}'.format(elapsed, deposit_rate))
    except KeyboardInterrupt:
        measuring = False
        pass

    

