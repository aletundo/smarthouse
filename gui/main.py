from PyQt4 import QtGui, QtCore, uic

import sys
import untitled_widget2

class smarthouse_app(QtGui.QMainWindow, untitled_widget2.Ui_MainWindow):

    # GUI initialization
    def __init__(self, parent=None):

        super(smarthouse_app, self).__init__(parent)
        self.setupUi(self)
        self.setWindowTitle('Smarthouse HMM')
        self.stackedWidget.setCurrentIndex(0)
        self.tabWidget.currentChanged.connect(self.switch_widget)

    def switch_widget(self):
        currentIndex = self.stackedWidget.currentIndex()
        newIndex = 0 if currentIndex == 1 else 1
        print(currentIndex,newIndex)
        self.stackedWidget.setCurrentIndex(newIndex)


def main():
    app = QtGui.QApplication(sys.argv)
    form = smarthouse_app()
    form.show()
    app.exec_()

if __name__ == '__main__':
    main()
