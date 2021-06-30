#!/usr/bin/env python3

# A Python/Tkinter GUI which roughly simulates a SteppIR SDA-100 controller.
#
# This version creates a client socket connection to a radio's CAT port at
# port 29090, and a listening CAT port at 19090 for various clients to connect
# to (Fldigi, Wsjt-x, Js8call, etc). It controls an SDA-100 controller on a
# serial port (which may be remotely located using "socat").


import tkinter as tk
import steppir
import time
from threading import Thread
import socket


RADIO_HOST = "127.0.0.1"
RADIO_CAT_PORT = 21000
#RADIO_CAT_PORT = 19090

CAT_HOST = "127.0.0.1"
CAT_LISTENER_PORT = 19090
#CAT_LISTENER_PORT = 29090




class SteppirApp(tk.Frame):

    # Class variables
    frequency = 0

    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.config(bg="Black")
        self.grid()
        self.create_widgets()
        (frequency) = step.get_frequency()
        freq_mhz = frequency / 1000000
        self.display.config(text="%6.3f MHz" % freq_mhz)
        (frequency) = step.get_frequency()
        freq_mhz = frequency / 1000000
        print("Frequency %5.3f MHz" % freq_mhz)
        self.display.config(text="%6.3f MHz" % freq_mhz)

    def create_widgets(self):

        self.winfo_toplevel().title("SteppIR")

        self.display = tk.Label(self, text="Display", font=("Arial", 20, 'bold'), height=2, fg="White", bg="Black")
 
        self.display.place(x=0, y=0)

        self.button_autotrack_on = tk.Button(self, text="Autotrack On", font=("Arial", 8, 'bold'), width=8, fg="White", bg="slate blue", command=self.autotrack_on)
        self.button_autotrack_on.grid(row=1, column=3)

        self.button_autotrack_off = tk.Button(self, text="Autotrack Off", font=("Arial", 8, 'bold'), width=8, fg="White", bg="slate blue", command=self.autotrack_off)
        self.button_autotrack_off.grid(row=2, column=3)

        self.button_retract = tk.Button(self, text="Retract", font=("Arial", 8, 'bold'), width=8, fg="White", bg="DarkOrange3", command=self.retract)
        self.button_retract.grid(row=0, column=2)

        self.button_direction_normal = tk.Button(self, text="Normal", font=("Arial", 8, 'bold'), width=8, fg="White", bg="medium sea green", command=self.direction_normal)
        self.button_direction_normal.grid(row=2, column=0)

        self.button_direction_180 = tk.Button(self, text="Reverse", font=("Arial", 8, 'bold'), width=8, fg="White", bg="medium sea green", command=self.direction_180)
        self.button_direction_180.grid(row=2, column=1)

        self.button_direction_bi_3_4 = tk.Button(self, text="BiDir(3/4)", font=("Arial", 8, 'bold'), width=8, fg="White", bg="medium sea green", command=self.direction_bi)
        self.button_direction_bi_3_4.grid(row=2, column=2)

        self.button_band_up = tk.Button(self, text="Band Up", font=("Arial", 8, 'bold'), width=8, fg="White", bg="cornflower blue", command=self.band_up)
        self.button_band_up.grid(row=3, column=0)

        self.button_up_1mhz = tk.Button(self, text="1 MHz Up", font=("Arial", 8, 'bold'), width=8, fg="White", bg="cornflower blue", command=self.up_1mhz)
        self.button_up_1mhz.grid(row=3, column=1)

        self.button_up_100khz = tk.Button(self, text="100 kHz Up", font=("Arial", 8, 'bold'), width=8, fg="White", bg="cornflower blue", command=self.up_100khz)
        self.button_up_100khz.grid(row=3, column=2)

        self.button_up_10khz = tk.Button(self, text="10 kHz Up", font=("Arial", 8, 'bold'), width=8, fg="White", bg="cornflower blue", command=self.up_10khz)
        self.button_up_10khz.grid(row=3, column=3)
 
        self.button_calibrate = tk.Button(self, text="Calibrate", font=("Arial", 8, 'bold'), width=8, fg="White", bg="DarkOrange3", command=self.calibrate)
        self.button_calibrate.grid(row=1, column=2)
 
        self.button_band_down = tk.Button(self, text="Band Dn", font=("Arial", 8, 'bold'), width=8, fg="White", bg="cornflower blue", command=self.band_down)
        self.button_band_down.grid(row=4, column=0)

        self.button_up_1mhz = tk.Button(self, text="1 MHz Dn", font=("Arial", 8, 'bold'), width=8, fg="White", bg="cornflower blue", command=self.down_1mhz)
        self.button_up_1mhz.grid(row=4, column=1)

        self.button_down_100khz = tk.Button(self, text="100 kHz Dn", font=("Arial", 8, 'bold'), width=8, fg="White", bg="cornflower blue", command=self.down_100khz)
        self.button_down_100khz.grid(row=4, column=2)

        self.button_down_10khz = tk.Button(self, text="10 kHz Dn", font=("Arial", 8, 'bold'), width=8, fg="White", bg="cornflower blue", command=self.down_10khz)
        self.button_down_10khz.grid(row=4, column=3)

        self.quit = tk.Button(self, text="Quit", font=("Arial", 8, 'bold'), width=8, fg="White", bg="OrangeRed3", command=self.master.destroy)
        self.quit.grid(row=0, column=3)

    # Frequency + 10kHz
    def up_10khz(self):
        print("frequency + 10 kHz")
        (frequency) = step.get_frequency()
        frequency += 10000
        freq_mhz = frequency / 1000000
        print("New Frequency %5.3f MHz" % freq_mhz)
        step.set_frequency(frequency)
        self.display.config(text="%6.3f MHz" % freq_mhz)

    # Frequency - 10 kHz
    def down_10khz(self):
        print("frequency - 10 kHz")
        (frequency) = step.get_frequency()
        frequency -= 10000
        freq_mhz = frequency / 1000000
        print("New Frequency %5.3f MHz" % freq_mhz)
        step.set_frequency(frequency)
        self.display.config(text="%6.3f MHz" % freq_mhz)

    # Frequency + 100 kHz
    def up_100khz(self):
        print("frequency + 100 kHz")
        (frequency) = step.get_frequency()
        frequency += 100000
        freq_mhz = frequency / 1000000
        print("New Frequency %5.3f MHz" % freq_mhz)
        step.set_frequency(frequency)
        self.display.config(text="%6.3f MHz" % freq_mhz)

    # Frequency - 100 kHz
    def down_100khz(self):
        print("frequency - 100 kHz")
        (frequency) = step.get_frequency()
        frequency -= 100000
        freq_mhz = frequency / 1000000
        print("New Frequency %5.3f MHz" % freq_mhz)
        step.set_frequency(frequency)
        self.display.config(text="%6.3f MHz" % freq_mhz)
 
    # Frequency + 1 MHz
    def up_1mhz(self):
        print("frequency + 1 MHz")
        (frequency) = step.get_frequency()
        frequency += 1000000
        freq_mhz = frequency / 1000000
        print("New Frequency %5.3f MHz" % freq_mhz)
        step.set_frequency(frequency)
        self.display.config(text="%6.3f MHz" % freq_mhz)
 
    # Frequency - 1 MHz
    def down_1mhz(self):
        print("frequency - 1 MHz")
        (frequency) = step.get_frequency()
        frequency -= 1000000
        freq_mhz = frequency / 1000000
        print("New Frequency %5.3f MHz" % freq_mhz)
        step.set_frequency(frequency)
        self.display.config(text="%6.3f MHz" % freq_mhz)

    def band_up(self):
        print("band up")
        (frequency) = step.get_frequency()
        if frequency  <   7300001:  # 40 meters
            frequency =  10100000   # 30 meter bottom
        elif frequency < 10150001:  # 30 meters
            frequency =  14000000   # 20 meter bottom
        elif frequency < 14350001:  # 20 meters
            frequency =  18068000   # 17 meter bottom
        elif frequency < 18168001:  # 17 meters
            frequency =  21000000   # 15 meter bottom
        elif frequency < 21450001:  # 15 meters
            frequency =  24890000   # 12 meter bottom
        elif frequency < 24990001:  # 12 meters
            frequency =  28000000   # 10 meter bottom
        elif frequency < 29700001:  # 10 meters
            frequency =  50000000   # 6 meter bottom
        elif frequency < 54000001:  # 6 meters
            frequency =   7000000   # 40 meter bottom
        freq_mhz = frequency / 1000000
        print("New frequency %5.3f MHz" % freq_mhz)
        step.set_frequency(frequency)
        self.display.config(text="%6.3f MHz" % freq_mhz)
 
    def band_down(self):
        print("band down")
        (frequency) = step.get_frequency()
        if frequency >   49999999:  # 6 meters
            frequency =  28000000   # 10 meter bottom
        elif frequency > 27999999:  # 10 meters
            frequency =  24890000   # 12 meter bottom
        elif frequency > 24889999:  # 12 meters
            frequency =  21000000   # 15 meter bottom
        elif frequency > 20999999:  # 15 meters
            frequency =  18068000   # 17 meter bottom
        elif frequency > 18067999:  # 17 meters
            frequency =  14000000   # 20 meter bottom
        elif frequency > 13999999:  # 20 meters
            frequency =  10100000   # 30 meter bottom
        elif frequency > 10099999:  # 30 meters
            frequency =   7000000   # 40 meter bottom
        elif frequency >  6999999:  # 40 meters
            frequency =  50000000   # 6 meter bottom
        freq_mhz = frequency / 1000000
        print("New frequency %5.3f MHz" % freq_mhz)
        step.set_frequency(frequency)
        self.display.config(text="%6.3f MHz" % freq_mhz)

    def autotrack_on(self):
        print("autotrack ON")
        step.set_autotrack_ON()

    def autotrack_off(self):
        print("autotrack OFF")
        step.set_autotrack_OFF()

    def retract(self):
        print("retract")
        step.retract_antenna()
 
    def calibrate(self):
        print("calibrate")
        step.calibrate_antenna()

    # If frequency = 0, elements are "Homed" 
    def direction_normal(self):
        print("direction: normal")
        step.set_dir_normal()
        (frequency) = step.get_frequency()
        print("Frequency", frequency)
        self.display.config(text=frequency)
        freq_mhz = frequency / 1000000
        self.display.config(text="%6.3f MHz" % freq_mhz)

    def direction_180(self):
        print("direction: 180")
        step.set_dir_180()
        (frequency) = step.get_frequency()
        print("Frequency", frequency)
        self.display.config(text=frequency)
        freq_mhz = frequency / 1000000
        self.display.config(text="%6.3f MHz" % freq_mhz)

    def direction_bi(self):
        print("direction: bidirectional")
        step.set_dir_bidirectional()
        (frequency) = step.get_frequency()
        print("Frequency", frequency)
        self.display.config(text=frequency)
        freq_mhz = frequency / 1000000
        self.display.config(text="%6.3f MHz" % freq_mhz)



