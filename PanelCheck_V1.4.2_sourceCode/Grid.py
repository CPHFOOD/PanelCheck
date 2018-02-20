
import os, sys, wx, wx.grid as gridlib

import numpy as np
import pandas as pd


class DataTable(gridlib.GridTableBase):

    def __init__(self, data=None):
        gridlib.GridTableBase.__init__(self)
        self.headerRows = 1
        if data is None:
            data = pd.DataFrame()
        self.data = data

    def GetNumberRows(self):
        return len(self.data)

    def GetNumberCols(self):
        return len(self.data.columns) + 1

    def GetValue(self, row, col):
        if col == 0:
            return self.data.index[row]
        return self.data.iloc[row, col - 1]

    def SetValue(self, row, col, value):
        self.data.iloc[row, col - 1] = value

    def GetColLabelValue(self, col):
        if col == 0:
            if self.data.index.name is None:
                return 'Index'
            else:
                return self.data.index.name
        return self.data.columns[col - 1]

    def GetTypeName(self, row, col):
        return wx.grid.GRID_VALUE_STRING

    def GetAttr(self, row, col, prop):
        attr = wx.grid.GridCellAttr()
        if row % 2 == 1:
            attr.SetBackgroundColour(EVEN_ROW_COLOUR)
        return attr


class GridFrame(wx.Frame):
    """
    Class GridFrame for worksheet type of data visualization.
    """
    def __init__(self, parent, frameName, results, config=None):
        """
        Init method for class GridFrame. Creates all gui items and handles
        frame events.

        @version: 1.0
        @since: 22.10.2005

        @author: Henning Risvik
        @organization: Matforsk - Norwegian Food Research Institute
        """
        wx.Frame.__init__(self, parent, -1, "Data Grid - " + frameName, (-1,-1), (500,400))


        #parametres
        ##        self.sampList = sampleList
        ##        self.assList = assessorList
        ##        self.repList = replicateList
        ##        self.attList = attributeList
        ##        self.sparseMatrix = matrix
        ##        self.results = results

        #grid initialization
        grid_id = wx.NewId()
        # wxGrid(wxWindow* parent, wxWindowID id, const wxPoint& pos = wxDefaultPosition, const wxSize& size = wxDefaultSize, long style = wxWANTS_CHARS, const wxString& name = wxPanelNameStr)
        self.grid = DataGridSheet(self)

        #table setup
        self.table = DataGrid(results)
        self.grid.SetTable(self.table)

        #this setReadOnly makes big grids slow
        ##        for row in range(0,self.table.GetNumberRows()):
        ##            for col in range(0, self.table.GetNumberCols()):
        ##                self.grid.SetReadOnly(row, col, True)

        # if Raw Data:
        if self.grid.GetCellValue(0,0) == "Raw Data":
            # coloring of assessor-, sample- and replicate-column
            # the three colors:
            #(r,g,b): (255,255,255)=White (0,0,0)=Black
            assessors_BG_Color = wx.Colour(240,240,240) #column 1 - very light gray +
            samples_BG_Color = wx.Colour(225,225,225) #column 2 - very light gray
            replicates_BG_Color = wx.Colour(210,210,210) #column 3 - light gray

            for i in range(3, self.grid.GetNumberRows()):
                self.grid.SetCellBackgroundColour(i,0,assessors_BG_Color)
                self.grid.SetCellBackgroundColour(i,1,samples_BG_Color)
                self.grid.SetCellBackgroundColour(i,2,replicates_BG_Color)

        if config != None:
            for key in config:
                if "back_color" in config[key]:
                    self.grid.SetCellBackgroundColour(key[0], key[1], config[key]["back_color"])

        #setting the icon for frame
        pathname = os.path.dirname(sys.argv[0])
        self.progPath = os.path.abspath(pathname)
        self.icon = wx.Icon(self.progPath + u"/fig.ico", wx.BITMAP_TYPE_ICO)
        self.SetIcon(self.icon)

        #button initialization
        butt_close = wx.NewId()
        self.button_1 = wx.Button(self, butt_close, "Close")

        #sizer initialization
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer_inner = wx.BoxSizer(wx.HORIZONTAL)

        #adding gui items
        sizer.Add(self.grid, 1, wx.LEFT|wx.TOP|wx.GROW)
        #sizer_inner.Add(self.button_1, 0, wx.FIXED_MINSIZE, 0)
        #sizer.Add(sizer_inner, 0, wx.ALIGN_CENTER|wx.TOP)

        self.statusBar = wx.StatusBar(self, -1)
        self.statusBar.SetFieldsCount(1)
        self.SetStatusBar(self.statusBar)

        #event binding
        self.grid.Bind(wx.EVT_KEY_DOWN, self.onKeyEvent)
        self.Bind(wx.EVT_CLOSE, self.onClose)
        self.Bind(wx.EVT_BUTTON, self.onClose, id=butt_close)

        #adjusting sizer
        self.SetSizer(sizer)
        sizer.SetSizeHints(self)
        self.Layout()






    def onClose(self,event=None):
        self.Hide()



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




