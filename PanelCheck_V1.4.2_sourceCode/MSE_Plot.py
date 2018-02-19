#!/usr/bin/env python


from Plot_Tools import *


##from IPython.Shell import IPShellEmbed
##ipshell = IPShellEmbed()

def MSE_error_check(s_data, plot_data):
    
    activeAssessorsList = plot_data.activeAssessorsList
    activeAttributesList = plot_data.activeAttributesList
    activeSamplesList = plot_data.activeSamplesList
    itemID = plot_data.tree_path 

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
    collectedActiveItemsList.extend(['General Plot'])    
    # Check wether the selected item is in the collectedActiveItemsList.
    # If not, an error message is activated.
    if itemID[0] not in collectedActiveItemsList:
        dlg = wx.MessageDialog(None, 'The assessor, attribute or sample is not active in CheckBox',
                               'Error Message',
                               wx.OK | wx.ICON_INFORMATION)
        dlg.ShowModal()
        dlg.Destroy()
        return 1

    else:
        # Calculation have requirements, test: activeSamplesList must have minimum 2 values
        if len(activeSamplesList) < 2:
            dlg = wx.MessageDialog(None, 'Minimum 2 samples needed.',
                               'Error Message',
                               wx.OK | wx.ICON_INFORMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return 1
        # Calculation have requirements, test: numberOfReplicates must be minimum 2
        if numberOfReplicates < 2:
            dlg = wx.MessageDialog(None, 'There must be a minimum of 2 replicates.',
                               'Error Message',
                               wx.OK | wx.ICON_INFORMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return 1
    return 0
    
       

def MSEPlotter_Assessor_General(s_data, plot_data, num_subplot=[1,1,1], **kwargs):
    """
    This function generates general F plots, plotting F values from the
    one-way ANOVA analsis. Each attribute has its own colour.
    
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
    @since: 02.03.2006
    """
    activeAssessorsList = plot_data.activeAssessorsList
    activeAttributesList = plot_data.activeAttributesList
    activeSamplesList = plot_data.activeSamplesList
    itemID = plot_data.tree_path 

    # Define variables that are used frequently in this function
    numberOfAssessors = len(activeAssessorsList)
    numberOfAttributes = len(activeAttributesList)
    numberOfSamples = len(activeSamplesList)
    numberOfReplicates = len(s_data.ReplicateList)
    
        
    plot_data.error = MSE_error_check(s_data, plot_data)
    
    
    if plot_data.error == 1: # has error
        return    
    elif plot_data.error == 0:    
        
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



        # Continue here if no error message
        # ---------------------------------
       
        # Figure
        replot = False; subplot = plot_data.overview_plot; scatter_width = 35
        if plot_data.fig != None: replot = True
        else: plot_data.fig = Figure(None)
        if subplot: # is subplot
            plot_data.ax = plot_data.fig.add_subplot(num_subplot[0], num_subplot[1], num_subplot[2])
            scatter_width = 15
        else: plot_data.ax = axes_create(plot_data.view_legend, plot_data.fig)
        ax = plot_data.ax; fig = plot_data.fig
        
        
        # Here starts the plotting procedure
        # ----------------------------------
        pointAndLabelList = []
        """
        """
        # Font settings
        font = {'fontname'   : 'Courier',
            'color'      : 'b',
            'fontweight' : 'bold',
            'fontsize'   : 10} 
        
        
        #axes positioning for correlation loadings plot
        ax.grid(plot_data.view_grid)
        
        
        
        # Finding the maximum F value for the selected assessors and
        # attributes, such that the maximum for Y-axis can be defined
        # further down the code
        selected_MSE_max = 0
        for ind in range(len(ANOVA_MSE)):
                MSE_value = max(ANOVA_MSE[ind])
                
                if MSE_value > selected_MSE_max:
                    selected_MSE_max = MSE_value
                
                #print selected_F_max
        
        # Here the spacing is adjusted depending on how many lines 
        # are to be plotted
        numberOfLines = numberOfAssessors * numberOfAttributes
        if numberOfLines <= 70:
            spacer = 3
        elif numberOfLines > 70 and numberOfLines <= 125:
            spacer = 4
        else:
            spacer = 5


        colors = colors_hex_list

        lines = []
        line_colors = []
        linewidths = []
        
        # x pos. of lables
        x_positions = []
        last_pos_max = 0.0
        
        # Getting F values and plotting lines in specific colors
        for ass_ind in range(len(plot_data.activeAssessorsList)):
                   
            pos_min = 0.0; pos_max = 0.0; c_index = 0
            for att_ind in range(len(plot_data.activeAttributesList)):
                
                # This calculates the position of the vertical line
                position = ((((ass_ind + 1) * spacer 
                    + ass_ind * numberOfAttributes) + 1)+ att_ind)
                
                # first pos
                if att_ind == 0:
                    pos_min = position
                
                # last pos
                if att_ind == len(ANOVA_MSE[ass_ind])-1:
                    pos_max = position
                    if ass_ind == len(ANOVA_MSE)-1:
                        last_pos_max = pos_max
      
                
                # lines[0] = ((x0, y0), (x1, y1))
                lines.append(((position, 0), (position, ANOVA_MSE[ass_ind][att_ind])))
                
                line_colors.append(colors[c_index])
                c_index += 1
                if c_index == len(colors): c_index = 0

                        
                # Creating pointAndLabelList
                label = '(' + plot_data.activeAssessorsList[ass_ind] + ', ' + plot_data.activeAttributesList[att_ind] + ')'
                pointAndLabelList.append([position, ANOVA_MSE[ass_ind][att_ind], label])
            
            x_positions.append((pos_max-pos_min)/2.0 + pos_min)
                    
        line_collection = LineCollection(lines, linewidths=1.2, colors=line_colors)
        #line_collection.set_linewidth(1.2)
        
        ax.add_collection(line_collection)
        
  
        
        # Defining the titles, axes names, etc
        myTitle = u'MSE plot: ' + itemID[0]
        min_x_scale = 0
        max_x_scale = last_pos_max + spacer + 1
        min_y_scale = 0
        max_y_scale = selected_MSE_max + selected_MSE_max * 0.1
        
        axes_setup(ax, '', 'MSE value', myTitle, [min_x_scale, max_x_scale, min_y_scale, max_y_scale])
        
        
        set_xlabeling(ax, plot_data.activeAssessorsList, font_size=10, x_positions=x_positions)
        if len(plot_data.activeAssessorsList) > 7:
            set_xlabeling_rotation(ax, 'vertical')
            
           
            
        if plot_data.view_legend:
            legend_list = []
            legend_list = activeAttributesList[:]
            plotList = []
            c_index = 0
            for att in activeAttributesList:
                p = Line2D([], [], color = colors[c_index], linewidth=1.2)
                plotList.append(p)
                c_index += 1
                if c_index == len(colors): c_index = 0
            fig.legend(plotList, legend_list, 'upper right')        
        
            
        #update plot-data variables:
        plot_data.point_lables = pointAndLabelList
        plot_data.raw_data = rawDataList
        plot_data.numeric_data = resultList
        plot_data.plot_type = "mse_ass"
        plot_data.point_lables_type = 1

        #Frame draw, for standard Matplotlib frame only use show()
        return plot_data

                    


def MSEPlotter_Assessor_Specific(s_data, plot_data, num_subplot=[1,1,1], **kwargs):
    """
    This function generates specific F plots by highlighting the selected
    attribute and plotting it in another colour than the remaining attributes.
    
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
    @since: 02.03.2006
    """
    activeAssessorsList = plot_data.activeAssessorsList
    activeAttributesList = plot_data.activeAttributesList
    activeSamplesList = plot_data.activeSamplesList
    itemID = plot_data.tree_path 

    # Define variables that are used frequently in this function
    numberOfAssessors = len(activeAssessorsList)
    numberOfAttributes = len(activeAttributesList)
    numberOfSamples = len(activeSamplesList)
    numberOfReplicates = len(s_data.ReplicateList)
    
        
    plot_data.error = MSE_error_check(s_data, plot_data)
    
    
    if plot_data.error == 1: # has error
        return    
    elif plot_data.error == 0:    
        
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



        # Continue here if no error message
        # ---------------------------------
       
        # Figure
        replot = False; subplot = plot_data.overview_plot; scatter_width = 35
        if plot_data.fig != None: replot = True
        else: plot_data.fig = Figure(None)
        if subplot: # is subplot
            plot_data.ax = plot_data.fig.add_subplot(num_subplot[0], num_subplot[1], num_subplot[2])
            scatter_width = 15
        else: plot_data.ax = axes_create(0, plot_data.fig)
        ax = plot_data.ax; fig = plot_data.fig
        
        
        # Here starts the plotting procedure
        # ----------------------------------
        pointAndLabelList = []
        """
        """
        # Font settings
        font = {'fontname'   : 'Courier',
            'color'      : 'b',
            'fontweight' : 'bold',
            'fontsize'   : 10} 
        
        
        #axes positioning for correlation loadings plot
        ax.grid(plot_data.view_grid)
        
        
        
        # Finding the maximum F value for the selected assessors and
        # attributes, such that the maximum for Y-axis can be defined
        # further down the code
        selected_MSE_max = 0
        for ind in range(len(ANOVA_MSE)):
                MSE_value = max(ANOVA_MSE[ind])
                
                if MSE_value > selected_MSE_max:
                    selected_MSE_max = MSE_value
                
                #print selected_F_max
        
        # Here the spacing is adjusted depending on how many lines 
        # are to be plotted
        numberOfLines = numberOfAssessors * numberOfAttributes
        if numberOfLines <= 70:
            spacer = 3
        elif numberOfLines > 70 and numberOfLines <= 125:
            spacer = 4
        else:
            spacer = 5



        
        
        
        lines = []
        colors = []
        linewidths = []
        
        # x pos. of lables
        x_positions = []
        last_pos_max = 0.0
        
        active_att_ind = plot_data.activeAttributesList.index(itemID[0])
        
        # Getting F values and plotting lines in specific colors
        for ass_ind in range(len(plot_data.activeAssessorsList)):
                   
            pos_min = 0.0; pos_max = 0.0
            for att_ind in range(len(plot_data.activeAttributesList)):
                
                # This calculates the position of the vertical line
                position = ((((ass_ind + 1) * spacer 
                    + ass_ind * numberOfAttributes) + 1)+ att_ind)
                
                # first pos
                if att_ind == 0:
                    pos_min = position
                
                # last pos
                if att_ind == len(ANOVA_MSE[ass_ind])-1:
                    pos_max = position
                    if ass_ind == len(ANOVA_MSE)-1:
                        last_pos_max = pos_max
      
                
                # lines[0] = [(x0, y0), (x1, y1)]
                lines.append(((position, 0), (position, ANOVA_MSE[ass_ind][att_ind])))
                
                if att_ind == active_att_ind:
                    colors.append("#00E080") # greenish
                    linewidths.append(2.4)
                else:
                    colors.append("#0000FF") # blue
                    linewidths.append(1.2)
                        
                # Creating pointAndLabelList
                label = '(' + plot_data.activeAssessorsList[ass_ind] + ', ' + plot_data.activeAttributesList[att_ind] + ')'
                pointAndLabelList.append([position, ANOVA_MSE[ass_ind][att_ind], label])
            
            x_positions.append((pos_max-pos_min)/2.0 + pos_min)
                    
        line_collection = LineCollection(lines, linewidths=linewidths, colors=colors)
        #line_collection.set_linewidth(1.2)
        
        ax.add_collection(line_collection)
        
  
        
        # Defining the titles, axes names, etc
        myTitle = u'MSE plot: ' + itemID[0]
        min_x_scale = 0
        max_x_scale = last_pos_max + spacer + 1
        min_y_scale = 0
        max_y_scale = selected_MSE_max + selected_MSE_max * 0.1
        
        axes_setup(ax, '', 'MSE value', myTitle, [min_x_scale, max_x_scale, min_y_scale, max_y_scale])
        
        
        set_xlabeling(ax, plot_data.activeAssessorsList, font_size=10, x_positions=x_positions)
        if len(plot_data.activeAssessorsList) > 7:
            set_xlabeling_rotation(ax, 'vertical')
        
            
        #update plot-data variables:
        plot_data.point_lables = pointAndLabelList
        plot_data.raw_data = rawDataList
        plot_data.numeric_data = resultList
        plot_data.plot_type = "mse_ass"
        plot_data.point_lables_type = 1

        #Frame draw, for standard Matplotlib frame only use show()
        return plot_data
    
    

def MSEPlotter_Attribute_General(s_data, plot_data, num_subplot=[1,1,1], **kwargs):
    """
    This function generates general F plots, plotting F values from the
    one-way ANOVA analsis. Each assessor has its own colour. Lines are
    sorted by attributes
    
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
    @since: 02.03.2006
    """
    activeAssessorsList = plot_data.activeAssessorsList
    activeAttributesList = plot_data.activeAttributesList
    activeSamplesList = plot_data.activeSamplesList
    itemID = plot_data.tree_path 

    # Define variables that are used frequently in this function
    numberOfAssessors = len(activeAssessorsList)
    numberOfAttributes = len(activeAttributesList)
    numberOfSamples = len(activeSamplesList)
    numberOfReplicates = len(s_data.ReplicateList)
    
        
    plot_data.error = MSE_error_check(s_data, plot_data)
    
    
    if plot_data.error == 1: # has error
        return    
    elif plot_data.error == 0:    
        
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



        # Continue here if no error message
        # ---------------------------------
       
        # Figure
        replot = False; subplot = plot_data.overview_plot; scatter_width = 35
        if plot_data.fig != None: replot = True
        else: plot_data.fig = Figure(None)
        if subplot: # is subplot
            plot_data.ax = plot_data.fig.add_subplot(num_subplot[0], num_subplot[1], num_subplot[2])
            scatter_width = 15
        else: plot_data.ax = axes_create(plot_data.view_legend, plot_data.fig)
        ax = plot_data.ax; fig = plot_data.fig
        
        
        # Here starts the plotting procedure
        # ----------------------------------
        pointAndLabelList = []
        """
        """
        # Font settings
        font = {'fontname'   : 'Courier',
            'color'      : 'b',
            'fontweight' : 'bold',
            'fontsize'   : 10} 
        
        
        #axes positioning for correlation loadings plot
        ax.grid(plot_data.view_grid)
        
        
        
        # Finding the maximum F value for the selected assessors and
        # attributes, such that the maximum for Y-axis can be defined
        # further down the code
        selected_MSE_max = 0
        for ind in range(len(ANOVA_MSE)):
                MSE_value = max(ANOVA_MSE[ind])
                
                if MSE_value > selected_MSE_max:
                    selected_MSE_max = MSE_value
                
                #print selected_F_max
        
        # Here the spacing is adjusted depending on how many lines 
        # are to be plotted
        numberOfLines = numberOfAssessors * numberOfAttributes
        if numberOfLines <= 70:
            spacer = 3
        elif numberOfLines > 70 and numberOfLines <= 125:
            spacer = 4
        else:
            spacer = 5


        colors = assign_colors(s_data.AssessorList, ["rep"])

        lines = []
        line_colors = []
        linewidths = []
        
        # x pos. of lables
        x_positions = []
        last_pos_max = 0.0
        
        # Getting F values and plotting lines in specific colors
        for att_ind in range(len(plot_data.activeAttributesList)):
                   
            pos_min = 0.0; pos_max = 0.0; c_index = 0

            for ass_ind in range(len(plot_data.activeAssessorsList)):
                
                # This calculates the position of the vertical line
                position = ((((att_ind + 1) * spacer 
                    + att_ind * numberOfAssessors) + 1)+ ass_ind)
                
                # first pos
                if ass_ind == 0:
                    pos_min = position
                
                # last pos
                if ass_ind == len(ANOVA_MSE)-1:
                    pos_max = position
                    if att_ind == len(ANOVA_MSE[ass_ind])-1:
                        last_pos_max = pos_max
      
                
                # lines[0] = [(x0, y0), (x1, y1)]
                lines.append(((position, 0), (position, ANOVA_MSE[ass_ind][att_ind])))
                
                line_colors.append(colors[(plot_data.activeAssessorsList[ass_ind], "rep")][0])
                #c_index += 1
                #if c_index == len(colors): c_index = 0

                        
                # Creating pointAndLabelList
                label = '(' + plot_data.activeAttributesList[att_ind] + ', ' + plot_data.activeAssessorsList[ass_ind] + ')'
                pointAndLabelList.append([position, ANOVA_MSE[ass_ind][att_ind], label])
            
            x_positions.append((pos_max-pos_min)/2.0 + pos_min)
                    
        line_collection = LineCollection(lines, linewidths=1.2, colors=line_colors)
        #line_collection.set_linewidth(1.2)
        
        ax.add_collection(line_collection)
        
  
        
        # Defining the titles, axes names, etc
        myTitle = u'MSE plot: ' + itemID[0]
        min_x_scale = 0
        max_x_scale = last_pos_max + spacer + 1
        min_y_scale = 0
        max_y_scale = selected_MSE_max + selected_MSE_max * 0.1
        
        axes_setup(ax, '', 'MSE value', myTitle, [min_x_scale, max_x_scale, min_y_scale, max_y_scale])
        
        
        set_xlabeling(ax, plot_data.activeAttributesList, font_size=10, x_positions=x_positions)
        if len(plot_data.activeAttributesList) > 7:
            set_xlabeling_rotation(ax, 'vertical')
            
           
            
        if plot_data.view_legend:
            legend_list = []
            legend_list = activeAssessorsList[:]
            plotList = []
            #c_index = 0
            for ass in activeAssessorsList:
                p = Line2D([], [], color = colors[(ass, "rep")][0], linewidth=1.2)
                plotList.append(p)
                #c_index += 1
                #if c_index == len(colors): c_index = 0
            fig.legend(plotList, legend_list, 'upper right')        
        
            
        #update plot-data variables:
        plot_data.point_lables = pointAndLabelList
        plot_data.raw_data = rawDataList
        plot_data.numeric_data = resultList
        plot_data.plot_type = "mse_att"
        plot_data.point_lables_type = 1

        #Frame draw, for standard Matplotlib frame only use show()
        return plot_data




def MSEPlotter_Attribute_Specific(s_data, plot_data, num_subplot=[1,1,1], **kwargs):
    """
    This function generates general F plots, plotting F values from the
    one-way ANOVA analsis. Each assessor has its own colour. Lines are
    sorted by attributes
    
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
    @since: 02.03.2006
    """
    activeAssessorsList = plot_data.activeAssessorsList
    activeAttributesList = plot_data.activeAttributesList
    activeSamplesList = plot_data.activeSamplesList
    itemID = plot_data.tree_path 

    # Define variables that are used frequently in this function
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
    collectedActiveItemsList.extend(['General Plot'])
    #print collectedActiveItemsList
    #print
    
    plot_data.error = MSE_error_check(s_data, plot_data)
    
    
    if plot_data.error == 1: # has error
        return    
    elif plot_data.error == 0:    
        
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



        # Continue here if no error message
        # ---------------------------------
       
        # Figure
        replot = False; subplot = plot_data.overview_plot; scatter_width = 35
        if plot_data.fig != None: replot = True
        else: plot_data.fig = Figure(None)
        if subplot: # is subplot
            plot_data.ax = plot_data.fig.add_subplot(num_subplot[0], num_subplot[1], num_subplot[2])
            scatter_width = 15
        else: plot_data.ax = axes_create(0, plot_data.fig)
        ax = plot_data.ax; fig = plot_data.fig
        
        
        # Here starts the plotting procedure
        # ----------------------------------
        pointAndLabelList = []
        """
        """
        # Font settings
        font = {'fontname'   : 'Courier',
            'color'      : 'b',
            'fontweight' : 'bold',
            'fontsize'   : 10} 
        
        
        #axes positioning for correlation loadings plot
        ax.grid(plot_data.view_grid)
        
        
        
        # Finding the maximum F value for the selected assessors and
        # attributes, such that the maximum for Y-axis can be defined
        # further down the code
        selected_MSE_max = 0
        for ind in range(len(ANOVA_MSE)):
                MSE_value = max(ANOVA_MSE[ind])
                
                if MSE_value > selected_MSE_max:
                    selected_MSE_max = MSE_value
                
                #print selected_F_max
        
        # Here the spacing is adjusted depending on how many lines 
        # are to be plotted
        numberOfLines = numberOfAssessors * numberOfAttributes
        if numberOfLines <= 70:
            spacer = 3
        elif numberOfLines > 70 and numberOfLines <= 125:
            spacer = 4
        else:
            spacer = 5

        lines = []
        colors = []
        linewidths = []
        
        # x pos. of lables
        x_positions = []
        last_pos_max = 0.0
        
        active_ass_ind = plot_data.activeAssessorsList.index(itemID[0])
        
        # Getting F values and plotting lines in specific colors
        for att_ind in range(len(plot_data.activeAttributesList)):
                   
            pos_min = 0.0; pos_max = 0.0

            for ass_ind in range(len(plot_data.activeAssessorsList)):
                
                # This calculates the position of the vertical line
                position = ((((att_ind + 1) * spacer 
                    + att_ind * numberOfAssessors) + 1)+ ass_ind)
                
                # first pos
                if ass_ind == 0:
                    pos_min = position
                
                # last pos
                if ass_ind == len(ANOVA_MSE)-1:
                    pos_max = position
                    if att_ind == len(ANOVA_MSE[ass_ind])-1:
                        last_pos_max = pos_max
      
                
                # lines[0] = [(x0, y0), (x1, y1)]
                lines.append(((position, 0), (position, ANOVA_MSE[ass_ind][att_ind])))

                if ass_ind == active_ass_ind:
                    colors.append("#00E080") # greenish
                    linewidths.append(2.4)
                else:
                    colors.append("#0000FF") # blue
                    linewidths.append(1.2)

                        
                # Creating pointAndLabelList
                label = '(' + plot_data.activeAttributesList[att_ind] + ', ' + plot_data.activeAssessorsList[ass_ind] + ')'
                pointAndLabelList.append([position, ANOVA_MSE[ass_ind][att_ind], label])
            
            x_positions.append((pos_max-pos_min)/2.0 + pos_min)
                    
        line_collection = LineCollection(lines, linewidths=linewidths, colors=colors)
        #line_collection.set_linewidth(1.2)
        
        ax.add_collection(line_collection)
        
  
        
        # Defining the titles, axes names, etc
        myTitle = u'MSE plot: ' + itemID[0]
        min_x_scale = 0
        max_x_scale = last_pos_max + spacer + 1
        min_y_scale = 0
        max_y_scale = selected_MSE_max + selected_MSE_max * 0.1
        
        axes_setup(ax, '', 'MSE value', myTitle, [min_x_scale, max_x_scale, min_y_scale, max_y_scale])
        
        
        set_xlabeling(ax, plot_data.activeAttributesList, font_size=10, x_positions=x_positions)
        if len(plot_data.activeAttributesList) > 7:
            set_xlabeling_rotation(ax, 'vertical')
            
            
        #update plot-data variables:
        plot_data.point_lables = pointAndLabelList
        plot_data.raw_data = rawDataList
        plot_data.numeric_data = resultList
        plot_data.plot_type = "mse_att"
        plot_data.point_lables_type = 1

        #Frame draw, for standard Matplotlib frame only use show()
        return plot_data