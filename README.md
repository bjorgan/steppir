Python interface for SteppIR controller
---------------------------------------

Control your SDA100 controller using Python!

Build/install instructions
--------------------------

The Python module is installed locally by:

```
python3 setup.py install --user
```

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


Software usage instructions
---------------------------

Set a new frequency and get the current frequency, run through some button selections:

```
import steppir
import time

# Initialize the module, open the port
# Parameters:
    port
    baudrate
    bytesize
    parity
    stopbits
    read_timeout
    xonxoff
    rtscts
    write_timeout
    dsrdtr
    inter_byte_timeout
    exclusive
step = steppir.SteppIR('/dev/ttyUSB0',
    1200,
    8,
    'N',
    1,
    2.0,
    False,
    False,
    2.0,
    False,
    None,
    None)

print(step.get_status())                     # Get frequency and print

print("Setting frequency")
step.set_parameters(51230000, 0x00, '1')         # Set frequency / direction / command, Normal
#step.set_parameters(51230000, 0x40, '1')         # Set frequency / direction / command, 180
#step.set_parameters(51230000, 0x80, '1')         # Set frequency / direction / command, Bidirectional

#step.set_parameters(51230000, 0x00, 'S')        # Home antenna (retract tapes)
#step.set_parameters(51230000, 0x00, 'V')        # Calibrate antenna

#step.set_parameters(51230000, 0x00, 'R')        # Turn ON serial frequency update
#step.set_parameters(51230000, 0x00, 'U')        # Turn OFF serial frequency update

time.sleep(1.0)

print("Setting frequency")
step.set_frequency(51240000)

time.sleep(1.0)

print("Setting direction 180")
step.set_dir_180()

time.sleep(1.0)

print("Setting direction bidirectional")
step.set_dir_bidirectional()

time.sleep(1.0)

print("Setting direction normal")
step.set_dir_normal()

time.sleep(1.0)

print(step.get_status())                     # Get frequency and print

#time.sleep(1.0)

#print("Calibrating antenna")
#step.calibrate_antenna()

#time.sleep(1.0)

#print("Retracting elements")
#step.retract_antenna()
```


