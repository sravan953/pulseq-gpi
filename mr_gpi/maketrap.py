from math import ceil, sqrt, pow

from mr_gpi.holder import Holder
from mr_gpi.opts import Opts


def maketrapezoid(**kwargs):
    channel = kwargs.get("channel", "z")
    system = kwargs.get("system", Opts())
    durationResult = kwargs.get("duration", 0)
    areaResult = kwargs.get("area", 0)
    flatTimeResult = kwargs.get("flatTime", 0)
    flatAreaResult = kwargs.get("flatArea", 0)
    amplitudeResult = kwargs.get("amplitude", 0)
    maxGradResult = kwargs.get("maxGrad", 0)
    maxSlewResult = kwargs.get("maxSlew", 0)
    riseTimeResult = kwargs.get("riseTime", 0)

    maxSlew = system.maxSlew
    riseTime = system.riseTime
    maxGrad = system.maxGrad

    maxGrad = maxGradResult if maxGradResult > 0 else maxGrad
    maxSlew = maxSlewResult if maxSlewResult > 0 else maxSlew
    riseTime = riseTimeResult if riseTimeResult > 0 else riseTime

    if flatTimeResult > 0:
        amplitude = amplitudeResult if (amplitudeResult != 0) else (flatAreaResult / flatTimeResult)
        if riseTime == 0:
            riseTime = abs(amplitude) / maxSlew
            riseTime = ceil(riseTime / system.gradRasterTime) * system.gradRasterTime
        fallTime, flatTime = riseTime, flatTimeResult
    elif durationResult > 0:
        if amplitudeResult != 0:
            amplitude = amplitudeResult
        else:
            if riseTime == 0:
                dC = 1 / abs(2 * maxSlew) + 1 / abs(2 * maxSlew)
                amplitude = (durationResult - sqrt(pow(durationResult, 2) - 4 * abs(areaResult) * dC)) / (
                    2 * dC)
            else:
                amplitude = areaResult / (durationResult - riseTime)

        if riseTime == 0:
            riseTime = ceil(
                amplitude / maxSlew / system.gradRasterTime) * system.gradRasterTime

        fallTime = riseTime
        flatTime = (durationResult - riseTime - fallTime)

        amplitude = areaResult / (riseTime / 2 + fallTime / 2 + flatTime) if amplitudeResult == 0 else amplitude

    grad = Holder()
    grad.type = 'trap'
    grad.channel = channel
    grad.amplitude = amplitude
    grad.riseTime = riseTime
    grad.flatTime = flatTime
    grad.fallTime = fallTime
    grad.area = amplitude * (flatTime + riseTime / 2 + fallTime / 2)
    grad.flatArea = amplitude * flatTime

    return grad
