from PyQt4 import QtGui, QtCore

class MainWindow(QtGui.QMainWindow):
    def __init__(self):
        QtGui.QMainWindow.__init__(self)
        self.setWindowTitle('Extended Side Dock Areas')
        self.window = QtGui.QMainWindow(self)
        self.window.setCentralWidget(QtGui.QTextEdit(self.window))
        self.window.setWindowFlags(QtCore.Qt.Widget)
        self.setCentralWidget(self.window)
        self.dock1 = QtGui.QDockWidget(self.window)
        self.dock1.setWidget(QtGui.QTextEdit(self.dock1))
        self.window.addDockWidget(
            QtCore.Qt.BottomDockWidgetArea, self.dock1)
        self.dock2 = QtGui.QDockWidget(self)
        self.dock2.setAllowedAreas(
            QtCore.Qt.LeftDockWidgetArea | QtCore.Qt.RightDockWidgetArea)
        self.dock2.setWidget(QtGui.QLabel('Left Dock Area', self.dock2))
        self.addDockWidget(QtCore.Qt.LeftDockWidgetArea, self.dock2)
        self.dock3 = QtGui.QDockWidget(self)
        self.dock3.setWidget(QtGui.QLabel('Right Dock Area', self.dock3))
        self.addDockWidget(QtCore.Qt.RightDockWidgetArea, self.dock3)

if __name__ == '__main__':

    import sys
    app = QtGui.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
