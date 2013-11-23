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
        
        self.folder_path = ""


        

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

        # Ensure sidebar exists
        if not hasattr(self, 'fileDock'):
            self.layoutFolderSidebar()

        folderPath = ""
        if folder.exec_():
            for folderPath in folder.selectedFiles():
                self.folder_path = "%s/" %(folderPath)

        dirs = os.listdir(self.folder_path)
        for file in dirs:
          if os.path.isfile(os.path.join(self.folder_path,file)):
            self.list.addItem(file)

    def showSelectedFile(self):
        self.selectedfile = self.list.currentItem().text()
        
        selectedFileStr = str(self.selectedfile)
        selectedFilePath = "%s%s" %(self.folder_path, selectedFileStr)

        time, current, trigger = self.readFile(selectedFilePath)
        self.calculateStats(time, current, trigger)
        self.showPlot(time, current, trigger)

    def openFile(self):
        fname = QtGui.QFileDialog.getOpenFileName(self, 'Open file', '.')
        time, current, trigger = self.readFile(fname)
        self.calculateStats(time, current, trigger)
        self.showPlot(time, current, trigger)
        
    def calculateStats(self, time, current, trigger):
      triggerThreshold = 1.0

      i = 0
      avgtriggercurrent = 0

      for index, triggerValue in enumerate(trigger):
        if triggerValue >= triggerThreshold:
          avgtriggercurrent += current[index]
          i += 1

      avgtriggercurrent = avgtriggercurrent/i
      avgCurrent = np.average(current)
          
      ptrig = float(avgtriggercurrent * 5.1)
      p = float(avgCurrent * 5.1)

      ptrigstring = str(ptrig)
      pstring = str(p)

      print ptrigstring
      print pstring
                               
    def layoutStatistics(self):

        # Statistics for the whole window
        self.wholeWindowBox = QtGui.QGroupBox(self.statsDock)
        self.wholeWindowBox.setFlat(True)
        self.wholeWindowBox.setTitle("Whole File")

        self.fileLabelMin = QtGui.QLabel(self.statsDock)
        self.fileLabelMin.setText("Min Current: %.2f mA" % (0))

        self.fileLabelMax = QtGui.QLabel(self.statsDock)
        self.fileLabelMax.setText("Max Current: %.2f mA" % (0))

        self.wholeLayout = QtGui.QVBoxLayout()
        self.wholeLayout.addWidget(self.fileLabelMin)
        self.wholeLayout.addWidget(self.fileLabelMax)
        self.wholeWindowBox.setLayout(self.wholeLayout)

        # Statistics for just the area under the trigger
        self.triggerBox = QtGui.QGroupBox(self.statsDock)
        self.triggerBox.setFlat(True)
        self.triggerBox.setTitle("Trigger Area(s)")

        self.triggerLabelMin = QtGui.QLabel(self.statsDock)
        self.triggerLabelMin.setText("Min Current: %.2f mA" % (0))

        self.triggerLabelMax = QtGui.QLabel(self.statsDock)
        self.triggerLabelMax.setText("Max Current: %.2f mA" % (0))

        self.triggerLayout = QtGui.QVBoxLayout()
        self.triggerLayout.addWidget(self.triggerLabelMin)
        self.triggerLayout.addWidget(self.triggerLabelMax)
        self.triggerBox.setLayout(self.triggerLayout)

        # Statistics for the area between the selectors
        self.regionBox = QtGui.QGroupBox(self.statsDock)
        self.regionBox.setFlat(True)
        self.regionBox.setTitle("Selection Area")

        self.regionLabelMin = QtGui.QLabel(self.statsDock)
        self.regionLabelMin.setText("Min Current: %.2f mA" % (0))

        self.regionLabelMax = QtGui.QLabel(self.statsDock)
        self.regionLabelMax.setText("Max Current: %.2f mA" % (0))

        self.selectorLayout = QtGui.QVBoxLayout()
        self.selectorLayout.addWidget(self.regionLabelMin)
        self.selectorLayout.addWidget(self.regionLabelMax)
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

    def regionChanged(self):
        minX, maxX = self.region.getRegion()
        self.regionLabelMin.setText("Region Min: %.3f" % (minX))
        self.regionLabelMax.setText("Region Max: %.3f" % (maxX))

    def showPlot(self,time,current,trigger):
        self.plot1 = self.graphwin.addPlot(title="Plot of current vs time", labels={'left':"Current(mA)", 'bottom':"Time(s)"})
        self.plot1.plot(time, current, pen=(0,255,0))
        self.plot1.plot(time, trigger, pen=(255,0,0))

        self.region = pg.LinearRegionItem()
        self.plot1.addItem(self.region)
        self.region.setRegion([0.1, 0.4])
        self.region.sigRegionChanged.connect(self.regionChanged)

def main():
    
    app = QtGui.QApplication(sys.argv)
    ex = Example()
    #sys.exit(app.exec_())
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
      app.exec_()

if __name__ == '__main__':
    main()
