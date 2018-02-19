
import wx, os, sys
import pandas as pd 

from numpy import ceil, floor

from Grid import DataTable, DataGrid, DataGridSheet



class Summary(wx.Dialog):
    def _init_ctrls(self, prnt):
        #wx.Frame.__init__(self, prnt, -1, "Summary", (-1,-1), (400,340))
        wx.Dialog.__init__(self, id=wx.NewId(), name=u'Summary', parent=prnt,
              pos=wx.DefaultPosition, size=wx.DefaultSize, style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER)
        self.SetClientSize(wx.Size(440, 440))
        
        pathname = os.path.dirname(sys.argv[0]) 
        self.progPath = os.path.abspath(pathname).decode(sys.getfilesystemencoding())
        figpath = self.progPath + u'/fig.ico'
        self.SetIcon(wx.Icon(figpath,wx.BITMAP_TYPE_ICO))
        
        
        # selected columns:
        self.ass_index = 0
        self.samp_index = 1
        self.rep_index = 2
        
        self.str_ind = 0
        
        self.sizer_main = wx.BoxSizer(wx.VERTICAL)


        # 1st panel # select panel
        self.panel1 = wx.Panel(self, id=wx.NewId())
        self.panel1.Show(True)
        
        self.sizer_select = wx.BoxSizer(wx.VERTICAL)
        self.grid = DataGridSheet(self.panel1)
        self.table = DataGrid([])
        self.grid.SetTable(self.table)        
        self.grid.Bind(wx.EVT_KEY_DOWN, self.onKeyEvent)        
        
        grid_col_names = []
        box_inner = wx.GridSizer(2, 3, 2, 6)
        h1 = wx.StaticText(self.panel1, -1, "Assessors:", size=(90,-1))
        h2 = wx.StaticText(self.panel1, -1, "Samples:", size=(90,-1))
        h3 = wx.StaticText(self.panel1, -1, "Replicates:", size=(90,-1))
        self.ch_ass = wx.Choice(self.panel1, -1, choices = grid_col_names, size=(90,-1))    
        self.ch_samp = wx.Choice(self.panel1, -1, choices = grid_col_names, size=(90,-1))   
        self.ch_rep = wx.Choice(self.panel1, -1, choices = grid_col_names, size=(90,-1))
        box_inner.Add(h1, 0, wx.EXPAND, 0)
        box_inner.Add(h2, 0, wx.EXPAND, 0)
        box_inner.Add(h3, 0, wx.EXPAND, 0)
        box_inner.Add(self.ch_ass, 0, wx.EXPAND, 0)
        box_inner.Add(self.ch_samp, 0, wx.EXPAND, 0)
        box_inner.Add(self.ch_rep, 0, wx.EXPAND, 0)
        
        wxline = wx.StaticLine(self.panel1, -1, style=wx.LI_VERTICAL)

        """box_balance = wx.BoxSizer(wx.VERTICAL)
        self.box_title = wx.StaticText(self.panel1, -1, "Balanced Data", size=(400,-1))
        self.radio1 = wx.RadioButton(self.panel1, -1, "Remove Assessors: ", style = wx.RB_GROUP, size=(400,-1))
        self.radio2 = wx.RadioButton(self.panel1, -1, "Remove Samples: ", size=(400,-1))
        box_balance.Add(self.box_title, 0, wx.ALIGN_LEFT|wx.ALIGN_TOP|wx.ALL, 2)
        box_balance.Add(self.radio1, 0, wx.ALIGN_LEFT|wx.ALIGN_TOP|wx.ALL, 2)
        box_balance.Add(self.radio2, 0, wx.ALIGN_LEFT|wx.ALIGN_TOP|wx.ALL, 2)
        #self.radio1.Show(False)
        #self.radio2.Show(False)"""
        """
        box_inner2 = wx.BoxSizer(wx.HORIZONTAL)
        butt_sizer = wx.BoxSizer(wx.VERTICAL)
        butt_rem = wx.NewId()
        self.butt_remove = wx.Button(id=butt_rem, label=u'Remove Column >>', parent=self.panel1)
        self.butt_remove.Bind(wx.EVT_BUTTON, self.OnButtonRem, id=butt_rem)        
        butt_add = wx.NewId()
        self.butt_add = wx.Button(id=butt_add, label=u'<< Re-add Column', parent=self.panel1)
        self.butt_add.Bind(wx.EVT_BUTTON, self.OnButtonAdd, id=butt_add)
        butt_sizer.Add(self.butt_remove, 0, wx.ALL)
        butt_sizer.Add(self.butt_add, 0, wx.ALL)"""
        box_inner2 = wx.BoxSizer(wx.VERTICAL)
        box_title = wx.StaticText(self.panel1, -1, "Import columns:")
        self.list_columns =  wx.CheckListBox(parent=self.panel1, id=-1, size=(130, 100))
        box_inner2.Add(box_title, 0, wx.ALL, 2)
        box_inner2.Add(self.list_columns, 1, wx.EXPAND, 2)
        
        
        box_inner1 = wx.BoxSizer(wx.HORIZONTAL)
        box_inner1.Add(box_inner, 0, wx.ALL, 2)
        box_inner1.Add(wxline, 0, wx.EXPAND, 2)
        box_inner1.Add(box_inner2, 1, wx.EXPAND, 2)
        
        ok1 = wx.NewId(); cancel1 = wx.NewId()
        self.buttonOK1 = wx.Button(id=ok1, label=u'Accept', parent=self.panel1)
        self.buttonOK1.Bind(wx.EVT_BUTTON, self.OnButtonOK1Button, id=ok1)
        self.buttonCancel1 = wx.Button(id=cancel1, label=u'Cancel', parent=self.panel1)
        self.buttonCancel1.Bind(wx.EVT_BUTTON, self.OnCancel1Button, id=cancel1)        
        self.sizer_select.Add(box_inner1, 0, wx.EXPAND, 4)
        self.sizer_select.Add(self.grid, 1, wx.GROW)
        
        box_buttons1 = wx.BoxSizer(wx.HORIZONTAL)
        box_buttons1.Add(self.buttonCancel1, 0, wx.ALIGN_RIGHT|wx.ALIGN_BOTTOM|wx.ALL, 2)
        box_buttons1.Add(self.buttonOK1, 0, wx.ALIGN_RIGHT|wx.ALIGN_BOTTOM|wx.ALL, 2)
        
        
        self.sizer_select.Add(box_buttons1, 0, wx.ALIGN_RIGHT|wx.ALL, 0)
        
        self.panel1.SetSizer(self.sizer_select)



        # 2nd panel # progress panel
        self.panel2 = wx.Panel(self, id=wx.NewId())
        self.panel2.Show(False)
        
        self.sizer_progress = wx.BoxSizer(wx.VERTICAL)
        box_inner2 = wx.BoxSizer(wx.HORIZONTAL)
        self.gauge1 = wx.Gauge(id=wx.NewId(), name='gauge1',
              parent=self.panel2, range=100, style=wx.GA_HORIZONTAL)
        
        self.textSummary2 = wx.TextCtrl(id=wx.NewId(), name=u'textSummary', parent=self.panel2, style=wx.TE_MULTILINE, value=u'')              
        box_inner2.Add(self.gauge1, 1, wx.EXPAND, 0)
        self.sizer_progress.Add(self.textSummary2, 1, wx.TOP|wx.GROW)
        self.sizer_progress.Add(box_inner2, 0, wx.GROW)
        self.panel2.SetSizer(self.sizer_progress)      
              
              
              
              
        # 3rd panel # summary panel     
        self.panel3 = wx.Panel(self, id=wx.NewId())
        self.panel3.Show(False)
        
        self.sizer_summary = wx.BoxSizer(wx.VERTICAL)
        box_inner3a = wx.BoxSizer(wx.HORIZONTAL)
        
        self.textScaleLimInfo = wx.StaticText(id=wx.NewId(),
              label=u'Scale limits for this data set:',
              name=u'textScaleLimInfo', parent=self.panel3, size=(-1,-1))
              
        self.textLabelLims = wx.StaticText(id=wx.NewId(),
              label=u'Data set min/max :', name=u'textLabelLims',
              parent=self.panel3)
        self.textSummary3 = wx.TextCtrl(id=wx.NewId(),
              name=u'textSummary', parent=self.panel3, style=wx.TE_MULTILINE|wx.TE_RICH2, value=u'') 
        
        self.textMin = wx.StaticText(id=wx.NewId(), label=u'Min. :',
              name=u'textMin', parent=self.panel3, size=(66, -1))

        self.textMax = wx.StaticText(id=wx.NewId(), label=u'Max. :',
              name=u'textMax', parent=self.panel3, size=(66, -1))
              
        self.textMinInput = wx.TextCtrl(id=wx.NewId(), parent=self.panel3, value=u'   ', size=(66, -1))

        self.textMaxInput = wx.TextCtrl(id=wx.NewId(), parent=self.panel3, value=u'   ', size=(66, -1))
        box_inner3b1 = wx.BoxSizer(wx.VERTICAL)
        box_inner3b2 = wx.BoxSizer(wx.VERTICAL)              
        box_inner3b1.Add(self.textMin, 0, wx.EXPAND)
        box_inner3b1.Add(self.textMinInput, 0, wx.EXPAND)
        box_inner3b2.Add(self.textMax, 0, wx.EXPAND)
        box_inner3b2.Add(self.textMaxInput, 0, wx.EXPAND)  
        
        ok3 = wx.NewId()
        self.buttonOK3 = wx.Button(id=ok3, label=u'OK',
              name=u'buttonOK3', parent=self.panel3)
        self.buttonOK3.Bind(wx.EVT_BUTTON, self.OnButtonOK3Button, id=ok3)
        #self.Bind(wx.EVT_CLOSE, self.Hide)

        box_inner3c = wx.BoxSizer(wx.VERTICAL)
        box_inner3d = wx.BoxSizer(wx.HORIZONTAL)
        
        self.textLims = wx.StaticText(id=wx.NewId(), label=u'',
              name=u'textLims', parent=self.panel3)


        box_inner3d.Add(self.textLabelLims, 0, wx.EXPAND, 0)    
        box_inner3d.Add(self.textLims, 0, wx.EXPAND, 0) 
        
        box_inner3c.Add(self.textScaleLimInfo, 1, wx.ALL, 2)
        box_inner3c.Add(box_inner3d, 0, wx.ALL, 2)
        
        box_inner3a.Add(box_inner3c, 1, wx.EXPAND, 2)
        box_inner3a.Add(box_inner3b1, 0, wx.EXPAND, 2)
        box_inner3a.Add(box_inner3b2, 0, wx.EXPAND, 2)
        box_inner3a.Add(self.buttonOK3, 0, wx.ALIGN_RIGHT|wx.ALIGN_BOTTOM|wx.ALL, 2)
        
        self.sizer_summary.Add(self.textSummary3, 1, wx.LEFT|wx.TOP|wx.GROW)
        self.sizer_summary.Add(box_inner3a, 0, wx.GROW)
        self.panel3.SetSizer(self.sizer_summary)
        
        self.sizer_main.Add(self.panel1, 1, wx.GROW)
        self.SetTitle('Select Columns:')
        self.SetSizer(self.sizer_main)
        self.Layout()
        

    def __init__(self, parent):
        """
        Opens summary frame with option for setting scale limit values.
        """
        self.limits = []
        self._init_ctrls(parent)
        self.gauge1.SetValue(0)
        self.Layout()
        #self.Show()


    def OnCancel1Button(self, event):
        #self.radio1_selection = self.radio1.GetValue()
        #self.radio2_selection = self.radio2.GetValue()
        
        self.Destroy()
  
        
    def OnButtonOK1Button(self, event):
        #self.radio1_selection = self.radio1.GetValue()
        #self.radio2_selection = self.radio2.GetValue()
        
        if self.checkSelections():
            #self.switch_to_progress()
            self.EndModal(1)
        else:
            pass


    def OnButtonOK3Button(self, event):
        if self.checkValues():
            self.Close()
        else:
            dlg = wx.MessageDialog(self, 'Values not accepted. Change one or both of the minimum and maximum scale values.',
                               'Error Message',
                               wx.OK | wx.ICON_INFORMATION)
            dlg.ShowModal()
            dlg.Destroy()
            
            
            
    def checkValues(self):
        try:
            limit = 65536 #just a big number, chosen randomly by HR (06.08.2005)
            if float(self.textMinInput.GetValue()) > limit*(-1) and float(self.textMinInput.GetValue()) < float(self.textMaxInput.GetValue()):
                if float(self.textMaxInput.GetValue()) < limit:
                    self.limits[2] = float(self.textMinInput.GetValue())
                    self.limits[3] = float(self.textMaxInput.GetValue())
                    return True
            else:
                return False
        except:
            return False
            
            
    def checkSelections(self):
        self.ass_index = self.ch_ass.GetSelection()
        self.samp_index = self.ch_samp.GetSelection()
        self.rep_index = self.ch_rep.GetSelection()
        
        self.out_columns = []
        for i in range(0, len(self.lables)):
            if not self.list_columns.IsChecked(i):
                self.out_columns.append(i)
        
        if self.ass_index == self.samp_index or self.ass_index == self.rep_index or self.rep_index == self.samp_index:
            dlg = wx.MessageDialog(self, 'Two or more of the column-selectors have been assigned to same column. Please change column selections.',
                               'Error Message',
                               wx.OK | wx.ICON_INFORMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return False
        elif self.ass_index == self.cols-1 or self.samp_index == self.cols-1 or self.rep_index == self.cols-1:
            dlg = wx.MessageDialog(self, 'You have assigned to last column, there will be no score values. Please change column selections or check file.',
                               'Error Message',
                               wx.OK | wx.ICON_INFORMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return False            
        elif self.ass_index in self.out_columns:
            dlg = wx.MessageDialog(self, 'You have uncheked column: ' + str(self.lables[self.ass_index])+ '. The column has been assigned as the Assessors-column.\nRe-select that column if you wish to use it as the Assessors-column.',
                               'Error Message',
                               wx.OK | wx.ICON_INFORMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return False   
        elif self.samp_index in self.out_columns:
            dlg = wx.MessageDialog(self, 'You have uncheked column: ' + str(self.lables[self.samp_index])+ '. The column has been assigned as the Samples-column.\nRe-select that column if you wish to use it as the Samples-column.',
                               'Error Message',
                               wx.OK | wx.ICON_INFORMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return False 
        elif self.rep_index in self.out_columns:
            dlg = wx.MessageDialog(self, 'You have uncheked column: ' + str(self.lables[self.rep_index])+ '. The column has been assigned as the Replicates-column.\nRe-select that column if you wish to use it as the Replicates-column.',
                               'Error Message',
                               wx.OK | wx.ICON_INFORMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return False
        else:
            return True
        
            
    def get_limits(self):
        return self.limits
    
    
    def switch_to_progress(self):
        self.panel1.Show(False) # select panel
        self.panel2.Show(True) # progress panel
        self.panel3.Show(False) # summary panel
        self.sizer_main.Detach(self.panel1)
        self.SetTitle('Progress:')
        self.sizer_main.Add(self.panel2, 1, wx.GROW)
        self.Layout()
    
    
    def switch_to_summary(self):
        self.panel1.Show(False) # select panel
        self.panel2.Show(False) # progress panel
        self.panel3.Show(True) # summary panel
        self.sizer_main.Detach(self.panel2)
        self.SetTitle('Summary:')
        self.sizer_main.Add(self.panel3, 1, wx.GROW)
        self.Layout()        
              
        
    def reset(self):
        self.panel1.Show(False) # select panel
        self.panel2.Show(True) # progress panel
        self.panel3.Show(False) # summary panel
        #self.SetSizer(self.sizer_progress)
        self.limits = []
        self.textLims.SetLabel("")
        self.textMinInput.SetValue("")
        self.textMaxInput.SetValue("")
        self.gauge1.SetValue(0)
        
        
        
    def set_limits(self, limits):
        self.limits = limits
        self.epsilon = -1*(-1*self.limits[3]-(-1*self.limits[2]))*0.04 #4% of length lower to upper limits
        #self.textLims.SetLabel(str(self.limits[2]) + ", ... ," + str(self.limits[3]))
        self.textLims.SetLabel("%5.2f, ...,%5.2f" % (self.limits[2], self.limits[3]))
        self.limits[2] =  floor(self.limits[2] - self.epsilon)
        self.limits[3] = ceil(self.limits[3] + self.epsilon)
        self.textMinInput.SetValue(str(self.limits[2]))
        self.textMaxInput.SetValue(str(self.limits[3]))
        
        
        
    def set_gauge(self, value):
        self.gauge1.SetValue(value)
        
        
        
    def set_text(self, text):
        self.textSummary2.Clear()
        self.textSummary2.WriteText(text)
    
    
    def append_text(self, text):
        self.textSummary2.AppendText(text)
        
        
    def set_text_summary(self, text):
        self.textSummary3.Clear()
        self.textSummary3.WriteText(text)
    
    
    def append_text_summary(self, text):
        self.textSummary3.AppendText(text)
        
        
    def set_grid(self, datasheet):
        print 'I made it to set_grid'
        self.datasheet = datasheet[:]
        #self.datasheet = pd.DataFrame(datasheet)
        print '1'
        # self.table = DataGrid(datasheet[1:])
        #self.table = DataTable(self.datasheet)
        print '2'
        print self.table
        self.grid.SetTable(DataGrid(self.datasheet),True)
        # self.grid.SetTable(DataTable(self.datasheet),True)
        print '3'
        self.grid.SetRowLabelSize(1)
        print '4'
        self.cols = len(datasheet[0])
        print 'About to define labels'
        self.lables = []
        #self.Layout()
        #col_choices = wx.ArrayString()
        print 'initialting set_grid for loop'
        for i in range(0, self.cols):
            #col_choices.Add(wx.String(self.grid.GetColLabelValue(i)))
            _label = datasheet[0][i] #self.grid.GetColLabelValue(i)
            if i == self.cols-1: _label = _label[:-1]
            self.ch_ass.Append(_label)
            self.ch_samp.Append(_label)
            self.ch_rep.Append(_label)       
            self.list_columns.Append(_label)
            self.list_columns.Check(i, True)
            
            self.table.SetColLabelValue(i, _label)
            self.lables.append(_label)
        
        print 'for loop i done'    
        self.table.SetColLables(self.lables)
        #print col_choices
        #self.ch_ass.Append(col_choices)
        self.ch_ass.Select(0)
        #self.ch_samp.Append(col_choices)
        self.ch_samp.Select(1)
        #self.ch_rep.Append(col_choices)
        self.ch_rep.Select(2)
        self.Layout()
        self.Show()
 
    
    
    def onKeyEvent(self,event=None):
        """
        Captures , act upon keystroke events.
        """
        if event == None: return
        #print type(event)
        key = event.GetKeyCode()
        #print key
        if (key < wx.WXK_SPACE or  key > 255):  return
        
        if (event.ControlDown() and chr(key)=='C'): # Ctrl-C
            self.onClipboard(event=event)
            
                       
    def onClipboard(self,event=None):
        """
        Copy to clipboard function.
        """
        self.grid.Copy()
                    
