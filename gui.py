#!/usr/bin/env python3

# A Python/Tkinter GUI which roughly simulates a SteppIR SDA-100 controller.


import tkinter as tk
import steppir
import time


class Application(tk.Frame):


    # Class variables
    frequency = 0



    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.grid()
        #self.place()
        self.create_widgets()
        (frequency) = step.get_frequency()
        freq_mhz = frequency / 1000000
        self.display.config(text="%5.3f MHz" % freq_mhz)
        (frequency) = step.get_frequency()
        freq_mhz = frequency / 1000000
        print("Frequency %5.3f MHz" % freq_mhz)
        self.display.config(text="%5.3f MHz" % freq_mhz)



    def create_widgets(self):

        self.display = tk.Label(self, text="Display", font=("Arial", 20), height=2, fg="White", bg="Black")
 
        self.display.place(x=0, y=0)

#        self.led_tuning = tk.Label(self, text="Tuning", width=5, height=1, fg="Grey")
#        self.led_tuning.grid(row=0, column=3)

        self.button_autotrack_on = tk.Button(self, text="Autotrack ON", width=8, fg="White", bg="orange3", command=self.autotrack_on)
        self.button_autotrack_on.grid(row=0, column=2)

        self.button_autotrack_off = tk.Button(self, text="Autotrack OFF", width=8, fg="White", bg="orange3", command=self.autotrack_off)
        self.button_autotrack_off.grid(row=1, column=2)

        self.button_retract = tk.Button(self, text="Retract", width=8, fg="White", bg="orange3", command=self.retract)
        self.button_retract.grid(row=1, column=3)

        self.button_direction_normal = tk.Button(self, text="Norm", width=8, fg="White", bg="medium sea green", command=self.direction_normal)
        self.button_direction_normal.grid(row=2, column=0)

        self.button_direction_180 = tk.Button(self, text="180°", width=8, fg="White", bg="medium sea green", command=self.direction_180)
        self.button_direction_180.grid(row=2, column=1)

        self.button_direction_bi_3_4 = tk.Button(self, text="Bi(3/4)", width=8, fg="White", bg="medium sea green", command=self.direction_bi)
        self.button_direction_bi_3_4.grid(row=2, column=2)

        self.button_band_up = tk.Button(self, text="Band Up", width=8, fg="White", bg="cornflower blue", command=self.band_up)
        self.button_band_up.grid(row=3, column=0)

        self.button_up_1mhz = tk.Button(self, text="1 MHz Up", width=8, fg="White", bg="cornflower blue", command=self.up_1mhz)
        self.button_up_1mhz.grid(row=3, column=1)

        self.button_up_100khz = tk.Button(self, text="100 kHz Up", width=8, fg="White", bg="cornflower blue", command=self.up_100khz)
        self.button_up_100khz.grid(row=3, column=2)

        self.button_up_10khz = tk.Button(self, text="10 kHz Up", width=8, fg="White", bg="cornflower blue", command=self.up_10khz)
        self.button_up_10khz.grid(row=3, column=3)
 
        self.button_calibrate = tk.Button(self, text="Calibrate", width=8, fg="White", bg="orange3", command=self.calibrate)
        self.button_calibrate.grid(row=2, column=3)
 
        self.button_band_down = tk.Button(self, text="Band Dn", width=8, fg="White", bg="cornflower blue", command=self.band_down)
        self.button_band_down.grid(row=4, column=0)

        self.button_up_1mhz = tk.Button(self, text="1 MHz Dn", width=8, fg="White", bg="cornflower blue", command=self.down_1mhz)
        self.button_up_1mhz.grid(row=4, column=1)

        self.button_down_100khz = tk.Button(self, text="100 kHz Dn", width=8, fg="White", bg="cornflower blue", command=self.down_100khz)
        self.button_down_100khz.grid(row=4, column=2)

        self.button_down_10khz = tk.Button(self, text="10 kHz Dn", width=8, fg="White", bg="cornflower blue", command=self.down_10khz)
        self.button_down_10khz.grid(row=4, column=3)

        self.quit = tk.Button(self, text="Quit", width=8, fg="White", bg="OrangeRed3", command=self.master.destroy)
        self.quit.grid(row=0, column=3)



    # Frequency + 10kHz
    def up_10khz(self):
