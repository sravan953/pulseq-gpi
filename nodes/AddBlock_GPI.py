import gpi
import h5py
from gpi import QtGui

from mr_gpi.makeadc import makeadc
from mr_gpi.makearbitrary_grad import makearbitrarygrad
from mr_gpi.makedelay import makedelay
from mr_gpi.makesinc import makesincpulse
from mr_gpi.maketrap import maketrapezoid


class AddBlockWidgets(gpi.GenericWidgetGroup):
    """A unique widget that display a variable number of StringBoxes (or FileBrowser) depending on the Event being
    configured.
    """

    valueChanged = gpi.Signal()

    def __init__(self, title, parent=None):
        super(AddBlockWidgets, self).__init__(title, parent)
        self.button_names_list = ['Off', 'Delay', 'Rf', 'Gx', 'G', 'GyPre', 'ArbGrad', 'ADC']
        self.clicked_button_name, self.clicked_button_index = '', 0
        self.buttons_list, self.text_edit_list = [], []
        col_count = 0
        wdg_layout = QtGui.QGridLayout()

        # Adding PushButtons
        for name in self.button_names_list:
            new_button = QtGui.QPushButton(name)
            new_button.setCheckable(True)
            new_button.setAutoExclusive(True)
            new_button.clicked.connect(self.button_clicked)
            new_button.clicked.connect(self.valueChanged)
            # Syntax: addWidget(widget, row, col, rowSpan, colSpan)
            wdg_layout.addWidget(new_button, 0, col_count, 1, 1)
            self.buttons_list.append(new_button)
            col_count += 1

        # Adding TextEdits
        for x in range(len(self.button_names_list)):
            self.text_edit = gpi.StringBox(str(x))
            self.text_edit.set_visible(False)
            # Syntax: addWidget(widget, row, col, rowSpan, colSpan)
            wdg_layout.addWidget(self.text_edit, x + 1, 1, 1, 6)
            self.text_edit_list.append(self.text_edit)

        # Adding FileBrowser
        self.file_browser = gpi.OpenFileBrowser('Read .hdf5')
        self.file_browser.set_button_title('Read .hdf5')
        self.file_browser.set_visible(False)
        wdg_layout.addWidget(self.file_browser, len(self.button_names_list) + 1, 1, 1, 4)

        self.setLayout(wdg_layout)
        self.buttons_list[0].setChecked(True)

    def get_val(self):
        if self.clicked_button_index == 0:
            return {}
        else:
            if self.clicked_button_index == 5:
                # Return 'gy_pre' because values are pre-computed in ConfigSeq_GPI Node
                return {'event': 'GyPre'}
            elif self.clicked_button_index == 6:
                values = {'event': self.clicked_button_name, 'data': [x.get_val() for x in self.text_edit_list],
                          'file': self.file_browser.get_val()}
                return values
            else:
                values = {'event': self.clicked_button_name, 'data': [x.get_val() for x in self.text_edit_list]}
                return values

    def set_val(self, val):
        if len(val) == 0:
            self.hide_text_edits()
            self.hide_file_browser()
        else:
            self.clicked_button_name = val['event']
            self.clicked_button_index = self.button_names_list.index(self.clicked_button_name)
            self.buttons_list[self.clicked_button_index].setChecked(True)
            self.show_text_edits(self.clicked_button_index)
            data = val['data']
            for x in range(len(self.button_names_list)):
                self.text_edit_list[x].set_val(data[x])
            self.file_browser.set_val(val['file'] if 'file' in val else '')

    def button_clicked(self):
        for button in self.buttons_list:
            if button.isChecked():
                self.clicked_button_index = self.buttons_list.index(button)
                self.clicked_button_name = self.button_names_list[self.clicked_button_index]
        self.show_text_edits(self.clicked_button_index)

    def show_text_edits(self, index):
        self.hide_text_edits()
        self.hide_file_browser()

        if index == 1:
            # Delay
            delay_label = 'Delay (s)'
            self.text_edit_list[0].set_visible(True)
            self.text_edit_list[0].set_placeholder(delay_label)
        elif index == 2:
            # RF
            sinc_labels = ['Duration (s)', 'Frequency Offset', 'Phase Offset', 'Time Bw Product', 'Apodization',
                           'Slice Thickness (m)']
            [self.text_edit_list[x].set_visible(True) for x in range(len(sinc_labels))]
            [self.text_edit_list[x].set_placeholder(sinc_labels[x]) for x in range(len(sinc_labels))]
        elif index == 3:
            # Gx
            trap_label = 'Flat Time (s)'
            self.text_edit_list[0].set_visible(True)
            self.text_edit_list[0].set_placeholder(trap_label)
        elif index == 4:
            # G
            trap_labels = ['Channel', 'Duration (s)', 'Area', 'Flat Time (s)', 'Flat Area', 'Amplitude (Hz)',
                           'Rise Time (s)']
            [self.text_edit_list[x].set_visible(True) for x in range(len(trap_labels))]
            [self.text_edit_list[x].set_placeholder(trap_labels[x]) for x in range(len(trap_labels))]
        elif index == 6:
            # Arbitrary Grad
            arb_grad_labels = ['Channel', 'Maximum Gradient', 'Maximum Slew']
            [self.text_edit_list[x].set_visible(True) for x in range(len(arb_grad_labels))]
            [self.text_edit_list[x].set_placeholder(arb_grad_labels[x]) for x in range(len(arb_grad_labels))]
            self.file_browser.set_visible(True)
        elif index == 7:
            # ADC
            adc_labels = ['Number of samples', 'Dwell (s)', 'Duration (s)', 'Delay (s)', 'Frequency Offset',
                          'Phase Offset']
            [self.text_edit_list[x].set_visible(True) for x in range(len(adc_labels))]
            [self.text_edit_list[x].set_placeholder(adc_labels[x]) for x in range(len(adc_labels))]

    def hide_text_edits(self):
        [x.set_visible(False) for x in self.text_edit_list]
        [x.set_val("") for x in self.text_edit_list]

    def hide_file_browser(self):
        self.file_browser.set_visible(False)


