"""
GPL 3 file header
"""
import sys

from PyQt5 import QtCore, QtWidgets
from PyQt5.QtCore import Qt, QMimeData
from PyQt5.QtGui import QPixmap, QTransform, QDrag
from PyQt5.QtWidgets import QMainWindow, QGraphicsScene, QGraphicsView, QGraphicsProxyWidget, QPushButton

from AsyncTasks import AsynchReturn, AsyncImage


class MyScene(QGraphicsScene):
	"""
	Subclass QGraphicsScene to manage drag and drop
	"""
	def dragEnterEvent(self, e):
		e.acceptProposedAction()

	def dropEvent(self, e):
		"""
		Item was dropped here.
		If is had a proxy it means it was already here so just move it.
		If no proxy then create a new item
		:param e: event
		:return:None
		"""
		src = e.source()
		if src.getProxy() is not None:
			src.getProxy().setPos(e.scenePos())
		else:
			pos = e.scenePos()
			self.addButtonToScent(pos.x(), pos.y())

	def dragMoveEvent(self, e):
		e.acceptProposedAction()

	def addButtonToScent(self, x, y):
		"""
		add a button to scene
		:param x:
		:param y:
		:return: None
		"""
		pw = QGraphicsProxyWidget()
		db = DragButton('push me')
		pw.setWidget(db)
		db.setProxy(pw)
		self.addItem(pw)
		pw.setPos(x, y)


class DragButton(QPushButton):
	"""
	Make a draggable button
	"""
	def __init__(self, *args):
		super(DragButton, self).__init__(*args)
		self.proxy = None

	def mouseMoveEvent(self, e):
		"""
		Move moved one me so start dragging
		:param e: event
		:return: None
		"""
		if e.buttons() == Qt.LeftButton:
			drag = QDrag(self)
			mime = QMimeData()
			drag.setMimeData(mime)
			drag.setPixmap(self.grab())
			drag.exec_(Qt.MoveAction)

	def setProxy(self, proxy):
		"""
		Set scene proxy if in a scene
		:param proxy:
		:return:
		"""
		self.proxy = proxy

	def getProxy(self):
		"""
		:return: proxy else None if not in scene
		"""
		return self.proxy


class CanvasTestView(QGraphicsView):
	"""
	Override QGraphicsView so we can get at mouse wheel to set scaling
	"""

	def __init__(self, scene, parent):
		super(CanvasTestView, self).__init__(scene, parent)
		self.zoom = 1
		# self.setAcceptDrops(True)

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
		self.runOnce = True

		super(MainWindow, self).__init__()
		self.setObjectName("MainWindow")
		self.resize(800, 600)
		self.centralWidget = QtWidgets.QWidget()
		self.centralWidget.setObjectName("centralWidget")
		self.gridLayout_2 = QtWidgets.QGridLayout(self.centralWidget)
		self.gridLayout_2.setObjectName("gridLayout_2")
		self.windowFrame = QtWidgets.QFrame(self.centralWidget)
		self.windowFrame.setFrameShape(QtWidgets.QFrame.StyledPanel)
		self.windowFrame.setFrameShadow(QtWidgets.QFrame.Raised)
		self.windowFrame.setObjectName("windowFrame")
		self.gridLayout = QtWidgets.QGridLayout(self.windowFrame)
		self.gridLayout.setContentsMargins(0, 0, 0, 0)
		self.gridLayout.setObjectName("gridLayout")
		self.ribbonBar = QtWidgets.QHBoxLayout()
		self.ribbonBar.setObjectName("ribbonBar")
		self.button3 = DragButton(self.windowFrame)
		self.button3.setObjectName("button3")
		self.ribbonBar.addWidget(self.button3)
		self.button2 = DragButton(self.windowFrame)
		self.button2.setObjectName("button2")
		self.ribbonBar.addWidget(self.button2)
		self.button1 = DragButton(self.windowFrame)
		self.button1.setObjectName("button1")
		self.ribbonBar.addWidget(self.button1)
		self.gridLayout.addLayout(self.ribbonBar, 0, 0, 1, 1)
		self.splitter = QtWidgets.QSplitter(self.windowFrame)
		self.splitter.setOrientation(QtCore.Qt.Horizontal)
		self.splitter.setObjectName("splitter")

		self.pixelMap = QPixmap()
		self.scene = MyScene()
		self.pixMapItem = self.scene.addPixmap(self.pixelMap)
		self.view = CanvasTestView(self.scene, self.splitter)
		self.view.setDragMode(QGraphicsView.ScrollHandDrag)
		self.view.setTransformationAnchor(QtWidgets.QGraphicsView.AnchorUnderMouse)
		self.view.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
		self.view.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)

		self.assetHolder = QtWidgets.QTabWidget(self.splitter)
		self.assetHolder.setObjectName("assetHolder")
		self.tab = QtWidgets.QWidget()
		self.tab.setObjectName("tab")
		self.assetHolder.addTab(self.tab, "")
		self.tab_2 = QtWidgets.QWidget()
		self.tab_2.setObjectName("tab_2")
		self.assetHolder.addTab(self.tab_2, "")

		self.gridLayout.addWidget(self.splitter, 1, 0, 1, 1)
		self.gridLayout_2.addWidget(self.windowFrame, 0, 0, 1, 1)
		self.setCentralWidget(self.centralWidget)
		self.statusbar = QtWidgets.QStatusBar(self)
		self.statusbar.setObjectName("statusbar")
		self.setStatusBar(self.statusbar)

		self.splitter.setSizes([600, 200])
		self.localize()
		self.loadAnImage()
		self.addImage()

		self.scene.addButtonToScent(100, 100)

	def localize(self):
		_translate = QtCore.QCoreApplication.translate
		self.setWindowTitle(_translate("MainWindow", "MainWindow"))
		self.button3.setText(_translate("MainWindow", "PushButton"))
		self.button2.setText(_translate("MainWindow", "PushButton"))
		self.button1.setText(_translate("MainWindow", "PushButton"))
		self.assetHolder.setTabText(self.assetHolder.indexOf(self.tab), _translate("MainWindow", "Tab 1"))
		self.assetHolder.setTabText(self.assetHolder.indexOf(self.tab_2), _translate("MainWindow", "Tab 2"))

	def addImage(self):
		self.show()
		self.resetScroll()
		self.view.zoomReset()

	def updateImage(self, newPixmap):
		"""
		new image loaded so update old pixel map
		:param newPixmap:
		:return: None
		"""
		self.pixelMap = newPixmap
		self.pixMapItem.setPixmap(self.pixelMap)
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
			AsyncImage('http://static4.paizo.com/image/content/PathfinderTales/PZO8500-CrisisOfFaith-Corogan.jpg',
					self.imageLoaded, self.failedLoad)
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


if __name__ == "__main__":
	app = QtWidgets.QApplication(sys.argv)
	mainWindow = MainWindow()
	mainWindow.show()
	sys.exit(app.exec_())
