import numpy as np


def write(self, name):
    output_file = open(name, 'w')
    output_file.write("# Pulseq sequence file\n")
    output_file.write("# Created by GPI Lab\n\n")
    output_file.write("# Format of blocks:\n")
    output_file.write("#  #  D RF  GX  GY  GZ ADC\n")
    output_file.write("[BLOCKS]\n")
    idFormatWidth = len(str(len(self.blockEvents)))
    id_format_str = '{:>' + str(idFormatWidth) + '}'
    id_format_str += ' {:>2.0f} {:>2.0f} {:>3.0f} {:>3.0f} {:>3.0f} {:>2.0f}\n'
    for i in range(0, len(self.blockEvents)):
        s = id_format_str.format(*np.insert(self.blockEvents[i + 1].astype(int), 0, (i + 1)))
        output_file.write(s)
    output_file.write('\n')

    output_file.write('# Format of RF events:\n')
    output_file.write('# id amplitude mag_id phase_id freq phase\n')
    output_file.write('# ..        Hz   ....     ....   Hz   rad\n')
    output_file.write('[RF]\n')
    rf_lib_keys = self.rflibrary.keys
    id_format_str = '{:>1.0f} {:>12.3f} {:>1.0f} {:>1.0f} {:>1.0f} {:>1.0f}\n'
    for k in rf_lib_keys.keys():
        libData = self.rflibrary.data[k][0:5]
        s = id_format_str.format(*np.insert(libData, 0, k))
        output_file.write(s)
    output_file.write('\n')

    grad_lib_values = np.array(list(self.gradlibrary.type.values()))
    arb_grad_mask = np.where(grad_lib_values == 'g')[0] + 1
    trap_grad_mask = np.where(grad_lib_values == 't')[0] + 1

    if any(arb_grad_mask):
        for x in arb_grad_mask:
            if x != 0:
                output_file.write('# Format of arbitrary gradients:\n')
                output_file.write('# id amplitude shape_id\n')
                output_file.write('# ..      Hz/m     ....\n')
                output_file.write('[GRADIENTS]\n')
                keys = self.gradlibrary.keys
                id_format_str = '{:>1.0f} {:>12.0f} {:>1.0f} \n'
                for k in keys[arb_grad_mask]:
                    s = id_format_str.format(*np.insert(self.gradlibrary.data[k], 0, k))
                    output_file.write(s)
                output_file.write('\n')

    if any(trap_grad_mask):
        output_file.write('# Format of trapezoid gradients:\n')
        output_file.write('# id amplitude rise flat fall\n')
        output_file.write('# ..      Hz/m   us   us   us\n')
        output_file.write('[TRAP]\n')
        for x in trap_grad_mask:
            if x != 0:
                keys = self.gradlibrary.keys
                id_format_str = '{:>2.0f} {:>12.1f} {:>3.0f} {:>4.0f} {:>3.0f}\n'
                k = keys[x]
                data = self.gradlibrary.data[k]
                data = np.reshape(data, (1, data.shape[0]))
                data[0][1:] = np.round(1e6 * data[0][1:])
                data = np.round(data, decimals=1)
                s = id_format_str.format(*np.insert(data, 0, k))
                output_file.write(s)
        output_file.write('\n')

    if len(self.adclibrary.keys) != 0:
        output_file.write('# Format of ADC events:\n')
        output_file.write('# id num dwell delay freq phase\n')
        output_file.write('# ..  ..    ns    us   Hz   rad\n')
        output_file.write('[ADC]\n')
        keys = self.adclibrary.keys
        id_format_str = '{:>2.0f} {:>3.0f} {:>6.0f} {:>3.0f} {:>.0f} {:>.0f}\n'
        for k in keys.values():
            data = np.multiply(self.adclibrary.data[k][0:5], [1, 1e9, 1e6, 1, 1])
            s = id_format_str.format(*np.insert(data, 0, k))
            output_file.write(s)
    output_file.write('\n')

    if len(self.delaylibrary.keys) != 0:
        output_file.write('# Format of delays:\n')
        output_file.write('# id delay (us)\n')
        output_file.write('[DELAYS]\n')
        keys = self.delaylibrary.keys
        id_format_str = '{:>.0f} {:>.0f}\n'
        for k in keys.values():
            data = np.round(1e6 * self.delaylibrary.data[k])
            s = id_format_str.format(*np.insert(data, 0, k))
            output_file.write(s)
        output_file.write('\n')

    if len(self.shapelibrary.keys) != 0:
        output_file.write('# Sequence Shapes\n')
        output_file.write('[SHAPES]\n\n')
        keys = self.shapelibrary.keys
        for k in keys.values():
            shape_data = self.shapelibrary.data[k]
            s = 'shape_id {:>.0f}\n'
            s = s.format(k)
            output_file.write(s)
            s = 'num_samples {:>.0f}\n'
            s = s.format(shape_data[0][0])
            output_file.write(s)
            s = '{:g}\n'
            for x in shape_data[0][1:]:
                s1 = s.format(x)
                output_file.write(s1)
            output_file.write('\n')
