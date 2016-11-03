from math import pi


def convert(fromValue, fromUnit):
    gamma, standard = 42.576e6, 0
    # Converting gradient
    if fromUnit == 'Hz/m':
        standard = fromValue
    elif fromUnit == 'mT/m':
        standard = fromValue * 1e-3 * gamma
    elif fromUnit == 'rad/ms/mm':
        standard = fromValue * 1e6 / (2 * pi)
    # Converting slew rate
    elif fromUnit == 'Hz/m/s':
        standard = fromValue
    elif fromUnit == 'mT/m/ms' or 'T/m/s':
        standard = fromValue * gamma
    elif fromUnit == 'rad/ms/mm/ms':
        standard = fromValue * 1e9 / (2 * pi)
    return standard
