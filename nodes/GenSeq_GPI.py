import gpi
import numpy as np

from mr_gpi.Sequence.sequence import Sequence
from mr_gpi.calcduration import calcduration


class ExternalNode(gpi.NodeAPI):
    """This node has no widgets since it does not require any configuration. This is a purely computational node- it
    adds the supplied blocks to a Sequence object. The output of this node can be used for plotting, e.g. Matplotlib
    """

    def initUI(self):
        # IO Ports
        self.addInPort(title='sequence_obj_in', type='DICT')
        self.addOutPort(title='sequence_obj_out', type='DICT')
        self.addOutPort(title='adc', type='NPYarray')
        self.addOutPort(title='rf_mag', type='NPYarray')
        self.addOutPort(title='rf_phase', type='NPYarray')
        self.addOutPort(title='trapX', type='NPYarray')
        self.addOutPort(title='trapY', type='NPYarray')
        self.addOutPort(title='trapZ', type='NPYarray')

        return 0

    def compute(self):
        try:
            self.inDict = self.getData('sequence_obj_in')
            self.system = self.inDict['system']
            self.seq = Sequence(self.system)
            gyPre, Ny = self.inDict['gyPre'], self.system.Ny

            self.events, self.eventNames = self.inDict['events'], self.inDict['eventNames']
            for i in range(Ny):
                for j in range(len(self.events)):
                    blockRow, blockNames = self.events[j], self.eventNames[j]
                    if 'GyPre' in blockNames:
                        gyIndex = blockNames.index('GyPre')
                        # GyPre has to be inserted only on the first iteration.
                        # In subsequent iterations, the inserted GyPre value is simply replaced.
                        if i == 0:
                            blockRow.insert(gyIndex, gyPre[i])
                        else:
                            blockRow[gyIndex] = gyPre[i]
                    self.seq.addBlock(*blockRow)
                self.inDict['seq'] = self.seq

            self.setData('sequence_obj_out', self.inDict)
            self.setPlotOutputs()
        except:
            self.log.node("Fatal error occurred.")

        return 0

    def setPlotOutputs(self):
        t0, timeRange = 0, [0, np.inf]
        tAdcPrev, tRfPrev, tGradPrev, tTrapPrev = 0, 0, 0, [0, 0, 0]
        adcValues = rfMagValues = rfPhaseValues = np.array(0)
        tXValues, tYValues, tZValues = np.array(0), np.array(0), np.array(0)

        for iB in range(1, len(self.seq.blockEvents)):
            block = self.seq.getBlock(iB)
            isValid = t0 >= timeRange[0] and t0 <= timeRange[1]
            if isValid:
                if block is not None:
                    if 'adc' in block:
                        adc = block['adc']
                        t = adc.delay + [(x * adc.dwell) for x in range(0, int(adc.numSamples))]
                        tcurr = t0 - tAdcPrev
                        adcDwell = adc.dwell
                        adcValues = np.append(adcValues, np.zeros(tcurr / adcDwell))
                        adcValues = np.append(adcValues, np.ones(len(t)))
                        tAdcPrev = (t0 + t)[-1]
                    if 'rf' in block:
                        rf = block['rf']
                        t = rf.t
                        tcurr = t0 - tRfPrev
                        rfMagValues = np.append(rfMagValues, np.zeros(tcurr / self.system.rfRasterTime))
                        rfMagValues = np.append(rfMagValues, abs(rf.signal))
                        rfPhaseValues = np.append(rfPhaseValues, np.zeros(tcurr / self.system.rfRasterTime))
                        rfPhaseValues = np.append(rfPhaseValues, np.angle(rf.signal))
                        tRfPrev = (t0 + t)[-1][-1]
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
                                chIndex = 'xyz'.index(grad.channel)
                                tcurr = t0 - tTrapPrev[chIndex]
                                if grad.channel == 'x':
                                    tXValues = np.append(tXValues,
                                                         np.zeros(tcurr / self.system.gradRasterTime))
                                    tXValues = np.append(tXValues, waveform)
                                elif grad.channel == 'y':
                                    tYValues = np.append(tYValues,
                                                         np.zeros(tcurr / self.system.gradRasterTime))
                                    tYValues = np.append(tYValues, waveform)
                                elif grad.channel == 'z':
                                    tZValues = np.append(tZValues,
                                                         np.zeros(tcurr / self.system.gradRasterTime))
                                    tZValues = np.append(tZValues, waveform)
                                tTrapPrev[chIndex] = (t0 + t)[-1]
            t0 += calcduration(block)

        # Setting outputs
        # ADC
        adcOutput = np.empty((len(adcValues), 2))
        for x in range(len(adcValues)):
            adcOutput[x][0] = x * adcDwell
            adcOutput[x][1] = adcValues[x]
        self.setData('adc', adcOutput)

        # RF Mag
        rfMagOutput = np.empty((len(rfMagValues), 2))
        for x in range(len(rfMagValues)):
            rfMagOutput[x][0] = x * self.system.rfRasterTime
            rfMagOutput[x][1] = rfMagValues[x]
        self.setData('rf_mag', rfMagOutput)

        # RF Phase
        rfPhOutput = np.empty((len(rfPhaseValues), 2))
        for x in range(len(rfPhaseValues)):
            rfPhOutput[x][0] = x * self.system.rfRasterTime
            rfPhOutput[x][1] = rfPhaseValues[x]
        self.setData('rf_phase', rfPhOutput)

        # TrapX
        tXOutput = np.empty((len(tXValues), 2))
        for x in range(len(tXValues)):
            tXOutput[x][0] = x * self.system.gradRasterTime
            tXOutput[x][1] = tXValues[x]
        self.setData('trapX', tXOutput)

        # TrapY
        tYOutput = np.empty((len(tYValues), 2))
        for x in range(len(tYValues)):
            tYOutput[x][0] = x * self.system.gradRasterTime
            tYOutput[x][1] = tYValues[x]
        self.setData('trapY', tYOutput)

        # TrapZ
        tZOutput = np.empty((len(tZValues), 2))
        for x in range(len(tZValues)):
            tZOutput[x][0] = x * self.system.gradRasterTime
            tZOutput[x][1] = tZValues[x]
        self.setData('trapZ', tZOutput)
