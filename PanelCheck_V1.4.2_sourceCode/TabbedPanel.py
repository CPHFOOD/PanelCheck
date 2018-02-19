import wx


class TabPanel(wx.Panel):
    def __init__(self, parent=-1, func=None, choice=None, active_checkbox=[True, True, True], **kwargs):
        wx.Panel.__init__(self, parent, -1, style=wx.CLIP_CHILDREN, **kwargs)
        
        # function to run when tree is double clicked
        self.func = func
        
        # pointer to choice list
        self.choice = choice
        
        self.changes = {}
        
        
        
        
        self.tree = wx.TreeCtrl(id=wx.NewId(),
              name=u'tree', parent=self, size=wx.Size(250, 400),
              style=wx.TR_HAS_BUTTONS | wx.TR_DEFAULT_STYLE | wx.SUNKEN_BORDER)
        
        self.tree.Bind(wx.EVT_LEFT_DCLICK, self.on_tree_left_double_click)
        
        

        
        
        self.text_Ass = wx.StaticText(id=wx.NewId(),
              label=u'Assessors:', name=u'text_Ass', parent=self, style=0)
        self.text_Att = wx.StaticText(id=wx.NewId(),
              label=u'Attributes:', name=u'text_Att', parent=self, style=0)
        self.text_Samp = wx.StaticText(id=wx.NewId(),
              label=u'Samples:', name=u'text_Samp', parent=self, style=0)
              
              
        c_ass_id=wx.NewId()
        c_att_id=wx.NewId()
        c_samp_id=wx.NewId()
        
        
            
        self.checkList_Ass = wx.CheckListBox(choices=[],
              id=c_ass_id, name=u'checkList_Ass',
              parent=self, style=0)
        self.checkList_Ass.Bind(wx.EVT_CHECKLISTBOX,
              self.on_ass_checkList_AssChecklistbox,
              id=c_ass_id)
        self.checkList_Ass.Bind(wx.EVT_LISTBOX,
              self.on_ass_checkList_AssListbox,
              id=c_ass_id)
        self.checkList_Ass.Enable(active_checkbox[0])
             
        self.checkList_Att = wx.CheckListBox(choices=[],
              id=c_att_id, name=u'checkList_Att',
              parent=self, style=0)
        self.checkList_Att.Bind(wx.EVT_CHECKLISTBOX,
              self.on_att_checkList_AttChecklistbox,
              id=c_att_id)
        self.checkList_Att.Bind(wx.EVT_LISTBOX,
              self.on_att_checkList_AttListbox,
              id=c_att_id)
        self.checkList_Att.Enable(active_checkbox[1])

        self.checkList_Samp = wx.CheckListBox(choices=[],
              id=c_samp_id, name=u'checkList_Samp',
              parent=self, style=0)
        self.checkList_Samp.Bind(wx.EVT_CHECKLISTBOX,
              self.on_samp_checkList_SampChecklistbox,
              id=wx.NewId())
        self.checkList_Samp.Bind(wx.EVT_LISTBOX,
              self.on_samp_checkList_SampListbox,
              id=c_samp_id)
        self.checkList_Samp.Enable(active_checkbox[2]) 
        
        
        butt_ass_en_id=wx.NewId()
        butt_ass_di_id=wx.NewId()
        
        butt_att_en_id=wx.NewId()
        butt_att_di_id=wx.NewId()
        
        butt_samp_en_id=wx.NewId()
        butt_samp_di_id=wx.NewId()

        self.button_Ass_EnableAll = wx.Button(id=butt_ass_en_id,
              label=u'Enable all', name=u'button_Ass_EnableAll',
              parent=self, style=0)
        self.button_Ass_EnableAll.Enable(active_checkbox[0])
        self.button_Ass_EnableAll.Bind(wx.EVT_BUTTON,
              self.on_ass_enable_all,
              id=butt_ass_en_id)

        self.button_Ass_DisableAll = wx.Button(id=butt_ass_di_id,
              label=u'Disable all', name=u'button_Ass_DisableAll',
              parent=self, style=0)
        self.button_Ass_DisableAll.Enable(active_checkbox[0])
        self.button_Ass_DisableAll.Bind(wx.EVT_BUTTON,
              self.on_ass_disable_all,
              id=butt_ass_di_id)

        self.button_Att_EnableAll = wx.Button(id=butt_att_en_id,
              label=u'Enable all', name=u'button_Att_EnableAll',
              parent=self, style=0)
        self.button_Att_EnableAll.Enable(active_checkbox[1])
        self.button_Att_EnableAll.Bind(wx.EVT_BUTTON,
              self.on_att_enable_all,
              id=butt_att_en_id)

        self.button_Att_DisableAll = wx.Button(id=butt_att_di_id,
              label=u'Disable all', name=u'button_Att_DisableAll',
              parent=self, style=0)
        self.button_Att_DisableAll.Enable(active_checkbox[1])
        self.button_Att_DisableAll.Bind(wx.EVT_BUTTON,
              self.on_att_disable_all,
              id=butt_att_di_id)

        self.button_Samp_EnableAll = wx.Button(id=butt_samp_en_id,
              label=u'Enable all', name=u'button_Samp_EnableAll',
              parent=self, style=0)
        self.button_Samp_EnableAll.Enable(active_checkbox[2])
        self.button_Samp_EnableAll.Bind(wx.EVT_BUTTON,
              self.on_samp_enable_all,
              id=butt_samp_en_id)

        self.button_Samp_DisableAll = wx.Button(id=butt_samp_di_id,
              label=u'Disable all', name=u'button_Samp_DisableAll',
              parent=self, style=0)
        self.button_Samp_DisableAll.Enable(active_checkbox[2])      
        self.button_Samp_DisableAll.Bind(wx.EVT_BUTTON,
              self.on_samp_disable_all,
              id=butt_samp_di_id)
              


        ass_butt_box = wx.BoxSizer(wx.VERTICAL)
        att_butt_box = wx.BoxSizer(wx.VERTICAL)
        samp_butt_box = wx.BoxSizer(wx.VERTICAL)

        
        # assessor check list sizer
        self.ass_sizer = wx.BoxSizer(wx.VERTICAL)
        ass_butt_box.Add(self.button_Ass_EnableAll, 0, wx.FIXED_MINSIZE|wx.ALIGN_CENTER)
        ass_butt_box.AddSpacer(4)
        ass_butt_box.Add(self.button_Ass_DisableAll, 0, wx.FIXED_MINSIZE|wx.ALIGN_CENTER)
        
        self.ass_sizer.Add(self.text_Ass, 0, wx.FIXED_MINSIZE|wx.ALIGN_CENTER)
        self.ass_sizer.Add(self.checkList_Ass, 1, wx.GROW)
        self.ass_sizer.AddSpacer(10)
        self.ass_sizer.Add(ass_butt_box, 0, wx.FIXED_MINSIZE|wx.ALIGN_CENTER)

        
        # attribute check list sizer
        self.att_sizer = wx.BoxSizer(wx.VERTICAL)
        att_butt_box.Add(self.button_Att_EnableAll, 0, wx.FIXED_MINSIZE|wx.ALIGN_CENTER)
        att_butt_box.AddSpacer(4)
        att_butt_box.Add(self.button_Att_DisableAll, 0, wx.FIXED_MINSIZE|wx.ALIGN_CENTER) 
        
        self.att_sizer.Add(self.text_Att, 0, wx.FIXED_MINSIZE|wx.ALIGN_CENTER)
        self.att_sizer.Add(self.checkList_Att, 1, wx.GROW)
        self.att_sizer.AddSpacer(10)
        self.att_sizer.Add(att_butt_box, 0, wx.FIXED_MINSIZE|wx.ALIGN_CENTER)        
  
  
  
        # sample check list sizer
        self.samp_sizer = wx.BoxSizer(wx.VERTICAL)
        samp_butt_box.Add(self.button_Samp_EnableAll, 0, wx.FIXED_MINSIZE|wx.ALIGN_CENTER)
        samp_butt_box.AddSpacer(4)
        samp_butt_box.Add(self.button_Samp_DisableAll, 0, wx.FIXED_MINSIZE|wx.ALIGN_CENTER)         

        self.samp_sizer.Add(self.text_Samp, 0, wx.FIXED_MINSIZE|wx.ALIGN_CENTER)
        self.samp_sizer.Add(self.checkList_Samp, 1, wx.GROW)
        self.samp_sizer.AddSpacer(10)
        self.samp_sizer.Add(samp_butt_box, 0, wx.FIXED_MINSIZE|wx.ALIGN_CENTER)
        
        
        check_grid_box = wx.GridSizer(1, 3, 10, 10)
        check_grid_box.Add(self.ass_sizer, 1, wx.GROW)
        check_grid_box.Add(self.att_sizer, 1, wx.GROW)
        check_grid_box.Add(self.samp_sizer, 1, wx.GROW)
        
        
        self.left_part = wx.BoxSizer(wx.VERTICAL)
        self.left_part.AddSpacer(10)
        self.left_part.Add(self.tree, 1, wx.GROW)
        self.left_part.AddSpacer(10)
        
        self.right_part = wx.BoxSizer(wx.VERTICAL)
        self.right_part.AddSpacer(10)
        self.right_part.Add(check_grid_box, 1, wx.GROW)
        self.right_part.AddSpacer(10)
        
        
        self.main_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.main_sizer.AddSpacer(10)
        self.main_sizer.Add(self.left_part, 0, wx.EXPAND|wx.BOTTOM)
        self.main_sizer.AddSpacer(20)
        self.main_sizer.Add(self.right_part, 1, wx.GROW)
        self.main_sizer.AddSpacer(10)
        
        self.SetSizer(self.main_sizer)
        

    def clear_lists(self):
        self.checkList_Ass.Clear()
        self.checkList_Att.Clear()
        self.checkList_Samp.Clear()
    
    def clear_tree(self):
        self.tree.DeleteAllItems()
        
    def clear_all(self):
        self.clear_lists()
        self.clear_tree()
        


    def expand_tree(self):
        root = self.tree.GetRootItem()
        self.tree.Expand(root)    
    
    def get_active_assessors(self):
        # returns the indices of active elements
        return self.get_ActivesFromCheckBoxList(self.checkList_Ass)
    
    def get_active_attributes(self):
        # returns the indices of active elements
        return self.get_ActivesFromCheckBoxList(self.checkList_Att) 
    
    def get_active_samples(self):
        # returns the indices of active elements
        return self.get_ActivesFromCheckBoxList(self.checkList_Samp)
        
        
    def set_lists(self, assessors, attributes, samples):
        self.fill_checkBoxList(assessors, self.checkList_Ass)
        self.fill_checkBoxList(attributes, self.checkList_Att)
        self.fill_checkBoxList(samples, self.checkList_Samp)
        
        
 
 
    ################# GUI EVENT HANDLING #################
    
    def on_tree_left_double_click(self, event):
	item = self.tree.GetSelection()
	if item.IsOk():
	    pydata = self.tree.GetItemData(item)
	    if pydata != None:
                self.func(pydata, self)
 
 
 
    def on_ass_checkList_AssChecklistbox(self, event):
        self.change_selection(event)
        
    def on_ass_checkList_AssListbox(self, event):
        self.set_selection(event)
        
    def on_att_checkList_AttChecklistbox(self, event):
        self.change_selection(event)
        
    def on_att_checkList_AttListbox(self, event):
        self.set_selection(event)
        
    def on_samp_checkList_SampChecklistbox(self, event):
        self.change_selection(event)
        
    def on_samp_checkList_SampListbox(self, event):
        self.set_selection(event) 
 
 
 
    def on_ass_disable_all(self, event):
        self.check_checkBoxList(self.checkList_Ass, False)
        
    def on_ass_enable_all(self, event):
        self.check_checkBoxList(self.checkList_Ass, True)
    
    def on_att_disable_all(self, event):
        self.check_checkBoxList(self.checkList_Att, False)
        
    def on_att_enable_all(self, event):
        self.check_checkBoxList(self.checkList_Att, True)
    
    def on_samp_disable_all(self, event):
        self.check_checkBoxList(self.checkList_Samp, False)
        
    def on_samp_enable_all(self, event):
        self.check_checkBoxList(self.checkList_Samp, True)
        
        
        
        
        
        
        
    ################# TabPanel Tools #################
    
    def fill_checkBoxList(self, xlist, parent, check=True):
            """
            Fills given CheckBoxList with elements. All elements are checked
            by default.
            
            @type parent:   wx.CheckBoxList          
            @type list:     list
            @param list:    A complete list (AssessorsList, AttributeList or SampleList). 
            """
            for item in xlist:
                parent.Append(item)
            for item in range(parent.GetCount()):
                parent.Check(item, check)
                
                
        
    def check_checkBoxList(self, parent, check):
            """
            Checks/unchecks all items in given parent (CheckBoxList) with given check (boolean).
            
            @type parent:   wx.CheckBoxList          
            @type check:    boolean         
            @param list:    AssessorList, AttributeList or SampleList
            """
            for i in range(parent.GetCount()):
                parent.Check(i, check)
                
                
                
    def get_ActivesFromCheckBoxList(self, parent):
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
            
            
    def set_selection(self, event):

        
        obj = event.GetEventObject()
        amount = obj.GetCount() # amount of elements in list
        i = self.choice.GetCurrentSelection() # index of current element in choice list
        j = obj.GetSelection() # index of current element in list
        
        if j >= 0:
        
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
            


    def get_selection_ass_att_samp(self):
        changes = {}
        
        changes["ass"] = self.get_ActivesFromCheckBoxList(self.checkList_Ass)
        changes["att"] = self.get_ActivesFromCheckBoxList(self.checkList_Att)
        changes["samp"] = self.get_ActivesFromCheckBoxList(self.checkList_Samp)
        
        return changes
        

    def update_selection(self, changes): # dict of "ass", "att" or "samp" with indices for update
        
        if changes.has_key("ass"):
            self.check_checkBoxList(self.checkList_Ass, False)
            for ind in changes["ass"]:
                self.checkList_Ass.Check(ind, True)

        if changes.has_key("att"):
            self.check_checkBoxList(self.checkList_Att, False)
            for ind in changes["att"]:
                self.checkList_Att.Check(ind, True)

        if changes.has_key("samp"):
            self.check_checkBoxList(self.checkList_Samp, False)
            for ind in changes["samp"]:
                self.checkList_Samp.Check(ind, True)
                    
        
                
    def change_selection(self, event):
        event.Skip()
        
        
        

