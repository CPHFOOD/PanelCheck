#import psyco
#psyco.full()

import os, sys, wx, re, math, glob
from PanelCheck_Tools import *
from matplotlib.figure import Figure
from matplotlib.backends.backend_agg import FigureCanvasAgg
from PanelCheck_Tools import *
import matplotlib.pyplot as plt
#Plots
from PanelCheck_Plots import *

from PlotData import *

class Export_Images_Dialog(wx.Dialog):
    def __init__(self, prnt, s_data, saving_ppt_file=False, view_grid=False, view_legend=False, active_plots=[], selection_changes={}):
        wx.Dialog.__init__(self, id=wx.NewId(), name=u'Export Images:', parent=prnt, title="Save Image Files:",
	                  pos=wx.DefaultPosition, size=wx.DefaultSize, style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER)
        
        pathname = os.path.dirname(sys.argv[0]) 
        self.progPath = os.path.abspath(pathname).decode(sys.getfilesystemencoding())
        figpath = self.progPath + u'/fig.ico'
        self.SetIcon(wx.Icon(figpath,wx.BITMAP_TYPE_ICO))
        
        self.parent = prnt
        
        self._panel = wx.Panel(id=wx.NewId(),
              name=u'_panel', parent=self, pos=wx.Point(0, 0),
              size=wx.Size(700, 440), style=wx.TAB_TRAVERSAL)
        
        self.s_data = s_data
        
        self.view_grid = view_grid
        self.view_legend = view_legend
        self.saving_ppt_file = saving_ppt_file
        
        self.AssessorList = self.s_data.AssessorList
	self.SampleList = self.s_data.SampleList
	self.ReplicateList = self.s_data.ReplicateList
        self.AttributeList = self.s_data.AttributeList       
        
        self.plots = [\
        "Line Sample Plots",\
        "Line Assessor Plots",\
        "Mean && STD Plots",\
        "Correlation Plots",\
        "Profile Plots",\
        "Eggshell Plots",\
        "F Plots (sorted by assessors)",\
        "F Plots (sorted by attributes)",\
        "p Plots (sorted by assessors)",\
        "p Plots (sorted by attributes)",\
        "MSE Plots (sorted by assessors)",\
        "MSE Plots (sorted by attributes)",\
        "p-MSE Plots (focus on assessors)",\
        "p-MSE Plots (focus on attributes)",\
        "Tucker-1 Plots",\
        "Tucker-1 Standardized Plots",\
        "Consensus Original",\
        "Consensus Standardized",\
        "STATIS Covariance",\
        "STATIS Correlation",\
        "Manhattan Original",\
        "Manhattan Standardized",\
        "2-way ANOVA (1 rep)",\
        "2-way ANOVA",\
        "3-way ANOVA"]
        
        
        self._text_plots = wx.StaticText(id=wx.NewId(),
              label=u'Plots:', name=u'_text_Ass', parent=self._panel,
              pos=wx.Point(100, 12), size=wx.Size(67, 16), style=0)
        _c_plots_id=wx.NewId()
        self._checkList_plots = wx.CheckListBox(choices=self.plots,
              id=_c_plots_id, parent=self._panel, pos=wx.Point(8, 32), size=wx.Size(240,
              278), style=0)
        self._checkList_plots.Bind(wx.EVT_LISTBOX,
              self.On_checkList_plots,
              id=_c_plots_id)
        self._checkList_plots.Bind(wx.EVT_CHECKLISTBOX,
              self.onCheckBoxListPlotsChange,
              id=_c_plots_id)              
              
        self._text_Ass = wx.StaticText(id=wx.NewId(),
              label=u'Assessors:', name=u'_text_Ass', parent=self._panel,
              pos=wx.Point(312, 38), size=wx.Size(67, 16), style=0)
        
        _c_ass_id=wx.NewId()
        _c_att_id=wx.NewId()
        _c_samp_id=wx.NewId()
        
        self._checkList_Ass = wx.CheckListBox(choices=self.AssessorList,
              id=_c_ass_id, name=u'_checkList_Ass',
              parent=self._panel, pos=wx.Point(280, 62), size=wx.Size(128,
              248), style=0)
        self._checkList_Ass.Bind(wx.EVT_LISTBOX,
              self.On_checkList_AssListbox,
              id=_c_ass_id)

        self._text_Att = wx.StaticText(id=wx.NewId(),
              label=u'Attributes:', name=u'_text_Att', parent=self._panel,
              pos=wx.Point(464, 38), size=wx.Size(58, 16), style=0)

        self._checkList_Att = wx.CheckListBox(choices=self.AttributeList,
              id=_c_att_id, name=u'_checkList_Att',
              parent=self._panel, pos=wx.Point(432, 62), size=wx.Size(128,
              248), style=0)
        self._checkList_Att.Bind(wx.EVT_LISTBOX,
              self.On_checkList_AttListbox,
              id=_c_att_id)

        self._text_Samp = wx.StaticText(id=wx.NewId(),
              label=u'Samples:', name=u'_text_Samp', parent=self._panel,
              pos=wx.Point(616, 38), size=wx.Size(57, 16), style=0)

        self._checkList_Samp = wx.CheckListBox(choices=self.SampleList,
              id=_c_samp_id, name=u'_checkList_Samp',
              parent=self._panel, pos=wx.Point(584, 62), size=wx.Size(128,
              248), style=0)
        self._checkList_Samp.Bind(wx.EVT_LISTBOX,
              self.On_checkList_SampListbox,
              id=_c_samp_id)
              
        _butt_ass_en_id=wx.NewId()
        _butt_ass_di_id=wx.NewId()
        _butt_att_en_id=wx.NewId()
        _butt_att_di_id=wx.NewId()
        _butt_samp_en_id=wx.NewId()
        _butt_samp_di_id=wx.NewId()

        self._button_Ass_EnableAll = wx.Button(id=_butt_ass_en_id,
              label=u'Enable all', name=u'_button_Ass_EnableAll',
              parent=self._panel, pos=wx.Point(304, 318), size=wx.Size(80,
              28), style=0)
        self._button_Ass_EnableAll.Bind(wx.EVT_BUTTON,
              self.On_button_Ass_EnableAllButton,
              id=_butt_ass_en_id)

        self._button_Ass_DisableAll = wx.Button(id=_butt_ass_di_id,
              label=u'Disable all', name=u'_button_Ass_DisableAll',
              parent=self._panel, pos=wx.Point(304, 350), size=wx.Size(80,
              28), style=0)
        self._button_Ass_DisableAll.Bind(wx.EVT_BUTTON,
              self.On_button_Ass_DisableAllButton,
              id=_butt_ass_di_id)

        self._button_Att_EnableAll = wx.Button(id=_butt_att_en_id,
              label=u'Enable all', name=u'_button_Att_EnableAll',
              parent=self._panel, pos=wx.Point(456, 318), size=wx.Size(80,
              28), style=0)
        self._button_Att_EnableAll.Bind(wx.EVT_BUTTON,
              self.On_button_Att_EnableAllButton,
              id=_butt_att_en_id)

        self._button_Att_DisableAll = wx.Button(id=_butt_att_di_id,
              label=u'Disable all', name=u'_button_Att_DisableAll',
              parent=self._panel, pos=wx.Point(456, 350), size=wx.Size(80,
              28), style=0)
        self._button_Att_DisableAll.Bind(wx.EVT_BUTTON,
              self.On_button_Att_DisableAllButton,
              id=_butt_att_di_id)

        self._button_Samp_EnableAll = wx.Button(id=_butt_samp_en_id,
              label=u'Enable all', name=u'_button_Samp_EnableAll',
              parent=self._panel, pos=wx.Point(608, 318), size=wx.Size(80,
              28), style=0)
        self._button_Samp_EnableAll.Bind(wx.EVT_BUTTON,
              self.On_button_Samp_EnableAllButton,
              id=_butt_samp_en_id)

        self._button_Samp_DisableAll = wx.Button(id=_butt_samp_di_id,
              label=u'Disable all', name=u'_button_Samp_DisableAll',
              parent=self._panel, pos=wx.Point(608, 350), size=wx.Size(80,
              28), style=0)
        self._button_Samp_DisableAll.Bind(wx.EVT_BUTTON,
              self.On_button_Samp_DisableAllButton,
              id=_butt_samp_di_id)
        
        self.choice_label = wx.StaticText(id=wx.NewId(), label=u'Enable/Disable every:',
              name='choice_label', parent=self._panel, pos=wx.Point(480,
              4), size=wx.Size(125, 16), style=0)
        self.choice_label.SetBackgroundColour(wx.SystemSettings.GetColour(wx.SYS_COLOUR_BTNFACE).Get())

        self.choice = wx.Choice(choices=["Single-select", " 1st", " 2nd", " 3rd",
              " 4th", " 5th", " 6th", " 7th", " 8th", " 9th", " 10th"], id=wx.NewId(),
              name='choice', parent=self._panel, pos=wx.Point(610, 0),
              size=wx.Size(100, 24), style=0)
        self.choice.SetSelection(0) 
        
        # ------------------------------------------------------------------------------- #        
        
        # go to program folder (Default is that images will be stored under Exports in the program folder)
        os.chdir(self.progPath)
        export_path = os.getcwdu() + "/Exports"
        if not os.path.isdir(export_path): # if folder not exists:
            os.mkdir(export_path)
        os.chdir(export_path)
        
        if saving_ppt_file:
            self.SetTitle("Make PowerPoint File:")
            self.radio1 = wx.RadioButton(self._panel, -1, "Make images in:", style = wx.RB_GROUP, pos=wx.Point(4, 320), size=(120,-1))
            self.radio1.SetToolTipString(u'Make images in selected folder')
            self.radio2 = wx.RadioButton(self._panel, -1, "Use images in:", pos=wx.Point(130, 320), size=(-1,-1))
            self.radio2.SetToolTipString(u'Images will not be made, but images found in selected folder will be used instead')
            browse_images = wx.NewId()
            self.input_browse_images = wx.TextCtrl(id=browse_images, parent=self._panel, pos=wx.Point(4, 350), size=wx.Size(210, 28))
            self.input_browse_images.SetValue(export_path)
            self.button_browse_im = wx.Button(id=browse_images, label=u'...', parent=self._panel, pos=wx.Point(218, 350), size=wx.Size(32,28))
            self.button_browse_im.Bind(wx.EVT_BUTTON, self.onButtonBrowseIm, id=browse_images)
            self.button_browse_im.SetToolTipString(u'Select image folder for current PowerPoint file')
        else:
            self.radio1 = wx.RadioButton(self._panel, -1, ".PNG", style = wx.RB_GROUP, pos=wx.Point(4, 320), size=(-1,-1))
            self.radio2 = wx.RadioButton(self._panel, -1, ".EPS (Postscript type)", pos=wx.Point(4, 350), size=(-1,-1))
            self._text_dpi = wx.StaticText(id=wx.NewId(),label=u'DPI:', parent=self._panel, pos=wx.Point(180, 325), size=wx.Size(30, 28), style=0)
            self._text_dpi.SetToolTipString(u'DPI (Dots per inch) is the resolution of the images (128dpi: 1024x768p)')
            self.input_dpi = wx.TextCtrl(id=wx.NewId(), parent=self._panel, pos=wx.Point(210, 320), size=wx.Size(40, 28), value="128")
        
        
        # ------------------------------------------------------------------------------- #
        self.line = wx.StaticLine(parent=self._panel, id=wx.NewId(), pos=wx.Point(0, 400), size=wx.Size(720, -1))
        
        
        ok = wx.NewId()
        self.buttonOK = wx.Button(id=ok, label=u'Save File(s)', parent=self._panel, pos=wx.Point(4, 410))
        self.buttonOK.Bind(wx.EVT_BUTTON, self.OnButtonOK, id=ok)

        self._text_out = wx.StaticText(id=wx.NewId(),
              label=u'Output:', name=u'_text_Att', parent=self._panel,
              pos=wx.Point(104, 415), size=wx.Size(46, 16), style=0)
        self.input_browse = wx.TextCtrl(id=wx.NewId(), parent=self._panel, pos=wx.Point(150, 410), size=wx.Size(400, 28))
        button_browse_id = wx.NewId()
        self.button_browse = wx.Button(id=button_browse_id, label=u'Browse...', parent=self._panel, pos=wx.Point(552, 410), size=wx.Size(80,28))
        self.button_browse.Bind(wx.EVT_BUTTON, self.onButtonBrowse, id=button_browse_id)
        _input = export_path
        if saving_ppt_file: 
            _input += "/presentation.ppt"
            self.button_browse.Bind(wx.EVT_BUTTON, self.onButtonBrowse2, id=button_browse_id)
        else:
            self.button_browse.Bind(wx.EVT_BUTTON, self.onButtonBrowse, id=button_browse_id)
        self.input_browse.SetValue(_input)        
        cancel = wx.NewId()
        self.buttonC = wx.Button(id=cancel, label=u'Close', parent=self._panel, pos=wx.Point(636, 410), size=wx.Size(80,28))
        self.buttonC.Bind(wx.EVT_BUTTON, self.OnButtonCancel, id=cancel)       
        self.Bind(wx.EVT_CLOSE, self.OnButtonCancel, id=wx.NewId())
        
        
        
        # Check all:
        self.check_CheckBoxList(self.AssessorList, self._checkList_Ass, True)
        self.check_CheckBoxList(self.AttributeList, self._checkList_Att, True)
        self.check_CheckBoxList(self.SampleList, self._checkList_Samp, True)
        #self.check_CheckBoxList(self.plots, self._checkList_plots, False)
        
        self.update_selection(selection_changes)
        self.update_selected_plots(active_plots)
        
        self.Layout()
        self.SetClientSize(wx.Size(720, 440))
        self.Show()

    
    def onCheckBoxListPlotsChange(self, event):
        self.parent.export_active_plots = self.get_ActiveIndicesFromCheckBoxList(self._checkList_plots)
    
    
    def onButtonBrowse(self, event):
        """
        Opens browse dialog for setting output path
        """
        dlg = wx.DirDialog(self, "Choose a directory:",defaultPath=os.getcwd(), 
                          style=wx.DD_DEFAULT_STYLE|wx.DD_NEW_DIR_BUTTON)

        if dlg.ShowModal() == wx.ID_OK:
            self.input_browse.SetValue(dlg.GetPath())
        dlg.Destroy() 
        
    def onButtonBrowse2(self, event):
        """
        Opens browse dialog
        """
        wildcard = "Presentation (*.ppt)|*.ppt||"
        dlg = wx.FileDialog(
            self, message="Save As", defaultDir=os.getcwd(), 
            defaultFile="presentation.ppt", wildcard=wildcard, style=wx.SAVE | wx.CHANGE_DIR)
        
        if dlg.ShowModal() == wx.ID_OK:
            self.input_browse.SetValue(dlg.GetPath())

        dlg.Destroy()    
        
    def OnButtonCancel(self, event):
        self.Destroy()
    
    def onButtonBrowseIm(self, event):
        """
        Opens browse dialog for setting image path
        """
        dlg = wx.DirDialog(self, "Choose a directory:",defaultPath=os.getcwd(), 
                          style=wx.DD_DEFAULT_STYLE|wx.DD_NEW_DIR_BUTTON)

        if dlg.ShowModal() == wx.ID_OK:
            self.input_browse_images.SetValue(dlg.GetPath())
        dlg.Destroy()        
    
    def OnButtonOK(self, event):
        activeAssessors_List = self.get_ActivesFromCheckBoxList(self.AssessorList, self._checkList_Ass)
        activeAttributes_List = self.get_ActivesFromCheckBoxList(self.AttributeList, self._checkList_Att)
        activeSamples_List = self.get_ActivesFromCheckBoxList(self.SampleList, self._checkList_Samp)
        active_plots = self.get_ActivesFromCheckBoxList(self.plots, self._checkList_plots)
            
        
        radio1 = self.radio1.GetValue()
        radio2 = self.radio2.GetValue()
        if radio2:
            selection = 1
        else:
            selection = 0
  
        if len(active_plots) < 1 and not (self.saving_ppt_file and selection == 1):
            dlg = wx.MessageDialog(None, 'No plots selected. Select from the Plots list and click again to save plots as image files.',
                               'Error Message', wx.OK | wx.ICON_INFORMATION)
            dlg.ShowModal(); dlg.Destroy(); return 
  
        in_im = ""; dpi = 128
        if self.saving_ppt_file:
            in_im = self.input_browse_images.GetValue()
        else:
            dpi_in = self.input_dpi.GetValue()
            try:
                dpi = int(dpi_in)
            except:
                dlg = wx.MessageDialog(None, 'Cannot process with current DPI value.\nPlease change DPI value.',
                               'Error Message',
                               wx.OK | wx.ICON_INFORMATION)
                dlg.ShowModal(); dlg.Destroy(); return
            if dpi > 4000:
                dlg = wx.MessageDialog(None, 'The DPI value is too high.\nPlease change DPI value.',
                               'Error Message',
                               wx.OK | wx.ICON_INFORMATION)
                dlg.ShowModal(); dlg.Destroy(); return        
            elif dpi < 1:
                 dlg = wx.MessageDialog(None, 'The DPI value cannot be less than 1.\nPlease change DPI value.',
                               'Error Message',
                               wx.OK | wx.ICON_INFORMATION)
                 dlg.ShowModal(); dlg.Destroy(); return               
        ExportImages(self.parent, self.s_data, active_plots, self.plots, self.input_browse.GetValue(), in_im,\
                                 activeAssessors_List, activeAttributes_List, activeSamples_List,\
                                 self.view_grid, self.view_legend, saving_ppt_file=self.saving_ppt_file, selection=selection, dpi=dpi)
        

        #self.EndModal(1)

    def On_button_Ass_EnableAllButton(self, event):
        self.check_CheckBoxList(self.AssessorList, self._checkList_Ass, True)
    
    def On_button_Ass_DisableAllButton(self, event):
        self.check_CheckBoxList(self.AssessorList, self._checkList_Ass, False)
    
    def On_button_Att_EnableAllButton(self, event):
        self.check_CheckBoxList(self.AttributeList, self._checkList_Att, True)
    
    def On_button_Att_DisableAllButton(self, event):
        self.check_CheckBoxList(self.AttributeList, self._checkList_Att, False)
    
    def On_button_Samp_EnableAllButton(self, event):
        self.check_CheckBoxList(self.SampleList, self._checkList_Samp, True)
    
    def On_button_Samp_DisableAllButton(self, event):
        self.check_CheckBoxList(self.SampleList, self._checkList_Samp, False)

    def On_checkList_plots(self, event):
        self.set_selection(event)
    
    def On_checkList_AssListbox(self, event):
        self.set_selection(event)

    def On_checkList_AttListbox(self, event):
        self.set_selection(event)

    def On_checkList_SampListbox(self, event):
        self.set_selection(event) 
        
    def set_selection(self, event):
        obj = event.GetEventObject()
        amount = obj.GetCount() # amount of elements in list
        i = self.choice.GetCurrentSelection() # index of current element in choice list
        j = obj.GetSelection() # index of current element in list
        if i > 0: # if i == 0 -> Single-select
            while j < amount:
                if obj.IsChecked(j):
                    obj.Check(j, False)
                else:
                    obj.Check(j, True)
                j += i # index in choice list has the correct value
        else:
            if obj.IsChecked(j):
	        obj.Check(j, False)
	    else:
                obj.Check(j, True)
        self.parent.export_active_plots = self.get_ActiveIndicesFromCheckBoxList(self._checkList_plots)
   
    def check_CheckBoxList(self, _list, parent, check):
        """
        Checks/unchecks all items in given parent (CheckBoxList) with given check (boolean).
        
        @type parent:   wx.CheckBoxList   
        
        @type check:    boolean
        
        @param list:    AssessorList, AttributeList or SampleList
        """
        for i in range(len(_list)):
            parent.Check(i, check)

    def get_ActiveIndicesFromCheckBoxList(self, parent):
            """
            Returns dictionary of active elements in given parent (CheckBoxList).
            
            @type parent:   wx.CheckBoxList        
            @param list:    AssessorList, AttributeList or SampleList
            """
            actives_list = []
            for i in range(parent.GetCount()):
                    if parent.IsChecked(i):
                        actives_list.append(i)
            return actives_list
                  
    def get_ActivesFromCheckBoxList(self, _list, parent):
        """
        Returns dictionary of active elements in given parent (CheckBoxList).
        
        @type parent:   wx.CheckBoxList        
        @param list:    AssessorList, AttributeList or SampleList
        """
        i = 0
        actives_list = []
        for element in _list:
                if parent.IsChecked(i):
                    actives_list.append(element)
                i += 1
        return actives_list
 

    def update_selected_plots(self, actives_list):   
        self.check_CheckBoxList(self.plots, self._checkList_plots, False)
        for ind in actives_list:
            self._checkList_plots.Check(ind, True) 
 
 
    def update_selection(self, changes): # dict of "ass", "att" or "samp" with indices for update
        
        if changes.has_key("ass"):
            self.check_CheckBoxList(self.AssessorList, self._checkList_Ass, False)
            for ind in changes["ass"]:
                self._checkList_Ass.Check(ind, True)

        if changes.has_key("att"):
            self.check_CheckBoxList(self.AttributeList, self._checkList_Att, False)
            for ind in changes["att"]:
                self._checkList_Att.Check(ind, True)

        if changes.has_key("samp"):
            self.check_CheckBoxList(self.SampleList, self._checkList_Samp, False)
            for ind in changes["samp"]:
                self._checkList_Samp.Check(ind, True) 
 
 
        
