from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QAction, qApp, QLabel, QLineEdit, QHBoxLayout, QVBoxLayout, QGridLayout, QStackedLayout, QWidget, QToolBox
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

		label = QLabel(self)
		label.setText("File name:")
		label.move(50, 50)

		self.lineEditFileName = QLineEdit('', self)
		self.lineEditFileName.move(150, 50)

		openFileButton = QPushButton('Open File', self)
		openFileButton.move(150, 150)
		openFileButton.clicked.connect(self.openFileHandler) 
		
		createFileButton = QPushButton('Create File', self)
		createFileButton.move(150, 200)
		createFileButton.clicked.connect(self.createFileHandler) 
		
		closeButton = QPushButton('Close Connection', self)
		closeButton.move(150, 250)
		closeButton.clicked.connect(self.closeConnectionHandler)

		

	def openFileHandler(self):
		fileName = self.lineEditFileName.text()
		self.startEditing.emit(self.clientSocket, fileName)

	def createFileHandler(self):
		fileName = self.lineEditFileName.text()
		sendMessage(self.clientSocket, "create", fileName)
		print("created " + fileName)

	def closeConnectionHandler(self):     
		self.clientSocket.close()
		self.closeConnection.emit()