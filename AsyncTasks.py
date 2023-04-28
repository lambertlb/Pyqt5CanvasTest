"""
GPL 3 file header
"""
import requests
from PyQt5 import QtCore
from PyQt5.QtCore import QRunnable, QThreadPool, QObject
from PyQt5.QtGui import QImage


class AsynchReturn:
	"""
	Class to hand answers back to caller
	Wanted to just return the actual async instance but got into
	circular references.
	Each subclass of AsynchBase can use data as it sees fit
	that the nice part of interpreted languages.
	"""
	def __init__(self):
		self.hadException = False
		self.data = None

	def getData(self):
		"""
		get data from operation
		:return: data
		"""
		return self.data

	def hadError(self):
		"""
		was there an error
		:return: True if was error
		"""
		return self.hadException


class AsyncSignal(QObject):
	"""
	Small worker class so QRunnable can call signals
	"""
	success = QtCore.pyqtSignal(AsynchReturn)
	failure = QtCore.pyqtSignal(AsynchReturn)


# global reference to thread pool
asyncPool = None


class AsynchBase(QRunnable):
	"""
	Class to allow long takes to run in thread pool
	"""
	signaler = None  # so we can call signals

	def __init__(self, onSuccess, onFailure):
		super().__init__()
		self.signaler = AsyncSignal()  # so we can call signals
		self.signaler.success.connect(onSuccess)
		self.signaler.failure.connect(onFailure)
		self.returnData = AsynchReturn()
		global asyncPool
		if asyncPool is None:
			asyncPool = QThreadPool.globalInstance()
			asyncPool.setMaxThreadCount(30)
		asyncPool.start(self)

	@QtCore.pyqtSlot()
	def run(self):
		"""
		run the task and handle exception
		:return: None
		"""
		try:
			self.runTask()
		except (Exception,):
			self.returnData.hadException = True
		self.taskFinished()

	def runTask(self):
		"""
		Subclasses need to override this method to do their work
		:return: None
		"""
		pass

	def taskFinished(self):
		"""
		Subclasses need to override this method to handle things after task is finished
		:return: None
		"""
		pass

	def hadError(self):
		"""
		Subclasses need to override this method to getting errors
		:return:True if there was an error
		"""
		return self.returnData.hadException


class AsyncImage(AsynchBase):
	"""
	Task to asynchronously load an image.
	if the URL starts with http it assumes a web request
	else if tries to load from file
	"""
	def __init__(self, url,  onSuccess, onFailure):
		self.url = url
		self.reply = None
		super(AsyncImage, self).__init__(onSuccess, onFailure)

	def runTask(self):
		"""
			Runs in background thread to load image
			:return: None
			"""
		if str(self.url).startswith('http'):    # is this a web request?
			self.reply = requests.get(self.url)
			if self.reply.status_code == 200:
				self.returnData.data = QImage()
				self.returnData.data.loadFromData(self.reply.content)
		else:
			self.returnData.data = QImage(self.url)

	def taskFinished(self):
		"""
		Task is finished need to signal to originator
		:return: None
		"""
		if self.hadError():
			self.signaler.failure.emit(self.returnData)
		else:
			self.signaler.success.emit(self.returnData)

	def hadError(self):
		"""
		Was there and error
		:return: True is there was
		"""
		return self.returnData.hadError() or self.returnData.getData() is None or self.returnData.getData().isNull()

	def getImage(self):
		"""
		get the image
		:return: QImage
		"""
		return self.returnData.getData()
