import math
from collections import OrderedDict

import gpi
import h5py
import numpy as np

import mr_gpi
from mr_gpi.Sequence.sequence import Sequence
from mr_gpi.calcduration import calcduration
from mr_gpi.makeadc import makeadc
from mr_gpi.makearbitrary_grad import makearbitrarygrad
from mr_gpi.makedelay import makedelay
from mr_gpi.makesinc import makesincpulse
from mr_gpi.maketrap import maketrapezoid


class ExternalNode(gpi.NodeAPI):
    def initUI(self):
        # Widgets
        self.addWidget('TextBox', 'Events you defined')
        self.addWidget('StringBox', 'Order of events')
        self.addWidget('PushButton', 'ComputeEvents', button_title="Compute events")

        # IO Ports
        self.addInPort(title='input', type='DICT', obligation=gpi.REQUIRED)
        self.addOutPort(title='seq_output', type='DICT')
        self.addOutPort(title='adc_output', type='NPYarray')
        self.addOutPort(title='rf_mag_output', type='NPYarray')
        self.addOutPort(title='rf_phase_output', type='NPYarray')
        self.addOutPort(title='trap_x_output', type='NPYarray')
        self.addOutPort(title='trap_y_output', type='NPYarray')
        self.addOutPort(title='trap_z_output', type='NPYarray')

        self.all_event_def = OrderedDict()
        self.all_event_ordered = OrderedDict()

        return 0

    def validate(self):
        self.in_dict = self.getData('input')
        if 'sequence' in self.in_dict:
            self.seq = self.in_dict['sequence']
        else:
            self.all_event_def = self.in_dict['all_event_def']
            self.all_event_ordered = self.in_dict['all_event_ordered']

            events_added_text = str()
            for unique_name in self.all_event_ordered:
                events_added_text += unique_name + '\n'
            self.setAttr('Events you defined', **{'val': events_added_text})

    def compute(self):
        if 'ComputeEvents' in self.widgetEvents():
            user_ordered_events = self.getVal('Order of events').split(',')
            if len(user_ordered_events) == 0:
                raise ValueError('Enter [Unique Name] of Events in the order you want Events to be added.')

            self.make_event_holders()
            self.add_blocks_to_seq(user_ordered_events)
            self.set_plot_outputs()

            # Setting output
            self.in_dict['seq'] = self.seq
            self.setData('seq_output', self.in_dict)

    def make_event_holders(self):
        self.system = self.in_dict['system']
        # arbgrad_file_path is only for arbitrary gradients
        arbgrad_file_path = self.all_event_def['file_path'] if 'file_path' in self.all_event_def else None
        self.all_event_holders = {}

        for event in self.all_event_def:
            event_unique_name = event['event_unique_name']
            event_name = event['event_name']
            if event_unique_name != 'gyPre':
                event_values = list(event['event_values'].values())
            include_in_loop = event['include_in_loop']

            if event_name == 'Delay':
                params = self.parse_config_params(event_values)
                delay = makedelay(params[0])
                self.all_event_holders[event_unique_name] = delay, include_in_loop
            elif event_name == 'Rf':
                max_grad, max_slew, flip_angle, duration, freq_offset, phase_offset, time_bw_product, apodization, slice_thickness = self.parse_config_params(
                    event_values)
                flip_angle = math.radians(flip_angle)
                max_grad = mr_gpi.convert.convert(max_grad, 'mT/m')
                max_slew = mr_gpi.convert.convert(max_slew, 'mT/m/ms')
                max_grad = self.system.max_grad if max_grad == 0 else max_grad
                max_slew = self.system.max_slew if max_slew == 0 else max_slew
                kwargs_for_sinc = {"flip_angle": flip_angle, "system": self.system, "duration": duration,
                                   "freq_offset": freq_offset, "phase_offset": phase_offset,
                                   "time_bw_product": time_bw_product, "apodization": apodization,
                                   "max_grad": max_grad, "max_slew": max_slew, "slice_thickness": slice_thickness}
                rf, gz = makesincpulse(**kwargs_for_sinc)
                self.all_event_holders[event_unique_name] = rf, include_in_loop
                if event['include_gz']:
                    self.all_event_holders['gz'] = gz, include_in_loop
            elif event_name == 'G':
                channel = event_values.pop(0)
                max_grad, max_slew, duration, area, flat_time, flat_area, amplitude, rise_time = self.parse_config_params(
                    event_values)
                max_grad = mr_gpi.convert.convert(max_grad, 'mT/m')
                max_slew = mr_gpi.convert.convert(max_slew, 'mT/m/ms')
                max_grad = self.system.max_grad if max_grad == 0 else max_grad
                max_slew = self.system.max_slew if max_slew == 0 else max_slew
                kwargs_for_trap = {"channel": channel, "system": self.system, "duration": duration, "area": area,
                                   "flat_time": flat_time, "flat_area": flat_area, "amplitude": amplitude,
                                   "max_grad": max_grad, "max_slew": max_slew, "rise_time": rise_time}
                trap = maketrapezoid(**kwargs_for_trap)
                self.all_event_holders[event_unique_name] = trap, include_in_loop
            elif event_name == 'GyPre':
                self.all_event_holders[event_unique_name] = 'gyPre', True
            elif event_name == 'ArbGrad':
                channel = event_values.pop(0)
                max_grad, max_slew = self.parse_config_params(event_values)
                file = h5py.File(gpi.TranslateFileURI(arbgrad_file_path), "r")
                self.dataset = str()

                def append_if_dataset(name, obj):
                    if isinstance(obj, h5py.Dataset):
                        self.dataset = name
                        return True

                file.visititems(append_if_dataset)

                waveform = file[self.dataset].value
                kwargs_for_arb_grad = {"channel": channel, "waveform": waveform, "max_grad": max_grad,
                                       "max_slew": max_slew, "system": self.system}
                arb_grad = makearbitrarygrad(**kwargs_for_arb_grad)
                self.all_event_holders[event_unique_name] = arb_grad, include_in_loop
            elif event_name == 'ADC':
                num_samples, dwell, duration, delay, freq_offset, phase_offset = self.parse_config_params(
                    event_values)
                kwargs_for_adc = {"num_samples": num_samples, "system": self.system, "dwell": dwell,
                                  "duration": duration, "delay": delay, "freq_offset": freq_offset,
                                  "phase_offset": phase_offset}
                adc = makeadc(**kwargs_for_adc)
                self.all_event_holders[event_unique_name] = adc, include_in_loop

    def parse_config_params(self, all_params):
        parsed_params = []
        for param in all_params:
            try:
                parsed_params.append(float(param))
            except ValueError:
                # Syntax: [-][*event_unique_name].[*event_property[operator][operand]]
                # * - Required
                if param.count('.') == 1:
                    sign = -1 if param[0] == '-' else 1
                    param = param[1:] if sign == -1 else param
                    p_split = param.split('.')
                    event_unique_name = p_split[0]
                    event_property = p_split[1]
                    operator = '/' if '/' in event_property else '*' if '*' in event_property else ''
                    operand = float(event_property.split(operator)[1]) if operator != '' else 1
                    if operator != '':
                        event_property = event_property.split(operator)[0]
                    if event_unique_name in self.all_event_holders:
                        event_holder = self.all_event_holders[event_unique_name][0]
                        value = sign * float(getattr(event_holder, event_property))
                        value = value / operand if operand == '/' else value * operand
                        parsed_params.append(float(value))
                else:
                    raise ValueError(
                        'The syntax for referring to other event parameters is: [sign][*event_unique_name].['
                        '*event_property][operator][operand]. * - required')

        if len(parsed_params) == 0:
            raise ValueError('Please make sure you have input correct configuration paraneters.')
        return parsed_params

    def add_blocks_to_seq(self, user_ordered_events):
        # Create Sequence object and add Events
        self.seq = Sequence(self.system)
        gyPre = self.in_dict['gy_pre']
        for i in range(self.system.Ny):
            for unique_node_name in user_ordered_events:
                events_to_add = []
                for event_unique_name in self.all_event_ordered[unique_node_name]:
                    if event_unique_name == 'gyPre':
                        events_to_add.append(gyPre[i])
                    else:
                        event = self.get_event_matching_unique_name(event_unique_name)
                        if event['include_in_loop']:
                            events_to_add.append(self.all_event_holders[event_unique_name][0])
                        else:
                            events_to_add.append(self.all_event_holders[event_unique_name][0])
                            self.all_event_ordered[unique_node_name].remove(event_unique_name)
                            self.all_event_holders.pop(event_unique_name)
                self.seq.add_block(*events_to_add)

    def get_event_matching_unique_name(self, event_unique_name):
        for event in self.all_event_def:
            if event['event_unique_name'] == event_unique_name:
                return event

    def set_plot_outputs(self):
        t0, time_range = 0, [0, np.inf]
        adc_values = [[], []]
        rf_mag_values = [[], []]
        rf_phase_values = [[], []]
        t_x_values = [[], []]
        t_y_values = [[], []]
        t_z_values = [[], []]

        for iB in range(1, len(self.seq.block_events)):
            block = self.seq.get_block(iB)
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
        self.setData('adc_output', adc_output)

        # RF Mag
        rf_mag_output = np.array(rf_mag_values)
        rf_mag_output = rf_mag_output.transpose()
        self.setData('rf_mag_output', rf_mag_output)

        # RF Phase
        rf_ph_output = np.array(rf_phase_values)
        rf_ph_output = rf_ph_output.transpose()
        self.setData('rf_phase_output', rf_ph_output)

        # TrapX
        t_x_output = np.array(t_x_values)
        t_x_output = t_x_output.transpose()
        self.setData('trap_x_output', t_x_output)

        # TrapY
        t_y_output = np.array(t_y_values)
        t_y_output = t_y_output.transpose()
        self.setData('trap_y_output', t_y_output)

        # TrapZ
        t_z_output = np.array(t_z_values)
        t_z_output = t_z_output.transpose()
        self.setData('trap_z_output', t_z_output)
