#import psyco
#psyco.full()


import sys, os, wx

import wx.lib.colourdb
from About import *
from LoadData import *
from FileOpen_Summary import *
from PlotFrame import *
from Export import *
from PanelCheck_IO import *
from PanelCheck_Tools import *
from TabbedPanel import TabPanel, RadioTabPanel
import xlrd

#Plots
from PanelCheck_Plots import *

##from IPython.Shell import IPShellEmbed
##ipshell = IPShellEmbed()

def create(parent, filename, delimiter):
    return Main_Frame(parent, filename, delimiter)

[wxID_MAIN_FRAMEMENUFILECLOSE_FILE, wxID_MAIN_FRAMEMENUFILEEXIT,
 wxID_MAIN_FRAMEMENUFILEIMPORT,
] = [wx.NewId() for _init_coll_menuFile_Items in range(3)]

[wxID_MAIN_FRAMEMENUHELPABOUT, wxID_MAIN_FRAMEMENUHELPMANUAL,
] = [wx.NewId() for _init_coll_menuHelp_Items in range(2)]

[wxID_MAIN_FRAMEMENUFILEIMPORTCOMPUSENSE, wxID_MAIN_FRAMEMENUFILEIMPORTEXCEL,
 wxID_MAIN_FRAMEMENUFILEIMPORTFIZZ, wxID_MAIN_FRAMEMENUFILEIMPORTPLAIN,
] = [wx.NewId() for _init_coll_menuFileImport_Items in range(4)]

[wxID_MAIN_FRAMEMENUVIEWGRID, wxID_MAIN_FRAMEMENUVIEWLEGEND,
] = [wx.NewId() for _init_coll_menuView_Items in range(2)]