class RadioCATLoop(Thread):
    # Handles the radio CAT interface. Connects to port with a socket
    # connection. Used to connect to linHPSDR's CAT port.
    #
    # If a frequency string is seen, report that back so the SteppIR can be
    # set to the same frequency.
    #
    # If a frequency string is never seen, add code to periodically query the
    # radio's frequency so it can be sent to the SteppIR if it changes.

    s = 0
    receive_buffer = 0x00

    def __init__(self, process_name):
        super().__init__()
        self.process_name = process_name

    # Run a thread asynchronously
    def run(self):
        self.receive_buffer = 0x00
        print("    Starting Radio CAT listener")
        last_frequency = 0
        while True:
            # Open network port to CAT port of linHPSDR S/W
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as self.s:
#                self.s.settimeout(120.1)   # Timeout for listening in seconds
                try:
                    self.s.connect((RADIO_HOST, RADIO_CAT_PORT))
                    while stop_threads == False:
                        self.receive_buffer = self.s.recv(1024)
#                        print("From RADIO:", self.receive_buffer)
                        key = self.receive_buffer[0:2]  # Byte array
                        if key == b'FA':    # Compare byte array
                            # Found a frequency response
#                            print("Found a frequency response!")
                            f_temp = self.receive_buffer[2:13]
                            frequency = int(f_temp) # Frequency in Hz
                            freq_mhz = frequency / 1000000
                            if last_frequency != frequency:
                                print("    Changing frequency")
                                last_frequency = frequency
                                text="%8.6f MHz" % freq_mhz
                                print('Received', text)
                                print("New Frequency %5.3f MHz" % freq_mhz)
                                # Send new frequency to the SteppIR
