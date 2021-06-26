Python interface for SteppIR controller
---------------------------------------

Control your SDA100 controller using Python!

Build/install instructions
--------------------------

The Python module is installed locally by:

```
python3 setup.py install --user
```
Note that you don't have to install it to use it with Python scripts.

Hardware usage instructions
---------------------------

See "SDA 100
Controller Operators Manual"
(https://consumer.steppir.com/wp-content/uploads/2011/10/operations-manual-SDA-100-rev-2-dec-12.pdf)
for details.

Hook up the computer to the Data OUT port on the controller.
Use a THREE WIRE CABLE to the DATA OUT port.
Set the controller to AUTOTRACK.
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
set_serial_update_ON()
set_serial_update_OFF()
retract_antenna()
calibrate_antenna()
```

See "steppir.py" for details on each one.

Software usage instructions
---------------------------

There's a new Pyton/Tkinter GUI that roughly simulates a SteppIR SDA-100
controller, those buttons that we can control remotely that is. Try:

```
gui.py
```

Note that if you use the function set_serial_update(), you'll need to keep
reading from the serial buffer constantly, else the buffer will overflow. It
might also mess up the looping constructs for some commands that verify the
status of a command after issuing a "set" command.

After you issue the retract_antenna() command and it completes, you must
manually enable AUTOTRACK on the controller before software can command the
controller again.

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

print(step.get_status())                    # Get status and print

print("Setting frequency")
step.set_parameters(51230000, 0x00, '1')    # Set frequency / direction / command, Normal
#step.set_parameters(51230000, 0x40, '1')   # Set frequency / direction / command, 180
#step.set_parameters(51230000, 0x80, '1')   # Set frequency / direction / command, Bidirectional

#step.set_parameters(51230000, 0x00, 'S')   # Home antenna (retract tapes)
#step.set_parameters(51230000, 0x00, 'V')   # Calibrate antenna

#step.set_parameters(51230000, 0x00, 'R')   # Turn ON serial frequency update
#step.set_parameters(51230000, 0x00, 'U')   # Turn OFF serial frequency update

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


