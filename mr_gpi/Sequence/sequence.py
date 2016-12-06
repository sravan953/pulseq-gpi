import numpy as np
from matplotlib import pyplot as plt

import mr_gpi.calcduration
from mr_gpi.Sequence import block
from mr_gpi.Sequence.read import read
from mr_gpi.Sequence.write import write
from mr_gpi.eventlib import EventLibrary


class Sequence:
    def __init__(self, system):
        self.system = system
        # EventLibrary.data is a dict
        self.shapeLibrary = EventLibrary()
        self.rfLibrary = EventLibrary()
        self.gradLibrary = EventLibrary()
        self.adcLibrary = EventLibrary()
        self.delayLibrary = EventLibrary()
        self.blockEvents = {}
        self.rfRasterTime = self.system.rfRasterTime
        self.gradRasterTime = self.system.gradRasterTime

    def __str__(self):
        s = "Sequence:"
        s += "\nshapeLibrary: " + str(self.shapeLibrary)
        s += "\nrfLibrary: " + str(self.rfLibrary)
        s += "\ngradLibrary: " + str(self.gradLibrary)
        s += "\nadcLibrary: " + str(self.adcLibrary)
        s += "\ndelayLibrary: " + str(self.delayLibrary)
        s += "\nrfRasterTime: " + str(self.rfRasterTime)
        s += "\ngradRasterTime: " + str(self.gradRasterTime)
        s += "\nblockEvents: " + str(self.blockEvents)
        return s

    def addBlock(self, *args):
        block.addblock(self, *args)

    def getBlock(self, blockIndex):
        return block.getblock(self, blockIndex)

    def read(self, filePath):
        read(self, filePath)

    def write(self, name):
        write(self, name)

    def plot(self):
        fig1, fig2 = plt.figure(1), plt.figure(2)
        f11, f12, f13 = fig1.add_subplot(311), fig1.add_subplot(312), fig1.add_subplot(313)
        f2 = [fig2.add_subplot(311), fig2.add_subplot(312), fig2.add_subplot(313)]
        t0, timeRange = 0, [0, np.inf]
        for iB in range(1, len(self.blockEvents)):
            block = self.getBlock(iB)
            isValid = t0 >= timeRange[0] and t0 <= timeRange[1]
            if isValid:
                if block is not None:
                    if 'adc' in block:
                        adc = block['adc']
                        t = adc.delay + [(x * adc.dwell) for x in range(0, int(adc.numSamples))]
                        f11.plot((t0 + t), np.zeros(len(t)))
                    if 'rf' in block:
                        rf = block['rf']
                        t = rf.t
                        f12.plot(np.squeeze(t0 + t), abs(rf.signal))
                        f13.plot(np.squeeze(t0 + t), np.angle(rf.signal))
                    gradChannels = ['gx', 'gy', 'gz']
                    for x in range(0, len(gradChannels)):
                        if gradChannels[x] in block:
                            grad = block[gradChannels[x]]
                            if grad.type == 'grad':
                                t = grad.t
                                waveform = 1e-3 * grad.waveform
                            else:
                                t = np.cumsum([0, grad.riseTime, grad.flatTime, grad.fallTime])
                                waveform = [1e-3 * grad.amplitude * x for x in [0, 1, 1, 0]]
                            f2[x].plot(np.squeeze(t0 + t), waveform)
            t0 += mr_gpi.calcduration.calcduration(block)

        f11.set_ylabel('adc')
        f12.set_ylabel('rf mag hz')
        f13.set_ylabel('rf phase rad')
        [f2[x].set_ylabel(gradChannels[x]) for x in range(3)]
        plt.show()

        # def setPlotOutputs(self):
        #     t0, timeRange = 0, [0, np.inf]
        #     tAdcPrev, tRfPrev, tGradPrev = 0, 0, 0
        #     tTrapPrev = [0, 0, 0]
        #     adcValues = rfMagValues = rfPhaseValues = np.array(0)
        #     tXValues, tYValues, tZValues = np.array(0), np.array(0), np.array(0)
        #     for iB in range(1, len(self.blockEvents)):
        #         block = self.getBlock(iB)
        #         isValid = t0 >= timeRange[0] and t0 <= timeRange[1]
        #         if isValid:
        #             if block is not None:
        #                 blockLen = mr_gpi.calcduration.calcduration(block)
        #                 if 'adc' in block:
        #                     adc = block['adc']
        #                     t = adc.delay + [(x * adc.dwell) for x in range(0, int(adc.numSamples))]
        #                     tcurr = t0 - tAdcPrev
        #                     adcDwell = adc.dwell
        #                     adcValues = np.append(adcValues, np.ones(len(t)))
        #                 if 'rf' in block:
        #                     rf = block['rf']
        #                     t = rf.t
        #                     tcurr = t0 - tRfPrev
        #                     rfMagValues = np.append(rfMagValues, np.zeros(tcurr / self.system.rfRasterTime))
        #                     rfMagValues = np.append(rfMagValues, abs(rf.signal))
        #                     rfPhaseValues = np.append(rfPhaseValues, np.zeros(tcurr / self.system.rfRasterTime))
        #                     rfPhaseValues = np.append(rfPhaseValues, np.angle(rf.signal))
        #                     tRfPrev = (t0 + t)[-1][-1]
        #                 gradChannels = ['gx', 'gy', 'gz']
        #                 for x in range(0, len(gradChannels)):
        #                     if gradChannels[x] in block:
        #                         grad = block[gradChannels[x]]
        #                         if grad.type == 'grad':
        #                             t = grad.t
        #                             waveform = 1e-3 * grad.waveform
        #                         else:
        #                             t = np.cumsum([0, grad.riseTime, grad.flatTime, grad.fallTime])
        #                             waveform = [1e-3 * grad.amplitude * x for x in [0, 1, 1, 0]]
        #                             chIndex = 'xyz'.index(grad.channel)
        #                             tcurr = t0 - tTrapPrev[chIndex]
        #                             if grad.channel == 'x':
        #                                 tXValues = np.append(tXValues,
        #                                                      np.zeros(tcurr / self.system.gradRasterTime))
        #                                 tXValues = np.append(tXValues, waveform)
        #                                 tYValues = np.append(tYValues,
        #                                                      np.zeros(tcurr / self.system.gradRasterTime))
        #                                 tZValues = np.append(tZValues,
        #                                                      np.zeros(tcurr / self.system.gradRasterTime))
        #                             elif grad.channel == 'y':
        #                                 tYValues = np.append(tYValues,
        #                                                      np.zeros(tcurr / self.system.gradRasterTime))
        #                                 tYValues = np.append(tYValues, waveform)
        #                                 tXValues = np.append(tXValues,
        #                                                      np.zeros(tcurr / self.system.gradRasterTime))
        #                                 tZValues = np.append(tZValues,
        #                                                      np.zeros(tcurr / self.system.gradRasterTime))
        #                             elif grad.channel == 'z':
        #                                 tZValues = np.append(tZValues,
        #                                                      np.zeros(tcurr / self.system.gradRasterTime))
        #                                 tZValues = np.append(tZValues, waveform)
        #                                 tXValues = np.append(tXValues,
        #                                                      np.zeros(tcurr / self.system.gradRasterTime))
        #                                 tYValues = np.append(tYValues,
        #                                                      np.zeros(tcurr / self.system.gradRasterTime))
        #                             tTrapPrev[chIndex] = (t0 + t)[-1]
        #                             # adcValues = np.append(adcValues, np.zeros(tcurr / self.system.gradRasterTime))
        #                             # rfMagValues = np.append(rfMagValues, np.zeros(tcurr / self.system.gradRasterTime))
        #                             # rfPhaseValues = np.append(rfPhaseValues, np.zeros(tcurr / self.system.gradRasterTime))
        #         t0 += mr_gpi.calcduration.calcduration(block)
        #
        #     # ADC
        #     plt.subplot(6, 1, 1)
        #     plt.plot([x * adcDwell for x in range(len(adcValues))], adcValues)
        #
        #     # RF Mag
        #     plt.subplot(6, 1, 2)
        #     plt.plot([x * self.system.rfRasterTime for x in range(len(rfMagValues))], rfMagValues)
        #
        #     # RF Phase
        #     plt.subplot(6, 1, 3)
        #     plt.plot([x * self.system.rfRasterTime for x in range(len(rfPhaseValues))], rfPhaseValues)
        #
        #     # TrapX
        #     plt.subplot(6, 1, 4)
        #     plt.plot([x * self.system.gradRasterTime for x in range(len(tXValues))], tXValues)
        #
        #     # TrapY
        #     plt.subplot(6, 1, 5)
        #     plt.plot([x * self.system.gradRasterTime for x in range(len(tYValues))], tYValues)
        #
        #     # TrapZ
        #     plt.subplot(6, 1, 6)
        #     plt.plot([x * self.system.gradRasterTime for x in range(len(tZValues))], tZValues)
        #     plt.show()