class GridFramePerfInd(GridFrame):
    """
    Class GridFrame for worksheet type of data visualization.
    """
    def __init__(self, parent, frameName, results, s_data, plot_data, config=None):
        """
        Init method for class GridFrame. Creates all gui items and handles
        frame events.

        @version: 1.0
        @since: 22.10.2005

        @author: Henning Risvik
        @organization: Matforsk - Norwegian Food Research Institute
        """
        GridFrame.__init__(self, parent, frameName, results, config) 
        
        
        
        import PlotData
        
        self.plotType = plot_data.tree_path[0]
        self.plot_data = PlotData.CollectionCalcPlotData()
        plot_data.copy_data_to(self.plot_data)
        self.plot_data.copy_data(plot_data)
        self.plot_data.overview_plot = True
        self.plot_data.special_opts["disable_cursor_link"] = True
        self.s_data = s_data
        self.numberOfWindow = 0
        self.figureList = []        
        
        self.grid.Bind(gridlib.EVT_GRID_CELL_LEFT_DCLICK, self.onLeftDClickEvent)
        self.Bind(wx.EVT_CLOSE, self.OnFrameClosing) 


    def onLeftDClickEvent(self,event=None):
        """
        Captures , act upon keystroke events.
        """
        row = event.GetRow()
        col = event.GetCol()
        
        
        print row, col
        
        import PlotFrame
        import perfInd_Plot
        
        if col <= 0 or col > len(self.plot_data.activeAssessorsList): 
            print "no grid plot"
            return
        
        plotted = False
        assessor = self.plot_data.activeAssessorsList[col-1]
        cell_0 = self.grid.GetCellValue(row, 0)
        
        if cell_0 == u"AGR prod":            
                perfInd_Plot.cv_AGR_prod(self.s_data, self.plot_data, assessor)
                plotted = True
        elif cell_0  == u"AGR att":
                perfInd_Plot.cv_AGR_att(self.s_data, self.plot_data, assessor)
                plotted = True
        elif cell_0 == u"REP prod":
                perfInd_Plot.cv_REP_prod(self.s_data, self.plot_data, assessor)
                plotted = True                
        elif cell_0 == u"REP att":
                perfInd_Plot.cv_REP_att(self.s_data, self.plot_data, assessor)
                plotted = True
        
        if plotted:
            self.numberOfWindow += 1   
            _title = {"fig":"Fig. " + str(self.numberOfWindow), "plot":self.plotType}                        
            self.figureList.append(PlotFrame.PlotFrame(None, _title, self.s_data, self.plot_data, self))
            if self.figureList[len(self.figureList)-1] != None:
                self.figureList[len(self.figureList)-1].Show()


    def OnFrameClosing(self, event): 
        for frame in self.figureList:
            try:
                frame.Close()
            except:
                print "Dead frame"
        self.Hide()                
    