#        self.led_tuning.config(fg="Red")
        print("frequency + 10 kHz")
        (frequency) = step.get_frequency()
        frequency += 10000
        freq_mhz = frequency / 1000000
        print("New Frequency %5.3f MHz" % freq_mhz)
        step.set_frequency(frequency)
        self.display.config(text="%5.3f MHz" % freq_mhz)
#        self.led_tuning.config(fg="Grey")
 


    # Frequency - 10 kHz
    def down_10khz(self):
#        self.led_tuning.config(fg="Red")
        print("frequency - 10 kHz")
        (frequency) = step.get_frequency()
        frequency -= 10000
        freq_mhz = frequency / 1000000
        print("New Frequency %5.3f MHz" % freq_mhz)
        step.set_frequency(frequency)
        self.display.config(text="%5.3f MHz" % freq_mhz)
#        self.led_tuning.config(fg="Grey")
 


    # Frequency + 100 kHz
    def up_100khz(self):
#        self.led_tuning.config(fg="Red")
        print("frequency + 100 kHz")
        (frequency) = step.get_frequency()
        frequency += 100000
        freq_mhz = frequency / 1000000
        print("New Frequency %5.3f MHz" % freq_mhz)
        step.set_frequency(frequency)
        self.display.config(text="%5.3f MHz" % freq_mhz)
#        self.led_tuning.config(fg="Grey")
 


    # Frequency - 100 kHz
    def down_100khz(self):
#        self.led_tuning.config(fg="Red")
        print("frequency - 100 kHz")
        (frequency) = step.get_frequency()
        frequency -= 100000
        freq_mhz = frequency / 1000000
        print("New Frequency %5.3f MHz" % freq_mhz)
        step.set_frequency(frequency)
        self.display.config(text="%5.3f MHz" % freq_mhz)
#        self.led_tuning.config(fg="Grey")


 
    # Frequency + 1 MHz
    def up_1mhz(self):
#        self.led_tuning.config(fg="Red")
        print("frequency + 1 MHz")
        (frequency) = step.get_frequency()
        frequency += 1000000
        freq_mhz = frequency / 1000000
        print("New Frequency %5.3f MHz" % freq_mhz)
        step.set_frequency(frequency)
        self.display.config(text="%5.3f MHz" % freq_mhz)
#        self.led_tuning.config(fg="Grey")


 
    # Frequency - 1 MHz
    def down_1mhz(self):
#        self.led_tuning.config(fg="Red")
        print("frequency - 1 MHz")
        (frequency) = step.get_frequency()
        frequency -= 1000000
        freq_mhz = frequency / 1000000
        print("New Frequency %5.3f MHz" % freq_mhz)
        step.set_frequency(frequency)
        self.display.config(text="%5.3f MHz" % freq_mhz)
#        self.led_tuning.config(fg="Grey")



    def band_up(self):
#        self.led_tuning.config(fg="Red")
        print("band up")
        (frequency) = step.get_frequency()
        if frequency  <   8000000:  # 40 meters
            frequency =  10100000   # 30 meter bottom
        elif frequency < 11000000:  # 30 meters
            frequency =  14000000   # 20 meter bottom
        elif frequency < 15000000:  # 20 meters
            frequency =  18068000   # 17 meter bottom
        elif frequency < 19000000:  # 17 meters
            frequency =  21000000   # 15 meter bottom
        elif frequency < 22000000:  # 15 meters
            frequency =  24890000   # 12 meter bottom
        elif frequency < 25000000:  # 12 meters
            frequency =  28000000   # 10 meter bottom
        elif frequency < 30000000:  # 10 meters
            frequency =  50000000   # 6 meter bottom
        elif frequency < 55000000:  # 6 meters
            frequency =   7000000   # 40 meter bottom
        freq_mhz = frequency / 1000000
        print("New frequency %5.3f MHz" % freq_mhz)
        step.set_frequency(frequency)
        self.display.config(text="%5.3f MHz" % freq_mhz)
