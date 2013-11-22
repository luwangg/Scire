from PyQt4 import QtGui, QtCore


class CheckableDirModel(QtGui.QDirModel):
    def __init__(self, parent=None):
        QtGui.QDirModel.__init__(self, None)
        self.checks = {}

    def data(self, index, role=QtCore.Qt.DisplayRole):
        if role != QtCore.Qt.CheckStateRole:
            return QtGui.QDirModel.data(self, index, role)
        else:
            if index.column() == 0:
                return self.checkState(index)

    def flags(self, index):
        return QtGui.QDirModel.flags(self, index) | QtCore.Qt.ItemIsUserCheckable

    def checkState(self, index):
        if index in self.checks:
            return self.checks[index]
        else:
            return QtCore.Qt.Unchecked

    def setData(self, index, value, role):
        if (role == QtCore.Qt.CheckStateRole and index.column() == 0):
            self.checks[index] = value
            for i in range(self.rowCount(index)):
                self.setData(index.child(i,0),value,role)
            return True 

        return QtGui.QDirModel.setData(self, index, value, role)

    def exportChecked(self, acceptedSuffix=['jpg', 'png', 'bmp']):
        selection=[]
        for c in self.checks.keys():
            if self.checks[c]==QtCore.Qt.Checked and self.fileInfo(c).completeSuffix().toLower() in acceptedSuffix:
                try:

                    selection.append(self.filePath(c).toUtf8())
                except:
                    pass
        return selection   

if __name__ == '__main__':
    import sys

    app = QtGui.QApplication(sys.argv)

    model = QtGui.QDirModel()
    tree = QtGui.QTreeView()
    tree.setModel(CheckableDirModel())

    tree.setAnimated(False)
    tree.setIndentation(20)
    tree.setSortingEnabled(True)

    tree.setWindowTitle("Dir View")
    tree.resize(640, 480)
    tree.show()

    sys.exit(app.exec_())  
