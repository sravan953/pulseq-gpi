import numpy as np

from mr_gpi.holder import Holder


def decompress_shape(compressed_shape):
    if compressed_shape.data.shape[0] != 1:
        raise ValueError("input should be of shape (1,x)")
    if not isinstance(compressed_shape, Holder):
        raise TypeError("input should be of type holder.Holder")

    dataPack, numSamples = compressed_shape.data, int(compressed_shape.num_samples)
    w = np.zeros(numSamples)

    countPack, countUnpack = 0, 0
    while countPack < max(dataPack.shape) - 1:

        if dataPack[0][countPack] != dataPack[0][countPack + 1]:
            w[countUnpack] = dataPack[0][countPack]
            countUnpack += 1
            countPack += 1
        else:
            rep = dataPack[0][countPack + 2] + 2
            w[countUnpack:(countUnpack + rep - 1)] = dataPack[0][countPack]
            countPack += 3
            countUnpack += rep

    if countPack == max(dataPack.shape) - 1:
        w[countUnpack] = dataPack[0][countPack]

    w = np.cumsum(w)
    return w
