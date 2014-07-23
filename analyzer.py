#!/usr/bin/python

import sys
import os
import pyqtgraph as pg
from pyqtgraph.Qt import QtGui, QtCore
import numpy as np
import csv

class StatsObject(object):
  def __init__(self):
    self.energy = 0
    self.duration = 0
    self.powerAverage = 0
    self.powerStddev = 0
    self.powerMin = 0
    self.powerMax = 0
    self.currentAverage = 0
    self.currentStddev = 0
    self.currentMin = 0
    self.currentMax = 0

class Analysis(QtGui.QMainWindow):

  def __init__(self):
    super(Analysis, self).__init__()
    self.initUI()

  def initUI(self):
    """Setup the main UI, status bar, and keyboard shortcuts"""
    self.setGeometry(300, 300, 1200, 800)

    # Initialize the plotting window
    self.graphwin = pg.GraphicsWindow(title="Current Sense Analysis")
    self.graphwin.setWindowTitle('Current vs time')
    self.setCentralWidget(self.graphwin)

    # Add button and shortcut to open files
    openFile = QtGui.QAction(QtGui.QIcon('open.png'), 'Open File', self)
    openFile.setShortcut('Ctrl+O')
    openFile.setStatusTip('Open new File')
    openFile.triggered.connect(self.openFile)

    # Add button and shortcut to open folders
    openFolder = QtGui.QAction(QtGui.QIcon('open.png'), 'Open Folder', self)
    openFolder.setStatusTip('Open Folder')
    openFolder.triggered.connect(self.openFolder)

    # Add button and shortcut to export plots
    exportPlot = QtGui.QAction(QtGui.QIcon('exit24.png'), 'Export', self)
    exportPlot.setShortcut('Ctrl+P')
    exportPlot.setStatusTip('Export Plot')
    exportPlot.triggered.connect(self.exportPlot)

    # Add button and shortcut to quit the program
    exitAction = QtGui.QAction(QtGui.QIcon('exit24.png'), 'Exit', self)
    exitAction.setShortcut('Ctrl+Q')
    exitAction.setStatusTip('Exit application')
    exitAction.triggered.connect(self.close)

    # Add button and shortcut to quit the program
    exportTableAction = QtGui.QAction(QtGui.QIcon('exit24.png'), 'Export Table', self)
    exportTableAction.setShortcut('Ctrl+E')
    exportTableAction.setStatusTip('Export Table as CSV')
    exportTableAction.triggered.connect(self.exportCSV)

    # Create a status bar
    self.statusBar()

    # Create a menu bar
    menubar = self.menuBar()

    # Create File menu
    menuFile = menubar.addMenu('File')
    menuFile.addAction(openFile)
    menuFile.addAction(openFolder)
    menuFile.addAction(exitAction)

    # Create the Export menu
    menuExport = menubar.addMenu('Export')
    menuExport.addAction(exportPlot)
    menuExport.addAction(exportTableAction)

    self.setWindowTitle('Data Analysis')
    self.layoutStatistics()
    self.show()

  def layoutFolderSidebar(self):
    """Initalize the sidebar layout"""
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
    """Prompt for and then display the contents of a file"""
    fullPath = QtGui.QFileDialog.getOpenFileName(self, 'Open file', '.')
    self.plotFile(fullPath)
    self.setRegionStats()
    fname = fullPath.split("/")[-1]
    self.plot1.setTitle(fname)

  def showSelectedFile(self):
    fname = self.list.currentItem().text()
    fullPath = "%s%s" %(self.folder_path, fname)
    self.plotFile(fullPath)
    self.setRegionStats()
    self.plot1.setTitle(fname)

  def plotFile(self, fullPath):
    time, current, trigger = self.readFile(fullPath)

    stats = self.calculateStats(time, current)
    self.setFileStats(stats)

    stats = self.calculateTriggerStats(time, current, trigger)
    self.setTriggerStats(stats)

    self.showPlot(time, current, trigger)
    self.highlightTriggerRegions(time, trigger)

  def openFolder(self):
    # Prompt for a folder
    folder = QtGui.QFileDialog(self, "Open Folder", ".")
    folder.setFileMode(QtGui.QFileDialog.Directory)
    folder.setOption(QtGui.QFileDialog.ShowDirsOnly, True)

    if folder.exec_():
      for folderPath in folder.selectedFiles():
        self.folder_path = "%s/" % (folderPath)

    # Ensure sidebar exists
    if not hasattr(self, 'fileDock'):
      self.layoutFolderSidebar()
      self.layoutStatsTable()

    dirs = os.listdir(self.folder_path)
    self.list.clear()
    for file in dirs:
      if os.path.isfile(os.path.join(self.folder_path,file)):
        self.list.addItem(file)

    self.list.sortItems()
    self.fileStats = np.zeros([int(self.list.count()), 3])

    self.fileDock.updateGeometry()
    self.populateStatsTable()

  def calculateTriggerStats(self, time, current, trigger):
    triggerThreshold = 1.0
    triggerCurrent = []

    for index, triggerValue in enumerate(trigger):
      if triggerValue >= triggerThreshold:
        triggerCurrent.extend([current[index]])

    stats = self.calculateStats(time, triggerCurrent)
    stats.duration = self.deltaT * len(triggerCurrent) * 1000
    return stats

  def exportPlot(self):
    """Display a prompt for a path and filename, then export the current plot as an image"""
    # create an exporter instance, as an argument give it
    # the item you wish to export
    exporter = pg.exporters.ImageExporter.ImageExporter(self.plot1)

    # set export parameters if needed
    exporter.parameters()['width'] = 100

    # save to file
    fullPath = QtGui.QFileDialog.getSaveFileName(self, 'Export Plot', '.')

    exporter.export

  def calculateStats(self, time, current):
    stats = StatsObject()

    if not len(time) == 0:
      stats.duration = (time[len(time)-1] - time[0]) * 1000

      stats.currentAverage = np.average(current)
      stats.currentStddev = np.std(current)
      stats.currentMax = np.max(current)
      stats.currentMin = np.min(current)

      # Assumes 5.1 VDC constant voltage source (USB)
      voltage = 5.1
      power = [x * voltage for x in current]

      stats.powerAverage = np.average(power)
      stats.powerStddev = np.std(power)
      stats.powerMax = np.max(power)
      stats.powerMin = np.min(power)

      energy = [p * self.deltaT for p in power]

      stats.energy = np.sum(energy)

    return stats

  # Highlights the last trigger region
  ## Assumes active high trigger, only highlights the final trigger region
  def highlightTriggerRegions(self, time, trigger):
    triggerThreshold = 1.0
    minX = 0

    for index, triggerValue in enumerate(trigger):
      if triggerValue >= triggerThreshold and minX == 0:
        minX = time[index]

      elif triggerValue < triggerThreshold and minX != 0:
        # Create region highlight or reuse if it already exists
        if not hasattr(self, "regionT"):
          self.regionT = pg.LinearRegionItem([minX, time[index-1]], movable=False, brush=pg.mkColor("FF363628"))

        else:
          self.regionT.setRegion([minX, time[index-1]])

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

    self.fileLabelDuration = QtGui.QLabel(self.statsDock)
    self.fileLabelEnergy = QtGui.QLabel(self.statsDock)
    self.fileLabelAvgPower = QtGui.QLabel(self.statsDock)

    self.wholeLayout = QtGui.QVBoxLayout()
    self.wholeLayout.addWidget(self.fileLabelDuration)
    self.wholeLayout.addWidget(self.fileLabelEnergy)
    self.wholeLayout.addWidget(self.fileLabelAvgPower)
    self.wholeWindowBox.setLayout(self.wholeLayout)

    # Statistics for just the area under the trigger
    self.triggerBox = QtGui.QGroupBox(self.statsDock)
    self.triggerBox.setFlat(True)
    self.triggerBox.setTitle("Trigger Area(s)")

    self.triggerLabelDuration = QtGui.QLabel(self.statsDock)
    self.triggerLabelEnergy = QtGui.QLabel(self.statsDock)
    self.triggerLabelAvgPower = QtGui.QLabel(self.statsDock)


    self.triggerLayout = QtGui.QVBoxLayout()
    self.triggerLayout.addWidget(self.triggerLabelDuration)
    self.triggerLayout.addWidget(self.triggerLabelEnergy)
    self.triggerLayout.addWidget(self.triggerLabelAvgPower)
    self.triggerBox.setLayout(self.triggerLayout)

    # Statistics for the area between the selectors
    self.regionBox = QtGui.QGroupBox(self.statsDock)
    self.regionBox.setFlat(True)
    self.regionBox.setTitle("Selection Area")

    self.regionLabelDuration = QtGui.QLabel(self.statsDock)
    self.regionLabelEnergy = QtGui.QLabel(self.statsDock)
    self.regionLabelAvgPower = QtGui.QLabel(self.statsDock)

    self.setFileStats(StatsObject())
    self.setTriggerStats(StatsObject())

    self.selectorLayout = QtGui.QVBoxLayout()
    self.selectorLayout.addWidget(self.regionLabelDuration)
    self.selectorLayout.addWidget(self.regionLabelEnergy)
    self.selectorLayout.addWidget(self.regionLabelAvgPower)
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

    self.tableDock.setWidget(self.table)

  def populateStatsTable(self):
    headers = ["Total Energy (mJ)", "Trigger Energy", "Duration (mS)", "Trigger Duration", "Average Current (mA)",
          "Max Current", "Min Current", "Average Power (mW)", "Max Power", "Min Power"]
    self.table.setColumnCount(len(headers))
    self.table.setHorizontalHeaderLabels(headers)
    self.table.resizeColumnsToContents()

    self.table.setRowCount(self.list.count())

    fileNames = []
    for index in xrange(self.list.count()):
      fileNames.append(self.list.item(index))
    files = [i.text() for i in fileNames]

    self.table.setVerticalHeaderLabels(files)

    for index, fileName in enumerate(files):
      selectedFilePath = "%s%s" % (self.folder_path, fileName)

      time, current, trigger = self.readFile(selectedFilePath)
      stats = self.calculateStats(time, current)
      triggerStats = self.calculateTriggerStats(time, current, trigger)

      self.table.setItem(index, 0, QtGui.QTableWidgetItem("%.3f" % stats.energy))
      self.table.setItem(index, 1, QtGui.QTableWidgetItem("%.3f" % triggerStats.energy))
      self.table.setItem(index, 2, QtGui.QTableWidgetItem("%.3f" % stats.duration))
      self.table.setItem(index, 3, QtGui.QTableWidgetItem("%.3f" % triggerStats.duration))
      self.table.setItem(index, 4, QtGui.QTableWidgetItem("%.3f" % stats.currentAverage))
      self.table.setItem(index, 5, QtGui.QTableWidgetItem("%.3f" % stats.currentMax))
      self.table.setItem(index, 6, QtGui.QTableWidgetItem("%.3f" % stats.currentMin))
      self.table.setItem(index, 7, QtGui.QTableWidgetItem("%.3f" % stats.powerAverage))
      self.table.setItem(index, 8, QtGui.QTableWidgetItem("%.3f" % stats.powerMax))
      self.table.setItem(index, 9, QtGui.QTableWidgetItem("%.3f" % stats.powerMin))

    self.table.updateGeometry()
    self.table.verticalHeader().sectionDoubleClicked.connect(self.showFileFromTable)

  def showFileFromTable(self, index):
    fname = self.table.verticalHeaderItem(index).text()
    fullPath = "%s%s" %(self.folder_path, fname)
    self.plotFile(fullPath)
    self.plot1.setTitle(fname)

  def readFile(self, fname):
    f = open(fname, 'rb')
    time = []
    current = []
    trigger = []
    with f:
     self.reader = csv.reader(f)

     for row in self.reader:
      time.extend([float(row[0])])
      current.extend([float(row[1])])
      trigger.extend([float(row[2])])

    self.deltaT = time[1]

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


    stats = self.calculateStats(self.plotDataX[rMinIndex:rMaxIndex], self.plotDataY[rMinIndex:rMaxIndex])

    self.regionLabelEnergy.setText("Energy: %.3f mJ" % stats.energy)
    self.regionLabelAvgPower.setText("Average Power: %.3f mA" % stats.powerAverage)
    self.regionLabelDuration.setText("Duration: %.3f mS" % stats.duration)

  # Set statistics for the entire file
  def setFileStats(self, stats):
    self.fileLabelEnergy.setText("Energy: %.3f mA" % stats.energy)
    self.fileLabelAvgPower.setText("Average Power: %.3f mA" % stats.powerAverage)
    self.fileLabelDuration.setText("Duration: %.3f mS" % stats.duration)

  # Set statistics for the area(s) under the trigger signal
  def setTriggerStats(self, stats):
    self.triggerLabelEnergy.setText("Energy: %.3f mJ" % stats.energy)
    self.triggerLabelAvgPower.setText("Average Power: %.3f mA" % stats.powerAverage)
    self.triggerLabelDuration.setText("Duration: %.3f mS" % stats.duration)

  def showPlot(self, time, current, trigger):
    self.plotDataX = time
    self.plotDataY = current

    if not hasattr(self, 'plot1'):
     self.plot1 = self.graphwin.addPlot(title="Plot of current vs time", labels={'left':"Current(mA)", 'bottom':"Time(s)"})

    self.plot1.clear()
    self.plot1.plot(time, current, pen=(0,255,0))
    # self.plot1.plot(time, trigger, pen=(255,0,0))
    self.plot1.enableAutoRange(enable=True)

    self.region = pg.LinearRegionItem()
    self.plot1.addItem(self.region)
    self.region.setBounds([time[0], time[len(time)-1]])
    self.region.setRegion([time[0], time[15]])
    self.region.sigRegionChanged.connect(self.setRegionStats)
    self.setRegionStats()

    self.plot1.showGrid(y=True)


  def keyPressEvent(self, event):
    if event.key() == QtCore.Qt.Key_Enter or event.key() == QtCore.Qt.Key_Return:
      self.showSelectedFile()

  def exportCSV(self):
   fullPath = QtGui.QFileDialog.getSaveFileName(self, 'Export CSV', '.')
   outFile = open(fullPath, 'w')

   line = ","
   for column in range(self.table.columnCount()):
    line += str(self.table.horizontalHeaderItem(column).text()) + ","
   line = line[:-1]+"\n"
   outFile.write(line)

   for row in range(self.table.rowCount()):
    line = "%s," % str(self.table.verticalHeaderItem(row).text())
    for column in range(self.table.columnCount()):
     line += str(self.table.item(row, column).text()) + ","
    line = line[:-1]+"\n"
    outFile.write(line)
   outFile.close()

def main():
  app = QtGui.QApplication(sys.argv)
  ex = Analysis()

  #sys.exit(app.exec_())
  if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
    app.exec_()
    app.deleteLater()
    app.exit()

if __name__ == '__main__':
  main()
