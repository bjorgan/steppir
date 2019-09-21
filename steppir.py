import serial
import struct

class SteppIR:
    """
    Serial interface for controlling SteppIR controllers like SteppIR SDA 100.

    For details on the serial interface, see "Transceiver interface operation
    for Steppir"
    (https://consumer.steppir.com/wp-content/uploads/2011/10/Transceiver-Interface-Operation-5-28-09.pdf).
    """

    def __init__(self):
        """
        Connect to SteppIR controller.

        Parameters
        ----------
        serial_interface: str
            Path to serial interface, e.g. /dev/ttyUSB0.
        baud_rate: int
            Baud rate, must match baud rate set in controller.
        """
        self.serial = serial.Serial('/dev/ttyUSB2', 9600)

    def get_frequency(self):
        """
        Get current frequency.

        Returns
        -------
        frequency: int
            Current frequency in Hz
        """

        #send status command
        self.serial.write(b'?A\r')

        #controller returns 11 byte string
        message = self.serial.read(11)

        #bytes at (one-indexed) position 3, 4, 5, 6 correspond to frequency
        frequency = struct.unpack('>i', message[2:6])[0]
        return frequency*10

    def set_frequency(self, freq):
        """
        Set new frequency.

        Parameters
        ----------
        freq: int
            Frequency in Hz
        """

        #scale frequency by 10
        freq /= 10

        #create byte array
        hex_freq = struct.pack('>i', int(freq))

        #steppir set command, new frequency, default flags at the end
        output_string = b'@A' + hex_freq + b'\x00\x179c\r'
        self.serial.write(output_string)
