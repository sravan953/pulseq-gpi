import mr_gpi.convert


class Opts:
    def __init__(self, **kwargs):
        validGradUnits = ['Hz/m', 'mT/m', 'rad/ms/mm']
        validSlewUnits = ['Hz/m/s', 'mT/m/ms', 'T/m/s', 'rad/ms/mm/ms']
        self.maxGrad = kwargs.get("maxGrad", 30)
        self.maxSlew = kwargs.get("maxSlew", 170)
        self.gradUnit = kwargs.get("gradUnit", validGradUnits[1])
        self.slewUnit = kwargs.get("slewUnit", validSlewUnits[1])

        # If values are not provided in required units, convert
        self.maxGrad = mr_gpi.convert.convert(float(self.maxGrad), self.gradUnit) if self.gradUnit != validGradUnits[
            0] else self.maxGrad
        self.maxSlew = mr_gpi.convert.convert(float(self.maxSlew), self.slewUnit) if self.slewUnit != validSlewUnits[
            0] else self.maxSlew

        self.te = kwargs.get("TE", 0)
        self.tr = kwargs.get("TR", 0)
        self.flip = kwargs.get("flip", 0)
        self.fov = kwargs.get("FOV", 0)
        self.Nx = kwargs.get("Nx", 0)
        self.Ny = kwargs.get("Ny", 0)
        self.riseTime = kwargs.get("riseTime", 0)
        self.rfDeadTime = kwargs.get("rfDeadTime", 0)
        self.adcDeadTime = kwargs.get("adcDeadTime", 0)
        self.rfRasterTime = kwargs.get("rfRasterTime", 1e-6)
        self.gradRasterTime = kwargs.get("gradRasterTime", 10e-6)

    def __str__(self):
        s = "Opts:"
        s += "\nmaxGrad: " + str(self.maxGrad) + str(self.gradUnit)
        s += "\nmaxSlew: " + str(self.maxSlew) + str(self.slewUnit)
        s += "\nTE: " + str(self.te)
        s += "\nTR: " + str(self.tr)
        s += "\nFlip: " + str(self.flip)
        s += "\nFOV: " + str(self.fov)
        s += "\nNx: " + str(self.Nx)
        s += "\nNy: " + str(self.Ny)
        s += "\nriseTime: " + str(self.riseTime)
        s += "\nrfDeadTime: " + str(self.rfDeadTime)
        s += "\nadcDeadTime: " + str(self.adcDeadTime)
        s += "\nrfRasterTime: " + str(self.rfRasterTime)
        s += "\ngradRasterTime: " + str(self.gradRasterTime)
        return s