#        self.led_tuning.config(fg="Grey")
 

 
    def band_down(self):
#        self.led_tuning.config(fg="Red")
        print("band down")
        (frequency) = step.get_frequency()
        if frequency >   49000000:  # 6 meters
            frequency =  28000000   # 10 meter bottom
        elif frequency > 27000000:  # 10 meters
            frequency =  24890000   # 12 meter bottom
        elif frequency > 24000000:  # 12 meters
            frequency =  21000000   # 15 meter bottom
        elif frequency > 20000000:  # 15 meters
            frequency =  18068000   # 17 meter bottom
        elif frequency > 17000000:  # 17 meters
            frequency =  14000000   # 20 meter bottom
        elif frequency > 13000000:  # 20 meters
            frequency =  10100000   # 30 meter bottom
        elif frequency > 10000000:  # 30 meters
            frequency =   7000000   # 40 meter bottom
        elif frequency >  6000000:  # 40 meters
            frequency =  50000000   # 6 meter bottom
        freq_mhz = frequency / 1000000
        print("New frequency %5.3f MHz" % freq_mhz)
        step.set_frequency(frequency)
        self.display.config(text="%5.3f MHz" % freq_mhz)
#        self.led_tuning.config(fg="Grey")
 


    def autotrack_on(self):
#        self.led_tuning.config(fg="Red")
        print("autotrack ON")
        step.set_autotrack_ON()
#        self.led_tuning.config(fg="Grey")



    def autotrack_off(self):
#        self.led_tuning.config(fg="Red")
        print("autotrack OFF")
        step.set_autotrack_OFF()
#        self.led_tuning.config(fg="Grey")



    def retract(self):
#        self.led_tuning.config(fg="Red")
        print("retract")
        step.retract_antenna()
#        self.led_tuning.config(fg="Grey")


 
    def calibrate(self):
#        self.led_tuning.config(fg="Red")
        print("calibrate")
        step.calibrate_antenna()
#        self.led_tuning.config(fg="Grey")



    # If frequency = 0, elements are "Homed" 
    def direction_normal(self):
#        self.led_tuning.config(fg="Red")
        print("direction: normal")
        step.set_dir_normal()
        (frequency) = step.get_frequency()
        print("Frequency", frequency)
        self.display.config(text=frequency)
        freq_mhz = frequency / 1000000
        self.display.config(text="%5.3f MHz" % freq_mhz)
#        self.led_tuning.config(fg="Grey")

 

    def direction_180(self):
#        self.led_tuning.config(fg="Red")
        print("direction: 180")
        step.set_dir_180()
        (frequency) = step.get_frequency()
        print("Frequency", frequency)
        self.display.config(text=frequency)
        freq_mhz = frequency / 1000000
        self.display.config(text="%5.3f MHz" % freq_mhz)
#        self.led_tuning.config(fg="Grey")

 

    def direction_bi(self):
#        self.led_tuning.config(fg="Red")
        print("direction: bidirectional")
        step.set_dir_bidirectional()
        (frequency) = step.get_frequency()
        print("Frequency", frequency)
        self.display.config(text=frequency)
        freq_mhz = frequency / 1000000
        self.display.config(text="%5.3f MHz" % freq_mhz)
#        self.led_tuning.config(fg="Grey")



step = steppir.SteppIR('/dev/ttyUSB0',  # port
    1200,   # baudrate
    8,      # bytesize
    'N',    # parity
    1,      # stopbits
    2.0,    # read_timeout
    False,  # xonxoff
    False,  # rtscts
    2.0,    # write_timeout
    False,  # dsrdtr
    None,   # inter_byte_timeout
    None)   # exclusive

root = tk.Tk()
app = Application(master=root)
app.mainloop()


