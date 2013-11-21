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
        self.graphwin.setWindowTitle('setWindowTitle')
        self.setCentralWidget(self.graphwin)
        
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
        fileMenu = menubar.addMenu('&File')
        fileMenu.addAction(openFile)

        toolbar = self.addToolBar('Exit')
        toolbar.addAction(exitAction)
        
        self.setGeometry(300, 300, 350, 250)
        self.setWindowTitle('Data Analysis')    
        self.show()
        
    def showDialog(self):

        
        fname = QtGui.QFileDialog.getOpenFileName(self, 'Open file', 
                '/home')
        
        f = open(fname, 'rb')
        xTime = []
        yCurrent = []
        yTrigger = []
        with f:
          self.reader = csv.reader(f)
          for row in self.reader:
            xTime.extend([float(row[0])])
            yCurrent.extend([float(row[1])])
            yTrigger.extend([float(row[2])])

          p1 = self.graphwin.addPlot(title="Main plot")
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








