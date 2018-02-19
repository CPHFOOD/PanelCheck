#!/usr/bin/env python

from Plot_Tools import *


##from IPython.Shell import IPShellEmbed
##ipshell = IPShellEmbed()


def FPlotter_Assessor_General(s_data, plot_data, num_subplot=[1,1,1], **kwargs):
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
    print itemID
    
    # Constructs a list that contains all active assessors AND attributes AND
    # 'Common Scores'.
    # This is necessary for easier check whether double clicked item
    # can be plotted or a error message must be shown.
    collectedActiveItemsList = activeAssessorsList[:]
    collectedActiveItemsList.extend(activeAttributesList[:])
    collectedActiveItemsList.extend(activeSamplesList[:])
    collectedActiveItemsList.extend(['General Plot'])
    #print collectedActiveItemsList
    #print itemID[1]
    #print collectedActiveItemsList
    # Check wether the selected item is in the collectedActiveItemsList.
    # If not, an error message is activated.
    if itemID[1] not in collectedActiveItemsList:
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
        
        
        
        # Here starts the plotting procedure
        # ----------------------------------
        # Figure
        replot = False; subplot = plot_data.overview_plot
        if plot_data.fig != None: replot = True
        else: plot_data.fig = Figure(None)
        if subplot: # is subplot
            plot_data.ax = plot_data.fig.add_subplot(num_subplot[0], num_subplot[1], num_subplot[2])
        else: plot_data.ax = axes_create(plot_data.view_legend, plot_data.fig)
        ax = plot_data.ax; fig = plot_data.fig          
        
        # Font settings
        font = {'fontname'   : 'Courier',
            'color'      : 'b',
            'fontweight' : 'bold',
            'fontsize'   : 10} 
        
        print "FPlotter_Assessor_General"
        
        #axes positioning for correlation loadings plot
        ax.grid(plot_data.view_grid)
        
 
        colors = assign_colors(s_data.AttributeList, ["rep"])
        
        # If 'Legend' is activated by user
        #if plot_data.view_legend:
        #    plotList = []
        #    for attribute in activeAttributesList:
        #        p = Patch(facecolor = extendedColorChoices[activeAttributesList.index(attribute)])
        #        plotList.append(p)
        #    fig.legend(plotList, activeAttributesList, 'upper right', handlelen = 0.015)
            #figlegend(plotList, activeAssessorsList, drawSettings[2])
            
        
        
        # Finding the maximum F value for the selected assessors and
        # attributes, such that the maximum for Y-axis can be defined
        # further down the code
        max_F = 0; max_p = 0;
        for ass_ind in range(len(ANOVA_F)):
            for att_ind in range(len(ANOVA_F[0])):
                
                F_value = ANOVA_F[ass_ind][att_ind];  p_value = ANOVA_p[ass_ind][att_ind]
                if isinstance(F_value, (int , float)) and isinstance(p_value, (int , float)):    
                    # find max values
                    if F_value > max_F:
                        max_F = F_value
                    if p_value > max_p:
                        max_p = p_value

        
        # Here the spacing is adjusted depending on how many lines 
        # are to be plotted
        numberOfLines = numberOfAssessors * numberOfAttributes
        if numberOfLines <= 70:
            spacer = 3
        elif numberOfLines > 70 and numberOfLines <= 125:
            spacer = 4
        else:
            spacer = 5
        
        
        
        if itemID[0] == "F-values": 
            outputANOVA = ANOVA_F
        else: 
            outputANOVA = ANOVA_p
        

        pointAndLabelList = []
        
        
        lines = []
        line_colors = []
        linewidths = []
        
        # x pos. of lables
        x_positions = []
        last_pos_max = 0.0
        
        for ass_ind in range(len(activeAssessorsList)):
        
            assessor = activeAssessorsList[ass_ind]
            #attributeValues = []
            pos_min = 0.0; pos_max = 0.0; c_index = 0
            
            for att_ind in range(len(activeAttributesList)):
            
                
                value = outputANOVA[ass_ind][att_ind]
                #attributeValues.append(value)
                if value == '*':
                    value = 0
                
                
                # This calculates the position of the vertical line
                position = ((((ass_ind + 1) * spacer 
                    + ass_ind * numberOfAttributes) + 1)+ att_ind)
                #print position
                
                # first pos
                if att_ind == 0:
                    pos_min = position
                
                # last pos
                if att_ind == len(outputANOVA[ass_ind])-1:
                    pos_max = position
                    if ass_ind == len(outputANOVA)-1:
                        last_pos_max = pos_max
                
                
                if value <= 0.000001:
                    continue
                
                attribute = activeAttributesList[att_ind]
                
                # lines[0] = [(x0, y0), (x1, y1)]
                lines.append(((position, 0), (position, value)))
                
                c = colors[(attribute, "rep")][0]
                line_colors.append(colors[(attribute, "rep")][0])                             
                
                # Creating pointAndLabelList
                label = '(' + assessor + ', ' + attribute + ')'
                
                print (label, c, position, value)
                
                pointAndLabelList.append([position, value, label])
           
            x_positions.append((pos_max-pos_min)/2.0 + pos_min)
                    
        line_collection = LineCollection(lines, colors=line_colors)
        line_collection.set_linewidth(1.2)
        
        ax.add_collection(line_collection)            



        # Defining the titles, axes names, etc
        min_x_scale = 0
        max_x_scale = last_pos_max + spacer + 1
        min_y_scale = 0
        max_y_scale = max_F + max_F * 0.1



        print F_signifcances
        
        # Plotting the horizontal lines for the F values at 
        # 5% and 1% significance level
        lines2 = []; line_colors2 = []
        if itemID[0] == "F-values":
            lines2.append(((0, F_signifcances[0]), (max_x_scale, F_signifcances[0])))
            line_colors2.append("#ff0000")
            lines2.append(((0, F_signifcances[1]), (max_x_scale, F_signifcances[1])))
            line_colors2.append("#000000")
        elif itemID[0] == "p-values":             
            lines2.append(((0, 0.01), (max_x_scale, 0.01)))
            line_colors2.append("#ff0000")
            lines2.append(((0, 0.05), (max_x_scale, 0.05)))            
            line_colors2.append("#000000")        

        line_collection2 = LineCollection(lines2, colors=line_colors2)
        line_collection2.set_linewidth(1.0)
        ax.add_collection(line_collection2) 

        if itemID[0] == "F-values": 
            _ylabel = "F value"
            myTitle = u'F plot: sorted by assessors'
            ymax = max_F
        else:
            _ylabel = "p value"
            myTitle = u'p plot: sorted by assessors'
            ymax = max_p
        ymax += ymax*0.1 # plus 10%

        
        axes_setup(ax, '', _ylabel, myTitle, [min_x_scale, max_x_scale, 0, ymax])
        
        set_xlabeling(ax, plot_data.activeAssessorsList, font_size=10, x_positions=x_positions)
        if len(plot_data.activeAssessorsList) > 7:
            set_xlabeling_rotation(ax, 'vertical')
        


        # If 'Legend' is activated by user
        if plot_data.view_legend:
            legend_list = []
            legend_list = activeAttributesList[:]
            #alpha_char = u"\u03b1"
            legend_list.append('')
            legend_list.append("sign. level: 1%") # "+alpha_char +"=1%")
            legend_list.append("sign. level: 5%") #"+alpha_char +"=5%")
            plotList = []
            c_index = 0
                
            for att in activeAttributesList:
                p = Line2D([], [], color = colors[(att, "rep")][0], linewidth=1.2)
                plotList.append(p)               
                
            plotList.append(None)
            plotList.append(Line2D([],[], color = "#ff0000", linewidth=1.0))
            plotList.append(Line2D([],[], color = "#000000", linewidth=1.0))
            fig.legend(plotList, legend_list, 'upper right')
            #figlegend(plotList, activeAssessorsList, drawSettings[2])

            
        #update plot-data variables:
        plot_data.point_lables = pointAndLabelList
        plot_data.raw_data = rawDataList
        plot_data.numeric_data = resultList
        plot_data.plot_type = "f_ass"
        plot_data.point_lables_type = 1

        #Frame draw, for standard Matplotlib frame only use show()
        return plot_data



