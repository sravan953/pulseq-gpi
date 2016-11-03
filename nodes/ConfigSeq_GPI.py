import math

import numpy as np

import gpi
from mr_gpi.maketrap import maketrapezoid
from mr_gpi.opts import Opts


class ExternalNode(gpi.NodeAPI):
    """This node providers options for configuring the properties of the pulse sequence.
    """

    def initUI(self):
        # Widgets
        self.addWidget('StringBox', 'Maximum Gradient (mT/m)', placeholder="maxGrad")
        self.addWidget('StringBox', 'Maximum Slew Rate (T/m/s)', placeholder="maxSlew")
        self.addWidget('StringBox', 'Repetition Time (s)', placeholder="TE")
        self.addWidget('StringBox', 'Echo Time (s)', placeholder="TR")
        self.addWidget('StringBox', 'Flip Angle (deg)', placeholder="alpha")
        self.addWidget('StringBox', 'Field of View', placeholder="fov")
        self.addWidget('StringBox', 'Nx', placeholder="Nx")
        self.addWidget('StringBox', 'Ny', placeholder="Ny")
        self.addWidget('StringBox', 'Rise Time (s)', placeholder="riseTime")
        self.addWidget('StringBox', 'RF Dead Time (s)', placeholder="rfDeadTime")
        self.addWidget('StringBox', 'ADC Dead Time (s)', placeholder="adcDeadTime")
        self.addWidget('StringBox', 'RF Raster Time (s)', placeholder="rfRaster")
        self.addWidget('StringBox', 'Gradient Raster Time (s)', placeholder="gradRaster")

        # IO Ports
        self.addOutPort('sequence_obj', 'DICT')

        return 0

    def compute(self):
        data = {}
        maxGrad = float(self.getVal('Maximum Gradient (mT/m)'))
        maxSlew = float(self.getVal('Maximum Slew Rate (T/m/s)'))
        te = float(self.getVal('Repetition Time (s)'))
        tr = float(self.getVal('Echo Time (s)'))
        # TODO CHECK ALPHA
        alpha = math.radians(float(self.getVal('Flip Angle (deg)')))
        fov = float(self.getVal('Field of View'))
        Nx = int(self.getVal('Nx'))
        Ny = int(self.getVal('Ny'))
        riseTime = float(self.getVal('Rise Time (s)'))
        rfDeadTime = float(self.getVal('RF Dead Time (s)'))
        adcDeadTime = float(self.getVal('ADC Dead Time (s)'))
        rfRasterTime = float(self.getVal('RF Raster Time (s)'))
        gradRasterTime = float(self.getVal('Gradient Raster Time (s)'))
        kwargsForOpts = {"maxGrad": maxGrad, "gradUnit": "mT/m", "maxSlew": maxSlew, "slewUnit": "T/m/ms", "TE": te,
                         "TR": tr, "flip": alpha, "FOV": fov, "Nx": Nx, "Ny": Ny, "riseTime": riseTime,
                         "rfDeadTime": rfDeadTime, "adcDeadTime": adcDeadTime, "rfRasterTime": rfRasterTime,
                         "gradRasterTime": gradRasterTime}
        system = Opts(**kwargsForOpts)
        data['system'] = system

        deltak = 1 / fov
        phaseAreas = np.array(([x for x in range(0, Ny)]))
        phaseAreas = (phaseAreas - Ny / 2) * deltak
        gyPreList = []
        for i in range(Ny):
            kwargsForGyPre = {"channel": 'y', "system": system, "area": phaseAreas[i], "duration": 2e-3}
            gyPre = maketrapezoid(**kwargsForGyPre)
            gyPreList.append(gyPre)
        data['gyPre'] = gyPreList

        self.setData('sequence_obj', data)

        return 0
