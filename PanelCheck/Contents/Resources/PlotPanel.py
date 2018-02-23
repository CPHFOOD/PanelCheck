import wx
import matplotlib
matplotlib.use('WXAgg')
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg
from matplotlib.figure import Figure



class NoRepaintCanvas(FigureCanvasWxAgg):
    """We subclass FigureCanvasWxAgg, overriding the _onPaint method, so that
    the draw method is only called for the first two paint events. After that,
    the canvas will only be redrawn when it is resized.
    """
    def __init__(self, *args, **kwargs):
        FigureCanvasWxAgg.__init__(self, *args, **kwargs)
        self._drawn = 0
        self.point_lables = []

    def _onPaint(self, evt):
        """
        Called when wxPaintEvt is generated
        """
       # if not self._isRealized:
       #     self.realize()
        if self._drawn < 2:
            # repaint = False
            self.draw()
            self._drawn += 1
        drawDC=wx.PaintDC(self)
        self.gui_repaint(drawDC=drawDC)
        #for label in self.point_lables:
        #    label.render(drawDC)
    
    def add_point_label(self, point, txt):
        p = PointLabel(self, point, txt)
        #self.point_lables.append(p)
        return p


class PlotPanel(wx.Panel):
    """
    The PlotPanel has a Figure and a Canvas. OnSize events simply set a 
    flag, and the actually redrawing of the
    figure is triggered by an Idle event.
    """
    def __init__(self, parent, id, color = None, setsize=True, \
        dpi = None, style = wx.NO_FULL_REPAINT_ON_RESIZE, figure = None, overview_plot=False, **kwargs):
        wx.Panel.__init__(self, parent, -1, style=wx.SIMPLE_BORDER | wx.CLIP_CHILDREN, **kwargs)
        if not figure:
            self.figure = Figure(None, dpi)
        else:
            self.figure = figure
        self.canvas = NoRepaintCanvas(self, id, self.figure)
        self.SetColor(color)
        self.Bind(wx.EVT_IDLE, self._onIdle)
        self.Bind(wx.EVT_SIZE, self._onSize)
        self._resizeflag = True
        if setsize:
            self._SetSize()

    def SetColor(self, rgbtuple):
        """Set figure and canvas colours to be the same"""
        if not rgbtuple:
            rgbtuple = wx.SystemSettings.GetColour(wx.SYS_COLOUR_BTNFACE).Get()
        col = [c/255.0 for c in rgbtuple]
        self.figure.set_facecolor(col)
        self.figure.set_edgecolor(col)
        self.canvas.SetBackgroundColour(wx.Colour(*rgbtuple))

    def _onSize(self, event):
        self._resizeflag = True

    def _onIdle(self, evt):
        if self._resizeflag:
            self._resizeflag = False
            self._SetSize()
            self.draw()

    def _SetSize(self, pixels = None):
        """
        This method can be called to force the Plot to be a desired size, which defaults to
        the ClientSize of the panel
        """
        if not pixels:
            pixels = self.GetClientSize()
        self.canvas.SetSize(pixels)
        self.figure.set_size_inches(pixels[0]/self.figure.get_dpi(),
        pixels[1]/self.figure.get_dpi())
        
    def draw(self):
        """Where the actual drawing happens"""
        pass


class PointLabel:
    def __init__(self, parent, point, txt):
            self.parent = parent
	    self.foreground = wx.Colour(0,0,0)
	    self.background = wx.Colour(220,220,220)
	    self.point = point
	    self.hiding = False
	    self.orig_txt = txt
	    self.txt = txt.split('\n')
            #self.font = wx.Font(7, wx.ROMAN, wx.NORMAL, wx.BOLD)
            self.font = self.parent.GetFont()
            self.font.SetPointSize(8)
            w = 0
            self.w = w
            self.ind = 0
            for line in self.txt:
                (w, self.h) = self.parent.GetTextExtent(line)
                if w > self.w: self.w = w
                self.ind += 1
            
            #print self.w   
            
            self.rect = (self.point[0]+5, self.point[1]+5, self.w+10, self.h*self.ind + 15)

            #wpen = wx.Pen(wx.Colour(0, 0, 0), 1, wx.SOLID)
            #dc.SetPen(wpen)            
            #dc.ResetBoundingBox() 
            #dc.BeginDrawing()
         	    
    
            
            
    def render(self, dc):
            #print "render"
            
            #dc.SetBackgroundMode(wx.SOLID)
            dc.SetTextForeground(self.foreground)
            dc.SetTextBackground(self.background)
            dc.SetFont(self.font)            
            
            dc.DrawRectangle(self.point[0]+5, self.point[1]+5, self.w+10, self.h*self.ind + 15)
            ind = 0
            for line in self.txt:
	        dc.DrawText(line, self.point[0] + 10, self.point[1] + 10 + dc.GetCharHeight()*ind)
	        ind += 1  
	
	
class PointLabel2:
    def __init__(self, parent, point, txt):
            self.parent = parent
	    self.foreground = wx.Colour(0,0,0)
	    self.background = wx.Colour(220,220,220)
	    self.point = point
	    self.hiding = True
	    self.orig_txt = txt
	    self.txt = txt.split('\n')
            #self.font = wx.Font(7, wx.ROMAN, wx.NORMAL, wx.BOLD)
            self.font = self.parent.GetFont()
            self.font.SetPointSize(8)
            w = 0
            self.w = w
            self.ind = 0
            for line in self.txt:
                (w, self.h) = self.parent.GetTextExtent(line)
                if w > self.w: self.w = w
                self.ind += 1
                
            self.bmp = wx.EmptyBitmap(self.w, self.h)
            
            dc = wx.MemoryDC()
            dc.SelectObject(self.bmp)                
            dc.SetTextForeground(self.foreground)
            dc.SetTextBackground(self.background)
            dc.SetFont(self.font)            
            
            dc.DrawRectangle(self.point[0]+5, self.point[1]-4, self.w+10, self.h*self.ind + 8)
            ind = 0
            for line in self.txt:
	        dc.DrawText(line, self.point[0] + 10, self.point[1] + dc.GetCharHeight()*ind)
	        ind += 1              

         	    
    def clear(self):
            memDC = wx.MemoryDC()
            memDC.SelectObject(self.bmp)
            memDC.Clear()
            
            
    def render(self, dc):
            memDC = wx.MemoryDC()
            memDC.SelectObject(self.bmp)

            dc.Blit(self.point[0], self.point[1],
                    self.bmp.GetWidth(), self.bmp.GetHeight(),
                    memDC, 0, 0, wx.COPY, True) 	        