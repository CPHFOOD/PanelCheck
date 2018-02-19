#!/usr/bin/env python

import wx, time
import wx.lib.buttons as buttons

from PlotPanel import *
from PanelCheck_Tools import *

#import wx.lib.dialogs
import os, sys
import matplotlib
#matplotlib.use('WXAgg')

#from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg
from matplotlib.ticker import FixedLocator
from matplotlib.artist import Artist
#from matplotlib.widgets import RectangleSelector
from matplotlib.backend_bases import NavigationToolbar2, LocationEvent, MouseEvent
#from matplotlib.legend import Legend
#from matplotlib.backends.backend_agg import FigureCanvasAgg
#from matplotlib.backends.backend_gtkagg import FigureCanvasGTKAgg as FigureCanvas
#import gtk

#matplotlib.use('WX')
#from matplotlib.backends.backend_wx import FigureCanvasWx as FigureCanvas

#from matplotlib.figure import Figure
#from matplotlib.numerix.mlab import rand




#for custom matplotlib drawing
#from matplotlib.artist import Artist
#from matplotlib.patches import Patch, Rectangle, Circle, bbox_artist, draw_bbox
#from matplotlib.font_manager import FontProperties
#from matplotlib.transforms import Bbox, Point, Value, get_bbox_transform, bbox_all,\
#     unit_bbox, inverse_transform_bbox, lbwh_to_bbox


from numpy import array

#Plots
from PanelCheck_Plots import *

"""

PLOT TYPE DEFINITIONS:
----------------------
line_samp
line_ass
line_rep

corr

profile

egg

f_ass_general
f_ass_specific
f_att_general
f_att_specific

mse_ass_general
mse_ass_specific
mse_att_general
mse_att_specific

pmse

tucker1

consensus
"""


