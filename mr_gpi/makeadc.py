from mr_gpi.holder import Holder
from mr_gpi.opts import Opts


def makeadc(**kwargs):
    numSamples = kwargs.get("numSamples", 0)
    system = kwargs.get("system", Opts())
    dwell = kwargs.get("dwell", 0)
    duration = kwargs.get("duration", 0)
    delay = kwargs.get("delay", 0)
    freqOffset = kwargs.get("freqOffset", 0)
    phaseOffset = kwargs.get("phaseOffset", 0)

    adc = Holder()
    adc.type = 'adc'
    adc.numSamples = numSamples
    adc.dwell = dwell
    adc.delay = delay
    adc.freqOffset = freqOffset
    adc.phaseOffset = phaseOffset
    adc.deadTime = system.adcDeadTime

    if (dwell == 0 and duration == 0) or (dwell > 0 and duration > 0):
        raise Exception("either dwell or duration must be defined")

    adc.dwell = duration / numSamples if duration > 0 else adc.dwell
    adc.duration = dwell * numSamples if dwell > 0 else 0
    return adc
