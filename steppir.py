import serial
import struct
import time


"""
This project was forked from the https://github.com/bjorgan/steppir project.
Thanks to Asgeir Bjorgan for getting this thing started!
The below was tested with a SteppIR SDA-100 controller.
-- Curt Mills, WE7U


NOTE: The controller must be in AUTOTRACK mode for serial control to work.
Homing/Retracting the elements will take it out of AUTOTRACK mode. You then
need to issue it the 'R' command to re-enable before other commands will
work again.

NOTE: For those remote'ing their SteppIR controller: It can remember the
state of the power switch but takes up to 3 minutes to memorize the power
state. It should come back on with power applied if you left it on for at
least that amount of time prior to the power being removed.

NOTE: If you're shutting off power to the controller manually, "home"
(retract) the antenna elements prior to doing so.

NOTE: Loss of power while tuning the antenna can get everything out-of-sync
and you'll need to calibrate afterwards.

NOTE: Use the Data Out connector for the full feature set. You can perform
all functions below if using that connector. Only use a 3-wire connection at
the DE-9 connector as some of the pins have +5V or TTL levels and you could
cause damage by hooking up a 5/7/9-pin serial cable. In my case (WE7U) I
bought an FTDI-based USB->serial cable with bare wires at one end and cut
back all wires except for RXD/TXD/GND. I soldered those three wires to a
DE-9 female connector and it worked great. The controller can be set to a
baud rate of 1200 to 19.2k baud. Setting a higher baud rate results in an
actual setting of 19.2k baud.

NOTE: There can be as much as a 1 second delay from a SET command before
variables are updated for a STATUS command. There should also be at least
100ms between commands sent to the controller.
"""