class ExternalNode(gpi.NodeAPI):
    """This node providers options for setting up the event that needs to be added. Event parameters should be set to 0
    if left unconfigured. Up to 6 simultaneous events can be added in one block. The 'ComputeEvents' button gathers the
    input data and constructs the block elements. The output of this node (or a chain of AddBlock nodes) has to be
    supplied to a GenSeq node.

     Units:
     - duration/flatTime/riseTime/dwell/delay (s)
     - sliceThickness (m)
     - amplitude (Hz)
    """

    def initUI(self):
        # Widgets
        self.addWidget('StringBox', 'Unique Node Name')
        for x in range(6):
            self.addWidget('AddBlockWidgets', 'Event ' + str(x + 1))
        self.addWidget('PushButton', 'ComputeEvents')
        self.addWidget('TextBox', 'EventInfo')

        # IO Ports
        self.addInPort('input', 'DICT')
        self.addOutPort('output', 'DICT')

        return 0

    def validate(self):
        if 'ComputeEvents' in self.widgetEvents() or self.portEvents():
            self.setDetailLabel(self.getVal('Unique Node Name'))

    def compute(self):
        if 'ComputeEvents' in self.widgetEvents() or self.portEvents():
            input = self.getData('input')
            system = input['system']

            current_events, current_event_names = [], []
            for current_event in range(6):
                event_dict = self.getVal('Event ' + str(current_event + 1))
                event_name = event_dict['event'] if 'event' in event_dict else None
                event_values = event_dict['data'] if 'data' in event_dict else None
                # path variable is only for arbitrary gradients
                path = event_dict['file'] if 'file' in event_dict else None

                if event_name == 'Delay':
                    current_events.append(makedelay(float(event_values[0])))
                elif event_name == 'Rf':
                    duration, freq_offset, phase_offset, time_bw_product, apodization, slice_thickness = [
                        float(event_values[x]) for x in range(6)]
                    kwargs_for_sinc = {"flip_angle": system.flip, "system": system, "duration": duration,
                                       "freq_offset": freq_offset, "phase_offset": phase_offset,
                                       "time_bw_product": time_bw_product,
                                       "apodization": apodization, "max_grad": system.max_grad,
                                       "max_slew": system.max_slew,
                                       "slice_thickness": slice_thickness}
                    rf, gz = makesincpulse(**kwargs_for_sinc)
                    current_events.append(rf)
                    current_events.append(gz)
                elif event_name == 'Gx':
                    flat_time = float(event_values[0])
                    channel = 'x'
                    duration, area, amplitude, rise_time = [0] * 4
                    flat_area = system.Nx * (1 / system.fov)
                    kwargs_for_trap = {"channel": channel, "system": system, "duration": duration, "area": area,
                                       "flat_time": flat_time, "flat_area": flat_area, "amplitude": amplitude,
                                       "max_grad": system.max_grad, "max_slew": system.max_slew, "rise_time": rise_time}
                    current_events.append(maketrapezoid(**kwargs_for_trap))
                elif event_name == 'G':
                    channel = event_values[0]
                    duration, area, flat_time, flat_area, amplitude, rise_time = [float(event_values[x]) for x in
                                                                                  range(1, 7)]
                    kwargs_for_trap = {"channel": channel, "system": system, "duration": duration, "area": area,
                                       "flat_time": flat_time, "flat_area": flat_area, "amplitude": amplitude,
                                       "max_grad": system.max_grad, "max_slew": system.max_slew, "rise_time": rise_time}
                    current_events.append(maketrapezoid(**kwargs_for_trap))
                elif event_name == 'GyPre':
                    pass
                elif event_name == 'ArbGrad':
                    channel = event_values[0]
                    max_grad, max_slew = [float(event_values[x]) for x in range(1, 3)]
                    file = h5py.File(gpi.TranslateFileURI(path), "r")
                    self.dataset = str()

                    def append_if_dataset(name, obj):
                        if isinstance(obj, h5py.Dataset):
                            self.dataset = name
                            return True

                    file.visititems(append_if_dataset)

                    waveform = file[self.dataset].value
                    kwargs_for_arb_grad = {"channel": channel, "waveform": waveform, "max_grad": max_grad,
                                           "max_slew": max_slew, "system": system}
                    arb_grad = makearbitrarygrad(**kwargs_for_arb_grad)
                    current_events.append(arb_grad)
                elif event_name == 'ADC':
                    num_samples, dwell, duration, delay, freq_offset, phase_offset = [float(event_values[x]) for x in
                                                                                      range(6)]
                    kwargs_for_adc = {"num_samples": num_samples, "system": system, "dwell": dwell,
                                      "duration": duration, "delay": delay, "freq_offset": freq_offset,
                                      "phase_offset": phase_offset}
                    adc = makeadc(**kwargs_for_adc)
                    current_events.append(adc)
                if event_name != 'Rf':
                    current_event_names.append(event_name)
                else:
                    current_event_names.append('Rf')
                    current_event_names.append('Gz')

            all_events = input['events'] if 'events' in input else []
            all_event_names = input['event_names'] if 'event_names' in input else []
            all_events.append(current_events)
            all_event_names.append(current_event_names)
            input['events'], input['event_names'] = all_events, all_event_names
            self.setData('output', input)

            # To display the computed info inside the node
            info_text = ""
            for current_event in current_events:
                attrs = [attr for attr in dir(current_event) if not callable(attr) and not attr.startswith('__')]
                text = ""
                for attr in attrs:
                    text += attr + ": " + str(getattr(current_event, attr)) + "\n"
                info_text += text + "~~~\n"
            self.setAttr('EventInfo', val=info_text)

        return 0