#                                step.set_frequency(frequency)
                                # Update the GUI frequency display
                                app.display.config(text="%6.3f MHz" % freq_mhz)

                        # Echo received data out ClientCATLoop server port 
                        if client_CAT_thread:
                            client_CAT_thread.conn.send(self.receive_buffer)
                        else:
                            print("No client thread to send to")

                except socket.timeout:
                    print("    Radio socket timeout")
                    pass
                except:
                    print("    Radio socket problem")
                    raise



class SteppirStatusLoop(Thread):
    # Continuously checks the status of the SteppIR controller and updates
    # status in the GUI to match.

    def __init__(self, process_name):
        super().__init__()
        self.process_name = process_name

    # Run a thread asynchronously
    def run(self):
        while stop_threads == False:
            print("            SteppIR Status Processing")
            time.sleep(1.0)



class ClientCATLoop(Thread):
    # Handles the client CAT interface. Handles connections to port
    # from various clients trying to control the CAT port like: Fldigi,
    # Wsjtx, Js8call, etc. Opens up a listening socket.

    s = 0
    conn = 0
    receive_buffer = 0x00

    def __init__(self, process_name):
        super().__init__()
        self.process_name = process_name

    # Run a listener thread asynchronously
    def run(self):
#        send_buffer = 0x00 
        self.receive_buffer = 0x00
        print("    Starting Client CAT listener")
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as self.s:
#            self.s.settimeout(60.0)   # Timeout for listening in seconds
            self.s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.s.bind((CAT_HOST, CAT_LISTENER_PORT))
            self.s.listen(0) # '0' means to allow no backlog of connections

            # Keep accepting client connections, one after the other
            # unless stop_threads == True
            while stop_threads == False:
                try:
                    self.conn, addr = self.s.accept() # Accept one client connection
                    with self.conn:
                        print('    Connected by', addr)
                        while True: # Keep processing commands until client disconnects
                            self.receive_buffer = self.conn.recv(1024)
#                            print("From CLIENT:", self.receive_buffer)

                            # Send data out the Radio socket (if any)
                            if radio_CAT_thread:
#                            if radio_CAT_thread.s != 0:
                                radio_CAT_thread.s.send(self.receive_buffer)
                            else:
                                print("No radio thread to send to")
 
                            if not self.receive_buffer:
                                break
                            if stop_threads == True:
                                self.stop()

#                            time.sleep(0.1)

                except socket.timeout:
                    print("    Listener socket timeout")
                    pass
                except:
                    print("    Listener socket problem")
                    raise



# Start of main program
#
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

# Start up processing thread(s)
stop_threads = False

client_CAT_thread = ClientCATLoop("Client")
client_CAT_thread.start()

radio_CAT_thread = RadioCATLoop("Radio")
radio_CAT_thread.start()

#steppir_monitor_thread = SteppirStatusLoop("SteppIR")
#steppir_monitor_thread.start()

# Creat/Start GUI main loop
root = tk.Tk()
app = SteppirApp(master=root)
app.mainloop()

# Stop all parallel threads
stop_threads = True
client_CAT_thread.join()
radio_CAT_thread.join()
#steppir_monitor_thread.join()


