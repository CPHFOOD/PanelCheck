#!/usr/bin/env python

from Plot_Tools import *


def CorrelationPlotter(s_data, plot_data, num_subplot=[1,1,1], **kwargs):
	"""
	This is the correlation plot function. In this plot the values of
	a single assessor are plotted against the average values of the
	panel in a scatter plot. The plot indicates how a single assessor 
	performs in relation to the panel.

	The panel average is calculated from the assessors that are checked
	in the assessor-checkListBox. The samples are also listed in a
	sample-checkListBox and can be checked/unchecked and be shown/left out
	in the plot.

        @type selection: int
        @param selection: Not used in this plotter
        
        
	@type s_data.SparseMatrix:     dictionary
	@param s_data.SparseMatrix:    Sparse matrix that contains 3-way data from assessors

	@type ActiveAssessors:  dictionary
	@param ActiveAssessors: Contains assessors that were selected/checked by the user
				in the assessor-checkListBox

	@type ActiveSamples:    dictionary
	@param ActiveSamples:   Contains samples that were selected/checked by the user
				in the sample-checkListBox

	@type noOfWindows:      integer
	@param noOfWindows:     Indicates the number of the actual plot to be generated

	@type assessorList:     list
	@param assessorList:    Contains all assessors from original data set

	@type s_data.SampleList:       list
	@param s_data.SampleList:      Contains all samples from original data set

	@type s_data.ReplicateList:    list
	@param s_data.ReplicateList:   Contains all replicates original from data set

	@type s_data.AttributeList:    list
	@param s_data.AttributeList:   Contains all attributes original from data set

	@type selectedItem:     list
	@param selectedItem:    Conatins which item in the tree was double-clicked

	@type y_min:            integer
	@param y_min:           indicates the highest score value given in in data set

	ActiveSample_list: Is created from ActiveAssessors (dictionary) and is
	used for iterating through the active asessors
	ActiveSample_list: list
	"""
	# First excerpt values from particular assessor (the one that
	# was clicked on)
	#print 'selected assessor: ', selectedItem[0]
        activeAssessorsList = plot_data.activeAssessorsList
        activeAttributesList = plot_data.activeAttributesList
        activeSamplesList = plot_data.activeSamplesList
        itemID = plot_data.tree_path

        if itemID[1] in s_data.AttributeList:
            index_a = 0
            index_b = 1
        else: 
            index_a = 1
            index_b = 0           

	position = s_data.AttributeList.index(itemID[index_b])
	particularAssessorData = []

	if itemID[index_a] not in activeAssessorsList: #selected assessor not active
	    dlg = wx.MessageDialog(None, 'The assessor is not active in CheckBox',
			       'Error Message',
			       wx.OK | wx.ICON_INFORMATION)
	    dlg.ShowModal()
	    dlg.Destroy()
	    return
	if len(activeSamplesList) < 1: #no active samples
	    dlg = wx.MessageDialog(None, 'No samples are active in CheckBox',
			       'Error Message',
			       wx.OK | wx.ICON_INFORMATION)
	    dlg.ShowModal()
	    dlg.Destroy()
	    return
	  
	colors = colors_hex_list
	    
        # Figure
        replot = False; subplot = plot_data.overview_plot; scatter_width = 35
        if plot_data.fig != None: replot = True
        else: plot_data.fig = Figure(None)
        if subplot: # is subplot
            plot_data.ax = plot_data.fig.add_subplot(num_subplot[0], num_subplot[1], num_subplot[2])
            scatter_width = 15
        elif len(activeSamplesList) <= len(colors):
            plot_data.ax = axes_create(plot_data.view_legend, plot_data.fig)
        else:
            plot_data.ax = axes_create(0, plot_data.fig)
        ax = plot_data.ax; fig = plot_data.fig
        
        
	#One element in the pointAndLabelList will always contain 3 items [x, y, label]
	pointAndLabelList = []

	# Create a list with active (checked in CheckListBox) assessors/attributes
	# that is chronologically sorted as in original file. Just doing
	# .keys() and .sort() is not enough, since only alphabetical order
	# is given. 


	# Collect data of selected assessors in one list and construct
	# pointAndLabelList
	for sample in activeSamplesList:

	    replicateSum = 0
	    for replicate in s_data.ReplicateList:
		value = s_data.SparseMatrix[itemID[index_a], sample, replicate][position]
		replicateSum += float(value)

	    replicateAverage = replicateSum / len(s_data.ReplicateList)
	    particularAssessorData.append(replicateAverage)


	# Now calculate the average values for the active assessors
	selectedAssessorAverage = []

	i = 0
	for sample in activeSamplesList:

	    assessorsReplicateSum = 0
	    for replicate in s_data.ReplicateList:

		for assessor in activeAssessorsList:
		    value = s_data.SparseMatrix[assessor, sample, replicate][position]
		    assessorsReplicateSum += float(value)

	    assessorsReplicateAverage = assessorsReplicateSum / (len(s_data.ReplicateList) * len(activeAssessorsList))
	    selectedAssessorAverage.append(assessorsReplicateAverage)
	    i += 1



	# Starting generation of the list that contains the data
	# that is shown in "Show Data"
	emptyLine = ['']

	
	rawDataList = raw_data_grid(s_data, plot_data)


	resultList = []
	sampleValues = ['Sample calculations:']
	resultList.append(sampleValues)
	assessorInfo = 'Assessor: ' + itemID[index_a]
	infoLine = [assessorInfo]
	resultList.append(infoLine)

	attributeInfo = 'Attribute: ' + itemID[index_b]
	infoLine = [attributeInfo]
	resultList.append(infoLine)

	resultList.append(emptyLine)

	headerLine = ['Sample', itemID[index_a], 'PanelAverage']
	resultList.append(headerLine)

	for sample in activeSamplesList:

	    dataLine = []
	    positionInList = activeSamplesList.index(sample)
	    selectedAssessorValue = particularAssessorData[positionInList]
	    panelAverageValue = selectedAssessorAverage[positionInList]

	    dataLine= [sample, num2str(selectedAssessorValue, fmt="%.2f"), num2str(panelAverageValue, fmt="%.2f")]
	    resultList.append(dataLine)


	# Setting max and min values for the axis
	x_start = 0
	x_end = 10
	y_start = 0
	y_min = plot_data.limits[3]
	y_end = y_min + y_min * 0.1

	# Construction the data for the line from origo 
	x_values = [x_start, x_end]
	y_values = [y_start, y_end]

	# Font settings
	font = {'fontname'   : 'Courier',
	    'color'      : 'b',
	    'fontweight' : 'bold',
	    'fontsize'   : 10}      
	   

	# The following line makes it possible to open a 
	# new window every time an item on the wxTreeCtrl is 
	# double-clicked


	# Settings for the labels in the plot
	myTitle = 'Correlation plot: ' + itemID[index_a] + ', ' + itemID[index_b]
	specificAssessor = itemID[index_a]


	# This is the line from the origo
	ax.plot([plot_data.limits[2], plot_data.limits[3]], [plot_data.limits[2], plot_data.limits[3]], '--')

	# Plotting the other assessors values
	for assessor in activeAssessorsList:
	    eachAssessorValues = []
	    for sample in activeSamplesList:
		replicateSum = 0
		for replicate in s_data.ReplicateList:
		    value = s_data.SparseMatrix[assessor, sample, replicate][position]
		    replicateSum += float(value)

		replicateAverage = replicateSum / len(s_data.ReplicateList)
		eachAssessorValues.append(replicateAverage)
		label = assessor + ' - ' + sample
		pointAndLabelList.append([selectedAssessorAverage[activeSamplesList.index(sample)], replicateAverage, label, sample, assessor, itemID[index_b]])

	    # use c = 'w' for points with black circle around it
	    # use other, f.ex. color = 'w' to avoid circle around point to be plotted 
	    ax.scatter(selectedAssessorAverage, eachAssessorValues, s = scatter_width-5, c = 'w', marker = 'o')




	# Plotting the values from the specific assessor
	ax.grid(plot_data.view_grid)
	
	
        if len(selectedAssessorAverage) <= len(colors):
            plotList = []
            for i in range(len(selectedAssessorAverage)):
                #plotList.append(ax.scatter([selectedAssessorAverage[i]], [particularAssessorData[i]], s = scatter_width, color = colors[i], marker = 'o'))
                ax.scatter([selectedAssessorAverage[i]], [particularAssessorData[i]], s = scatter_width, color = colors[i], marker = 'o')
                plotList.append(Line2D([],[], color = colors[i], linewidth=4))
	    if plot_data.view_legend:
	        fig.legend(plotList, plot_data.activeSamplesList, 'upper right')
	else:
            ax.scatter(selectedAssessorAverage, particularAssessorData, s = scatter_width, color = 'r', marker = 'o')
	   	
	#ax.scatter(selectedAssessorAverage, particularAssessorData, s = scatter_width, color = 'r', marker = 'o')
	#ipshell()

	limits = []
	limits.append(plot_data.limits[2])
	limits.append(plot_data.limits[3])
	limits.append(plot_data.limits[2])
	limits.append(plot_data.limits[3])
	
	if subplot: axes_setup(ax, '', '', 'Corr. plot: ' + itemID[index_a] + ', ' + itemID[index_b], limits, font_size=10)
	else: axes_setup(ax, 'Active panel average', itemID[index_a], myTitle, limits)

        #update plot-data variables:
        plot_data.point_lables = pointAndLabelList
        plot_data.raw_data = rawDataList
        plot_data.numeric_data = resultList
        plot_data.plot_type = "corr"
        plot_data.point_lables_type = 0

        #Frame draw, for standard Matplotlib frame only use show()
        return plot_data



def CorrelationOverviewPlotter(s_data, plot_data, **kwargs):
    """
    Overview Plot
    """

    itemID_list = [] # takes part in what to be plotted
    if plot_data.tree_path[0] in s_data.AssessorList:
        for att in s_data.AttributeList:
            itemID_list.append([plot_data.tree_path[0], att])
        rotation_list = s_data.AttributeList
    else:
        for ass in plot_data.activeAssessorsList:
            itemID_list.append([plot_data.tree_path[0], ass])
        rotation_list = plot_data.activeAssessorsList
    return OverviewPlotter(s_data, plot_data, itemID_list, CorrelationPlotter, rotation_list)
    
   