import numpy as np

from mr_gpi.eventlib import EventLibrary


def read(self, path):
    inputFile = open(path, 'r')
    self.shapeLibrary = EventLibrary()
    self.rfLibrary = EventLibrary()
    self.gradLibrary = EventLibrary()
    self.adcLibrary = EventLibrary()
    self.delayLibrary = EventLibrary()
    self.blockEvents = {}
    self.rfRasterTime = self.system.rfRasterTime
    self.gradRasterTime = self.system.gradRasterTime

    while True:
        section = skipComments(inputFile)
        if section == -1:
            break
        if section == '[BLOCKS]':
            self.blockEvents = readBlocks(inputFile)
        elif section == '[RF]':
            self.rfLibrary = readEvents(inputFile, 1, None, None)
        elif section == '[GRAD]':
            self.gradLibrary = readEvents(inputFile, 1, 'g', self.gradLibrary)
        elif section == '[TRAP]':
            self.gradLibrary = readEvents(inputFile, [1, 1e-6, 1e-6, 1e-6], 't', self.gradLibrary)
        elif section == '[ADC]':
            self.adcLibrary = readEvents(inputFile, [1, 1e-9, 1e-6, 1, 1], None, None)
        elif section == '[DELAYS]':
            self.delayLibrary = readEvents(inputFile, 1e-6, None, None)
        elif section == '[SHAPES]':
            self.shapeLibrary = readShapes(inputFile)


def readBlocks(inputFile):
    inputFile.readline()
    line = stripLine(inputFile)
    for x in range(len(line)):
        line[x] = float(line[x])

    eventTable = []
    while not (line == '\n' or line[0] == '#'):
        eventRow = []
        for c in line:
            eventRow.append(float(c))
        eventTable.append(eventRow)

        line = stripLine(inputFile)
        # Break here to avoid crash when the while loop condition is evaluated for line != '\n'
        # Crash occurs because spaces have been eliminated
        if len(line) == 0:
            break

    blockEvents = {}
    for x in range(len(eventTable)):
        blockEvents[x + 1] = np.array(eventTable[x])

    return blockEvents


def readEvents(inputFile, scale, type, eventLib):
    scale = 1 if scale is not None else scale
    eventLibrary = eventLib if eventLib is not None else EventLibrary()

    line = stripLine(inputFile)
    for x in range(len(line)):
        line[x] = float(line[x])

    while not (line == '\n' or line[0] == '#'):
        id = line[0]
        data = np.multiply(line, scale)
        eventLibrary.insert(id, data, type)

        line = stripLine(inputFile)
        if line == []:
            break

        for x in range(len(line)):
            line[x] = float(line[x])

    return eventLibrary


def readShapes(inputFile):
    shapeLibrary = EventLibrary()

    stripLine(inputFile)
    line = stripLine(inputFile)

    while not (line == -1 or len(line) == 0 or line[0] != 'shape_id'):
        id = int(line[1])
        line = skipComments(inputFile)
        line = line.split(' ')
        numSamples = line[1]
        data = []
        line = skipComments(inputFile)
        line = line.split(' ')
        while not (len(line) == 0 or line[0] == '#'):
            data.append(float(line[0]))
            line = stripLine(inputFile)
        line = skipComments(inputFile)
        # line could be -1 since -1 is EOF marker, returned from skipComments(inputFile)
        line = line.split(' ') if line != -1 else line
        data.insert(int(numSamples), 0)
        data = np.reshape(data, [1, len(data)])
        shapeLibrary.insert(id, data, None)

    return shapeLibrary


def skipComments(inputFile):
    line = inputFile.readline()
    if line == '':
        return -1
    while line == '\n' or line[0] == '#':
        line = inputFile.readline()
        if line == '':
            return -1
    line = line.strip()
    return line


def stripLine(inputFile):
    # Remove spaces and newline whitespace
    line = inputFile.readline()
    line = line.strip()
    line = line.split(' ')
    while '' in line:
        line.remove('')
    return line