class Main_Frame(wx.Frame):
#---GUI construction---#FFFFFF#FF8040-------------------------------------------

    def _init_coll_menuBar_Menus(self, parent):

        parent.Append(menu=self.menuFile, title=u'File')
        parent.Append(menu=self.menuView, title=u'Options')
        parent.Append(menu=self.menuHelp, title=u'Help')

    def _init_coll_menuFileImport_Items(self, parent):

        parent.Append(
          #  
          id=wxID_MAIN_FRAMEMENUFILEIMPORTPLAIN,
              kind=wx.ITEM_NORMAL, item=u'Plain Text (Tab delimited)')
        cd_id = wx.NewId(); sd_id = wx.NewId(); pc_id = wx.NewId()
        parent.Append(id=cd_id, kind=wx.ITEM_NORMAL, item=u'Plain Text (Comma delimited)')
        parent.Append(id=sd_id, kind=wx.ITEM_NORMAL, item=u'Plain Text (Semicolon delimited)')
        parent.AppendSeparator()
        parent.Append(id=wxID_MAIN_FRAMEMENUFILEIMPORTEXCEL,
              kind=wx.ITEM_NORMAL, item=u'Excel...')
        parent.AppendSeparator()
        parent.Append(id=pc_id,
              kind=wx.ITEM_NORMAL, item=u'PanelCheck file...')


        #parent.Append(  id=wxID_MAIN_FRAMEMENUFILEIMPORTFIZZ,
        #      kind=wx.ITEM_NORMAL, item=u'FIZZ')
        #parent.Append(  id=wxID_MAIN_FRAMEMENUFILEIMPORTCOMPUSENSE,
        #      kind=wx.ITEM_NORMAL, item=u'Compusense')
        self.Bind(wx.EVT_MENU, self.OnMenuFileOpen_plainMenu,
              id=wxID_MAIN_FRAMEMENUFILEIMPORTPLAIN)
        #self.Bind(wx.EVT_MENU, self.OnMenuFileOpen_fizzMenu,
        #      id=wxID_MAIN_FRAMEMENUFILEIMPORTFIZZ)
        self.Bind(wx.EVT_MENU, self.OnMenuFileOpen_CD_Menu, id=cd_id)
        self.Bind(wx.EVT_MENU, self.OnMenuFileOpen_SD_Menu, id=sd_id)
        self.Bind(wx.EVT_MENU, self.OnMenuFileOpen_excelMenu,
              id=wxID_MAIN_FRAMEMENUFILEIMPORTEXCEL)
        self.Bind(wx.EVT_MENU, self.OnMenuFileOpen_PC_Menu, id=pc_id)
        #self.Bind(wx.EVT_MENU, self.OnMenuFileOpen_compusenseMenu,
        #      id=wxID_MAIN_FRAMEMENUFILEIMPORTCOMPUSENSE)

    def _init_coll_menuHelp_Items(self, parent):
        workflow_id = wx.NewId()
        parent.Append(
          #  
          id=workflow_id,
              kind=wx.ITEM_NORMAL, item=u'Workflow')
        parent.Append(
          #  
          id=wxID_MAIN_FRAMEMENUHELPMANUAL,
              kind=wx.ITEM_NORMAL, item=u'Manual (V1.2.1)')
        parent.Append(
          #  
          id=wxID_MAIN_FRAMEMENUHELPABOUT,
              kind=wx.ITEM_NORMAL, item=u'About')
        self.Bind(wx.EVT_MENU, self.OnMenuHelpManualMenu,
              id=wxID_MAIN_FRAMEMENUHELPMANUAL)
        self.Bind(wx.EVT_MENU, self.OnMenuHelpAboutMenu,
              id=wxID_MAIN_FRAMEMENUHELPABOUT)
        self.Bind(wx.EVT_MENU, self.OnMenuHelpWorkflowMenu,
              id=workflow_id)

    def _init_coll_menuFile_Items(self, parent):

        self.menuFileExport = wx.Menu(title='')
        self.menuFileRecent = wx.Menu(title='')
        self.recent_id = wx.NewId()
        si_id = wx.NewId(); ppt_id = wx.NewId(); save_id = wx.NewId();
        self.menuFileExport.Append(
          # 
          id=si_id, kind=wx.ITEM_NORMAL, item=u'Image Files...')
        self.menuFileExport.Append(
         #   
          id=ppt_id, kind=wx.ITEM_NORMAL, item=u'PowerPoint File...')
        self.Bind(wx.EVT_MENU, self.OnMenuFileExportImages_Menu, id=si_id)
        self.Bind(wx.EVT_MENU, self.OnMenuFileExportPPT_Menu, id=ppt_id)

        parent.AppendSubMenu(
              submenu=self.menuFileImport,
               
            #  id=wxID_MAIN_FRAMEMENUFILEIMPORT,
              text=u'Import')

        parent.AppendSubMenu(
          submenu=self.menuFileRecent,
            
          #id=wx.NewId(),
          text=u'Import Recent'
              )
        parent.AppendSubMenu(
          submenu=self.menuFileExport,
           
          #id=wx.NewId(),
          text=u'Export'
              )

        parent.Append(
          # 
          id=save_id,
          item='Save File...',
          kind=wx.ITEM_NORMAL, 
          )

        parent.Append(
          # 
          id=wxID_MAIN_FRAMEMENUFILECLOSE_FILE,
              kind=wx.ITEM_NORMAL, item='Close File')
        parent.Append(
          #  
          id=wxID_MAIN_FRAMEMENUFILEEXIT,
              kind=wx.ITEM_NORMAL, item='Exit')
        self.Bind(wx.EVT_MENU, self.OnMenuFileClose_fileMenu,
              id=wxID_MAIN_FRAMEMENUFILECLOSE_FILE)
        self.Bind(wx.EVT_MENU, self.OnMenuFileExitMenu,
              id=wxID_MAIN_FRAMEMENUFILEEXIT)
        self.Bind(wx.EVT_MENU, self.OnMenuFileSave,
              id=save_id)


    def _init_coll_menuView_Items(self, parent):
        self.menuViewPlot = wx.Menu(title='')
        self.menuOptionsGrid = self.menuViewPlot.Append( id=wxID_MAIN_FRAMEMENUVIEWGRID,
              kind=wx.ITEM_CHECK, item=u'View Grid')
        self.menuOptionsLegend = self.menuViewPlot.Append( id=wxID_MAIN_FRAMEMENUVIEWLEGEND,
              kind=wx.ITEM_CHECK, item=u'View Legend')


        self.menuViewSelect = wx.Menu(title='')
        selectAll_id = wx.NewId();
        self.menuOptionsSelectAll = self.menuViewSelect.Append(  id=selectAll_id,
              kind=wx.ITEM_CHECK, item=u'Equal for all Plots')



        parent.Append( 
          id=wxID_MAIN_FRAMEMENUFILEIMPORT,
          item=u'Plot',
          subMenu=self.menuViewPlot)

        parent.Append(  
          id=wxID_MAIN_FRAMEMENUFILEIMPORT,
          item=u'Selection',
          subMenu=self.menuViewSelect, )

        self.menuOptionsLegend.Check(True)
        self.menuOptionsSelectAll.Check(True)

        #self.menuViewLegend = True
        self.Bind(wx.EVT_MENU, self.OnMenuViewGridMenu,
              id=wxID_MAIN_FRAMEMENUVIEWGRID)
        self.Bind(wx.EVT_MENU, self.OnMenuViewLegendMenu,
              id=wxID_MAIN_FRAMEMENUVIEWLEGEND)



    def _init_coll_main_notebook_Pages(self, parent):
        parent.AddPage(imageId=-1, page=self.uni_notebook, select=True,
              text=u'Univariate')
        parent.AddPage(imageId=-1, page=self.multi_notebook, select=False,
              text=u'Multivariate')
        parent.AddPage(imageId=-1, page=self.avgr_notebook, select=False,
              text=u'Consensus')
        parent.AddPage(imageId=-1, page=self.overall_notebook, select=False,
              text=u'Overall')

        self.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGING, self.OnPageChanging, id=parent.GetId())
        self.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGED, self.OnPageChanged, id=parent.GetId())

    def _init_coll_uni_notebook_Pages(self, parent):
        _and = '&&'
        parent.AddPage(imageId=-1, page=self.line_panel, select=True,
              text=u'Line Plots')
        parent.AddPage(imageId=-1, page=self.mean_std_panel, select=False,
              text=u'Mean '+ _and +' STD Plots')
        parent.AddPage(imageId=-1, page=self.corr_panel, select=False,
              text=u'Correlation Plots')
        parent.AddPage(imageId=-1, page=self.profile_panel, select=False,
              text=u'Profile Plots')
        parent.AddPage(imageId=-1, page=self.egg_panel, select=False,
              text=u'Eggshell Plots')
        parent.AddPage(imageId=-1, page=self.f_panel, select=False,
              text=u'F ' + _and + ' p Plots')
        parent.AddPage(imageId=-1, page=self.mse_panel, select=False,
              text=u'MSE Plots')
        parent.AddPage(imageId=-1, page=self.pmse_panel, select=False,
              text=u'p-MSE Plots')

        self.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGING, self.OnPageChanging, id=parent.GetId())
        self.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGED, self.OnPageChanged, id=parent.GetId())

    def _init_coll_multi_notebook_Pages(self, parent):
        parent.AddPage(imageId=-1, page=self.tuck1_panel, select=True,
              text=u'Tucker-1 Plots')
        parent.AddPage(imageId=-1, page=self.manh_panel, select=False,
              text=u'Manhattan Plots')

        self.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGING, self.OnPageChanging, id=parent.GetId())
        self.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGED, self.OnPageChanged, id=parent.GetId())

    def _init_coll_avgr_notebook_Pages(self, parent):
        parent.AddPage(imageId=-1, page=self.org_panel, select=True,
              text=u'Original')
        parent.AddPage(imageId=-1, page=self.std_panel, select=False,
              text=u'Standardized')
        parent.AddPage(imageId=-1, page=self.statis_panel, select=False,
              text=u'STATIS')

        self.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGING, self.OnPageChanging, id=parent.GetId())
        self.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGED, self.OnPageChanged, id=parent.GetId())

    def _init_coll_overall_notebook_Pages(self, parent):
        parent.AddPage(imageId=-1, page=self.mm_anova_panel1, select=True,
              text=u'2-way ANOVA (1 rep)')
        parent.AddPage(imageId=-1, page=self.mm_anova_panel2, select=False,
              text=u'2-way ANOVA')
        parent.AddPage(imageId=-1, page=self.mm_anova_panel3, select=False,
              text=u'3-way ANOVA')                     
        #parent.AddPage(imageId=-1, page=self.perf_ind_panel, select=False, item=u'Performance Indices')

        self.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGING, self.OnPageChanging, id=parent.GetId())
        self.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGED, self.OnPageChanged, id=parent.GetId())

    def _init_coll_statusBar_Fields(self, parent):
        parent.SetFieldsCount(1)

        parent.SetStatusText(i=0, text=u'status')

        parent.SetStatusWidths([-1])

    def _init_utils(self):
        self.menuFile = wx.Menu(title=u'')

        self.menuHelp = wx.Menu(title=u'')

        self.menuBar = wx.MenuBar()

        self.menuFileImport = wx.Menu(title='')

        self.menuView = wx.Menu(title='')

        self._init_coll_menuFile_Items(self.menuFile)
        self._init_coll_menuHelp_Items(self.menuHelp)
        self._init_coll_menuBar_Menus(self.menuBar)
        self._init_coll_menuFileImport_Items(self.menuFileImport)
        self._init_coll_menuView_Items(self.menuView)


    def _init_ctrls(self, prnt):
        wx.Frame.__init__(self, id=wx.NewId(), name=u'Main_Frame',
              parent=prnt, pos=wx.Point(331, 170), size=wx.Size(875, 560),
              style=wx.DEFAULT_FRAME_STYLE, title='PanelCheck V1.4.2')
        self._init_utils()
        self.SetClientSize(wx.Size(875, 560))
        self.SetAutoLayout(True)
        self.SetMenuBar(self.menuBar)
        self.Bind(wx.EVT_CLOSE, self.OnMain_FrameClose)

        self.statusBar = wx.StatusBar(id=wx.NewId(),
              name=u'statusBar', parent=self, style=0)
        self.statusBar.SetToolTip(u'statusBar')
        self._init_coll_statusBar_Fields(self.statusBar)
        self.SetStatusBar(self.statusBar)

        self.main_notebook = wx.Notebook(id=wx.NewId(),
              name=u'main_notebook', parent=self, pos=wx.Point(0, 0),
              size=wx.Size(752, 465),
              style=wx.NB_FIXEDWIDTH | wx.TAB_TRAVERSAL)




        self.uni_notebook = wx.Notebook(id=wx.NewId(),
              name=u'uni_notebook', parent=self.main_notebook, pos=wx.Point(0,
              0), size=wx.Size(744, 436), style=0)

        self.multi_notebook = wx.Notebook(id=wx.NewId(),
              name=u'multi_notebook', parent=self.main_notebook, pos=wx.Point(0,
              0), size=wx.Size(744, 436), style=0)

        self.avgr_notebook = wx.Notebook(id=wx.NewId(),
              name=u'avgr_notebook', parent=self.main_notebook, pos=wx.Point(0,
              0), size=wx.Size(744, 436), style=0)

        self.overall_notebook = wx.Notebook(id=wx.NewId(),
              name=u'overall_notebook', parent=self.main_notebook, pos=wx.Point(0,
              0), size=wx.Size(744, 436), style=0)



        self.choice_label = wx.StaticText(id=wx.NewId(), label=u'Enable/Disable every:',
              name='choice_label', parent=self.main_notebook, pos=wx.Point(600,
              -14), size=wx.Size(125, 16), style=0)
        self.choice_label.SetBackgroundColour(wx.SystemSettings.GetColour(wx.SYS_COLOUR_BTNFACE).Get())

        self.choice = wx.Choice(choices=["Single-select", " 1st", " 2nd", " 3rd",
              " 4th", " 5th", " 6th", " 7th", " 8th", " 9th", " 10th"], id=wx.NewId(),
              name='choice', parent=self.main_notebook, pos=wx.Point(740, -16),
              size=wx.Size(100, 24), style=0)
        self.choice.SetSelection(0)

        #self.butt_workflow = wx.Button(id=wx.NewId(), label="Workflow", parent=self.main_notebook, size=wx.Size(75, 24), pos=wx.Point(750, 0))




        self.line_panel = TabPanel(parent=self.uni_notebook, func=self.create_plot, choice=self.choice)

        self.mean_std_panel = TabPanel(parent=self.uni_notebook, func=self.create_plot, choice=self.choice)

        self.corr_panel = TabPanel(parent=self.uni_notebook, func=self.create_plot, choice=self.choice)

        self.profile_panel = RadioTabPanel(parent=self.uni_notebook, func_list=[self.create_plot, self.show_profilePlot_tree, self.show_profilePlot_tree], choice=self.choice, radiobox_choices=["Sample averages", "Sample Replicates"], radio_label="Show:")
        self.profile_radioBoxModel = wx.RadioBox(choices=["Increasing intensity", "Original sample order"],
              id=-1, label="Sorting:", parent=self.profile_panel,
              size=wx.DefaultSize,
              style=wx.RA_SPECIFY_COLS)
        self.profile_panel.lower_right_sizer.AddSpacer(5)
        self.profile_panel.lower_right_sizer.Add(self.profile_radioBoxModel, 0, wx.GROW)





        self.egg_panel = TabPanel(parent=self.uni_notebook, func=self.create_plot, choice=self.choice)

        self.f_panel = RadioTabPanel(parent=self.uni_notebook, func_list=[self.create_plot, self.show_fPlot_tree_assessor, self.show_fPlot_tree_attribute], choice=self.choice, radiobox_choices=["Assessors", "Attributes"], radio_label="Sorted by:")

        self.mse_panel = RadioTabPanel(parent=self.uni_notebook, func_list=[self.create_plot, self.show_msePlot_tree_assessor, self.show_msePlot_tree_attribute], choice=self.choice, radiobox_choices=["Assessors", "Attributes"], radio_label="Sorted by:")

        self.pmse_panel = TabPanel(parent=self.uni_notebook, func=self.create_plot, choice=self.choice)



        self.tuck1_panel = RadioTabPanel(parent=self.multi_notebook, func_list=[self.create_plot, self.show_tuck1Plot_tree, self.show_tuck1Plot_tree], choice=self.choice, radiobox_choices=["None", "Standardize"], radio_label="Variable standardization:")

        box = wx.StaticBox(self.tuck1_panel, -1, "Axis options:")
        bsizer = wx.StaticBoxSizer(box, wx.HORIZONTAL)
        self.tuck1_cb = wx.CheckBox(self.tuck1_panel, -1, label="Equal axis")
        self.tuck1_panel.lower_right_sizer.AddSpacer(5)
        bsizer.AddSpacer(5)
        bsizer.Add(self.tuck1_cb, 0, wx.FIXED_MINSIZE|wx.ALIGN_CENTER_VERTICAL)
        bsizer.AddSpacer(5)
        self.tuck1_radioBoxModel = wx.RadioBox(choices=["Sample averages", "Sample replicates"],
              id=-1, label="Model based on:", parent=self.tuck1_panel,
              size=wx.DefaultSize,
              style=wx.RA_SPECIFY_COLS)
        self.tuck1_panel.lower_right_sizer.Add(self.tuck1_radioBoxModel, 0, wx.GROW)
        self.tuck1_panel.lower_right_sizer.AddSpacer(5)
        self.tuck1_panel.lower_right_sizer.Add(bsizer, 0, wx.GROW)




        self.manh_panel = RadioTabPanel(parent=self.multi_notebook, func_list=[self.create_plot, self.show_manhattan_tree, self.show_manhattan_tree], choice=self.choice, radiobox_choices=["None", "Standardize"], radio_label="Variable standardization:")

        box = wx.StaticBox(self.manh_panel, -1, "Max. PCs:")
        bsizer = wx.StaticBoxSizer(box, wx.HORIZONTAL)
        self.manh_spin_txt = wx.TextCtrl(self.manh_panel, -1, size=(50, 25), value="6", style=wx.TE_READONLY)
        self.manh_spin = wx.SpinButton(self.manh_panel, -1, size=(25, 25), style=wx.SP_VERTICAL)
        self.manh_spin.SetRange(1, 100)
        self.manh_spin.SetValue(6)
        self.manh_panel.lower_right_sizer.AddSpacer(5)
        bsizer.AddSpacer(5)
        bsizer.Add(self.manh_spin_txt, 0, wx.FIXED_MINSIZE|wx.ALIGN_CENTER_VERTICAL)
        bsizer.Add(self.manh_spin, 0, wx.FIXED_MINSIZE|wx.ALIGN_CENTER_VERTICAL)
        bsizer.AddSpacer(5)
        self.manh_panel.lower_right_sizer.Add(bsizer, 0, wx.GROW)
        self.Bind(wx.EVT_SPIN, self.onManhSpin, self.manh_spin)



        self.org_panel = TabPanel(parent=self.avgr_notebook, func=self.create_plot, choice=self.choice)
        box = wx.StaticBox(self.org_panel, -1, "Axis options:")
        bsizer = wx.StaticBoxSizer(box, wx.HORIZONTAL)
        self.org_cb = wx.CheckBox(self.org_panel, -1, label="Equal axis")
        #self.org_panel.right_part.AddSpacer(10)
        bsizer.AddSpacer(5)
        bsizer.Add(self.org_cb, 0, wx.FIXED_MINSIZE|wx.ALIGN_CENTER_VERTICAL)
        bsizer.AddSpacer(5)
        self.org_panel.right_part.Add(bsizer, 0, wx.FIXED_MINSIZE)
        self.org_panel.right_part.AddSpacer(10)


        self.std_panel = TabPanel(parent=self.avgr_notebook, func=self.create_plot, choice=self.choice)
        box = wx.StaticBox(self.std_panel, -1, "Axis options:")
        bsizer = wx.StaticBoxSizer(box, wx.HORIZONTAL)
        self.std_cb = wx.CheckBox(self.std_panel, -1, label="Equal axis")
        #self.std_panel.right_part.AddSpacer(10)
        bsizer.AddSpacer(5)
        bsizer.Add(self.std_cb, 0, wx.FIXED_MINSIZE|wx.ALIGN_CENTER_VERTICAL)
        bsizer.AddSpacer(5)
        self.std_panel.right_part.Add(bsizer, 0, wx.FIXED_MINSIZE)
        self.std_panel.right_part.AddSpacer(10)


        self.statis_panel = RadioTabPanel(parent=self.avgr_notebook, func_list=[self.create_plot, self.show_statis_tree, self.show_statis_tree], choice=self.choice, radiobox_choices=["Covariance", "Correlation"], radio_label="STATIS based on:")
        box = wx.StaticBox(self.statis_panel, -1, "Axis options:")
        bsizer = wx.StaticBoxSizer(box, wx.HORIZONTAL)
        self.statis_cb = wx.CheckBox(self.statis_panel, -1, label="Equal axis")
        self.statis_panel.lower_right_sizer.AddSpacer(5)
        bsizer.AddSpacer(5)
        bsizer.Add(self.statis_cb, 0, wx.FIXED_MINSIZE|wx.ALIGN_CENTER_VERTICAL)
        bsizer.AddSpacer(5)
        self.statis_panel.lower_right_sizer.Add(bsizer, 0, wx.GROW)





        self.mm_anova_panel1 = TabPanel(parent=self.overall_notebook, func=self.create_plot, choice=self.choice)

        self.mm_anova_panel2 = TabPanel(parent=self.overall_notebook, func=self.create_plot, choice=self.choice)

        self.mm_anova_panel3 = TabPanel(parent=self.overall_notebook, func=self.create_plot, choice=self.choice)


        """
        self.perf_ind_panel = TabPanel(parent=self.overall_notebook, func=self.create_plot, choice=self.choice)        
        boxMain = wx.BoxSizer(wx.HORIZONTAL)
        box = wx.StaticBox(self.perf_ind_panel, -1, "Set target level:")
        bsizer = wx.StaticBoxSizer(box, wx.VERTICAL)      
        bsizerAGR = wx.BoxSizer(wx.HORIZONTAL)
        bsizerREP = wx.BoxSizer(wx.HORIZONTAL)
        bsizerDIS = wx.BoxSizer(wx.HORIZONTAL)
        self.perf_ind_spin_agr = wx.SpinCtrl(self.perf_ind_panel, -1, "AGR", size=wx.Size(60, -1))
        self.perf_ind_spin_agr.SetRange(0, 100)
        self.perf_ind_spin_agr.SetValue(70)
        self.perf_ind_spin_rep = wx.SpinCtrl(self.perf_ind_panel, -1, "REP", size=wx.Size(60, -1))        
        self.perf_ind_spin_rep.SetRange(0, 100)
        self.perf_ind_spin_rep.SetValue(70)
        self.perf_ind_spin_dis = wx.SpinCtrl(self.perf_ind_panel, -1, "DIS", size=wx.Size(60, -1))        
        self.perf_ind_spin_dis.SetRange(0, 100)
        self.perf_ind_spin_dis.SetValue(70)
        self.perf_ind_panel.right_part.AddSpacer(5)
        bsizerAGR.AddSpacer(5)
        bsizerAGR.Add(wx.StaticText(self.perf_ind_panel, -1, "AGR:", size=wx.Size(30, -1)), 0, wx.FIXED_MINSIZE|wx.ALIGN_CENTER_VERTICAL)
        bsizerAGR.Add(self.perf_ind_spin_agr, 0, wx.FIXED_MINSIZE|wx.ALIGN_CENTER_VERTICAL)
        bsizerAGR.AddSpacer(5)
        bsizerREP.AddSpacer(5)
        bsizerREP.Add(wx.StaticText(self.perf_ind_panel, -1, "REP:", size=wx.Size(30, -1)), 0, wx.FIXED_MINSIZE|wx.ALIGN_CENTER_VERTICAL)
        bsizerREP.Add(self.perf_ind_spin_rep, 0, wx.FIXED_MINSIZE|wx.ALIGN_CENTER_VERTICAL)
        bsizerREP.AddSpacer(5)
        bsizerDIS.AddSpacer(5)
        bsizerDIS.Add(wx.StaticText(self.perf_ind_panel, -1, "DIS:", size=wx.Size(30, -1)), 0, wx.FIXED_MINSIZE|wx.ALIGN_CENTER_VERTICAL)
        bsizerDIS.Add(self.perf_ind_spin_dis, 0, wx.FIXED_MINSIZE|wx.ALIGN_CENTER_VERTICAL)
        bsizerDIS.AddSpacer(5)
        bsizer.Add(bsizerAGR, 0, wx.FIXED|wx.ALIGN_CENTER_HORIZONTAL)
        bsizer.Add(bsizerREP, 0, wx.FIXED|wx.ALIGN_CENTER_HORIZONTAL)
        bsizer.Add(bsizerDIS, 0, wx.FIXED|wx.ALIGN_CENTER_HORIZONTAL)     
        boxMain.Add(bsizer, 0, wx.EXPAND|wx.ALL)
        #self.perf_ind_rb_lvl = wx.RadioBox(self.perf_ind_panel, -1, "Set levels:", wx.DefaultPosition, wx.Size(100, -1), ["individually", "same for all"], 1, wx.RA_SPECIFY_COLS)
        #boxMain.AddSpacer(5)
        #boxMain.Add(self.perf_ind_rb_lvl, 0, wx.EXPAND|wx.ALL)
        self.perf_ind_rb_comp = wx.RadioBox(self.perf_ind_panel, -1, "Compute AGR and REP with:", wx.DefaultPosition, wx.Size(160, -1), ["RV", "RV2"], 1, wx.RA_SPECIFY_COLS)
        boxMain.AddSpacer(5)
        boxMain.Add(self.perf_ind_rb_comp, 0, wx.EXPAND|wx.ALL)
        box = wx.StaticBox(self.perf_ind_panel, -1, "Include in plots:")
        bsizer = wx.StaticBoxSizer(box, wx.VERTICAL)    
        self.perf_ind_cbl_include = wx.CheckListBox(self.perf_ind_panel, -1, wx.DefaultPosition, wx.Size(150, 65), ["Target level", "1% significance level", "5% significance level", "10% significance level"])
        self.perf_ind_cbl_include.Check(0, False)
        self.perf_ind_cbl_include.Check(1, False)
        self.perf_ind_cbl_include.Check(2, False)
        self.perf_ind_cbl_include.Check(3, False)
        bsizer.Add(self.perf_ind_cbl_include, 0, wx.FIXED)
        boxMain.AddSpacer(5)
        boxMain.Add(bsizer, 0, wx.FIXED|wx.ALL)
        self.perf_ind_panel.right_part.Add(boxMain, 0, wx.FIXED_MINSIZE)
        self.perf_ind_panel.right_part.AddSpacer(5)
        """
        

        ##########DropTarget-Setting-Start##########
        self.main_notebook.SetDropTarget(DropTarget(self))
        ##########DropTarget-Setting-End##########

        ##########Icon-Setting-Start##########
        pathname = os.path.dirname(sys.argv[0])
        self.progPath = os.path.abspath(pathname).decode(sys.getfilesystemencoding())
        figpath = self.progPath + u'/fig.ico'
        self.SetIcon(wx.Icon(figpath,wx.BITMAP_TYPE_ICO))
        ##########Icon-Setting-End##########

        ##########Sizer-Settings-Start##########
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer.Add(self.main_notebook, 1, wx.LEFT|wx.TOP|wx.GROW)
        self.SetSizer(self.sizer)
        self.Layout()
        ##########Sizer-Settings-End##########

        self._init_coll_main_notebook_Pages(self.main_notebook)
        self._init_coll_uni_notebook_Pages(self.uni_notebook)
        self._init_coll_multi_notebook_Pages(self.multi_notebook)
        self._init_coll_avgr_notebook_Pages(self.avgr_notebook)
        self._init_coll_overall_notebook_Pages(self.overall_notebook)


    def __init__(self, parent, filename, delimiter='\t'):
        self.image_save_path = ""
        self.selection_changes = {}
        self.export_active_plots = []
        self.file_for_opening = filename
        self._init_ctrls(parent)
        self.initialize_variables()

        # try to open file:
        if self.file_for_opening != "":
            self.OnGeneralFileOpen(self.file_for_opening, delimiter)



    def OnPageChanging(self, event):
        if self.menuOptionsSelectAll.IsChecked():
            obj = event.GetEventObject()
            if obj == self.main_notebook:
                obj = obj.GetCurrentPage().GetCurrentPage()
            else:
                obj = obj.GetCurrentPage()
            self.selection_changes = obj.get_selection_ass_att_samp()

    def OnPageChanged(self, event):
        if self.menuOptionsSelectAll.IsChecked():
            obj = event.GetEventObject()
            if obj == self.main_notebook:
                obj = obj.GetCurrentPage().GetCurrentPage()
            else:
                obj = obj.GetCurrentPage()
            obj.update_selection(self.selection_changes)

    def onManhSpin(self, event):
        self.manh_spin_txt.SetValue(str(event.GetPosition()))



