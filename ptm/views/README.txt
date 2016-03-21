To run the application enter 'python main.py' into the command line.

Structure:
layout.ui is the QTDesigner file, used to make changes to the general look of the UI

layout.py is the compiled python code for the UI, this can also be used to launch the app without any functionality

Compiling UI:
To compile the layout.ui file into a python file readable by main.py, use the following command,  pyuic5 layout.ui -o layout.py

