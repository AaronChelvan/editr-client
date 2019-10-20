from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import json, string

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
		# The location of the cursor
		cursorPosition = self.textCursor().selectionStart()

		# The number of characters highlighted (0 == no characters highlighted)
		numChars = self.textCursor().selectionEnd() - self.textCursor().selectionStart()

		if event.key() == Qt.Key_Backspace:
			if numChars > 0:
				print("Deleted %d chars starting at offset %d" % (numChars, cursorPosition))
			elif self.textCursor().atStart() == False: # Is there a character to the left of the cursor?
				print("Deleted char at offset %d" % (cursorPosition-1))
			else:
				print("Nothing to delete")
		elif event.key() == Qt.Key_Delete:
			if numChars > 0:
				print("Deleted %d chars starting at offset %d" % (numChars, cursorPosition))
			elif self.textCursor().atEnd() == False: # Is there a character to the right of the cursor?
				print("Deleted char at offset %d" % cursorPosition)
			else:
				print("Nothing to delete")
		elif event.text() in string.printable and event.text() != "": # if the character is a printable string
			if numChars > 0:
				print("Deleted %d chars starting at offset %d" % (numChars, cursorPosition))
			print("Inserted " + repr(event.text()) + " at offset %d" % cursorPosition)
		
		# Process the key press in the textbox
		super(Textbox, self).keyPressEvent(event)


app = QApplication([])
app.setApplicationName("Editr Client")

window = MainWindow()
window.show()
app.exec_()
