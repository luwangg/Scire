from PyQt4 import QtGui, QtCore

class Window(QtGui.QWidget):
    def __init__(self):
        QtGui.QWidget.__init__(self)
        layout = QtGui.QVBoxLayout(self)
        self.button = QtGui.QPushButton('Select Files', self)
        layout.addWidget(self.button)
        self.button.clicked.connect(self.handleButton)

    def handleButton(self):
        title = self.button.text()
        
        for path in QtGui.QFileDialog.getOpenFileNames(self, title):
            print path

if __name__ == '__main__':

    import sys
    app = QtGui.QApplication(sys.argv)
    window = Window()
    window.show()
    sys.exit(app.exec_())
