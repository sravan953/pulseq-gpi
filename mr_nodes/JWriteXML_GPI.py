import gpi

from mr_gpi.pulseq2jemris import jseqtree


class ExternalNode(gpi.NodeAPI):
    """This Node provides allows the user to configure the Parameters for Jemris.
    
    Structure of input data:
    - ConcatSequence Parameters : dict
        Key-value pairs of parameters_params to configure the Parameters module.
    - ConcatSequence Sequences : dict
        Key-value pair of 'AtomicSequence Pulses' and list of Sequences that make up the ConcatSequence. 
    --- AtomicSequence Pulses : dict
            Key-value pair of 'AtomicSequence Pulses' and list of parameters_params to configure required pulses.
    """

    def initUI(self):
        self.parameters_params = ['FOVx', 'FOVy', 'FOVz', 'GradMaxAmpl', 'GradRiseTime', 'GradSlewRate', 'HardwareMode',
                           'Nx', 'Ny', 'Nz', 'TD', 'TE', 'TI', 'TR']
        # Widgets
        self.addWidget('TextBox', 'Parameter configuration:')
        for label in self.parameters_params:
            self.addWidget('StringBox', label)
        self.addWidget('SaveFileBrowser', 'File location', button_title='Browse')
        self.addWidget('PushButton', 'Write XML', button_title="Compute events")

        # IO Ports
        self.addInPort('ConcatSequence', 'LIST')

        return 0

    def compute(self):
        if 'Write XML' in self.widgetEvents():
            # Get input data
            in_tuple = self.getData('ConcatSequence')

            concat_seq_params = in_tuple[0]
            # concat_seq_children_params is a list of ConcatSequence/AtomicSequence definitions
            # Iterate through concat_seq_children_params to construct each Sequence
            concat_seq_children_params = in_tuple[1]

            j = jseqtree.JSeqTree()
            avl_seq = []
            for each_seq_params in concat_seq_children_params:
                avl_seq.append(self.make_seq(j, each_seq_params))
            final_concat_seq = j.add_to_concat(concat_seq_params, *avl_seq)

            # Construct dict for Parameters module
            params = {}
            for label in self.parameters_params:
                if self.getVal(label) != '':
                    params[label] = self.getVal(label)

            j.make_seq_tree(params, final_concat_seq)
            # Get file save location
            file_location = self.getVal('File location')
            j.write_xml(file_location)

            return 0

    def make_seq(self, j, each_seq_params):
        pulse_list = []
        for pulse_params in each_seq_params:
            if 'DelaySequence' in pulse_params:
                # DelaySequence, do not call make_pulse()
                return j.make_delay(pulse_params)
            pulse_list.append(self.make_pulse(j, pulse_params))

        return j.add_to_atomic(*pulse_list)

    def make_pulse(self, j, pulse_def):
        if not isinstance(pulse_def, dict):
            raise TypeError("Illegal arguments. make_pulse() takes one dict argument that contains key-value pairs of "
                            "Jemris parameters_params and values. You have passed arguments of type: " + str(type(pulse_def)))

        event_name = pulse_def.pop('event_name')
        if event_name == 'Rf':
            return j.make_rf_pulse(pulse_def)
        elif event_name == 'Trap':
            return j.make_trap_grad_pulse(pulse_def)