class PlotFrame(wx.Frame):
    """
    Class PlotFrame, shows a frame with given figure and axes.
    """
    def __init__(self, parent, fig_title, s_data, plot_data, mother):
        """
        Init method for class PlotFrame. Creates all gui items and handles
        frame events. And shows the figure canvas.

        @version: 1.0
        @since: 01.06.2005


        @type frameName: string
        @param frameName: Name of the new PlotFrame

        @type fig: canvas
        @param fig: The main figure to be drawn

        @type ax: object
        @param ax: Axes containing all plot information

        #datasets:
        #pointAndLabelList = datasets[0]
        #rawData = datasets[1]
        #results = datasets[2]
        #plotConfig = datasets[3]

        @type sampleList:     list
        @param sampleList:    Complete list of ALL samples

        @type assessorList:     list
        @param assessorList:    Complete list of ALL assessors

        @type replicateList:    list
        @param replicateList:   Complete list of ALL replicates

        @type attributeList:    list
        @param attributeList:   Complete list of ALL attributes

        @type pointAndLabelList: list
        @param pointAndLabelList: List of all points with labels

        @type results: list
        @param results: List of results

        @type plotConfig: list
        @param results: List of special configurations for the PlotFrame

            plotConfig[0] = type of plot [0,1,2,...] (For later changes, give a number for each different type of plotting)
            plotConfig[1] = which type of print label method to use
            plotConfig[2] = can be custom epsilon value for example, this is not chosen yet
            plotConfig[3] = settings ,plotConfig[4] = more settings etc.


        @author: Henning Risvik
        @organization: Matforsk - Norwegian Food Research Institute
        """
        # frame initilization
        frame_id = wx.NewId()
        _title = fig_title["fig"] + ": " + fig_title["plot"] + " (" + s_data.abspath + ")"
        wx.Frame.__init__(self, parent, frame_id, _title, (-1,-1), (-1,-1))
        self.fig_title = fig_title

        # list parametres
        self.s_data = s_data

        self.plot_data = plot_data
        self.active_ass = self.plot_data.activeAssessorsList
        self.active_att = self.plot_data.activeAttributesList
        self.active_samp = self.plot_data.activeSamplesList
        self.overview_plot = self.plot_data.overview_plot

        self.mother = mother
        
        self.disable_cursor_link = False
        if "disable_cursor_link" in plot_data.special_opts:
            self.disable_cursor_link = plot_data.special_opts["disable_cursor_link"]



        self.plot_panel_id = wx.NewId()
        self.plot_panel = PlotPanel(self, id=self.plot_panel_id, figure=self.plot_data.fig, overview_plot=self.overview_plot)

        #self.plot_panel.canvas.Bind(wx.EVT_MOTION, self.on_panel_motion)
        self.plot_panel.canvas.Bind(wx.EVT_LEFT_DCLICK, self.on_panel_left_double_click)
        self.plot_panel.canvas.Bind(wx.EVT_KEY_DOWN, self.on_key_event)

        #self.plot_panel.canvas.Bind(wx.EVT_LEFT_DOWN, self.on_panel_left_click) # press_event
        #self.plot_panel.canvas.Bind(wx.EVT_LEFT_UP, self.on_panel_left_release) # release_event

        #print self.plot_panel.canvas.bitmap
        self.plot_panel.subplot = self.plot_data.ax
        self.plot_panel.canvas.mpl_connect('motion_notify_event', self.mouse_move)
        self.plot_panel.canvas.mpl_connect('button_press_event', self.mouse_click)
        self.plot_panel.canvas.mpl_connect('button_release_event', self.mouse_release)
        #self.plot_panel.canvas.mpl_connect('key_press_event', self.on_key_event) # for CTRL+C, copy

        print self.plot_panel.canvas.GetId()


        self.nav_tools = NavigationToolbar2Wx(self.plot_panel.canvas)


        self.gridFrameShowingRawData = False
        self.gridFrameShowingNumericalResults = False
        self.summaryFrameShowing = False
        self.tooltipShowing = False
        self.toolTipText = ""
        self.dclick_data = None
        self.pc_ctrl_on = False
        self.cursor_set = False
        self.mouse_down = False

        self.num_res_changed = False
        self.raw_data_changed = False
        self.summary_changed = False


        # Settings for Mousepointing and Labeling:
        self.labeling_type = self.plot_data.point_lables_type
        # 0, using: printLabelIfCorrectPoint() method
        # 1, using: printLabelIfCorrectLine() method


        #Calculation of epsilon for mousepoint info
        xLims = self.plot_data.ax.get_xlim()
        yLims = self.plot_data.ax.get_ylim()
        self.original_xLims = xLims
        self.original_yLims = yLims
        self.epsilonX = -1*(-1*xLims[1]-(-1*xLims[0]))*0.0065 #0.65% of x-edge length
        self.epsilonY = -1*(-1*yLims[1]-(-1*yLims[0]))*0.0095 #0.95% of y-edge length


        self.points_labels = self.plot_data.point_lables
        self.rawData = self.plot_data.raw_data
        self.results = self.plot_data.numeric_data
        self.plot_type = self.plot_data.plot_type
        #self.plotter = self.set_plotter(self.plot_type)
        
        print "plot type: " + self.plot_type


        self.lsd_plot = False
        self.lsd_line_selected = -1
        self.lsd_ydiff = 0; self.lsd_ylength = 1
        if self.plot_type == "mm_anova_lsd_2way1rep" or self.plot_type == "mm_anova_lsd_2way" or self.plot_type == "mm_anova_lsd_3way":
            self.lsd_plot = True
        if self.plot_type == "manhattan_ass" or self.plot_type == "manhattan_att":
            self.epsilonX = 0.45
            self.epsilonY = 0.45

        # setting parameters for special configurations
        if self.plot_type == "tucker1": # tucker1 has special configuration for plot.
            #for Tucker-1 plotConfig[2] is used as PCA mode selection and plotConfig[3] for max number of PCs
            self.PCAmode = self.plot_data.selection
            self.maxPCs = self.plot_data.max_PCs
        if self.plot_type == "consensus": # consensus has special configuration for plot.
            #for Consensus plotConfig[2] is used as tab selection
            self.average_mode = self.plot_data.selection
            self.maxPCs = self.plot_data.max_PCs
        if self.plot_type == "statis_consensus": # consensus has special configuration for plot.
            #for Consensus plotConfig[2] is used as tab selection
            self.statis_mode = self.plot_data.selection
            self.maxPCs = self.plot_data.max_PCs

        if self.labeling_type == 1:
            # PlotFrame has special configuration

            # setting labeling type to be used
            # 0, using: printLabelIfCorrectPoint() method
            # 1, using: printLabelIfCorrectLine() method

            # recalculate epsilon x:
            if self.plot_type == "mm_anova_f_2way1rep" or self.plot_type == "mm_anova_f_2way" or self.plot_type == "mm_anova_f_3way" or self.plot_type == "mean_std_att" or self.plot_type == "mean_std_ass":
                self.epsilonX = plot_data.point_label_line_width
            else:
                self.epsilonX = -1*(-1*xLims[1]-(-1*xLims[0]))*0.0025 #0.25% of x-edge length



        print self.epsilonX
        print self.epsilonY




        #setting the icon for frame
        pathname = os.path.dirname(sys.argv[0])
        self.progPath = os.path.abspath(pathname).decode(sys.getfilesystemencoding())
        self.icon = wx.Icon(self.progPath + u"/fig.ico", wx.BITMAP_TYPE_ICO)
        self.SetIcon(self.icon)


        #gui elements
        if self.plot_type == "tucker1" or self.plot_type == "consensus" or self.plot_type == "statis_consensus":
            self.pc_ctrl_on = True
            self.pc_x_index = 0; self.pc_y_index = 1;
        self.button_panel = wx.Panel(self, id = -1)


        #button initialization
        butt_print = wx.NewId()
        butt_print_setup = wx.NewId()
        butt_copy = wx.NewId()
        butt_save = wx.NewId()

        butt_zoom_reset_id = wx.NewId()
        butt_zoom_id = wx.NewId()
        butt_pan_id = wx.NewId()

        butt_sum = wx.NewId()
        butt_rawData = wx.NewId()
        butt_numResult = wx.NewId()

        buttUp_id = wx.NewId(); buttDown_id = wx.NewId()
        buttReset_id = wx.NewId()
        buttLeft_id = wx.NewId(); buttRight_id = wx.NewId()

        buttPrevPlot_id = wx.NewId(); buttNextPlot_id = wx.NewId()
        butt_close = wx.NewId()



        #self.button_print = wx.Button(self.button_panel, butt_print, "Print")
            #self.button_save = wx.Button(self.button_panel, butt_save, "Save")
        self.button_print = wx.BitmapButton(bitmap=wx.Bitmap(self.progPath + u'/gfx/_ctrl_print.gif', wx.BITMAP_TYPE_GIF),
                  parent=self.button_panel, size=wx.Size(24, 24),
                  style=wx.BU_AUTODRAW, id=butt_print)
        self.button_print.SetToolTip(u'Print Image')

        self.button_print_setup = wx.BitmapButton(bitmap=wx.Bitmap(self.progPath + u'/gfx/_ctrl_print_setup.gif', wx.BITMAP_TYPE_GIF),
                  parent=self.button_panel, size=wx.Size(24, 24),
                  style=wx.BU_AUTODRAW, id=butt_print_setup)
        self.button_print_setup.SetToolTip(u'Print Setup')

        self.button_copy_clip = wx.BitmapButton(bitmap=wx.Bitmap(self.progPath + u'/gfx/_ctrl_copy.gif', wx.BITMAP_TYPE_GIF),
                  parent=self.button_panel, size=wx.Size(24, 24),
                  style=wx.BU_AUTODRAW, id=butt_copy)
        self.button_copy_clip.SetToolTip(u'Copy Image to Clipboard (CTRL+C)')
        self.button_save = wx.BitmapButton(bitmap=wx.Bitmap(self.progPath + u'/gfx/_ctrl_save.gif', wx.BITMAP_TYPE_GIF),
                  parent=self.button_panel, size=wx.Size(24, 24),
                  style=wx.BU_AUTODRAW, id=butt_save)
        self.button_save.SetToolTip(u'Save Image')

        self.butt_zoom_reset = wx.BitmapButton(bitmap=wx.Bitmap(self.progPath + u'/gfx/_nav_home.gif', wx.BITMAP_TYPE_GIF),
                  name=u'butt_zoom_reset', parent=self.button_panel, size=wx.Size(24, 24),
                  style=wx.BU_AUTODRAW, id=butt_zoom_reset_id)
        self.butt_zoom_reset.SetToolTip(u'Reset Axes')

        self.butt_zoom = buttons.GenBitmapToggleButton(parent=self.button_panel, id=butt_zoom_id,
                  bitmap=wx.Bitmap(self.progPath + u'/gfx/_nav_zoom.gif', wx.BITMAP_TYPE_GIF), size=wx.Size(24, 24))
        self.butt_zoom.SetToolTip(u'Rectangle Zoom')


        self.butt_pan = buttons.GenBitmapToggleButton(parent=self.button_panel, id=butt_pan_id,
                  bitmap=wx.Bitmap(self.progPath + u'/gfx/_nav_pan.gif', wx.BITMAP_TYPE_GIF), size=wx.Size(24, 24))
        self.butt_pan.SetToolTip(u'Pan Axes')

        self.button_summ = wx.Button(self.button_panel, butt_sum, "Summary")
        self.button_raw = wx.Button(self.button_panel, butt_rawData, "Raw Data")
        self.button_res = wx.Button(self.button_panel, butt_numResult, "Numerical Results")
        #self.button_close = wx.BitmapButton(bitmap=wx.Bitmap(self.progPath + u'/gfx/_ctrl_close.gif', wx.BITMAP_TYPE_GIF),
        #          name=u'butt_zoom_reset', parent=self.button_panel, size=wx.Size(24, 24),
        #          style=wx.BU_AUTODRAW, id=butt_close)
        #self.button_close.SetToolTipString(u'Close')

        if self.pc_ctrl_on:

            self.buttUp = wx.BitmapButton(bitmap=wx.Bitmap(self.progPath + u'/gfx/_pc_pointer_up.gif', wx.BITMAP_TYPE_GIF),
                  name=u'buttUp', parent=self.button_panel, size=wx.Size(24, 24),
                  style=wx.BU_AUTODRAW, id=buttUp_id)
            self.buttUp.SetToolTip(u'Next PC on vertical-axis')

            self.buttDown = wx.BitmapButton(bitmap=wx.Bitmap(self.progPath + u'/gfx/_pc_pointer_down.gif', wx.BITMAP_TYPE_GIF),
                  name=u'buttDown', parent=self.button_panel, size=wx.Size(24, 24),
                  style=wx.BU_AUTODRAW, id=buttDown_id)
            self.buttDown.SetToolTip(u'Previous PC on vertical-axis')

            self.buttReset = wx.BitmapButton(bitmap=wx.Bitmap(self.progPath + u'/gfx/_pc_circle.gif', wx.BITMAP_TYPE_GIF),
                  name=u'buttReset', parent=self.button_panel,size=wx.Size(24, 24),
                  style=wx.BU_AUTODRAW, id=buttReset_id)
            self.buttReset.SetToolTip(u'Reset PC setting')

            self.buttLeft = wx.BitmapButton(bitmap=wx.Bitmap(self.progPath + u'/gfx/_pc_pointer_left.gif', wx.BITMAP_TYPE_GIF),
                  name=u'buttLeft', parent=self.button_panel, size=wx.Size(24, 24),
                  style=wx.BU_AUTODRAW, id=buttLeft_id)
            self.buttLeft.SetToolTip(u'Previous PC on horizontal-axis')

            self.buttRight = wx.BitmapButton(bitmap=wx.Bitmap(self.progPath + u'/gfx/_pc_pointer_right.gif', wx.BITMAP_TYPE_GIF),
                  name=u'buttRight', parent=self.button_panel, size=wx.Size(24, 24),
                  style=wx.BU_AUTODRAW, id=buttRight_id)
            self.buttRight.SetToolTip(u'Next PC on horizontal-axis')


        self.buttPrevPlot = wx.Button(self.button_panel, buttPrevPlot_id, "<< Prev. Plot")
        self.buttNextPlot = wx.Button(self.button_panel, buttNextPlot_id, "Next Plot >>")
        self.button_close = wx.Button(self.button_panel, butt_close, "Close")


        #sizer initialization
        self.box = wx.BoxSizer(wx.VERTICAL) #main
        self.sizer_inner = wx.BoxSizer(wx.HORIZONTAL)
        self.sizer_PC_ctrl = wx.BoxSizer(wx.HORIZONTAL)

        self.dc = wx.ClientDC(self.plot_panel.canvas)
        self.p = None



        # add to sizer
        self.sizer_inner.Add(self.button_print, 0, wx.EXPAND)
        self.sizer_inner.Add(self.button_print_setup, 0, wx.EXPAND)
        self.sizer_inner.Add(self.button_copy_clip, 0, wx.EXPAND)
        self.sizer_inner.Add(self.button_save, 0, wx.EXPAND)

        self.sizer_inner.Add(self.butt_zoom_reset, 0, wx.EXPAND)
        self.sizer_inner.Add(self.butt_zoom, 0, wx.EXPAND)
        self.sizer_inner.Add(self.butt_pan, 0, wx.EXPAND)
        self.sizer_inner.Add(self.button_summ, 0, wx.EXPAND)
        self.sizer_inner.Add(self.button_raw, 0, wx.EXPAND)
        self.sizer_inner.Add(self.button_res, 0, wx.EXPAND)

        #adding gui items
        if self.pc_ctrl_on:
            self.sizer_PC_ctrl.Add(self.buttUp, 0, wx.FIXED_MINSIZE, 0)
            self.sizer_PC_ctrl.Add(self.buttDown, 0, wx.FIXED_MINSIZE, 0)
            self.sizer_PC_ctrl.Add(self.buttReset, 0, wx.FIXED_MINSIZE, 0)
            self.sizer_PC_ctrl.Add(self.buttLeft, 0, wx.FIXED_MINSIZE, 0)
            self.sizer_PC_ctrl.Add(self.buttRight, 0, wx.FIXED_MINSIZE, 0)



        if self.pc_ctrl_on:
            self.sizer_inner.Add(self.sizer_PC_ctrl, 0, wx.EXPAND)

        self.sizer_inner.Add(self.buttPrevPlot, 1, wx.EXPAND)
        self.sizer_inner.Add(self.buttNextPlot, 1, wx.EXPAND)
        self.sizer_inner.Add(self.button_close, 0, wx.EXPAND)

        self.number = 1 # for numbering of under-plots
        if self.overview_plot:
            if self.pc_ctrl_on:
                self.buttUp.Show(False)
                self.buttDown.Show(False)
                self.buttReset.Show(False)
                self.buttLeft.Show(False)
                self.buttRight.Show(False)
            self.button_summ.Show(False)
            self.button_raw.Show(False)
            self.button_res.Show(False)
            self.butt_zoom_reset.Show(False)
            self.butt_zoom.Show(False)
            self.butt_pan.Show(False)
            self.buttPrevPlot.Show(False)
            self.buttNextPlot.Show(False)
            self.sizer_inner.Layout()


        self.button_panel.SetSizer(self.sizer_inner)

        self.box.SetMinSize((500,450))

        self.box.Add(self.plot_panel, 1, wx.GROW)
        self.box.Add(self.button_panel, 0, wx.ALIGN_CENTER|wx.EXPAND)

        self.statusBar = wx.StatusBar(self, -1)
        self.statusBar.SetFieldsCount(1)
        self.SetStatusBar(self.statusBar)

        #event binding
        #EVT_PAINT(self, self.onPaint)
        print self.plot_panel.canvas

        #self.plot_panel.canvas.Bind(wx.EVT_KEY_DOWN, self.onKeyEvent, id=self.plot_panel_id)

        self.Bind(wx.EVT_BUTTON, self.onPrint, id=butt_print)
        self.Bind(wx.EVT_BUTTON, self.onPrintSetup, id=butt_print_setup)
        self.Bind(wx.EVT_BUTTON, self.onClipboard, id=butt_copy)
        self.Bind(wx.EVT_BUTTON, self.onExport, id=butt_save)

        self.Bind(wx.EVT_BUTTON, self.on_zoom_reset, id=butt_zoom_reset_id)
        self.Bind(wx.EVT_BUTTON, self.on_zoom_toggle, id=butt_zoom_id)
        self.Bind(wx.EVT_BUTTON, self.on_pan_toggle, id=butt_pan_id)

        self.Bind(wx.EVT_BUTTON, self.onSummary, id=butt_sum)
        self.Bind(wx.EVT_BUTTON, self.onRawData, id=butt_rawData)
        self.Bind(wx.EVT_BUTTON, self.onNumericalResults, id=butt_numResult)

        if self.pc_ctrl_on:
            self.Bind(wx.EVT_BUTTON, self.nextPC_y, id=buttUp_id)
            self.Bind(wx.EVT_BUTTON, self.prevPC_y, id=buttDown_id)
            self.Bind(wx.EVT_BUTTON, self.resetPC, id=buttReset_id)
            self.Bind(wx.EVT_BUTTON, self.prevPC_x, id=buttLeft_id)
            self.Bind(wx.EVT_BUTTON, self.nextPC_x, id=buttRight_id)
            if self.plot_data.tree_path[0] == u'PCA Explained Variance' or self.plot_data.tree_path[0] == u'Assessor Weights' or self.plot_data.tree_path[0] == u'Spiderweb Plot':
                self.enable_pc_ctrl(False)

        self.Bind(wx.EVT_BUTTON, self.prevPlot, id=buttPrevPlot_id)
        self.Bind(wx.EVT_BUTTON, self.nextPlot, id=buttNextPlot_id)
        self.Bind(wx.EVT_BUTTON, self.onClose, id=butt_close)


        #self.rect_select = RectangleSelector(self.plot_panel.subplot, self.zoom, drawtype='box', useblit=True)
        #self.enable_rs(self.rect_select, False)

        #adjusting sizer
        #self.SetBackgroundColour(wx.Colour(192,192,192))
        self.SetSize((830, 680))
        self.SetSizer(self.box)
        self.cursor_arrow = wx.Cursor(wx.CURSOR_ARROW)
        self.cursor_hand = wx.Cursor(wx.CURSOR_HAND)
        self.cursor_cross = wx.Cursor(wx.CURSOR_CROSS)

        # mouse click point
        self.m_x = 0
        self.m_y = 0
        self.Layout()

    def on_panel_motion(self, evt):
        x = evt.GetX()
        y = self.plot_panel.canvas.figure.bbox.height() - evt.GetY()
        m_event = MouseEvent("motion_notify_event", self.plot_panel.canvas, x, y, guiEvent=evt)
        self.mouse_move(m_event)


    def on_panel_left_double_click(self, evt):

        if self.plot_type == "tucker1" or \
           self.plot_type == "statis_consensus" or \
           self.plot_type == "pmse" or \
           self.plot_type == "mm_anova_f_3way" or self.plot_type == "mm_anova_f_2way" or self.plot_type == "mm_anova_f_2way1rep" or \
           self.plot_type == "consensus" or \
           self.plot_type == "corr":


            if self.dclick_data != None:
                if self.plot_type == "pmse":
                    plotter = self.get_plot_method("corr")
                    tree_path = [self.plot_data.activeAssessorsList[self.dclick_data[0]], self.plot_data.activeAttributesList[self.dclick_data[1]]]
                    plot_data = PlotData(self.active_ass, self.active_att, self.active_samp, tree_path, self.plot_data.view_grid, self.plot_data.view_legend)
                    plot_data.set_limits(self.plot_data.limits)
                    plot_data = plotter(self.s_data, plot_data)

                elif self.plot_type == "corr":
                    plotter = self.get_plot_method("line_ass")
                    tree_path = [self.dclick_data[0], self.dclick_data[1]]
                    plot_data = PlotData(self.active_ass, [self.dclick_data[2]], self.active_samp, tree_path, self.plot_data.view_grid, self.plot_data.view_legend)
                    plot_data.special_opts["coloring"] = "samples"
                    plot_data.set_limits(self.plot_data.limits)
                    plot_data = plotter(self.s_data, plot_data)

                elif self.plot_type == "tucker1":
                    new_plot_type = self.plot_data.special_opts["dclick_plot"]
                    plotter = self.get_plot_method(new_plot_type)
                    if new_plot_type == "corr":
                        tree_path = [self.dclick_data[0], self.dclick_data[1]]
                    elif new_plot_type == "line_samp":
                        tree_path = [self.dclick_data[0]]
                    plot_data = PlotData(self.active_ass, self.active_att, self.active_samp, tree_path, self.plot_data.view_grid, self.plot_data.view_legend)
                    plot_data.set_limits(self.plot_data.limits)
                    plot_data = plotter(self.s_data, plot_data)


                elif self.plot_type == "statis_consensus":
                    if self.plot_data.special_opts["interactivity_on"]:
                        new_plot_type = self.plot_data.special_opts["dclick_plot"]
                        plotter = self.get_plot_method(new_plot_type)
                        tree_path = [self.dclick_data[0]]
                        plot_data = PlotData(self.active_ass, self.active_att, self.active_samp, tree_path, self.plot_data.view_grid, self.plot_data.view_legend)
                        plot_data.set_limits(self.plot_data.limits)
                        plot_data = plotter(self.s_data, plot_data)


                elif self.plot_type == "mm_anova_f_3way" or self.plot_type == "mm_anova_f_2way" or self.plot_type == "mm_anova_f_2way1rep":
                    plotter = self.get_plot_method("profile")
                    tree_path = [self.dclick_data[0]]
                    plot_data = CollectionCalcPlotData(self.active_ass, self.active_att, self.active_samp, tree_path, self.plot_data.view_grid, self.plot_data.view_legend)
                    if self.plot_type == "mm_anova_f_3way" or self.plot_type == "mm_anova_f_2way":
                        plot_data.collection_calc_data["p_matr"] = deepcopy(self.plot_data.p_matr)
                    plot_data.set_limits(self.plot_data.limits)
                    plot_data = plotter(self.s_data, plot_data)


                elif self.plot_type == "consensus":
                    if self.plot_data.special_opts["interactivity_on"]:
                        new_plot_type = self.plot_data.special_opts["dclick_plot"]
                        plotter = self.get_plot_method(new_plot_type)
                        if new_plot_type == "line_samp":
                            tree_path = [self.dclick_data[0]]
                        plot_data = PlotData(self.active_ass, self.active_att, self.active_samp, tree_path, self.plot_data.view_grid, self.plot_data.view_legend)
                        plot_data.set_limits(self.plot_data.limits)
                        plot_data = plotter(self.s_data, plot_data)

                fig_tit = deepcopy(self.fig_title)
                fig_tit["fig"] += "." + str(self.number)

                pf = PlotFrame(self, fig_tit, self.s_data, plot_data, self.mother)
                self.number += 1
                pf.Show()
        self.click_action(evt)




    def on_panel_left_click(self, evt):

        print evt.GetEventType()
        #time.sleep(0.2)
        x = evt.GetX()
        y = self.plot_panel.canvas.figure.bbox.height() - evt.GetY()
        m_event = MouseEvent("button_press_event", self.plot_panel.canvas, x, y, guiEvent=evt)
        self.mouse_click(m_event)


    def on_panel_left_release(self, evt):
        #time.sleep(0.2)
        x = evt.GetX()
        y = self.plot_panel.canvas.figure.bbox.height() - evt.GetY()
        m_event = MouseEvent("button_release_event", self.plot_panel.canvas, x, y, guiEvent=evt)
        self.mouse_release(m_event)


    def enable_pc_ctrl(self, show=True):
        buttons = self.sizer_PC_ctrl.GetChildren()
        for butt in buttons:
            butt.Show(show)
        self.button_panel.Layout()
        self.button_panel.Refresh()
        self.button_panel.Update()


    def on_zoom_reset(self, event):
        self.plot_panel.subplot.set_xlim(self.original_xLims[0], self.original_xLims[1])
        self.plot_panel.subplot.set_ylim(self.original_yLims[0], self.original_yLims[1])
        self.recalc_epsilon()
        self.plot_panel.subplot.figure.canvas.draw()



    def on_zoom_toggle(self, event):
        self.nav_tools.zoom(event)
        if self.butt_zoom.GetValue():
            self.butt_pan.SetValue(False)
            self.plot_panel.SetCursor(self.cursor_cross)
        else:
            self.plot_panel.SetCursor(self.cursor_arrow)




    def on_pan_toggle(self, event):
        self.nav_tools.pan(event)
        if self.butt_pan.GetValue():
            self.butt_zoom.SetValue(False)
            self.plot_panel.SetCursor(self.cursor_hand)
        else:
            self.plot_panel.SetCursor(self.cursor_arrow)




    def recalc_epsilon(self):
        if self.plot_type == "manhattan_ass" or self.plot_type == "manhattan_att":
            self.epsilonX = 0.45
            self.epsilonY = 0.45

        elif self.plot_type == "mm_anova_f_3way" or self.plot_type == "mm_anova_f_2way" or self.plot_type == "mm_anova_f_2way1rep" or self.plot_type == "mean_std_att" or self.plot_type == "mean_std_ass":
            self.epsilonX = self.plot_data.point_label_line_width

        else:
            xLims = self.plot_panel.subplot.get_xlim()
            yLims = self.plot_panel.subplot.get_ylim()

            # update mouse-point epsilon:
            if self.labeling_type == 0:
                self.epsilonX = -1*(-1*xLims[1]-(-1*xLims[0]))*0.0065 #0.65% of x-edge length
                self.epsilonY = -1*(-1*yLims[1]-(-1*yLims[0]))*0.0095 #0.95% of y-edge length
            elif self.labeling_type == 1:
                self.epsilonX = -1*(-1*xLims[1]-(-1*xLims[0]))*0.0025 #0.25% of x-edge length


    def onPaint(self, event):
        self.plot_panel.figure.canvas.draw()
        event.Skip()



    def get_plot_method(self, plot_type):
        if plot_type == "line_samp": return SampleLinePlotter

        elif plot_type == "line_ass": return AssessorLinePlotter

        elif plot_type == "line_rep": return ReplicateLinePlotter

        elif plot_type == "mean_std_ass": return RawDataAssessorPlotter

        elif plot_type == "mean_std_att": return RawDataAttributePlotter

        elif plot_type == "corr": return CorrelationPlotter

        elif plot_type == "profile": return profilePlotter

        elif plot_type == "egg": return EggshellPlotter

        elif plot_type == "f_ass": return FPlotter_Assessor_General

        elif plot_type == "f_att": return FPlotter_Attributes_General

        elif plot_type == "mse_ass": return MSEPlotter_Assessor_General

        elif plot_type == "mse_att": return MSEPlotter_Attributes_General

        elif plot_type == "pmse": return pmsePlotter

        elif plot_type == "tucker1": return Tucker1Plotter

        elif plot_type == "consensus": return PCA_plotter


        elif plot_type == "mm_anova_f_2way1rep": return MixModel_ANOVA_Plotter_2way1rep

        elif plot_type == "mm_anova_lsd_2way1rep": return MixModel_ANOVA_LSD_Plotter_2way1rep

        elif plot_type == "mm_anova_f_2way": return MixModel_ANOVA_Plotter_2way

        elif plot_type == "mm_anova_lsd_2way": return MixModel_ANOVA_LSD_Plotter_2way

        elif plot_type == "mm_anova_f_3way": return MixModel_ANOVA_Plotter_3way

        elif plot_type == "mm_anova_lsd_3way": return MixModel_ANOVA_LSD_Plotter_3way


        elif plot_type == "manhattan_ass" or plot_type == "manhattan_att": return ManhattanPlotter
        
        elif plot_type == "perf_ind": return perfindPlotter



    def update_gui(self):
        if self.pc_ctrl_on:
            self.buttUp.Show(True)
            self.buttDown.Show(True)
            self.buttReset.Show(True)
            self.buttLeft.Show(True)
            self.buttRight.Show(True)
        self.button_summ.Show()
        self.button_raw.Show()
        self.button_res.Show()
        self.buttPrevPlot.Show()
        self.buttNextPlot.Show()
        self.sizer_inner.Layout()
        self.overview_plot = False
        self.plot_panel.SetCursor(self.cursor_arrow)


    def set_points_in_ranges(self):
        ind = 1
        for line2d in self.plot_data.lsd_lines:
            ydata = line2d[0].get_ydata()
            set_points_in_range(self.plot_panel.subplot, ydata, ind, self.plot_data.lsd_points)
            ind += 1


    def updateLSD(self, x, y, selected): # selected [1, ..., n]
        line2d = self.plot_data.lsd_lines[selected - 1][0]
        ydata = line2d.get_ydata()
        new_y =  y - self.lsd_ydiff
        new_ydata = array([new_y + self.lsd_ylength, new_y], float)
        line2d.set_ydata(new_ydata)

        set_points_in_range(self.plot_panel.subplot, new_ydata, selected, self.plot_data.lsd_points)

        #self.plot_panel.figure.draw_artist(line2d)
        #self.gui_repaint(drawDC=wx.PaintDC(self))
        self.plot_panel.figure.canvas.draw()
        #self.plot_panel.subplot.draw_artist(line2d)
        #self.plot_panel.figure.canvas.blit(self.plot_panel.subplot.bbox)
        #self.plot_panel.Refresh()
        #self.plot_panel.Update()


    def LSD_select_line(self, x, y):
        selected = -1; ind = 1
        for line2d in self.plot_data.lsd_lines:
            #print line2d
            xdata = line2d[0].get_xdata()
            ydata = line2d[0].get_ydata()
            if xdata[0] < x+self.epsilonX and xdata[0] > x-self.epsilonX:
                if ydata[0] > y and ydata[1] < y:
                    self.lsd_ydiff = y - ydata[1]
                    self.lsd_ylength = ydata[0] - ydata[1]
                    return ind
            ind += 1
        return selected





    def mouse_move(self, event):
        """
        Draw mouse (x,y) information in the statusbar.

        @type event:    object
        @param event:    An event is a structure holding information about an
        event passed to a callback or member function.
        """
        if self.disable_cursor_link: return
        
        
        if event.inaxes is None:
            if self.overview_plot and self.cursor_set:
                self.plot_panel.SetCursor(self.cursor_arrow)
                self.cursor_set = False
            return
        x = event.xdata
        y = event.ydata
        #if not self.overview_plot:
        #    self.plot_panel.canvas.SetFocus()

        self.statusBar.SetStatusText("x=%f  y=%f"% (x, y), 0)

        if self.lsd_plot and self.lsd_line_selected > -1: # case: lsd plot
            if self.m_y != y:
                self.updateLSD(x, y, self.lsd_line_selected)
                #time.sleep(0.02)

        elif not self.overview_plot:
            if self.labeling_type == 0:
                if self.plot_type == "manhattan_ass" or self.plot_type == "manhattan_att":
                    ax = event.inaxes
                    if ax == self.plot_panel.figure.axes[1]: return
                self.printLabelIfCorrectPoint(x, y)
            elif self.labeling_type == 1:
                self.printLabelIfCorrectLine(x, y)
            #self.statusBar.SetStatusText(a.get_label() + "x=%f  y=%f"% (x, y))
        else:
            if not self.cursor_set:
                if self.plot_type == "manhattan_ass" or self.plot_type == "manhattan_att":
                    ax = event.inaxes
                    if ax == self.plot_panel.figure.axes[1] or ax == self.plot_panel.figure.axes[0]: return
                self.plot_panel.SetCursor(self.cursor_hand)
                self.cursor_set = True
            elif self.plot_type == "manhattan_ass" or self.plot_type == "manhattan_att":
                ax = event.inaxes
                if ax == self.plot_panel.figure.axes[1] or ax == self.plot_panel.figure.axes[0]:
                    self.plot_panel.SetCursor(self.cursor_arrow)
                    self.cursor_set = False




    def mouse_click(self, event):
        """
        Draws tooltip information box.
        """
        self.plot_panel.canvas.SetFocus()

        if not self.overview_plot:
            if event.inaxes is None: return
            else:



                if self.lsd_plot:
                    self.m_x = event.xdata
                    self.m_y = event.ydata
                    self.lsd_line_selected = self.LSD_select_line(self.m_x, self.m_y)

                    #print self.lsd_line_selected
                    if self.lsd_line_selected == -1: # none selected
                        self.click_action(event)



                else:
                    self.click_action(event)



        else:
            if self.disable_cursor_link: return
            if event.inaxes is None: return
            ax = event.inaxes
            if self.plot_type == "manhattan_ass" or self.plot_type == "manhattan_att":
                if ax == self.plot_panel.figure.axes[1] or ax == self.plot_panel.figure.axes[0]: return
            #event.guiEvent # actual wx.MouseEvent
            #self.replot(self.plot_type, ax._num)
            #self.update_gui()
            #self.overview_plot = False
            print ax._num
            plot_data = self.newplot(self.plot_type, ax._num)
            plot_data.set_limits(self.plot_data.limits)

            fig_tit = deepcopy(self.fig_title)
            fig_tit["fig"] += "." + str(self.number)

            pf = PlotFrame(self, fig_tit, self.s_data, plot_data, self.mother)
            self.number += 1
            pf.Show();
            """
            Rember to disable this function on line 1128 in backend_wx in matplotlib:
            evt.Skip(false) # or remove line, now event will not be processed any more (left-click resets focus for some reason).
            """



    def click_action(self, event):
        if self.p != None:
            self.plot_panel.canvas.RefreshRect(self.p.rect)
            self.plot_panel.canvas.Update()
        if self.toolTipText != "":
            if self.p != None:
                if self.p.orig_txt != self.toolTipText:
                    point = (event.guiEvent.GetX(), event.guiEvent.GetY())
                    self.p = PointLabel(self.plot_panel, point, self.toolTipText)
                    self.p.render(self.dc)
                    self.p.hiding = False
                elif self.p.hiding:
                    self.p.render(self.dc)
                    self.p.hiding = False
                else:
                    self.plot_panel.canvas.RefreshRect(self.p.rect)
                    self.plot_panel.canvas.Update()
                    self.p.hiding = True
            else:
                point = (event.guiEvent.GetX(), event.guiEvent.GetY())
                self.p = PointLabel(self.plot_panel, point, self.toolTipText)
                self.p.render(self.dc)


    def mouse_release(self, event):
        """
        """
        if self.butt_zoom.GetValue():
            self.recalc_epsilon()
        #if self.lsd_line_selected > -1:
        #    line2d = self.plot_data.lsd_lines[self.lsd_line_selected - 1][0]
        #    line2d.set_animated(False)

        self.lsd_line_selected = -1

        #self.plot_panel.figure.canvas.draw()












        # the printer / clipboard methods are implemented
        # in backend_wx, and so are very simple to use.
    def onPrinterPreview(self,event=None):
        """
        Creates a preview window for how the print will look.
        """
        self.plot_panel.canvas.Printer_Preview(event=event)


    def onPrintSetup(self,event=None):
        """
        Runs os print setup function of figure canvas.
        """
        self.plot_panel.canvas.Printer_Setup2(event=event)


    def onPrint(self,event=None):
        """
        Runs os print function of figure canvas.
        """
        self.plot_panel.figure.text(0.01, 0.01, "PanelCheck", fontdict={'fontname':'Arial Narrow','color': 'black','fontweight':'bold','fontsize':14,'alpha':0.25})
        self.plot_panel.canvas.Printer_Print(event=event)
        del self.plot_panel.figure.texts[-1]


    def onClipboard(self, event=None):
        """
        Copy to clipboard function.
        """

        print self.plot_panel.canvas.bitmap
        bmp_obj = wx.BitmapDataObject()
        bmp_obj.SetBitmap(self.plot_panel.canvas.bitmap)

        wx.TheClipboard.Open()
        wx.TheClipboard.SetData(bmp_obj)
        wx.TheClipboard.Close()
        #bitmap = self.plot_panel.subplot.figure.canvas.bitmap
        #self.plot_panel.canvas.Copy_to_Clipboard(event=event, bmp=bitmap)
        #self.plot_panel.canvas.Copy_to_Clipboard(event=event)



    def on_key_event(self,event=None):
        """
        Captures , act upon keystroke events.
        """
        #print "KeyEvent"
        if event == None: return
        key = event.GetKeyCode()
        #print key
        #print chr(key)
        if (key < wx.WXK_SPACE or key > 255):  return

        if (event.ControlDown() and chr(key)=='C'): # Ctrl-C
            print "ctrl+c"
            self.onClipboard(event=event)



    def onExport(self,event=None):
        """
        Save figure image to file.
        """
        file_choices = "PNG (*.png)|*.png|" \
                       "RAW (*.raw)|*.raw|" \
                       "PS (*.ps)|*.ps|" \
                       "EPS (*.eps)|*.eps|" \
                       "BMP (*.bmp)|*.bmp"

        if self.mother.image_save_path == "": thisdir  = os.getcwd()
        else: thisdir = self.mother.image_save_path

        dlg = wx.FileDialog(self, message='Save Plot Figure as...',
                            defaultDir = thisdir, defaultFile='plot',
                            wildcard=file_choices, style=wx.SAVE)

        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPath()
            filedir = split_path(path)[0]
            self.mother.image_save_path = filedir
            #path = str(path)
            self.plot_panel.figure.text(0.01, 0.01, "PanelCheck", fontdict={'fontname':'Arial Narrow','color': 'black','fontweight':'bold','fontsize':14,'alpha':0.25})
            self.plot_panel.canvas.print_figure(path.encode(codec) ,dpi=150)
            if (path.find(thisdir) ==  0):
                path = path[len(thisdir)+1:]
            print 'Saved plot to %s' % path.encode(codec)
            print 'in ' + self.mother.image_save_path.encode(codec)
            del self.plot_panel.figure.texts[-1]
        dlg.Destroy()



    def onSummary(self, event=None):
        """
        Shows message dialog window with information about assessors, samples,
        replicates and attributes.
        """


        if not self.summaryFrameShowing or self.summary_changed == True:
            self.summFrame = SummaryFrame(self, self.get_summary_text(self.plot_type))
            self.summary_changed = False
        else:
            self.summFrame.Raise()

        self.summFrame.Show()
        self.summaryFrameShowing = True
        #self.summary_changed == True



    def get_summary_text(self, plot_type):
        """
        Returns summary text. Sometimes to be customized by given plot_type.
        """

        return summaryConstructor(self, self.active_samp, self.active_ass,
                                self.s_data.ReplicateList, self.active_att)



    def printLabelIfCorrectPoint(self, x, y):
        """
        Outputs assessor and its point values on the statusbar.
        Epsilon is calculated according to the axis values.
        Line in self.points_labes is constructed by two points.

        @type x:     float
        @param x:    Cursor x point

        @type y:     float
        @param y:    Cursor y point
        """
        self.toolTipText = ""
        for innerList in self.points_labels:
            if innerList[0] < x+self.epsilonX and innerList[0] > x-self.epsilonX:
                if innerList[1] < y+self.epsilonY and innerList[1] > y-self.epsilonY:
                    self.statusBar.SetStatusText("x=%f  y=%f"% (innerList[0], innerList[1]) + "     " + innerList[2])
                    self.toolTipText = "x=%.3f  y=%.3f"% (innerList[0], innerList[1]) + "\n" + innerList[2]
                    if self.plot_type == "pmse":
                        self.dclick_data = [innerList[3], innerList[4]]
                    elif  self.plot_type == "corr":
                        self.dclick_data = [innerList[3], innerList[4], innerList[5]]
                    elif  self.plot_type == "tucker1":
                        if len(innerList) >= 4:
                            self.dclick_data = innerList[3]
                    elif  self.plot_type == "consensus":
                        if len(innerList) >= 4:
                            self.dclick_data = innerList[3]
                    elif  self.plot_type == "statis_consensus":
                        if len(innerList) >= 4:
                            self.dclick_data = innerList[3]
                    return

        self.dclick_data = None


    def printLabelIfCorrectLine(self, x, y):
        """
        Outputs text and line values on the statusbar.
        Epsilon is calculated according to the axis values.
        All lines are vertical and length is always from lower limit to a given value.

        @type x:     float
        @param x:    Cursor x point

        @type y:     float
        @param y:    Cursor y point
        """
        for innerList in self.points_labels:
            if innerList[0] < x+self.epsilonX and innerList[0] > x-self.epsilonX:
                if innerList[1] > y and y > 0:
                    self.statusBar.SetStatusText("x=%.3f  y=%.3f"% (innerList[0], innerList[1]) + "     " + innerList[2])
                    if self.plot_type == "mm_anova_f_3way" or self.plot_type == "mm_anova_f_2way" or self.plot_type == "mm_anova_f_2way1rep":
                        self.dclick_data = [innerList[3]]
                    return

        self.dclick_data = None


    def onClose(self, event=None):
        self.Close()



    def onRawData(self, event=None):
        if not self.gridFrameShowingRawData or self.raw_data_changed == True:
            _title = self.fig_title["fig"] + ": " + self.fig_title["plot"] + " (" + self.s_data.abspath + ")"
            self.gridFrame_raw = GridFrame(self, _title, self.rawData)
            self.gridFrame_raw.grid.set_color_on_pos(self.plot_data.raw_data_mv_pos)
            print self.plot_data.raw_data_mv_pos
            self.raw_data_changed = False
        else:
            self.gridFrame_raw.Raise()

        self.gridFrame_raw.Show()
        self.gridFrameShowingRawData = True
        #self.gridFrameShowingNumericalResults = False



    def onNumericalResults(self, event=None):
        if not self.gridFrameShowingNumericalResults or self.num_res_changed == True:
            plotType = self.plot_data.tree_path[0]
            if plotType == u'AGR prod' or plotType == u'AGR att' or plotType == u'REP prod' or plotType == u'REP att':
                print "GridFramePerfInd"
                _title = self.fig_title["fig"] + ": " + self.fig_title["plot"] + " (" + self.s_data.abspath + ")"
                self.gridFrame_num = GridFramePerfInd(self, _title, self.results, self.s_data, self.plot_data, config=self.plot_data.numeric_data_config)
                self.num_res_changed = False           
            else:
                _title = self.fig_title["fig"] + ": " + self.fig_title["plot"] + " (" + self.s_data.abspath + ")"
                self.gridFrame_num = GridFrame(self, _title, self.results, config=self.plot_data.numeric_data_config)
                self.num_res_changed = False
        else:
            self.gridFrame_num.Raise()

        self.gridFrame_num.Show()
        self.gridFrameShowingNumericalResults = True
        #self.gridFrameShowingRawData = False



    def prevPC_y(self, event=None):
        self.pc_y_index -= 1
        if self.pc_y_index < 0:
            self.pc_y_index = self.maxPCs-1
        self.replot_pc(self.plot_type, self.pc_x_index, self.pc_y_index)

    def nextPC_y(self, event=None):
        self.pc_y_index += 1
        if self.pc_y_index > self.maxPCs-1:
            self.pc_y_index = 0
        self.replot_pc(self.plot_type, self.pc_x_index, self.pc_y_index)

    def resetPC(self, event=None):
        self.pc_x_index = 0; self.pc_y_index = 1
        self.replot_pc(self.plot_type, self.pc_x_index, self.pc_y_index)

    def prevPC_x(self, event=None):
        self.pc_x_index -= 1
        if self.pc_x_index < 0:
            self.pc_x_index = self.maxPCs-1
        self.replot_pc(self.plot_type, self.pc_x_index, self.pc_y_index)

    def nextPC_x(self, event=None):
        self.pc_x_index += 1
        if self.pc_x_index > self.maxPCs-1:
            self.pc_x_index = 0
        self.replot_pc(self.plot_type, self.pc_x_index, self.pc_y_index)



    def update_variables(self):
        #self.fig = fig
        #self.fig.add_axes(self.axes)
        #self.canvas= FigureCanvasWx(self, -1, self.fig)
        #self.fig.set_canvas(self.canvas)
        #self.canvas.figure = self.fig
        #self.canvas.__init__(self, -1, self.fig)
        #self.fig.draw_artist(self.axes)
        #self.canvas.mpl_connect('motion_notify_event', self.mouse_move)
        #self.canvas.mpl_connect('button_press_event', self.mouse_click)

        #draw()

        self.points_labels = self.plot_data.point_lables
        self.rawData = self.plot_data.raw_data
        self.results = self.plot_data.numeric_data

        self.num_res_changed = True
        self.raw_data_changed = True
        self.summary_changed = True



    def get_pos(self, value, check_list, index):
        i = 0; j = i
        for element in check_list:
            if value == element: j = i; break
            i += 1
        if j == len(check_list)-1 and index == 1: return 0
        else: return j+index



    def find_pos(self, value, list):
        i = 0
        for element in list:
            if value == element: return i
            i += 1



    def create_list_from_dict(self, dict, list):
        """
        Not general function!

        Returns a list of ex: ActiveAssessors from ActiveAssessors_Dict
        """
        actives = []
        for element in list:
            if dict.has_key(element): actives.append(element)
        return actives



    def get_tree_path(self, plot_type, index, index_is_pos=False):
        """
        Creates tree_path for plot given by index

        plot_type: str

        index: int   -1 (Previous Plot)
                      1 (Next Plot)

        Returns tree_path and position
        """
        tree_path = []
        if plot_type == "line_samp":
            if index_is_pos: i = index
            else: i = self.get_pos(self.plot_data.tree_path[0], self.s_data.SampleList, index)
            tree_path.append(self.s_data.SampleList[i])

        elif plot_type == "line_ass":
            if index_is_pos: i = index
            else:i = self.get_pos(self.plot_data.tree_path[1], self.active_ass, index)
            tree_path.append(self.plot_data.tree_path[0])
            tree_path.append(self.active_ass[i])

        elif plot_type == "line_rep":
            if index_is_pos: i = index
            else: i = self.get_pos(self.plot_data.tree_path[2], self.s_data.ReplicateList, index)
            tree_path.append(self.plot_data.tree_path[0])
            tree_path.append(self.plot_data.tree_path[1])
            tree_path.append(self.s_data.ReplicateList[i])

        elif plot_type == "mean_std_ass" or plot_type == "mean_std_att":
            roller_list = self.active_ass[:]
            roller_list.extend(self.active_att[:])
            if index_is_pos: i = index
            else: i = self.get_pos(self.plot_data.tree_path[0], roller_list, index)
            tree_path.append(roller_list[i])
            # set correct plot type:
            if tree_path[0] in self.active_ass: self.plot_type = "mean_std_ass"; self.plot_data.plot_type = "mean_std_ass"
            else: self.plot_type = "mean_std_att"; self.plot_data.plot_type = "mean_std_att"

        elif plot_type == "corr":
            if self.plot_data.tree_path[1] in self.s_data.AttributeList:
                if index_is_pos: i = index
                else: i = self.get_pos(self.plot_data.tree_path[1], self.s_data.AttributeList, index)
                tree_path.append(self.plot_data.tree_path[0])
                tree_path.append(self.s_data.AttributeList[i])
            else:
                if index_is_pos: i = index
                else: i = self.get_pos(self.plot_data.tree_path[1], self.active_ass, index)
                tree_path.append(self.plot_data.tree_path[0])
                tree_path.append(self.active_ass[i])

        elif plot_type == "profile":
            if index_is_pos: i = index
            else: i = self.get_pos(self.plot_data.tree_path[0], self.s_data.AttributeList, index)
            tree_path.append(self.s_data.AttributeList[i])

        elif plot_type == "egg":
            if index_is_pos: i = index
            else: i = self.get_pos(self.plot_data.tree_path[0], self.s_data.AttributeList, index)
            tree_path.append(self.s_data.AttributeList[i])

        elif plot_type == "f_ass":
            actives = self.active_att[:]
            actives.insert(0, "General Plot")
            if index_is_pos: i = index
            else: i = self.get_pos(self.plot_data.tree_path[1], actives, index)
            tree_path.append(self.plot_data.tree_path[0])
            tree_path.append(actives[i])

        elif plot_type == "f_att":
            actives = self.active_ass[:]
            actives.insert(0, "General Plot")
            if index_is_pos: i = index
            else: i = self.get_pos(self.plot_data.tree_path[1], actives, index)
            tree_path.append(self.plot_data.tree_path[0])
            tree_path.append(actives[i])


        elif plot_type == "mse_ass":
            actives =  self.active_att[:]
            actives.insert(0, "General Plot")
            if index_is_pos: i = index
            else: i = self.get_pos(self.plot_data.tree_path[0], actives, index)
            tree_path.append(actives[i])

        elif plot_type == "mse_att":
            actives = self.active_ass[:]
            actives.insert(0, "General Plot")
            if index_is_pos: i = index
            else: i = self.get_pos(self.plot_data.tree_path[0], actives, index)
            tree_path.append(actives[i])

        elif plot_type == "pmse":
            actives = self.active_ass[:]
            actives.extend(self.active_att[:]) # actives now contain active assessors followed by active attributes
            if index_is_pos: i = index
            else: i = self.get_pos(self.plot_data.tree_path[0], actives, index)
            tree_path.append(actives[i])

        elif plot_type == "tucker1":
            actives = ['Common Scores']
            actives.extend(self.active_ass)
            actives.extend(self.active_att) # actives now contain 'Common Scores' and active assessors followed by active attributes
            if index_is_pos: i = index
            else: i = self.get_pos(self.plot_data.tree_path[0], actives, index)
            tree_path.append(actives[i])

        elif plot_type == "consensus":
            _list = [u'PCA Scores', u'PCA Loadings', u'PCA Correlation Loadings', u'Bi-Plot', u'PCA Explained Variance', u'Spiderweb Plot']
            if index_is_pos: i = index
            else: i = self.get_pos(self.plot_data.tree_path[0], _list, index)
            tree_path.append(_list[i])
            if tree_path[0] == u'PCA Explained Variance' or tree_path[0] == u'Spiderweb Plot':
                self.enable_pc_ctrl(False)
            else:
                self.enable_pc_ctrl(True)

        elif plot_type == "statis_consensus":
            _list = [u'PCA Scores', u'PCA Loadings', u'PCA Correlation Loadings', u'Bi-Plot', u'PCA Explained Variance', u'Assessor Weights', u'Spiderweb Plot']
            if index_is_pos: i = index
            else: i = self.get_pos(self.plot_data.tree_path[0], _list, index)
            tree_path.append(_list[i])
            if tree_path[0] == u'PCA Explained Variance' or tree_path[0] == u'Assessor Weights' or tree_path[0] == u'Spiderweb Plot':
                self.enable_pc_ctrl(False)
            else:
                self.enable_pc_ctrl(True)


        elif plot_type == "mm_anova_f_2way1rep":
            _list = [u'F1', u'F2']
            if index_is_pos: i = index
            else: i = self.get_pos(self.plot_data.tree_path[0], _list, index)
            tree_path.append(_list[i])

        elif plot_type == "mm_anova_f_2way":
            _list = [u'F1', u'F2', u'F3']
            if index_is_pos: i = index
            else: i = self.get_pos(self.plot_data.tree_path[0], _list, index)
            tree_path.append(_list[i])

        elif plot_type == "mm_anova_f_3way":
            _list = ['F1', 'F2', 'F2b', 'F3', 'F4', 'F5']
            if index_is_pos: i = index
            else: i = self.get_pos(self.plot_data.tree_path[0], _list, index)
            tree_path.append(_list[i])


        elif plot_type == "mm_anova_f_3way":
            _list = ['F1', 'F2', 'F2b', 'F3', 'F4', 'F5']
            if index_is_pos: i = index
            else: i = self.get_pos(self.plot_data.tree_path[0], _list, index)
            tree_path.append(_list[i])

        elif plot_type == "mm_anova_lsd_2way1rep" or plot_type == "mm_anova_lsd_2way" or plot_type == "mm_anova_lsd_3way":
            _list = ['LSD1', 'LSD2']
            if index_is_pos: i = index
            else: i = self.get_pos(self.plot_data.tree_path[0], _list, index)
            tree_path.append(_list[i])

        elif plot_type == "manhattan_ass":
            actives = self.active_ass[:]
            if index_is_pos: i = index
            else: i = self.get_pos(self.plot_data.tree_path[0], actives, index)
            tree_path.append(actives[i])

        elif plot_type == "manhattan_att":
            actives = self.active_att[:]
            if index_is_pos: i = index
            else: i = self.get_pos(self.plot_data.tree_path[0], actives, index)
            tree_path.append(actives[i])
            
            
        
        elif plot_type == "perf_ind":
            _list = [u'AGR prod', u'AGR att', u'REP prod', u'REP att', u'DIS total', u'DIS panel-1']  
            if index_is_pos: i = index
            else: i = self.get_pos(self.plot_data.tree_path[0], _list, index)   
            tree_path.append(_list[i])
            

        return tree_path, i



    def get_roller_list(self, plot_type, i):
        """
        Creates tree_path for plot (for overview plots)

        plot_type: str

        Returns tree_path
        """
        tree_path = []
        if plot_type == "line_samp":
            tree_path.append(self.s_data.SampleList[i])

        elif plot_type == "line_ass":
            tree_path.append(self.plot_data.tree_path[0])
            tree_path.append(self.active_ass[i])

        elif plot_type == "mean_std_ass":
            tree_path.append(self.active_ass[i])

        elif plot_type == "mean_std_att":
            tree_path.append(self.active_att[i])

        elif plot_type == "corr":
            if self.plot_data.tree_path[1] in self.s_data.AttributeList:
                tree_path.append(self.plot_data.tree_path[0])
                tree_path.append(self.s_data.AttributeList[i])
            else:
                tree_path.append(self.plot_data.tree_path[0])
                tree_path.append(self.active_ass[i])

        elif plot_type == "profile":
            tree_path.append(self.s_data.AttributeList[i])

        elif plot_type == "egg":
            tree_path.append(self.s_data.AttributeList[i])

        elif plot_type == "pmse":
            if self.plot_data.tree_path[0] in self.active_att:
                tree_path.append(self.active_att[i])
            else:
                tree_path.append(self.active_ass[i])

        elif plot_type == "tucker1":
            if self.plot_data.tree_path[0] in self.active_att:
                tree_path.append(self.active_att[i])
            else:
                tree_path.append(self.active_ass[i])




        elif plot_type == "mm_anova_f_2way1rep":
            _list = [u'F1', u'F2']
            tree_path.append(_list[i])

        elif plot_type == "mm_anova_f_2way":
            _list = [u'F1', u'F2', u'F3']
            tree_path.append(_list[i])

        elif plot_type == "mm_anova_f_3way":
            _list = ['F1', 'F2', 'F2b', 'F3', 'F4', 'F5']
            tree_path.append(_list[i])

        elif plot_type == "mm_anova_lsd_2way1rep" or plot_type == "mm_anova_lsd_2way" or plot_type == "mm_anova_lsd_3way":
            _list = ['LSD1', 'LSD2']
            tree_path.append(_list[i])


        #elif plot_type == "mm_anova_fp":
        #    _list = [u'REP*SAMP vs ERROR', u'SAMP*ASS vs ERROR', u'SAMP vs SAMP*ASS', u'SAMP in 3-way mixed model']
        #    tree_path.append(_list[i])

        #elif plot_type == "mm_anova_lsd":
        #    _list = ['Sample*Assessor 95% LSD values', 'Sample*Assessor 95% Bonferroni LSD values', '3-way mixed model 95% LSD values', '3-way mixed model 95% Bonferroni LSD values']
        #    tree_path.append(_list[i])

        elif plot_type == "manhattan_ass":
            tree_path.append(self.active_ass[i])

        elif plot_type == "manhattan_att":
            tree_path.append(self.active_att[i])
        
        elif plot_type == "perf_ind":
            _list = [u'AGR prod', u'AGR att', u'REP prod', u'REP att', u'DIS total', u'DIS panel-1'] 
            tree_path.append(_list[i])
        
        
        return tree_path



    def replot_pc(self, plot_type, pc_x, pc_y):
        if plot_type == "tucker1":
            self.plot_panel.figure.clear()
            self.plot_data = Tucker1Plotter(self.s_data, self.plot_data, selection=self.PCAmode, pc_x=pc_x, pc_y=pc_y)
        elif plot_type == "consensus":
            self.plot_panel.figure.clear()
            self.plot_data = PCA_plotter(self.s_data, self.plot_data, selection=self.average_mode, pc_x=pc_x, pc_y=pc_y)    # 0: PC1, 1: PC2
        elif plot_type == "statis_consensus":
            self.plot_panel.figure.clear()
            self.plot_data = STATIS_PCA_Plotter(self.s_data, self.plot_data, selection=self.statis_mode, pc_x=pc_x, pc_y=pc_y)    # 0: PC1, 1: PC2


        self.plot_panel.subplot = self.plot_data.ax
        self.plot_panel.figure = self.plot_data.fig
        self.update_variables()
        self.plot_panel.canvas = self.plot_data.fig.canvas
        self.plot_panel.subplot.figure.canvas.draw()
        self.original_xLims = self.plot_panel.subplot.get_xlim()
        self.original_yLims = self.plot_panel.subplot.get_ylim()


    def newplot(self, plot_type, index):
        """
        Runs calculation, only for getting new values without changing the canvas.

        plot_type: str

        index: int   -1 (Previous Plot)
                      1 (Next Plot)
        """
        tree_path = self.get_roller_list(plot_type, index)

        plotter = self.get_plot_method(plot_type)
        if plot_type == "mm_anova_f_2way1rep" or plot_type == "mm_anova_lsd_2way1rep" or plot_type == "mm_anova_f_2way" or plot_type == "mm_anova_lsd_2way" or plot_type == "mm_anova_f_3way" or plot_type == "mm_anova_lsd_3way":
            plot_data = MM_ANOVA_PlotData(self.active_ass, self.active_att, self.active_samp, tree_path, self.plot_data.view_grid, self.plot_data.view_legend) # overview_plot = False
            plot_data.sensmixed_data = self.plot_data.sensmixed_data
            plot_data.accepted_active_attributes = self.plot_data.accepted_active_attributes
            if self.plot_type == "mm_anova_f_3way" or self.plot_type == "mm_anova_f_2way":
                plot_data.p_matr = deepcopy(self.plot_data.p_matr)


        elif plot_type == "tucker1" or plot_type == "consensus":
            plot_data = PCA_PlotData(self.active_ass, self.active_att, self.active_samp, tree_path, self.plot_data.view_grid, self.plot_data.view_legend) # overview_plot = False
            plot_data.copy_data(self.plot_data)
            #plot_data.selection = self.plot_data.selection
            #plot_data.max_PCs = self.plot_data.max_PCs
            #plot_data.Scores = self.plot_data.Scores;
            #plot_data.Loadings = self.plot_data.Loadings;
            #plot_data.E = self.plot_data.E
            #plot_data.CorrLoadings = self.plot_data.CorrLoadings
            #plot_data.numeric_data_tucker1matrix = self.plot_data.numeric_data_tucker1matrix
            #plot_data.newActiveAttributesList = self.plot_data.newActiveAttributesList
            #plot_data.raw_data = self.plot_data.raw_data
            plot_data.aspect = self.plot_data.aspect
            #plot_data.p_matr = self.plot_data.p_matr
            return plotter(self.s_data, plot_data, selection=self.plot_data.selection)


        elif plot_type == "pmse":
            plot_data = ANOVA_PlotData(self.active_ass, self.active_att, self.active_samp, tree_path, self.plot_data.view_grid, self.plot_data.view_legend) # overview_plot = False
            plot_data.copy_data(self.plot_data)
            #plot_data.ANOVA_F = self.plot_data.ANOVA_F
            #plot_data.ANOVA_p = self.plot_data.ANOVA_p
            #plot_data.ANOVA_MSE = self.plot_data.ANOVA_MSE
            #plot_data.F_signifcances = self.plot_data.F_signifcances
            #plot_data.raw_data = self.plot_data.raw_data
            #plot_data.numeric_data = self.plot_data.numeric_data
            #plot_data.p_matr = self.plot_data.p_matr


        elif plot_type == "manhattan_ass" or plot_type == "manhattan_att":
            plot_data = CollectionCalcPlotData(self.active_ass, self.active_att, self.active_samp, tree_path, self.plot_data.view_grid, self.plot_data.view_legend) # overview_plot = False
            plot_data.copy_data(self.plot_data)
            #plot_data.collection_calc_data = self.plot_data.collection_calc_data
            plot_data.maxPCs = self.plot_data.maxPCs
            plot_data.selection = self.plot_data.selection


        elif plot_type == "egg" or plot_type == "profile" or plot_type == "mean_std_att" or plot_type == "mean_std_att":
            plot_data = CollectionCalcPlotData(self.active_ass, self.active_att, self.active_samp, tree_path, self.plot_data.view_grid, self.plot_data.view_legend) # overview_plot = False
            plot_data.copy_data(self.plot_data)
            #plot_data.collection_calc_data = self.plot_data.collection_calc_data

        elif plot_type == "perf_ind":
            plot_data = CollectionCalcPlotData(self.active_ass, self.active_att, self.active_samp, tree_path, self.plot_data.view_grid, self.plot_data.view_legend) # overview_plot = False
            plot_data.copy_data(self.plot_data)
            plot_data.special_opts = self.plot_data.special_opts
        
        else:
            plot_data = PlotData(self.active_ass, self.active_att, self.active_samp, tree_path, self.plot_data.view_grid, self.plot_data.view_legend) # overview_plot = False



        plot_data.set_limits(self.plot_data.limits)

        # modify active lists:
        #if plot_type == "line_samp":
        #    plot_data.activeSamplesList = tree_path[:]
        #if plot_type == "egg" or plot_type == "profile":
        #    plot_data.activeAttributesList = tree_path[:]
        #if plot_type == "corr":
        #    if self.plot_data.tree_path[1] in self.s_data.AttributeList:
        #        plot_data.activeAttributesList = [self.s_data.AttributeList[index]]
        #    else:
        #        plot_data.activeAttributesList = [self.plot_data.tree_path[0]]

        if hasattr(self.plot_data, 'aspect'):
            plot_data.aspect = self.plot_data.aspect

        return plotter(self.s_data, plot_data)



    def replot(self, plot_type, index):
        """
        Runs calculation and sets next or previous plot as Figure's canvas.
        issues to resolve:
                - needs performance improvement and storage of plots in self.plots


        plot_type: str

        index: int   -1 (Previous Plot)
                      1 (Next Plot)
        """

        tree_path, i = self.get_tree_path(plot_type, index)
        self.plot_data.tree_path = tree_path
        self.plot_panel.figure.clear()

        plot_type = self.plot_data.plot_type
        
        print plot_type
        print tree_path
        print i

        if plot_type == "line_samp":
            self.plot_data = SampleLinePlotter(self.s_data, self.plot_data)


        elif plot_type == "line_ass":
            self.plot_data = AssessorLinePlotter(self.s_data, self.plot_data)


        elif plot_type == "line_rep":
            self.plot_data = ReplicateLinePlotter(self.s_data, self.plot_data)


        elif plot_type == "mean_std_ass":
            self.plot_data = RawDataAssessorPlotter(self.s_data, self.plot_data)


        elif plot_type == "mean_std_att":
            self.plot_data = RawDataAttributePlotter(self.s_data, self.plot_data)


        elif plot_type == "corr":
            self.plot_data = CorrelationPlotter(self.s_data, self.plot_data)
            #if self.plot_data.tree_path[1] in self.s_data.AttributeList:
            #    self.plot_data.activeAttributesList = [self.plot_data.tree_path[1]]
                #self.active_att = [self.plot_data.tree_path[1]]

        elif plot_type == "profile":
            #self.plot_data.activeAttributesList = [self.plot_data.tree_path[0]]
            self.plot_data = profilePlotter(self.s_data, self.plot_data)
            #self.active_att = [self.plot_data.tree_path[0]]


        elif plot_type == "egg":
            #self.plot_data.activeAttributesList = [self.plot_data.tree_path[0]]
            self.plot_data = EggshellPlotter(self.s_data, self.plot_data)
            #self.active_att = [self.plot_data.tree_path[0]]


        elif plot_type == "f_ass":
            if i == 0:
                self.plot_data = FPlotter_Assessor_General(self.s_data, self.plot_data)
            else:
                self.plot_data = FPlotter_Assessor_Specific(self.s_data, self.plot_data)


        elif plot_type == "f_att":
            if i == 0:
                self.plot_data = FPlotter_Attribute_General(self.s_data, self.plot_data)
            else:
                self.plot_data = FPlotter_Attribute_Specific(self.s_data, self.plot_data)

        elif plot_type == "mse_ass":
            if i == 0:
                self.plot_data = MSEPlotter_Assessor_General(self.s_data, self.plot_data)
            else:
                self.plot_data = MSEPlotter_Assessor_Specific(self.s_data, self.plot_data)


        elif plot_type == "mse_att":
            if i == 0:
                self.plot_data = MSEPlotter_Attribute_General(self.s_data, self.plot_data)
            else:
                self.plot_data = MSEPlotter_Attribute_Specific(self.s_data, self.plot_data)


        elif plot_type == "pmse":
            self.plot_data = pmsePlotter(self.s_data, self.plot_data)


        elif plot_type == "tucker1":
            self.plot_data = Tucker1Plotter(self.s_data, self.plot_data, selection=self.PCAmode, pc_x=self.pc_x_index, pc_y=self.pc_y_index)


        elif plot_type == "consensus":
            self.plot_data = PCA_plotter(self.s_data, self.plot_data, selection=self.average_mode, pc_x=self.pc_x_index, pc_y=self.pc_y_index) # 0: PC1, 1: PC2


        elif plot_type == "statis_consensus":
            if self.plot_data.tree_path[0] == u'Assessor Weights':
                self.plot_data = STATIS_AssWeight_Plotter(self.s_data, self.plot_data, selection=self.statis_mode) # 0: PC1, 1: PC2
            else:
                self.plot_data = STATIS_PCA_Plotter(self.s_data, self.plot_data, selection=self.statis_mode, pc_x=self.pc_x_index, pc_y=self.pc_y_index) # 0: PC1, 1: PC2
                self.maxPCs = self.plot_data.max_PCs


        elif plot_type == "mm_anova_f_2way1rep":
            self.plot_data = MixModel_ANOVA_Plotter_2way1rep(self.s_data, self.plot_data)


        elif plot_type == "mm_anova_lsd_2way1rep":
            self.plot_data = MixModel_ANOVA_LSD_Plotter_2way1rep(self.s_data, self.plot_data)


        elif plot_type == "mm_anova_f_2way":
            self.plot_data = MixModel_ANOVA_Plotter_2way(self.s_data, self.plot_data)


        elif plot_type == "mm_anova_lsd_2way":
            self.plot_data = MixModel_ANOVA_LSD_Plotter_2way(self.s_data, self.plot_data)


        elif plot_type == "mm_anova_f_3way":
            self.plot_data = MixModel_ANOVA_Plotter_3way(self.s_data, self.plot_data)


        elif plot_type == "mm_anova_lsd_3way":
            self.plot_data = MixModel_ANOVA_LSD_Plotter_3way(self.s_data, self.plot_data)

        elif plot_type == "manhattan_ass" or plot_type == "manhattan_att":
            self.plot_data = ManhattanPlotter(self.s_data, self.plot_data)
            
        elif plot_type == "perf_ind":
            self.plot_data.special_opts["recalc"] = False
            self.plot_data = perfindPlotter(self.s_data, self.plot_data)            
            

        self.plot_panel.subplot = self.plot_data.ax
        self.plot_panel.figure = self.plot_data.fig
        #self.plot_panel.subplot.set_figure(self.plot_data.fig)
        self.update_variables()
        self.recalc_epsilon()

        #print self.plot_panel.figure
        #print self.plot_panel.subplot

        #print self.plot_data.fig.canvas.GetId() # = self.plot_data.fig
        #self.plot_panel.canvas.figure.set_canvas(self.plot_panel.canvas)

        #print datasets
        #self.plot_panel.canvas = self.plot_data.fig.canvas

        #self.plot_panel.canvas = self.plot_panel.figure.canvas
        #print self.plot_panel.canvas.GetId()

        #self.plot_panel.canvas = self.plot_data.fig.canvas
        self.plot_panel.subplot.figure.canvas.draw()
        #print self.plot_panel.canvas.bitmap
        #self.Bind(wx.EVT_KEY_DOWN, self.onKeyEvent, id=self.plot_panel.figure.canvas.GetId())
        #self.plot_panel.subplot.figure.canvas.Bind(wx.EVT_KEY_DOWN, self.onKeyEvent)
        #self.plot_panel.subplot.figure.canvas.draw()
        #self.plot_panel.canvas = self.plot_panel.subplot.figure.canvas
        #self.Refresh()


    def prevPlot(self, event=None):
        self.replot(self.plot_type, -1)
        self.original_xLims = self.plot_panel.subplot.get_xlim()
        self.original_yLims = self.plot_panel.subplot.get_ylim()

    def nextPlot(self, event=None):
        self.replot(self.plot_type, 1)
        self.original_xLims = self.plot_panel.subplot.get_xlim()
        self.original_yLims = self.plot_panel.subplot.get_ylim()



