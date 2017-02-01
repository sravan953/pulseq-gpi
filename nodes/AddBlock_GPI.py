from collections import OrderedDict

import gpi
from gpi import QtGui


class AddBlockWidgets(gpi.GenericWidgetGroup):
    """A unique widget that display a variable number of StringBoxes (or FileBrowser) depending on the Event being
    configured.
    """

    valueChanged = gpi.Signal()

    def __init__(self, title, parent=None):
        super(AddBlockWidgets, self).__init__(title, parent)
        self.button_names_list = ['Off', 'Delay', 'Rf', 'G', 'GyPre', 'ArbGrad', 'ADC']
        self.clicked_button_name, self.clicked_button_index = '', 0
        self.buttons_list, self.string_box_list = [], []
        self.wdg_layout = QtGui.QGridLayout()

        self.add_event_pushbuttons()
        self.add_config_stringboxes()
        self.add_include_in_loop_pushbutton()
        self.add_include_gz_pushbutton()
        self.add_file_browser()

        self.setLayout(self.wdg_layout)
        self.buttons_list[0].setChecked(True)

        # Labels for StringBoxes for configuring Events
        self.delay_labels = ['Unique Event name', 'Delay (s)']
        self.sinc_labels = ['Unique Event name', 'Maximum Gradient (mT/m)', 'Maximum Slew (T/m/s)', 'Duration (s)',
                            'Frequency Offset', 'Phase Offset', 'Time Bw Product', 'Apodization', 'Slice Thickness (m)']
        self.trap_labels = ['Unique Event name', 'Channel', 'Duration (s)', 'Area', 'Flat Time (s)', 'Flat Area',
                            'Amplitude (Hz)', 'Rise Time (s)']
        self.arb_grad_labels = ['Unique Event name', 'Channel', 'Maximum Gradient (mT/m)', 'Maximum Slew (T/m/s)']
        self.adc_labels = ['Unique Event name', 'Number of samples', 'Dwell (s)', 'Duration (s)', 'Delay (s)',
                           'Frequency Offset', 'Phase Offset']
        # Placeholders for StringBoxes for configuring Events
        self.delay_placeholders = ['event_unique_name', 'delay']
        self.sinc_placeholders = ['event_unique_name', 'max_grad', 'max_slew', 'duration', 'freq_offset',
                                  'phase_offset',
                                  'time_bw_prod', 'apodization', 'slice_thickness']
        self.trap_placeholders = ['event_unique_name', 'channel', 'duration', 'area', 'flat_time', 'flat_area',
                                  'amplitude',
                                  'rise_time']
        self.arb_grad_placeholders = ['event_unique_name', 'channel', 'max_grad', 'max_slew']
        self.adc_placeholders = ['event_unique_name', 'num_samples', 'dwell', 'duration', 'delay', 'freq_offset',
                                 'phase_offset']

        # First index is None because the first button is 'Off'. Look into event_def['event_values'] in get_val()
        # Fourth index is also None because of GyPre - no config
        self.labels = [None, self.delay_labels, self.sinc_labels, self.trap_labels, None, self.arb_grad_labels,
                       self.adc_labels]
        self.placeholders = [None, self.delay_placeholders, self.sinc_placeholders, self.trap_placeholders, None,
                             self.arb_grad_placeholders, self.adc_placeholders]

    def add_event_pushbuttons(self):
        """Adding PushButtons for the Events."""
        col_count = 0
        for name in self.button_names_list:
            new_button = QtGui.QPushButton(name)
            new_button.setCheckable(True)
            new_button.setAutoExclusive(True)
            new_button.clicked.connect(self.button_clicked)
            new_button.clicked.connect(self.valueChanged)
            # Syntax: addWidget(widget, row, col, rowSpan, colSpan)
            self.wdg_layout.addWidget(new_button, 0, col_count, 1, 1)
            self.buttons_list.append(new_button)
            col_count += 1

    def add_config_stringboxes(self):
        """Adding StringBoxes for configuring the Events."""
        for x in range(9):
            string_box = gpi.StringBox(str(x))
            string_box.set_visible(False)
            # Syntax: addWidget(widget, row, col, rowSpan, colSpan)
            self.wdg_layout.addWidget(string_box, x + 1, 1, 1, 6)
            self.string_box_list.append(string_box)

    def add_include_in_loop_pushbutton(self):
        """Adding PushButton to toggle Event being included/excluded in loop."""
        self.include_in_loop_pushbutton = QtGui.QPushButton('Add event in loop')
        self.include_in_loop_pushbutton.setCheckable(True)
        self.include_in_loop_pushbutton.setChecked(True)
        self.include_in_loop_pushbutton.setVisible(False)
        self.include_in_loop_pushbutton.clicked.connect(self.button_clicked)
        self.include_in_loop_pushbutton.clicked.connect(self.valueChanged)
        # Syntax: addWidget(widget, row, col, rowSpan, colSpan)
        self.wdg_layout.addWidget(self.include_in_loop_pushbutton, 10, 1, 1, 6)

    def add_include_gz_pushbutton(self):
        """Adding PushButton toggle for Gz along with Rf."""
        self.include_gz_pushbutton = QtGui.QPushButton('Add Gz event with Rf')
        self.include_gz_pushbutton.setCheckable(True)
        self.include_gz_pushbutton.setVisible(False)
        self.include_gz_pushbutton.clicked.connect(self.button_clicked)
        self.include_gz_pushbutton.clicked.connect(self.valueChanged)
        # Syntax: addWidget(widget, row, col, rowSpan, colSpan)
        self.wdg_layout.addWidget(self.include_gz_pushbutton, 11, 1, 1, 6)

    def add_file_browser(self):
        """Adding FileBrowser necessary for ArbGrad Event."""
        self.file_browser = gpi.OpenFileBrowser('Read .hdf5')
        self.file_browser.set_button_title('Read .hdf5')
        self.file_browser.set_visible(False)
        # Syntax: addWidget(widget, row, col, rowSpan, colSpan)
        self.wdg_layout.addWidget(self.file_browser, 5, 1, 1, 6)

    # Getter
    def get_val(self):
        if self.clicked_button_index == 0:
            # 'Off' PushButton selected, return empty dict
            return {}
        elif self.clicked_button_index == 4:
            # Phase encode, GyPre
            return {'event_name': 'GyPre', 'event_unique_name': 'gyPre', 'event_values': None, 'include_in_loop': True}
        else:
            """
            event_def contains:
            - event_name: str - Event name, corresponds to Event button that is selected
            - event_unique_name: str - Unique Event name; user input
            - event_values: OrderedDict - key-value pairs of Event parameters and values
            - include_in_loop: bool - If Event should be added to Sequence Ny times
            - include_gz: bool - If Gz Event should be added to Sequence with Rf Event
            - file_path: str - Path to .hdf5 file required for arbitrary gradient Event
            """
            event_def = {}
            event_def['event_name'] = self.clicked_button_name
            event_def['event_unique_name'] = self.string_box_list[0].get_val()
            event_def['event_values'] = OrderedDict(
                zip(self.placeholders[self.clicked_button_index][1:], [x.get_val() for x in self.string_box_list[1:]]))
            event_def['include_in_loop'] = self.include_in_loop_pushbutton.isChecked()
            if self.clicked_button_index == 2:
                # For Rf event, check if Gz has to be included
                event_def['include_gz'] = self.include_gz_pushbutton.isChecked()
            elif self.clicked_button_index == 6:
                event_def['file_path'] = self.file_browser.get_val()
            return event_def

    # Setter
    def set_val(self, val):
        self.hide_config_widgets()
        if len(val) != 0:
            event_unique_name = val['event_unique_name']
            event_values = val['event_values']
            self.clicked_button_name = val['event_name']
            self.clicked_button_index = self.button_names_list.index(self.clicked_button_name)
            self.buttons_list[self.clicked_button_index].setChecked(True)
            self.show_config_widgets()
            self.include_in_loop_pushbutton.setChecked(bool(val['include_in_loop']))
            if 'include_gz' in val:
                self.include_gz_pushbutton.setChecked(val['include_gz'])
            labels = self.labels[self.clicked_button_index]
            placeholders = self.placeholders[self.clicked_button_index]
            self.string_box_list[0].setTitle('Unique Event Name')
            self.string_box_list[0].set_placeholder('event_unique_name')
            self.string_box_list[0].set_val(event_unique_name)
            for x in range(1, len(placeholders)):
                self.string_box_list[x].setTitle(labels[x])
                self.string_box_list[x].set_placeholder(placeholders[x])
                self.string_box_list[x].set_val(event_values[placeholders[x]])

    def button_clicked(self):
        """Identifies the button that was clicked and stores the name and ID of the button."""
        for button in self.buttons_list:
            if button.isChecked():
                self.clicked_button_index = self.buttons_list.index(button)
                self.clicked_button_name = self.button_names_list[self.clicked_button_index]
        self.show_config_widgets()

    def show_config_widgets(self):
        """Show appropriate number of StringBoxes and relevant Widgets based on the button that was clicked."""
        self.hide_config_widgets()

        if self.clicked_button_index != 0 and self.clicked_button_index != 4:
            self.include_in_loop_pushbutton.setVisible(True)
        if self.clicked_button_index == 1:
            # Delay
            [self.string_box_list[x].set_visible(True) for x in range(len(self.delay_placeholders))]
            [self.string_box_list[x].setTitle(self.delay_labels[x]) for x in range(len(self.delay_labels))]
            [self.string_box_list[x].set_placeholder(self.delay_placeholders[x]) for x in
             range(len(self.delay_placeholders))]
        elif self.clicked_button_index == 2:
            # RF
            [self.string_box_list[x].set_visible(True) for x in range(len(self.sinc_placeholders))]
            [self.string_box_list[x].setTitle(self.sinc_labels[x]) for x in range(len(self.sinc_labels))]
            [self.string_box_list[x].set_placeholder(self.sinc_placeholders[x]) for x in
             range(len(self.sinc_placeholders))]
            self.include_gz_pushbutton.setVisible(True)
        elif self.clicked_button_index == 3:
            # G
            [self.string_box_list[x].set_visible(True) for x in range(len(self.trap_placeholders))]
            [self.string_box_list[x].setTitle(self.trap_labels[x]) for x in range(len(self.trap_labels))]
            [self.string_box_list[x].set_placeholder(self.trap_placeholders[x]) for x in
             range(len(self.trap_placeholders))]
        elif self.clicked_button_index == 5:
            # Arbitrary Grad
            [self.string_box_list[x].set_visible(True) for x in range(len(self.arb_grad_placeholders))]
            [self.string_box_list[x].setTitle(self.arb_grad_labels[x]) for x in range(len(self.arb_grad_labels))]
            [self.string_box_list[x].set_placeholder(self.arb_grad_placeholders[x]) for x in
             range(len(self.arb_grad_placeholders))]
            self.file_browser.set_visible(True)
        elif self.clicked_button_index == 6:
            # ADC
            [self.string_box_list[x].set_visible(True) for x in range(len(self.adc_placeholders))]
            [self.string_box_list[x].setTitle(self.adc_labels[x]) for x in range(len(self.adc_labels))]
            [self.string_box_list[x].set_placeholder(self.adc_placeholders[x]) for x in
             range(len(self.adc_placeholders))]

    def hide_config_widgets(self):
        """Hide all Widgets."""
        [x.set_visible(False) for x in self.string_box_list]
        [x.set_val("") for x in self.string_box_list]
        self.include_in_loop_pushbutton.setVisible(False)
        self.include_gz_pushbutton.setVisible(False)
        self.file_browser.set_visible(False)


