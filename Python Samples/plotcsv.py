from pyqtgraph.Qt import QtGui, QtCore
import numpy as np
import pyqtgraph as pg
import csv

app = QtGui.QApplication([])

win = pg.GraphicsWindow(title="Current Sense Analysis")
win.resize(1000,600)
win.setWindowTitle('setWindowTitle')

xTime = []
yCurrent = []
yTrigger = []

with open('data.csv', 'rb') as f:
  reader = csv.reader(f)
  for row in reader:
    xTime.extend([float(row[0])])
    yCurrent.extend([float(row[1])])
    yTrigger.extend([float(row[2])])


p1 = win.addPlot(title="Main plot")

p1.plot(xTime, yCurrent, pen=(0,255,0))
p1.plot(xTime, yTrigger, pen=(255,0,0))

if __name__ == '__main__':
  import sys
  if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
    QtGui.QApplication.instance().exec_()
