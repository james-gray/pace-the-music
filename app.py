from PyQt5 import QtWidgets

from ptm.views.base import PaceTheMusic

# Initialize the class on startup
def main():
    app = QtWidgets.QApplication(sys.argv) # new instance of QApplication
    form = PaceTheMusic() # set form to represent the application
    form.show() # display form
    app.exec_() # execute app

if __name__=='__main__':
    main()
