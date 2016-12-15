from mr_gpi.holder import Holder
from mr_gpi.opts import Opts


def makearbitrarygrad(**kwargs):
    channel = kwargs.get("channel", "z")
    system = kwargs.get("system", Opts())
    waveform = kwargs.get("waveform")
    # TODO test
    # maxgradresult = kwargs.get("maxgrad", 0)
    # maxslewresult = kwargs.get("maxslew", 0)

    # maxgrad = maxgradresult if maxgradresult > 0 else system.maxgrad
    # maxslew = maxslewresult if maxslewresult > 0 else system.maxslew

    g = waveform
    slew = (g[1:] - g[0:-1]) / system.grad_raster_time
    grad = Holder()
    grad.type = 'grad'
    grad.channel = channel
    grad.waveform = g
    grad.t = [x * system.grad_raster_time for x in range(len(g) - 1)]
    return grad