#---Menu-Actions---#FFFFFF#FF8040-----------------------------------------------
    def OnMain_FrameClose(self, event):
        self.OnClosing(event)

        for frame in self.figureList:
            try:
                frame.Close()
            except:
                print "Dead frame"
        sys.exit()



    def OnMenuFileOpen_plainMenu(self, event):
        """
        Opens a plain text file with a help function from LoadData class

        @type event:    object
        @param event:    An event is a structure holding information about an
        event passed to a callback or member function.
        """

        self.delimiter = '\t'


        self.statusBar.SetStatusText("Opening file...")
        wildcard = "Text Files (Tab delimited) (*.txt)|*.txt|"         \
            "Dat Files (Tab delimited) (*.dat)|*.dat|"    \
            "All Files (*.*)|*.*||"

        dlg = wx.FileDialog(
            self, message="Choose a file", defaultDir=os.getcwd(),
            defaultFile="", wildcard=wildcard, style=wx.FD_OPEN | wx.FD_MULTIPLE | wx.FD_CHANGE_DIR)

        if dlg.ShowModal() == wx.ID_OK:
            self.preloading()
            pathList = dlg.GetPaths()
            self.fileName = pathList[0]
            self.summaryFrame.append_text(self.fileName + "\n")
            self.summaryFrame.set_gauge(0)

            newData = PlainText(self, self.fileName, self.summaryFrame, '\t')
            if(newData.fileRead):

                self.summaryFrame.append_text("\nLoading data...\n")

                self.s_data = newData.s_data


                #print "min/max:"
                #print self.NewData.get_MAX_MIN_Values()
                self.update_tabs()
            else:
                print "Failed to load file"
                self.summaryFrame.Destroy()
                self.statusBar.SetStatusText("Failed to load file")
        else:
            self.statusBar.SetStatusText("Ready") # cancel opening
        dlg.Destroy()



    def OnMenuFileOpen_CD_Menu(self, event):
        """
        Opens a plain text file with a help function from LoadData class

        @type event:    object
        @param event:    An event is a structure holding information about an
        event passed to a callback or member function.
        """

        self.delimiter = ','


        self.statusBar.SetStatusText("Opening file...")
        wildcard = "CSV Files (Comma delimited) (*.csv)|*.csv|"         \
            "Text Files (Comma delimited) (*.txt)|*.txt|"    \
            "All Files (*.*)|*.*||"

        dlg = wx.FileDialog(
            self, message="Choose a file", defaultDir=os.getcwd(),
            defaultFile="", wildcard=wildcard, style=wx.FD_OPEN | wx.FD_MULTIPLE | wx.FD_CHANGE_DIR)

        if dlg.ShowModal() == wx.ID_OK:
            self.preloading()
            pathList = dlg.GetPaths()
            self.fileName = pathList[0]
            self.summaryFrame.append_text(self.fileName + "\n")
            self.summaryFrame.set_gauge(0)

            newData = PlainText(self, self.fileName, self.summaryFrame, ',')
            if(newData.fileRead):

                self.summaryFrame.append_text("\nLoading data...\n")

                self.s_data = newData.s_data


                #print "min/max:"
                #print self.NewData.get_MAX_MIN_Values()
                self.update_tabs()
            else:
                print "Failed to load file"
                self.summaryFrame.Destroy()
                self.statusBar.SetStatusText("Failed to load file")
        else:
            self.statusBar.SetStatusText("Ready") # cancel opening
        dlg.Destroy()



    def OnMenuFileOpen_SD_Menu(self, event):
        """
        Opens a plain text file with a help function from LoadData class

        @type event:    object
        @param event:    An event is a structure holding information about an
        event passed to a callback or member function.
        """

        self.delimiter = ';'

        self.statusBar.SetStatusText("Opening file...")
        wildcard = "CSV Files (Semicolon delimited) (*.csv)|*.csv|"         \
            "Text Files (Semicolon delimited) (*.txt)|*.txt|"    \
            "All Files (*.*)|*.*||"

        dlg = wx.FileDialog(
            self, message="Choose a file", defaultDir=os.getcwd(),
            defaultFile="", wildcard=wildcard, style=wx.FD_OPEN | wx.FD_MULTIPLE | wx.FD_CHANGE_DIR)

        if dlg.ShowModal() == wx.ID_OK:
            self.preloading()
            pathList = dlg.GetPaths()
            self.fileName = pathList[0]
            self.summaryFrame.append_text(self.fileName + "\n")
            self.summaryFrame.set_gauge(0)

            newData = PlainText(self, self.fileName, self.summaryFrame, ';')
            if(newData.fileRead):

                self.summaryFrame.append_text("\nLoading data...\n")

                self.s_data = newData.s_data


                #print "min/max:"
                #print self.NewData.get_MAX_MIN_Values()
                self.update_tabs()
            else:
                print "Failed to load file"
                self.summaryFrame.Destroy()
                self.statusBar.SetStatusText("Failed to load file")
        else:
            self.statusBar.SetStatusText("Ready") # cancel opening
        dlg.Destroy()



    def OnMenuFileOpen_fizzMenu(self, event):
        """
        Opens a FIZZ file with a help function from LoadData class.

        @type event:    object
        @param event:    An event is a structure holding information about an event passed to a callback or member function.
        """
        """
        dlg = wx.MessageDialog(self, "Support for FIZZ-files is not implemented yet.",'Error Message',wx.OK | wx.ICON_INFORMATION)
        if dlg.ShowModal() == wx.ID_OK:
            print "Support for FIZZ files not implemented."
        dlg.Destroy()
        """
        pass
