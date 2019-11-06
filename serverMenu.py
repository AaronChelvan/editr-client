from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QAction, qApp, QLabel, QLineEdit, QHBoxLayout, QVBoxLayout, QGridLayout, QStackedLayout, QWidget, QToolBox, QGroupBox
from PyQt5.QtGui import QIcon, QPalette, QColor
from PyQt5.QtCore import Qt
from functools import partial
import sys, socket

# The menu window which contains:
# - Contains a menu for inputting an IP address and port number
# - A list of recent connections

class serverMenuWindow(QtWidgets.QMainWindow):
    connectSuccessful = QtCore.pyqtSignal(object)

    def __init__(self):
        QtWidgets.QMainWindow.__init__(self)
        self.setWindowTitle('Editr')
        self.setFixedSize(450,400)
        self.setGeometry(600, 350, 600, 500)
        self.menu()

        #self.central = QtWidgets.QWidget()
        #self.setCentralWidget(self.central)

        central = QWidget()
        self.setCentralWidget(central)

        self.grid = GridLayout(central,self.emitObject)

        self.errorMessages = []
        self.errorMessages.append("Invalid Port") #0
        self.errorMessages.append("Connection Failed") #1

        label = QLabel()
        label.setText("IP Address:")
        #label.move(50, 50)
        label.setFixedSize(60,50)

        label2 = QLabel()
        label2.setText("Port:")
        #label2.move(50, 100)
        label2.setFixedSize(40,50)


        self.lineEditIP = QLineEdit('')
        #self.lineEditIP.move(150, 50)
        self.lineEditIP.setFixedSize(100,50)

        self.lineEditPort = QLineEdit('')
        #self.lineEditPort.move(150, 100)
        self.lineEditPort.setFixedSize(100,50)

        connectButton = QPushButton('Connect')
        #connectButton.move(200, 150)
        connectButton.clicked.connect(self.connectToServer)
        connectButton.setFixedSize(120,40)

        #connectionLayout = QHBoxLayout()
        connectionLayout = QGridLayout()
        connectionLayout.addWidget(label,0,0)
        connectionLayout.addWidget(label2,1,0)
        connectionLayout.addWidget(self.lineEditIP,0,1)
        connectionLayout.addWidget(self.lineEditPort,1,1)
        connectionLayout.addWidget(connectButton,1,2)
        connectionBox = QGroupBox()
        connectionBox.setLayout(connectionLayout)
        connectionBox.setTitle("Server Connection")

        totalLayout = QVBoxLayout()
        totalLayout.addWidget(connectionBox)
        totalLayout.addWidget(self.grid)

        #central = QWidget()
        central.setLayout(totalLayout)
        #self.setCentralWidget(central)


    def emitObject(self,object):
        self.connectSuccessful.emit(object)

    def text(self):
        print("main switch")
        self.switch_window.emit()

    def menu(self):
        exitAct = QAction(QIcon('exit.png'), '&Exit', self)
        exitAct.setShortcut('Ctrl+Q')
        exitAct.setStatusTip('Exit application')
        exitAct.triggered.connect(qApp.quit)

        menubar = self.menuBar()
        filemenu = menubar.addMenu('&File')
        filemenu.addAction(exitAct)

        ##Will be used to add new connections
        menubar.addMenu('&Add')

        menubar.addMenu('&Settings')

        helpmenu = menubar.addMenu('&Help')
        aboutAct = QAction('&About', self)

        feedbackAct = QAction('&Feedback', self)
        helpAct = QAction('&Help', self)

        helpmenu.addAction(aboutAct)
        helpmenu.addAction(feedbackAct)
        helpmenu.addAction(helpAct)


    def newRecent(self, ip, port):
        check = False
        for object in self.grid.returnList():
            ipTest = object.ipAddress()
            portTest = object.portReturn()
            if str(ip) == ipTest and str(port) == portTest:
                check = True
                break
            else:
                continue

        if not check:
            self.grid.addNew(ip, port)
            with open("recents.txt", "a+") as f:
                f.write(str(ip) + ":" + str(port) + "\n")


    def connectToServer(self):
        # Get the IP address and port number
        ip = self.lineEditIP.text()
        port = self.lineEditPort.text()
        print("ip = %s, port = %s"% (ip, port))

        # Check if the port number is valid
        if not port.isdigit():
            self.connectionError(0)
            print("Invalid port number") # TODO make this an error message that appears in the UI
            return
        
        # Attempt to connect to the server
        clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            clientSocket.connect((ip, int(port)))
        except socket.error:
            print("Could not connect")
            self.connectionError(1)
            return

        # Switch to the text editor window
        self.newRecent(ip, port)
        self.connectSuccessful.emit(clientSocket)

    def connectionError(self, errorNum):
        self.error = notificationWindow(self.errorMessages[errorNum])
        self.error.setGeometry(600,550,100,100)
        self.error.show()

class notificationWindow(QWidget):
    def __init__(self,name):
        super().__init__()

        self.name = name
        self.initUI()

    def initUI(self):
        notwindow = QLabel(self.name,self)



class GridLayout(QtWidgets.QGroupBox):
    def __init__(self, parent,win):
        QtWidgets.QWidget.__init__(self,"Recent Connections", parent=parent)
        self.recentList = []
        self.xCur = 0
        self.xMax = 5
        self.yCur = 0
        self.yMax = 5
        self.win = win

        self.move(50,200)
        #self.setFixedSize(500,200)

        layout = QGridLayout()
        self.layout = layout
        self.layout.setColumnStretch(1, 1)
        self.layout.setRowStretch(2, 4)

        self.setLayout(self.layout)

        try:

            with open('recents.txt') as content_file:
                content = content_file.read()
                lines = content.splitlines()
                size = len(lines)
                #if size > 1:

                for i in range(0,size):
                    print(lines[i])
                    split = lines[i].split(":")
                    ip = split[0]
                    port = split[1]
                    self.addNew(ip,port)
                    self.recentList.append
        except FileNotFoundError:
            pass


    def addNew(self, ip, port):
        if self.yCur < 4:
            ySet = self.yCur
            self.yCur += 1
        else:
            self.yCur = 0
            self.xCur += 1
            ySet = 0

        if self.xCur < 5:
            push = QPushButton(str(ip) + ":" + str(port))
            #push.setFixedSize(50,30)
            self.layout.addWidget(push, self.xCur, ySet)
            new = Savedrecent(str(ip), str(port), self.win)
            push.clicked.connect(new.connectToServer)
            self.recentList.append(new)

    def returnList(self):
        return self.recentList


class Savedrecent:
    connectSuccessful = QtCore.pyqtSignal(object)

    def __init__(self, ip, port,win):
        self.ip = ip
        self.port = port
        self.win = win

    def ipAddress(self):
        return self.ip

    def portReturn(self):
        return self.port

    def connectToServer(self):
        # Get the IP address and port number
        ip = self.ip
        port = self.port
        print("ip = %s, port = %s" % (ip, port))

        # Check if the port number is valid
        if not port.isdigit():
            print("Invalid port number")
            return

        # Attempt to connect to the server
        clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            clientSocket.connect((ip, int(port)))
        except socket.error:
            self.connectionError()
            print("Could not connect")
            return

        self.win(clientSocket)
        # Switch to the text editor window
        #self.newRecent(ip, port)
        #self.connectSuccessful.emit(clientSocket)
    def connectionError(self):
        self.error = notificationWindow("Connection Failed")
        self.error.setGeometry(600,550,100,100)
        self.error.show()

