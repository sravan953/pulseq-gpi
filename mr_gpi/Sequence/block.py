import numpy as np

from mr_gpi.compress_shape import compressShape
from mr_gpi.decompress_shape import decompressShape
from mr_gpi.holder import Holder


def addblock(self, *args):
    setblock(self, len(self.blockEvents) + 1, *args)


def setblock(self, blockIndex, *args):
    self.blockEvents[blockIndex] = np.zeros(6)
    duration = 0
    for event in args:
        if event.type == 'rf':
            mag = abs(event.signal)
            amplitude = np.max(mag)
            mag = np.divide(mag, amplitude)
            # Following 2 lines of code are workarounds for numpy's divide functions returning NaN when mathematical
            # edge cases are encountered (eg., divide by 0) (fix for line 49)
            nanIndices = np.isnan(mag)
            mag[nanIndices] = 0
            phase = np.angle(event.signal)
            lessThanZeroIndices = np.where(phase < 0)
            phase[lessThanZeroIndices] += 2 * np.pi
            phase /= 2 * np.pi

            magShape = compressShape(mag)
            data = np.array([[magShape.num_samples]])
            data = np.append(data, magShape.data, axis=1)
            magId, found = self.shapeLibrary.find(data)
            if not found:
                self.shapeLibrary.insert(magId, data, None)

            phaseShape = compressShape(phase)
            data = np.array([[magShape.num_samples]])
            data = np.append(data, phaseShape.data, axis=1)
            phaseId, found = self.shapeLibrary.find(data)
            if not found:
                self.shapeLibrary.insert(phaseId, data, None)

            data = np.array([amplitude, magId, phaseId, event.freqOffset, event.phaseOffset, event.deadTime])
            dataId, found = self.rfLibrary.find(data)
            if not found:
                self.rfLibrary.insert(dataId, data, None)

            self.blockEvents[blockIndex][1] = dataId
            duration = max(duration, max(mag.shape) * self.rfRasterTime + event.deadTime)
        elif event.type == 'grad':
            channelNum = ['x', 'y', 'z'].index(event.channel)
            amplitude = max(abs(event.waveform))
            g = event.waveform / amplitude
            shape = compressShape(g)
            data = np.array([[shape.num_samples]])
            data = np.append(data, shape.data, axis=1)
            shapeId, found = self.shapeLibrary.find(data)
            if not found:
                self.shapeLibrary.insert(shapeId, data)
            data = np.array([amplitude, shapeId])
            index, found = self.gradLibrary.find(data)
            if not found:
                self.gradLibrary.insert(index, data, 'g')
            idx = 2 + channelNum
            self.blockEvents[blockIndex][idx] = index
            duration = max(duration, max() * self.gradRasterTime)
        elif event.type == 'trap':
            channelNum = ['x', 'y', 'z'].index(event.channel)
            data = np.array([event.amplitude, event.riseTime, event.flatTime, event.fallTime])
            index, found = self.gradLibrary.find(data)
            if not found:
                self.gradLibrary.insert(index, data, 't')
            idx = 2 + channelNum
            self.blockEvents[blockIndex][idx] = index
            duration = max(duration, event.riseTime + event.flatTime + event.fallTime)
        elif event.type == 'adc':
            data = np.array(
                [event.numSamples, event.dwell, event.delay, event.freqOffset, event.phaseOffset, event.deadTime])
            index, found = self.adcLibrary.find(data)
            if not found:
                self.adcLibrary.insert(index, data, None)
            self.blockEvents[blockIndex][5] = index
            duration = max(duration, event.delay + event.numSamples * event.dwell + event.deadTime)
        elif event.type == 'delay':
            data = np.array([event.delay])
            index, found = self.delayLibrary.find(data)
            if not found:
                self.delayLibrary.insert(index, data, None)
            self.blockEvents[blockIndex][0] = index
            duration = max(duration, event.delay)


def getblock(self, blockIndex):
    block = {}
    eventInd = self.blockEvents[blockIndex]
    if eventInd[0] > 0:
        delay = Holder()
        delay.type = 'delay'
        delay.delay = self.delayLibrary.data[eventInd[0]]
        block['delay'] = delay
    elif eventInd[1] > 0:
        rf = Holder()
        rf.type = 'rf'
        libData = self.rfLibrary.data[eventInd[1]]

        amplitude, magShape, phaseShape = libData[0], libData[1], libData[2]
        shapeData = self.shapeLibrary.data[magShape]
        compressed = Holder()
        compressed.num_samples = shapeData[0][0]
        compressed.data = shapeData[0][1:]
        compressed.data = compressed.data.reshape((1, compressed.data.shape[0]))
        mag = decompressShape(compressed)
        shapeData = self.shapeLibrary.data[phaseShape]
        compressed.num_samples = shapeData[0][0]
        compressed.data = shapeData[0][1:shapeData.shape[1]]
        compressed.data = compressed.data.reshape((1, compressed.data.shape[0]))
        phase = decompressShape(compressed)
        rf.signal = 1j * 2 * np.pi * phase
        rf.signal = amplitude * mag * np.exp(rf.signal)
        rf.t = [(x * self.rfRasterTime) for x in range(1, max(mag.shape) + 1)]
        rf.t = np.reshape(rf.t, (1, len(rf.t)))
        rf.freqOffset = libData[4]
        rf.phaseOffset = libData[5]
        if max(libData.shape) < 6:
            libData = np.append(libData, 0)
        rf.deadTime = libData[5]

        block['rf'] = rf
    gradChannels = ['gx', 'gy', 'gz']
    for i in range(1, len(gradChannels) + 1):
        if eventInd[2 + (i - 1)] > 0:
            grad, compressed = Holder(), Holder()
            type = self.gradLibrary.type[eventInd[2 + (i - 1)]]
            libData = self.gradLibrary.data[eventInd[2 + (i - 1)]]
            grad.type = 'trap' if type == 't' else 'grad'
            grad.channel = gradChannels[i - 1][1]
            if grad.type == 'grad':
                amplitude = libData[0]
                shapeId = libData[1]
                shapeData = self.shapeLibrary.data[shapeId]
                compressed.num_samples = shapeData[0]
                compressed.data = shapeData[0][1:shapeData.shape[1]]
                g = decompressShape(compressed)
                grad.waveform = amplitude * g
                grad.t = np.array(([x for x in range(1, max(g.shape))] * self.gradRasterTime))
            else:
                grad.amplitude, grad.riseTime, grad.flatTime, grad.fallTime = [libData[x] for x in range(4)]
                grad.area = grad.amplitude * (grad.flatTime + grad.riseTime / 2 + grad.fallTime / 2)
                grad.flatArea = grad.amplitude * grad.flatTime
            block[gradChannels[i - 1]] = grad

    if eventInd[5] > 0:
        libData = self.adcLibrary.data[eventInd[5]]
        if max(libData.shape) < 6:
            libData[len(libData) + 1] = 0
        adc = Holder()
        adc.numSamples, adc.dwell, adc.delay, adc.freqOffset, adc.phaseOffset, adc.deadTime = [libData[x] for x in
                                                                                               range(6)]
        adc.type = 'adc'
        block['adc'] = adc
    return block
