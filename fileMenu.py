from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QAction, qApp, QLabel, QLineEdit, QHBoxLayout, QVBoxLayout, QGridLayout, QStackedLayout, QWidget, QToolBox, QComboBox
from PyQt5.QtGui import QIcon, QPalette, QColor
from PyQt5.QtCore import Qt
from lib import *

class fileMenuWindow(QtWidgets.QMainWindow):
	startEditing = QtCore.pyqtSignal(object, str) 
	closeConnection = QtCore.pyqtSignal()

	def __init__(self, clientSocket):
		QMainWindow.__init__(self)
		self.setWindowTitle('Editr')
		self.setGeometry(400,400,600,500)
		self.clientSocket = clientSocket

		# Label for the drop-down menu
		fileNameLabel = QLabel()
		fileNameLabel.setText("File name:")
		fileNameLabel.setFixedSize(100, 50)

		# Drop-down menu for selecting a file
		self.comboBox = QComboBox()
		# TODO - add the list of files from the server to the combox box
		exampleFiles = ["file1", "file2", "file3"]
		for f in exampleFiles:
			self.comboBox.addItem(f) 

		# Button for opening a file
		openFileButton = QPushButton('Open File')
		openFileButton.clicked.connect(self.openFileHandler) 
		openFileButton.setFixedSize(100, 50)

		# Text field for entering the name of a file to create
		self.lineEditFileName = QLineEdit()
		self.lineEditFileName.setFixedSize(200, 30)
		
		# Button for creating a file
		createFileButton = QPushButton('Create File')
		createFileButton.clicked.connect(self.createFileHandler) 
		createFileButton.setFixedSize(100, 50)
		
		# Button for closing connection to the server
		closeButton = QPushButton('Close Connection')
		closeButton.clicked.connect(self.closeConnectionHandler)
		closeButton.setFixedSize(150, 50)

		# Layout configuration
		layout = QGridLayout()
		layout.addWidget(fileNameLabel, 0, 0)
		layout.addWidget(self.comboBox, 0, 1)
		layout.addWidget(openFileButton, 1, 0)
		layout.addWidget(self.lineEditFileName, 2, 0)
		layout.addWidget(createFileButton, 2, 1)
		layout.addWidget(closeButton, 3, 0)
		q = QWidget()
		q.setLayout(layout)
		self.setCentralWidget(q)

	def openFileHandler(self):
		fileName = self.comboBox.currentText()
		self.startEditing.emit(self.clientSocket, fileName)

	def createFileHandler(self):
		fileName = self.lineEditFileName.text()
		sendMessage(self.clientSocket, "create", fileName)
		print("created " + fileName)

	def closeConnectionHandler(self):     
		self.clientSocket.close()
		self.closeConnection.emit()