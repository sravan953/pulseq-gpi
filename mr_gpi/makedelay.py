from mr_gpi.holder import Holder


def makedelay(d):
    delay = Holder()
    if d < 0:
        raise ValueError('Delay {:.2f} ms is invalid'.format(d * 1e3))
    delay.type = 'delay'
    delay.delay = d
    return delay
