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
        self.addWidget('TextBox', 'System limits')

        # IO Ports
        self.addOutPort('output', 'DICT')

        return 0

    def compute(self):
        try:
            out_dict = {}
            max_grad = float(self.getVal('Maximum Gradient (mT/m)'))
            max_slew = float(self.getVal('Maximum Slew Rate (T/m/s)'))
            te = float(self.getVal('Repetition Time (s)'))
            tr = float(self.getVal('Echo Time (s)'))
            fov = float(self.getVal('Field of View'))
            Nx = int(self.getVal('Nx'))
            Ny = int(self.getVal('Ny'))
            rise_time = float(self.getVal('Rise Time (s)'))
            rf_dead_time = float(self.getVal('RF Dead Time (s)'))
            adc_dead_time = float(self.getVal('ADC Dead Time (s)'))
            rf_raster_time = float(self.getVal('RF Raster Time (s)'))
            grad_raster_time = float(self.getVal('Gradient Raster Time (s)'))

            kwargs_for_opts = {"max_grad": max_grad, "grad_unit": "mT/m", "max_slew": max_slew, "slew_unit": "T/m/ms",
                               "te": te, "tr": tr, "fov": fov, "Nx": Nx, "Ny": Ny, "rise_time": rise_time,
                               "rf_dead_time": rf_dead_time, "adc_dead_time": adc_dead_time,
                               "rf_raster_time": rf_raster_time, "grad_raster_time": grad_raster_time}
            system = Opts(kwargs_for_opts)
            out_dict['system'] = system

            self.setData('output', out_dict)

            # To display the computed info in the TextBox
            self.setAttr('System limits', val=str(system))

            return 0
        except ValueError:
            return 1