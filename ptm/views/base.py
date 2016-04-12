from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QTableWidgetItem, QMenu, QAction, QComboBox, QMessageBox, QInputDialog
import sys, os, layout, db

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
        msgBox = QMessageBox()
        try:
            temp = int(self.timeInput.text())
            if(temp > 3600):
                print 'Length of a segment cannot exceed 3600 seconds!'
                msgBox.setText('Length of a segment cannot exceed 3600 seconds!')
                msgBox.exec_()
                return
            elif(temp <= 5):
                print  'Length of a segment has to be greater than 5 seconds!'
                msgBox.setText('Length of a segment has to be greater than 5 seconds!')
                msgBox.exec_()
                return
        except ValueError:
            print('Invalid time input')
            msgBox.setText('Invalid time input')
            msgBox.exec_()
            return

        self.addSegment()

    # generate a playlist when the user clicks on the "Generate Playlist" button
    def genButtonClicked(self):
        if not os.path.exists('./playlists'): # create playlist folder if it doesn't exist
            os.mkdir('./playlists', 0755)

        msgBox = QMessageBox()
        if self.segmentTable.rowCount() == 0:
            print 'You need to have segments to do that!'
            return

        playListName = self.enterPlaylistName()

        if not playListName:
            msgBox.setText('You have to enter a valid name!')
            msgBox.exec_()
            return

        print 'Grabbing playlist: ', playListName
        db.generatePlayList(
            playlist_name=playListName,
            plan_id=1,
        )

        msgBox.setText('Your playlist has been added to the \'playlists\' folder!')
        msgBox.exec_()

    # open a dialog window to take user input for playlist name
    def enterPlaylistName(self):
        inputDialog = QInputDialog()
        inputDialog.setLabelText('Enter a name for the playlist: ')
        inputDialog.exec_()
        name = inputDialog.textValue().replace(" ", "")

        return name

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
            db.addSegment(plan_id=1, pace=pace, time=time) # Add the segment to the database

        #TODO: create playlist file and add it to folder

    # update the database when a user edits the length of a segment
    def segmentTimeChanged(self, event):
        rowPos = self.segmentTable.currentRow()
        print 'RowPos = ', rowPos
        if(rowPos==-1): # make sure the user has actually selected a row
            return
        time = int(self.segmentTable.item(rowPos, 1).text())
        db.updateSegTime(plan_id=1, seg_pos=rowPos, time=time)

    # update the database when a user edits the pace of a segment
    def segmentPaceChanged(self, event):
        rowPos = self.segmentTable.currentRow()
        print 'RowPos = ', rowPos
        if(rowPos==-1): # make sure the user has actually selected a row
            return
        pace = self.segmentTable.cellWidget(rowPos, 0).currentText()
        db.updateSegPace(plan_id=1, seg_pos=rowPos, pace=pace)


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

        db.removeSegment(plan_id=1, seg_pos=rowPos) # Repeat above steps in the database
        db.insertSegment(plan_id=1, seg_pos=rowPos-1, pace=tempPace.currentText(), time=int(tempTime.text()))

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

        db.removeSegment(plan_id=1, seg_pos=rowPos) # Repeat above steps in the database
        db.insertSegment(plan_id=1, seg_pos=rowPos+1, pace=tempPace.currentText(), time=int(tempTime.text()))


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
