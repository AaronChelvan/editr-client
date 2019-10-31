from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QAction, qApp, QLabel, QLineEdit, QHBoxLayout, QVBoxLayout, QGridLayout, QStackedLayout, QWidget, QToolBox
from PyQt5.QtGui import QIcon, QPalette, QColor
from PyQt5.QtCore import Qt
import sys, socket

# The menu window which contains:
# - Contains a menu for inputting an IP address and port number
# - A list of recent connections

class serverMenu(QtWidgets.QMainWindow):
    connectSuccessful = QtCore.pyqtSignal(object)

    def __init__(self):
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

        #self.fileName = QLineEdit('', self)
        #self.fileName.move(150, 150)

        connectButton = QPushButton('Connect', self)
        connectButton.move(150, 200)
        connectButton.clicked.connect(self.connectToServer)


    def connectToServer(self):
        # Get the IP address and port number
        ip = self.lineEditIP.text()
        port = self.lineEditPort.text()
        print("ip = %s, port = %s"% (ip, port))

        # Check if the port number is valid
        if not port.isdigit():
            print("Invalid port number") # TODO make this an error message that appears in the UI
            return
        
        # Attempt to connect to the server
        clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            clientSocket.connect((ip, int(port)))
        except socket.error:
            print("Could not connect")
            return

        # Switch to the text editor window
        self.connectSuccessful.emit(clientSocket)

