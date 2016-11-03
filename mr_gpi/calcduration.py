from mr_gpi.holder import Holder


def calcduration(dict):
    return calcdurationForHolder(*dict.values())


def calcdurationForHolder(*values):
    duration = 0
    for event in values:
        if not isinstance(event, Holder):
            raise TypeError("input(s) should be of type mr_gpi.holder.Holder")

        if event.type == 'delay':
            duration = max(duration, event.delay)
        elif event.type == 'rf':
            duration = max(duration, event.t[0][-1] + event.deadTime)
        elif event.type == 'grad':
            duration = max(duration, event.t[0][-1])
        elif event.type == 'adc':
            adcTime = event.delay + event.numSamples * event.dwell + event.deadTime
            duration = max(duration, adcTime)
        elif event.type == 'trap':
            duration = max(duration, event.riseTime + event.flatTime + event.fallTime)

    return duration