##        self.statusBar.SetStatusText("Opening file...")
##        wildcard = "FIZZ Text Files (*.fizz)|*.fizz|"    \
##            "Text Files (*.txt)|*.txt|"         \
##            "All Files (*.*)|*.*||"
##        dlg = wx.FileDialog(
##            self, message="Choose a file", defaultDir=os.getcwd(),
##            defaultFile="", wildcard=wildcard, style=wx.OPEN | wx.MULTIPLE | wx.CHANGE_DIR)
##
##        if dlg.ShowModal() == wx.ID_OK:
##            self.preloading()
##            pathList = dlg.GetPaths()
##            self.fileName = pathList[0]
##
##
##            self.NewData = FIZZ(self, self.fileName, self.summaryFrame)
##            if(self.NewData.fileRead):
##
##                self.Matrix = self.NewData.MatrixData()
##                self.AttributeList = self.NewData.Attributes()
##                self.AssessorList = self.NewData.Assessors()
##                self.SampleList = self.NewData.Samples()
##                self.ReplicateList = self.NewData.Replicates()
##                self.SparseMatrix = self.NewData.SparseMatrixData()
##
##                #print "min/max:"
##                #print self.NewData.get_MAX_MIN_Values()
##
##                self.update_tabs()
##            else:
##                print "Failed to load file"
##                self.statusBar.SetStatusText("Failed to load file")
##        else:
##            self.statusBar.SetStatusText("Ready") # cancel opening
##        dlg.Destroy()



    def OnMenuFileOpen_excelMenu(self, event):
        """
        Opens a win32 Excel file with a help function from LoadData class.

        @type event:    object
        @param event:    An event is a structure holding information about an event passed to a callback or member function.
        """
        self.delimiter = ''

        self.statusBar.SetStatusText("Opening file...")
        wildcard = "Excel Files (*.xls)|*.xls|Excel Files (*.xlsx)|*.xlsx|All Files (*.*)|*.*||"
        dlg = wx.FileDialog(
            self, message="Choose a file", defaultDir=os.getcwd(),
            defaultFile="", wildcard=wildcard, style=wx.FD_OPEN | wx.FD_MULTIPLE | wx.FD_CHANGE_DIR)

        if dlg.ShowModal() == wx.ID_OK:
            self.preloading()
            pathList = dlg.GetPaths()
            self.fileName = pathList[0]
            self.summaryFrame.append_text(self.fileName + "\n")
            self.summaryFrame.set_gauge(0)

            newData = Excel(self, self.fileName, self.summaryFrame)



            if(newData.fileRead):

                self.summaryFrame.append_text("\nLoading data...\n")

                self.s_data = newData.s_data

                #print "min/max:"
                #print self.NewData.get_MAX_MIN_Values()


                self.update_tabs()
            else:
                print "Failed to load file"
                self.summaryFrame.Destroy()
                self.statusBar.SetStatusText("Failed to load file")
        else:
            self.statusBar.SetStatusText("Ready") # cancel opening
        dlg.Destroy()


    def OnMenuFileOpen_compusenseMenu(self, event):
        """
        Opens a win32 Excel file with a help function from LoadData class.

        @type event:    object
        @param event:    An event is a structure holding information about an event passed to a callback or member function.
        """
        """
        dlg = wx.MessageDialog(self, "Support for Compusense-files is not implemented.",'Error Message',wx.OK | wx.ICON_INFORMATION)
        if dlg.ShowModal() == wx.ID_OK:
            print "Support for Compusense files not implemented yet."
        dlg.Destroy()
        """
        pass


    def OnMenuFileOpen_PC_Menu(self, event):
        """
        Opens a standard PanelCheck file.

        @type event:    object
        @param event:    An event is a structure holding information about an
        event passed to a callback or member function.
        """

        self.delimiter = '\t'


        self.statusBar.SetStatusText("Opening file...")
        wildcard = "PanelCheck Files (*.pchk)|*.pchk|"         \
            "Dat Files (Tab delimited) (*.dat)|*.dat|"    \
            "All Files (*.*)|*.*||"

        dlg = wx.FileDialog(
            self, message="Choose a file", defaultDir=os.getcwd(),
            defaultFile="", wildcard=wildcard, style=wx.FD_OPEN | wx.FD_MULTIPLE | wx.FD_CHANGE_DIR)

        if dlg.ShowModal() == wx.ID_OK:
            self.preloading()
            pathList = dlg.GetPaths()
            self.fileName = pathList[0]
            self.summaryFrame.append_text(self.fileName + "\n")
            self.summaryFrame.set_gauge(0)

            newData = PlainText(self, self.fileName, self.summaryFrame, '\t')
            if(newData.fileRead):

                self.summaryFrame.append_text("\nLoading data...\n")

                self.s_data = newData.s_data


                #print "min/max:"
                #print self.NewData.get_MAX_MIN_Values()
                self.update_tabs()
            else:
                print "Failed to load file"
                self.summaryFrame.Destroy()
                self.statusBar.SetStatusText("Failed to load file")
        else:
            self.statusBar.SetStatusText("Ready") # cancel opening
        dlg.Destroy()


    def OnMenuFileExportImages_Menu(self, event):
        """
        For exporting image files.
        """
        print "images"
        if self.s_data != None:
            selection_changes = {}
            if self.menuOptionsSelectAll.IsChecked():
                selection_changes = self.main_notebook.GetCurrentPage().GetCurrentPage().get_selection_ass_att_samp()
            Export_Images_Dialog(self, self.s_data, saving_ppt_file=False, view_grid=self.menuViewGrid, view_legend=self.menuViewLegend, active_plots=self.export_active_plots, selection_changes=selection_changes)
        else:
            dlg = wx.MessageDialog(None, 'Open a data set to export the plots.',
                               'Error Message',
                               wx.OK | wx.ICON_INFORMATION)
            dlg.ShowModal()
            dlg.Destroy()

    def OnMenuFileExportPPT_Menu(self, event):
        """
        For exporting ppt files.
        """
        print "ppt"
        if self.s_data != None:
            selection_changes = {}
            if self.menuOptionsSelectAll.IsChecked():
                selection_changes = self.main_notebook.GetCurrentPage().GetCurrentPage().get_selection_ass_att_samp()
            Export_Images_Dialog(self, self.s_data, saving_ppt_file=True, view_grid=self.menuViewGrid, view_legend=self.menuViewLegend, active_plots=self.export_active_plots, selection_changes=selection_changes)
        else:
            dlg = wx.MessageDialog(None, 'Open a data set to export the plots.',
                               'Error Message',
                               wx.OK | wx.ICON_INFORMATION)
            dlg.ShowModal()
            dlg.Destroy()


    def OnClosing(self, event):
        v = {}
        v["grid"] = self.menuOptionsGrid.IsChecked()
        v["legend"] = self.menuOptionsLegend.IsChecked()
        v["selection"] = self.menuOptionsSelectAll.IsChecked()

        self.session_data.update(view=v, image_save_path=self.image_save_path, export_active_plots=self.export_active_plots)
        self.session_data.store_session_file(filename=self.progPath + "/session.dat")


    def OnMenuFileSave(self, event):
        """
        Save current dataset as standard panelcheck file.
        """
        file_choices = "PanelCheck file (*.pchk)|*.pchk||"

        thisdir  = os.getcwd()

        dlg = wx.FileDialog(self, message='Save current dataset as...',
                            defaultDir = thisdir, defaultFile='dataset001.pchk',
                            wildcard=file_choices, style=wx.SAVE)

        if dlg.ShowModal() == wx.ID_OK:
            abspath = dlg.GetPath()
            #abspath = str(abspath)
            msg = save_dataset(abspath, self.s_data)
            self.statusBar.SetStatusText(msg)
        dlg.Destroy()



    def OnMenuFileClose_fileMenu(self, event):
        """
        Closes the file imported.
        """

        if self.s_data != None:
            abspath = self.s_data.abspath

        self.AttributeList = []
        self.AssessorList = []
        self.SampleList = []
        self.ReplicateList = []

        self.session_data.update(sensory_data=None)
        self.session_data.store_session_file(filename=self.progPath + "/session.dat")


        # clear trees and lists
        self.line_panel.clear_all()
        self.mean_std_panel.clear_all()
        self.corr_panel.clear_all()
        self.profile_panel.clear_all()
        self.egg_panel.clear_all()
        self.f_panel.clear_all()
        self.mse_panel.clear_all()
        self.pmse_panel.clear_all()

        self.tuck1_panel.clear_all()
        self.manh_panel.clear_all()

        self.org_panel.clear_all()
        self.std_panel.clear_all()
        self.statis_panel.clear_all()

        self.mm_anova_panel1.clear_all()
        self.mm_anova_panel2.clear_all()
        self.mm_anova_panel3.clear_all()
        #self.perf_ind_panel.clear_all()

        if self.s_data != None:
            self.statusBar.SetStatusText("\"" + abspath + "\" closed")

        self.s_data = None


    def OnMenuFileExitMenu(self, event):
        """
        Exits the program.

        @type event:    object
        @param event:    An event is a structure holding information about an
        event passed to a callback or member function.
        """
        #self.Close()
        self.OnClosing(event)

        for frame in self.figureList:
            try:
                frame.Close()
            except:
                print "Dead frame"
        sys.exit()



    def OnMenuViewGridMenu(self, event):
        if self.menuViewGrid:
            self.menuViewGrid = False
        else:
            self.menuViewGrid = True



    def OnMenuViewLegendMenu(self, event):
        if self.menuViewLegend:
            self.menuViewLegend = False
        else:
            self.menuViewLegend = True


    def OnMenuHelpManualMenu(self, event):
        """
        Opens the Manual.

        @type event:    object
        @param event:    An event is a structure holding information about an
        event passed to a callback or member function.
        """
        fil = self.progPath + u"/help.chm"
        os.startfile(fil)


    def OnMenuHelpWorkflowMenu(self, event):
        """
        Opens the workflow.

        @type event:    object
        @param event:    An event is a structure holding information about an
        event passed to a callback or member function.
        """
        fil = self.progPath + u"/workflow.pdf"
        os.startfile(fil)


    def OnMenuHelpAboutMenu(self, event):
        """
        Open the about information window.

        @type event:    object
        @param event:    An event is a structure holding information about an
        event passed to a callback or member function.
        """
        frame = AboutFrame(None)
        frame.Show()




    ###########NECESSARY_CUSTOM_METHODS_START###########
    def initialize_variables(self):
        """
        Initializes start variables.
        """
        self.figureList = []
        self.menuViewGrid = False
        self.menuViewLegend = True
        self.summaryFrame = None
        self.s_data = None

        self.disabledItems = {}
        self.disabledAssessors = {}

        self.numberOfWindow = 0
        self.statusBar.SetStatusText("Ready")

        self.colourList = wx.lib.colourdb.getColourList()
        wx.lib.colourdb.updateColourDB()


        self.session_data = load_session_data(filename=self.progPath + "/session.dat")
        if self.session_data != None:
            try:
                print "Session data loaded"
                self.menuViewGrid = self.session_data.view["grid"]
                self.menuViewLegend = self.session_data.view["legend"]
                self.s_data = self.session_data.sensory_data
                if self.s_data != None:
                    self.update_tabs(setting_limits=False)
                    self.statusBar.SetStatusText(self.s_data.abspath)

                self.add_recent_files()

                self.menuOptionsSelectAll.Check(self.session_data.view["selection"])
                self.menuOptionsLegend.Check(self.session_data.view["legend"])
                self.menuOptionsGrid.Check(self.session_data.view["grid"])

                self.image_save_path = self.session_data.image_save_path
                self.export_active_plots = self.session_data.export_active_plots

                #print self.session_data.recent_files
            except:
                print "Error during load of session file."
                print "New session data"
                self.session_data = SessionData()

        else:
            print "New session data"
            self.session_data = SessionData()

        # plot data storage:
        self.init_plot_data()




    def init_plot_data(self):
        # plot data storage:
        self.mm_anova1_plot_data = None # plot data for Mixed Model ANOVA
        self.mm_anova2_plot_data = None # plot data for Mixed Model ANOVA
        self.mm_anova3_plot_data = None # plot data for Mixed Model ANOVA
        self.mse_plot_data = None # plot data for all mse plots
        self.f_plot_data = None # plot data for all F and p plots
        self.pmse_plot_data = None # plot data for all pmse plots
        self.tucker1_plot_data = None # plot data for all tucker1 plots
        self.manh_plot_data = None # plot data for all manhattan plots
        self.profile_plot_data = None
        self.egg_plot_data = None
        self.mean_plot_data = None
        self.perf_ind_data = None



    def add_recent_files(self):
        if hasattr(self, "recent_inds"):
            for ind in self.recent_inds:
                self.menuFileRecent.Remove(ind)
        self.recent_inds = []
        num_tot = len(self.session_data.recent_files)
        for ind in range(num_tot):
            recent_id = wx.NewId()
            self.recent_inds.append(recent_id)
            #(dirname, file, ext) = split_path(self.session_data.recent_files[ind][0])
            #filename = file + "." + ext

            filename = self.session_data.recent_files[ind][0]

            #menuitem = wx.MenuItem(parentMenu=self.menuFileRecent,   id=recent_id, kind=wx.ITEM_NORMAL, item=filename)
            self.menuFileRecent.Prepend(  id=recent_id, kind=wx.ITEM_NORMAL, item=filename)
            self.Bind(wx.EVT_MENU, self.OnGeneralFileOpenRecent, id=recent_id)


    def preloading(self):
        """
        To be used at beginning of each file loading.
        """
        # initializing summary frame
        self.summaryFrame = Summary(self)
        self.summaryFrame.set_text("Opening file...\n")


    def update_tabs(self, setting_limits=True):
        """
        Updates items in main GUI. To be used at the end of all open_file
        methods. Shows information dialog window about the opened file.
        """
        self.AssessorList = self.s_data.AssessorList
        self.SampleList = self.s_data.SampleList
        self.ReplicateList = self.s_data.ReplicateList
        self.AttributeList = self.s_data.AttributeList

        # clear trees and lists
        self.line_panel.clear_all()
        self.mean_std_panel.clear_all()
        self.corr_panel.clear_all()
        self.profile_panel.clear_all()
        self.egg_panel.clear_all()
        self.f_panel.clear_all()
        self.mse_panel.clear_all()
        self.pmse_panel.clear_all()

        self.tuck1_panel.clear_all()
        self.manh_panel.clear_all()

        self.org_panel.clear_all()
        self.std_panel.clear_all()
        self.statis_panel.clear_all()

        self.mm_anova_panel1.clear_all()
        self.mm_anova_panel2.clear_all()
        self.mm_anova_panel3.clear_all()
        #self.perf_ind_panel.clear_all()


        #Show Trees
        self.show_linePlot_tree()
        self.show_mean_stdPlot_tree()
        self.show_corrPlot_tree()
        self.show_tuck1Plot_tree()
        self.show_eggPlot_tree()
        self.show_pmsePlot_tree()
        self.show_fPlot_tree()
        self.show_msePlot_tree()
        self.show_org_tree()
        self.show_std_tree()
        self.show_statis_tree()

        self.show_mm_anova1_tree()
        self.show_mm_anova2_tree()
        self.show_mm_anova3_tree()
        #self.show_perf_ind_tree()
        
        self.show_profilePlot_tree()
        self.show_manhattan_tree()



        # set lists
        self.line_panel.set_lists(self.s_data.AssessorList, self.s_data.AttributeList, self.s_data.SampleList)
        self.mean_std_panel.set_lists(self.s_data.AssessorList, self.s_data.AttributeList, self.s_data.SampleList)
        self.corr_panel.set_lists(self.s_data.AssessorList, self.s_data.AttributeList, self.s_data.SampleList)
        self.profile_panel.set_lists(self.s_data.AssessorList, self.s_data.AttributeList, self.s_data.SampleList)
        self.egg_panel.set_lists(self.s_data.AssessorList, self.s_data.AttributeList, self.s_data.SampleList)
        self.f_panel.set_lists(self.s_data.AssessorList, self.s_data.AttributeList, self.s_data.SampleList)
        self.mse_panel.set_lists(self.s_data.AssessorList, self.s_data.AttributeList, self.s_data.SampleList)
        self.pmse_panel.set_lists(self.s_data.AssessorList, self.s_data.AttributeList, self.s_data.SampleList)

        self.tuck1_panel.set_lists(self.s_data.AssessorList, self.s_data.AttributeList, self.s_data.SampleList)
        self.manh_panel.set_lists(self.s_data.AssessorList, self.s_data.AttributeList, self.s_data.SampleList)

        self.org_panel.set_lists(self.s_data.AssessorList, self.s_data.AttributeList, self.s_data.SampleList)
        self.std_panel.set_lists(self.s_data.AssessorList, self.s_data.AttributeList, self.s_data.SampleList)
        self.statis_panel.set_lists(self.s_data.AssessorList, self.s_data.AttributeList, self.s_data.SampleList)

        self.mm_anova_panel1.set_lists(self.s_data.AssessorList, self.s_data.AttributeList, self.s_data.SampleList)
        self.mm_anova_panel2.set_lists(self.s_data.AssessorList, self.s_data.AttributeList, self.s_data.SampleList)
        self.mm_anova_panel3.set_lists(self.s_data.AssessorList, self.s_data.AttributeList, self.s_data.SampleList)
        #self.perf_ind_panel.set_lists(self.s_data.AssessorList, self.s_data.AttributeList, self.s_data.SampleList)

        self.statusBar.SetStatusText("\"" + self.s_data.abspath + "\" opened")


        if setting_limits:
            summaryConstructor2(self, self.SampleList, self.AssessorList,
                                    self.ReplicateList, self.AttributeList, self.s_data.mv_inf, self.summaryFrame)
            #self.message = wx.lib.dialogs.ScrolledMessageDialog(self, self.summary, "Summary of data")
            #self.message.ShowModal()
            limits = self.s_data.get_MAX_MIN_Values()
            print "min/max:"
            print limits
            self.summaryFrame.set_limits(limits)
            #self.summaryFrame.append_text_summary(self.summary)
            self.summaryFrame.switch_to_summary()
            if self.summaryFrame.ShowModal() == wx.ID_OK:
                    #frame.checkValues()
                limits = self.summaryFrame.get_limits()
            else:
                limits = self.summaryFrame.get_limits()
            self.summaryFrame.Destroy()
            self.s_data.scale_limits = limits
            print self.s_data.scale_limits
            self.session_data.update(new_recent=[self.s_data.abspath, self.delimiter], sensory_data=self.s_data)
            self.session_data.store_session_file(filename=self.progPath + "/session.dat")

        self.add_recent_files()

        # plot data storage:
        self.init_plot_data()


    def show_linePlot_tree(self):
        """
        Prepares the wxTreeCtrl by sorting after:
            1. samples
            2. assessors
            3. replicates
        """
        tree = self.line_panel.tree

        root = tree.AddRoot(u'Sensory data')
        tree.SetItemData(root, 'root')
        #myChildren = []
        child = tree.AppendItem(root, "Overview Plot")
        tree.SetItemData(child, ["Overview Plot"])
        tree.SetItemTextColour(child, 'DARK GREEN')

        for samples in self.SampleList:
            child = tree.AppendItem(root, samples)
            tree.SetItemData(child, [samples])
            #myChildren.append(child)
            tree.SetItemTextColour(child, wx.BLUE)
            grandChild = tree.AppendItem(child, "Overview Plot")
            tree.SetItemData(grandChild, [samples, "Overview Plot"])
            tree.SetItemTextColour(grandChild, 'DARK GREEN')
            for assessors in self.AssessorList:
                grandChild = tree.AppendItem(child, assessors)
                tree.SetItemData(grandChild, [samples, assessors])
                #myChildren.append(grandChild)
                tree.SetItemTextColour(grandChild, 'CORNFLOWERBLUE')

                for replicates in self.ReplicateList:
                    greatGrandChild = tree.AppendItem(grandChild, replicates)
                    tree.SetItemData(greatGrandChild, [samples, assessors, replicates])
                    #myChildren.append(greatGrandChild)
                    tree.SetItemTextColour(greatGrandChild, 'NAVY')
        tree.Expand(root)


    def show_mean_stdPlot_tree(self):
        """
        Prepares the wxTreeCtrl in p-MSE plot:
            1. assessors are listed first
            2. attributes are listed last
        """
        tree = self.mean_std_panel.tree

        root = tree.AddRoot(u'Sensory data')
        tree.SetItemData(root, None)

        child = tree.AppendItem(root, "Overview Plot (assessors)")
        tree.SetItemData(child, ["Overview Plot (assessors)"])
        tree.SetItemTextColour(child, 'DARK GREEN')
        for assessor in self.AssessorList:
            child = tree.AppendItem(root, assessor)
            tree.SetItemData(child, [assessor])
            tree.SetItemTextColour(child, wx.BLUE)

        child = tree.AppendItem(root, "Overview Plot (attributes)")
        tree.SetItemData(child, ["Overview Plot (attributes)"])
        tree.SetItemTextColour(child, 'DARK GREEN')
        for attribute in self.AttributeList:
            child = tree.AppendItem(root, attribute)
            tree.SetItemData(child, [attribute])
            tree.SetItemTextColour(child, 'STEELBLUE3')
        tree.Expand(root)
        

    def show_corrPlot_tree(self):
        """
        Prepares the wxTreeCtrl in Correlation plot by sorting after:
            1. assessors
            2. attributes

            1. attributes
            2. assessors

        """
        tree = self.corr_panel.tree

        root = tree.AddRoot(u'Sensory data')
        tree.SetItemData(root, None)

        for assessor in self.AssessorList:
            child = tree.AppendItem(root, assessor)
            tree.SetItemData(child, [assessor])
            tree.SetItemTextColour(child, wx.Colour(140, 16, 0))
            grandChild = tree.AppendItem(child, "Overview Plot")
            tree.SetItemData(grandChild, [assessor, "Overview Plot"])
            tree.SetItemTextColour(grandChild, 'DARK GREEN')
            for attribute in self.AttributeList:
                grandChild = tree.AppendItem(child, attribute)
                tree.SetItemData(grandChild, [assessor,attribute])
                tree.SetItemTextColour(grandChild, wx.BLUE)
        for attribute in self.AttributeList:
            child = tree.AppendItem(root, attribute)
            tree.SetItemData(child, [attribute])
            tree.SetItemTextColour(child, wx.Colour(230, 128, 116))
            grandChild = tree.AppendItem(child, "Overview Plot")
            tree.SetItemData(grandChild, [attribute, "Overview Plot"])
            tree.SetItemTextColour(grandChild, 'DARK GREEN')
            for assessor in self.AssessorList:
                grandChild = tree.AppendItem(child, assessor)
                tree.SetItemData(grandChild, [attribute, assessor])
                tree.SetItemTextColour(grandChild, wx.BLUE)
        tree.Expand(root)
        

    def show_profilePlot_tree(self):
        """
        Prepares the wxTreeCtrl in Eggshell plot:
            attributes are listed
        """
        tree = self.profile_panel.tree

        root = tree.AddRoot(u'Sensory data')
        tree.SetItemData(root, None)
        child = tree.AppendItem(root, "Overview Plot")
        tree.SetItemData(child, ["Overview Plot"])
        tree.SetItemTextColour(child, 'DARK GREEN')
        for attribute in self.AttributeList:
            child = tree.AppendItem(root, attribute)
            tree.SetItemData(child, [attribute])
            tree.SetItemTextColour(child, wx.BLUE)
        tree.Expand(root)


    def show_tuck1Plot_tree(self):
        """
        Prepares the wxTreeCtrl in Tucker1:
            1. assessors are listed first
            2. attributes are listed last
        """
        tree = self.tuck1_panel.tree

        root = tree.AddRoot(u'Sensory data')
        tree.SetItemData(root, None)

        child = tree.AppendItem(root, u'Common Scores')
        tree.SetItemData(child, [u'Common Scores'])
        tree.SetItemTextColour(child, wx.BLUE)

        child = tree.AppendItem(root, "Overview Plot (assessors)")
        tree.SetItemData(child, ["Overview Plot (assessors)"])
        tree.SetItemTextColour(child, 'DARK GREEN')

        for assessor in self.AssessorList:
            child = tree.AppendItem(root, assessor)
            tree.SetItemData(child, [assessor])
            tree.SetItemTextColour(child, 'STEELBLUE3')

        child = tree.AppendItem(root, "Overview Plot (attributes)")
        tree.SetItemData(child, ["Overview Plot (attributes)"])
        tree.SetItemTextColour(child, 'DARK GREEN')

        for attribute in self.AttributeList:
            child = tree.AppendItem(root, attribute)
            tree.SetItemData(child, [attribute])
            tree.SetItemTextColour(child, 'NAVY')
            #self.colourList[58]
        tree.Expand(root)
        

    def show_eggPlot_tree(self):
        """
        Prepares the wxTreeCtrl in Eggshell plot:
            attributes are listed
        """
        tree = self.egg_panel.tree

        root = tree.AddRoot(u'Sensory data')
        tree.SetItemData(root, None)
        child = tree.AppendItem(root, "Overview Plot")
        tree.SetItemData(child, ["Overview Plot"])
        tree.SetItemTextColour(child, 'DARK GREEN')
        for attribute in self.AttributeList:
            child = tree.AppendItem(root, attribute)
            tree.SetItemData(child, [attribute])
            tree.SetItemTextColour(child, wx.BLUE)
        tree.Expand(root)


    def show_pmsePlot_tree(self):
        """
        Prepares the wxTreeCtrl in p-MSE plot:
            1. assessors are listed first
            2. attributes are listed last
        """
        tree = self.pmse_panel.tree

        root = tree.AddRoot(u'Sensory data')
        tree.SetItemData(root, None)
        child = tree.AppendItem(root, "Overview Plot (assessors)")
        tree.SetItemData(child, ["Overview Plot (assessors)"])
        tree.SetItemTextColour(child, 'DARK GREEN')
        for assessor in self.AssessorList:
            child = tree.AppendItem(root, assessor)
            tree.SetItemData(child, [assessor])
            tree.SetItemTextColour(child, wx.BLUE)
        child = tree.AppendItem(root, "Overview Plot (attributes)")
        tree.SetItemData(child, ["Overview Plot (attributes)"])
        tree.SetItemTextColour(child, 'DARK GREEN')
        for attribute in self.AttributeList:
            child = tree.AppendItem(root, attribute)
            tree.SetItemData(child, [attribute])
            tree.SetItemTextColour(child, 'STEELBLUE3')
        tree.Expand(root)


    def show_fPlot_tree(self):
        """
        Prepares the wxTreeCtrl in F plot:
            1. general F plot sorted by assessor using many colours
            2. assessors are listed under for highlighting
        """
        tree = self.f_panel.tree

        root = tree.AddRoot(u'Sensory data')
        tree.SetItemData(root, None)

        child = tree.AppendItem(root, "F-values")
        tree.SetItemData(child, ["F-values"])
        tree.SetItemTextColour(child, wx.Colour(140, 16, 0))

        gchild = tree.AppendItem(child, u'General Plot')
        tree.SetItemData(gchild, ["F-values", u'General Plot'])
        tree.SetItemTextColour(gchild, wx.BLUE)
        for attribute in self.AttributeList:
            gchild = tree.AppendItem(child, attribute)
            tree.SetItemData(gchild, ["F-values", attribute])
            tree.SetItemTextColour(gchild, 'STEELBLUE3')


        child = tree.AppendItem(root, "p-values")
        tree.SetItemData(child, ["p-values"])
        tree.SetItemTextColour(child, wx.Colour(230, 128, 116))

        gchild = tree.AppendItem(child, u'General Plot')
        tree.SetItemData(gchild, ["p-values", u'General Plot'])
        tree.SetItemTextColour(gchild, wx.BLUE)
        for attribute in self.AttributeList:
            gchild = tree.AppendItem(child, attribute)
            tree.SetItemData(gchild, ["p-values", attribute])
            tree.SetItemTextColour(gchild, 'STEELBLUE3')
        tree.Expand(root)
        

    def show_org_tree(self):
        """
        Prepares the wxTreeCtrl in Average-Original plot:
        """
        tree = self.org_panel.tree

        root = tree.AddRoot(u'Sensory data')
        tree.SetItemData(root, None)

        child = tree.AppendItem(root, u'Consensus Data')
        tree.SetItemData(child, [u'Averaged Data'])
        tree.SetItemTextColour(child, wx.BLUE)
        child = tree.AppendItem(root, u'PCA Scores')
        tree.SetItemData(child, [u'PCA Scores'])
        tree.SetItemTextColour(child, 'STEELBLUE3')
        child = tree.AppendItem(root, u'PCA Loadings')
        tree.SetItemData(child, [u'PCA Loadings'])
        tree.SetItemTextColour(child, 'STEELBLUE3')
        child = tree.AppendItem(root, u'PCA Correlation Loadings')
        tree.SetItemData(child, [u'PCA Correlation Loadings'])
        tree.SetItemTextColour(child, 'STEELBLUE3')
        child = tree.AppendItem(root, u'Bi-Plot')
        tree.SetItemData(child, [u'Bi-Plot'])
        tree.SetItemTextColour(child, 'STEELBLUE3')
        child = tree.AppendItem(root, u'PCA Explained Variance')
        tree.SetItemData(child, [u'PCA Explained Variance'])
        tree.SetItemTextColour(child, 'STEELBLUE3')
        child = tree.AppendItem(root, u'Spiderweb Plot')
        tree.SetItemData(child, [u'Spiderweb Plot'])
        tree.SetItemTextColour(child, 'STEELBLUE3')
        tree.Expand(root)
        

    def show_std_tree(self):
        """
        Prepares the wxTreeCtrl in Average-Standardized plot:
        """
        tree = self.std_panel.tree

        root = tree.AddRoot(u'Sensory data')
        tree.SetItemData(root, None)

        child = tree.AppendItem(root, u'Consensus Data')
        tree.SetItemData(child, [u'Averaged Data'])
        tree.SetItemTextColour(child, wx.BLUE)
        child = tree.AppendItem(root, u'PCA Scores')
        tree.SetItemData(child, [u'PCA Scores'])
        tree.SetItemTextColour(child, 'STEELBLUE3')
        child = tree.AppendItem(root, u'PCA Loadings')
        tree.SetItemData(child, [u'PCA Loadings'])
        tree.SetItemTextColour(child, 'STEELBLUE3')
        child = tree.AppendItem(root, u'PCA Correlation Loadings')
        tree.SetItemData(child, [u'PCA Correlation Loadings'])
        tree.SetItemTextColour(child, 'STEELBLUE3')
        child = tree.AppendItem(root, u'Bi-Plot')
        tree.SetItemData(child, [u'Bi-Plot'])
        tree.SetItemTextColour(child, 'STEELBLUE3')
        child = tree.AppendItem(root, u'PCA Explained Variance')
        tree.SetItemData(child, [u'PCA Explained Variance'])
        tree.SetItemTextColour(child, 'STEELBLUE3')
        child = tree.AppendItem(root, u'Spiderweb Plot')
        tree.SetItemData(child, [u'Spiderweb Plot'])
        tree.SetItemTextColour(child, 'STEELBLUE3')
        tree.Expand(root)



    def show_statis_tree(self):
        """
        Prepares the wxTreeCtrl in Average-Standardized plot:
        """
        tree = self.statis_panel.tree

        root = tree.AddRoot(u'Sensory data')
        tree.SetItemData(root, None)

        child = tree.AppendItem(root, u'Consensus Data')
        tree.SetItemData(child, [u'Averaged Data'])
        tree.SetItemTextColour(child, wx.BLUE)
        child = tree.AppendItem(root, u'PCA Scores')
        tree.SetItemData(child, [u'PCA Scores'])
        tree.SetItemTextColour(child, 'STEELBLUE3')
        child = tree.AppendItem(root, u'PCA Loadings')
        tree.SetItemData(child, [u'PCA Loadings'])
        tree.SetItemTextColour(child, 'STEELBLUE3')
        child = tree.AppendItem(root, u'PCA Correlation Loadings')
        tree.SetItemData(child, [u'PCA Correlation Loadings'])
        tree.SetItemTextColour(child, 'STEELBLUE3')
        child = tree.AppendItem(root, u'Bi-Plot')
        tree.SetItemData(child, [u'Bi-Plot'])
        tree.SetItemTextColour(child, 'STEELBLUE3')
        child = tree.AppendItem(root, u'PCA Explained Variance')
        tree.SetItemData(child, [u'PCA Explained Variance'])
        tree.SetItemTextColour(child, 'STEELBLUE3')
        child = tree.AppendItem(root, u'Assessor Weights')
        tree.SetItemData(child, [u'Assessor Weights'])
        tree.SetItemTextColour(child, 'STEELBLUE3')
        child = tree.AppendItem(root, u'Spiderweb Plot')
        tree.SetItemData(child, [u'Spiderweb Plot'])
        tree.SetItemTextColour(child, 'STEELBLUE3')
        tree.Expand(root)
        

    def show_fPlot_tree_attribute(self):
        """
        Prepares the wxTreeCtrl in F plot:
            1. general F plot sorted by assessor using many colours
            2. assessors are listed under for highlighting
        """
        tree = self.f_panel.tree


        root = tree.AddRoot(u'Sensory data')
        tree.SetItemData(root, None)

        child = tree.AppendItem(root, "F-values")
        tree.SetItemData(child, ["F-values"])
        tree.SetItemTextColour(child, wx.Colour(140, 16, 0))

        gchild = tree.AppendItem(child, u'General Plot')
        tree.SetItemData(gchild, ["F-values", u'General Plot'])
        tree.SetItemTextColour(gchild, wx.BLUE)
        for ass in self.AssessorList:
            gchild = tree.AppendItem(child, ass)
            tree.SetItemData(gchild, ["F-values", ass])
            tree.SetItemTextColour(gchild, 'STEELBLUE3')


        child = tree.AppendItem(root, "p-values")
        tree.SetItemData(child, ["p-values"])
        tree.SetItemTextColour(child, wx.Colour(230, 128, 116))

        gchild = tree.AppendItem(child, u'General Plot')
        tree.SetItemData(gchild, ["p-values", u'General Plot'])
        tree.SetItemTextColour(gchild, wx.BLUE)
        for ass in self.AssessorList:
            gchild = tree.AppendItem(child, ass)
            tree.SetItemData(gchild, ["p-values", ass])
            tree.SetItemTextColour(gchild, 'STEELBLUE3')

        tree.Expand(root)


    def show_fPlot_tree_assessor(self):
        """
        Prepares the wxTreeCtrl in F plot:
            1. general F plot sorted by attribute using many colours
            2. attributes are listed under for highlighting
        """
        tree = self.f_panel.tree

        root = tree.AddRoot(u'Sensory data')
        tree.SetItemData(root, None)

        child = tree.AppendItem(root, "F-values")
        tree.SetItemData(child, ["F-values"])
        tree.SetItemTextColour(child, wx.Colour(140, 16, 0))

        gchild = tree.AppendItem(child, u'General Plot')
        tree.SetItemData(gchild, ["F-values", u'General Plot'])
        tree.SetItemTextColour(gchild, wx.BLUE)
        for attribute in self.AttributeList:
            gchild = tree.AppendItem(child, attribute)
            tree.SetItemData(gchild, ["F-values", attribute])
            tree.SetItemTextColour(gchild, 'STEELBLUE3')


        child = tree.AppendItem(root, "p-values")
        tree.SetItemData(child, ["p-values"])
        tree.SetItemTextColour(child, wx.Colour(230, 128, 116))

        gchild = tree.AppendItem(child, u'General Plot')
        tree.SetItemData(gchild, ["p-values", u'General Plot'])
        tree.SetItemTextColour(gchild, wx.BLUE)
        for attribute in self.AttributeList:
            gchild = tree.AppendItem(child, attribute)
            tree.SetItemData(gchild, ["p-values", attribute])
            tree.SetItemTextColour(gchild, 'STEELBLUE3')
        tree.Expand(root)



    def show_msePlot_tree(self):
        """
        Prepares the wxTreeCtrl in MSE plot:
            1. general MSE plot sorted by assessor using many colours
            2. assessors are listed under for highlighting
        """
        tree = self.mse_panel.tree

        root = tree.AddRoot(u'Sensory data')
        tree.SetItemData(root, None)

        child = tree.AppendItem(root, u'General Plot')
        tree.SetItemData(child, [u'General Plot'])
        tree.SetItemTextColour(child, wx.BLUE)

        for attribute in self.AttributeList:
            child = tree.AppendItem(root, attribute)
            tree.SetItemData(child, [attribute])
            tree.SetItemTextColour(child, 'STEELBLUE3')
        tree.Expand(root)


    def show_msePlot_tree_assessor(self):
        """
        Prepares the wxTreeCtrl in MSE plot:
            1. general MSE plot sorted by assessor using many colours
            2. assessors are listed under for highlighting
        """
        tree = self.mse_panel.tree

        root = tree.AddRoot(u'Sensory data')
        tree.SetItemData(root, None)

        child = tree.AppendItem(root, u'General Plot')
        tree.SetItemData(child, [u'General Plot'])
        tree.SetItemTextColour(child, wx.BLUE)

        for attribute in self.AttributeList:
            child = tree.AppendItem(root, attribute)
            tree.SetItemData(child, [attribute])
            tree.SetItemTextColour(child, 'STEELBLUE3')
        tree.Expand(root)


    def show_msePlot_tree_attribute(self):
        """
        Prepares the wxTreeCtrl in mse plot:
            1. general F plot sorted by attribute using many colours
            2. attributes are listed under for highlighting
        """
        tree = self.mse_panel.tree

        root = tree.AddRoot(u'Sensory data')
        tree.SetItemData(root, None)

        child = tree.AppendItem(root, u'General Plot')
        tree.SetItemData(child, [u'General Plot'])
        tree.SetItemTextColour(child, wx.BLUE)

        for assessor in self.AssessorList:
            child = tree.AppendItem(root, assessor)
            tree.SetItemData(child, [assessor])
            tree.SetItemTextColour(child, 'STEELBLUE3')
        tree.Expand(root)


    def show_manhattan_tree(self):
        """
        Build Manhattan tree elements
        """
        tree = self.manh_panel.tree

        root = tree.AddRoot(u'Sensory data')
        tree.SetItemData(root, None)


        child = tree.AppendItem(root, "Overview Plot (assessors)")
        tree.SetItemData(child, ["Overview Plot (assessors)"])
        tree.SetItemTextColour(child, 'DARK GREEN')

        for assessor in self.AssessorList:
            child = tree.AppendItem(root, assessor)
            tree.SetItemData(child, [assessor])
            tree.SetItemTextColour(child, 'STEELBLUE3')


        child = tree.AppendItem(root, "Overview Plot (attributes)")
        tree.SetItemData(child, ["Overview Plot (attributes)"])
        tree.SetItemTextColour(child, 'DARK GREEN')

        for attribute in self.AttributeList:
            child = tree.AppendItem(root, attribute)
            tree.SetItemData(child, [attribute])
            tree.SetItemTextColour(child, 'NAVY')
        tree.Expand(root)


    def show_mm_anova1_tree(self):
        """
        """

        # Types:

        # 'REP*SAMP vs ERROR'
        # 'SAMP*ASS vs ERROR'
        # 'SAMP vs SAMP*ASS'
        # 'SAMP in 3-way mixed model'

        # LSD:

        # '95% (uncorrected) LSD-values {5}'
        # '95% (Bonferroni corrected) LSD-values {5}'
        # '95% (uncorrected) LSD-values {6}'
        # '95% (Bonferroni corrected) LSD-values {6}'

        tree = self.mm_anova_panel1.tree

        root = tree.AddRoot(u'Sensory data')
        tree.SetItemData(root, None)
        child = tree.AppendItem(root, u"Overview Plot (F values)")
        tree.SetItemData(child, [u"Overview Plot 1"])
        tree.SetItemTextColour(child, 'DARK GREEN')
        child = tree.AppendItem(root, u'Assessor Effect')
        tree.SetItemData(child, [u'F1'])
        tree.SetItemTextColour(child, wx.BLUE)
        child = tree.AppendItem(root, u'Product Effect')
        tree.SetItemData(child, [u'F2'])
        tree.SetItemTextColour(child, wx.BLUE)

        child = tree.AppendItem(root, u"Overview Plot (LSD values)")
        tree.SetItemData(child, [u"Overview Plot 2"])
        tree.SetItemTextColour(child, 'DARK GREEN')
        child = tree.AppendItem(root, u'Sample means & LSD')
        tree.SetItemData(child, [u'LSD1'])
        tree.SetItemTextColour(child, 'STEELBLUE3')
        child = tree.AppendItem(root, u'Sample means & Bonferroni LSD')
        tree.SetItemData(child, [u'LSD2'])
        tree.SetItemTextColour(child, 'STEELBLUE3')
        tree.Expand(root)



    def show_mm_anova2_tree(self):
        """
        """

        # Types:

        # 'REP*SAMP vs ERROR'
        # 'SAMP*ASS vs ERROR'
        # 'SAMP vs SAMP*ASS'
        # 'SAMP in 3-way mixed model'

        # LSD:

        # '95% (uncorrected) LSD-values {5}'
        # '95% (Bonferroni corrected) LSD-values {5}'
        # '95% (uncorrected) LSD-values {6}'
        # '95% (Bonferroni corrected) LSD-values {6}'

        tree = self.mm_anova_panel2.tree

        root = tree.AddRoot(u'Sensory data')
        tree.SetItemData(root, None)
        child = tree.AppendItem(root, u"Overview Plot (F values)")
        tree.SetItemData(child, [u"Overview Plot 1"])
        tree.SetItemTextColour(child, 'DARK GREEN')
        child = tree.AppendItem(root, u'Assessor Effect')
        tree.SetItemData(child, [u'F1'])
        tree.SetItemTextColour(child, wx.BLUE)
        child = tree.AppendItem(root, u'Product Effect')
        tree.SetItemData(child, [u'F2'])
        tree.SetItemTextColour(child, wx.BLUE)
        child = tree.AppendItem(root, u'Assessor*Product Interaction')
        tree.SetItemData(child, [u'F3'])
        tree.SetItemTextColour(child, wx.BLUE)

        child = tree.AppendItem(root, u"Overview Plot (LSD values)")
        tree.SetItemData(child, [u"Overview Plot 2"])
        tree.SetItemTextColour(child, 'DARK GREEN')
        child = tree.AppendItem(root, u'Sample means & LSD')
        tree.SetItemData(child, [u'LSD1'])
        tree.SetItemTextColour(child, 'STEELBLUE3')
        child = tree.AppendItem(root, u'Sample means & Bonferroni LSD')
        tree.SetItemData(child, [u'LSD2'])
        tree.SetItemTextColour(child, 'STEELBLUE3')
        tree.Expand(root)
        

    def show_mm_anova3_tree(self):
        """
        """

        # Types:

        # 'REP*SAMP vs ERROR'
        # 'SAMP*ASS vs ERROR'
        # 'SAMP vs SAMP*ASS'
        # 'SAMP in 3-way mixed model'

        # LSD:

        # '95% (uncorrected) LSD-values {5}'
        # '95% (Bonferroni corrected) LSD-values {5}'
        # '95% (uncorrected) LSD-values {6}'
        # '95% (Bonferroni corrected) LSD-values {6}'

        tree = self.mm_anova_panel3.tree

        root = tree.AddRoot(u'Sensory data')
        tree.SetItemData(root, None)
        child = tree.AppendItem(root, u"Overview Plot (F values)")
        tree.SetItemData(child, [u"Overview Plot 1"])
        tree.SetItemTextColour(child, 'DARK GREEN')
        child = tree.AppendItem(root, u'Assessor Effect')
        tree.SetItemData(child, [u'F1'])
        tree.SetItemTextColour(child, wx.BLUE)
        child = tree.AppendItem(root, u'Product Effect')
        tree.SetItemData(child, [u'F2'])
        tree.SetItemTextColour(child, wx.BLUE)
        child = tree.AppendItem(root, u'Replicate Effect')
        tree.SetItemData(child, [u'F2b'])
        tree.SetItemTextColour(child, wx.BLUE)
        child = tree.AppendItem(root, u'Assessor*Product Interaction')
        tree.SetItemData(child, [u'F3'])
        tree.SetItemTextColour(child, wx.BLUE)
        child = tree.AppendItem(root, u'Product*Replicate Interaction')
        tree.SetItemData(child, [u'F4'])
        tree.SetItemTextColour(child, wx.BLUE)
        child = tree.AppendItem(root, u'Assessor*Replicate Interaction')
        tree.SetItemData(child, [u'F5'])
        tree.SetItemTextColour(child, wx.BLUE)

        child = tree.AppendItem(root, u"Overview Plot (LSD values)")
        tree.SetItemData(child, [u"Overview Plot 2"])
        tree.SetItemTextColour(child, 'DARK GREEN')
        child = tree.AppendItem(root, u'Sample means & LSD')
        tree.SetItemData(child, [u'LSD1'])
        tree.SetItemTextColour(child, 'STEELBLUE3')
        child = tree.AppendItem(root, u'Sample means & Bonferroni LSD')
        tree.SetItemData(child, [u'LSD2'])
        tree.SetItemTextColour(child, 'STEELBLUE3')
        tree.Expand(root)


    def show_perf_ind_tree(self):
        """
        Original performance indices
          
        Overview plot
        Indices table
        AGR prod
        AGR att
        REP prod
        REP att
        DIS total
        DIS panel-1
        p values for AGR and REP
        RV for 1% sign. level
        RV for 5% sign. level
        RV for 10% sign. level
        RV2 for 1% sign. level
        RV2 for 5% sign. level
        RV2 for 10% sign. level
        """

        tree = self.perf_ind_panel.tree

        root_sd = tree.AddRoot(u'Sensory data')
        tree.SetItemData(root_sd, None)
        root = tree.AppendItem(root_sd, u'Original performance indices')
        tree.SetItemData(root, None)
        child = tree.AppendItem(root, u"Overview Plot")
        tree.SetItemData(child, [u"Overview Plot"])
        tree.SetItemTextColour(child, 'DARK GREEN')
        child = tree.AppendItem(root, u'Indices table')
        tree.SetItemData(child, [u'Indices table'])
        tree.SetItemTextColour(child, 'BLUE')    
        child = tree.AppendItem(root, u'AGR prod')
        tree.SetItemData(child, [u'AGR prod'])   
        child = tree.AppendItem(root, u'AGR att')
        tree.SetItemData(child, [u'AGR att'])  
        child = tree.AppendItem(root, u'REP prod')
        tree.SetItemData(child, [u'REP prod']) 
        child = tree.AppendItem(root, u'REP att')
        tree.SetItemData(child, [u'REP att']) 
        child = tree.AppendItem(root, u'DIS total')
        tree.SetItemData(child, [u'DIS total']) 
        child = tree.AppendItem(root, u'DIS panel-1')
        tree.SetItemData(child, [u'DIS panel-1']) 
        child = tree.AppendItem(root, u'p values for AGR and REP')
        tree.SetItemData(child, [u'p values for AGR and REP']) 
        child_sl = tree.AppendItem(root, u'Significance level tables')
        tree.SetItemData(child_sl, None)        
        
        child = tree.AppendItem(child_sl, u'RV for 1% sign. level')
        tree.SetItemData(child, [u'RV for 1% sign. level'])
        tree.SetItemTextColour(child, 'STEELBLUE3')       
        child = tree.AppendItem(child_sl, u'RV for 5% sign. level')
        tree.SetItemData(child, [u'RV for 5% sign. level'])
        tree.SetItemTextColour(child, 'STEELBLUE3')       
        child = tree.AppendItem(child_sl, u'RV for 10% sign. level')
        tree.SetItemData(child, [u'RV for 10% sign. level'])
        tree.SetItemTextColour(child, 'STEELBLUE3')       
        child = tree.AppendItem(child_sl, u'RV2 for 1% sign. level')
        tree.SetItemData(child, [u'RV2 for 1% sign. level'])
        tree.SetItemTextColour(child, 'NAVY')       
        child = tree.AppendItem(child_sl, u'RV2 for 5% sign. level')
        tree.SetItemData(child, [u'RV2 for 5% sign. level'])
        tree.SetItemTextColour(child, 'NAVY')       
        child = tree.AppendItem(child_sl, u'RV2 for 10% sign. level')
        tree.SetItemData(child, [u'RV2 for 10% sign. level'])
        tree.SetItemTextColour(child, 'NAVY')
        
        root = tree.AppendItem(root_sd, u'Standardized performance indices (only AGR and REP)')
        tree.SetItemData(root, None)
        child = tree.AppendItem(root, u'Indices table')
        tree.SetItemData(child, [u'Indices table std']) 
        tree.SetItemTextColour(child, 'BLUE') 
        
        tree.ExpandAll()
        tree.Collapse(child_sl)
        



    def create_plot(self, pydata, tab_panel):
        """
        Event handling function for mouse left double-click. Among other
        functionalities runs plot method.

        @type event:    object
        @param event:    An event is a structure holding information about an event passed to a callback or member function.

        @type tab:      string
        @param tab:     , ...
        """

        # default values:
        res = None
        plot = True # show plot
        grid = False # not grid
        grid_config = None # grid_config
        overview_plot = False # not overview plot

        #print pydata

        # This variable needs to be increased every time before a new
        # plot is created. Reason for this is that a new window is plotted
        # every time like figure(x)
        self.numberOfWindow += 1

        #figure draw settings: (grid, legend, legend location, limits)
        #drawSettings = [self.menuViewGrid, self.menuViewLegend, 'upper right', self.s_data.scale_limits]


        activeAssessors_List = []
        active_ass_inds = tab_panel.get_active_assessors()
        for ind in active_ass_inds:
            activeAssessors_List.append(self.AssessorList[ind])

        activeAttributes_List = []
        active_att_inds = tab_panel.get_active_attributes()
        for ind in active_att_inds:
            activeAttributes_List.append(self.AttributeList[ind])

        activeSamples_List = []
        active_samp_inds = tab_panel.get_active_samples()
        for ind in active_samp_inds:
            activeSamples_List.append(self.SampleList[ind])
        # ALL PLOT METHODS RETURNS A MODIFIED PLOTDATA OBJECT

        plot_title = ""


        # When line plot tab is active plot line plots
        # --------------------------------------------
        if tab_panel == self.line_panel:
            plot_title = "Line Plot"



            plot_data = PlotData(activeAssessors_List, activeAttributes_List, activeSamples_List, pydata, self.menuViewGrid, self.menuViewLegend)
            plot_data.set_limits(self.s_data.scale_limits)

            if pydata[0] == "Overview Plot":
                res = SampleLineOverviewPlotter(self.s_data, plot_data)
                overview_plot = True
            elif len(pydata) > 1 and pydata[1] == "Overview Plot":
                plot_data.view_legend = False
                res = AssessorLineOverviewPlotter(self.s_data, plot_data)
                overview_plot = True
            elif len(pydata) == 3:
                res = ReplicateLinePlotter(self.s_data, plot_data)
            #print pydata
            elif len(pydata) == 2:
                res = AssessorLinePlotter(self.s_data, plot_data)
            #print pydata
            elif len(pydata) == 1:
                res = SampleLinePlotter(self.s_data, plot_data)
            #print pydata
            else:
                print "The root!!!"

        # When mean & std plot tab is active plot:
        # ----------------------------------------------------------
        elif tab_panel ==  self.mean_std_panel:
            plot_title = "Mean/STD Plot"


            temp_plot_data = self.mean_plot_data

            if temp_plot_data == None:
                new_plot_data = CollectionCalcPlotData(activeAssessors_List, activeAttributes_List, activeSamples_List, pydata, self.menuViewGrid, self.menuViewLegend)
            elif temp_plot_data.actives_changed(activeAssessors_List, activeAttributes_List, activeSamples_List):
                new_plot_data = CollectionCalcPlotData(activeAssessors_List, activeAttributes_List, activeSamples_List, pydata, self.menuViewGrid, self.menuViewLegend)
            else:
                new_plot_data = CollectionCalcPlotData(activeAssessors_List, activeAttributes_List, activeSamples_List, pydata, self.menuViewGrid, self.menuViewLegend)
                # use old calc data:
                new_plot_data.copy_data(temp_plot_data)
                #temp_plot_data = new_plot_data

            self.mean_plot_data = new_plot_data
            self.mean_plot_data.set_limits(self.s_data.scale_limits)

            if pydata[0] in self.AssessorList:
                res = RawDataAssessorPlotter(self.s_data, self.mean_plot_data)
            elif pydata[0] in self.AttributeList:
                res = RawDataAttributePlotter(self.s_data, self.mean_plot_data)
            elif pydata[0] == "Overview Plot (assessors)":
                overview_plot = True
                res = RawDataAssessorOverviewPlotter(self.s_data, self.mean_plot_data)

            elif pydata[0] == "Overview Plot (attributes)":
                overview_plot = True
                res = RawDataAttributeOverviewPlotter(self.s_data, self.mean_plot_data)

        # When correlation plot tab is active plot correlation plots
        # ----------------------------------------------------------
        elif tab_panel == self.corr_panel:
            plot_title = "Correlation Plot"


            if len(pydata) == 2:

                #print pydata
                plot_data = PlotData(activeAssessors_List, activeAttributes_List, activeSamples_List, pydata, self.menuViewGrid, self.menuViewLegend) # no legend
                plot_data.set_limits(self.s_data.scale_limits)

                if pydata[1] == "Overview Plot":
                    res = CorrelationOverviewPlotter(self.s_data, plot_data)
                    overview_plot = True
                else:
                    res = CorrelationPlotter(self.s_data, plot_data)


        # When Tucker-1 plot tab is active plot Tucker-1 plots
        # ----------------------------------------------------
        elif tab_panel == self.tuck1_panel:
            plot_title = "Tucker-1 Plot"

            selection = []
            # Check which sorting or tree-ctrl the user chose:
            selection.append(self.tuck1_panel.get_radio_selection())
            selection.append(self.tuck1_radioBoxModel.GetSelection())
            print selection

            if self.tucker1_plot_data == None:
                #print "anova plot data is None"
                self.tucker1_plot_data = PCA_PlotData(activeAssessors_List, activeAttributes_List, activeSamples_List, pydata, self.menuViewGrid, self.menuViewLegend)

            elif self.tucker1_plot_data.actives_changed(activeAssessors_List, activeAttributes_List, activeSamples_List):
                #print "actives changed"
                self.tucker1_plot_data = PCA_PlotData(activeAssessors_List, activeAttributes_List, activeSamples_List, pydata, self.menuViewGrid, self.menuViewLegend)

            elif self.tucker1_plot_data.selection != selection:
                self.tucker1_plot_data = PCA_PlotData(activeAssessors_List, activeAttributes_List, activeSamples_List, pydata, self.menuViewGrid, self.menuViewLegend)

            else:
                new_plot_data = PCA_PlotData(activeAssessors_List, activeAttributes_List, activeSamples_List, pydata, self.menuViewGrid, self.menuViewLegend)

                # use same calc data:
                new_plot_data.copy_data(self.tucker1_plot_data)
                self.tucker1_plot_data = new_plot_data

            self.tucker1_plot_data.set_limits(self.s_data.scale_limits)

            if self.tuck1_cb.GetValue(): self.tucker1_plot_data.aspect = 'equal'
            else: self.tucker1_plot_data.aspect = 'auto'



            if pydata[0] == "Overview Plot (assessors)":
                res = Tucker1AssOverviewPlotter(self.s_data, self.tucker1_plot_data, selection)
                overview_plot = True
            elif pydata[0] == "Overview Plot (attributes)":
                res = Tucker1AttOverviewPlotter(self.s_data, self.tucker1_plot_data, selection)
                overview_plot = True
            else:
                res = Tucker1Plotter(self.s_data, self.tucker1_plot_data, selection=selection)



        elif tab_panel == self.profile_panel:
            plot_title = "Profile Plot"


            selection = []
            # Check which sorting or tree-ctrl the user chose:
            selection.append(self.profile_panel.get_radio_selection())
            selection.append(self.profile_radioBoxModel.GetSelection())


            temp_plot_data = self.profile_plot_data
            

            if temp_plot_data == None:
                new_plot_data = CollectionCalcPlotData(activeAssessors_List, activeAttributes_List, activeSamples_List, pydata, self.menuViewGrid, self.menuViewLegend)
            elif temp_plot_data.actives_changed(activeAssessors_List, activeAttributes_List, activeSamples_List):
                new_plot_data = CollectionCalcPlotData(activeAssessors_List, activeAttributes_List, activeSamples_List, pydata, self.menuViewGrid, self.menuViewLegend)
            else:
                new_plot_data = CollectionCalcPlotData(activeAssessors_List, activeAttributes_List, activeSamples_List, pydata, self.menuViewGrid, self.menuViewLegend)
                # use old calc data:
                new_plot_data.copy_data(temp_plot_data)

            self.profile_plot_data = new_plot_data
            self.profile_plot_data.special_opts["selection"] = selection

            self.profile_plot_data.set_limits(self.s_data.scale_limits)


            if pydata[0] == "Overview Plot":
                res = profileOverviewPlotter(self.s_data, self.profile_plot_data, selection=selection)
                overview_plot = True
            else:
                res = profilePlotter(self.s_data, self.profile_plot_data, selection=selection)



        elif tab_panel == self.egg_panel:
            plot_title = "Eggshell Plot"


            temp_plot_data = self.egg_plot_data

            if temp_plot_data == None:
                new_plot_data = CollectionCalcPlotData(activeAssessors_List, activeAttributes_List, activeSamples_List, pydata, self.menuViewGrid, self.menuViewLegend)
            elif temp_plot_data.actives_changed(activeAssessors_List, activeAttributes_List, activeSamples_List):
                new_plot_data = CollectionCalcPlotData(activeAssessors_List, activeAttributes_List, activeSamples_List, pydata, self.menuViewGrid, self.menuViewLegend)
            else:
                new_plot_data = CollectionCalcPlotData(activeAssessors_List, activeAttributes_List, activeSamples_List, pydata, self.menuViewGrid, self.menuViewLegend)
                # use old calc data:
                new_plot_data.copy_data(temp_plot_data)

            self.egg_plot_data = new_plot_data
            self.egg_plot_data.set_limits(self.s_data.scale_limits)


            if pydata[0] == "Overview Plot":
                res = EggshellOverviewPlotter(self.s_data, self.egg_plot_data)
                overview_plot = True
            else:
                res = EggshellPlotter(self.s_data, self.egg_plot_data)



        elif tab_panel == self.pmse_panel:
            plot_title = "p-MSE Plot"


            #plot_data = PlotData(activeAssessors_List, activeAttributes_List, activeSamples_List, pydata, self.menuViewGrid, self.menuViewLegend)

            if self.pmse_plot_data == None:
                #print "anova plot data is None"
                self.pmse_plot_data = ANOVA_PlotData(activeAssessors_List, activeAttributes_List, activeSamples_List, pydata, self.menuViewGrid, self.menuViewLegend)
            if self.pmse_plot_data.actives_changed(activeAssessors_List, activeAttributes_List, activeSamples_List):
                #print "actives changed"
                self.pmse_plot_data = ANOVA_PlotData(activeAssessors_List, activeAttributes_List, activeSamples_List, pydata, self.menuViewGrid, self.menuViewLegend)
            else:
                new_plot_data = ANOVA_PlotData(activeAssessors_List, activeAttributes_List, activeSamples_List, pydata, self.menuViewGrid, self.menuViewLegend)

                # use same calc data:
                new_plot_data.copy_data(self.pmse_plot_data)
                self.pmse_plot_data = new_plot_data

            self.pmse_plot_data.set_limits(self.s_data.scale_limits)

            if pydata[0] == "Overview Plot (assessors)" or pydata[0] == "Overview Plot (attributes)":
                res = pmse_OverviewPlotter(self.s_data, self.pmse_plot_data)
                overview_plot = True
            else:
                res = pmsePlotter(self.s_data, self.pmse_plot_data)


        elif tab_panel == self.f_panel:
            plot_title = "F/p Plot"
            # Check which sorting or tree-ctrl the user chose:
            selection = self.f_panel.get_radio_selection()
            print selection


            if self.f_plot_data == None:
                #print "anova plot data is None"
                self.f_plot_data = ANOVA_PlotData(activeAssessors_List, activeAttributes_List, activeSamples_List, pydata, self.menuViewGrid, self.menuViewLegend)
            if self.f_plot_data.actives_changed(activeAssessors_List, activeAttributes_List, activeSamples_List):
                #print "actives changed"
                self.f_plot_data = ANOVA_PlotData(activeAssessors_List, activeAttributes_List, activeSamples_List, pydata, self.menuViewGrid, self.menuViewLegend)
            else:
                new_plot_data = ANOVA_PlotData(activeAssessors_List, activeAttributes_List, activeSamples_List, pydata, self.menuViewGrid, self.menuViewLegend)

                # use same calc data:
                new_plot_data.copy_data(self.f_plot_data)
                self.f_plot_data = new_plot_data


            self.f_plot_data.set_limits(self.s_data.scale_limits)


            if len(pydata) == 2:
                # When user double-clicks on 'General Plot'
                if pydata[1] == u'General Plot':
                    # Go here if 'sorted by assessor' is selected
                    if selection == 0:
                        res = FPlotter_Assessor_General(self.s_data, self.f_plot_data)
                    elif selection == 1:
                        res = FPlotter_Attribute_General(self.s_data, self.f_plot_data)

                else:
                    # Go here if 'sorted by assessor' is selected
                    if selection == 0:
                        res = FPlotter_Assessor_Specific(self.s_data, self.f_plot_data)
                    elif selection == 1:
                        res = FPlotter_Attribute_Specific(self.s_data, self.f_plot_data)


        elif tab_panel == self.mse_panel:
            plot_title = "MSE Plot"

            # Check which sorting or tree-ctrl the user chose:
            selection = self.mse_panel.get_radio_selection()
            print selection

            if self.mse_plot_data == None:
                #print "anova plot data is None"
                self.mse_plot_data = ANOVA_PlotData(activeAssessors_List, activeAttributes_List, activeSamples_List, pydata, self.menuViewGrid, self.menuViewLegend)
            if self.mse_plot_data.actives_changed(activeAssessors_List, activeAttributes_List, activeSamples_List):
                #print "actives changed"
                self.mse_plot_data = ANOVA_PlotData(activeAssessors_List, activeAttributes_List, activeSamples_List, pydata, self.menuViewGrid, self.menuViewLegend)
            else:
                new_plot_data = ANOVA_PlotData(activeAssessors_List, activeAttributes_List, activeSamples_List, pydata, self.menuViewGrid, self.menuViewLegend)

                # use same calc data:
                new_plot_data.copy_data(self.mse_plot_data)
                self.mse_plot_data = new_plot_data


            self.mse_plot_data.set_limits(self.s_data.scale_limits)

            # When user double-clicks on 'General Plot'
            if pydata[0] == u'General Plot':
                # Go here if 'sorted by assessor' is selected
                if selection == 0:
                    res = MSEPlotter_Assessor_General(self.s_data, self.mse_plot_data)
                # Go here if 'sorted by attribute' is selected
                elif selection == 1:
                    res = MSEPlotter_Attribute_General(self.s_data, self.mse_plot_data)

            else:
                # Go here if 'sorted by assessor' is selected
                if selection == 0:
                    res = MSEPlotter_Assessor_Specific(self.s_data, self.mse_plot_data)
                # Go here if 'sorted by attribute' is selected
                elif selection == 1:
                    res = MSEPlotter_Attribute_Specific(self.s_data, self.mse_plot_data)


        # When original tab in Averages is active do the following
        # --------------------------------------------------------
        elif tab_panel == self.org_panel:
            plot_title = "Consensus Plot"

            selection = 0 # averOrg

            plot_data = PlotData(activeAssessors_List, activeAttributes_List, activeSamples_List, pydata, self.menuViewGrid, self.menuViewLegend)
            plot_data.set_limits(self.s_data.scale_limits)

            if self.org_cb.GetValue(): plot_data.aspect = 'equal'
            else: plot_data.aspect = 'auto'

            # When user double-clicks on 'Data'
            if pydata[0] == u'Averaged Data':
                plot = False # no plot
                grid = True # show grid
                frame_name, result_list = Averaged_Data_Grid(self.s_data, plot_data, selection=selection)

            # When user double-clicks on 'PCA scores'
            #elif pydata[0] == u'PCA Scores':
            #    res = PCA_plotter(self.s_data, plot_data, selection=selection)

            # When user double-clicks on 'PCA Loadings'
            #elif pydata[0] == u'PCA Loadings':
            #    res = PCA_plotter(self.s_data, plot_data, selection=selection)

            # When user double-clicks on 'PCA Correlation Loadings'
            #elif pydata[0] == u'PCA Correlation Loadings':
            #    res = PCA_plotter(self.s_data, plot_data, selection=selection)

            # When user double-clicks on 'PCA Explained Variance'
            #elif pydata[0] == u'PCA Explained Variance':

            else:
                res = PCA_plotter(self.s_data, plot_data, selection=selection)

        # When standardised tab in Averages is active do the following
        # ------------------------------------------------------------
        elif tab_panel == self.std_panel:
            plot_title = "Consensus Plot"

            selection = 1 # averStd

            plot_data = PlotData(activeAssessors_List, activeAttributes_List, activeSamples_List, pydata, self.menuViewGrid, self.menuViewLegend)
            plot_data.set_limits(self.s_data.scale_limits)

            if self.std_cb.GetValue(): plot_data.aspect = 'equal'
            else: plot_data.aspect = 'auto'

            # When user double-clicks on 'Data'
            if pydata[0] == u'Averaged Data':
                plot = False # no plot
                grid = True # show grid
                frame_name, result_list = Averaged_Data_Grid(self.s_data, plot_data, selection=selection)

            # When user double-clicks on 'PCA scores'
            #elif pydata[0] == u'PCA Scores':
            #    res = PCA_plotter(self.s_data, plot_data, selection=selection)


            # When user double-clicks on 'PCA Loadings'
            #elif pydata[0] == u'PCA Loadings':
            #    res = PCA_plotter(self.s_data, plot_data, selection=selection)


            # When user double-clicks on 'PCA Correlation Loadings'
            #elif pydata[0] == u'PCA Correlation Loadings':
            #    res = PCA_plotter(self.s_data, plot_data, selection=selection)


            # When user double-clicks on 'PCA Explained Variance'
            #elif pydata[0] == u'PCA Explained Variance':
            else:
                res = PCA_plotter(self.s_data, plot_data, selection=selection)


        # When standardised tab in Averages is active do the following
        # ------------------------------------------------------------
        elif tab_panel == self.statis_panel:
            plot_title = "STATIS Plot"

            selection = self.statis_panel.get_radio_selection()
            print selection

            plot_data = PlotData(activeAssessors_List, activeAttributes_List, activeSamples_List, pydata, self.menuViewGrid, self.menuViewLegend)
            plot_data.set_limits(self.s_data.scale_limits)

            if self.statis_cb.GetValue(): plot_data.aspect = 'equal'
            else: plot_data.aspect = 'auto'

            # When user double-clicks on 'Data'
            if pydata[0] == u'Averaged Data':
                plot = False # no plot
                grid = True # show grid
                frame_name, result_list = STATIS_Averaged_Data_Grid(self.s_data, plot_data, selection=selection)

            # When user double-clicks on 'PCA scores'
            #elif pydata[0] == u'PCA Scores':
            #    res = STATIS_PCA_Plotter(self.s_data, plot_data, selection=selection)

            # When user double-clicks on 'PCA Loadings'
            #elif pydata[0] == u'PCA Loadings':
            #    res = STATIS_PCA_Plotter(self.s_data, plot_data, selection=selection)

            # When user double-clicks on 'PCA Correlation Loadings'
            #elif pydata[0] == u'PCA Correlation Loadings':
            #    res = STATIS_PCA_Plotter(self.s_data, plot_data, selection=selection)

            # When user double-clicks on 'PCA Explained Variance'
            #elif pydata[0] == u'PCA Explained Variance':
            #    res = STATIS_PCA_Plotter(self.s_data, plot_data, selection=selection)

            # When user double-clicks on 'Weights'
            elif pydata[0] == u'Assessor Weights':
                res = STATIS_AssWeight_Plotter(self.s_data, plot_data, selection=selection)
            else:
                res = STATIS_PCA_Plotter(self.s_data, plot_data, selection=selection)




        elif tab_panel == self.mm_anova_panel1:
            plot_title = "2-way ANOVA (1 rep) Plot"


            #if self.mm_anova1_plot_data == None:
                #print "anova plot data is None"
            self.mm_anova1_plot_data = MM_ANOVA_PlotData(activeAssessors_List, activeAttributes_List, activeSamples_List, pydata, self.menuViewGrid, self.menuViewLegend)
            #if self.mm_anova1_plot_data.actives_changed(activeAssessors_List, activeAttributes_List, activeSamples_List):
                #print "actives changed"
            #    self.mm_anova1_plot_data  = MM_ANOVA_PlotData(activeAssessors_List, activeAttributes_List, activeSamples_List, pydata, self.menuViewGrid, self.menuViewLegend)
            #else:
            #    new_plot_data  = MM_ANOVA_PlotData(activeAssessors_List, activeAttributes_List, activeSamples_List, pydata, self.menuViewGrid, self.menuViewLegend)

                # use same calc data:
            #    new_plot_data.copy_data(self.mm_anova1_plot_data)
            #    self.mm_anova1_plot_data = new_plot_data

            self.mm_anova1_plot_data.set_limits(self.s_data.scale_limits)




            _types = ['F1', 'F2']
            lsd_types = ['LSD1', 'LSD2']

            if pydata[0] == "Overview Plot 1": # F & p
                res = MixModel_ANOVA_OverviewPlotter(self.s_data, self.mm_anova1_plot_data, plot_type="2way1rep")
                overview_plot = True
            elif pydata[0] == "Overview Plot 2": # LSD
                res = MixModel_ANOVA_LSD_OverviewPlotter(self.s_data, self.mm_anova1_plot_data, plot_type="2way1rep")
                overview_plot = True
            elif pydata[0] in _types:
                res = MixModel_ANOVA_Plotter_2way1rep(self.s_data, self.mm_anova1_plot_data )
            elif pydata[0] in lsd_types:
                res = MixModel_ANOVA_LSD_Plotter_2way1rep(self.s_data, self.mm_anova1_plot_data )





        elif tab_panel == self.mm_anova_panel2:
            plot_title = "2-way ANOVA Plot"


            #if self.mm_anova2_plot_data == None:
                #print "anova plot data is None"
            self.mm_anova2_plot_data = MM_ANOVA_PlotData(activeAssessors_List, activeAttributes_List, activeSamples_List, pydata, self.menuViewGrid, self.menuViewLegend)
            #if self.mm_anova2_plot_data.actives_changed(activeAssessors_List, activeAttributes_List, activeSamples_List):
                #print "actives changed"
            #    self.mm_anova2_plot_data  = MM_ANOVA_PlotData(activeAssessors_List, activeAttributes_List, activeSamples_List, pydata, self.menuViewGrid, self.menuViewLegend)
            #else:
            #    new_plot_data  = MM_ANOVA_PlotData(activeAssessors_List, activeAttributes_List, activeSamples_List, pydata, self.menuViewGrid, self.menuViewLegend)

                # use same calc data:
            #    new_plot_data.copy_data(self.mm_anova2_plot_data)
            #    self.mm_anova2_plot_data = new_plot_data

            self.mm_anova2_plot_data.set_limits(self.s_data.scale_limits)




            _types = ['F1', 'F2', 'F3']
            lsd_types = ['LSD1', 'LSD2']

            if pydata[0] == "Overview Plot 1": # F & p
                res = MixModel_ANOVA_OverviewPlotter(self.s_data, self.mm_anova2_plot_data, plot_type="2way")
                overview_plot = True
            elif pydata[0] == "Overview Plot 2": # LSD
                res = MixModel_ANOVA_LSD_OverviewPlotter(self.s_data, self.mm_anova2_plot_data, plot_type="2way")
                overview_plot = True
            elif pydata[0] in _types:
                res = MixModel_ANOVA_Plotter_2way(self.s_data, self.mm_anova2_plot_data )
            elif pydata[0] in lsd_types:
                res = MixModel_ANOVA_LSD_Plotter_2way(self.s_data, self.mm_anova2_plot_data )




        elif tab_panel == self.mm_anova_panel3:
            plot_title = "3-way ANOVA Plot"


            #if self.mm_anova3_plot_data == None:
                #print "anova plot data is None"
            self.mm_anova3_plot_data = MM_ANOVA_PlotData(activeAssessors_List, activeAttributes_List, activeSamples_List, pydata, self.menuViewGrid, self.menuViewLegend)
            #if self.mm_anova3_plot_data.actives_changed(activeAssessors_List, activeAttributes_List, activeSamples_List):
                #print "actives changed"
            #    self.mm_anova3_plot_data  = MM_ANOVA_PlotData(activeAssessors_List, activeAttributes_List, activeSamples_List, pydata, self.menuViewGrid, self.menuViewLegend)
            #else:
            #    new_plot_data  = MM_ANOVA_PlotData(activeAssessors_List, activeAttributes_List, activeSamples_List, pydata, self.menuViewGrid, self.menuViewLegend)

                # use same calc data:
             #   new_plot_data.copy_data(self.mm_anova3_plot_data)
             #   self.mm_anova3_plot_data = new_plot_data

            self.mm_anova3_plot_data.set_limits(self.s_data.scale_limits)




            _types = ['F1', 'F2', 'F2b', 'F3', 'F4', 'F5']
            lsd_types = ['LSD1', 'LSD2']

            if pydata[0] == "Overview Plot 1": # F & p
                res = MixModel_ANOVA_OverviewPlotter(self.s_data, self.mm_anova3_plot_data, plot_type="3way")
                overview_plot = True
            elif pydata[0] == "Overview Plot 2": # LSD
                res = MixModel_ANOVA_LSD_OverviewPlotter(self.s_data, self.mm_anova3_plot_data, plot_type="3way")
                overview_plot = True
            elif pydata[0] in _types:
                res = MixModel_ANOVA_Plotter_3way(self.s_data, self.mm_anova3_plot_data )
            elif pydata[0] in lsd_types:
                res = MixModel_ANOVA_LSD_Plotter_3way(self.s_data, self.mm_anova3_plot_data )





        elif tab_panel == self.manh_panel:
            plot_title = "Manhattan Plot"


            maxPCs = int(self.manh_spin_txt.GetValue())
            selection = self.manh_panel.get_radio_selection()

            # view legend is not used in Manhattan plots
            if self.manh_plot_data == None:
                self.manh_plot_data = CollectionCalcPlotData(activeAssessors_List, activeAttributes_List, activeSamples_List, pydata, self.menuViewGrid, self.menuViewLegend)
            elif self.manh_plot_data.actives_changed(activeAssessors_List, activeAttributes_List, activeSamples_List):
                self.manh_plot_data = CollectionCalcPlotData(activeAssessors_List, activeAttributes_List, activeSamples_List, pydata, self.menuViewGrid, self.menuViewLegend)
            elif self.manh_plot_data.maxPCs != maxPCs:
                self.manh_plot_data = CollectionCalcPlotData(activeAssessors_List, activeAttributes_List, activeSamples_List, pydata, self.menuViewGrid, self.menuViewLegend)
            elif self.manh_plot_data.selection != selection:
                self.manh_plot_data = CollectionCalcPlotData(activeAssessors_List, activeAttributes_List, activeSamples_List, pydata, self.menuViewGrid, self.menuViewLegend)
            else:
                new_plot_data = CollectionCalcPlotData(activeAssessors_List, activeAttributes_List, activeSamples_List, pydata, self.menuViewGrid, self.menuViewLegend)
                # use old calc data:
                new_plot_data.copy_data(self.manh_plot_data)
                self.manh_plot_data = new_plot_data

            self.manh_plot_data.set_limits(self.s_data.scale_limits)
            self.manh_plot_data.maxPCs = maxPCs

            if pydata[0] == "Overview Plot (assessors)":
                res = ManhattanAssOverviewPlotter(self.s_data, self.manh_plot_data, selection=selection)
                overview_plot = True
            elif pydata[0] == "Overview Plot (attributes)":
                res = ManhattanAttOverviewPlotter(self.s_data, self.manh_plot_data, selection=selection)
                overview_plot = True
            else:
                res = ManhattanPlotter(self.s_data, self.manh_plot_data, selection=selection)


        elif tab_panel == self.perf_ind_panel:
            plot_title = "Performance Indices Plot"
            
            new_plot_data = CollectionCalcPlotData(activeAssessors_List, activeAttributes_List, activeSamples_List, pydata, self.menuViewGrid, self.menuViewLegend)
            
            #performance indices settings
            new_plot_data.special_opts["agr"] = self.perf_ind_spin_agr.GetValue()
            new_plot_data.special_opts["rep"] = self.perf_ind_spin_rep.GetValue()
            new_plot_data.special_opts["dis"] = self.perf_ind_spin_dis.GetValue()
            new_plot_data.special_opts["lvl"] = "same for all" #self.perf_ind_rb_lvl.GetStringSelection()
            new_plot_data.special_opts["comp"] = self.perf_ind_rb_comp.GetStringSelection()
            new_plot_data.special_opts["target_lvl"] = self.perf_ind_cbl_include.IsChecked(0)
            new_plot_data.special_opts["1_sign_lvl"] = self.perf_ind_cbl_include.IsChecked(1)
            new_plot_data.special_opts["5_sign_lvl"] = self.perf_ind_cbl_include.IsChecked(2)
            new_plot_data.special_opts["10_sign_lvl"] = self.perf_ind_cbl_include.IsChecked(3)
            new_plot_data.special_opts["recalc"] = True
            
            if self.perf_ind_data == None:
                self.perf_ind_data = new_plot_data
            elif self.perf_ind_data.actives_changed(activeAssessors_List, activeAttributes_List, activeSamples_List):
                self.perf_ind_data = new_plot_data
            else:
                recalc = False
                if new_plot_data.special_opts["comp"] != self.perf_ind_data.special_opts["comp"]:              
                    self.perf_ind_data.special_opts["recalc"] = True
                    recalc = True
                    
                if recalc:
                    self.perf_ind_data = new_plot_data
                else:
                    new_plot_data.copy_data(self.perf_ind_data)
                    self.perf_ind_data = new_plot_data
                    self.perf_ind_data.special_opts["recalc"] = False
            
            print self.perf_ind_data.special_opts
            
            if pydata[0] == "Overview Plot":
                
                res = perfind_OverviewPlotter(self.s_data, self.perf_ind_data, selection=0)
                overview_plot = True
            else:
                res = perfindPlotter(self.s_data, self.perf_ind_data, selection=0)
                if(res == None): return
                
                result_list = self.perf_ind_data.numeric_data
                grid_config = self.perf_ind_data.numeric_data_config
                frame_name = "Performance Indices - " + str(pydata[0])
                plot = self.perf_ind_data.special_opts["plot_frame"]
                
                if pydata[0] == u"Indices table":
                    self.figureList.append(GridFramePerfInd(self, frame_name, result_list, self.s_data, res, config=grid_config))
                    if self.figureList[len(self.figureList)-1] != None:
                        self.figureList[len(self.figureList)-1].Show()
                        return             


        if plot:
            #try:
            _title = {"fig":"Fig. " + str(self.numberOfWindow), "plot":plot_title}

            self.statusBar.SetStatusText(self.s_data.abspath)

            if res == None: print "Plotting failed!"; self.statusBar.SetStatusText("Plotting failed!")
            else:
                self.figureList.append(PlotFrame(None, _title, self.s_data, res, self))
                if self.figureList[len(self.figureList)-1] != None:
                    self.figureList[len(self.figureList)-1].Show()
            #except:
            #    print "Plotting failed!"

        else:
            self.figureList.append(GridFrame(self, frame_name, result_list, config=grid_config))
            if self.figureList[len(self.figureList)-1] != None:
                self.figureList[len(self.figureList)-1].Show()
    ###########NECESSARY_CUSTOM_METHODS_END###########


    def OnGeneralFileOpen(self, fileName, delimiter):
        """
        Opens a file with a help function from LoadData class

        """
        self.preloading()
        self.statusBar.SetStatusText("Opening file...")
        self.summaryFrame.append_text(fileName + "\n")
        self.summaryFrame.set_gauge(0)

        # Supported formats
        # .wk1 .wk3 .wk4; Lotus Worksheets. Can often be converted by Excel.
        # .xls .xlw; Microsoft Excel Spreadsheet, Excel Workbook
        # .txt .dat .*; various text formats
        if(fileName[-4:] == ".xls" or fileName[-5:] == ".xlsx" or fileName[-4:] == ".xlw" or fileName[-4:] == ".wk1" or fileName[-4:] == ".wk3" or fileName[-4:] == ".wk4"):
            # Trying to open using Excel method in LoadData.py
            self.delimiter = delimiter
            newData = Excel(self, fileName, self.summaryFrame)
        else:
            # Trying to open using PlainText method in LoadData.py
            self.delimiter = delimiter
            newData = PlainText(self, fileName, self.summaryFrame, delimiter)

        if(newData.fileRead):

            self.summaryFrame.append_text("\nLoading data...\n")

            self.s_data = newData.s_data
            self.update_tabs()
        else:
            print "Failed to load file"
            self.summaryFrame.Destroy()
            self.statusBar.SetStatusText("Failed to load file")


    def OnGeneralFileOpenRecent(self, event):
        """
        Opens a file with a help function from LoadData class

        """

        recent_ind = self.recent_inds.index(event.GetId())
        fileName = self.session_data.recent_files[recent_ind][0]
        delimiter = self.session_data.recent_files[recent_ind][1]

        self.preloading()
        self.statusBar.SetStatusText("Opening file...")
        self.summaryFrame.append_text(fileName + "\n")
        self.summaryFrame.set_gauge(0)

        # Supported formats
        # .wk1 .wk3 .wk4; Lotus Worksheets. Can often be converted by Excel.
        # .xls .xlw; Microsoft Excel Spreadsheet, Excel Workbook
        # .txt .dat .*; various text formats
        if(fileName[-4:] == ".xls" or fileName[-5:] == ".xlsx" or fileName[-4:] == ".xlw" or fileName[-4:] == ".wk1" or fileName[-4:] == ".wk3" or fileName[-4:] == ".wk4"):
            # Trying to open using Excel method in LoadData.py
            self.delimiter = delimiter
            newData = Excel(self, fileName, self.summaryFrame)
        else:
            # Trying to open using PlainText method in LoadData.py
            self.delimiter = delimiter
            newData = PlainText(self, fileName, self.summaryFrame, delimiter)

        if(newData.fileRead):

            self.summaryFrame.append_text("\nLoading data...\n")

            self.s_data = newData.s_data
            self.update_tabs()
        else:
            print "Failed to load file"
            self.summaryFrame.Destroy()
            self.statusBar.SetStatusText("Failed to load file")



