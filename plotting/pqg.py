"""
The backend for pyqtgraph
"""


import pyqtgraph as pg
from PyQt5.QtGui import QColor
from typing import Iterable, Iterator, Callable
from enum import IntEnum, auto

class arg_dest(IntEnum):
	PLOT=auto()
	LEG=auto()
	TEXT=auto()

def iden(x):
	return x
class Default:
	def __init__(self,val,pred=lambda x:bool(x),gen:Callable=iden):
		self.val=val
		self.pred=pred
		self.gen=gen
	def apply(self,given,mapper:Callable=iden):
		if self.pred(given):
			return mapper(given)
		return self.gen(self.val)


def next_color() -> Iterator[str]:
	colors=['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf']
	idx=0
	while True:
		yield colors[idx]
		idx=(idx+1)%len(colors)

g_color=next_color()
class PQG_fig:
	fig:pg.GraphicsLayoutWidget
	axes:list[pg.AxisItem]
	tighten:bool
	def __init__(self,title:str=""):
		app=pg.mkQApp(title)
		self.fig=pg.GraphicsLayoutWidget(show=True)
		self.axes=[self.fig.addPlot()]
		self._axis=0
		self.tighten=False

	def process_args(self,
						dst:arg_dest,
						color:str="",
						lw:int=1,
						):
		res={}
		if dst==arg_dest.PLOT:
			res['pen']=Default(g_color,gen=next).apply(color,lambda c:pg.mkPen(width=lw,color=c))
		return res

	def plot(self,x:Iterable,y:Iterable, **kwargs):
		args=self.process_args(arg_dest.PLOT,**kwargs)
		self.axis.plot(x,y,**args)
	def semilogx(self,x:Iterable, y:Iterable,**kwargs):
		args=self.process_args(arg_dest.PLOT,**kwargs)
		self.axis.plot(x,y,**args)
		self.axis.setLogMode(True,False)

	def semilogy(self,x:Iterable, y:Iterable,**kwargs):
		args=self.process_args(arg_dest.PLOT,**kwargs)
		self.axis.plot(x,y,**args)
		self.axis.setLogMode(False,True)

	@property
	def axis(self):
		return self.axes[self._axis]
	@axis.setter
	def axis(self,ax_num:int):
		if ax_num > len(self.axes)-1:
			raise IndexError("Requested an axis that is outside the scope of current axes. Please call add_subplot first next time!")
		self._axis=ax_num
