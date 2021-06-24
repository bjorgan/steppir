import serial
import struct


"""
This project was forked from the https://github.com/bjorgan/steppir project.
Thanks to Asgeir Bjorgan for getting this thing started!
The below was tested with a SteppIR SDA-100 controller.
-- Curt Mills, WE7U


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



    def __init__(self, serial_port, baud_rate):
        """
        Connect to SteppIR controller.

        Parameters:
        -----------
        serial_interface: str
            Path to serial interface, e.g. /dev/ttyUSB0.

        baud_rate: int
            Baud rate, must match baud rate set in controller.
        """
        self.serial = serial.Serial(serial_port, baud_rate)



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

        # Send status command
        self.serial.write(b'?A\r')

        # Controller returns 11-byte string
        message = self.serial.read(11)

        # Bytes at position 2, 3, 4, 5 correspond to frequency, but the first is always 0.
        frequency = struct.unpack('>i', message[2:6])[0]

        # Active Motors. I couldn't figure out the mapping for each motor from
        # the docs. Any info on this mapping would be appreciated.
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
        #print("Freq:", frequency*10, "\tActive Motors:", active_motors, "\tDir:", direction, "\tInterface Vers:", version)

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
            'R' = Turn ON serial frequency update. Needed after Home/Retract to re-enable
            'U' = Turn OFF Serial frequency update
            'S' = Home antenna (Retract tapes)
            'V' = Calibrate antenna

        Returns:
        --------
        -nothing-
        """


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

        # NOTE: Buttons don't aways do what's expected the first time. May need to put the command
        # in a loop and check status, repeating the command if required.

        # NOTE: Sometimes the serial.write function hangs. Need a timeout (and retry?)



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

        get_status(frequency, active_motors, direction, version)
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

        # Fetch current direction
        (frequency_temp, active_motors, direction, dir_label, version) = self.get_status()
    
        # Set frequency and direction
        self.set_parameters(frequency, direction, '1')


 
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

        # Fetch current frequency
        (frequency, active_motors, direction, dir_label, version) = self.get_status()
    
        # Set frequency and direction
        self.set_parameters(frequency, 0x00, '1')

 

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

        # Fetch current frequency
        (frequency, active_motors, direction, dir_label, version) = self.get_status()
    
        # Set frequency and direction
        self.set_parameters(frequency, 0x40, '1')
 


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

        # Fetch current frequency
        (frequency, active_motors, direction, dir_label, version) = self.get_status()
    
        # Set frequency and direction
        self.set_parameters(frequency, 0x80, '1')
 


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
    
        # Set frequency and wavelength
        self.set_parameters(frequency, 0x20, '1')
 

    def set_serial_update_ON(self):
        """
        Turn ON serial frequency update. Must re-enable after a Home/Retract command.

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
 


    def set_serial_update_OFF(self):
        """
        Turn OFF serial frequency update.

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
    
        # Retract tapes
        self.set_parameters(frequency, direction, 'S')


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
    
        # Calibrate the antenna to the controller
        self.set_parameters(frequency, direction, 'V')


