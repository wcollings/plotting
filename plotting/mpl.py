"""
The backend for Matplotlib
"""

import numpy as np
from typing import Iterable
from matplotlib.axes import Axes
from matplotlib.artist import Artist
from matplotlib.figure import Figure
from matplotlib import legend, pyplot as plt

class MPL_fig: 
	fig:Figure
	axes:list
	tighten:bool
	log_axis:int
	simple_axis_labels:bool
	def __init__(self,title:str=""):
		self.fig=plt.figure()
		self.fig.suptitle(title)
		self.axes=[self.fig.gca()]
		self._fontsize=12
		self._axis=0
		self.log_axis=0
		self.tighten=True
		self.simple_axis_labels=False
		plt.autoscale(True,axis='both')

	def plot(self, *args, **kwargs):
		if not self.axes:
			self.create_axes(1,1)
		line=self.axis.plot(*args,**kwargs)
		self.axis.grid(True)
		return line

	def semilogx(self, *args, **kwargs):
		if not self.axes:
			self.create_axes(1,1)
		line=self.axis.semilogx(*args,**kwargs)
		self.axis.grid(True)
		self.log_axis=1
		return line

	def semilogy(self, *args, **kwargs):
		if not self.axes:
			self.create_axes(1,1)
		line=self.axis.semilogy(*args,**kwargs)
		self.axis.grid(True)
		self.log_axis=2
		return line

	def loglog(self,*args,**kwargs):
		if not self.axes:
			self.create_axes(1,1)
		line=self.axis.loglog(*args,**kwargs)
		self.axis.grid(True)
		self.log_axis=3
		return line

	def create_axes(self,num_x:int,num_y:int, index:int=1):
		"""
		Make the given number of subplots within this figure
		"""
		for axis in self.axes:
			axis.remove()
		_axes=self.fig.subplots(num_x,num_y, squeeze=False)
		if isinstance(_axes,Axes):
			self.axes=[_axes]
		elif isinstance(_axes,np.ndarray):
			self.axes=_axes.flatten().tolist()

	def __iter__(self):
		if isinstance(self.axes,Iterable):
			yield from self.axes
		else:
			yield self.axes

	def clear(self):
		"""clear this figure of all its subplots."""
		self.fig.clear()
		self.axes=[]

	def set_ylabel(self,label) -> None:
		self.axis.set_ylabel(label)
	
	def sharex(self,axis) -> None:
		self.axis.sharex(axis)
	
	@property
	def title(self) -> str:
		return self.fig.get_suptitle()
	@title.setter
	def title(self,s):
		self.fig.suptitle(s)
	@property
	def fontsize(self):
		return self._fontsize
	@fontsize.setter
	def fontsize(self,fs:int):
		self._fontsize=fs
		for ax in self:
			for item in ([ax.title, ax.xaxis.label, ax.yaxis.label] +
							 ax.get_xticklabels() + ax.get_yticklabels()):
				item.set_fontsize(fs)
		plt.rcParams.update({'legend.fontsize':fs})
	@property
	def axis(self) -> Axes:
		return self.axes[self._axis]
	@axis.setter
	def axis(self,axis_num:int):
		if axis_num > len(self.axes):
			raise IndexError("Requested an axis that is outside the scope of current axes. Please call add_subplot first next time!")
		self._axis=axis_num

	def __del__(self):
		for axis in self.axes:
			del axis
		del self.fig

	@property
	def num_subfigs(self):
		return len(self.axes)
	@num_subfigs.setter
	def num_subfigs(self,spec):
		if sum(spec)-len(spec) >= self.num_subfigs:
			for ax in self.axes:
				ax.remove()
			self.create_axes(*spec)