class NavigationToolbar2Wx(NavigationToolbar2, wx.ToolBar):
    def __init__(self, canvas):
        wx.ToolBar.__init__(self, canvas.GetParent(), -1)
        NavigationToolbar2.__init__(self, canvas)
        self.canvas = canvas
        self._idle = True
        self.statbar = None

    def _init_toolbar(self):
        self._parent = self.canvas.GetParent()
        self._NTB2_PAN     =wx.NewId()
        self._NTB2_ZOOM    =wx.NewId()

    def zoom(self, *args):
        self.ToggleTool(self._NTB2_PAN, False)
        NavigationToolbar2.zoom(self, *args)

    def pan(self, *args):
        self.ToggleTool(self._NTB2_ZOOM, False)
        NavigationToolbar2.pan(self, *args)


    def release(self, event):
        try: del self.lastrect
        except AttributeError: pass

    def dynamic_update(self):
        d = self._idle
        self._idle = False
        if d:
            self.canvas.draw()
            self._idle = True

    def draw_rubberband(self, event, x0, y0, x1, y1):
        canvas = self.canvas
        dc = wx.ClientDC(canvas)

        # Set logical function to XOR for rubberbanding
        dc.SetLogicalFunction(wx.XOR)

        # Set dc brush and pen
        # Here I set brush and pen to white and grey respectively
        # You can set it to your own choices

        # The brush setting is not really needed since we
        # dont do any filling of the dc. It is set just for
        # the sake of completion.

        wbrush =wx.Brush(wx.Colour(255,255,255), wx.TRANSPARENT)
        wpen =wx.Pen(wx.Colour(200, 200, 200), 1, wx.SOLID)
        dc.SetBrush(wbrush)
        dc.SetPen(wpen)


        dc.ResetBoundingBox()
        dc.BeginDrawing()
        height = self.canvas.figure.bbox.height()
        y1 = height - y1
        y0 = height - y0

        if y1<y0: y0, y1 = y1, y0
        if x1<y0: x0, x1 = x1, x0

        w = x1 - x0
        h = y1 - y0

        rect = int(x0), int(y0), int(w), int(h)
        try: lastrect = self.lastrect
        except AttributeError: pass
        else: dc.DrawRectangle(*lastrect)  #erase last
        self.lastrect = rect
        dc.DrawRectangle(*rect)
        dc.EndDrawing()



