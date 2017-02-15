"""
This is starter code to demonstrate a Gradient Recalled Echo example working as a pure Python implementation.
"""
from math import pi

import numpy as np

from mr_gpi.Sequence.sequence import Sequence
from mr_gpi.calcduration import calcholderduration
from mr_gpi.makeadc import makeadc
from mr_gpi.makedelay import makedelay
from mr_gpi.makesinc import makesincpulse
from mr_gpi.maketrap import maketrapezoid
from mr_gpi.opts import Opts

kwargs_for_opts = {"max_grad": 30, "grad_unit": "mT/m", "max_slew": 170, "slew_unit": "T/m/s"}
system = Opts(**kwargs_for_opts)
seq = Sequence(system)

fov = 220e-3
Nx = 64
Ny = 64
slice_thickness = 5e-3

flip = 15 * pi / 180
kwargs_for_sinc = {"flip_angle": flip, "system": system, "duration": 4e-3, "slice_thickness": slice_thickness,
                   "apodization": 0.5, "time_bw_product": 4}
rf, gz = makesincpulse(**kwargs_for_sinc)
# plt.plot(rf.t[0], rf.signal[0])
# plt.show()

deltak = 1 / fov
kWidth = Nx * deltak
readoutTime = 6.4e-3
kwargs_for_trap = {"channel": 'x', "system": system, "flat_area": kWidth, "flat_time": readoutTime}
gx = maketrapezoid(**kwargs_for_trap)
kwargs_for_adc = {"num_samples": Nx, "duration": gx.flat_time, "delay": gx.rise_time}
adc = makeadc(**kwargs_for_adc)

kwargs_for_trap = {"channel": 'x', "system": system, "area": -gx.area / 2, "duration": 2e-3}
gx_pre = maketrapezoid(**kwargs_for_trap)
kwargs_for_trap = {"channel": 'z', "system": system, "area": -gz.area / 2, "duration": 2e-3}
gz_reph = maketrapezoid(**kwargs_for_trap)
phase_areas = np.array(([x for x in range(0, Ny)]))
phase_areas = (phase_areas - Ny / 2) * deltak

delayTE = 10e-3 - calcholderduration(*[gx_pre]) - calcholderduration(*[rf]) / 2 - calcholderduration(
    *[gx]) / 2
delayTR = 20e-3 - calcholderduration(*[gx_pre]) - calcholderduration(*[rf]) - calcholderduration(
    *[gx]) - delayTE
delay1 = makedelay(delayTE)
delay2 = makedelay(delayTR)

for i in range(Ny):
    seq.add_block(*[rf, gz])
    kwargsForGyPre = {"channel": 'y', "system": system, "area": phase_areas[i], "duration": 2e-3}
    gyPre = maketrapezoid(**kwargsForGyPre)
    seq.add_block(*[gx_pre, gyPre, gz_reph])
    seq.add_block(*[delay1])
    seq.add_block(*[gx, adc])
    seq.add_block(*[delay2])

seq.plot()
# The .seq file will be available inside the /gpi/<user>/pulseq-gpi folder
# seq.write("gre_python.seq")

"""
The following lines of code demonstrate the read-from-seq functionality.
Comment out the preceding lines of code in this file, and uncomment the following lines of code.
"""
# seq = Sequence()
# seq.read('/Users/<user>/gpi/<user>/pulseq-gpi/<file>.seq')
# seq.plot()
