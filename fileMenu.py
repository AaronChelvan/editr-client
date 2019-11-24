from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QAction, qApp, QLabel, QLineEdit, QHBoxLayout, QVBoxLayout, QGridLayout, QStackedLayout, QWidget, QToolBox, QComboBox, QGroupBox, QMessageBox, QInputDialog
from PyQt5.QtGui import QIcon, QPalette, QColor
from PyQt5.QtCore import Qt
from lib import *

class fileMenuWindow(QtWidgets.QMainWindow):
	startEditing = QtCore.pyqtSignal(object, str, object, str)
	closeConnection = QtCore.pyqtSignal()

	updateList = QtCore.pyqtSignal(object)

	def __init__(self, clientSocket):
		QMainWindow.__init__(self)
		self.setWindowTitle('Editr')
		self.setFixedSize(600,500)
		self.clientSocket = clientSocket
		self.name = None

		self.textlist = []
		self.index = 0
		self.openFiles = []

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

		self.menu()

	def openFileHandler(self):
		fileName = self.comboBox.currentText()
		if fileName in self.openFiles:
			showErrorMessage("File is already open!")
		#else:
		#	response = sendMessage(self.clientSocket, True, "open", fileName)
		#	if "Err" in response["OpenResp"]:
		#		showErrorMessage(response["OpenResp"]["Err"])
		#	else:
		self.startEditing.emit(self.clientSocket, fileName, self.listFiles, self.name)

	def createFileHandler(self):
		fileName = self.lineEditFileName.text()
		response = sendMessage(self.clientSocket, True, "create", fileName)
		if "Err" in response["CreateResp"]:
			showErrorMessage(response["CreateResp"]["Err"])
		else:
			showSuccessMessage("\"%s\" created" % fileName)
		self.updateFileList()

	def renameFileHandler(self):
		fileName = self.comboBox.currentText()
		if fileName in self.openFiles:
			showErrorMessage("Target file is open! Please close it first")
		else:
			newName, okPressed = QInputDialog.getText(self, "Rename file", "Enter new file name:", QLineEdit.Normal, "")
			if okPressed:
				if newName != '':
					response = sendMessage(self.clientSocket, True, "rename", fileName, newName)
					if "Err" in response["RenameResp"]:
						showErrorMessage(response["RenameResp"]["Err"])
					else:
						showSuccessMessage("Renamed \"%s\" to \"%s\"" % (fileName, newName))
				else:
					showErrorMessage("File name cannot be empty")
			self.updateFileList()

	def deleteFileHandler(self):
		fileName = self.comboBox.currentText()
		if fileName in self.openFiles:
			showErrorMessage("Target file is open! Please close it first")
		else:
			response = sendMessage(self.clientSocket, True, "delete", fileName)
			if "Err" in response["DeleteResp"]:
				showErrorMessage(response["DeleteResp"]["Err"])
			else:
				showSuccessMessage("Deleted \"%s\"" % fileName)
			self.updateFileList()
	
	# Updates the list of files displayed in the drop-down menu
	def updateFileList(self):
		# Retrieve the list of files from the server
		response = sendMessage(self.clientSocket, True, "getFiles")
		if "Err" in response["FilesListResp"]:
			self.showErrorMessage(response["FilesListResp"]["Err"])
			return
		self.listFiles = sorted(response["FilesListResp"]["Ok"])
		
		# Add the files to the drop-down menu
		self.comboBox.clear()
		for file in self.listFiles:
			self.comboBox.addItem(file)

		# If there are no files, disable the "open", "rename", and "delete" buttons
		if len(self.listFiles) == 0:
			self.openFileButton.setEnabled(False)
			self.renameFileButton.setEnabled(False)
			self.deleteFileButton.setEnabled(False)
		else: # Otherwise, enable all of the buttons
			self.openFileButton.setEnabled(True)
			self.renameFileButton.setEnabled(True)
			self.deleteFileButton.setEnabled(True)

		self.updateList.emit(self.listFiles)

	def closeConnectionHandler(self):
		self.clientSocket.close()
		self.closeConnection.emit()

	def appendTextList(self,text):
		self.textlist.append(text)
		self.textlist[self.index].show()
		self.index += 1
		self.openFiles.append(text.fileName)

	def remove_from_list(self, fileName):
		self.openFiles.remove(fileName)

	def returnOpenFiles(self):
		return self.openFiles

	def updateOpenFiles(self, fileName):
		self.openFiles.append(fileName)

	def removeOpenFiles(self, fileList):
		for object in fileList:
			self.openFiles.remove(object.fileName)

	def menu(self):
		exitAct = QAction(QIcon('exit.png'), '&Exit', self)
		exitAct.setShortcut('Ctrl+Q')
		exitAct.setStatusTip('Exit application')
		exitAct.triggered.connect(qApp.quit)

		menubar = self.menuBar()
		filemenu = menubar.addMenu('&File')
		filemenu.addAction(exitAct)

		namemenu = menubar.addMenu('&Name')
		nameAction = QAction('Set Username', self)
		nameAction.triggered.connect(self.setName)
		namemenu.addAction(nameAction)

	def setName(self):
		if len(self.openFiles) > 0:
			showErrorMessage("Cant set name when files opened")
			return

		name, okPressed = QInputDialog.getText(self, "", "Set Username", QLineEdit.Normal, "")

		if okPressed and name != "":
			self.name = name

		if okPressed and name == "":
			showErrorMessage("Name cannot be blank")

		print(self.name)
