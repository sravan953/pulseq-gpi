import gpi
import numpy as np

from mr_gpi.Sequence.sequence import Sequence
from mr_gpi.calcduration import calcduration


class ExternalNode(gpi.NodeAPI):
    """This node has no widgets since it does not require any configuration. This is a purely computational node- it
    adds the supplied blocks to a Sequence object. The output of this node can be supplied to a Matplotlib node for
    plotting.
    """

    def initUI(self):
        # IO Ports
        self.addInPort(title='input', type='DICT')
        self.addOutPort(title='output', type='DICT')
        self.addOutPort(title='adc', type='NPYarray')
        self.addOutPort(title='rf_mag', type='NPYarray')
        self.addOutPort(title='rf_phase', type='NPYarray')
        self.addOutPort(title='trap_x', type='NPYarray')
        self.addOutPort(title='trap_y', type='NPYarray')
        self.addOutPort(title='trap_z', type='NPYarray')

        return 0

    def compute(self):
        in_dict = self.getData('input')
        self.seq = in_dict['sequence']
        if self.seq is None:
            system = in_dict['system']
            self.seq = Sequence(system)
            gy_pre, Ny = in_dict['gy_pre'], system.Ny

            events, event_names = in_dict['events'], in_dict['event_names']
            for i in range(Ny):
                for j in range(len(events)):
                    block_row, block_names = events[j], event_names[j]
                    if 'GyPre' in block_names:
                        gy_index = block_names.index('GyPre')
                        # GyPre has to be inserted only on the first iteration.
                        # In subsequent iterations, the inserted GyPre value is simply replaced.
                        if i == 0:
                            block_row.insert(gy_index, gy_pre[i])
                        else:
                            block_row[gy_index] = gy_pre[i]
                    self.seq.addblock(*block_row)
                in_dict['seq'] = self.seq

        self.setData('output', in_dict)
        self.setPlotOutputs()

        return 0

    def setPlotOutputs(self):
        t0, time_range = 0, [0, np.inf]
        adc_values = [[], []]
        rf_mag_values = [[], []]
        rf_phase_values = [[], []]
        t_x_values = [[], []]
        t_y_values = [[], []]
        t_z_values = [[], []]

        for iB in range(1, len(self.seq.block_events)):
            block = self.seq.getblock(iB)
            is_valid = time_range[0] <= t0 <= time_range[1]
            if is_valid:
                if block is not None:
                    if 'adc' in block:
                        adc = block['adc']
                        t = adc.delay + [(x * adc.dwell) for x in range(0, int(adc.num_samples))]
                        adc_values[0].extend(t0 + t)
                        adc_values[1].extend(np.ones(len(t)))
                    if 'rf' in block:
                        rf = block['rf']
                        t = rf.t
                        rf_mag_values[0].extend(t0 + t[0])
                        rf_mag_values[1].extend(abs(rf.signal))
                        rf_phase_values[0].extend(t0 + t[0])
                        rf_phase_values[1].extend(np.angle(rf.signal))
                    grad_channels = ['gx', 'gy', 'gz']
                    for x in range(0, len(grad_channels)):
                        if grad_channels[x] in block:
                            grad = block[grad_channels[x]]
                            if grad.type == 'grad':
                                t = grad.t
                                waveform = 1e-3 * grad.waveform
                            else:
                                t = np.cumsum([0, grad.rise_time, grad.flat_time, grad.fall_time])
                                waveform = [1e-3 * grad.amplitude * x for x in [0, 1, 1, 0]]
                                if grad.channel == 'x':
                                    t_x_values[0].extend(t0 + t)
                                    t_x_values[1].extend(waveform)
                                elif grad.channel == 'y':
                                    t_y_values[0].extend(t0 + t)
                                    t_y_values[1].extend(waveform)
                                elif grad.channel == 'z':
                                    t_z_values[0].extend(t0 + t)
                                    t_z_values[1].extend(waveform)
            t0 += calcduration(block)

        # Setting outputs
        # ADC
        adc_output = np.array(adc_values)
        adc_output = adc_output.transpose()
        self.setData('adc', adc_output)

        # RF Mag
        rf_mag_output = np.array(rf_mag_values)
        rf_mag_output = rf_mag_output.transpose()
        self.setData('rf_mag', rf_mag_output)

        # RF Phase
        rf_ph_output = np.array(rf_phase_values)
        rf_ph_output = rf_ph_output.transpose()
        self.setData('rf_phase', rf_ph_output)

        # TrapX
        t_x_output = np.array(t_x_values)
        t_x_output = t_x_output.transpose()
        self.setData('trap_x', t_x_output)

        # TrapY
        t_y_output = np.array(t_y_values)
        t_y_output = t_y_output.transpose()
        self.setData('trap_y', t_y_output)

        # TrapZ
        t_z_output = np.array(t_z_values)
        t_z_output = t_z_output.transpose()
        self.setData('trap_z', t_z_output)
