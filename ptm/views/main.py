from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QTableWidgetItem, QMenu, QAction
import sys
import layout

# This class deals with GUI elements, adding connections to buttons etc..
class PaceTheMusic(QtWidgets.QMainWindow, layout.Ui_MainWindow):
	def __init__(self, parent=None):
		super(PaceTheMusic, self).__init__(parent)
		self.setupUi(self)
		self.addButton.clicked.connect(self.addButtonClicked)

	# do this stuff when user clicks on the "Add Segment" button
 	def addButtonClicked(self):
 		try:
			temp = int(self.timeInput.text())
			if(temp > 3600):
				print 'Length of a segment cannot exceed 3600 seconds!'
				return
			elif(temp <= 5):
				print  'Length of a segment has to be greater than 5 seconds!'
				return
		except ValueError:
			print('Invalid time input')
			return

		time = self.timeInput.text() # Grab current text for time input box
		pace = self.paceSelect.currentText() # Grab current text for pace input box
		self.addSegment(time, pace)


	# adds a segment to the QtableWidget
	def addSegment(self, time, pace):
		rowPos = self.segmentTable.rowCount() # Add an empty row
		self.segmentTable.insertRow(rowPos) 

		#self.segmentTable.setItem(rowPos, 0, QTableWidgetItem(str(rowPos))) # Add ID (Use default numbering scheme instead of extra column?)
		self.segmentTable.setItem(rowPos, 0, QTableWidgetItem(pace)) # Add pace
		self.segmentTable.setItem(rowPos, 1, QTableWidgetItem(time)) # Add time length

	# remove a row (segment) from the QtableWidget
	def removeSegment(self, row):
		self.segmentTable.removeRow(row)

	# right-click menu for QtableWidget
	def contextMenuEvent(self, event):
		self.menu = QMenu(self)
		deleteAction = self.menu.addAction('Delete')
		action = self.menu.exec_(self.mapToGlobal(event.pos()))
		if action == deleteAction:
			self.removeSegment(self.segmentTable.currentRow()) # remove the currently selected row


# Initialize the class on startup
def main():
	app = QtWidgets.QApplication(sys.argv) # new instance of QApplication
	form = PaceTheMusic() # set form to represent the application
	form.show() # display form
	app.exec_() # execute app

if __name__=='__main__':
	main()


'''
Names for buttons and widgets etc..

INPUT: paceInput, timeInput
BUTTON: addButton
'''
