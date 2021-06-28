Python interface for SteppIR controller
---------------------------------------

Control your SDA100 controller using Python!

Includes both a Python library and a graphical interface which uses it.

History
-------

This project was forked from the https://github.com/bjorgan/steppir project.
Thanks to Asgeir Bjorgan for getting this thing started! I've added greatly
to the functonality and robustness of the code since then, but it couldn't
have gotten off the ground without that initial effort.
This library was tested against a SteppIR SDA-100 controller (NOT upgraded
to "Mustang" firmware) set up to control a DB18e antenna.
-- Curt Mills, WE7U

For details on the serial interface, see "Transceiver interface operation
for Steppir"
(https://consumer.steppir.com/wp-content/uploads/2011/10/Transceiver-Interface-Operation-5-28-09.pdf).

Note: The document is no longer available from SteppIR, but versions can
still be found around the 'net. The most recent one found:
Transceiver-Interface-Operation-6_23_2011.pdf

For the SDA-2000 controller there is a protocol document dated 10/09/2018
that is otherwise similar to the above documents but included a few more
protocol details that may only be found in the SDA-2000 controller.

Build/install instructions
--------------------------

The Python module is installed locally by:

```
python3 setup.py install --user
```
Note that you don't have to install the library in order to use it from Python scripts. Simply have them in the same directory as your Python script(s) and the script(s) should find the library.

Hardware usage instructions
---------------------------

See "SDA 100
Controller Operators Manual"
(https://consumer.steppir.com/wp-content/uploads/2011/10/operations-manual-SDA-100-rev-2-dec-12.pdf)
for details.

Hook up the computer to the Data OUT port on the controller.
Use a THREE WIRE CABLE to the DATA OUT port.
Set the controller to AUTOTRACK, either by pushing the button manually or
    by issuing the set_autotrack_ON() command from the library.
Set the SDA-100 controller Data Out port to 1200 baud (more bulletproof).

Library Functions
-----------------

```
__init__()
get_status()
set_parameters()
get_frequency()
set_frequency()
set_dir_normal()
set_dir_180()
set_dir_bidirectional()
set_dir_3_4()
set_autotrack_ON()
set_autotrack_OFF()
retract_antenna()
calibrate_antenna()
```

See "steppir.py" for details on each one.

Software usage instructions
---------------------------

Included is a Pyton/Tkinter GUI which roughly simulates a SteppIR SDA-100
controller. At least those buttons we can control remotely. Try:

```
gui.py
```

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

You'll sometimes see messages similar to this:

```
Didn't set direction, iteration: 1
```

That message means that the first time through the loop, the controller didn't
perform the change in direction command. On the next iteration it did perform
the change in direction and the message wasn't seen again. This looping and
status checking is done automatically inside the library.

Example script
--------------

Set frequencies/modes, run through some button selections, calibrate and then
retract the antenna elements:

```
import steppir
import time

# Initialize the module, open the port
step = steppir.SteppIR('/dev/ttyUSB0',  # port
    1200,   # baudrate
    8,      # bytesize
    'N',    # parity
    1,      # stopbits
    2.0,    # read_timeout
    False,  # xonxoff s/w handshaking
    False,  # rtscts h/w handshaking
    2.0,    # write_timeout
    False,  # dsrdtr h/w handshaking
    None,   # inter_byte_timeout
    None)   # exclusive port access

step.set_autotrack_ON()                     # Enable AUTOTRACK mode

print(step.get_status())                    # Get status and print

print("Setting frequency")
step.set_parameters(51230000, 0x00, '1')    # Set frequency / direction / command, Normal
#step.set_parameters(51230000, 0x40, '1')   # Set frequency / direction / command, 180
#step.set_parameters(51230000, 0x80, '1')   # Set frequency / direction / command, Bidirectional

#step.set_parameters(51230000, 0x00, 'S')   # Home antenna (retract tapes)
#step.set_parameters(51230000, 0x00, 'V')   # Calibrate antenna

#step.set_parameters(51230000, 0x00, 'R')   # Turn ON AUTOTRACK
#step.set_parameters(51230000, 0x00, 'U')   # Turn OFF AUTOTRACK

time.sleep(1.0)                             # Delay 1 second

print("Setting frequency")
step.set_frequency(51240000)                # Set frequency

time.sleep(1.0)                             # Delay 1 second

print("Setting direction 180")              # Set direction to 180 degrees
step.set_dir_180()

time.sleep(1.0)                             # Delay 1 second

print("Setting direction bidirectional")
step.set_dir_bidirectional()                # Set direction to bidirectional

time.sleep(1.0)                             # Delay 1 second

print("Setting direction normal")
step.set_dir_normal()                       # Set direction to normal

time.sleep(1.0)                             # Delay 1 second

print(step.get_status())                    # Get status and print

#time.sleep(1.0)                            # Delay 1 second

#print("Calibrating antenna")
#step.calibrate_antenna()                   # Calibrate antenna

#time.sleep(1.0)                            # Delay 1 second

#print("Retracting elements")
#step.retract_antenna()                     # Retract antenna elements
```


