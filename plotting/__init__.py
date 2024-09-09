from typing import Callable, Iterable
import pandas as pd
from itertools import chain, accumulate
from matplotlib import legend, pyplot as plt
from matplotlib.axes import Axes
from matplotlib.artist import Artist
from matplotlib.figure import Figure
import numpy as np
import os
import sys
from os import path
from .mpl import MPL_fig as _fig
import __main__ as main

__all__=['figure_wrapper']
class figure_wrapper:
	outfile:str
	tighten:bool
	figs:list
	fig_idx:int
	fontsize:int
	make_legend:bool
	legend_loc:str
	wait_save:bool
	interactive:bool
	show_at_end:bool
	fix_ticks_at_end:bool
	_autoscale:bool
	def __init__(self, outf:str="",interactive=False, show:bool=False, tighten:bool=False):
		# All of this interactive stuff should be moved into the backends
		# if run from jupyter notebook
		if "ipykernel" in sys.modules:
			self.show_at_end=False
			self.wait_save=False
		# if run from REPL
		elif not hasattr(main,'__file__') or interactive:
			print("figure_wrapper called interactively!")
			plt.ion()
			self.interactive=True
			plt.show(block=False)
			self.show_at_end=False
			self.wait_save=True
		else:
			plt.ioff()
			self.show_at_end=show
			self.wait_save=False
			self.interactive=show
		self.figs=[_fig()]
		self.fig_idx=0
		self.fontsize=12
		self.outfile=outf
		self.make_legend=False
		self.legend_loc="best"
		self.autoscale=False
		self.tighten=tighten
		self.fix_ticks_at_end=False
	@property
	def fig(self):
		return self.figs[self.fig_idx]
	
	def set_title(self,t:str):
		self.fig.title=t
	def process_args(self,
						newplot:bool=False,
						hold:bool=True,
						fig:int=-1,
						prompt_for_resize:bool=False,
						legend_loc:str="",
						plot_loc:int=-1,
						name:str="",
						yy:bool=False,
						**kwargs):
		if legend_loc !="":
			self.legend_loc=legend_loc
		if plot_loc != -1:
			self.fig.axis=plot_loc-1
		if newplot:
			self.figs.append(_fig())
			self.fig_idx=len(self.figs)-1
		if fig !=-1:
			self.fig_idx=fig
		if not hold:
			self.fig.clear()
		if prompt_for_resize:
			self.wait_save=True
		# default plotting options
		if name !="":
			self.make_legend=True
		if yy:
			self.fig.axes.append(self.fig.axis.twinx())
			self.fig.axis=len(self.fig.axes)-1
			if "color" in kwargs:
				self.fig.axis.tick_params(axis='y',labelcolor=kwargs['color'])
		kwargs['label']=name
		if not "lw" in kwargs and not "linewidth" in kwargs:
			kwargs['lw']=2


		return kwargs

	def plot(self,
			 x:Iterable,
			 y:Iterable,/,
			 **kwargs):
		plot_args=self.process_args(**kwargs)
		self.fig.plot(x,y,**plot_args) #pyright:ignore
		self.draw()

	def pd(self,func:Callable,series:list[pd.Series],**kwargs) -> None:
		if func.__name__=="plot2":
			self.plot2(
				  series[0].index, 
				  series[0],
				  series[1],
				  xlab=str(series[0].index.name),
				  ylab1=str(series[0].name),
				  ylab2=str(series[1].name),
				  **kwargs
		   )
		else:
			func(self,
		  series[0].index,
		  series[0],
		  **kwargs)

	def slogx(self,
			  x:Iterable,
			  y:Iterable,/,
			  **kwargs):
		plot_args=self.process_args(**kwargs)
		self.fig.semilogx(x,y,**plot_args) #pyright:ignore
		self.draw()

	def slogy(self,
			  x:Iterable,
			  y:Iterable,/,
			  **kwargs):
		plot_args=self.process_args(**kwargs)
		self.fig.semilogy(x,y,**plot_args) #pyright:ignore
		self.draw()

	def loglog(self,
			  x:Iterable,
			  y:Iterable,/,
			  **kwargs):
		plot_args=self.process_args(**kwargs)
		self.fig.loglog(x,y,**plot_args) #pyright:ignore
		self.draw()

	def pfunc(self,
			  x:Iterable,
			  f:Callable[[Iterable],Iterable],/,
			  **kwargs):
		self.plot(x,np.vectorize(f)(x),**kwargs)

	def plot2(self,
				x:Iterable,
				y1:Iterable,
				y2:Iterable,/,
				xlab:str="",
				ylab1:str="",
				ylab2:str="",
				adjust_ticks:bool=False,
				**kwargs):
		plot_args=self.process_args(**kwargs)
		if self.fig.num_subfigs < 2:
			self.fig.create_axes(2,1)
		self.fig.axis=0
		self.fig.plot(x,y1,**plot_args)
		self.fig.set_ylabel(ylab1)
		self.fig.axis=1
		self.fig.plot(x,y2,**plot_args)
		self.fig.sharex(self.fig.axes[0])
		self.fig.set_ylabel(ylab2)
		self.fig.axis.set_xlabel(xlab)
		self.draw()
		if adjust_ticks:
			self.fix_ticks_at_end = True

	def axline(self,loc:float,axis="x"):
		if axis=="x":
			plt.axvline(loc,linewidth=2,color='k',linestyle='dashed')
		else:
			plt.axhline(loc,linewidth=2,color='k',linestyle='dashed')

	def fix_ticks(self):
		tks=self.fig.axes[0].get_xticklabels()
		x1=round(float(tks[1]._x),2)
		x0=round(float(tks[0]._x),2)
		t_delta=round(x1-x0,3)
		self.fig.axes[0].xaxis.set_ticklabels([])
		xlab= self.fig.axes[1].get_xlabel()
		print(xlab)
		self.fig.axes[1].set_xlabel(xlab + f' ({t_delta}µs/division)')

	def save(self,pth:str, wait_save=False, tighten:bool=True):
		self.fig.tighten=tighten
		if self.fix_ticks_at_end:
			self.fix_ticks()
		if self.make_legend:
			self.fig.axis.legend(loc=self.legend_loc,draggable=wait_save)
		if self.autoscale:
			plt.autoscale(True, axis='y',tight=False)
		if self.wait_save|wait_save:
			input("Please resize the image as desired, then hit enter")
		fig_saver(self.fig).save(pth)
	
	def set_xlim(self,left:float,right:float):
		self.fig.axis.set_xlim(left,right)

	def set_ylim(self,bot:float,top:float):
		self.fig.axis.set_ylim(bot,top)

	def set_labels(self,xlab:str|None=None,ylab:str|None=None,ax:int=-1,**kwargs):
		if ax==-1:
			ax=self.fig._axis
		if xlab:
			self.fig.axes[ax].set_xlabel(xlab,kwargs)
		if ylab:
			self.fig.axes[ax].set_ylabel(ylab,kwargs)
		self.draw()

	def draw(self):
		if not self.show_at_end:
			plt.draw()
	
	def set_fontsize(self,fs):
		self.fig.fontsize=fs
		self.draw()
	
	@property
	def autoscale(self):
		return self._autoscale
	@autoscale.setter
	def autoscale(self,val:bool):
		self._autoscale=val
		plt.autoscale(val, axis='y',tight=True)
	@property
	def xlim(self):
		return self.fig.axes[0].get_xlim()
	@xlim.setter
	def xlim(self,lim:tuple):
		self.set_xlim(lim[0],lim[1])
		self.draw()
	
	@property
	def ylim(self) -> tuple[tuple[float,float]]:
		lims=[]
		for ax in self.fig:
			lims.append(ax.get_ylim())
		return tuple(lims)
	@ylim.setter
	def ylim(self,lims:tuple):
		"""
		If lims is two elements long, this is interpreted as (bot,top), with the graph to 
		adjust being the first axis.
		If lims is three elements long, this is interpreted as (axis,bot,top).
		"""
		if len(lims)==3:
			(sel,start,stop)=lims
		else:
			(start,stop)=lims
			sel=0
		self.fig.axes[sel].set_ylim(start,stop)
		self.draw()

	def __enter__(self):
		return self
	def __exit__(self,*_):
		for ax in self.fig:
			ax.grid(visible=True)
		if self.show_at_end:
			plt.show()
		if self.outfile !="":
			self.save(self.outfile,wait_save=self.wait_save,tighten=self.tighten)
	
	def __del__(self):
		for fig in self.figs:
			del fig

