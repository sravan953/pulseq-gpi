import numpy as np

from mr_gpi.holder import Holder


def compressShape(decompressedShape):
    if decompressedShape.shape[0] != 1:
        raise ValueError("input should be of shape (1,x)")
    if not isinstance(decompressedShape, np.ndarray):
        raise TypeError("input should be of type numpy.ndarray")

    data = np.array([decompressedShape[0][0]])
    data = np.concatenate((data, np.diff(decompressedShape[0])))

    maskChanges = np.array([1])
    diffAsOnes = (abs(np.diff(data)) > 1e-8).astype(int)
    maskChanges = np.concatenate((maskChanges, diffAsOnes))
    # Following 2 lines of code are equivalent to MATLAB's find function
    nonZeroIndices = np.nonzero(maskChanges)
    vals = data[nonZeroIndices].astype(float)
    k = np.array(np.nonzero(np.append(maskChanges, 1)))
    k = k.reshape((1, k.shape[1]))
    n = np.diff(k)[0]

    nExtra = (n - 2).astype(float)
    vals2 = np.copy(vals)
    vals2[np.where(nExtra < 0)] = np.NAN
    nExtra[np.where(nExtra < 0)] = np.NAN
    v = np.array([vals, vals2, nExtra])
    v = np.concatenate(np.hsplit(v, v.shape[1]))
    finiteVals = np.isfinite(v)
    v = v[finiteVals]
    vAbs = abs(v)
    smallestIndices = np.where(vAbs < 1e-10)
    v[smallestIndices] = 0

    s = Holder()
    s.num_samples = decompressedShape.shape[1]
    s.data = v.reshape([1, v.shape[0]])
    return s