class ExternalNode(gpi.NodeAPI):
    """
    This node providers options for setting up the event that needs to be added. Event parameters should be set to 0
    if left unconfigured. Up to 6 simultaneous events can be added in one block. The 'ComputeEvents' button gathers the
    input data and constructs the block elements. The output of this node (or a chain of AddBlock nodes) has to be
    supplied to a GenSeq node.

     Units:
     - duration (s)
     - flatTime (s)
     - riseTime (s)
     - dwell (s)
     - delay (s)
     - sliceThickness (m)
     - amplitude (Hz)
    """

    def initUI(self):
        # Init constant(s)
        self.num_concurrent_events = 6

        # Widgets
        self.addWidget('StringBox', 'Unique Node Name')
        for x in range(self.num_concurrent_events):
            self.addWidget('AddBlockWidgets', 'Event ' + str(x + 1))
        self.addWidget('PushButton', 'ComputeEvents', button_title="Compute events")

        # IO Ports
        self.addInPort('input', 'DICT')
        self.addOutPort('output', 'DICT')

        return 0

    def validate(self):
        if 'ComputeEvents' in self.widgetEvents() or 'input' in self.portEvents():
            self.unique_node_name = self.getVal('Unique Node Name')
            self.setDetailLabel(self.unique_node_name)

    def compute(self):
        if 'ComputeEvents' in self.widgetEvents() or 'input' in self.portEvents():
            in_dict = self.getData('input')
            all_event_def = in_dict['all_event_def'] if 'all_event_def' in in_dict else []
            all_event_ordered = in_dict['all_event_ordered'] if 'all_event_ordered' in in_dict else OrderedDict()
            ordered_events = []

            for x in range(self.num_concurrent_events):
                event_def = self.getVal('Event ' + str(x + 1))
                if len(event_def) != 0:
                    all_event_def.append(event_def)
                    ordered_events.append(event_def['event_unique_name'])

            all_event_ordered[self.unique_node_name] = ordered_events

            in_dict['all_event_def'] = all_event_def
            in_dict['all_event_ordered'] = all_event_ordered
            self.setData('output', in_dict)

        return 0
