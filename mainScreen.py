"""
GPL 3 file header
"""
import sys
from PyQt5 import QtCore
from PyQt5.QtGui import QPixmap, QTransform
from PyQt5.QtWidgets import QMainWindow, QApplication, QGraphicsScene, QGraphicsView


class CanvasTestView(QGraphicsView):
	def wheelEvent(self, event):
		delta = event.angleDelta().y() / 120
		if delta > 0:
			mainWindow.zoomIn()
		elif delta < 0:
			mainWindow.zoomOut()


class MainWindow(QMainWindow):
	def __init__(self):
		self.imageWidth = None
		self.imageHeight = None
		self.zoom = None
		self.screenWidth = None
		self.screenHeight = None

		super(MainWindow, self).__init__()
		self.setWindowTitle('Test Canvas')
		self.img = QPixmap('image/level1.jpg')
		self.scene = QGraphicsScene()
		self.scene.addPixmap(self.img)
		self.view = CanvasTestView(self.scene, self)
		self.view.setDragMode(QGraphicsView.ScrollHandDrag)
		self.view.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
		self.view.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
		self.addImage()

	def resizeEvent(self, resizeEvent):
		width = self.frameGeometry().width()
		height = self.frameGeometry().height()
		self.view.resize(width + 2, height + 2)

	def addImage(self):
		self.getScreenResolution()
		self.imageWidth = self.img.width()
		self.imageHeight = self.img.height()
		self.zoom = 1
		if self.imageWidth > self.screenWidth or self.imageHeight > self.screenHeight:
			self.resize(self.screenWidth, self.screenHeight)
			self.show()
			self.resetScroll()
			self.view.fitInView(self.scene.sceneRect(), QtCore.Qt.KeepAspectRatio)
		else:
			self.resize(self.imageWidth + 2, self.imageHeight + 2)
			self.show()
			self.resetScroll()

	def keyPressEvent(self, event):
		pass

	def mouseDoubleClickEvent(self, event):
		self.zoomReset()

	def zoomIn(self):
		self.zoom *= 1.05
		self.updateView()

	def zoomOut(self):
		self.zoom /= 1.05
		self.updateView()

	def zoomReset(self):
		self.zoom = 1
		self.updateView()

	def updateView(self):
		self.view.setTransform(QTransform().scale(self.zoom, self.zoom))

	def resetScroll(self):
		self.view.verticalScrollBar().setValue(0)
		self.view.horizontalScrollBar().setValue(0)

	def getScreenResolution(self):
		resolution = app.desktop().availableGeometry()
		self.screenWidth = resolution.width()
		self.screenHeight = resolution.height()


if __name__ == '__main__':
	app = QApplication(sys.argv)
	mainWindow = MainWindow()
	sys.exit(app.exec_())
