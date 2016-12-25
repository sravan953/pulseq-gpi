import math

from scipy.io import loadmat

from mr_gpi.Sequence.sequence import Sequence
from mr_gpi.calcduration import calcholderduration
from mr_gpi.makeadc import makeadc
from mr_gpi.makearbitrary_grad import makearbitrarygrad
from mr_gpi.makedelay import makedelay
from mr_gpi.makesinc import makesincpulse
from mr_gpi.maketrap import maketrapezoid
from mr_gpi.opts import Opts


fov = 220e-3
dwelltime = 250e-6
kwargs_for_opts = {'max_grad': 30, 'grad_unit': 'mT/m', 'max_slew': 80, 'slew_unit': 'T/m/s', 'adc_dead_time': 10e-6,
                   'rf_dead_time': 10e-6}
lims = Opts(**kwargs_for_opts)
lims.gradRasterTime = dwelltime
kwargs_for_sinc = {'flip_angle': 20 * math.pi / 180, 'duration': 4e-3, 'slice_thickness': 5e-3, 'apodization': 0.5,
                   'time_bw_product': 4, 'system': lims}
[rf, gz] = makesincpulse(**kwargs_for_sinc)

Gx = loadmat('x.mat')
Gx = Gx['Gx']
Gy = loadmat('y.mat')
Gy = Gy['Gy']
kwarg_for_grad = {'channel': 'x', 'waveform': Gx, 'system': lims}
gx = makearbitrarygrad(**kwarg_for_grad)
kwarg_for_grad = {'channel': 'y', 'waveform': Gy, 'system': lims}
gy = makearbitrarygrad(**kwarg_for_grad)
Nx = max(Gx.shape)

kwargs_for_adc = {'num_samples': Nx, 'duration': Nx * dwelltime}
adc = makeadc(**kwargs_for_adc)
kwargs_for_trap = {'channel': 'z', 'area': -gz.area / 2, 'duration': 2e-3}
gzReph = maketrapezoid(**kwargs_for_trap)

TE = 10e-3
TR = 120e-3
delayTE = TE - calcholderduration(*[gz]) / 2 - rf.t[0][-1]
delayTR = TR - calcholderduration(*[gz]) - calcholderduration(*[gx]) - delayTE

seq = Sequence(lims)
seq.addblock(*[rf, gz])
seq.addblock(*[gzReph])
seq.addblock(*[makedelay(delayTE)])
seq.addblock(*[gx, gy, adc])
seq.addblock(*[makedelay(delayTR)])

seq.plot()
