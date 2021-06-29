import serial
import struct
import time


"""
This project was forked from the https://github.com/bjorgan/steppir project.
Thanks to Asgeir Bjorgan for getting this thing started! I've added greatly
to the functonality and robustness of the code since then, but it couldn't
have gotten off the ground without that initial effort.
This library was tested against a SteppIR SDA-100 controller (NOT upgraded
to "Mustang" firmware) set up to control a DB18e antenna.
-- Curt Mills, WE7U


The controller must be in AUTOTRACK mode for most of the commands to work.
Homing/Retracting the elements will take it out of AUTOTRACK mode, you then
must issue an AUTOTRACK ON command or activate a GUI button to re-enable
AUTOTRACK before the controller will accept most commands. When NOT in
AUTOTRACK mode only the CALIBRATE and RETRACT commands will work.

When not in AUTOTRACK mode the controller should NOT track the frequency
of an attached radio either.

For those remote'ing their SteppIR controller: It can remember the state of
the power switch but takes up to 3 minutes while powered-up to memorize the
power state. After three minutes of being powered-up, removing power and
then re-applying it should cause the controller to power back up.

Loss of power while tuning the antenna can get the controller out of sync
with the positioning of the antenna elements. You'll need to issue the
CALIBRATE command in this case.

Before shutting off power to the controller manually, issue the RETRACT (Home)
command. Note that you must issue the AUTOTRACK ON command (or push the button
to enable it on the controller) to regain full remote control afterwards.
Also, if doing this from the GUI you may need to use BAND UP before the unit
starts tuning to the correct frequencies.

Use the Data Out connector for the full feature set. You can perform all
functions below if using that connector. Only use a 3-wire connection at the
DE-9 connector as some of the pins have +5V or TTL levels and you could cause
damage by hooking up a 5/7/9-pin serial cable. I bought an FTDI-based
USB->serial cable with bare wires at one end and trimmed back all wires except
RXD/TXD/GND. I soldered those to a DE-9 female connector and it worked just
fine. The controller can be set to a baud rate of 1200 to 19.2k baud. Setting
a higher baud rate than 19.2k results in an actual setting of 19.2k baud.  For
robustness of the control link I suggest one of the low baud rates.

There can be as much as a 1 second delay from a SET command before variables
are updated as returned from a STATUS command. There should be at least 100ms
between commands sent to the controller. This library includes time delays in
the appropriate places to prevent sending commands to the controller too
quickly. Don't issue the Status command to the controller more often than 10
times per second.

I'm still working on feedback between the library and the GUI so we know
when commands are accepted/completed when the H/W unit is tuning the antenna.
"""



