"""
GPL 3 file header
"""
import sys

from PyQt5 import QtCore, QtWidgets
from PyQt5.QtGui import QPixmap, QTransform
from PyQt5.QtWidgets import QMainWindow, QApplication, QGraphicsScene, QGraphicsView

from AsyncTasks import AsyncImage, AsynchReturn


class CanvasTestView(QGraphicsView):
	"""
	Override QGraphicsView so we can get at mouse wheel to set scaling
	"""

	def __init__(self, scene, parent):
		super(CanvasTestView, self).__init__(scene, parent)
		self.zoom = 1

	def wheelEvent(self, event):
		delta = event.angleDelta().y() / 120
		if delta > 0:
			self.zoom *= 1.05
		elif delta < 0:
			self.zoom /= 1.05
		self.transform()

	def transform(self):
		self.setTransform(QTransform().scale(self.zoom, self.zoom))

	def zoomReset(self):
		self.zoom = 1
		self.transform()


class MainWindow(QMainWindow):
	def __init__(self):
		self.imageWidth = None
		self.imageHeight = None
		self.screenWidth = None
		self.screenHeight = None
		self.runOnce = False

		super(MainWindow, self).__init__()
		self.setWindowTitle('Test Canvas')
		self.img = QPixmap()
		self.scene = QGraphicsScene()
		self.pixMapItem = self.scene.addPixmap(self.img)
		self.view = CanvasTestView(self.scene, self)
		self.view.setDragMode(QGraphicsView.ScrollHandDrag)
		self.view.setTransformationAnchor(QtWidgets.QGraphicsView.AnchorUnderMouse)
		self.view.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
		self.view.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
		self.addImage()

	def appLoaded(self):
		"""
		app is loaded so thread pool should be running
		:return: None
		"""
		self.loadAnImage()

	def resizeEvent(self, resizeEvent):
		"""
		Screen was resized
		:param resizeEvent: resize event
		:return: None
		"""
		width = self.frameGeometry().width()
		height = self.frameGeometry().height()
		self.view.resize(width + 2, height + 2)

	def addImage(self):
		"""
		Image added so get size of everything
		:return:
		"""
		self.getScreenResolution()
		self.imageWidth = self.img.width()
		self.imageHeight = self.img.height()
		if self.imageWidth > self.screenWidth or self.imageHeight > self.screenHeight:
			self.resize(self.screenWidth, self.screenHeight)
			self.show()
			self.resetScroll()
			self.view.fitInView(self.scene.sceneRect(), QtCore.Qt.KeepAspectRatio)
		else:
			self.resize(self.imageWidth + 2, self.imageHeight + 2)
			self.show()
			self.resetScroll()
		self.view.zoomReset()

	def updateImage(self, newPixmap):
		"""
		new image loaded so update old pixel map
		:param newPixmap:
		:return: None
		"""
		self.img = newPixmap
		self.pixMapItem.setPixmap(self.img)
		self.addImage()

	def keyPressEvent(self, event):
		"""
		Update picture when a key is pressed
		:param event:
		:return:
		"""
		self.loadAnImage()

	def loadAnImage(self):
		"""
		Load images in background
		:return: None
		"""
		if not self.runOnce:
			AsyncImage('http://static4.paizo.com/image/content/PathfinderTales/PZO8500-CrisisOfFaith-Corogan.jpg', self.imageLoaded, self.failedLoad)
			self.runOnce = True
		else:
			AsyncImage('image/level1.jpg', self.imageLoaded2, self.failedLoad)
			self.runOnce = False

	@QtCore.pyqtSlot(AsynchReturn)
	def imageLoaded(self, asynchReturn):
		"""
		Callback from background task when image loaded
		:param asynchReturn: Image that was loaded
		:return: None
		"""
		self.updateImage(QPixmap.fromImage(asynchReturn.getData()))

	@QtCore.pyqtSlot(AsynchReturn)
	def imageLoaded2(self, asynchReturn):
		"""
		Callback from background task when image loaded
		added second one to make sure they can be separated
		:param asynchReturn: Image that was loaded
		:return: None
		"""
		self.updateImage(QPixmap.fromImage(asynchReturn.getData()))

	@QtCore.pyqtSlot(AsynchReturn)
	def failedLoad(self, asynchReturn):
		"""
		Image loading failed
		:param asynchReturn: return data from task
		:return: None
		"""
		pass

	def mouseDoubleClickEvent(self, event):
		self.view.zoomReset()

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
	mainWindow.appLoaded()
	sys.exit(app.exec_())
