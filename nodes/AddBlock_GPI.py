import gpi
from gpi import QtGui

from mr_gpi.makeadc import makeadc
from mr_gpi.makedelay import makedelay
from mr_gpi.makesinc import makesincpulse
from mr_gpi.maketrap import maketrapezoid


class AddBlockWidgets(gpi.GenericWidgetGroup):
    """A unique widget that display the appropriate number of StringBoxes.
    """

    valueChanged = gpi.Signal()

    def __init__(self, title, parent=None):
        super(AddBlockWidgets, self).__init__(title, parent)
        self.buttonNamesList = ['Off', 'Delay', 'Rf', 'Gx', 'G', 'GyPre', 'ADC']
        self.clickedButtonName, self.clickedButtonIndex = '', 0
        self.buttonsList, self.teList = [], []
        colCount = 0
        wdgLayout = QtGui.QGridLayout()

        for name in self.buttonNamesList:
            newbutton = QtGui.QPushButton(name)
            newbutton.setCheckable(True)
            newbutton.setAutoExclusive(True)
            newbutton.clicked.connect(self.buttonClicked)
            newbutton.clicked.connect(self.valueChanged)
            # addWidget(widget, row, col, rowSpan, colSpan)
            wdgLayout.addWidget(newbutton, 0, colCount, 1, 1)
            self.buttonsList.append(newbutton)
            colCount += 1

        for x in range(8):
            self.te = gpi.StringBox(str(x))
            self.te.set_visible(False)
            wdgLayout.addWidget(self.te, x + 1, 1, 1, 6)
            self.teList.append(self.te)
        self.setLayout(wdgLayout)
        self.buttonsList[0].setChecked(True)

    def get_val(self):
        if self.clickedButtonIndex == 0:
            return {}
        else:
            if self.clickedButtonIndex == 5:
                # Return 'GyPre' because values are pre-computed in ConfigSeq_GPI Node
                return {'event': 'GyPre'}
            else:
                values = {'event': self.clickedButtonName, 'data': [x.get_val() for x in self.teList]}
                return values

    def set_val(self, val):
        if len(val) == 0:
            self.hideOtherTes()
        else:
            self.clickedButtonName = val['event']
            self.clickedButtonIndex = self.buttonNamesList.index(self.clickedButtonName)
            self.buttonsList[self.clickedButtonIndex].setChecked(True)
            self.showTes(self.clickedButtonIndex)
            data = val['data']
            for x in range(8):
                self.teList[x].set_val(data[x])

    def buttonClicked(self):
        for button in self.buttonsList:
            if button.isChecked():
                self.clickedButtonIndex = self.buttonsList.index(button)
                self.clickedButtonName = self.buttonNamesList[self.clickedButtonIndex]
        self.showTes(self.clickedButtonIndex)

    def showTes(self, index):
        self.hideOtherTes()

        if index == 1:
            delayLabels = ['delay']
            self.teList[0].set_visible(True)
            self.teList[0].set_placeholder(delayLabels[0])
        elif index == 2:
            sincLabels = ['duration (s)', 'freqOffset', 'phaseOffset', 'timeBwProduct', 'apodization',
                          'sliceThickness (m)']
            [self.teList[x].set_visible(True) for x in range(6)]
            [self.teList[x].set_placeholder(sincLabels[x]) for x in range(6)]
        elif index == 3:
            trapLabels = ['flatTime (s)']
            self.teList[0].set_visible(True)
            self.teList[0].set_placeholder(trapLabels[0])
        elif index == 4:
            trapLabels = ['channel', 'duration (s)', 'area', 'flatTime (s)', 'flatArea', 'amplitude (Hz)',
                          'riseTime (s)']
            [self.teList[x].set_visible(True) for x in range(7)]
            [self.teList[x].set_placeholder(trapLabels[x]) for x in range(7)]
        elif index == 6:
            adcLabels = ['numSamples', 'dwell (s)', 'duration (s)', 'delay (s)', 'freqOffset', 'phaseOffset']
            [self.teList[x].set_visible(True) for x in range(6)]
            [self.teList[x].set_placeholder(adcLabels[x]) for x in range(6)]

    def hideOtherTes(self):
        [x.set_visible(False) for x in self.teList]
        [x.set_val("") for x in self.teList]


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
        self.addInPort('sequence_obj_in', 'DICT')
        self.addOutPort('sequence_obj_out', 'DICT')

        return 0

    def validate(self):
        if 'ComputeEvents' in self.widgetEvents() or self.portEvents():
            self.setDetailLabel(self.getVal('Unique Node Name'))

    def compute(self):
        if 'ComputeEvents' in self.widgetEvents() or self.portEvents():
            input = self.getData('sequence_obj_in')
            system = input['system']

            currentEvents, currentEventNames = [], []
            for currentEvent in range(6):
                eventDict = self.getVal('Event ' + str(currentEvent + 1))
                eventName = eventDict['event'] if 'event' in eventDict else None
                eventValues = eventDict['data'] if 'data' in eventDict else None

                if eventName == 'Delay':
                    currentEvents.append(makedelay(float(eventValues[0])))
                elif eventName == 'Rf':
                    duration, freqOffset, phaseOffset, timeBwProduct, apodization, sliceThickness = [
                        float(eventValues[x]) for x in range(6)]
                    kwargsForSinc = {"flipAngle": system.flip, "system": system, "duration": duration,
                                     "freqOffset": freqOffset, "phaseOffset": phaseOffset,
                                     "timeBwProduct": timeBwProduct,
                                     "apodization": apodization, "maxGrad": system.maxGrad,
                                     "maxSlew": system.maxSlew,
                                     "sliceThickness": sliceThickness}
                    rf, gz = makesincpulse(**kwargsForSinc)
                    currentEvents.append(rf)
                    currentEvents.append(gz)
                elif eventName == 'Gx':
                    flatTime = float(eventValues[0])
                    channel = 'x'
                    duration, area, amplitude, riseTime = [0] * 4
                    flatArea = system.Nx * (1 / system.fov)
                    kwargsForTrap = {"channel": channel, "system": system, "duration": duration, "area": area,
                                     "flatTime": flatTime, "flatArea": flatArea, "amplitude": amplitude,
                                     "maxGrad": system.maxGrad, "maxSlew": system.maxSlew, "riseTime": riseTime}
                    currentEvents.append(maketrapezoid(**kwargsForTrap))
                elif eventName == 'G':
                    channel = eventValues[0]
                    duration, area, flatTime, flatArea, amplitude, riseTime = [float(eventValues[x]) for x in
                                                                               range(1, 7)]
                    kwargsForTrap = {"channel": channel, "system": system, "duration": duration, "area": area,
                                     "flatTime": flatTime, "flatArea": flatArea, "amplitude": amplitude,
                                     "maxGrad": system.maxGrad, "maxSlew": system.maxSlew, "riseTime": riseTime}
                    currentEvents.append(maketrapezoid(**kwargsForTrap))
                elif eventName == 'GyPre':
                    pass
                elif eventName == 'ADC':
                    numSamples, dwell, duration, delay, freqOffset, phaseOffset = [float(eventValues[x]) for x in
                                                                                   range(6)]
                    kwargsForAdc = {"numSamples": numSamples, "system": system, "dwell": dwell, "duration": duration,
                                    "delay": delay, "freqOffset": freqOffset, "phaseOffset": phaseOffset}
                    adc = makeadc(**kwargsForAdc)
                    currentEvents.append(adc)
                if eventName != 'Rf':
                    currentEventNames.append(eventName)
                else:
                    currentEventNames.append('Rf')
                    currentEventNames.append('Gz')

            allEvents = input['events'] if 'events' in input else []
            allEventNames = input['eventNames'] if 'eventNames' in input else []
            allEvents.append(currentEvents)
            allEventNames.append(currentEventNames)
            input['events'], input['eventNames'] = allEvents, allEventNames
            self.setData('sequence_obj_out', input)

            # To display the computed info inside the node
            infoText = ""
            for currentEvent in currentEvents:
                attrs = [attr for attr in dir(currentEvent) if not callable(attr) and not attr.startswith('__')]
                text = ""
                for attr in attrs:
                    text += attr + ": " + str(getattr(currentEvent, attr)) + "\n"
                infoText += text + "~~~\n"
            self.setAttr('EventInfo', val=infoText)

        return 0
