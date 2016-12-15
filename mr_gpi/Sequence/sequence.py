import numpy as np
from matplotlib import pyplot as plt

import mr_gpi.calcduration
from mr_gpi.Sequence import block
from mr_gpi.Sequence.read import read
from mr_gpi.Sequence.write import write
from mr_gpi.eventlib import EventLibrary
from mr_gpi.opts import Opts


class Sequence:
    def __init__(self, system=Opts()):
        self.system = system
        # EventLibrary.data is a dict
        self.shape_library = EventLibrary()
        self.rf_library = EventLibrary()
        self.grad_library = EventLibrary()
        self.adc_library = EventLibrary()
        self.delay_library = EventLibrary()
        self.block_events = {}
        self.rf_raster_time = self.system.rf_raster_time
        self.grad_raster_time = self.system.grad_raster_time

    def __str__(self):
        s = "Sequence:"
        s += "\nshape_library: " + str(self.shape_library)
        s += "\nrf_library: " + str(self.rf_library)
        s += "\ngrad_library: " + str(self.grad_library)
        s += "\nadc_library: " + str(self.adc_library)
        s += "\ndelay_library: " + str(self.delay_library)
        s += "\nrf_raster_time: " + str(self.rf_raster_time)
        s += "\ngrad_raster_time: " + str(self.grad_raster_time)
        s += "\nblock_events: " + str(self.block_events)
        return s

    def addblock(self, *args):
        block.addblock(self, *args)

    def getblock(self, block_index):
        return block.getblock(self, block_index)

    def read(self, file_path):
        read(self, file_path)

    def write(self, name):
        write(self, name)

    def plot(self):
        fig1, fig2 = plt.figure(1), plt.figure(2)
        f11, f12, f13 = fig1.add_subplot(311), fig1.add_subplot(312), fig1.add_subplot(313)
        f2 = [fig2.add_subplot(311), fig2.add_subplot(312), fig2.add_subplot(313)]
        t0, time_range = 0, [0, np.inf]
        for iB in range(1, len(self.block_events)):
            block = self.getblock(iB)
            is_valid = time_range[0] <= t0 <= time_range[1]
            if is_valid:
                if block is not None:
                    if 'adc' in block:
                        adc = block['adc']
                        t = adc.delay + [(x * adc.dwell) for x in range(0, int(adc.num_samples))]
                        f11.plot((t0 + t), np.zeros(len(t)))
                    if 'rf' in block:
                        rf = block['rf']
                        t = rf.t
                        f12.plot(np.squeeze(t0 + t), abs(rf.signal))
                        f13.plot(np.squeeze(t0 + t), np.angle(rf.signal))
                    grad_channels = ['gx', 'gy', 'gz']
                    for x in range(0, len(grad_channels)):
                        if grad_channels[x] in block:
                            grad = block[grad_channels[x]]
                            if grad.type == 'grad':
                                t = grad.t
                                waveform = 1e-3 * grad.waveform
                            else:
                                t = np.cumsum([0, grad.rise_time, grad.flat_time, grad.fall_time])
                                waveform = [1e-3 * grad.amplitude * x for x in [0, 1, 1, 0]]
                            f2[x].plot(np.squeeze(t0 + t), waveform)
            t0 += mr_gpi.calcduration.calcduration(block)

        f11.set_ylabel('adc')
        f12.set_ylabel('rf mag hz')
        f13.set_ylabel('rf phase rad')
        [f2[x].set_ylabel(grad_channels[x]) for x in range(3)]
        plt.show()
