import math

import gpi
import numpy as np

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
        self.addOutPort('output', 'DICT')

        return 0

    def compute(self):
        data = {}
        try:
            max_grad = float(self.getVal('Maximum Gradient (mT/m)'))
            max_slew = float(self.getVal('Maximum Slew Rate (T/m/s)'))
            te = float(self.getVal('Repetition Time (s)'))
            tr = float(self.getVal('Echo Time (s)'))
            alpha = math.radians(float(self.getVal('Flip Angle (deg)')))
            fov = float(self.getVal('Field of View'))
            Nx = int(self.getVal('Nx'))
            Ny = int(self.getVal('Ny'))
            rise_time = float(self.getVal('Rise Time (s)'))
            rf_dead_time = float(self.getVal('RF Dead Time (s)'))
            adc_dead_time = float(self.getVal('ADC Dead Time (s)'))
            rf_raster_time = float(self.getVal('RF Raster Time (s)'))
            grad_raster_time = float(self.getVal('Gradient Raster Time (s)'))

            kwargs_for_opts = {"max_grad": max_grad, "grad_unit": "mT/m", "max_slew": max_slew, "slew_unit": "T/m/ms", "te": te,
                             "tr": tr, "flip": alpha, "fov": fov, "Nx": Nx, "Ny": Ny, "rise_time": rise_time,
                             "rf_dead_time": rf_dead_time, "adc_dead_time": adc_dead_time, "rf_raster_time": rf_raster_time,
                             "grad_raster_time": grad_raster_time}
            system = Opts(**kwargs_for_opts)
            data['system'] = system
            data['gy_pre'] = self.compute_gypre(fov, Ny, system)
            self.setData('output', data)
        except ValueError:
            self.log.node('Please make sure you have input valid data.')

        return 0

    def compute_gypre(self, fov, Ny, system):
        deltak = 1 / fov
        phase_areas = np.array(([x for x in range(0, Ny)]))
        phase_areas = (phase_areas - Ny / 2) * deltak
        gy_pre_list = []
        for i in range(Ny):
            kwargs_for_gy_pre = {"channel": 'y', "system": system, "area": phase_areas[i], "duration": 2e-3}
            gy_pre = maketrapezoid(**kwargs_for_gy_pre)
            gy_pre_list.append(gy_pre)
        return gy_pre_list
