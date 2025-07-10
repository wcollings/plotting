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
	"""
		Create a figure conveniently. This works both from Jupyter or from a standalone script. Basic operation is described below.

		First, it is recommended to use this with the context manager syntax (with figure_wrapper(...) as fw:).
		When the context is exited, the figure automatically goes through the save and close procedure!
		Arguments for the constructor are:
			outf : str,default=""
				Where to save the final plot (or set of plots)
			interactive : bool, default=False
				Whether this was run from the REPL or a source that can accept user input, or from a script. Default is False, meaning it was run from a script
			show : bool, default=False
				If the module is used interactively, this is ignored and internally set to True. Otherwise, this governs whether or not the final plot is displayed before being saved.
			tighten : bool,default=False
				This determines if the builtin matplotlib "tighten" function is called before the plot(s) are saved. It's set to False because often the way Matplotlib originally generates the plots is good enough, spacing-wise, and their "tighten" heuristic isn't great, so if it does need to be changed its better to do that manually.

		After the object is constructed, make some lines! With figure_wrapper::plot(...), slogx(...), slogy(...), loglog(...), or plot2(...).
		You can also make a vertical line with figure_wrapper::axline(...)
		Using these, you pass in the x- and y-data, and some other specifications as described in `process_args`. These take lists, or 1-D numpy arrays, or tuples, etc.
		If you have instead an independent (x-axis) array and a function, you can call figure_wrapper::pfunc(...), and pass the function you wish to plot. This essentially calls `map(func,xdata)` and plots the output of that, but is provided for convenience.
		If you have the data as a pandas Series, the x-axis data is already recorded in the `index` property, and the name you want in the legend is in the Series Name property, you can instead use figure_wrapper::pd(...), and simply pass in the right function, and everything else will be extracted and handled for you. E.G.:
			>>> df = pandas.DataFrame({'line1':[1,2,3,4], 'line2':[5,6,7,8]}, index=[-1,-2,-3,-4])
			>>> with figure_wrapper(outf="my_plot.png") as fw:
			>>>	fw.pd(fw.slogx,df['line1'],...)
		Plot as many times as you want, subsequent calls just overlay more data unless specified otherwise.
		To adjust the x-axis, you can either call `set_xlim(x_start,x_end)`, or you can set the property:
			>>> fw.xlim=(start,end)
		The same is true for the y-axis.
		Optionally, you can instead set the property `figure_wrapper.autoscale=True` to let the final x- and y-axes be determined by the max and min x and y axis values plotted on each graph. This is largely untested and should not be relied on, but if it works for you then great.

		You can set the title of the figure with the `set_title` function.
		You can adjust the font size of all text elements by calling `set_fontsize`.

		I've provided a function called figure_wrapper::fix_ticks, which will take the x-axis and reformat it so that rather than specific values being marked out, the tick labels will be removed and the axis label will be replaced with "Time (xxx us)". You can also set this to be called automatically using the property `fix_ticks_at_end`

		MULTIPLE SUBPLOTS
		-----------------
		Sometimes you'll want two plots stacked on top of each other, for which use `plot2` instead. If this is called AFTER the first plotting call, the original graph WILL be lost!
		If you need more than that, call `figure_wrapper.fig.create_axes(rows,cols). This will clear the current figure, and re-instantiate with whatever configuration was requested.
		Whatever subplot was drawn to last becomes the default going forward (after plot2, this will be the bottom plot). Calling plot etc. will draw to that subplot only!
		If you would like to draw to a different plot, you can either specify which plot in the plotting command (again, see process_args), or you can set it as a property:
			>>> fw.axis=2
		will set a new default to the third (0-indexing!) subplot.
		Calling plot2 on a figure which already has subplots registered will plot the lines in the first and second subplots, but will not clear the plot.
		All subplots will share the same x-axis limits, but not the same y-axis.
		To adjust the y-axis when subplots exist, it is recommended to adjust this via the property, `figure_wrapper.ylim=bottom,top`. 
		Using this, if a 2-tuple is passed, this is assumed to be a command intended for the current default subplot, and will adjust accordingly.
		If a 3-tuple is passed, the first argument is assumed to be the axis index.
			>>> fw.ylim=1,0.5,1.5
		will set the second axis (0-indexing!) to show only 0.5->1.5 on the y-axis.

		MULTIPLE FIGURES
		----------------
		Sometimes you'll want multiple figure windows with the same data. In this case, just add the argument `new_plot` when you go to plot the data.
		In the same way as with subplots, this will now becomes the default figure and axis to plot to, so if you need to go back to the original figure window you need to set the property:
			>>> fw.fig=0

		SAVING
		------
		When the context is exited, the figure will go about saving and closing. Some things final things happen at this stage.
		For every plot, subplot, and figure, the grid will be turned on.
		If you've set the `tighten` property, the graph will be adjusted accordingly.
		If you've set autoscale, the limits will be adjusted as best as possible.
		If the graph is to be shown, it will show up now, and the program will block until the console is advanced.
		If you set `outf`, the figure will be set to be saved. If this contains forward slashes, indicating a different directory, and that path doesn't exist, it will be created automatically. Then, the figure is saved to that path. The image filetype will be determined by the file extension provided.
	"""
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
		"""
			Process any additional arguments needed for generating the plot.

			Parameters
			----------
			newplot : bool, default=False
				Whether to plot this in a new figure window, or on the current one
			hold : bool, default=True
				Whether to append this line to the last graph, or delete all lines and _just_ plot this new line. `True` means keep the old graph.
			fig: int, default=-1
				Specify which figure window to plot to. When a new figure window is created, it can be specified with increasing numbers starting from 0, i.e. a second figure window would be 1, and third would be 2, etc. The default, -1, means "whatever the most recent figure window written to was".
			prompt_for_resize : bool, default=False
				this only needs to be set once per `figure_wrapper` object. It determines if you want to just save the graph as it is generated, or if you want to do some manual resizing, or axis tweaking, after all the lines have been plotted but before the graph is saved and closed.
			legend_loc : str, default=""
				If you want to specify where the legend goes on the plot, pass that here. Accepts all the arguments that matplotlib.pyplot.Legend.loc accepts
			plot_loc : int, default=-1
				set the specific axis within the current (or specified) figure window to plot to. The default, -1, means "whatever the most recent axis written to was".
			name : str, default=""
				The name of the line, which will be put into the legend if and when that gets generated. If this is specified for any lines, this also triggers the legend to be generated.
			yy : bool,default=False
				Whether this goes on the normal (left) y-axis, or the secondary (right) y-axis.
			color : Any
				See accepted matplotlib colors.
			linewidth : int
				The line width, default is 2
			lw : int
				alias for linewidth
			**kwargs : dict
				Anything else that matplotlib.pyplot.plot accepts can be passed here and will be passed on literally.
		"""
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
		"""
			Create a lin-lin plot, with all provided arguments. For accepted kwargs, see `process_args`
		"""
		plot_args=self.process_args(**kwargs)
		self.fig.plot(x,y,**plot_args) #pyright:ignore
		self.draw()

	def pd(self,func:Callable,series:list[pd.Series],**kwargs) -> None:
		'''
			Process the given function `func` with provided pandas series `series`.
		'''
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
		'''
			semilog plot, with the x-axis in log scale.
		'''
		plot_args=self.process_args(**kwargs)
		self.fig.semilogx(x,y,**plot_args) #pyright:ignore
		self.draw()

	def slogy(self,
			  x:Iterable,
			  y:Iterable,/,
			  **kwargs):
		'''
			semilog plot, with the y-axis in log scale
		'''
		plot_args=self.process_args(**kwargs)
		self.fig.semilogy(x,y,**plot_args) #pyright:ignore
		self.draw()

	def loglog(self,
			  x:Iterable,
			  y:Iterable,/,
			  **kwargs):
		'''
			log-log plot
		'''
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
			sel=self.fig._axis
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
		for dir in accumulate(all_breaks[:-1],func=lambda a,b:f'{a}/{b}'):
			if not path.exists(dir):
				os.mkdir(dir)
		print(f"saving {all_breaks[-1]} to folder {'/'.join(all_breaks[:-1])}")

	def save(self,pth):
		self.prep_fig_for_save()
		pth=path.abspath(pth)
		self.create_dirs(pth)
		self.fig.fig.savefig(fname=pth)
