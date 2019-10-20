from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import json

# The main window for the client program
class MainWindow(QMainWindow):
	# Constructor
	def __init__(self):
		super(MainWindow, self).__init__()
		self.setCentralWidget(Textbox()) # Add a Textbox to the window

# The textbox where the file contents will be displayed
class Textbox(QTextEdit):
	# Constructor
	def __init__(self):
		super(Textbox, self).__init__()
		self.setFont(QFont('Monospace', 14)) # Set the font

	# When a key is pressed
	def keyPressEvent(self, event):
		# Print key press info
		rowNumber = self.textCursor().blockNumber()
		colNumber = self.textCursor().columnNumber()

		if event.key() == Qt.Key_Backspace:
			if self.textCursor().atStart() == False: # Is there a character to the left of the cursor?
				print("Deleted char at (%d, %d)" % (rowNumber, colNumber))
			else:
				print("Nothing to delete")
		elif event.key() == Qt.Key_Delete:
			if self.textCursor().atEnd() == False: # Is there a character to the right of the cursor?
				print("Deleted char at (%d, %d)" % (rowNumber, colNumber))
			else:
				print("Nothing to delete")
		elif event.text() != "": # Ignore ctrl, shift, etc.
			print("Inserted " + repr(event.text()) + " at (" + str(rowNumber) + ", " + str(colNumber) + ")")
		
		# Process the key press in the textbox
		super(Textbox, self).keyPressEvent(event)


app = QApplication([])
app.setApplicationName("Editr Client")

window = MainWindow()
window.show()
app.exec_()
