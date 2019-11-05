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

		# Button for opening a file
		self.openFileButton = QPushButton('Open File')
		self.openFileButton.clicked.connect(self.openFileHandler) 
		self.openFileButton.setFixedSize(100, 50)

		# Button for renaming a file
		self.renameFileButton = QPushButton('Rename File')
		self.renameFileButton.clicked.connect(self.renameFileHandler)
		self.renameFileButton.setFixedSize(100, 50)

		# Button for deleting a file
		self.deleteFileButton = QPushButton('Delete File')
		self.deleteFileButton.clicked.connect(self.deleteFileHandler)
		self.deleteFileButton.setFixedSize(100, 50)
		
		# Drop-down menu for selecting a file
		self.comboBox = QComboBox()
		self.comboBox.view().setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
		self.updateFileList()
		
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
		fileSelectLayout = QHBoxLayout()
		fileSelectLayout.addWidget(self.comboBox)
		fileSelectLayout.addWidget(self.openFileButton)
		fileSelectLayout.addWidget(self.renameFileButton)
		fileSelectLayout.addWidget(self.deleteFileButton)
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
		self.updateFileList()

	def renameFileHandler(self):
		print("clicked rename button")
		self.updateFileList()

	def deleteFileHandler(self):
		print("clicked delete button")
		self.updateFileList()
	
	# Updates the list of files displayed in the drop-down menu
	def updateFileList(self):
		# Retrieve the list of files from the server
		response = sendMessage(self.clientSocket, "getFiles")
		listFiles = sorted(response["FilesListResp"]["Ok"])
		
		# Add the files to the drop-down menu
		self.comboBox.clear()
		for file in listFiles:
			self.comboBox.addItem(file)

		# If there are no files, disable the "open", "rename", and "delete" buttons
		if len(listFiles) == 0:
			self.openFileButton.setEnabled(False)
			self.renameFileButton.setEnabled(False)
			self.deleteFileButton.setEnabled(False)
		else: # Otherwise, enable all of the buttons
			self.openFileButton.setEnabled(True)
			self.renameFileButton.setEnabled(True)
			self.deleteFileButton.setEnabled(True)

	def closeConnectionHandler(self):     
		self.clientSocket.close()
		self.closeConnection.emit()