class SimpleFigLegend(Figure):
    """
    !!!Unfinished!!!
    A custom legend-box for PanelCheck (rather then using figlegend in matplotlib).
    Comment: Width will be stable and canvas hopefully nicer and more suitable. Width is a issue with the current legend solution.
    """
    def __init__(self, parent, symbolColorsAndLabelsList):
        Figure.__init__(self)
        self.set_figure(parent.figure)
        self.parent = parent
        self.symbolColors = symbolColorsAndLabelsList[0]
        self.texts = symbolColorsAndLabelsList[1]
        self.fontsize = FontProperties(size='smaller').get_size_in_points()

        self.set_transform( get_bbox_transform( unit_bbox(), self.parent.bbox) )

        #legend position
        self.xPos = 0.8
        self.yPos = 0.95

        self.symbolWidth = 0.1

        self.HEIGHT = self._approx_text_height()
        self.legendPatch = Rectangle(
            xy=(self.xPos, self.yPos), width=0.5, height=self.HEIGHT*len(self.texts),
            facecolor='w', edgecolor='k',
            )
        self._set_artist_props(self.legendPatch)

        #self.legendPatch.set_bounds(l,b,w,h)



    def _set_artist_props(self, a):
        a.set_figure(self.figure)
        a.set_transform(self._transform)



    def _approx_text_height(self):
        return self.fontsize/72.0*self.figure.dpi.get()/self.parent.bbox.height()



    def draw(self):
        renderer.open_group('legend')

        #positioning
        #self.legendPatch.set_x(self.xPos)
        #self.legendPatch.set_y(self.yPos)
        i = 0
        for t in self.texts:
            t.set_position( (self.xPos + self.symbolWidth + 0.02 , self.yPos - (0.01 + i*self.HEIGHT)) )
            c = Circle.__init__((self.xPos + 0.01, self.yPos - (0.01 + i*self.HEIGHT)), radius=5, resolution=20)
            c.set_facecolor(self.symbolColors[i])
            c.set_figure(self.legendPatch.figure)
            c.set_transform(self._transform)
            i += 1


        #render
        self.legendPatch.draw(renderer)

        #for h in self.symbols:
        #    h.draw(renderer)

        for t in self.texts:
            t.draw(renderer)
        renderer.close_group('legend')


