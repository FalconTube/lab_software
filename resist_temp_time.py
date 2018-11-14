# __author__ = Yannic Falke

from Classes.device_classes import *
from Classes.measurement_class import Measurement


class Logger(Measurement):
    def __init__(self):
        # self.gate = Gate(1)
        # self.meter = Meter(2, four_wire=False, curr_source=1E-6)
        self.meter = Lockin()

        self.lakeshore = Lakeshore()
        self.ask_savename()
        savestring = "# time[s], Voltage[V], R[Ohms], temperature[K]"
        self.create_savefile(savestring)

        try:
            self.log_data()
        except KeyboardInterrupt:
            self.finish_measurement()

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
        while 1:
            time.sleep(3)
            time_elapsed = time.time() - start_time
            meterV = self.meter.read_voltage()
            # meterI = self.meter.read_current()
            meterI = 1E-6 # ampere
            temperature = self.lakeshore.read_temp()
            resistance = meterV / meterI * four_point_fac
            # Plot values in real time

            temps.append(temperature)
            t.append(time_elapsed)
            r.append(resistance)
            v.append(meterV)
            print(
                "Time: {}, Voltage: {}, R: {}, Temp: {}".format(
                    time_elapsed, voltage, resistance, temperature
                )
            )
            # ax.plot(t, r, 'r.')
            # ax1.plot(t, temps, 'k.')

            # plt.tight_layout()
            # plt.draw()
            # plt.pause(0.01)
            self.savefile.write(
                "{}, {}, {}, {} \n".format(time_elapsed, voltage, resistance, temperature)
            )


if __name__ == "__main__":
    logger = Logger()