def FPlotter_Assessor_Specific(s_data, plot_data, num_subplot=[1,1,1], **kwargs):
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
    
    
    # Constructs a list that contains all active assessors AND attributes AND
    # 'Common Scores'.
    # This is necessary for easier check whether double clicked item
    # can be plotted or a error message must be shown.
    collectedActiveItemsList = activeAssessorsList[:]
    collectedActiveItemsList.extend(activeAttributesList)
    collectedActiveItemsList.extend(activeSamplesList)
    collectedActiveItemsList.extend(['General Plot'])
    #print collectedActiveItemsList
    #print
    
    # Check wether the selected item is in the collectedActiveItemsList.
    # If not, an error message is activated.
    if itemID[1] not in collectedActiveItemsList:
        dlg = wx.MessageDialog(None, 'The assessor, attribute or sample is not active in CheckBox',
                               'Error Message',
                               wx.OK | wx.ICON_INFORMATION)
        dlg.ShowModal()
        dlg.Destroy()

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
        
        
        
        print "FPlotter_Assessor_Specific"
        
        
        # Here starts the plotting procedure
        # ----------------------------------
        # Figure
        replot = False; subplot = plot_data.overview_plot
        if plot_data.fig != None: replot = True
        else: plot_data.fig = Figure(None)
        if subplot: # is subplot
            plot_data.ax = plot_data.fig.add_subplot(num_subplot[0], num_subplot[1], num_subplot[2])
        else: plot_data.ax = axes_create(plot_data.view_legend, plot_data.fig)
        ax = plot_data.ax; fig = plot_data.fig 
        
        
        # Font settings
        font = {'fontname'   : 'Courier',
            'color'      : 'b',
            'fontweight' : 'bold',
            'fontsize'   : 10} 
        
        
        #axes positioning for correlation loadings plot
        ax.grid(plot_data.view_grid)
        
        
        # Create a list with colour choices that are then used for the
        # vertical lines in the plot
        colorChoices = ['r','g','c','m','y','k','b','#666666','#00FF00',
                        '#00FFFF','#999999','#993333','#CCCCFF',
                        '#FF3300','#00FFCC']
        extendedColorChoices = ['r','g','c','m','y','k','b','#666666','#00FF00',
                        '#00FFFF','#999999','#993333','#CCCCFF',
                        '#FF3300','#00FFCC']
        extendedColorChoices.extend(colorChoices)
        
        
        # Finding the maximum F value for the selected assessors and
        # attributes, such that the maximum for Y-axis can be defined
        # further down the code
        max_F = 0; max_p = 0;
        for ass_ind in range(len(ANOVA_F)):
            for att_ind in range(len(ANOVA_F[0])):
                
                F_value = ANOVA_F[ass_ind][att_ind]
                p_value = ANOVA_p[ass_ind][att_ind]
                if isinstance(F_value, (int , float)) and isinstance(p_value, (int , float)):    
                    # find max values
                    if F_value > max_F:
                        max_F = F_value
                    if p_value > max_p:
                        max_p = p_value

        
        # Here the spacing is adjusted depending on how many lines 
        # are to be plotted
        numberOfLines = numberOfAssessors * numberOfAttributes
        if numberOfLines <= 70:
            spacer = 3
        elif numberOfLines > 70 and numberOfLines <= 125:
            spacer = 4
        else:
            spacer = 5
        
        
        
        if itemID[0] == "F-values": 
            outputANOVA = ANOVA_F
        else: 
            outputANOVA = ANOVA_p
        

        pointAndLabelList = []
        
        
        lines = []
        line_colors = []
        linewidths = []
        
        # x pos. of lables
        x_positions = []
        last_pos_max = 0.0
        
        active_att_ind = plot_data.activeAttributesList.index(itemID[1])
        
        for ass_ind in range(len(activeAssessorsList)):
        
            assessor = activeAssessorsList[ass_ind]
            #attributeValues = []
            pos_min = 0.0; pos_max = 0.0; c_index = 0
            
            for att_ind in range(len(activeAttributesList)):
            
                
                value = outputANOVA[ass_ind][att_ind]
                #attributeValues.append(value)
                if value == '*':
                    value = 0
                
                # This calculates the position of the vertical line
                position = ((((ass_ind + 1) * spacer 
                    + ass_ind * numberOfAttributes) + 1)+ att_ind)
                #print position
                
                # first pos
                if att_ind == 0:
                    pos_min = position
                
                # last pos
                if att_ind == len(outputANOVA[ass_ind])-1:
                    pos_max = position
                    if ass_ind == len(outputANOVA)-1:
                        last_pos_max = pos_max
                        
                
                if value <= 0.000001:
                    continue                    
                
                # lines[0] = [(x0, y0), (x1, y1)]
                lines.append(((position, 0), (position, value)))
                
                if att_ind == active_att_ind:
                    line_colors.append("#00E080") # greenish
                    linewidths.append(2.4)
                else:
                    line_colors.append("#0000FF") # blue
                    linewidths.append(1.2)                 
                
                
                
                attribute = activeAttributesList[att_ind]
                
                
                # Creating pointAndLabelList
                label = '(' + assessor + ', ' + attribute + ')'
                pointAndLabelList.append([position, value, label])
                print label
           
            x_positions.append((pos_max-pos_min)/2.0 + pos_min)
                    
        line_collection = LineCollection(lines, colors=line_colors, linewidths=linewidths)
        ax.add_collection(line_collection)            



        # Defining the titles, axes names, etc
        min_x_scale = 0
        max_x_scale = last_pos_max + spacer + 1
        min_y_scale = 0
        max_y_scale = max_F + max_F * 0.1



        
        # Plotting the horizontal lines for the F values at 
        # 5% and 1% significance level
        lines2 = []; line_colors2 = []
        if itemID[0] == "F-values":
            lines2.append(((0, F_signifcances[0]), (max_x_scale, F_signifcances[0])))
            line_colors2.append("#ff0000")
            lines2.append(((0, F_signifcances[1]), (max_x_scale, F_signifcances[1])))
            line_colors2.append("#000000")
        elif itemID[0] == "p-values":             
            lines2.append(((0, 0.01), (max_x_scale, 0.01)))
            line_colors2.append("#ff0000")
            lines2.append(((0, 0.05), (max_x_scale, 0.05)))            
            line_colors2.append("#000000")        

        line_collection2 = LineCollection(lines2, colors=line_colors2)
        line_collection2.set_linewidth(1.0)
        ax.add_collection(line_collection2) 

        if itemID[0] == "F-values": 
            _ylabel = "F value"
            myTitle = u'F plot: ' + itemID[1]
            ymax = max_F
        else:
            _ylabel = "p value"
            myTitle = u'p plot: ' + itemID[1]
            ymax = max_p
        ymax += ymax*0.1 # plus 10%

        
        axes_setup(ax, '', _ylabel, myTitle, [min_x_scale, max_x_scale, 0, ymax])
        
        set_xlabeling(ax, plot_data.activeAssessorsList, font_size=10, x_positions=x_positions)
        if len(plot_data.activeAssessorsList) > 7:
            set_xlabeling_rotation(ax, 'vertical')
        

        if plot_data.view_legend:
            #alpha_char = u"\u03b1"
            legend_list = []
            legend_list.append('')
            legend_list.append("sign. level: 1%") # "+alpha_char +"=1%")
            legend_list.append("sign. level: 5%") #"+alpha_char +"=5%")
            legend_list.append('')
            plotList = []
            plotList.append(None)
            plotList.append(Line2D([],[], color = "#ff0000", linewidth=1.1))
            plotList.append(Line2D([],[], color = "#000000", linewidth=1.1))
            plotList.append(None)
            fig.legend(plotList, legend_list, 'upper right') 

            
        #update plot-data variables:
        plot_data.point_lables = pointAndLabelList
        plot_data.raw_data = rawDataList
        plot_data.numeric_data = resultList
        plot_data.plot_type = "f_ass"
        plot_data.point_lables_type = 1

        #Frame draw, for standard Matplotlib frame only use show()
        return plot_data

    

