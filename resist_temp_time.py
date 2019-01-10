# __author__ = Yannic Falke

from Classes.device_classes import *
from Classes.measurement_class import Measurement
from math import log as ln

class Logger(Measurement):
    def __init__(self):
        # self.gate = Gate(1)
        # self.meter = Meter(2, four_wire=False, curr_source=1E-6)
        self.meter = Lockin()

        self.lakeshore = Lakeshore()
        self.ask_savename()
        self.ask_autogain_time()
        savestring = "# time[s], Voltage[V], R[Ohms], temperature[K]"
        self.create_savefile(savestring)

        try:
            self.log_data()
        except KeyboardInterrupt:
            self.finish_measurement()
    
    def ask_autogain_time(self):
        self.gain_time = float(self._cache.cache_input(
            'Set time [MIN] after which AUTO GAIN is performed (0 for never): ', 0
        ))
        self.gain_time *= 60

    def log_data(self):
        r = []
        t = []
        v = []
        temps = []
        start_time = time.time()
        # fig = plt.figure()
        # ax = fig.add_subplot(211)
        # ax1 = fig.add_subplot(212)
        # ax.set_xlabel("Time [s]")
        # ax.set_ylabel("Resistance [Ohm]")
        # ax1.set_ylabel("Temperature [K]")
        four_point_fac = np.pi * 2 / ln(2)
        reset_start = time.time()
        while 1:
            time.sleep(1)
            time_elapsed = time.time() - start_time
            reset_time = time.time() - reset_start
            if self.gain_time != 0:
                if reset_time >= self.gain_time:
                    self.meter.auto_gain()
                    time.sleep(10)
                    reset_start = time.time()
            meterV = float(self.meter.read_voltage())
            # meterI = self.meter.read_current()
            meterI = 1E-5 # ampere
            temperature = self.lakeshore.read_temp()
            #resistance = meterV / meterI * four_point_fac           #with van der pauw geometrie
            resistance = meterV / meterI                             #without van der pauw geometrie
            # Plot values in real time

            temps.append(temperature)
            t.append(time_elapsed)
            r.append(resistance)
            v.append(meterV)
            print(
                "Time: {}, Voltage: {}, R: {}, Temp: {}".format(
                    time_elapsed, meterV, resistance, temperature
                )
            )
            # ax.plot(t, r, 'r.')
            # ax1.plot(t, temps, 'k.')

            # plt.tight_layout()
            # plt.draw()
            # plt.pause(0.01)
            self.savefile.write(
                "{}, {}, {}, {} \n".format(time_elapsed, meterV, resistance, temperature)
            )


if __name__ == "__main__":
    logger = Logger()