class DropTarget(wx.FileDropTarget):
    def __init__(self, parent):
        wx.FileDropTarget.__init__(self)
        self.parent = parent

    def OnDropFiles(self, x, y, filenames):
        self.OnGeneralFileOpen(filenames[0])



    def OnGeneralFileOpen(self, fileName):
        """
        Opens a file with a help function from LoadData class

        """
        self.parent.preloading()
        self.parent.statusBar.SetStatusText("Opening file...")
        self.parent.summaryFrame.append_text(fileName + "\n")
        self.parent.summaryFrame.set_gauge(0)

        # Supported formats
        # .wk1 .wk3 .wk4; Lotus Worksheets. Can often be converted by Excel.
        # .xls .xlw; Microsoft Excel Spreadsheet, Excel Workbook
        # .txt .dat .*; various text formats
        if(fileName[-4:] == ".xls" or fileName[-5:] == ".xlsx" or fileName[-4:] == ".xlw" or fileName[-4:] == ".wk1" or fileName[-4:] == ".wk3" or fileName[-4:] == ".wk4"):
            # Trying to open using Excel method in LoadData.py
            self.parent.delimiter = ''
            newData = Excel(self.parent, fileName, self.parent.summaryFrame)
        elif fileName[-4:] == ".csv":
            # Trying to open using PlainText method in LoadData.py
            self.parent.delimiter = ';'
            newData = PlainText(self.parent, fileName, self.parent.summaryFrame, ';')
        else:
            # Trying to open using PlainText method in LoadData.py
            self.parent.delimiter = '\t'
            newData = PlainText(self.parent, fileName, self.parent.summaryFrame, '\t')
        if(newData.fileRead):

            self.parent.summaryFrame.append_text("\nLoading data...\n")

            self.parent.s_data = newData.s_data
            self.parent.update_tabs()
        else:
            print "Failed to load file"
            self.parent.summaryFrame.Destroy()
            self.parent.statusBar.SetStatusText("Failed to load file")
