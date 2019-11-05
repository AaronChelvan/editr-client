from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QAction, qApp, QLabel, QLineEdit, QHBoxLayout, QVBoxLayout, QGridLayout, QStackedLayout, QWidget, QToolBox, QComboBox, QGroupBox, QMessageBox
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

		# Button for renaming a file
		renameFileButton = QPushButton('Rename File')
		renameFileButton.clicked.connect(self.renameFileHandler)
		renameFileButton.setFixedSize(100, 50)

		# Button for deleting a file
		deleteFileButton = QPushButton('Delete File')
		deleteFileButton.clicked.connect(self.deleteFileHandler)
		deleteFileButton.setFixedSize(100, 50)
		
		# Button for closing connection to the server
		closeButton = QPushButton('Close Connection')
		closeButton.clicked.connect(self.closeConnectionHandler)
		closeButton.setFixedSize(150, 50)

		# Layout configuration
		fileSelectLayout = QHBoxLayout()
		fileSelectLayout.addWidget(self.comboBox)
		fileSelectLayout.addWidget(openFileButton)
		fileSelectLayout.addWidget(renameFileButton)
		fileSelectLayout.addWidget(deleteFileButton)
		fileSelectGroupBox = QGroupBox()
		fileSelectGroupBox.setLayout(fileSelectLayout)
		fileSelectGroupBox.setTitle("Select a file")

		createFileLayout = QHBoxLayout()
		createFileLayout.addWidget(self.lineEditFileName)
		createFileLayout.addWidget(createFileButton)
		createFileGroupBox = QGroupBox()
		createFileGroupBox.setLayout(createFileLayout)
		createFileGroupBox.setTitle("Create a file")

		overallLayout = QVBoxLayout()
		overallLayout.addWidget(fileSelectGroupBox)
		overallLayout.addWidget(createFileGroupBox)
		overallLayout.addWidget(closeButton)

		q = QWidget()
		q.setLayout(overallLayout)
		self.setCentralWidget(q)

	def openFileHandler(self):
		fileName = self.comboBox.currentText()
		self.startEditing.emit(self.clientSocket, fileName)

	def createFileHandler(self):
		fileName = self.lineEditFileName.text()
		response = sendMessage(self.clientSocket, "create", fileName)
		if "Err" in response["CreateResp"]:
			print("file already exists")
			errorMessage = QMessageBox()
			errorMessage.setIcon(QMessageBox.Warning)
			errorMessage.setText("\"%s\" already exists" % fileName)
			errorMessage.setWindowTitle("Error")
			errorMessage.exec_()
		else:
			print("created " + fileName)
			successMessage = QMessageBox()
			successMessage.setText("\"%s\" created" % fileName)
			successMessage.setWindowTitle("Success")
			successMessage.exec_()

	def renameFileHandler(self):
		print("clicked rename button")

	def deleteFileHandler(self):
		print("clicked delete button")
	
	def closeConnectionHandler(self):     
		self.clientSocket.close()
		self.closeConnection.emit()