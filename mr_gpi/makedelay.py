from mr_gpi.holder import Holder


def makedelay(d):
    delay = Holder()
    delay.type = 'delay'
    delay.delay = d
    return delay
