#!/usr/bin/env python


from Plot_Tools import *


def pmsePlotter(s_data, plot_data, num_subplot=[1,1,1], **kwargs):
    """
    This function generates the Tucker-1 plots, both Common Score Plot,
    Correlation Loadings focused on assessor and Correlation Loadings focused
    on attributes.
    
    @type drawSettings:     list
    @param drawSettings:    List of settings on how to draw the figure. [grid?, legend?, legend_position, x_y_Limits]
        
    @type sparseMatrix:     dictionary
    @param sparseMatrix:    Complete dictionary type of Matrix with all values
    
    @type ActiveAssessors:  dictionary
    @param ActiveAssessors: Contains the active/checked assessors
    
    @type ActiveAttributes:  dictionary
    @param ActiveAttributes: Contains the active/checked attributes
    
    @type ActiveSamples:    dictionary
    @param ActiveSamples:   Contains the active/checked samples
    
    @type noOfWindows:      integer
    @param noOfWindows:     nteger value for the new window
    
    @type insideItemID:     pyData
    @param insideItemID:    pyData from wxTree
    
    @type assessorList:     list
    @param assessorList:    Complete list of ALL assessors
    
    @type sampleList:     list
    @param sampleList:    Complete list of ALL samples
    
    @type replicateList:    list
    @param replicateList:   Complete list of ALL replicates
    
    @type attributeList:    list
    @param attributeList:   Complete list of ALL attributes
    
    
    @author: Oliver Tomic
    @organization: Matforsk - Norwegian Food Research Institute
    @version: 1.0
    @since: 01.07.2005
    """
    activeAssessorsList = plot_data.activeAssessorsList
    activeAttributesList = plot_data.activeAttributesList
    activeSamplesList = plot_data.activeSamplesList
    itemID = plot_data.tree_path    
    
    # Construction of Tucker1-matrix, where assessor matrices are 
    # put beside each other starting with assessor1, then assessor 2
    # and so on
    numberOfAssessors = len(activeAssessorsList)
    numberOfAttributes = len(activeAttributesList)
    numberOfSamples = len(activeSamplesList)
    numberOfReplicates = len(s_data.ReplicateList)
    
   
    
    # Constructs a list that contains all active assessors AND attributes AND
    # 'Common Scores'.
    # This is necessary for easier check whether double clicked item
    # can be plotted or a error message must be shown.
    collectedActiveItemsList = activeAssessorsList[:]
    collectedActiveItemsList.extend(activeAttributesList[:])
    collectedActiveItemsList.extend(activeSamplesList[:])
    #print collectedActiveItemsList
    #print
    
    # Check wether the selected item is in the collectedActiveItemsList.
    # If not, an error message is activated.
    if itemID[0] not in collectedActiveItemsList:
        dlg = wx.MessageDialog(None, 'The assessor, attribute or sample is not active in CheckBox',
                               'Error Message',
                               wx.OK | wx.ICON_INFORMATION)
        dlg.ShowModal()
        dlg.Destroy()
        return

    else:
        # Calculation have requirements, test: activeSamplesList must have minimum 2 values
        if len(activeSamplesList) < 2:
            dlg = wx.MessageDialog(None, 'Minimum 2 samples needed.',
                               'Error Message',
                               wx.OK | wx.ICON_INFORMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        # Calculation have requirements, test: numberOfReplicates must be minimum 2
        if numberOfReplicates < 2:
            dlg = wx.MessageDialog(None, 'There must be a minimum of 2 replicates.',
                               'Error Message',
                               wx.OK | wx.ICON_INFORMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        # Calculation have requirements, test: numberOfReplicates must be minimum 2
        if numberOfAssessors < 2:
            dlg = wx.MessageDialog(None, 'There must be a minimum of 2 assessors.',
                               'Error Message',
                               wx.OK | wx.ICON_INFORMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        
        
        # Continue here if no error message
        # ---------------------------------  
        
        colors = colors_hex_list; colored_lim = 8
        
        
        view_legend = False
        if itemID[0] in activeAttributesList:
            view_legend = plot_data.view_legend
        elif itemID[0] in activeAssessorsList:
            if len(activeAttributesList) <= colored_lim and len(activeAttributesList) <= len(colors):
                view_legend = plot_data.view_legend
        
        plot_data.view_legend = view_legend
        

        
        
        # Figure
        replot = False; subplot = plot_data.overview_plot; scatter_width = 60
        if plot_data.fig != None: replot = True
        else: plot_data.fig = Figure(None)
        if subplot: # is subplot
            plot_data.ax = plot_data.fig.add_subplot(num_subplot[0], num_subplot[1], num_subplot[2])
            scatter_width = 30
        else:
            plot_data.ax = axes_create(view_legend, plot_data.fig)
        ax = plot_data.ax; fig = plot_data.fig         
        
        
        
        if plot_data.ANOVA_F == None or plot_data.ANOVA_p == None or plot_data.ANOVA_MSE == None or plot_data.F_signifcances == None: 
            # Calculation of all p- and MSE values        
            ANOVA_F, ANOVA_p, ANOVA_MSE, F_signifcances = ANOVA(s_data, plot_data)
            plot_data.ANOVA_F = ANOVA_F
            plot_data.ANOVA_p = ANOVA_p
            plot_data.ANOVA_MSE = ANOVA_MSE
            plot_data.F_signifcances = F_signifcances
            
            # Starting generation of the list that contains the raw data
            # that is shown in "Raw Data" when pushing the button in the plot            
            rawDataList = raw_data_grid(s_data, plot_data)
            resultList = numerical_data_grid(s_data, plot_data, ANOVA_F, ANOVA_p, ANOVA_MSE, F_signifcances)
        else:
            ANOVA_F = plot_data.ANOVA_F
            ANOVA_p = plot_data.ANOVA_p
            ANOVA_MSE = plot_data.ANOVA_MSE
            F_signifcances = plot_data.F_signifcances
            
            
            rawDataList = plot_data.raw_data
            resultList = plot_data.numeric_data
        
 
 
        pointAndLabelList = []
        secondaryPointsAndLabels = []
 
        # Finding the maximum F value for the selected assessors and
        # attributes, such that the maximum for Y-axis can be defined
        # further down the code
        
        # Create the coordinates for the pMSE plot from the postANOVA dictionary
        # x: MSE value; y: p value
        # This plots the values for all assessors 
        x_values = []
        y_values = []
        max_MSE = 0; max_p = 0;
        for ass_ind in range(len(ANOVA_MSE)):
            for att_ind in range(len(ANOVA_MSE[0])):
                
                MSE_value = ANOVA_MSE[ass_ind][att_ind];  p_value = ANOVA_p[ass_ind][att_ind]
                if isinstance(MSE_value, (int , float)) and isinstance(p_value, (int , float)):    
                    # find max values
                    if MSE_value > max_MSE:
                        max_MSE = MSE_value
                    if p_value > max_p:
                        max_p = p_value
                    
                    # set scatter values:
                    x_values.append(MSE_value)
                    y_values.append(p_value)  
                    
                    assessor = activeAssessorsList[ass_ind]
                    attribute = activeAttributesList[att_ind]
                    label = '(' + assessor + ', ' + attribute + ')'
                    
                    # set point and lables:
                    if assessor == itemID[0] or attribute == itemID[0]:
                        pointAndLabelList.append([MSE_value, p_value, label, ass_ind, att_ind])
                    else:
                        secondaryPointsAndLabels.append([MSE_value, p_value, label, ass_ind, att_ind])              

        #extending pointAndLabelList so it contains all the values
        pointAndLabelList.extend(secondaryPointsAndLabels)                     

        
        

        
        # Here starts the plotting procedure
        # ----------------------------------

        ax.grid(plot_data.view_grid)
        
        
        
        # Font settings
        font = {'fontname'   : 'Courier',
            'color'      : 'b',
            'fontweight' : 'bold',
            'fontsize'   : 10}       
        
        colors = assign_colors(s_data.AssessorList, ["rep"])
        
        
        #ax.plot(x_values, y_values, 'bo')
        ax.scatter(x_values, y_values, s=15, c='w', marker='o')
        
        
        # Highlight the selected assessor/attribute
        
        _colors = []
        
        # If an attribute is selected:
        if itemID[0] in activeAttributesList:
            
            frame_colored = colored_frame(s_data, plot_data, activeAttributesList, itemID[0])
            
            active_att_ind = activeAttributesList.index(itemID[0])
            
            spec_x_values = []
            spec_y_values = []
           
            c_index = 0
            for ass_ind in range(len(activeAssessorsList)):
                if isinstance(ANOVA_p[ass_ind][active_att_ind], (int , float)): # if p value is not '*'
                    spec_x_values.append(ANOVA_MSE[ass_ind][active_att_ind])
                    spec_y_values.append(ANOVA_p[ass_ind][active_att_ind])
                    _colors.append(colors[(activeAssessorsList[ass_ind], "rep")][0])
                #c_index += 1
                #if c_index == len(colors): c_index = 0
            
            #print spec_x_values
            if len(activeAssessorsList) <= colored_lim and len(activeAssessorsList) <= len(colors):
                for i in range(len(spec_x_values)):
                    ax.scatter([spec_x_values[i]], [spec_y_values[i]], s = scatter_width, color = _colors[i], marker = 's')
            else:
                ax.scatter(spec_x_values, spec_y_values, s = scatter_width, color = '#FF0000', marker = 's')
            #myTitle = 'p*MSE plot: Attribute ' + itemID[0]
        
        # If an assessor is selected:
        elif itemID[0] in activeAssessorsList:
            colors = assign_colors(s_data.AttributeList, ["rep"])
            active_ass_ind = activeAssessorsList.index(itemID[0])
        
            spec_x_values = []
            spec_y_values = []
            
            c_index = 0            
            for att_ind in range(len(activeAttributesList)):
                if isinstance(ANOVA_p[active_ass_ind][att_ind], (int , float)): # if p value is not '*'
                    spec_x_values.append(ANOVA_MSE[active_ass_ind][att_ind])
                    spec_y_values.append(ANOVA_p[active_ass_ind][att_ind])
                    _colors.append(colors[(activeAttributesList[att_ind], "rep")][0])
                #c_index += 1
                #if c_index == len(colors): c_index = 0
                
            if len(activeAttributesList) <= colored_lim and len(activeAttributesList) <= len(colors):
                for i in range(len(spec_x_values)):
                    ax.scatter([spec_x_values[i]], [spec_y_values[i]], s = scatter_width, color = _colors[i], marker = 's')
            else:
                ax.scatter(spec_x_values, spec_y_values, s = scatter_width, color = '#0033FF', marker = 's')
        
        
        # Defining the titles, axes names, etc
        myTitle = 'p*MSE plot: ' + itemID[0]
        min_x_scale = - max_MSE * 0.01
        max_x_scale = max_MSE + 0.1 * max_MSE
        min_y_scale = - max_p * 0.01
        max_y_scale = 1.05 # This was used before: max_p + 0.05 * max_p
        if subplot:
            axes_setup(ax, '', '', myTitle, [min_x_scale, max_x_scale, min_y_scale, max_y_scale], font_size=10)
        else:
            axes_setup(ax, 'MSE', 'p value', myTitle, [min_x_scale, max_x_scale, min_y_scale, max_y_scale])
        
        
        if plot_data.view_legend:
            if itemID[0] in activeAttributesList:
                if len(activeAssessorsList) <= colored_lim and len(activeAssessorsList) <= len(colors):
                    plotList = []; c_index = 0
                    for ass in activeAssessorsList:
                        #plotList.append(Patch(facecolor = colors[c_index]))
                        #plotList.append(Rectangle(xy=(0,0), width=1, height=1, facecolor=colors[c_index]))
                        plotList.append(Line2D([],[], color = colors[(ass, "rep")][0], linewidth=5))
                        #c_index += 1
                        
                    fig.legend(plotList, activeAssessorsList, 'upper right')
                    if frame_colored:
                        significance_legend(plot_data, pos='lower right')
                else:
                    if frame_colored:
                        significance_legend(plot_data, pos='upper right')
                
                    
            elif itemID[0] in activeAssessorsList:
                colors = assign_colors(s_data.AttributeList, ["rep"])
                
                if len(activeAttributesList) <= colored_lim and len(activeAttributesList) <= len(colors):
                    plotList = []; c_index = 0
                    for attribute in activeAttributesList:
                        #plotList.append(Patch(facecolor = colors[c_index]))
                        #plotList.append(Rectangle(xy=(0,0), width=1, height=1, facecolor=colors[c_index]))
                        plotList.append(Line2D([],[], color = colors[(attribute, "rep")][0], linewidth=5))
                        c_index += 1   
                        if c_index >= len(activeAssessorsList): c_index = 0
                    fig.legend(plotList, activeAttributesList, 'upper right')
                    
                    
                    
  
        
        #update plot-data variables:
        plot_data.point_lables = pointAndLabelList
        plot_data.raw_data = rawDataList
        plot_data.numeric_data = resultList
        plot_data.plot_type = "pmse"
        plot_data.point_lables_type = 0

        #Frame draw, for standard Matplotlib frame only use show()
        return plot_data




def pmse_OverviewPlotter(s_data, plot_data, **kwargs):
    """
    Overview Plot
    """
    
    itemID_list = []
    if plot_data.tree_path == ["Overview Plot (assessors)"]:
        for ass in plot_data.activeAssessorsList:
            itemID_list.append([ass])
        rotation_list = plot_data.activeAssessorsList[:]
    elif plot_data.tree_path == ["Overview Plot (attributes)"]:
        for att in plot_data.activeAttributesList:
            itemID_list.append([att])
        rotation_list = plot_data.activeAttributesList[:]
    return OverviewPlotter(s_data, plot_data, itemID_list, pmsePlotter, rotation_list)

    
    
    
    
    
    
