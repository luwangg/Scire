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
        self.setGeometry(300, 300, 1200, 800)
     
        self.graphwin = pg.GraphicsWindow(title="Current Sense Analysis")
  #      self.graphwin.resize(600,800)
        self.graphwin.setWindowTitle('Current vs time')
        self.setCentralWidget(self.graphwin)

        # Create a status bar
        self.statusBar()

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

        #aboutAction = QtGui.QAction(None, 'About', self)
        #aboutAction.triggered.connect(self.aboutWindow)

        menuFile = menubar.addMenu('File')
        #menuHelp = menubar.addMenu('Help')

        menuFile.addAction(openFile)
        menuFile.addAction(openFolder)
        menuFile.addAction(exitAction)

        self.setWindowTitle('Data Analysis') 
        self.layoutStatistics()  
        self.layoutControls()
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

    def openFile(self):
        fname = QtGui.QFileDialog.getOpenFileName(self, 'Open file', '.')
        self.plotFile(fname)

    def showSelectedFile(self):
        fname = self.list.currentItem().text()
        fullPath = "%s%s" %(self.folder_path, fname)
        self.plotFile(fullPath)

    def plotFile(self, fullPath):
        time, current, trigger = self.readFile(fullPath)

        avgCurrent, stdevCurrent, varCurrent = self.calculateStats(time, current)
        self.setFileStats(avgCurrent, stdevCurrent, varCurrent)

        avgCurrentTrig, stddevCurrentTrig, varCurrentTrig = self.calculateTriggerStats(time, current, trigger)
        self.setTriggerStats(avgCurrentTrig, stddevCurrentTrig, varCurrentTrig)

        self.showPlot(time, current, trigger)
        self.highlightTriggerRegions(time, trigger)

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
            self.layoutStatsTable()

        dirs = os.listdir(self.folder_path)
        self.list.clear()
        for file in dirs:
          if os.path.isfile(os.path.join(self.folder_path,file)):
            self.list.addItem(file)

        self.fileStats = np.zeros([int(self.list.count()), 3])

        self.fileDock.updateGeometry()
        self.populateStatsTable()

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

    # Highlights the last trigger region
    def highlightTriggerRegions(self, time, trigger):
      triggerThreshold = 1.0
      minX = 0

      for index, triggerValue in enumerate(trigger):
        if triggerValue >= triggerThreshold and minX == 0:
          minX = time[index]
        elif triggerValue < triggerThreshold and minX != 0:
          self.regionT = pg.LinearRegionItem([minX, time[index-1]],movable=False,brush=pg.mkColor("FF363618"))
          self.plot1.addItem(self.regionT)
          minX = 0

    def layoutStatistics(self):
        # Add a dock to the right of the plot
        self.statsDock = QtGui.QDockWidget(self)
        self.statsDock.setWindowTitle("Statistics")
        self.addDockWidget(QtCore.Qt.RightDockWidgetArea, self.statsDock)

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
        
        self.fileLabelMin.setText("Average Current: %.2f mA" % 0)
        self.fileLabelMax.setText("Standard Deviation: %.2f mA" % 0)
        self.fileLabelVar.setText("Variance: %.2f mA" % 0)

        self.triggerLabelMin.setText("Average Current: %.2f mA" % 0)
        self.triggerLabelMax.setText("Standard Deviation: %.2f mA" % 0)
        self.triggerLabelVar.setText("Variance: %.2f mA" % 0)

        self.regionLabelMin.setText("Average Current: %.2f mA" % 0)
        self.regionLabelMax.setText("Standard Deviation: %.2f mA" % 0)
        self.regionLabelVar.setText("Variance: %.2f mA" % 0)

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

    def layoutControls(self):
        self.controlDock = QtGui.QDockWidget(self)
        self.controlDock.setWindowTitle("Controls")
        self.addDockWidget(QtCore.Qt.RightDockWidgetArea, self.controlDock)

        self.controlBox = QtGui.QGroupBox(self.controlDock)
        self.controlVBox = QtGui.QVBoxLayout()
        self.controlVBox.addStretch(1)

        self.controlBox.setLayout(self.controlVBox)
        self.controlDock.setWidget(self.controlBox)

    def layoutStatsTable(self):
        self.tableDock = QtGui.QDockWidget(self)
        self.addDockWidget(QtCore.Qt.BottomDockWidgetArea, self.tableDock)

        self.table = QtGui.QTableWidget()
        self.table.setColumnCount(3) # Number of stats

        self.tableDock.setWidget(self.table)

    def populateStatsTable(self):
        headers = ["Avg Current", "Stdev Current", "Current Variance"]
        self.table.setHorizontalHeaderLabels(headers)
        self.table.resizeColumnsToContents()

        self.table.setRowCount(self.list.count())

        fileNames = []
        for index in xrange(self.list.count()):
          fileNames.append(self.list.item(index))
        files = [i.text() for i in fileNames]

        self.table.setVerticalHeaderLabels(files)
        self.table.setItem(1,1,QtGui.QTableWidgetItem("Hello"))

        for index, fileName in enumerate(files):
          selectedFilePath = "%s%s" % (self.folder_path, fileName)

          time, current, trigger = self.readFile(selectedFilePath)
          avgCurrent, stdevCurrent, varCurrent = self.calculateStats(time, current)

          self.table.setItem(index, 0, QtGui.QTableWidgetItem("%.3f" % avgCurrent))
          self.table.setItem(index, 1, QtGui.QTableWidgetItem("%.3f" % stdevCurrent))
          self.table.setItem(index, 2, QtGui.QTableWidgetItem("%.3f" % varCurrent))
        
        self.table.updateGeometry()
        self.table.verticalHeader().sectionDoubleClicked.connect(self.showFileFromTable)

    def showFileFromTable(self, index):
        fname = self.table.verticalHeaderItem(index).text()
        fullPath = "%s%s" %(self.folder_path, fname)
        self.plotFile(fullPath)

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
        # self.plot1.plot(time, trigger, pen=(255,0,0))
        self.plot1.enableAutoRange(enable=True)
        self.region.setRegion([0.1, 0.2])

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