class SteppIR:
    """
    Serial interface for controlling SteppIR controllers like the SDA-100.

    For details on the serial interface, see "Transceiver interface operation
    for Steppir"
    (https://consumer.steppir.com/wp-content/uploads/2011/10/Transceiver-Interface-Operation-5-28-09.pdf).

    Note: The document is no longer available from SteppIR, but versions can
    still be found around the 'net. The most recent one found:
    Transceiver-Interface-Operation-6_23_2011.pdf

    For the SDA-2000 controller there is a protocol document dated 10/09/2018
    that is otherwise similar to the above documents but included a few more
    protocol details that may only be found in the SDA-2000 controller.
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

	The controller returns 11 bytes: We break them out into individual
	parameters and return them to the calling function. This "get_status"
	function is used by all functions in this library that need status
	from the controller.

	This command does NOT retry automatically.

        Parameters:
        -----------
        -none-

        Returns:
        --------
        frequency: int
            Current frequency in Hz

        active_motors
            An 8-bit value specifying motors which are currently "busy".
	    A value of 0xff indicates the controller is in SETUP mode or
	    has just been given a command to process.
		Bit 0x01 Is always a '1'
		Bit 0x02
		Bit 0x04 Appears to indicate AUTOTRACK mode ON/OFF
		Bit 0x08
		Bit 0x10
		Bit 0x20
		Bit 0x40
		Bit 0x80

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

            # Send 3-byte status command
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
            # seeing 0x07 for this parameter when the motors are busy. There are
	    # four bits defined in the docs plus another note that says this byte
	    # will get set to 0xff (all bits set) to acknowledge successful receipt
	    # of a command. For a DB18e antenna there are six stepper motors, most
	    # likely driven in pairs, so that would result in 3 bits being set if
	    # all motors are busy.
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

	Here we send exactly 10 bytes to the controller. This "set_parameters"
	function is used by all other functions in this library that need to send
	something to the controller. Always set a valid frequency when sending
	the set_parameters command.

	This command does NOT retry automatically.

	Requesting status immediately after a command: The controller sets the "ac"
        byte (retrieved via the "get_status" command) to 0xff when it receives a
	valid command string. It clears "ac" (minus the motor busy bits) when it is
	done processing a command. Consider "frequency", "direction", and "ac" bytes
	valid only when "ac" is NOT equal to 0xff. These may be SDA-2000 features
	and not included in the SDA-100 protocol?

	If "direction" is 0xc0, the byte preceeding it (called "pa", always 0x00 in
	the code below) selects antenna pattern 0 through 15. This hasn't been tried
	in the code yet but should correspond to hex numbers 0x00 to 0x0F. 0x00 is
	the default direction for "pa". May be an SDA-2000 only feature?

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
	    0xc0 = Use pattern value in "pa" byte (not implemented in this library yet)

        command: ascii
            '1' = Set frequency and direction
            'R' = Turn ON AUTOTRACK. Needed after Home/Retract to re-enable full control
            'U' = Turn OFF AUTOTRACK
            'S' = Home the antenna (Retract the elements into the hubs)
            'V' = Calibrate the antenna

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

            # Create byte array for the frequency. Note that this creates four
	    # bytes but the first byte will always be 0x00, as the protocol
	    # doc requires.
            hex_frequency = struct.pack('>i', int(frequency))

            cmd2 = bytes(command, 'utf-8')  # Multiple bytes
            cmd3 = cmd2[0]  # 1 byte

            # Steppir "set" command: New frequency, default flags at the end
            #                 0 1   2 3 4 5             6     7                              8                             9 10
            output_string = b'@A' + hex_frequency + b'\x00' + direction.to_bytes(1, 'big') + cmd3.to_bytes(1, 'big') + b'\x00\r'

            self.serial.write(output_string)

            # Needed to assure we don't run commands too close together
            time.sleep(0.1)



    def get_frequency(self):
        """
        Get current frequency in Hz.

	This command retries automatically.

        Parameters:
        -----------
        -none-

        Returns:
        -------
        frequency: int
            Current frequency in Hz
        """

        done = False
        loops = 0
        while (done == False) & (loops < 3):

            loops += 1

            (frequency, active_motors, direction, dir_label, version) = self.get_status()

            if frequency != 0:
                done = True;
            else:
                print("Didn't get frequency, iteration:", loops, frequency, frequency)

        return frequency



    def set_frequency(self, frequency):
        """
        Set new frequency, in Hz.

	This command retries automatically.

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
            time.sleep(0.75)

            # Check frequency and direction to assure they were set correctly.
            (frequency_temp, active_motors, direction, dir_label, version) = self.get_status()

            if frequency == frequency_temp:
                done = True;
            else:
                print("Didn't set frequency, iteration:", loops, frequency, frequency_temp)



    def set_dir_normal(self):
        """
        Set the beam direction to "normal" (0x00) or a vertical antenna to
	its normal wavelength.

	This command retries automatically.

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
            time.sleep(0.75)

            # Check direction to assure it was set correctly
            (frequency_temp, active_motors, direction_temp, dir_label, version) = self.get_status()

            if 0x00 == direction_temp:
                done = True;
            else:
                print("Didn't set direction, iteration:", loops)
 
 

    def set_dir_180(self):
        """
        Set the beam direction to "180" (0x40) from normal.

	This command retries automatically.

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
            time.sleep(0.75)

            # Check direction to assure it was set correctly
            (frequency_temp, active_motors, direction_temp, dir_label, version) = self.get_status()

            if 0x40 == direction_temp:
                done = True;
            else:
                print("Didn't set direction, iteration:", loops)
 
 

    def set_dir_bidirectional(self):
        """
        Set the direction to "Bidirectional" (0x80) (normal and reverse
	directions at the same time).

	This command retries automatically.

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
            time.sleep(0.75)

            # Check direction to assure it was set correctly
            (frequency_temp, active_motors, direction_temp, dir_label, version) = self.get_status()

            if 0x80 == direction_temp:
                done = True;
            else:
                print("Didn't set direction, iteration:", loops)
 


    def set_dir_3_4(self):
        """
        Set a vertical antenna to 3/4 wavelength (0x20). Not applicable to
	beam antennas.

	This command retries automatically.

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
            time.sleep(0.75)

            # Check direction to assure it was set correctly
            (frequency_temp, active_motors, direction_temp, dir_label, version) = self.get_status()

            if 0x20 == direction_temp:
                done = True;
            else:
                print("Didn't set direction, iteration:", loops)
 


    def set_autotrack_ON(self):
        """
        Turn ON AUTOTRACK. Must re-enable using this command after a
	Home/Retract command.

	This command does NOT retry automatically.

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
        Turn OFF AUTOTRACK. With AUTOTRACK off only these commands will be
	accepted by the controller over the serial port:
		AUTOTRACK ON
		CALIBRATE
		RETRACT

	This command does NOT retry automatically.

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
        Retract antenna elements into the controller hubs ("Home").

	This command does NOT retry automatically but it does wait until the motors
	are not busy.

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
        time.sleep(0.75)

        # Retract tapes
        self.set_parameters(frequency, direction, 'S')
   
        done = False
        loops = 0
        while (done == False) & (loops < 60):

            loops += 1
 
            # Wait to assure status gets updated in the controller
            time.sleep(0.75)

            # Check that motors aren't busy
            (frequency_temp, active_motors, direction_temp, dir_label, version) = self.get_status()

            if active_motors == 0x00:
                done = True;
            else:
                print("Motors are busy:", hex(active_motors), "Iteration:", loops)
 


    def calibrate_antenna(self):
        """
        Calibrate the antenna to the controller.

	This command does NOT retry automatically but it does wait until the
	motors are not busy.

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
        time.sleep(0.75)

        # Calibrate the antenna to the controller
        self.set_parameters(frequency, direction, 'V')

        done = False
        loops = 0
        while (done == False) & (loops < 120):

            loops += 1
 
            # Wait to assure status gets updated in the controller
            time.sleep(0.75)

            # Check that motors aren't busy
            (frequency_temp, active_motors, direction_temp, dir_label, version) = self.get_status()

            if active_motors == 0x00:
                done = True;
            else:
                print("Motors are busy:", hex(active_motors), "Iteration:", loops)


