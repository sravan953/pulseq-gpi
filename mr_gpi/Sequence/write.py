import numpy as np


def write(self, name):
    outputFile = open(name, 'w')
    outputFile.write("# Pulseq sequence file\n")
    outputFile.write("# Created by GPI Lab\n\n")
    outputFile.write("# Format of blocks:\n")
    outputFile.write("#  #  D RF  GX  GY  GZ ADC\n")
    outputFile.write("[BLOCKS]\n")
    idFormatWidth = len(str(len(self.blockEvents)))
    idFormatStr = '{:>' + str(idFormatWidth) + '}'
    idFormatStr += ' {:>2.0f} {:>2.0f} {:>3.0f} {:>3.0f} {:>3.0f} {:>2.0f}\n'
    for i in range(0, len(self.blockEvents)):
        s = idFormatStr.format(*np.insert(self.blockEvents[i + 1].astype(int), 0, (i + 1)))
        outputFile.write(s)
    outputFile.write('\n')

    outputFile.write('# Format of RF events:\n')
    outputFile.write('# id amplitude mag_id phase_id freq phase\n')
    outputFile.write('# ..        Hz   ....     ....   Hz   rad\n')
    outputFile.write('[RF]\n')
    rfLibKeys = self.rfLibrary.keys
    idFormatStr = '{:>1.0f} {:>12.3f} {:>1.0f} {:>1.0f} {:>1.0f} {:>1.0f}\n'
    for k in rfLibKeys.keys():
        libData = self.rfLibrary.data[k][0:5]
        s = idFormatStr.format(*np.insert(libData, 0, k))
        outputFile.write(s)
    outputFile.write('\n')

    gradLibValues = np.array(list(self.gradLibrary.type.values()))
    arbGradMask = np.where(gradLibValues == 'g')[0] + 1
    trapGradMask = np.where(gradLibValues == 't')[0] + 1

    if any(arbGradMask):
        for x in arbGradMask:
            if x != 0:
                outputFile.write('# Format of arbitrary gradients:\n')
                outputFile.write('# id amplitude shape_id\n')
                outputFile.write('# ..      Hz/m     ....\n')
                outputFile.write('[GRADIENTS]\n')
                keys = self.gradLibrary.keys
                idFormatStr = '{:>1.0f} {:>12.0f} {:>1.0f} \n'
                for k in keys[arbGradMask]:
                    s = idFormatStr.format(*np.insert(self.gradLibrary.data[k], 0, k))
                    outputFile.write(s)
                outputFile.write('\n')

    if any(trapGradMask):
        outputFile.write('# Format of trapezoid gradients:\n')
        outputFile.write('# id amplitude rise flat fall\n')
        outputFile.write('# ..      Hz/m   us   us   us\n')
        outputFile.write('[TRAP]\n')
        for x in trapGradMask:
            if x != 0:
                keys = self.gradLibrary.keys
                idFormatStr = '{:>2.0f} {:>12.1f} {:>3.0f} {:>4.0f} {:>3.0f}\n'
                k = keys[x]
                data = self.gradLibrary.data[k]
                data = np.reshape(data, (1, data.shape[0]))
                data[0][1:] = np.round(1e6 * data[0][1:])
                data = np.round(data, decimals=1)
                s = idFormatStr.format(*np.insert(data, 0, k))
                outputFile.write(s)
        outputFile.write('\n')

    if len(self.adcLibrary.keys) != 0:
        outputFile.write('# Format of ADC events:\n')
        outputFile.write('# id num dwell delay freq phase\n')
        outputFile.write('# ..  ..    ns    us   Hz   rad\n')
        outputFile.write('[ADC]\n')
        keys = self.adcLibrary.keys
        idFormatStr = '{:>2.0f} {:>3.0f} {:>6.0f} {:>3.0f} {:>.0f} {:>.0f}\n'
        for k in keys.values():
            data = np.multiply(self.adcLibrary.data[k][0:5], [1, 1e9, 1e6, 1, 1])
            s = idFormatStr.format(*np.insert(data, 0, k))
            outputFile.write(s)
    outputFile.write('\n')

    if len(self.delayLibrary.keys) != 0:
        outputFile.write('# Format of delays:\n')
        outputFile.write('# id delay (us)\n')
        outputFile.write('[DELAYS]\n')
        keys = self.delayLibrary.keys
        idFormatStr = '{:>.0f} {:>.0f}\n'
        for k in keys.values():
            data = np.round(1e6 * self.delayLibrary.data[k])
            s = idFormatStr.format(*np.insert(data, 0, k))
            outputFile.write(s)
        outputFile.write('\n')

    if len(self.shapeLibrary.keys) != 0:
        outputFile.write('# Sequence Shapes\n')
        outputFile.write('[SHAPES]\n\n')
        keys = self.shapeLibrary.keys
        for k in keys.values():
            shape_data = self.shapeLibrary.data[k]
            s = 'shape_id {:>.0f}\n'
            s = s.format(k)
            outputFile.write(s)
            s = 'num_samples {:>.0f}\n'
            print(shape_data.shape)
            s = s.format(shape_data[0][0])
            outputFile.write(s)
            s = '{:g}\n'
            for x in shape_data[0][1:]:
                s1 = s.format(x)
                outputFile.write(s1)
            outputFile.write('\n')
