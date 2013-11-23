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
        
     
        self.graphwin = pg.GraphicsWindow(title="Current Sense Analysis")
        self.graphwin.resize(1000,600)
        self.graphwin.setWindowTitle('Current vs time')
        self.setCentralWidget(self.graphwin)
        #self.graphwin.move(15,10)
        
        self.folder_path = ""
        self.dock1 = QtGui.QDockWidget(self)
        self.dock2 = QtGui.QDockWidget(self)
        self.dock3 = QtGui.QDockWidget(self)
        self.addDockWidget(
            QtCore.Qt.RightDockWidgetArea, self.dock1)
        self.addDockWidget(QtCore.Qt.RightDockWidgetArea, self.dock2)
        self.addDockWidget(QtCore.Qt.LeftDockWidgetArea, self.dock3)
        #self.list = QtGui.QListWidget(self)
                           
        #self.splitDockWidget(self.dock1, self.dock2, Qt.Vertical)

        # Create a status bar
        self.statusBar()


        # Add a dock to the right of the plot
        self.dock1 = QtGui.QDockWidget(self)
        self.dock1.setWindowTitle("Statistics")
        self.addDockWidget(QtCore.Qt.RightDockWidgetArea, self.dock1)

        #self.splitDockWidget(self.dock1, self.dock2, Qt.Vertical)

        # Create a menu bar
        menubar = self.menuBar()

        # Add button and shortcut to open files
        openFile = QtGui.QAction(QtGui.QIcon('open.png'), 'Open', self)
        openFile.setShortcut('Ctrl+O')
        openFile.setStatusTip('Open new File')
        openFile.triggered.connect(self.showDialog)


        openFolder = QtGui.QAction(QtGui.QIcon('open.png'), 'Open', self)
        openFolder.setShortcut('Ctrl+O')
        openFolder.setStatusTip('Open Folder')
        openFolder.triggered.connect(self.openFolder)

        # Add button and shortcut to quit the program

        exitAction = QtGui.QAction(QtGui.QIcon('exit24.png'), 'Exit', self)
        exitAction.setShortcut('Ctrl+Q')
        exitAction.setStatusTip('Exit application')
        exitAction.triggered.connect(self.close)


        fileopen = menubar.addMenu('&File')
        folderopen = menubar.addMenu('&Folder')
        exitaction = menubar.addMenu('Exit')
        fileopen.addAction(openFile)
        folderopen.addAction(openFolder)
        exitaction.addAction(exitAction)

        #toolbar = self.addToolBar('&File')
        #toolbar.addAction(openFile)
        self.setGeometry(300, 300, 350, 250)
        self.setWindowTitle('Data Analysis')    
        self.show()

        
    
    def openFolder(self):
        folder = QtGui.QFileDialog(self)
        folder.setFileMode(QtGui.QFileDialog.Directory)
        folder.setOption(QtGui.QFileDialog.ShowDirsOnly, True)
        #foldertreeview = folder.findChild(QtGui.QTreeView)
        #foldertreeview.setSelectionMode(QtGui.QAbstractItemView.ExtendedSelection)

        self.list = QtGui.QListWidget(self.dock3)
        #btn = QtGui.QPushButton('Open File', self.dock3)
        #folder_path = ""
        filepath = ""
        if folder.exec_():
            for filepath in folder.selectedFiles():
                print filepath
                self.folder_path = "%s/" %(filepath)
        dirs = os.listdir(self.folder_path)
        for file in dirs:
          print file
          self.list.addItem(file)
           

        filelist = QtGui.QGroupBox(self.dock3)
        filelistlayout = QtGui.QVBoxLayout()
        filelistlayout.addWidget(self.list)
        #filelistlayout.addWidget(btn)
        

        filelist.setLayout(filelistlayout)
        self.dock3.setWidget(filelist)

        #btn.clicked.connect(self.showfile)
        self.list.itemDoubleClicked.connect(self.showselectedfile)

    def showselectedfile(self):

        self.selectedfile = self.list.currentItem().text()
        print self.selectedfile
        
        selectedfilestr = str(self.selectedfile)
        selectedfilepath = "%s%s" %(self.folder_path, selectedfilestr)
        print selectedfilepath
        clickedfile= QtGui.QFileDialog.getOpenFileName(self, 'Open File', selectedfilepath)
        
        f1 = open(clickedfile, 'rb')  

        # def updatePlot(self, ):                                 
    def updateStatistics(self, minCurrent, maxCurrent):

        # Statistics for the whole window
        self.wholeWindowBox = QtGui.QGroupBox(self.dock1)
        self.wholeWindowBox.setFlat(True)
        self.wholeWindowBox.setTitle("Whole File")

        self.fileLabelMin = QtGui.QLabel(self.dock1)
        self.fileLabelMin.setText("Min Current: %.2f mA" % (minCurrent))

        self.fileLabelMax = QtGui.QLabel(self.dock1)
        self.fileLabelMax.setText("Max Current: %.2f mA" % (maxCurrent))

        self.wholeLayout = QtGui.QVBoxLayout()
        self.wholeLayout.addWidget(self.fileLabelMin)
        self.wholeLayout.addWidget(self.fileLabelMax)
        self.wholeWindowBox.setLayout(self.wholeLayout)

        # Statistics for just the area under the trigger
        self.triggerBox = QtGui.QGroupBox(self.dock1)
        self.triggerBox.setFlat(True)
        self.triggerBox.setTitle("Trigger Area(s)")

        self.triggerLabelMin = QtGui.QLabel(self.dock1)
        self.triggerLabelMin.setText("Min Current: %.2f mA" % (minCurrent))

        self.triggerLabelMax = QtGui.QLabel(self.dock1)
        self.triggerLabelMax.setText("Max Current: %.2f mA" % (maxCurrent))

        self.triggerLayout = QtGui.QVBoxLayout()
        self.triggerLayout.addWidget(self.triggerLabelMin)
        self.triggerLayout.addWidget(self.triggerLabelMax)
        self.triggerBox.setLayout(self.triggerLayout)

        # Statistics for the area between the selectors
        self.regionBox = QtGui.QGroupBox(self.dock1)
        self.regionBox.setFlat(True)
        self.regionBox.setTitle("Selection Area")

        self.regionLabelMin = QtGui.QLabel(self.dock1)
        self.regionLabelMin.setText("Min Current: %.2f mA" % (minCurrent))

        self.regionLabelMax = QtGui.QLabel(self.dock1)
        self.regionLabelMax.setText("Max Current: %.2f mA" % (maxCurrent))

        self.selectorLayout = QtGui.QVBoxLayout()
        self.selectorLayout.addWidget(self.regionLabelMin)
        self.selectorLayout.addWidget(self.regionLabelMax)
        self.regionBox.setLayout(self.selectorLayout)

        self.statsBox = QtGui.QGroupBox(self.dock1)
        self.vbox = QtGui.QVBoxLayout()
        self.vbox.addWidget(self.wholeWindowBox)
        self.vbox.addWidget(self.triggerBox)
        self.vbox.addWidget(self.regionBox)
        self.vbox.addStretch(1)

        self.statsBox.setLayout(self.vbox)
        self.dock1.setWidget(self.statsBox)

    def showDialog(self):

        fname = QtGui.QFileDialog.getOpenFileName(self, 'Open file', '.')
        
        f = open(fname, 'rb')
        xTime = []
        yCurrent = []
        yTrigger = []
        with f:
          self.reader = csv.reader(f)
          avgcurrent = 0
          avgtriggercurrent = 0
          triggerthreshold = 1
          count = 0
          i = 0
          for row in self.reader:
            xTime.extend([float(row[0])])
            yCurrent.extend([float(row[3])])
            yTrigger.extend([float(row[6])])
            if float(row[6]) >= triggerthreshold:
              avgtriggercurrent += float(row[3])
              i+= 1
          
            
            count+= 1
            avgcurrent+= float(row[3])
          avgtriggercurrent = avgtriggercurrent/i
          avgcurrent = avgcurrent/count
          
          ptrig = float(avgtriggercurrent * 5.1)
          p = float(avgcurrent * 5.1)

          ptrigstring = str(ptrig)
          pstring = str(p)

          self.updateStatistics(3.14, 6.28)

          self.showPlot(xTime,yCurrent,yTrigger)

          self.region = pg.LinearRegionItem()
          self.plot1.addItem(self.region)
          self.region.setRegion([0.1, 0.4])
          self.region.sigRegionChanged.connect(self.regionChanged)

    def regionChanged(self):
      minX, maxX = self.region.getRegion()
      self.regionLabelMin.setText("Region Min: %.3f" % (minX))
      self.regionLabelMax.setText("Region Max: %.3f" % (maxX))

    def showPlot(self,time,current,trigger):
        self.plot1 = self.graphwin.addPlot(title="Plot of current vs time", labels={'left':"Current(mA)", 'bottom':"Time(s)"})
        self.plot1.plot(time, current, pen=(0,255,0))
        self.plot1.plot(time, trigger, pen=(255,0,0))
        


def main():
    
    app = QtGui.QApplication(sys.argv)
    ex = Example()
    #sys.exit(app.exec_())
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
      app.exec_()

if __name__ == '__main__':
    main()








