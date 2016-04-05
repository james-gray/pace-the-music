# NOTE(James): Test import to see if this works
from ptm.models.activity import ActivityPlan
from ptm.models.activity import Pace
from ptm.models.base import session

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QTableWidgetItem, QMenu, QAction, QComboBox
import sys
import layout

# Each key represents a pace object in the DB
paces = {'Slow':Pace.query.filter_by(speed='Slow').first(), 'Steady':Pace.query.filter_by(speed='Steady').first(), 'Fast':Pace.query.filter_by(speed='Fast').first(), 'Sprint':Pace.query.filter_by(speed='Sprint').first()}

# This class deals with GUI elements, adding connections to buttons etc..
class PaceTheMusic(QtWidgets.QMainWindow, layout.Ui_MainWindow):
    def __init__(self, parent=None):
        super(PaceTheMusic, self).__init__(parent)
        self.setupUi(self)
        self.addButton.clicked.connect(self.addButtonClicked)
        self.genButton.clicked.connect(self.genButtonClicked)

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
        try:
            #TODO check if plan exists, if not create it
        try:
            plan = ActivityPlan(name='Plan')
            for i in range(self.segmentTable.rowCount()):
                pace = paces[self.segmentTable.cellWidget(i, 0).currentText()]
                time = int(self.segmentTable.item(i, 1).text())

                plan.append_segment(pace=pace, length=time)

            session.add(plan)
            session.commit()
            print "Plan segments: %s" % plan.segments

        except ValueError:
            return

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


'''
Names for buttons and widgets etc..

INPUT: paceInput, timeInput
BUTTON: addButton
'''