class fig_saver:
	def __init__(self,fig:_fig):
		self.fig=fig

	def prep_fig_for_save(self):
		if self.fig.tighten:
			self.fig.fig.tight_layout()
		# for ax in self.fig:
		# 	ax.grid(visible=True)
		# 	ys=list(ax.get_ylim())
		# 	delta=(ys[1]-ys[0])*0.1
		# 	if self.fig.log_axis != 0:
		# 		ys[0]*=0.9
		# 	else:
		# 		ys[0]-=delta
		# 	ys[1]+=delta
		# 	ax.set_ylim(ys)
	
	def create_dirs(self,pth):
		if pth.startswith('/'):
			all_breaks=pth[1:].split('/')
			all_breaks[0]='/'+all_breaks[0]
		else:
			all_breaks=pth.split('/')
		dirs_made=[]
		for dir in accumulate(all_breaks[:-1],func=lambda a,b:f'{a}/{b}'):
			if not path.exists(dir):
				os.mkdir(dir)
		print(f"saving {all_breaks[-1]} to folder {'/'.join(all_breaks[:-1])}")

	def save(self,pth):
		self.prep_fig_for_save()
		pth=path.abspath(pth)
		self.create_dirs(pth)
		self.fig.fig.savefig(fname=pth)
		# plt.close('all')