class DataGrid(gridlib.PyGridTableBase):
    """
    Grid content handling. Custom PyGridTableBase type.
    """
    def __init__(self, results):
        gridlib.GridTableBase.__init__(self)

        #parametres
        ##        self.sampList = sampleList
        ##        self.assList = assessorList
        ##        self.repList = replicateList
        ##        self.attList = attributeList
        ##        self.sparseMatrix = matrix
        print 'Do i crash here?'
        #find longest array in results
        max_col = 0
        for row in results:
            col_length = len(row)
            if max_col < col_length:
                max_col = col_length
        self.cols = max_col


        #data grid initialization
        self.data = []
        self.col_lables = []
        for i in range(1, self.cols+1): self.col_lables.append(str(i))

        #filling data grid
        j = 0
        for row in results:
            self.data.append(row)
            #complete self.data, so there will be no "empty" cells
            for i in range(len(row), self.cols):
                self.data[j].append('')
            j += 1



    def GetNumberRows(self):
        return len(self.data)


    def GetNumberCols(self):
        return self.cols


    def IsEmptyCell(self, row, col):
        ##        try:
        ##            return not self.data[row][col]
        ##        except IndexError:
        ##            return True
        return False



    def GetValue(self, row, col):
        ##try:
            return self.data[row][col]
        ##except IndexError:
        ##    return ''

    def GetColLabelValue(self, col):
        return self.col_lables[col]


    def SetValue(self, row, col, value):
        print "Cannot change value at (" + str(row) + "," + str(col) + ")!"
        ##        try:
        ##            self.data[row][col] = value
        ##        except IndexError:
        ##            # add a new row
        ##            self.data.append([''] * self.GetNumberCols())
        ##            self.SetValue(row, col, value)
        ##            # tell the grid we've added a row
        ##            msg = gridlib.GridTableMessage(self,            # The table
        ##                    gridlib.GRIDTABLE_NOTIFY_ROWS_APPENDED, # what we did to it
        ##                    1                                       # how many
        ##                    )
        ##            self.GetView().ProcessTableMessage(msg)

    def SetColLables(self, values):
        self.col_lables = values


class DataGridSheet(gridlib.Grid):
    """
    Grid GUI and copy handling.
    """
    def __init__(self, parent):
        gridlib.Grid.__init__(self, parent, -1)

        #self._selected = None           # Init range currently selected

        #self.Bind(gridlib.EVT_GRID_RANGE_SELECT, self.OnRangeSelect)

    def OnRangeSelect(self, event):
        """ Track which cells are selected so that copy/paste behavior can be implemented """
        # If a single cell is selected, then Selecting() returns False (0)
        # and range coords are entire grid.  In this case cancel previous selection.
        # If more than one cell is selected, then Selecting() is True (1)
        # and range accurately reflects selected cells.  Save them.
        # If more cells are added to a selection, selecting remains True (1)
        self._selected = None
        if event.Selecting():
            self._selected = ((event.GetTopRow(), event.GetLeftCol()),
                              (event.GetBottomRow(), event.GetRightCol()))
        event.Skip()



    def getSelections(self):
        x1 = -1
        y1 = -1
        x2 = self.GetNumberCols()
        y2 = self.GetNumberRows()
        found_x1 = False
        found_y1 = False

        row_ind = 0; col_ind = 0
        while(row_ind < y2):
            while(col_ind < x2):
                if not found_x1:
                    if self.IsInSelection(row_ind, col_ind):
                        x1 = col_ind; found_x1 = True;
                else:
                    if not self.IsInSelection(row_ind, col_ind):
                        x2 = col_ind;
                col_ind += 1
            if found_x1:
                if not found_y1:
                    if self.IsInSelection(row_ind, x1):
                        y1 = row_ind; found_y1 = True;
                else:
                    if not self.IsInSelection(row_ind, x1):
                        y2 = row_ind;
            elif col_ind == x2: col_ind = 0
            row_ind += 1
        x2 -= 1; y2 -= 1
        return (x1, x2, y1, y2)


    def set_color_on_pos(self, positions, color=None):
        if color == None: color = wx.RED

        for pos in positions:
            self.SetCellTextColour(pos[0], pos[1], color)


    def Copy(self):
        """ Copy the currently selected cells to the clipboard """
        # TODO: raise an error when there are no cells selected?
        selections = self.getSelections()
        if selections[0] == -1 or selections[2] == -1:
            print "no selection"; return
        else: print selections

        #if self._selected == None: return
        #((r1, c1), (r2, c2)) = self._selected

        # Build a string to put on the clipboard
        # (Is there a faster way to do this in Python?)
        crlf = chr(13) + chr(10)
        tab = chr(9)
        s = ""

        c1 = selections[0]
        c2 = selections[1]
        r1 = selections[2]
        r2 = selections[3]

        for row in range(r1, r2+1):
            for col in range(c1, c2+1):
                s += self.GetCellValue(row, col)
                s += tab
            #s += self.GetCellValue(row, c2)
            s += crlf

        # Put the string on the clipboard
        if wx.TheClipboard.Open():
            wx.TheClipboard.Clear()
            wx.TheClipboard.SetData(wx.TextDataObject(s))
            wx.TheClipboard.Close()

