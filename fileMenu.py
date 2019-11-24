from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QAction, qApp, QLabel, QLineEdit, QHBoxLayout, QVBoxLayout, QGridLayout, QStackedLayout, QWidget, QToolBox, QComboBox, QGroupBox, QMessageBox, QInputDialog
from PyQt5.QtGui import QIcon, QPalette, QColor
from PyQt5.QtCore import Qt
from lib import *

class fileMenuWindow(QtWidgets.QMainWindow):
	startEditing = QtCore.pyqtSignal()
	closeConnection = QtCore.pyqtSignal()

	updateList = QtCore.pyqtSignal(object)

	def __init__(self):
		QMainWindow.__init__(self)
		self.setWindowTitle('Editr')
		self.setFixedSize(600,500)

		self.textlist = []
		self.index = 0
		self.openFiles = []

		# Button for opening a file
		self.openFileButton = QPushButton('Open File')
		self.openFileButton.clicked.connect(self.openFileHandler) 
		self.openFileButton.setFixedSize(100, 50)

		# Button for closing connection to the server
		closeButton = QPushButton('Close Connection')
		closeButton.clicked.connect(self.closeConnectionHandler)
		closeButton.setFixedSize(150, 50)

		# Layout configuration
		fileSelectLayout = QHBoxLayout()
		fileSelectLayout.addWidget(self.openFileButton)

		q = QWidget()
		q.setLayout(fileSelectLayout)
		self.setCentralWidget(q)

	def openFileHandler(self):

		#else:
		#	response = sendMessage(self.clientSocket, True, "open", fileName)
		#	if "Err" in response["OpenResp"]:
		#		showErrorMessage(response["OpenResp"]["Err"])
		#	else:
		self.startEditing.emit()

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
		# self.openFiles.append(text.fileName)

	def remove_from_list(self, fileName):
		self.openFiles.remove(fileName)

	def returnOpenFiles(self):
		return self.openFiles

	def updateOpenFiles(self, fileName):
		self.openFiles.append(fileName)

	def removeOpenFiles(self, fileList):
		for object in fileList:
			self.openFiles.remove(object.fileName)
