import numpy as np

from mr_gpi.holder import Holder
from mr_gpi.maketrap import maketrapezoid
from mr_gpi.opts import Opts


def makesincpulse(**kwargs):
    flipAngle = kwargs.get("flipAngle")
    system = kwargs.get("system", Opts())
    duration = kwargs.get("duration", 0)
    freqOffset = kwargs.get("freqOffset", 0)
    phaseOffset = kwargs.get("phaseOffset", 0)
    timeBwProduct = kwargs.get("timeBwProduct", 0)
    apodization = kwargs.get("apodization", 0)
    maxGrad = kwargs.get("maxGrad", 0)
    maxSlew = kwargs.get("maxSlew", 0)
    sliceThickness = kwargs.get("sliceThickness", 0)

    BW = timeBwProduct / duration
    alpha = apodization
    N = int(round(duration / 1e-6))
    t = np.zeros((1, N))
    for x in range(1, N + 1):
        t[0][x - 1] = x * system.rfRasterTime
    tt = t - (duration / 2)
    window = np.zeros((1, tt.shape[1]))
    for x in range(0, tt.shape[1]):
        window[0][x] = 1.0 - alpha + alpha * np.cos(2 * np.pi * tt[0][x] / duration)
    signal = np.multiply(window, np.sinc(BW * tt))
    flip = np.sum(signal) * system.rfRasterTime * 2 * np.pi
    signal = signal * flipAngle / flip

    rf = Holder()
    rf.type = 'rf'
    rf.signal = signal
    rf.t = t
    rf.freqOffset = freqOffset
    rf.phaseOffset = phaseOffset
    rf.deadTime = system.rfDeadTime

    system.maxGrad = maxGrad if maxGrad > 0 else system.maxGrad
    system.maxSlew = maxSlew if maxSlew > 0 else system.maxSlew

    amplitude = BW / sliceThickness
    area = amplitude * duration
    kwargsForTrap = {"channel": 'z', "system": system, "flatTime": duration, "flatArea": area}
    gz = maketrapezoid(**kwargsForTrap)

    fillTime = gz.riseTime
    NfillTime = int(round(fillTime / 1e-6))
    tFill = np.zeros((1, NfillTime))
    for x in range(1, NfillTime + 1):
        tFill[0][x - 1] = x * 1e-6
    temp = np.concatenate((tFill[0], rf.t[0] + tFill[0][-1]))
    temp = temp.reshape((1, len(temp)))
    rf.t = np.resize(rf.t, temp.shape)
    rf.t[0] = temp
    z = np.zeros((1, tFill.shape[1]))
    temp2 = np.concatenate((z[0], rf.signal[0]))
    temp2 = temp2.reshape((1, len(temp2)))
    rf.signal = np.resize(rf.signal, temp2.shape)
    rf.signal[0] = temp2

    if fillTime < rf.deadTime:
        fillTime = rf.deadTime - fillTime
        NfillTime = int(round(fillTime / 1e-6))
        for x in range(1, NfillTime + 1):
            tFill[0][x - 1] = x * 1e-6
        rf.t = np.array(tFill, rf.t + tFill[0][-1])
        z = np.zeros((1, tFill.shape[1]))
        rf.signal = np.concatenate((z[0], rf.signal[0]))

    # Following 2 lines of code are workarounds for numpy returning 3.14... for np.angle(-0.00...)
    negativeZeroIndices = np.where(rf.signal == -0.0)
    rf.signal[negativeZeroIndices] = 0
    return [rf, gz]
