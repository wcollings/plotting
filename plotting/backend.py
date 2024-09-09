"""
Defines the protocol for all backends
"""
from typing import Iterable, Protocol, Iterator
from pyqtgraph import GraphicsLayoutWidget, AxisItem
from matplotlib.figure import Figure
from matplotlib.axes import Axes

FigTp=Figure|GraphicsLayoutWidget
AxisTp=Axes|AxisItem

class Backend(Protocol):
	fig:FigTp
	axes:list
	tighten:bool
	log_axis:int
	def __init__(self,title:str=""):
		"""
		Sets up the figure, creates and shows it if required.

		Parameters
		----------
		title:str
			The title of the window to show
		"""
		...
	
	def plot(self,x:Iterable,y:Iterable, **kwargs):
		"""
		Create a standard plot from the data provided. linear x and y scales, nothing crazy
		"""
		...
	
	def semilogx(self,x:Iterable,y:Iterable, **kwargs):
		"""
		Create a plot, x is log, y is linear
		"""
		...
	def semilogy(self,x:Iterable,y:Iterable, **kwargs):
		"""
		Create a plot, x is linear, y is log
		"""
		...
	def loglog(self,x:Iterable,y:Iterable, **kwargs):
		"""
		Create a plot, x is log, y is log
		"""
		...

	def create_axes(self,num_x:int,num_y:int, index:int=1):
		"""
		Make the given number of subplots within this figure
		Within the figure, replace the current layout with a matrix of plots as requested. This is stored as an unwrapped 2d array. Any plots that were there already are erased when this is called.

		If we request a 2x2 matrix, they are indexed as:
		---------
		| 0 | 1 |
		---------
		| 2 | 3 |
		---------

		A 1x2 is obviously:
		-----
		| 0 |
		-----
		| 1 |
		-----

		Parameters
		----------
		num_x:int
			The number of columns to create
		num_y:int
			The number of rows to create
		index:int
			The 
		"""
		...

	def __iter__(self) -> Iterator:
		"""
		Create an iterator over the subplots, in case you need it for something (like setting the grid for all of them at once, etc).
		"""
		...
	def clear(self):
		"""
		Clear all the subplots and data from this figure, leaving us with a blank window
		"""
		...
	@property
	def title(self) -> str:
		"""
		return the title of the figure
		"""
		...
		# return self.fig.get_suptitle()
	@title.setter
	def title(self,s):
		"""
		Set the title of the fig
		"""
		...
		# self.fig.suptitle(s)
	@property
	def fontsize(self):
		"""
		return the fontsize of all the text of the fig

		Return
		------
		int
			The fontsize, in point
		"""
		...
		# return self._fontsize
	@fontsize.setter
	def fontsize(self,fs:int):
		"""
		Set the fontsize of all the text of the fig
		"""
		...
		# self._fontsize=fs
		# for ax in self:
		# 	for item in ([ax.title, ax.xaxis.label, ax.yaxis.label] +
		# 					 ax.get_xticklabels() + ax.get_yticklabels()):
		# 		item.set_fontsize(fs)
		# plt.rcParams.update({'legend.fontsize':fs})
	@property
	def axis(self) -> AxisTp:
		"""
		A pointer to the current axis
		"""
		...
		# return self.axes[self._axis]
	@axis.setter
	def axis(self,axis_num:int):
		"""
		Set the index of the axis you want to edit. Effectively changes the pointer
		"""
		...
		# if axis_num > len(self.axes):
		# 	raise IndexError("Requested an axis that is outside the scope of current axes. Please call add_subplot first next time!")
		# self._axis=axis_num

	def __del__(self):
		"""

		"""
		...
		# for axis in self.axes:
		# 	del axis
		# del self.fig

	@property
	def num_subfigs(self):
		"""

		"""
		...
		# return len(self.axes)
	@num_subfigs.setter
	def num_subfigs(self,spec):
		"""

		"""
		...
		# if sum(spec)-len(spec) >= self.num_subfigs:
		# 	for ax in self.axes:
		# 		ax.remove()
		# 	self.create_axes(*spec)
