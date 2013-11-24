#!/usr/bin/python
# -*- coding: utf-8 -*-


import sys
import os
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
        self.setGeometry(300, 300, 1000, 600)
     
        self.graphwin = pg.GraphicsWindow(title="Current Sense Analysis")
        self.graphwin.resize(600,800)
        self.graphwin.setWindowTitle('Current vs time')
        self.setCentralWidget(self.graphwin)

        # Create a status bar
        self.statusBar()

        # Add a dock to the right of the plot
        self.statsDock = QtGui.QDockWidget(self)
        self.statsDock.setWindowTitle("Statistics")
        self.addDockWidget(QtCore.Qt.RightDockWidgetArea, self.statsDock)

        # Create a menu bar
        menubar = self.menuBar()

        # Add button and shortcut to open files
        openFile = QtGui.QAction(QtGui.QIcon('open.png'), 'Open File', self)
        openFile.setShortcut('Ctrl+O')
        openFile.setStatusTip('Open new File')
        openFile.triggered.connect(self.openFile)

        # Add button and shortcut to open folders
        openFolder = QtGui.QAction(QtGui.QIcon('open.png'), 'Open Folder', self)
        openFolder.setStatusTip('Open Folder')
        openFolder.triggered.connect(self.openFolder)

        # Add button and shortcut to quit the program
        exitAction = QtGui.QAction(QtGui.QIcon('exit24.png'), 'Exit', self)
        exitAction.setShortcut('Ctrl+Q')
        exitAction.setStatusTip('Exit application')
        exitAction.triggered.connect(self.close)

        menuOpen = menubar.addMenu('Open')
        menuExit = menubar.addMenu('Exit')

        menuOpen.addAction(openFile)
        menuOpen.addAction(openFolder)
        menuExit.addAction(exitAction)

        self.setWindowTitle('Data Analysis') 

        self.layoutStatistics()

        self.fileLabelMin.setText("Average Current: %.2f mA" % (0))
        self.fileLabelMax.setText("Standard Deviation: %.2f mA" % (0))
        self.fileLabelVar.setText("Variance: %.2f mA" %(0))

        self.triggerLabelMin.setText("Average Current: %.2f mA" % (0))
        self.triggerLabelMax.setText("Standard Deviation: %.2f mA" % (0))
        self.triggerLabelVar.setText("Variance: %.2f mA" % (0))
        
        
        self.show()

    def layoutFolderSidebar(self):
        # Add a dock to the left of the plot
        self.fileDock = QtGui.QDockWidget(self)
        self.addDockWidget(QtCore.Qt.LeftDockWidgetArea, self.fileDock)

        self.list = QtGui.QListWidget(self.fileDock)

        self.filelist = QtGui.QGroupBox(self.fileDock)
        self.filelistlayout = QtGui.QVBoxLayout()
        self.filelistlayout.addWidget(self.list)
        self.filelistlayout.setContentsMargins(0,0,0,0)

        self.filelist.setLayout(self.filelistlayout)
        self.filelist.setContentsMargins(0,0,0,0)

        self.fileDock.setWidget(self.filelist)
        self.filelist.setMinimumSize(150, 50)
        self.list.itemDoubleClicked.connect(self.showSelectedFile)

    def openFolder(self):
        # Prompt for a folder
        folder = QtGui.QFileDialog(self, "Open Folder", ".")
        folder.setFileMode(QtGui.QFileDialog.Directory)
        folder.setOption(QtGui.QFileDialog.ShowDirsOnly, True)

        if folder.exec_():
            for folderPath in folder.selectedFiles():
                self.folder_path = "%s/" %(folderPath)

        # Ensure sidebar exists
        if not hasattr(self, 'fileDock'):
            self.layoutFolderSidebar()

        dirs = os.listdir(self.folder_path)
        for file in dirs:
          if os.path.isfile(os.path.join(self.folder_path,file)):
            self.list.addItem(file)

        self.fileDock.updateGeometry()

    def showSelectedFile(self):
        self.selectedfile = self.list.currentItem().text()
        

        selectedFileStr = str(self.selectedfile)
        selectedFilePath = "%s%s" %(self.folder_path, selectedFileStr)

        time, current, trigger = self.readFile(selectedFilePath)
        self.calculateTriggerStats(time, current, trigger)
        self.showPlot(time, current, trigger)

    def openFile(self):
        fname = QtGui.QFileDialog.getOpenFileName(self, 'Open file', '.')
        time, current, trigger = self.readFile(fname)

        avgCurrent, stdevCurrent, varCurrent = self.calculateTriggerStats(time, current, trigger)
        self.setTriggerStats(avgCurrent, stdevCurrent, varCurrent)

        avgCurrent, stdevCurrent, varCurrent = self.calculateStats(time, current)
        self.setFileStats(avgCurrent, stdevCurrent, varCurrent)

        self.showPlot(time, current, trigger)
        
    def calculateTriggerStats(self, time, current, trigger):
      triggerThreshold = 1.0
      triggerCurrent = []

      for index, triggerValue in enumerate(trigger):
        if triggerValue >= triggerThreshold:
          triggerCurrent.extend([current[index]])

      avgCurrent = np.average(triggerCurrent)
      stdevCurrent = np.std(triggerCurrent)
      varCurrent = np.var(triggerCurrent)

      return (avgCurrent, stdevCurrent, varCurrent)

    def calculateStats(self, time, current):
      avgCurrent = np.average(current)
      stdevCurrent = np.std(current)
      varCurrent = np.var(current)
      
      return (avgCurrent, stdevCurrent, varCurrent)

    def highlightTriggerRegions(self, time, trigger):
      triggerThreshold = 1.0
      minX = 0

      for index, triggerValue in enumerate(trigger):
        if triggerValue >= triggerThreshold and minX == 0:
          minX = time[index]
        elif minX != 0:
          self.regionT = pg.LinearRegionItem([minX, time[index]],movable=False)
          self.plot1.addItem(self.regionT)


    def layoutStatistics(self):
        # Statistics for the whole window
        self.wholeWindowBox = QtGui.QGroupBox(self.statsDock)
        self.wholeWindowBox.setFlat(True)
        self.wholeWindowBox.setTitle("Whole File")

        self.fileLabelMin = QtGui.QLabel(self.statsDock)
        self.fileLabelMax = QtGui.QLabel(self.statsDock)
        self.fileLabelVar = QtGui.QLabel(self.statsDock)
        

        self.wholeLayout = QtGui.QVBoxLayout()
        self.wholeLayout.addWidget(self.fileLabelMin)
        self.wholeLayout.addWidget(self.fileLabelMax)
        self.wholeLayout.addWidget(self.fileLabelVar)
        self.wholeWindowBox.setLayout(self.wholeLayout)

        # Statistics for just the area under the trigger
        self.triggerBox = QtGui.QGroupBox(self.statsDock)
        self.triggerBox.setFlat(True)
        self.triggerBox.setTitle("Trigger Area(s)")

        self.triggerLabelMin = QtGui.QLabel(self.statsDock)
        self.triggerLabelMax = QtGui.QLabel(self.statsDock)
        self.triggerLabelVar = QtGui.QLabel(self.statsDock)

        self.triggerLayout = QtGui.QVBoxLayout()
        self.triggerLayout.addWidget(self.triggerLabelMin)
        self.triggerLayout.addWidget(self.triggerLabelMax)
        self.triggerLayout.addWidget(self.triggerLabelVar)
        self.triggerBox.setLayout(self.triggerLayout)

        # Statistics for the area between the selectors
        self.regionBox = QtGui.QGroupBox(self.statsDock)
        self.regionBox.setFlat(True)
        self.regionBox.setTitle("Selection Area")

        self.regionLabelMin = QtGui.QLabel(self.statsDock)
        self.regionLabelMax = QtGui.QLabel(self.statsDock)
        self.regionLabelVar = QtGui.QLabel(self.statsDock)
        self.regionLabelVar.setText("Max Current: %.2f mA" % (0))

        self.selectorLayout = QtGui.QVBoxLayout()
        self.selectorLayout.addWidget(self.regionLabelMin)
        self.selectorLayout.addWidget(self.regionLabelMax)
        self.selectorLayout.addWidget(self.regionLabelVar)
        self.regionBox.setLayout(self.selectorLayout)

        self.statsBox = QtGui.QGroupBox(self.statsDock)
        self.vbox = QtGui.QVBoxLayout()
        self.vbox.addWidget(self.wholeWindowBox)
        self.vbox.addWidget(self.triggerBox)
        self.vbox.addWidget(self.regionBox)
        self.vbox.addStretch(1)

        self.statsBox.setLayout(self.vbox)
        self.statsDock.setWidget(self.statsBox)

    def readFile(self, fname):
        f = open(fname, 'rb')
        time = []
        current = []
        trigger = []
        with f:
          self.reader = csv.reader(f)

          for row in self.reader:
            time.extend([float(row[0])])
            current.extend([float(row[3])])
            trigger.extend([float(row[6])])

        return (time, current, trigger)


    def setRegionStats(self):
        minX, maxX = self.region.getRegion()

        rMinIndex = 0
        rMaxIndex = 0

        for index, t in enumerate(self.plotDataX):
          if t <= minX:
            rMinIndex = index
          if t <= maxX:
            rMaxIndex = index

        avgCurrent, stdevCurrent, varCurrent = self.calculateStats(self.plotDataX[rMinIndex:rMaxIndex], self.plotDataY[rMinIndex:rMaxIndex])

        self.regionLabelMin.setText("Average Current: %.3f mA" % avgCurrent)
        self.regionLabelMax.setText("Standard Deviation: %.3f mA" % stdevCurrent)
        self.regionLabelVar.setText("Variance: %.3f mA" % varCurrent)

    # Set statistics for the entire file
    def setFileStats(self, avg, stddev, var):
        self.fileLabelMin.setText("Average Current: %.2f mA" % avg)
        self.fileLabelMax.setText("Standard Deviation: %.2f mA" % stddev)
        self.fileLabelVar.setText("Variance: %.2f mA" % var)

    # Set statistics for the area(s) under the trigger signal
    def setTriggerStats(self, avg, stddev, var):
        self.triggerLabelMin.setText("Average Current: %.2f mA" % avg)
        self.triggerLabelMax.setText("Standard Deviation: %.2f mA" % stddev)
        self.triggerLabelVar.setText("Variance: %.2f mA" % var)

    def showPlot(self, time, current, trigger):
        self.plotDataX = time
        self.plotDataY = current

        if not hasattr(self, 'plot1'):
          self.plot1 = self.graphwin.addPlot(title="Plot of current vs time", labels={'left':"Current(mA)", 'bottom':"Time(s)"})
          self.region = pg.LinearRegionItem()
          self.plot1.addItem(self.region)
          self.region.sigRegionChanged.connect(self.setRegionStats)
          self.plot1.showGrid(y=True)

        self.plot1.plot(time, current, pen=(0,255,0))
        self.plot1.plot(time, trigger, pen=(255,0,0))
        self.plot1.enableAutoRange(enable=True)
        self.region.setRegion([0.1, 0.4])

def main():
    
    app = QtGui.QApplication(sys.argv)
    ex = Example()
    #sys.exit(app.exec_())
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
      app.exec_()
      app.deleteLater()
      app.exit()

if __name__ == '__main__':
    main()