class ExportImages:
    def __init__(self, parent, s_data, active_plots, plots, outputdir, images_dir, active_ass, active_att, active_samp, grid, legend, saving_ppt_file=False, selection=0, dpi = 128):
        print "saving images"
        self.s_data = s_data
        
        self.active_plots = active_plots # plots for exporting
        self.outputdir = outputdir # directory for saving all files
        self.plots = plots
        
        self.parent = parent
        
        self.summary = ""
        
	self.active_ass = active_ass
	self.active_att = active_att
        self.active_samp = active_samp
        
        
        # plot data:
        self.mm_anova1_plot_data = None # plot data for Mixed Model ANOVA
        self.mm_anova2_plot_data = None # plot data for Mixed Model ANOVA
        self.anova_plot_data = None # plot data for all F and p plots
        self.pca_plot_data = None # plot data for all tucker1 plots
        self.coll_calc_plot_data = None
        self.manhattan_plot_data = None
        
        
 
 
        
        self.view_grid = grid
        self.view_legend = legend
        
        self.image_files = [] 
        
        folder = "_data_set_" + self.ascii_encode(self.s_data.filename)
        if not saving_ppt_file:
            self.im_out_dir = outputdir + "/" + folder
        else:
            self.im_out_dir = images_dir + "/" + folder
        
        if not os.path.isdir(self.im_out_dir): # if folder not exists:
            if not saving_ppt_file:
                os.mkdir(self.im_out_dir)
            else:
                if selection == 0:
                   os.mkdir(self.im_out_dir) 
            
        
        #plot_data = PlotData(self.active_ass, self.active_att, self.active_samp, [self.active_samp[0], self.active_ass[0], self.s_data.ReplicateList[0]], False, False) # no legend
        #plot_data.set_limits(self.s_data.scale_limits)
        #plot_data = ReplicateLinePlotter(self.s_data, plot_data)
        self.canvas = FigureCanvasAgg(Figure(None))
        filename = self.im_out_dir + "_null_.png"
        
        #filename = str(filename)
        self.canvas.print_figure(filename.encode(codec), dpi=dpi)
        os.remove(filename)
        
        
        
        if saving_ppt_file:
            if selection == 0:
                self.save_image_files(self.im_out_dir, dpi)
            else:
                self.find_image_files(images_dir)
            self.save_ppt_file(self.image_files, self.outputdir)
        else:
            if selection == 0:
                self.save_image_files(self.im_out_dir, dpi)
            else:
                self.save_image_files(self.im_out_dir, dpi, ext=".eps")
 
    
    def find_image_files(self, images_dir):
        files = glob.glob(images_dir + "/*.png")
        files.extend(glob.glob(images_dir + "/*.eps"))
        files.extend(glob.glob(images_dir + "/*.bmp"))
        files.extend(glob.glob(images_dir + "/*.jpg"))
        files.extend(glob.glob(images_dir + "/*.gif"))
        self.image_files = files
    
 
    def canvas_ok(self, plot_data, plotter):
            if hasattr(plot_data, "fig") and plot_data.fig != None:
                self.canvas.figure = plot_data.fig
                self.canvas.figure.set_canvas(self.canvas)
                return True
            else: 
                self.summary += "Plot method failed: " + str(plotter) + "\n"
                return False
 
 
    def plot_ok(self, tree_path, plotter, selection=0):
        if plotter == FPlotter_Attribute_General or plotter == FPlotter_Attribute_Specific or plotter == FPlotter_Assessor_General or plotter == FPlotter_Assessor_Specific \
          or plotter == MSEPlotter_Attribute_General or plotter == MSEPlotter_Attribute_Specific or plotter == MSEPlotter_Assessor_General or plotter == MSEPlotter_Assessor_Specific \
          or plotter == pmsePlotter:
            if self.anova_plot_data == None:
                self.anova_plot_data = ANOVA_PlotData(self.active_ass, self.active_att, self.active_samp, tree_path, self.view_grid, self.view_legend)
                self.anova_plot_data.set_limits(self.s_data.scale_limits)
                self.anova_plot_data = plotter(self.s_data, self.anova_plot_data, selection=selection)
                return self.canvas_ok(self.anova_plot_data, plotter)
            else:
                self.anova_plot_data.tree_path = tree_path
                self.anova_plot_data.fig = None # reset Figure 
                self.anova_plot_data = plotter(self.s_data, self.anova_plot_data, selection=selection)
                return self.canvas_ok(self.anova_plot_data, plotter)
                
                
        
        elif plotter == EggshellPlotter or plotter == profilePlotter or plotter == RawDataAttributePlotter:
            if self.coll_calc_plot_data == None:
                self.coll_calc_plot_data = CollectionCalcPlotData(self.active_ass, self.active_att, self.active_samp, tree_path, self.view_grid, self.view_legend)
                self.coll_calc_plot_data.set_limits(self.s_data.scale_limits)
                self.coll_calc_plot_data = plotter(self.s_data, self.coll_calc_plot_data)
                return self.canvas_ok(self.coll_calc_plot_data, plotter)
            else:
                self.coll_calc_plot_data.tree_path = tree_path
                self.coll_calc_plot_data.fig = None # reset Figure
                self.coll_calc_plot_data = plotter(self.s_data, self.coll_calc_plot_data)                
                return self.canvas_ok(self.coll_calc_plot_data, plotter)                 
                
                
                
        elif plotter == Tucker1Plotter:
            if self.pca_plot_data == None or self.pca_plot_data.selection != selection:
                self.pca_plot_data = PCA_PlotData(self.active_ass, self.active_att, self.active_samp, tree_path, self.view_grid, self.view_legend)
                self.pca_plot_data.set_limits(self.s_data.scale_limits)
                self.pca_plot_data = plotter(self.s_data, self.pca_plot_data, selection=selection)
                return self.canvas_ok(self.pca_plot_data, plotter)
            else:
                self.pca_plot_data.tree_path = tree_path
                self.pca_plot_data.fig = None # reset Figure 
                self.pca_plot_data = plotter(self.s_data, self.pca_plot_data, selection=selection)                
                return self.canvas_ok(self.pca_plot_data, plotter)
        
        
        
        elif plotter == ManhattanPlotter: 
            if self.manhattan_plot_data == None or self.manhattan_plot_data.selection != selection:
                self.manhattan_plot_data = CollectionCalcPlotData(self.active_ass, self.active_att, self.active_samp, tree_path, self.view_grid, self.view_legend)
                self.manhattan_plot_data.set_limits(self.s_data.scale_limits)
                self.manhattan_plot_data.maxPCs = int(self.parent.manh_spin_txt.GetValue())
                self.manhattan_plot_data = plotter(self.s_data, self.manhattan_plot_data, selection=selection)
                return self.canvas_ok(self.manhattan_plot_data, plotter)
            else:
                self.manhattan_plot_data.tree_path = tree_path
                self.manhattan_plot_data.fig = None # reset Figure
                self.manhattan_plot_data.maxPCs = int(self.parent.manh_spin_txt.GetValue())
                self.manhattan_plot_data = plotter(self.s_data, self.manhattan_plot_data, selection=selection)                
                return self.canvas_ok(self.manhattan_plot_data, plotter)            



        elif plotter == MixModel_ANOVA_Plotter_2way or plotter == MixModel_ANOVA_LSD_Plotter_2way or plotter == MixModel_ANOVA_Plotter_3way or plotter == MixModel_ANOVA_LSD_Plotter_3way: 
            if self.mm_anova2_plot_data == None:
                self.mm_anova2_plot_data = MM_ANOVA_PlotData(self.active_ass, self.active_att, self.active_samp, tree_path, self.view_grid, self.view_legend)
                self.mm_anova2_plot_data.set_limits(self.s_data.scale_limits)
                self.mm_anova2_plot_data = plotter(self.s_data, self.mm_anova2_plot_data)
                return self.canvas_ok(self.mm_anova2_plot_data, plotter)
            else:
                self.mm_anova2_plot_data.tree_path = tree_path
                self.mm_anova2_plot_data.fig = None # reset Figure
                self.mm_anova2_plot_data = plotter(self.s_data, self.mm_anova2_plot_data, selection=selection)                
                return self.canvas_ok(self.mm_anova2_plot_data, plotter)  



        elif plotter == MixModel_ANOVA_Plotter_2way1rep or plotter == MixModel_ANOVA_LSD_Plotter_2way1rep: 
            if self.mm_anova1_plot_data == None:
                self.mm_anova1_plot_data = MM_ANOVA_PlotData(self.active_ass, self.active_att, self.active_samp, tree_path, self.view_grid, self.view_legend)
                self.mm_anova1_plot_data.set_limits(self.s_data.scale_limits)
                self.mm_anova1_plot_data = plotter(self.s_data, self.mm_anova1_plot_data, selection=selection)
                return self.canvas_ok(self.mm_anova1_plot_data, plotter)
            else:
                self.mm_anova1_plot_data.tree_path = tree_path
                self.mm_anova1_plot_data.fig = None # reset Figure
                self.mm_anova1_plot_data = plotter(self.s_data, self.mm_anova1_plot_data)                
                return self.canvas_ok(self.mm_anova1_plot_data, plotter)


        
        else:
            plot_data = PlotData(self.active_ass, self.active_att, self.active_samp, tree_path, self.view_grid, self.view_legend)
            plot_data.set_limits(self.s_data.scale_limits)
            plot_data = plotter(self.s_data, plot_data, selection=selection)        
            return self.canvas_ok(plot_data, plotter)
        
        

    def int2str(self, num, digits=3):
        str_num = str(num)
        len_num = len(str_num)
        _zeros = ""
        while len_num < digits:
            _zeros += "0"
            len_num += 1
        return _zeros + str_num
        
 
 
    def save_image_files(self, outputdir, dpi, ext=".png"):
        self.yes_to_all = False
        self.no_to_all = False
        progress = Progress(None)
        progress.set_gauge(value=0, text="Saving images...\nThis may take several minutes.\nPlease wait...\n")
        _num = len(self.active_plots)
        part = 100/_num; _index = 0; plot_ind = 0
        current_value = int(math.ceil(part)); _index += 1
        
        # Line Sample Plots
        if self.plots[plot_ind] in self.active_plots:
            _nr = 1
            for samp in self.active_samp:
                if self.plot_ok([samp], SampleLinePlotter):
                    filename = outputdir + "/"+ self.int2str(plot_ind) +"_line_samp" + self.int2str(_nr) + "_" + re.sub(' ', '_', self.ascii_enc(samp)) + ext
                    self.save_image_file(self.canvas, filename, dpi=dpi); _nr += 1
                    if self.no_to_all: progress.Destroy(); return
            progress.set_gauge(value=current_value); _index += 1
    
        plot_ind += 1
        # Line Assessor Plots
        if self.plots[plot_ind] in self.active_plots:
            _nr = 1
            for samp in self.active_samp:
                for ass in self.active_ass:
                    if self.plot_ok([samp, ass], AssessorLinePlotter):
                        filename = outputdir + "/"+ self.int2str(plot_ind) +"_line_samp_ass" + self.int2str(_nr) + "_" + re.sub(' ', '_', self.ascii_enc(samp)) + "_" + re.sub(' ', '_', self.ascii_enc(ass)) + ext
                        self.save_image_file(self.canvas, filename, dpi=dpi); _nr += 1
                        if self.no_to_all: progress.Destroy(); return
            current_value = int(math.ceil(part*_index)); _index += 1
            progress.set_gauge(value=current_value)
            
        plot_ind += 1
        # Mean && STD Plots
        if self.plots[plot_ind] in self.active_plots:
            _nr = 1
            for ass in self.active_ass:
                if self.plot_ok([ass], RawDataAssessorPlotter):
                    filename = outputdir + "/"+ self.int2str(plot_ind) +"_mean_std_ass" + self.int2str(_nr) + "_" + re.sub(' ', '_', self.ascii_enc(ass)) + ext
                    self.save_image_file(self.canvas, filename, dpi=dpi); _nr += 1
                    if self.no_to_all: progress.Destroy(); return
            for att in self.active_att:
                if self.plot_ok([att], RawDataAttributePlotter):
                    filename = outputdir + "/"+ self.int2str(plot_ind) +"_mean_std_att" + self.int2str(_nr) + "_" + re.sub(' ', '_', self.ascii_enc(att)) + ext
                    self.save_image_file(self.canvas, filename, dpi=dpi); _nr += 1
                    if self.no_to_all: progress.Destroy(); return    
            current_value = int(math.ceil(part*_index)); _index += 1
            progress.set_gauge(value=current_value)  
            
        plot_ind += 1
        # Correlation Plots
        if self.plots[plot_ind] in self.active_plots:
            _nr = 1
            for ass in self.active_ass:
                for att in self.active_att:
                    if self.plot_ok([ass, att], CorrelationPlotter):
                        filename = outputdir + "/"+ self.int2str(plot_ind) +"_corr_ass_att" + self.int2str(_nr) + "_" + re.sub(' ', '_', self.ascii_enc(ass)) + "_" + re.sub(' ', '_', self.ascii_enc(att)) + ext
                        self.save_image_file(self.canvas, filename, dpi=dpi); _nr += 1
                        if self.no_to_all: progress.Destroy(); return                    
            current_value = int(math.ceil(part*_index)); _index += 1
            progress.set_gauge(value=current_value)
        
        plot_ind += 1
        # Profile Plots
        if self.plots[plot_ind] in self.active_plots:
            _nr = 1
            for att in self.active_att:
                if self.plot_ok([att], profilePlotter):
                    filename = outputdir + "/"+ self.int2str(plot_ind) +"_profile" + self.int2str(_nr) + "_" + re.sub(' ', '_', self.ascii_enc(att)) + ext
                    self.save_image_file(self.canvas, filename, dpi=dpi); _nr += 1
                    if self.no_to_all: progress.Destroy(); return
            current_value = int(math.ceil(part*_index)); _index += 1
            progress.set_gauge(value=current_value) 
            
        plot_ind += 1
        # Eggshell Plots
        if self.plots[plot_ind] in self.active_plots:
            _nr = 1
            for att in self.active_att:
                if self.plot_ok([att], EggshellPlotter):
                    filename = outputdir + "/"+ self.int2str(plot_ind) +"_eggshell" + self.int2str(_nr) + "_" + re.sub(' ', '_', self.ascii_enc(att)) + ext
                    self.save_image_file(self.canvas, filename, dpi=dpi); _nr += 1
                    if self.no_to_all: progress.Destroy(); return
            current_value = int(math.ceil(part*_index)); _index += 1
            progress.set_gauge(value=current_value)
            
        plot_ind += 1
        # F Assessor Plots
        if self.plots[plot_ind] in self.active_plots:
            _nr = 1
            if self.plot_ok(['F-values','General Plot'], FPlotter_Attribute_General): 
                filename = outputdir + "/"+ self.int2str(plot_ind) +"_f_ass_general" + ext
                self.save_image_file(self.canvas, filename, dpi=dpi)
                if self.no_to_all: progress.Destroy(); return 
            for att in self.active_att:
                if self.plot_ok(['F-values',att], FPlotter_Assessor_Specific):
                    filename = outputdir + "/"+ self.int2str(plot_ind) +"b_f_ass" + self.int2str(_nr) + "_" + re.sub(' ', '_', self.ascii_enc(att)) + ext
                    self.save_image_file(self.canvas, filename, dpi=dpi); _nr += 1
                    if self.no_to_all: progress.Destroy(); return 
            current_value = int(math.ceil(part*_index)); _index += 1
            progress.set_gauge(value=current_value)
            
        plot_ind += 1
        # F Attribute Plots
        if self.plots[plot_ind] in self.active_plots:
            _nr = 1
            if self.plot_ok(['F-values','General Plot'], FPlotter_Attribute_General):
                filename = outputdir + "/"+ self.int2str(plot_ind) +"_f_att_general" + ext
                self.save_image_file(self.canvas, filename, dpi=dpi)
                if self.no_to_all: progress.Destroy(); return 
            for ass in self.active_ass:
                if self.plot_ok(['F-values',ass], FPlotter_Attribute_Specific):
                    filename = outputdir + "/"+ self.int2str(plot_ind) +"b_f_att" + self.int2str(_nr) + "_" + re.sub(' ', '_', self.ascii_enc(ass)) + ext
                    self.save_image_file(self.canvas, filename, dpi=dpi); _nr += 1
                    if self.no_to_all: progress.Destroy(); return 
            current_value = int(math.ceil(part*_index)); _index += 1
            progress.set_gauge(value=current_value)
            
        plot_ind += 1
        # p Assessor Plots
        if self.plots[plot_ind] in self.active_plots:
            _nr = 1
            if self.plot_ok(['p-values','General Plot'], FPlotter_Assessor_General):
                filename = outputdir + "/"+ self.int2str(plot_ind) +"_p_ass_general" + ext
                self.save_image_file(self.canvas, filename, dpi=dpi)
                if self.no_to_all: progress.Destroy(); return 
            for att in self.active_att:
                if self.plot_ok(['p-values',att], FPlotter_Assessor_Specific):
                    filename = outputdir + "/"+ self.int2str(plot_ind) +"b_p_ass" + self.int2str(_nr) + "_" + re.sub(' ', '_', self.ascii_enc(att)) + ext
                    self.save_image_file(self.canvas, filename, dpi=dpi); _nr += 1
                    if self.no_to_all: progress.Destroy(); return 
            current_value = int(math.ceil(part*_index)); _index += 1
            progress.set_gauge(value=current_value)
            
        plot_ind += 1
        # p Attribute Plots
        if self.plots[plot_ind] in self.active_plots:
            _nr = 1
            if self.plot_ok(['p-values','General Plot'], FPlotter_Attribute_General):
                filename = outputdir + "/"+ self.int2str(plot_ind) +"_p_att_general" + ext
                self.save_image_file(self.canvas, filename, dpi=dpi)
                if self.no_to_all: progress.Destroy(); return         
            for ass in self.active_ass:
                if self.plot_ok(['p-values',ass], FPlotter_Attribute_Specific):
                    filename = outputdir + "/"+ self.int2str(plot_ind) +"b_p_att" + self.int2str(_nr) + "_" + re.sub(' ', '_', self.ascii_enc(ass)) + ext
                    self.save_image_file(self.canvas, filename, dpi=dpi); _nr += 1
                    if self.no_to_all: progress.Destroy(); return 
            current_value = int(math.ceil(part*_index)); _index += 1
            progress.set_gauge(value=current_value)
            
        plot_ind += 1
        # MSE Assessor Plots
        if self.plots[plot_ind] in self.active_plots:
            if self.plot_ok(['General Plot'], MSEPlotter_Assessor_General):
                filename = outputdir + "/"+ self.int2str(plot_ind) +"_mse_ass_general" + ext
                self.save_image_file(self.canvas, filename, dpi=dpi)
            if self.no_to_all: progress.Destroy(); return 
            _nr = 1
            for att in self.active_att:
                if self.plot_ok([att], MSEPlotter_Assessor_Specific): 
                    filename = outputdir + "/"+ self.int2str(plot_ind) +"b_mse_ass" + self.int2str(_nr) + "_" + re.sub(' ', '_', self.ascii_enc(att)) + ext
                    self.save_image_file(self.canvas, filename, dpi=dpi); _nr += 1
                    if self.no_to_all: progress.Destroy(); return 
            current_value = int(math.ceil(part*_index)); _index += 1; 
            progress.set_gauge(value=current_value)
            
        plot_ind += 1
        # MSE Attribute Plots
        if self.plots[plot_ind] in self.active_plots:
            if self.plot_ok(['General Plot'], MSEPlotter_Attribute_General):
                filename = outputdir + "/"+ self.int2str(plot_ind) +"_mse_att_general" + ext
                self.save_image_file(self.canvas, filename, dpi=dpi)
                if self.no_to_all: progress.Destroy(); return
            _nr = 1
            for ass in self.active_ass:
                if self.plot_ok([ass], MSEPlotter_Attribute_Specific):
                    filename = outputdir + "/"+ self.int2str(plot_ind) +"b_mse_att" + self.int2str(_nr) + "_" + re.sub(' ', '_', self.ascii_enc(ass)) + ext
                    self.save_image_file(self.canvas, filename, dpi=dpi); _nr += 1
                    if self.no_to_all: progress.Destroy(); return 
            current_value = int(math.ceil(part*_index)); _index += 1
            progress.set_gauge(value=current_value)                

        plot_ind += 1
        # p-MSE Assessor Plots
        if self.plots[plot_ind] in self.active_plots:
            _nr = 1
            for ass in self.active_ass:
                if self.plot_ok([ass], pmsePlotter):
                    filename = outputdir + "/"+ self.int2str(plot_ind) +"_pmse_ass" + self.int2str(_nr) + "_" + re.sub(' ', '_', self.ascii_enc(ass)) + ext
                    self.save_image_file(self.canvas, filename, dpi=dpi); _nr += 1
                    if self.no_to_all: progress.Destroy(); return
            current_value = int(math.ceil(part*_index)); _index += 1
            progress.set_gauge(value=current_value)
        
        plot_ind += 1
        # p-MSE Attribute Plots
        if self.plots[plot_ind] in self.active_plots:
            _nr = 1
            for att in self.active_att:
                if self.plot_ok([att], pmsePlotter):
                    filename = outputdir + "/"+ self.int2str(plot_ind) +"_pmse_att" + self.int2str(_nr) + "_" + re.sub(' ', '_', self.ascii_enc(att)) + ext
                    self.save_image_file(self.canvas, filename, dpi=dpi); _nr += 1
                    if self.no_to_all: progress.Destroy(); return
            current_value = int(math.ceil(part*_index)); _index += 1
            progress.set_gauge(value=current_value)
            
        plot_ind += 1
        # Tucker-1 Plots
        if self.plots[plot_ind] in self.active_plots:
            if self.plot_ok(['Common Scores'], Tucker1Plotter, selection=0):
                filename = outputdir + "/"+ self.int2str(plot_ind) +"_tucker1_common_scores" + ext
                self.save_image_file(self.canvas, filename, dpi=dpi)
                if self.no_to_all: progress.Destroy(); return 
            _nr = 1
            for ass in self.active_ass:
                if self.plot_ok([ass], Tucker1Plotter, selection=0):
                    filename = outputdir + "/"+ self.int2str(plot_ind) +"b_tucker1_ass" + self.int2str(_nr) + "_" + re.sub(' ', '_', self.ascii_enc(ass)) + ext
                    self.save_image_file(self.canvas, filename, dpi=dpi); _nr += 1
                    if self.no_to_all: progress.Destroy(); return 
            for att in self.active_att:
                if self.plot_ok([att], Tucker1Plotter, selection=0):
                    filename = outputdir + "/"+ self.int2str(plot_ind) +"c_tucker1_att" + self.int2str(_nr) + "_" + re.sub(' ', '_', self.ascii_enc(att)) + ext
                    self.save_image_file(self.canvas, filename, dpi=dpi); _nr += 1
                    if self.no_to_all: progress.Destroy(); return 
            current_value = int(math.ceil(part*_index)); _index += 1
            progress.set_gauge(value=current_value)         
        
        plot_ind += 1
        # Tucker-1 Standardize Plots
        if self.plots[plot_ind] in self.active_plots:
            if self.plot_ok(['Common Scores'], Tucker1Plotter, selection=1):
                filename = outputdir + "/"+ self.int2str(plot_ind) +"_tucker1_standard_common_scores" + ext
                self.save_image_file(self.canvas, filename, dpi=dpi)
                if self.no_to_all: progress.Destroy(); return
            _nr = 1
            for ass in self.active_ass:
                if self.plot_ok([ass], Tucker1Plotter, selection=1):
                    filename = outputdir + "/"+ self.int2str(plot_ind) +"b_tucker1_standard_ass" + self.int2str(_nr) + "_" + re.sub(' ', '_', self.ascii_enc(ass)) + ext
                    self.save_image_file(self.canvas, filename, dpi=dpi); _nr += 1
                    if self.no_to_all: progress.Destroy(); return 
            for att in self.active_att:
                if self.plot_ok([att], Tucker1Plotter, selection=1):
                    filename = outputdir + "/"+ self.int2str(plot_ind) +"c_tucker1_standard_att" + self.int2str(_nr) + "_" + re.sub(' ', '_', self.ascii_enc(att)) + ext
                    self.save_image_file(self.canvas, filename, dpi=dpi); _nr += 1
                    if self.no_to_all: progress.Destroy(); return 
            current_value = int(math.ceil(part*_index)); _index += 1
            progress.set_gauge(value=current_value) 

        plot_ind += 1
        # Consensus Original
        if self.plots[plot_ind] in self.active_plots:
            _list = [u'PCA Scores', u'PCA Loadings', u'PCA Correlation Loadings', u'PCA Explained Variance', 'Spiderweb Plot', 'Bi-Plot']
            type_ind = 1
            for type in _list:
                if self.plot_ok([type], PCA_plotter, selection=0):
                    filename = outputdir + "/"+ self.int2str(plot_ind) +"_consensus_original"+ str(type_ind) + ext
                    self.save_image_file(self.canvas, filename, dpi=dpi)
                    if self.no_to_all: progress.Destroy(); return 
                type_ind += 1
            current_value = int(math.ceil(part*_index)); _index += 1
            progress.set_gauge(value=current_value)       
        
        plot_ind += 1
        # Consensus Standardized
        if self.plots[plot_ind] in self.active_plots:
            _list = [u'PCA Scores', u'PCA Loadings', u'PCA Correlation Loadings', u'PCA Explained Variance', 'Spiderweb Plot', 'Bi-Plot']
            type_ind = 1
            for type in _list:
                if self.plot_ok([type], PCA_plotter, selection=1):
                    filename = outputdir + "/"+ self.int2str(plot_ind) +"_consensus_standardized"+ str(type_ind) + ext
                    self.save_image_file(self.canvas, filename, dpi=dpi)
                    if self.no_to_all: progress.Destroy(); return 
                type_ind += 1
            current_value = int(math.ceil(part*_index)); _index += 1
            progress.set_gauge(value=current_value)

        plot_ind += 1
        # STATIS Cov
        if self.plots[plot_ind] in self.active_plots:
            selection = 0 # covariance
            _list = [u'PCA Scores', u'PCA Loadings', u'PCA Correlation Loadings', u'PCA Explained Variance', 'Spiderweb Plot', 'Bi-Plot']
            type_ind = 1
            for type in _list:
                if self.plot_ok([type], STATIS_PCA_Plotter, selection):
                    filename = outputdir + "/"+ self.int2str(plot_ind) +"_statis"+ str(type_ind) + "_cov" + ext
                    self.save_image_file(self.canvas, filename, dpi=dpi)
                    if self.no_to_all: progress.Destroy(); return 
                type_ind += 1            
            if self.plot_ok([u'Assessor Weight'], STATIS_AssWeight_Plotter, selection): 
                filename = outputdir + "/"+ self.int2str(plot_ind) +"_statis5_cov_ass_weight" + ext
                self.save_image_file(self.canvas, filename, dpi=dpi)
                if self.no_to_all: progress.Destroy(); return
            current_value = int(math.ceil(part*_index)); _index += 1
            progress.set_gauge(value=current_value)


        plot_ind += 1
        # STATIS Corr
        if self.plots[plot_ind] in self.active_plots:
            selection = 1 # correlation
            _list = [u'PCA Scores', u'PCA Loadings', u'PCA Correlation Loadings', u'PCA Explained Variance', 'Spiderweb Plot', 'Bi-Plot', 'Assessor Weight']
            type_ind = 1
            for type in _list:
                if type == "Assessor Weight":
                    plotter = STATIS_AssWeight_Plotter
                else:
                    plotter = STATIS_AssWeight_Plotter
                if self.plot_ok([type], plotter, selection):
                    filename = outputdir + "/"+ self.int2str(plot_ind) +"_statis"+ str(type_ind) + "_corr" + ext
                    self.save_image_file(self.canvas, filename, dpi=dpi)
                    if self.no_to_all: progress.Destroy(); return 
                type_ind += 1            
            current_value = int(math.ceil(part*_index)); _index += 1
            progress.set_gauge(value=current_value)

        plot_ind += 1
        # Manhattan Original
        if self.plots[plot_ind] in self.active_plots:
            type_ind = 1
            for ass in self.active_ass:
                if self.plot_ok([ass], ManhattanPlotter, selection=0):
                    filename = outputdir + "/"+ self.int2str(plot_ind) +"_manhattan_original"+ str(type_ind) + ext
                    self.save_image_file(self.canvas, filename, dpi=dpi)
                    if self.no_to_all: progress.Destroy(); return 
                type_ind += 1
            current_value = int(math.ceil(part*_index)); _index += 1
            progress.set_gauge(value=current_value)       
        
        plot_ind += 1
        # Manhattan Standardized
        if self.plots[plot_ind] in self.active_plots:
            type_ind = 1
            for ass in self.active_ass:
                if self.plot_ok([ass], ManhattanPlotter, selection=1):
                    filename = outputdir + "/"+ self.int2str(plot_ind) +"_manhattan_standardized"+ str(type_ind) + ext
                    self.save_image_file(self.canvas, filename, dpi=dpi)
                    if self.no_to_all: progress.Destroy(); return 
                type_ind += 1
            current_value = int(math.ceil(part*_index)); _index += 1
            progress.set_gauge(value=current_value)

 
        plot_ind += 1
        # Mixed Model ANOVA
        if self.plots[plot_ind] in self.active_plots:
            _nr = 1      
            _types = ['F1', 'F2']
            for _type in _types:         
                if self.plot_ok([_type], MixModel_ANOVA_Plotter_2way1rep):
                    filename = outputdir + "/"+ self.int2str(plot_ind) +"_mm_anova_f_" +str(_nr)+ ext; _nr += 1
                    self.save_image_file(self.canvas, filename, dpi=dpi)
                    if self.no_to_all: progress.Destroy(); return   
            lsd_types = ['LSD1', 'LSD2']
            _nr = 1
            for _type in lsd_types:
                if self.plot_ok([_type], MixModel_ANOVA_LSD_Plotter_2way1rep):
                    filename = outputdir + "/"+ self.int2str(plot_ind) +"_mm_anova_lsd_" +str(_nr)+ ext; _nr += 1
                    self.save_image_file(self.canvas, filename, dpi=dpi)
                    if self.no_to_all: progress.Destroy(); return
            current_value = int(math.ceil(part*_index)); _index += 1
            progress.set_gauge(value=current_value)                 

        plot_ind += 1
        # Mixed Model ANOVA
        if self.plots[plot_ind] in self.active_plots:
            _nr = 1
            _types = ['F1', 'F2', 'F3']
            for _type in _types:         
                if self.plot_ok([_type], MixModel_ANOVA_Plotter_2way):
                    filename = outputdir + "/"+ self.int2str(plot_ind) +"_mm_anova_f_" +str(_nr)+ ext; _nr += 1
                    self.save_image_file(self.canvas, filename, dpi=dpi)
                    if self.no_to_all: progress.Destroy(); return   
            lsd_types = ['LSD1', 'LSD2']
            _nr = 1
            for _type in lsd_types:
                if self.plot_ok([_type], MixModel_ANOVA_LSD_Plotter_2way):
                    filename = outputdir + "/"+ self.int2str(plot_ind) +"_mm_anova_lsd_" +str(_nr)+ ext; _nr += 1
                    self.save_image_file(self.canvas, filename, dpi=dpi)
                    if self.no_to_all: progress.Destroy(); return
            current_value = int(math.ceil(part*_index)); _index += 1
            progress.set_gauge(value=current_value) 
                    
        plot_ind += 1
        # Mixed Model ANOVA     
        if self.plots[plot_ind] in self.active_plots:
            _nr = 1
            _types = ['F1', 'F2', 'F3', 'F4']
            for _type in _types:         
                if self.plot_ok([_type], MixModel_ANOVA_Plotter_3way):
                    filename = outputdir + "/"+ self.int2str(plot_ind) +"_mm_anova_f_" +str(_nr)+ ext; _nr += 1
                    self.save_image_file(self.canvas, filename, dpi=dpi)
                    if self.no_to_all: progress.Destroy(); return   
            lsd_types = ['LSD1', 'LSD2']
            _nr = 1
            for _type in lsd_types:
                if self.plot_ok([_type], MixModel_ANOVA_LSD_Plotter_3way):
                    filename = outputdir + "/"+ self.int2str(plot_ind) +"_mm_anova_lsd_" +str(_nr)+ ext; _nr += 1
                    self.save_image_file(self.canvas, filename, dpi=dpi)
                    if self.no_to_all: progress.Destroy(); return
            current_value = int(math.ceil(part*_index)); _index += 1
            progress.set_gauge(value=current_value)                    
 
 
        progress.set_gauge(value=100, text="Done\n")
        progress.Destroy()


    def save_ppt_file(self, image_files, pdf_file):
        plt.savefigure(pdf_file)

    def char_ok(self, c):
        test_pattern = r'[a-zA-Z_0-9]'
        if re.search(test_pattern, c) != None:
            return True
        else:
            return False
            
    
    def ascii_encode(self, obj):
        """ 
        returns the decoded unicode representation of obj 
        
        Also removes some characters not used in dir or file names ie.
        """
        return obj.encode('ascii', 'ignore') # remove bad characters
         
        
        
        
    def ascii_enc(self, obj):
        """ 
        returns the decoded unicode representation of obj 
        
        Also removes some characters not used in dir or file names ie.
        """
        #new_obj = obj.encode('ascii', 'ignore') # remove bad characters
        
        ret_obj = ""
        # for each character
        for c in obj:
            if self.char_ok(c): ret_obj += c
        return ret_obj
        
        
    def save_image_file(self, canvas, file, dpi):
        """
        Saves image file
        
        @type file:	string
        @param file:	absolute file path 
        
        @type image:	wx.Image
        @param image:	image data to be saved
        
        @type type:	int
        @param type:	file type         
        """
        file = file.encode(codec)
    
        canvas.figure.text(0.01, 0.01, "PanelCheck", fontdict={'fontname':'Arial Narrow','color': 'black','fontweight':'bold','fontsize':14,'alpha':0.25})        
    
	if self.yes_to_all:
	    canvas.print_figure(file, dpi=dpi)
	    self.image_files.append(file)
	elif os.path.isfile(file):  # does file exist?
	    save = False
	    #splitted = split_path(file)
	    string = file
	    if len(string) > 55: string = string[:15] + " ... " + string[-35:]
	    dlg = SaveDialog(self.parent, string)
	    dlg.CenterOnScreen()
	    code = dlg.ShowModal()
	    if code == dlg.id_yes:
	        save = True
	    elif code == dlg.id_yes_all:
	        self.yes_to_all = True; save = True
	    elif code == dlg.id_no:
	        save = False
	    else:
	        self.no_to_all = True;
	        save = False # no to all
	    dlg.Destroy()
	    if save:
	        canvas.print_figure(file, dpi=dpi)
	        self.image_files.append(file)	    
	else:
	    canvas.print_figure(file, dpi=dpi)
	    self.image_files.append(file)       
    
        del canvas.figure.texts[-1]
        
        
