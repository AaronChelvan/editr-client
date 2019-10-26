from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QAction, qApp, QLabel, QLineEdit, QHBoxLayout, QVBoxLayout, QGridLayout, QStackedLayout, QWidget, QToolBox
from PyQt5.QtGui import QIcon, QPalette, QColor
from PyQt5.QtCore import Qt
import sys
import client

# The menu window which contains:
# - Contains a menu for inputting an IP address and port number
# - A list of recent connections

class Menu(QtWidgets.QMainWindow):
    switch_window = QtCore.pyqtSignal()

    def __init__(self,app):
        QMainWindow.__init__(self)
        self.setWindowTitle('Editr')
        self.setGeometry(400,400,600,500)

        label = QLabel(self)
        label.setText("IP Address:")
        label.move(50, 50)

        label2 = QLabel(self)
        label2.setText("Port:")
        label2.move(50, 100)

        recents = QLabel(self)
        recents.setText("Put recent connections here")
        recents.setGeometry(300,50,200,20)

        self.lineEditIP = QLineEdit('', self)
        self.lineEditIP.move(150, 50)

        self.lineEditPort = QLineEdit('', self)
        self.lineEditPort.move(150, 100)

        connectButton = QPushButton('Connect', self)
        connectButton.move(150, 150)
        connectButton.clicked.connect(self.connectToServer)

        exitAct = QAction(QIcon('exit.png'), '&Exit', self)
        exitAct.setShortcut('Ctrl+Q')
        exitAct.setStatusTip('Exit application')
        exitAct.triggered.connect(app.quit)

        menubar = self.menuBar()
        fileMenu = menubar.addMenu('&File')
        fileMenu.addAction(exitAct)

    def connectToServer(self):
        # Get the IP address and port number
        ip = self.lineEditIP.text()
        port = self.lineEditPort.text()
        print("ip = %s, port = %s"% (ip, port))

        self.switch_window.emit()

class Controller:
    def __init__(self,app):
        self.app = app
        pass

    def show_menu(self):
        self.window = Menu(self.app)
        self.window.switch_window.connect(self.show_text)
        self.window.show()

    def show_text(self):
        self.window = client.MainWindow()
        self.window.show()
        self.app.exec_()

# The colour scheme
def palette():
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(53, 53, 53))
    palette.setColor(QPalette.WindowText, Qt.white)
    palette.setColor(QPalette.Base, QColor(25, 25, 25))
    palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
    palette.setColor(QPalette.Text, Qt.white)
    palette.setColor(QPalette.Button, QColor(53, 53, 53))
    palette.setColor(QPalette.ButtonText, Qt.white)
    palette.setColor(QPalette.BrightText, Qt.red)
    return palette

def main():
    app = QtWidgets.QApplication(sys.argv)
    app.setStyle("Fusion")
    app.setApplicationName("Editr")
    pal = palette()
    app.setPalette(pal)
    controller = Controller(app)
    controller.show_menu()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
