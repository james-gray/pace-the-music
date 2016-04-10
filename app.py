import sys

import qdarkstyle
from PyQt5 import QtWidgets

from ptm.views.base import PaceTheMusic

def main():
    app = QtWidgets.QApplication(sys.argv) # new instance of QApplication
    form = PaceTheMusic() # set form to represent the application
    app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())
    form.show() # display form
    app.exec_() # execute app

if __name__=='__main__':
    main()
