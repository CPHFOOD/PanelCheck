import wx, os, sys


class Progress(wx.Dialog):
    def _init_ctrls(self, prnt):
        # generated method, don't edit
        #wx.Frame.__init__(self, prnt, -1, "Summary", (-1,-1), (200,100))
        wx.Dialog.__init__(self, id=wx.NewId(), name=u'Progress', parent=prnt,
              pos=wx.DefaultPosition, size=wx.DefaultSize,
              style=wx.DEFAULT_DIALOG_STYLE, title=u'Progress:')
        self.SetClientSize(wx.Size(200, 100))
        
        pathname = os.path.dirname(sys.argv[0]) 
        self.progPath = os.path.abspath(pathname).decode(sys.getfilesystemencoding())
        figpath = self.progPath + u'/fig.ico'
        self.SetIcon(wx.Icon(figpath,wx.BITMAP_TYPE_ICO))
        sizer = wx.BoxSizer(wx.VERTICAL)
        self.textSummary = wx.TextCtrl(id=wx.NewId(), parent=self,  style=wx.TE_MULTILINE, value=u'')

	sizer_inner = wx.BoxSizer(wx.VERTICAL)
        self.gauge = wx.Gauge(id=wx.NewId(), parent=self, range=100, style=wx.GA_HORIZONTAL)
        sizer.Add(self.textSummary, 1, wx.EXPAND, 0)
        sizer_inner.Add(self.gauge, 1, wx.EXPAND, 0)
        sizer.Add(sizer_inner, 0, wx.EXPAND, 0)
        
        self.Bind(wx.EVT_CLOSE, self.closeFrame)
        
        self.SetSizer(sizer)



    def __init__(self, parent):
        """
        Opens progress dialog.
        """
        self._init_ctrls(parent)
        self.gauge.SetValue(0)
        self.Layout()
        self.Update()
        self.Show()
   
   
   
    def set_gauge(self, value=0, text=''):
        self.gauge.SetValue(value)
        self.append_text(text)
        self.Layout()
        self.Update()
   
   
   
    def append_text(self, text):
        self.textSummary.AppendText(text)
        
        
    def closeFrame(self, event):
        """
        Exits the program.
        
        @type event:    object
        @param event:    An event is a structure holding information about an 
        event passed to a callback or member function.
        """
        self.Destroy()