class SteppIR:
    """
    Serial interface for controlling SteppIR controllers like SteppIR SDA 100.

    For details on the serial interface, see "Transceiver interface operation
    for Steppir"
    (https://consumer.steppir.com/wp-content/uploads/2011/10/Transceiver-Interface-Operation-5-28-09.pdf).

    Note: The document is no longer available from SteppIR, but versions can
    still be found around the 'net. The most recent one found:
    Transceiver-Interface-Operation-6_23_2011.pdf
    """

    # Class variables
    serial_port = None
    baud_rate = None
    bytesize = None
    parity = None
    stopbits = None
    read_timeout = None
    xonxoff = None
    rtscts = None
    write_timeout = None
    dsrdtr = None
    inter_byte_timeout = None
    exclusive = None



    def __init__(self, port, baudrate, bytesize, parity, stopbits, read_timeout, xonxoff, rtscts, write_timeout, dsrdtr, inter_byte_timeout, exclusive):
        """
        Set serial parameters.

        Parameters:
        -----------
        serial_interface: str
            Path to serial interface, e.g. /dev/ttyUSB0.

        baud_rate: int
            Baud rate, must match baud rate set in controller.

        bytesize: int
            Should be 8

        parity: str
            Should be 'N'

        stopbits: int
            Should be 1

        read_timeout: float
            Serial read timeout in seconds, float

        xonxoff: Boolean
            Software handshaking, should be False

        rtscts: Boolean
            RTS/CTS hardware handshaking, should be False

        write_timeout: float
            Serial write timeout in seconds, float

        dsrdtr: Boolean
            DSR/DTR Hardware handshaking, should be False

        inter_byte_timeout: float
            Should be None

        exclusive: Boolean
            Serial port exclusive access, should be False
        """

        # Set the Class variables based on the parameters received
        self.serial_port = port
        self.baud_rate = baudrate
        self.bytesize = bytesize
        self.parity = parity
        self.stopbits = stopbits
        self.read_timeout = read_timeout
        self.xonxoff = xonxoff
        self.rtscts = rtscts
        self.write_timeout = write_timeout
        self.dsrdtr = dsrdtr
        self.inter_byte_timeout = inter_byte_timeout
        self.exclusive = exclusive

        # Needed to assure we don't run commands too close together
        time.sleep(0.1)



    def get_status(self):
        """
        Get current parameters from SteppIR controller.

        Parameters:
        -----------
        -none-

        Returns:
        --------
        frequency: int
            Current frequency in Hz

        active_motors
            An 8-bit value specifying motors that are currently "busy"

        direction
            An 8-bit value specifying the direction the antenna is pointing:
                0x00 Normal direction
                0x20 3/4 wave (For vertical antennas only)
                0x40 180 direction from normal
                0x80 Bidirectional antenna pattern

        dir_label
            A printable string version of the direction:
                "Bidirectional"
                "180 Degrees"
                "3/4 Wave" (For vertical antennas only)
                "Normal"

        interface_version
            Two ASCII chars specifying transceiver interface version
        """

        with serial.Serial(self.serial_port, 
            self.baud_rate, 
            self.bytesize, 
            self.parity, 
            self.stopbits, 
            self.read_timeout, 
            self.xonxoff, 
            self.rtscts, 
            self.write_timeout, 
            self.dsrdtr, 
            self.inter_byte_timeout, 
            self.exclusive) as self.serial:

            # Send status command
            self.serial.write(b'?A\r')

            # Controller returns 11-byte string
            message = self.serial.read(11)

            # Needed to assure we don't run commands too close together
            time.sleep(0.1)

            # Bytes at position 2, 3, 4, 5 correspond to frequency, but the first is always 0.
            frequency = struct.unpack('>i', message[2:6])[0]
            frequency = frequency * 10

            # Active Motors. I couldn't figure out the mapping for each motor from
            # the docs. Any info on this mapping would be appreciated. So far I'm
            # seeing 0x07 for this parameter when the motors are busy.
            active_motors = message[6]

            # Direction (or wavelength for verticals)
            direction = message[7] & 0xe0
            if direction == 0x80:
                dir_label = "Bidirectional"
            elif direction == 0x40:
                dir_label = "180 degrees"
            elif direction == 0x20:
                dir_label = "3/4 Wave"
            else: dir_label = "Normal"

            version = message[8:10]

            #print("Message:", hex(message[0]), hex(message[1]), hex(message[2]), hex(message[3]), hex(message[4]), hex(message[5]), hex(message[6]), hex(message[7]), hex(message[8]), hex(message[9]), hex(message[10]))
            #print("Freq:", frequency, "\tActive Motors:", active_motors, "\tDir:", direction, "\tInterface Vers:", version)

            return frequency, active_motors, direction, dir_label, version



    def set_parameters(self, frequency, direction, command ):
        """
        Send parameters to the SteppIR controller.

        Parameters:
        -----------
        frequency: int
            Frequency in Hz

        direction: int
            The direction the antenna is pointing
            0x00 = Normal direction
            0x40 = 180 direction
            0x80 = Bidirectional
            0x20 = 3/4 wave (For vertical antennas only)

        command: ascii
            '1' = Set frequency and direction
            'R' = Turn ON AUTOTRACK. Needed after Home/Retract to re-enable
            'U' = Turn OFF AUTOTRACK
            'S' = Home antenna (Retract tapes)
            'V' = Calibrate antenna

        Returns:
        --------
        -nothing-
        """

        with serial.Serial(self.serial_port, 
            self.baud_rate, 
            self.bytesize, 
            self.parity, 
            self.stopbits, 
            self.read_timeout, 
            self.xonxoff, 
            self.rtscts, 
            self.write_timeout, 
            self.dsrdtr, 
            self.inter_byte_timeout, 
            self.exclusive) as self.serial:
 
            # Scale frequency by 10
            frequency /= 10

            # Create byte array for the frequency
            hex_frequency = struct.pack('>i', int(frequency))

            cmd2 = bytes(command, 'utf-8')  # Multiple bytes
            cmd3 = cmd2[0]  # 1 byte

            # Steppir set command, new frequency, default flags at the end
            #                 0 1   2 3 4 5             6     7                              8                             9 10
            output_string = b'@A' + hex_frequency + b'\x00' + direction.to_bytes(1, 'big') + cmd3.to_bytes(1, 'big') + b'\x00\r'

            self.serial.write(output_string)

            # Needed to assure we don't run commands too close together
            time.sleep(0.1)



    def get_frequency(self):
        """
        Get current frequency.

        Parameters:
        -----------
        -none-

        Returns:
        -------
        frequency: int
            Current frequency in Hz
        """

        (frequency, active_motors, direction, dir_label, version) = self.get_status()
        return frequency



    def set_frequency(self, frequency):
        """
        Set new frequency.

        Parameters:
        -----------
        frequency: int
            Frequency in Hz

        Returns:
        --------
        -nothing-
        """

        # Fetch current frequency
        (frequency_temp, active_motors, direction, dir_label, version) = self.get_status()
  
        done = False 
        loops = 0
        while (done == False) & (loops < 3): 

            loops += 1

            # Set frequency and direction
            self.set_parameters(frequency, direction, '1')

            # Wait to assure status gets updated in the controller
            time.sleep(0.9)

            # Check frequency and direction to assure they were set correctly.
            (frequency_temp, active_motors, direction, dir_label, version) = self.get_status()

            if frequency == frequency_temp:
                done = True;
            else:
                print("Didn't set frequency, iteration:", loops, frequency, frequency_temp)



    def set_dir_normal(self):
        """
        Set the direction to "normal" (0x00).

        Parameters:
        -----------
        -none-

        Returns:
        --------
        -nothing-
        """

        # Fetch current frequency/direction
        (frequency, active_motors, direction, dir_label, version) = self.get_status()

        done = False
        loops = 0
        while (done == False) & (loops < 3):

            loops += 1
    
            # Set frequency and direction
            self.set_parameters(frequency, 0x00, '1')

            # Wait to assure status gets updated in the controller
            time.sleep(0.9)

            # Check direction to assure it was set correctly
            (frequency_temp, active_motors, direction_temp, dir_label, version) = self.get_status()

            if 0x00 == direction_temp:
                done = True;
            else:
                print("Didn't set direction, iteration:", loops)
 
 

    def set_dir_180(self):
        """
        Set the direction to "180" (0x40).

        Parameters:
        -----------
        -none-

        Returns:
        --------
        -nothing-
        """

        # Fetch current frequency/direction
        (frequency, active_motors, direction, dir_label, version) = self.get_status()

        done = False
        loops = 0
        while (done == False) & (loops < 3):

            loops += 1
    
            # Set frequency and direction
            self.set_parameters(frequency, 0x40, '1')
 
            # Wait to assure status gets updated in the controller
            time.sleep(0.9)

            # Check direction to assure it was set correctly
            (frequency_temp, active_motors, direction_temp, dir_label, version) = self.get_status()

            if 0x40 == direction_temp:
                done = True;
            else:
                print("Didn't set direction, iteration:", loops)
 
 

    def set_dir_bidirectional(self):
        """
        Set the direction to "Bidirectional" (0x80).

        Parameters:
        -----------
        -none-

        Returns:
        --------
        -nothing-
        """

        # Fetch current frequency/direction
        (frequency, active_motors, direction, dir_label, version) = self.get_status()
 
        done = False
        loops = 0
        while (done == False) & (loops < 3):

            loops += 1
    
            # Set frequency and direction
            self.set_parameters(frequency, 0x80, '1')
 
            # Wait to assure status gets updated in the controller
            time.sleep(0.9)

            # Check direction to assure it was set correctly
            (frequency_temp, active_motors, direction_temp, dir_label, version) = self.get_status()

            if 0x80 == direction_temp:
                done = True;
            else:
                print("Didn't set direction, iteration:", loops)
 


    def set_dir_3_4(self):
        """
        Set the antenna to 3/4 wavelength (0x20). Only used for vertical antennas.

        Parameters:
        -----------
        -none-

        Returns:
        --------
        -nothing-
        """

        # Fetch current frequency
        (frequency, active_motors, direction, dir_label, version) = self.get_status()
 
        done = False
        loops = 0
        while (done == False) & (loops < 3):

            loops += 1
    
            # Set frequency and wavelength
            self.set_parameters(frequency, 0x20, '1')

            # Wait to assure status gets updated in the controller
            time.sleep(0.9)

            # Check direction to assure it was set correctly
            (frequency_temp, active_motors, direction_temp, dir_label, version) = self.get_status()

            if 0x20 == direction_temp:
                done = True;
            else:
                print("Didn't set direction, iteration:", loops)
 


    def set_autotrack_ON(self):
        """
        Turn ON AUTOTRACK. Must re-enable after a Home/Retract command.

        Parameters:
        -----------
        -none-

        Returns:
        --------
        -nothing-
        """

        # Fetch current frequency and direction
        (frequency, active_motors, direction, dir_label, version) = self.get_status()
    
        # Turn on serial update
        self.set_parameters(frequency, direction, 'R')
 


    def set_autotrack_OFF(self):
        """
        Turn OFF autotrack.

        Parameters:
        -----------
        -none-

        Returns:
        --------
        -nothing-
        """

        # Fetch current frequency and direction
        (frequency, active_motors, direction, dir_label, version) = self.get_status()
    
        # Turn off serial update
        self.set_parameters(frequency, direction, 'U')



    def retract_antenna(self):
        """
        Retract tapes into the controller hubs.

        Parameters:
        -----------
        -none-

        Returns:
        --------
        -nothing-
        """

        # Fetch current frequency and direction
        (frequency, active_motors, direction, dir_label, version) = self.get_status()

        # Wait to assure status gets updated in the controller
        time.sleep(0.9)

        # Retract tapes
        self.set_parameters(frequency, direction, 'S')
   
        done = False
        loops = 0
        while (done == False) & (loops < 60):

            loops += 1
 
            # Wait to assure status gets updated in the controller
            time.sleep(0.9)

            # Check that motors aren't busy
            (frequency_temp, active_motors, direction_temp, dir_label, version) = self.get_status()

            if active_motors == 0x00:
                done = True;
            else:
                print("Motors are busy:", hex(active_motors), "Iteration:", loops)
 


    def calibrate_antenna(self):
        """
        Calibrate the antenna to the controller.

        Parameters:
        -----------
        -none-

        Returns:
        --------
        -nothing-
        """

        # Fetch current frequency and direction
        (frequency, active_motors, direction, dir_label, version) = self.get_status()
 
        # Wait to assure status gets updated in the controller
        time.sleep(0.9)

        # Calibrate the antenna to the controller
        self.set_parameters(frequency, direction, 'V')

        done = False
        loops = 0
        while (done == False) & (loops < 120):

            loops += 1
 
            # Wait to assure status gets updated in the controller
            time.sleep(0.9)

            # Check that motors aren't busy
            (frequency_temp, active_motors, direction_temp, dir_label, version) = self.get_status()

            if active_motors == 0x00:
                done = True;
            else:
                print("Motors are busy:", hex(active_motors), "Iteration:", loops)