def FPlotter_Attribute_General(s_data, plot_data, num_subplot=[1,1,1], **kwargs):
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
    collectedActiveItemsList.extend(activeAttributesList)
    collectedActiveItemsList.extend(activeSamplesList)
    collectedActiveItemsList.extend(['General Plot'])
    #print collectedActiveItemsList
    #print
    
    # Check wether the selected item is in the collectedActiveItemsList.
    # If not, an error message is activated.
    if itemID[1] not in collectedActiveItemsList:
        dlg = wx.MessageDialog(None, 'The assessor, attribute or sample is not active in CheckBox',
                               'Error Message',
                               wx.OK | wx.ICON_INFORMATION)
        dlg.ShowModal()
        dlg.Destroy()

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
        
     
        print "FPlotter_Attribute_General"
          
        
        # Here starts the plotting procedure
        # ----------------------------------
        # Figure
        replot = False; subplot = plot_data.overview_plot
        if plot_data.fig != None: replot = True
        else: plot_data.fig = Figure(None)
        if subplot: # is subplot
            plot_data.ax = plot_data.fig.add_subplot(num_subplot[0], num_subplot[1], num_subplot[2])
        else: plot_data.ax = axes_create(plot_data.view_legend, plot_data.fig)
        ax = plot_data.ax; fig = plot_data.fig          
        
        # Font settings
        font = {'fontname'   : 'Courier',
            'color'      : 'b',
            'fontweight' : 'bold',
            'fontsize'   : 10} 
        
        
        #axes positioning for correlation loadings plot
        ax.grid(plot_data.view_grid)
        
        
        # Create a list with colour choices that are then used for the
        # vertical lines in the plot
        colorChoices = ['r','g','c','m','y','k','b','#666666','#00FF00',
                        '#00FFFF','#999999','#993333','#CCCCFF',
                        '#FF3300','#00FFCC']
        extendedColorChoices = ['r','g','c','m','y','k','b','#666666','#00FF00',
                        '#00FFFF','#999999','#993333','#CCCCFF',
                        '#FF3300','#00FFCC']
        extendedColorChoices.extend(colorChoices)
        extendedColorChoices.extend(colorChoices)
        
        colors = assign_colors(s_data.AssessorList, ["rep"])
        
        # If 'Legend' is activated by user
        #if plot_data.view_legend:
        #    plotList = []
        #    for attribute in activeAttributesList:
        #        p = Patch(facecolor = extendedColorChoices[activeAttributesList.index(attribute)])
        #        plotList.append(p)
        #    fig.legend(plotList, activeAttributesList, 'upper right', handlelen = 0.015)
            #figlegend(plotList, activeAssessorsList, drawSettings[2])
            
        
        
        # Finding the maximum F value for the selected assessors and
        # attributes, such that the maximum for Y-axis can be defined
        # further down the code
        max_F = 0; max_p = 0;
        for ass_ind in range(len(ANOVA_F)):
            for att_ind in range(len(ANOVA_F[0])):
                
                F_value = ANOVA_F[ass_ind][att_ind];  p_value = ANOVA_p[ass_ind][att_ind]
                if isinstance(F_value, (int , float)) and isinstance(p_value, (int , float)):    
                    # find max values
                    if F_value > max_F:
                        max_F = F_value
                    if p_value > max_p:
                        max_p = p_value

        
        # Here the spacing is adjusted depending on how many lines 
        # are to be plotted
        numberOfLines = numberOfAssessors * numberOfAttributes
        if numberOfLines <= 70:
            spacer = 3
        elif numberOfLines > 70 and numberOfLines <= 125:
            spacer = 4
        else:
            spacer = 5
        
        
        
        if itemID[0] == "F-values": 
            outputANOVA = ANOVA_F
        else: 
            outputANOVA = ANOVA_p
        

        pointAndLabelList = []
        
        
        lines = []
        line_colors = []
        linewidths = []
        
        # x pos. of lables
        x_positions = []
        last_pos_max = 0.0
        
        
        for att_ind in range(len(activeAttributesList)):
            
            
            #attributeValues = []
            pos_min = 0.0; pos_max = 0.0; c_index = 0
              
            for ass_ind in range(len(activeAssessorsList)):
                assessor = activeAssessorsList[ass_ind]
                value = outputANOVA[ass_ind][att_ind]
                #attributeValues.append(value)
                if value == '*':
                    value = 0
                
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
                
                
                if value <= 0.000001:
                    continue                
                
                
                # lines[0] = [(x0, y0), (x1, y1)]
                lines.append(((position, 0), (position, value)))           
                c = colors[(assessor, "rep")][0]
                line_colors.append(colors[(assessor, "rep")][0])                
                
               
                attribute = activeAttributesList[att_ind]
                
                # Creating pointAndLabelList
                label = '(' + assessor + ', ' + attribute + ')'
                print (label, c, position, value)
                pointAndLabelList.append([position, value, label])
           
            x_positions.append((pos_max-pos_min)/2.0 + pos_min)
                    
        line_collection = LineCollection(lines, colors=line_colors)
        line_collection.set_linewidth(1.2)
        
        ax.add_collection(line_collection)            



        # Defining the titles, axes names, etc
        min_x_scale = 0
        max_x_scale = last_pos_max + spacer + 1
        min_y_scale = 0
        max_y_scale = max_F + max_F * 0.1


        
        # Plotting the horizontal lines for the F values at 
        # 5% and 1% significance level
        lines2 = []; line_colors2 = []
        if itemID[0] == "F-values":
            lines2.append(((0, F_signifcances[0]), (max_x_scale, F_signifcances[0])))
            line_colors2.append("#ff0000")
            lines2.append(((0, F_signifcances[1]), (max_x_scale, F_signifcances[1])))
            line_colors2.append("#000000")
        elif itemID[0] == "p-values":             
            lines2.append(((0, 0.01), (max_x_scale, 0.01)))
            line_colors2.append("#ff0000")
            lines2.append(((0, 0.05), (max_x_scale, 0.05)))            
            line_colors2.append("#000000")        

        line_collection2 = LineCollection(lines2, colors=line_colors2)
        line_collection2.set_linewidth(1.0)
        ax.add_collection(line_collection2) 

        if itemID[0] == "F-values": 
            _ylabel = "F value"
            myTitle = u'F plot: sorted by attributes'
            ymax = max_F
        else:
            _ylabel = "p value"
            myTitle = u'p plot: sorted by attributes'
            ymax = max_p
        ymax += ymax*0.1 # plus 10%
        axes_setup(ax, '', _ylabel, myTitle, [min_x_scale, max_x_scale, 0, ymax])
        
        set_xlabeling(ax, plot_data.activeAttributesList, font_size=10, x_positions=x_positions)
        if len(plot_data.activeAttributesList) > 7:
            set_xlabeling_rotation(ax, 'vertical')
            

        # If 'Legend' is activated by user
        if plot_data.view_legend:
            legend_list = []
            legend_list = activeAssessorsList[:]
            #alpha_char = u"\u03b1"
            legend_list.append('')
            legend_list.append("sign. level: 1%") # "+alpha_char +"=1%")
            legend_list.append("sign. level: 5%") #"+alpha_char +"=5%")
            plotList = []
            for ass in activeAssessorsList:
                p = Line2D([], [], color = colors[(ass, "rep")][0], linewidth=1.2)
                plotList.append(p)
            plotList.append(None)
            plotList.append(Line2D([],[], color = "#ff0000", linewidth=1.1))
            plotList.append(Line2D([],[], color = "#000000", linewidth=1.1))
            fig.legend(plotList, legend_list, 'upper right')
            #figlegend(plotList, activeAssessorsList, drawSettings[2])

        
        
            
        #update plot-data variables:
        plot_data.point_lables = pointAndLabelList
        plot_data.raw_data = rawDataList
        plot_data.numeric_data = resultList
        plot_data.plot_type = "f_att"
        plot_data.point_lables_type = 1

        #Frame draw, for standard Matplotlib frame only use show()
        return plot_data




