# __author__ = Yannic Falke

from Classes.device_classes import *
from Classes.measurement_class import Measurement


class TwoPt_Jun(Measurement):
    def __init__(self):
        self.gate = Gate(1)
        self.meter = Meter(2, curr_source=0.00005, four_wire=False)
        self.lakeshore = Lakeshore()
        self.ask_savename()
        savestring = "# Time [s], Temperature [K], Resistance [Ohm]"
        self.create_savefile(savestring)
        try:
            self.log_data()
        except KeyboardInterrupt:
            self.finish_measurement()

    def log_data(self):
        r = []
        t = []
        temps = []
        start_time = time.time()
        fig = plt.figure()
        ax = fig.add_subplot(211)
        ax1 = fig.add_subplot(212)
        ax.set_xlabel("Time [s]")
        ax.set_ylabel("Resistance [Ohm]")
        ax1.set_ylabel("Temperature [K]")
        while 1:
            time.sleep(2)
            time_elapsed = time.time() - start_time
            meterV = self.meter.read_voltage()
            meterI = self.meter.read_current()
            temperature = self.lakeshore.read_temp()
            resistance = meterV / meterI
            # Plot values in real time

            temps.append(temperature)
            t.append(time_elapsed)
            r.append(resistance)
            print(
                "Time: {}, R: {}, Temp: {}".format(
                    time_elapsed, resistance, temperature
                )
            )
            # ax.plot(t, r, 'r.')
            # ax1.plot(t, temps, 'k.')

            # plt.tight_layout()
            # plt.draw()
            # plt.pause(0.01)

            self.savefile.write(
                "{}, {}, {} \n".format(time_elapsed, temperature, resistance)
            )


if __name__ == "__main__":
    gs = TwoPt_Jun()

