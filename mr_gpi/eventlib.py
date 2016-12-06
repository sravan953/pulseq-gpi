import numpy as np


class EventLibrary:
    def __init__(self):
        # size of data is 0x0 because of rangeLen in find()
        self.keys, self.data, self.lengths, self.type = {}, {}, {}, {}

    def __str__(self):
        s = "EventLibrary:"
        s += "\nkeys: " + str(self.keys)
        s += "\ndata: " + str(self.data)
        s += "\nlengths: " + str(self.lengths)
        s += "\ntype: " + str(self.type)
        return s

    def find(self, newData):
        found = False
        keyId = 0

        try:
            rangeLen = len(self.data)
        except ValueError:
            rangeLen = 0
        for i in range(1, rangeLen + 1):
            if (self.lengths[i]) == max(newData.shape) and np.linalg.norm((self.data[i] - newData), ord=2) < 1e-6:
                keyId, found = self.keys[i], True
                return [keyId, found]

        keyId = 1 if (len(self.keys) == 0) else (max(self.keys) + 1)
        return [keyId, found]

    def insert(self, keyId, newData, dataType):
        if not isinstance(newData, np.ndarray):
            newData = np.array(newData)
        self.keys[keyId] = keyId
        self.data[keyId] = newData
        self.lengths[keyId] = max(self.data[keyId].shape)
        self.type[keyId] = dataType
