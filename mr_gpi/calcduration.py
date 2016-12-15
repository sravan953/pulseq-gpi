from mr_gpi.holder import Holder


def calcduration(input_dict):
    return calcholderduration(*input_dict.values())


def calcholderduration(*values):
    duration = 0
    for event in values:
        if not isinstance(event, Holder):
            raise TypeError("input(s) should be of type mr_gpi.holder.Holder")

        if event.type == 'delay':
            duration = max(duration, event.delay)
        elif event.type == 'rf':
            duration = max(duration, event.t[0][-1] + event.dead_time)
        elif event.type == 'grad':
            duration = max(duration, event.t[0][-1])
        elif event.type == 'adc':
            adc_time = event.delay + event.num_samples * event.dwell + event.dead_time
            duration = max(duration, adc_time)
        elif event.type == 'trap':
            duration = max(duration, event.rise_time + event.flat_time + event.fall_time)

    return duration
