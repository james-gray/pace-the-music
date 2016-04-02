from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QTableWidgetItem, QMenu, QAction, QComboBox
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

		self.addSegment()


	# adds a segment to the QtableWidget
	def addSegment(self):
		time = self.timeInput.text() # Grab current text for time input box
		pace = self.copyPaceSelector() # Create a pace selector, defaulted to chosen pace
		rowPos = self.segmentTable.rowCount()

		self.segmentTable.insertRow(rowPos) # Add an empty row
		self.segmentTable.setCellWidget(rowPos, 0, pace) # Add pace
		self.segmentTable.setItem(rowPos, 1, QTableWidgetItem(time)) # Add time length

	# right-click menu for QtableWidget
	def contextMenuEvent(self, event):
		self.menu = QMenu(self)
		deleteAction = self.menu.addAction('Delete')
		moveUpAction = self.menu.addAction('Move up')
		moveDownAction = self.menu.addAction('Move down')
		action = self.menu.exec_(self.mapToGlobal(event.pos()))

		if action == deleteAction:
			self.segmentTable.removeRow(self.segmentTable.currentRow()) # remove the currently selected row
		elif action == moveUpAction:
			self.moveRowUp(self.segmentTable.currentRow())
		elif action == moveDownAction:
			self.moveRowDown(self.segmentTable.currentRow())

	# move row up
	def moveRowUp(self, rowPos):
		if rowPos == 0:
			print 'You can\'t do that'
			return

		tempPace = self.copyPaceSelector()
		tempPace.setCurrentIndex(self.segmentTable.cellWidget(rowPos, 0).currentIndex())
		tempTime = self.segmentTable.takeItem(rowPos, 1)
		self.segmentTable.removeRow(rowPos)
		self.segmentTable.insertRow(rowPos-1) # Add an empty row
		self.segmentTable.setCellWidget(rowPos-1, 0, tempPace) # Add pace
		self.segmentTable.setItem(rowPos-1, 1, tempTime) # Add time length

	# move row down
	def moveRowDown(self, rowPos):
		if rowPos == self.segmentTable.rowCount()-1:
			print 'You can\'t do that'
			return

		tempPace = self.copyPaceSelector()
		tempPace.setCurrentIndex(self.segmentTable.cellWidget(rowPos, 0).currentIndex())
		tempTime = self.segmentTable.takeItem(rowPos, 1)
		self.segmentTable.removeRow(rowPos)
		self.segmentTable.insertRow(rowPos+1) # Add an empty row
		self.segmentTable.setCellWidget(rowPos+1, 0, tempPace) # Add pace
		self.segmentTable.setItem(rowPos+1, 1, tempTime) # Add time length


	# create a pace selector identical to the one used to add segments
	def copyPaceSelector(self):
		selector = QComboBox() # create a combo box 
		for i in range(self.paceSelect.count()):
			selector.addItem(self.paceSelect.itemText(i))
		selector.setCurrentIndex(self.paceSelect.currentIndex())
		return selector


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
