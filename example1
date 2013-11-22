import sys
from PyQt4 import QtGui, QtCore, QtNetwork, uic

class MainWindow(QtGui.QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        uic.loadUi('gui.ui', self)            
        self.connect(self.multiPackerAddDirsBtn,
                     QtCore.SIGNAL('clicked()'), self.multiPackerAddDirs)

    def multiPackerAddDirs(self):
        dialog = QtGui.QFileDialog(self)
        dialog.setFileMode(QtGui.QFileDialog.Directory)
        dialog.setOption(QtGui.QFileDialog.ShowDirsOnly, True)
        dialogTreeView = dialog.findChild(QtGui.QTreeView)
        dialogTreeView.setSelectionMode(
            QtGui.QAbstractItemView.ExtendedSelection)
        if dialog.exec_():
            for dirname in dialog.selectedFiles():
                self.multiPackerDirList.addItem(str(dirname))
                print(str(dirname))

if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.exec_()
