#!/usr/bin/python
# -*- coding: utf-8 -*-


import sys
import pyqtgraph as pg
from pyqtgraph.Qt import QtGui, QtCore
import numpy as np
import pyqtgraph as pg
import csv

class Example(QtGui.QMainWindow):
    
    def __init__(self):
        super(Example, self).__init__()
        
        self.initUI()
        
    def initUI(self):               
        
     
        
        self.graphwin = pg.GraphicsWindow(title="Current Sense Analysis")
        self.graphwin.resize(1000,600)
        self.graphwin.setWindowTitle('Current vs time')
        self.setCentralWidget(self.graphwin)
        #self.graphwin.move(15,10)
        self.dock1 = QtGui.QDockWidget(self)
        self.dock2 = QtGui.QDockWidget(self)
        self.dock1.setWidget(QtGui.QTextEdit(self.dock1))
        self.dock2.setWidget(QtGui.QTextEdit(self.dock2))
        self.addDockWidget(
            QtCore.Qt.RightDockWidgetArea, self.dock1)
        self.addDockWidget(QtCore.Qt.RightDockWidgetArea, self.dock2)
        #self.splitDockWidget(self.dock1, self.dock2, Qt.Vertical)
        
        openFile = QtGui.QAction(QtGui.QIcon('open.png'), 'Open', self)
        openFile.setShortcut('Ctrl+O')
        openFile.setStatusTip('Open new File')
        openFile.triggered.connect(self.showDialog)

        exitAction = QtGui.QAction(QtGui.QIcon('exit24.png'), 'Exit', self)
        exitAction.setShortcut('Ctrl+Q')
        exitAction.setStatusTip('Exit application')
        exitAction.triggered.connect(self.close)

        self.statusBar()

        menubar = self.menuBar()
        fileopen = menubar.addMenu('&File')
        exitaction = menubar.addMenu('Exit')
        fileopen.addAction(openFile)
        exitaction.addAction(exitAction)

        #toolbar = self.addToolBar('&File')
        #toolbar.addAction(openFile)
        self.setGeometry(300, 300, 350, 250)
        self.setWindowTitle('Data Analysis')    
        self.show()
        
    def showDialog(self):

        fname = QtGui.QFileDialog.getOpenFileName(self, 'Open file', '.')
        
        f = open(fname, 'rb')
        xTime = []
        yCurrent = []
        yTrigger = []
        with f:
          self.reader = csv.reader(f)

          for row in self.reader:
            xTime.extend([float(row[0])])
            yCurrent.extend([float(row[3])])
            yTrigger.extend([float(row[6])])

          p1 = self.graphwin.addPlot(title=fname, labels={'left':"Current (mA)", 'bottom':"Time (s)"})
          p1.plot(xTime, yCurrent, pen=(0,255,0))
          p1.plot(xTime, yTrigger, pen=(255,0,0))
        
def main():
    
    app = QtGui.QApplication(sys.argv)
    ex = Example()
    #sys.exit(app.exec_())
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
      app.exec_()

if __name__ == '__main__':
    main()








