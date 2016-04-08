# NOTE(James): Test import to see if this works
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QTableWidgetItem, QMenu, QAction, QComboBox
import sys, layout, db

#db = DatabaseFunctions()
# This class deals with GUI elements, adding connections to buttons etc..
class PaceTheMusic(QtWidgets.QMainWindow, layout.Ui_MainWindow):
    def __init__(self, parent=None):
        super(PaceTheMusic, self).__init__(parent)
        self.setupUi(self)
        self.displaySegments() # initialize segments from database
        self.addButton.clicked.connect(self.addButtonClicked)
        self.genButton.clicked.connect(self.genButtonClicked)
        self.segmentTable.itemChanged.connect(self.segmentTimeChanged)

    # display segments that are in the database NOTE: ONLY USE UPON STARTUP
    def displaySegments(self):
        segmentList = db.listSegments(1)
        for i in range(len(segmentList)):
            print 'time = ', str(segmentList[i].length)
            print 'pace = ', segmentList[i].pace_id
            self.addSegment(str(segmentList[i].length), segmentList[i].pace_id, False)

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

    # generate a playlist when the user clicks on the "Generate Playlist" button
    def genButtonClicked(self):
        if self.segmentTable.rowCount() == 0:
            print 'You need to have segments to do that!'
            return

        print 'Grabbing playlist'
        db.generatePlayList(1, 1)

    # adds a segment to the QtableWidget, if addToDB is true it also adds the segment to the database
    def addSegment(self, time=None, pace=None, addToDB=True):
        if(time == None):
            time = self.timeInput.text() # Grab current text for time input box
        pace = self.createPaceSelector(pace) # Create a pace selector, defaulted to 'pace'
        rowPos = self.segmentTable.rowCount()

        self.segmentTable.insertRow(rowPos) # Add an empty row
        self.segmentTable.setCellWidget(rowPos, 0, pace) # Add pace
        self.segmentTable.setItem(rowPos, 1, QTableWidgetItem(time)) # Add time length

        pace = self.segmentTable.cellWidget(rowPos, 0).currentText()
        if(addToDB):
            db.addSegment(1, pace, time) # Add the segment to the database

    # update the database when a user edits the length of a segment
    def segmentTimeChanged(self, event):
        rowPos = self.segmentTable.currentRow()
        print 'RowPos = ', rowPos
        if(rowPos==-1): # make sure the user has actually selected a row
            return
        time = int(self.segmentTable.item(rowPos, 1).text())
        db.updateSegTime(1, rowPos, time)

    # update the database when a user edits the pace of a segment
    def segmentPaceChanged(self, event):
        rowPos = self.segmentTable.currentRow()
        print 'RowPos = ', rowPos
        if(rowPos==-1): # make sure the user has actually selected a row
            return
        pace = self.segmentTable.cellWidget(rowPos, 0).currentText()
        db.updateSegPace(1, rowPos, pace)


    # right-click menu for QtableWidget
    def contextMenuEvent(self, event):
        self.menu = QMenu(self)
        deleteAction = self.menu.addAction('Delete')
        moveUpAction = self.menu.addAction('Move up')
        moveDownAction = self.menu.addAction('Move down')
        action = self.menu.exec_(self.mapToGlobal(event.pos()))

        if action == deleteAction:
            db.removeSegment(1, self.segmentTable.currentRow()) # remove the segment from the database
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

        tempPace = self.createPaceSelector()
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

        tempPace = self.createPaceSelector()
        tempPace.setCurrentIndex(self.segmentTable.cellWidget(rowPos, 0).currentIndex())
        tempTime = self.segmentTable.takeItem(rowPos, 1)
        self.segmentTable.removeRow(rowPos)
        self.segmentTable.insertRow(rowPos+1) # Add an empty row
        self.segmentTable.setCellWidget(rowPos+1, 0, tempPace) # Add pace
        self.segmentTable.setItem(rowPos+1, 1, tempTime) # Add time length


    # create a pace selector identical to the one used to add segments
    def createPaceSelector(self, pace_id=None):
        selector = QComboBox() # create a combo box

        for i in range(self.paceSelect.count()):
            selector.addItem(self.paceSelect.itemText(i))
        if pace_id == None:
            selector.setCurrentIndex(self.paceSelect.currentIndex())
        else:
            selector.setCurrentIndex(pace_id-1) # subtract 1 because comboboxes are indexed starting at 0

        selector.currentIndexChanged.connect(self.segmentPaceChanged) # connect to the function that deals with adding the change to the database
        return selector

'''
Names for buttons and widgets etc..

INPUT: paceInput, timeInput
BUTTON: addButton
'''
