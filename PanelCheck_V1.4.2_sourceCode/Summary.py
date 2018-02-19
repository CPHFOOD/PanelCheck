import wx, sys, os

def create(parent):
    return SummaryFrame(parent)

[wxID_SUMMARYFRAME, wxID_SUMMARYFRAMEBUTTON_OK, wxID_SUMMARYFRAMEPANEL, 
 wxID_SUMMARYFRAMETEXT, wxID_SUMMARYFRAMEBUTTONPANEL,
] = [wx.NewId() for _init_ctrls in range(5)]

class SummaryFrame(wx.Frame):
    def _init_ctrls(self, prnt, text):
        wx.Frame.__init__(self, id=-1, name=u'SummaryFrame',
              parent=prnt, title=u'Summary')
        self.SetClientSize(wx.Size(392, 317))

        self.button_panel = wx.Panel(self, id = wxID_SUMMARYFRAMEBUTTONPANEL)

        self.text = wx.TextCtrl(id=wxID_SUMMARYFRAMETEXT, name=u'text',
              parent=self, value=text, style=wx.TE_MULTILINE)
        print 'summary frame'      
        #sizer initialization
        self.box = wx.BoxSizer(wx.VERTICAL) #main
        sizer_inner = wx.BoxSizer(wx.HORIZONTAL)

        self.button_ok = wx.Button(id=wxID_SUMMARYFRAMEBUTTON_OK, label=u'OK',
              name=u'button_ok', parent=self)
        self.button_ok.Bind(wx.EVT_BUTTON, self.closeFrame,
              id=wxID_SUMMARYFRAMEBUTTON_OK)
        self.Bind(wx.EVT_CLOSE, self.closeFrame)
              
        pathname = os.path.dirname(sys.argv[0]) 
        self.progPath = os.path.abspath(pathname).decode(sys.getfilesystemencoding())
        self.icon = wx.Icon(self.progPath + u"/fig.ico", wx.BITMAP_TYPE_ICO)
        self.SetIcon(self.icon)              
              
        
        sizer_inner.Add(self.button_panel, 1, wx.EXPAND)
        sizer_inner.Add(self.button_ok, 0, wx.EXPAND)
        #self.button_panel.SetSizer(sizer_inner)
        self.box.Add(self.text, 1, wx.GROW)
        self.box.Add(sizer_inner, 0, wx.EXPAND)
        self.SetSizer(self.box)
        self.Layout()

    def __init__(self, parent, text):
        self._init_ctrls(parent, text)
        
    def closeFrame(self, event=None):
        """
            Exits the program.
            
            @type event:    object
            @param event:    An event is a structure holding information about an 
            event passed to a callback or member function.
        """
        self.Hide()
        
        

class Starter(wx.App):
    def OnInit(self):
        frame = SummaryFrame(None, "")
        self.SetTopWindow(frame)
        frame.Show()
        return 1

if __name__ == "__main__":
    import gettext
    gettext.install("app") # replace with the appropriate catalog name
    app = Starter(0)
    app.MainLoop()