class SaveDialog(wx.Dialog):
    """
    Custom dialog class, for having the "Yes to all" button
    """
    def __init__(self, prnt, file, yesToAll_btn=True, noToAll_btn=True):
        wx.Dialog.__init__(self, parent=prnt,id=-1, 
              pos=wx.DefaultPosition, size=wx.DefaultSize,
              style=wx.DEFAULT_DIALOG_STYLE, title=u'Overwrite?')

        box = wx.BoxSizer(wx.VERTICAL)        
        text = wx.StaticText(self, id=wx.NewId(), label=u'File exists:\n'+file+'\n\nDo you wish to overwrite?')
    
        
        btnsizer = wx.BoxSizer(wx.HORIZONTAL)
        
        self.id_yes = wx.NewId(); self.id_yes_all = wx.NewId(); 
        self.id_no = wx.NewId(); self.id_no_all = wx.NewId(); 
        yes = wx.Button(self, id=self.id_yes, label=u'Yes')
        yes.Bind(wx.EVT_BUTTON, self.onYes, id=self.id_yes)
        if yesToAll_btn:
            yes_to_all = wx.Button(self, id=self.id_yes_all, label=u'Yes to all')
            yes_to_all.Bind(wx.EVT_BUTTON, self.onYesAll, id=self.id_yes_all)
        no = wx.Button(self, id=self.id_no, label=u'No')
        no.Bind(wx.EVT_BUTTON, self.onNo, id=self.id_no)
        if noToAll_btn:
            no_all = wx.Button(self, id=self.id_no_all, label=u'No to all')
            no_all.Bind(wx.EVT_BUTTON, self.onNoAll, id=self.id_no_all)
        
        btnsizer.Add(yes, 0, wx.EXPAND)
        if yesToAll_btn:
            btnsizer.Add(yes_to_all, 0, wx.EXPAND)
        btnsizer.Add(no, 0, wx.EXPAND)
        if noToAll_btn:
            btnsizer.Add(no_all, 0, wx.EXPAND)

        box.Add(text, 0, wx.ALIGN_CENTER|wx.ALL, 5)
        box.Add(btnsizer, 0, wx.ALIGN_CENTER|wx.ALL, 5)
        
        self.SetSizer(box)
        #box.Fit(self)
        self.SetSize((400, 150))
        
    def onYes(self, event):
        self.EndModal(self.id_yes)
        
    def onYesAll(self, event):
        self.EndModal(self.id_yes_all)
        
    def onNo(self, event):
        self.EndModal(self.id_no)
        
    def onNoAll(self, event):
        self.EndModal(self.id_no_all)