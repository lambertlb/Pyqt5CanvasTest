"""
GPL 3 file header
"""
import sys

import requests
from PyQt5 import QtCore
from PyQt5.QtCore import QThreadPool, QRunnable
from PyQt5.QtGui import QPixmap, QTransform, QImage
from PyQt5.QtWidgets import QMainWindow, QApplication, QGraphicsScene, QGraphicsView


class WorkerSignals(QtCore.QObject):
	"""
	Small worker class so QRunnable can call signals
	"""
	signal = QtCore.pyqtSignal(QImage)


class WorkerThread(QRunnable):
	"""
	Class to allow long taks to run in thread pool
	"""
	signaler = WorkerSignals()  # so we can call signals

	def __init__(self, url, onLoad):
		super().__init__()
		self.url = url
		self.signaler.signal.connect(onLoad)

	@QtCore.pyqtSlot()
	def run(self):
		"""
		Runs in backgroun thread
		:return: None
		"""
		if str(self.url).startswith('http'):
			reply = requests.get(self.url)
			qimg = QImage()
			qimg.loadFromData(reply.content)
		else:
			qimg = QImage(self.url)
		self.signaler.signal.emit(qimg)


class CanvasTestView(QGraphicsView):
	"""
	Override QGraphicsView so we can get at mouse wheel to set scaling
	"""
	def wheelEvent(self, event):
		delta = event.angleDelta().y() / 120
		if delta > 0:
			mainWindow.zoomIn()
		elif delta < 0:
			mainWindow.zoomOut()


class MainWindow(QMainWindow):
	def __init__(self):
		self.zoom = None
		self.imageWidth = None
		self.imageHeight = None
		self.screenWidth = None
		self.screenHeight = None
		self.runOnce = False

		super(MainWindow, self).__init__()
		QThreadPool.globalInstance().setMaxThreadCount(100) # make sure we have a buch of threads
		self.setWindowTitle('Test Canvas')
		self.img = QPixmap()
		self.scene = QGraphicsScene()
		self.pixMapItem = self.scene.addPixmap(self.img)
		self.view = CanvasTestView(self.scene, self)
		self.view.setDragMode(QGraphicsView.ScrollHandDrag)
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

	def updateImage(self, newPixmap):
		"""
		new image loaded so update old pixel map
		:param newPixmap:
		:return: None
		"""
		self.img = newPixmap
		self.pixMapItem.setPixmap(self.img)
		self.addImage()
		pass

	def keyPressEvent(self, event):
		"""
		Update picture when a key is pressed
		:param event:
		:return:
		"""
		self.loadAnImage()
		pass

	def loadAnImage(self):
		"""
		Load images in background
		:return: None
		"""
		if not self.runOnce:
			url = 'http://static4.paizo.com/image/content/PathfinderTales/PZO8500-CrisisOfFaith-Corogan.jpg'
			worker = WorkerThread(url, self.imageLoaded)
			self.runOnce = True
		else:
			url = 'image/level1.jpg'
			worker = WorkerThread(url, self.imageLoaded)
			self.runOnce = False
		QThreadPool.globalInstance().start(worker)

	@QtCore.pyqtSlot(QImage)
	def imageLoaded(self, image):
		"""
		Callback from background task when image loaded
		:param image: Image that was loaded
		:return: None
		"""
		self.updateImage(QPixmap.fromImage(image))

	@QtCore.pyqtSlot(QImage)
	def imageLoaded2(self, image):
		"""
		Callback from background task when image loaded
		added second one to make sure they can be separated
		:param image: Image that was loaded
		:return: None
		"""

		self.updateImage(QPixmap.fromImage(image))

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
	mainWindow.appLoaded()
	sys.exit(app.exec_())