def FPlotter_Attribute_Specific(s_data, plot_data, num_subplot=[1,1,1], **kwargs):
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
    collectedActiveItemsList.extend(activeAttributesList)
    collectedActiveItemsList.extend(activeSamplesList)
    collectedActiveItemsList.extend(['General Plot'])
    #print collectedActiveItemsList
    #print
    
    # Check wether the selected item is in the collectedActiveItemsList.
    # If not, an error message is activated.
    if itemID[1] not in collectedActiveItemsList:
        dlg = wx.MessageDialog(None, 'The assessor, attribute or sample is not active in CheckBox',
                               'Error Message',
                               wx.OK | wx.ICON_INFORMATION)
        dlg.ShowModal()
        dlg.Destroy()

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
        
        
        print "FPlotter_Attribute_Specific"

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

        # Here starts the plotting procedure
        # ----------------------------------
        # Figure
        replot = False; subplot = plot_data.overview_plot
        if plot_data.fig != None: replot = True
        else: plot_data.fig = Figure(None)
        if subplot: # is subplot
            plot_data.ax = plot_data.fig.add_subplot(num_subplot[0], num_subplot[1], num_subplot[2])
        else: plot_data.ax = axes_create(plot_data.view_legend, plot_data.fig)
        ax = plot_data.ax; fig = plot_data.fig 
        
        
        # Font settings
        font = {'fontname'   : 'Courier',
            'color'      : 'b',
            'fontweight' : 'bold',
            'fontsize'   : 10} 
        
        
        #axes positioning for correlation loadings plot
        ax.grid(plot_data.view_grid)
        
        
        # Create a list with colour choices that are then used for the
        # vertical lines in the plot
        colorChoices = ['r','g','c','m','y','k','b','#666666','#00FF00',
                        '#00FFFF','#999999','#993333','#CCCCFF',
                        '#FF3300','#00FFCC']
        extendedColorChoices = ['r','g','c','m','y','k','b','#666666','#00FF00',
                        '#00FFFF','#999999','#993333','#CCCCFF',
                        '#FF3300','#00FFCC']
        extendedColorChoices.extend(colorChoices)
        
        
        # Finding the maximum F value for the selected assessors and
        # attributes, such that the maximum for Y-axis can be defined
        # further down the code
        max_F = 0; max_p = 0;
        for ass_ind in range(len(ANOVA_F)):
            for att_ind in range(len(ANOVA_F[0])):
                
                F_value = ANOVA_F[ass_ind][att_ind] 
                p_value = ANOVA_p[ass_ind][att_ind]
                if isinstance(F_value, (int , float)) and isinstance(p_value, (int , float)):    
                    # find max values
                    if F_value > max_F:
                        max_F = F_value
                    if p_value > max_p:
                        max_p = p_value

        
        # Here the spacing is adjusted depending on how many lines 
        # are to be plotted
        numberOfLines = numberOfAssessors * numberOfAttributes
        if numberOfLines <= 70:
            spacer = 3
        elif numberOfLines > 70 and numberOfLines <= 125:
            spacer = 4
        else:
            spacer = 5
        
        
        
        if itemID[0] == "F-values": 
            outputANOVA = ANOVA_F
        else: 
            outputANOVA = ANOVA_p
        

        pointAndLabelList = []
        
        
        lines = []
        line_colors = []
        linewidths = []
        
        # x pos. of lables
        x_positions = []
        last_pos_max = 0.0
        
        active_ass_ind = plot_data.activeAssessorsList.index(itemID[1])
        
        for att_ind in range(len(activeAttributesList)):
        
            #attributeValues = []
            pos_min = 0.0; pos_max = 0.0; c_index = 0
            
            
            for ass_ind in range(len(activeAssessorsList)):
                
                
                assessor = activeAssessorsList[ass_ind]
                value = outputANOVA[ass_ind][att_ind]
                #attributeValues.append(value)
                if value == '*':
                    value = 0
                
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
                        
                        
                if value <= 0.000001:
                    continue                            
                        
                
                # lines[0] = [(x0, y0), (x1, y1)]
                lines.append(((position, 0), (position, value)))
                
                if ass_ind == active_ass_ind:
                    line_colors.append("#00E080") # greenish
                    linewidths.append(2.4)
                else:
                    line_colors.append("#0000FF") # blue
                    linewidths.append(1.2)                 
                
               
                attribute = activeAttributesList[att_ind]
                
                # Creating pointAndLabelList
                label = '(' + assessor + ', ' + attribute + ')'
                pointAndLabelList.append([position, value, label])
           
            x_positions.append((pos_max-pos_min)/2.0 + pos_min)
                    
        line_collection = LineCollection(lines, colors=line_colors, linewidths=linewidths)
        ax.add_collection(line_collection)            



        # Defining the titles, axes names, etc
        min_x_scale = 0
        max_x_scale = last_pos_max + spacer + 1
        min_y_scale = 0
        max_y_scale = max_F + max_F * 0.1


        # Plotting the horizontal lines for the F values at 
        # 5% and 1% significance level
        lines2 = []; line_colors2 = []
        if itemID[0] == "F-values":
            lines2.append(((0, F_signifcances[0]), (max_x_scale, F_signifcances[0])))
            line_colors2.append("#ff0000")
            lines2.append(((0, F_signifcances[1]), (max_x_scale, F_signifcances[1])))
            line_colors2.append("#000000")
        elif itemID[0] == "p-values":             
            lines2.append(((0, 0.01), (max_x_scale, 0.01)))
            line_colors2.append("#ff0000")
            lines2.append(((0, 0.05), (max_x_scale, 0.05)))            
            line_colors2.append("#000000")        

        line_collection2 = LineCollection(lines2, colors=line_colors2)
        line_collection2.set_linewidth(1.0)
        ax.add_collection(line_collection2) 


        
        if itemID[0] == "F-values": 
            _ylabel = "F value"
            myTitle = u'F plot: ' + itemID[1]
            ymax = max_F
        else:
            _ylabel = "p value"
            myTitle = u'p plot: ' + itemID[1]
            ymax = max_p
        ymax += ymax*0.1 # plus 10%
        axes_setup(ax, '', _ylabel, myTitle, [min_x_scale, max_x_scale, 0, ymax])

        set_xlabeling(ax, plot_data.activeAttributesList, font_size=10, x_positions=x_positions)
        if len(plot_data.activeAttributesList) > 7:
            set_xlabeling_rotation(ax, 'vertical')


        if plot_data.view_legend:
            legend_list = []
            legend_list.append('')
            legend_list.append("sign. level: 1%") # "+alpha_char +"=1%")
            legend_list.append("sign. level: 5%") #"+alpha_char +"=5%")
            legend_list.append('')
            plotList = []
            plotList.append(None)
            plotList.append(Line2D([],[], color = "#ff0000", linewidth=1.1))
            plotList.append(Line2D([],[], color = "#000000", linewidth=1.1))
            plotList.append(None)
            fig.legend(plotList, legend_list, 'upper right')        
            
        #update plot-data variables:
        plot_data.point_lables = pointAndLabelList
        plot_data.raw_data = rawDataList
        plot_data.numeric_data = resultList
        plot_data.plot_type = "f_att"
        plot_data.point_lables_type = 1

        #Frame draw, for standard Matplotlib frame only use show()
        return plot_data