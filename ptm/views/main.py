from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QListWidgetItem
import sys
import layout

# This class deals with GUI elements, adding connections to buttons etc..
class PaceTheMusic(QtWidgets.QMainWindow, layout.Ui_MainWindow):
	def __init__(self, parent=None):
		super(PaceTheMusic, self).__init__(parent)
		self.setupUi(self)
		self.addButton.clicked.connect(self.button_click)

	# do this stuff when user clicks on the "Add Segment" button
 	def button_click(self):
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
		self.add_segment(time, pace)


	# adds a segment to the QListWidget
	def add_segment(self, time, pace):
		pos = str(self.segmentList.count()+1) # Set the position of the segment in the list
		#print 'Length: ' + time + ' Pace: ' + pace

		segment = QListWidgetItem(pos + ') ' + pace + '  ' + time + '(s)')
		self.segmentList.addItem(segment)



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
