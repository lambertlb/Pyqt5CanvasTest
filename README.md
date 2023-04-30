# Pyqt5CanvasTest
Testing out PyQT5 and PySide2

This project is for me to learn more about python and also see how good PyQT5 is.

Lesson one: i Figure out how to asynchronously load images from web or disk.
    I did this by using the thread pool and QRunnable to run a asynch task.
    This was painful to figure out since web had lots of bad advice on this.
    It turns out to be pretty simple if you know the tricks. 

Lesson two: I figured out how to zoom and pan an image using QGraphicsScene and QGraphicsView and how 
to zoom and pan around a mouse point

Lesson three: I used qt builder to layout a window with ribbon bar, graphics area and a tab layout.
    Used a splitter to separate graphics from tabbed layout

Lesson four: I got drag and drop working. If button is dragged within the scene then it is just moved.
    If a button is dropped from outside the scene then a new one is created.

I switched to PySide2 to make sure it still worked. Everything works but get a couple of annoying
warnings that i can't seem to get rid of. "'Slot' object is not callable"

Bottom line is I have learned enough about Python and Pyqt5 to start an application so will
not do much more in this project.