class RadioTabPanel(TabPanel):
    def __init__(self, parent=-1, func_list=[None, None, None], choice=None, active_checkbox=[True, True, True], radiobox_choices=[], radio_label="", **kwargs):
        TabPanel.__init__(self, parent=parent, func=func_list[0], choice=choice, active_checkbox=active_checkbox, **kwargs)
        
        self.show_tree1 = func_list[1]
        self.show_tree2 = func_list[2]
        
        self.lower_right_sizer = wx.BoxSizer(wx.HORIZONTAL)
        radiobox_id = wx.NewId()
        self.radioBox = wx.RadioBox(choices=radiobox_choices,
              id=radiobox_id, label=radio_label, parent=self, 
              size=wx.DefaultSize,
              style=wx.RA_SPECIFY_COLS)   
              
        self.radioBox.Bind(wx.EVT_RADIOBOX, self.on_radio_click,
              id=radiobox_id)
        self.lower_right_sizer.Add(self.radioBox, 0, wx.FIXED_MINSIZE)       
        self.right_part.Add(self.lower_right_sizer, 0, wx.GROW)
        self.right_part.AddSpacer(10)
              
              
    def get_radio_selection(self):
        return self.radioBox.GetSelection()
        
        
    def on_radio_click(self, event):
        selection = self.radioBox.GetSelection()
        root = self.tree.GetRootItem()
        
        if self.tree.GetCount() > 0:
            if selection == 0:
                self.tree.DeleteAllItems()
                self.show_tree1()
                self.tree.Expand(root)
            elif selection == 1:
                self.tree.DeleteAllItems()
                self.show_tree2()
                self.tree.Expand(root)                
                