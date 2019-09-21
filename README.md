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

Hook up the computer to the Data OUT port on the controller. See "SDA 100
Controller Operators Manual"
(https://consumer.steppir.com/wp-content/uploads/2011/10/operations-manual-SDA-100-rev-2-dec-12.pdf)
for details.  The controller must be in auto track mode.

Software usage instructions
---------------------------

Set a new frequency and get the current frequency:

```
import steppir
step = steppir.SteppIR('/dev/ttyUSB0', 9600)
step.set_frequency(14020000)
print(step.get_frequency())
```
