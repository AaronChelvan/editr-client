from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
import json

# The main window for the client program
class MainWindow(QMainWindow):
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
		print(self.cursorRect())
		if event.text() != "": # Ignore ctrl, shift, etc.
			print(repr(event.text()))

		# Process the key press in the textbox 
		super(Textbox, self).keyPressEvent(event)

app = QApplication([])
app.setApplicationName("Editr Client")

window = MainWindow()
window.show()
app.exec_()
