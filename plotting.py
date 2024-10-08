from typing import Callable, Iterable
from itertools import chain, accumulate
from matplotlib import pyplot as plt
from matplotlib.axes import Axes
import numpy as np
import os
from os import path

class _fig: 
	axes:list
	def __init__(self,title:str="generated by _fig"):
		self.fig=plt.figure()
		self.fig.suptitle(title)
		self.axes=[]
		self._fontsize=12
		wrapped_plot_fs=['plot','semilogx','semilogy']
		def wrap(f:str):
			nonlocal self
			def inner(self,f:str):
				if self.axes is None:
					self.create_axes(1,1)
				return getattr(plt,f)
			return inner(self,f)
		for name in wrapped_plot_fs:
			setattr(self,name,wrap(name))

	def create_axes(self,num_x:int,num_y:int):
		"""
		Make the given number of subplots within this figure
		"""
		_axes=self.fig.subplots(num_x,num_y)
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
	@property
	def num_subfigs(self):
		if isinstance(self.axes,np.ndarray):
			return self.axes.shape
		return (1,1)
	@num_subfigs.setter
	def num_subfigs(self,x,y):
		self.clear()
		self.create_axes(x,y)



class figure_wrapper:
	def __init__(self):
		self.figs=[_fig("test")]
		self.fig_idx=0
		self.fontsize=12
		self.wait_save=False
		plt.show(block=False)
	@property
	def fig(self):
		return self.figs[self.fig_idx]
	
	def process_args(self,
						newplot:bool=False,
						hold:bool=True,
						fig:int=-1,
						grid:bool=True,
						prompt_for_resize:bool=False,
						**kwargs):
		if newplot:
			self.figs.append(_fig())
			self.fig_idx=len(self.figs)-1
		if fig !=-1:
			self.fig_idx=fig
		if not hold:
			self.fig.clear()
		if grid:
			plt.grid(visible=True,figure=self.fig.fig)
		if prompt_for_resize:
			self.wait_save=True

		# default plotting options

		if not "lw" in kwargs and not "linewidth" in kwargs:
			kwargs['lw']=2


		return kwargs

	def plot(self,
			 x:Iterable,
			 y:Iterable,/,
			 name:str="",
			 **kwargs):
		plot_args=self.process_args(**kwargs)
		self.fig.plot(x,y,label=name,**plot_args) #pyright:ignore
		plt.draw()

	def slogx(self,
			  x:Iterable,
			  y:Iterable,/,
			  name:str="",
			  **kwargs):
		plot_args=self.process_args(**kwargs)
		self.fig.semilogx(x,y,label=name,**plot_args) #pyright:ignore
		plt.draw()

	def slogy(self,
			  x:Iterable,
			  y:Iterable,/,
			  name:str="",
			  **kwargs):
		plot_args=self.process_args(**kwargs)
		self.fig.semilogy(x,y,label=name,**plot_args) #pyright:ignore
		plt.draw()

	def pfunc(self,
			  x:Iterable,
			  f:Callable[[Iterable],Iterable],/,
			  **kwargs):
		self.plot(x,np.vectorize(f)(x),**kwargs)

	def pplot2(self,
				x:Iterable,
				y1:Iterable,
				y2:Iterable,/,
				name:str="",
				xlab:str="",
				ylab1:str="",
				ylab2:str="",
				**kwargs):
		plot_args=self.process_args(grid=False,**kwargs)
		self.fig.create_axes(2,1)
		self.fig.axes[0].plot(x,y1,label=name,**plot_args)
		self.fig.axes[0].set_ylabel(ylab1)
		self.fig.axes[0].grid()
		tks=self.fig.axes[0].get_xticks()
		tk_labs=['']*len(tks)
		self.fig.axes[0].set_xticks(tks,labels=tk_labs)
		# self.fig.axes[0].get_xaxis().set_visible(False)
		self.fig.axes[1].plot(x,y2,label=name,**plot_args)
		self.fig.axes[1].sharex(self.fig.axes[0])
		self.fig.axes[1].set_ylabel(ylab2)
		self.fig.axes[1].set_xlabel(xlab)
		self.fig.axes[1].grid()
		self.fig.fontsize=20
		plt.draw()

	def save(self,pth:str, wait_save=False):
		if pth.startswith('/'):
			all_breaks=pth[1:].split('/')
			all_breaks[0]='/'+all_breaks[0]
		else:
			all_breaks=pth.split('/')
		for dir in accumulate(all_breaks[:-1],func=lambda a,b:f'{a}/{b}'):
			if not path.exists(dir):
				os.mkdir(dir)
		if self.wait_save|wait_save:
			input("Please resize the image as desired, then hit enter")
		print(f"saving {all_breaks[-1]} to folder {'/'.join(all_breaks[:-1])}")
		self.fig.fig.savefig(fname=pth)

class Plotting:
	def __init__(self):
		self.fig=figure_wrapper()
	def __enter__(self):
		return self.fig
	def __exit__(self):
		pass
