from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QAction, qApp, QLabel, QLineEdit, QHBoxLayout, QVBoxLayout, QGridLayout, QStackedLayout, QWidget, QToolBox, QGroupBox
from PyQt5.QtGui import QIcon, QPalette, QColor, QPixmap
from PyQt5.QtCore import Qt
import sys, socket
import client

# The menu window which contains:
# - Contains a menu for inputting an IP address and port number
# - A list of recent connections

class Menu(QtWidgets.QMainWindow):

    switch_window = QtCore.pyqtSignal()

    def __init__(self, app):
        QtWidgets.QMainWindow.__init__(self)
        self.setWindowTitle('Editr')
        self.setGeometry(400,400,600,500)
        #self.createGridLayout()

        self.central = QtWidgets.QWidget()
        self.setCentralWidget(self.central)
        self.grid = GridLayout(self.central)

        label = QLabel(self)
        label.setText("IP Address:")
        label.move(50, 50)

        label2 = QLabel(self)
        label2.setText("Port:")
        label2.move(50, 100)

        #labelP = QLabel(self)
        #labelP.setBaseSize(2000,2000)
        #pixmap = QPixmap('crab.png').scaled(50,50)
        #labelP.setPixmap(pixmap)
        #labelP.move(200,200)
        #labelP.hasScaledContents()
        #pixmap.scaled(20050,2550)
        #labelP.raise_()

        self.lineEditIP = QLineEdit('', self)
        self.lineEditIP.move(150, 50)

        self.lineEditPort = QLineEdit('', self)
        self.lineEditPort.move(150, 100)

        connectButton = QPushButton('Connect', self)
        connectButton.move(150, 150)
        connectButton.clicked.connect(self.connectToServer)

        self.menu(app)


    def text(self):
        print("main switch")
        self.switch_window.emit()

    def menu(self, app):
        exitAct = QAction(QIcon('exit.png'), '&Exit', self)
        exitAct.setShortcut('Ctrl+Q')
        exitAct.setStatusTip('Exit application')
        exitAct.triggered.connect(app.quit)

        menubar = self.menuBar()
        filemenu = menubar.addMenu('&File')
        filemenu.addAction(exitAct)


        ##Will be used to add new connections
        menubar.addMenu('&Add')

        menubar.addMenu('&Settings')

        helpmenu = menubar.addMenu('&Help')
        aboutAct = QAction('&About',self)

        feedbackAct = QAction('&Feedback', self)
        helpAct = QAction('&Help',self)

        helpmenu.addAction(aboutAct)
        helpmenu.addAction(feedbackAct)
        helpmenu.addAction(helpAct)

    def connectToServer(self):
        # Get the IP address and port number
        ip = self.lineEditIP.text() # Will need to change this to work
        port = self.lineEditPort.text()
        print("ip = %s, port = %s" % (ip, port))

        # Check if the port number is valid
        if not port.isdigit():
            print("Invalid port number")  # TODO make this an error message that appears in the UI
            return

        # Attempt to connect to the server
        clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            clientSocket.connect((ip, int(port)))
        except socket.error:
            print("Could not connect")
            return

        # If connection successful
        #self.close()  # close this window
        #self.grid.addNew(ip,port)
        window = client.MainWindow(clientSocket)
        window.show()  # open the text editor window
        self.app.exec_()


class GridLayout(QtWidgets.QGroupBox):
    def __init__(self, parent):
        QtWidgets.QWidget.__init__(self,"Recent Connections", parent=parent)
        self.xCur = 0
        self.xMax = 5
        self.yCur = 0
        self.yMax = 5

        self.move(50,200)
        self.setFixedSize(500,200)

        #horizontalGroupBox = QGroupBox("Recent Connections")
        layout = QGridLayout()
        self.layout = layout
        layout.setColumnStretch(1, 4)
        layout.setColumnStretch(2, 4)

        self.setLayout(layout)
        self.addNew("IP 1", "Port 0")

    def addNew(self, ip, port):
        if self.xCur < 5:
            xSet = self.xCur
            self.xCur += 1
        else:
            self.xCur = 0
            self.yCur += 1
            xSet = 0

        if self.yCur < 5:
            self.layout.addWidget(QPushButton(str(ip) + " " + str(port)), xSet, self.yCur)



class Savededitr:

    def __init__(self, name, ip, port):
        self.name = name
        self.ip = ip
        self.port = port

    def displayWindows(self):
        label = QLabel(self)
        label.setText(self.name)
        label.move(50, 50) ##Needs relative location

        #pixmap = QPixmap('crab.png')
        #label.setPixmap(pixmap)


    def windowClicked(self):
        pass


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
    recentList = []
    app.setStyle("Fusion")
    app.setApplicationName("Editr")
    pal = palette()
    app.setPalette(pal)
    window = Menu(app)
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
