import gpi


class ExternalNode(gpi.NodeAPI):
    """This node lets the user specify a file name and save location to write open-source file format seq files.
    """

    def initUI(self):
        # IO Ports
        self.addInPort(title='input', type='DICT')

        # Widgets
        self.addWidget('SaveFileBrowser', 'File location', button_title='Save .seq file at')
        self.addWidget('PushButton', 'Write seq file', button_title='Write')
        return 0

    def compute(self):
        if 'Write seq file' in self.widgetEvents():
            inDict = self.getData('input')
            seq = inDict['seq']
            fileLocation = self.getVal('File location')
            fileLocation += '.seq' if '.seq' not in fileLocation else ''
            seq.write(fileLocation)