def set_xlabeling(ax, x_string_list):
    """
    Sets x-labels by given x_string_list onto ax
    """
    amount = len(x_string_list)
    x_range = ax.get_xlim()
    start_x = (x_range[1]-amount)/2
    part = ((x_range[1]-2*start_x)/amount)
    spacer = part/2

    x_positions = []
    for i in range(0 , amount):
        x_positions.append(start_x + spacer + i*part)

    #print tickPositions
    locator = FixedLocator(x_positions)
    ax.xaxis.set_major_locator(locator)
    ax.set_xticklabels(x_string_list)
    if amount > 13:
        for xtick_label in ax.get_xticklabels():
            setp(xtick_label, 'rotation', 'vertical')


def axes_create(legend, fig):
    """
    Creates figure axes.

    @type legend: boolean
    @param legend: Whether legend is on or off.
    """
    ax = 0
    if(legend): #if legend to be drawn
        ax = fig.add_axes([0.1, 0.1, 0.65, 0.8]) #[left, bottom, width, height]
    else:
        ax = fig.add_axes([0.1, 0.1, 0.8, 0.8]) #[left, bottom, width, height]
    return ax



def axes_setup(ax, xLabel, yLabel, title, limits):
    """
    Sets up the axes.

    @type ax: object
    @param ax: Axes to be worked on.

    @type title: string
    @param title: Axes title.

    @type xLabel: string
    @param xLabel: Label name under the x-axes.

    @type yLabel: string
    @param yLabel: Label name left of the y-axes.

    @type limits: list
    @param limits: Limits for the axes. [x_min, x_max, y_min, y_max]
    """
    font = {'fontname'   : 'Arial Narrow',
            'color'      : 'black',
            'fontweight' : 'normal',
            'fontsize'   : 13}

    # Settings for the labels in the plot
    ax.set_xlabel(xLabel, font)
    ax.set_ylabel(yLabel, font)
    ax.set_title(title, font)
    ax.set_xlim(limits[0], limits[1])
    ax.set_ylim(limits[2], limits[3])



##def printLabelIfCorrectPoint(self, x, y):
##    """
##    Outputs assessor and its point values on the statusbar.
##    Epsilon should be calculated according to the axis values.
##
##    @type x:     float
##    @param x:    Cursor x point
##
##    @type y:     float
##    @param y:    Cursor y point
##    """
##    for innerList in self.points_labels:
##        if innerList[0] < x+self.epsilonX and innerList[0] > x-self.epsilonX:
##            if innerList[1] < y+self.epsilonY and innerList[1] > y-self.epsilonY:
##                self.statusBar.SetStatusText("x=%f  y=%f"% (innerList[0], innerList[1]) + "     " + innerList[2])
##                return
