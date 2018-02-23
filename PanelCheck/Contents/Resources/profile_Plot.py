#!/usr/bin/env python


from Plot_Tools import *
import os, sys
"""
#def profilePlotCalc(f_assessorAveragesList, f_selectedAtt, f_activeSamplesList):

    profilePlotCalc function:

    1. Calculates the mean for given samples over all assessors
    2. Ranks the samples by their mean score for the selected attribute
    3. Ranks the samples scores of every assessor the same way
    4. Returns ranked sample means for selected attribute
    5. Returns ranked sample scores of each assessor for selected attribute
    
    # First find dimensions of the average arrays of each assessor
    rows, cols = f_assessorAveragesList[0].shape
    

    # Now compute the average of each given sample over the given assessors
    sampleAveragesList = []
    for sample in range(len(f_activeSamplesList)):

        assessorSamples = []
        for assessor in f_assessorAveragesList:
            assessorSamples.append(assessor[sample])

        sampleAverage = average(vstack(assessorSamples), 0)
        sampleAveragesList.append(sampleAverage)

    sampleAveragesArray = array(sampleAveragesList)


    attributeVector = sampleAveragesArray[:, f_selectedAtt]


    sortingDict = {}
    for value in range(len(attributeVector)):
        sortingDict[attributeVector[value]] = value


    sampleScores = sortingDict.keys()
    sampleScores.sort()

    rankOrder = []
    for value in sampleScores:
        rankOrder.append(sortingDict[value])

    orderedActiveSampleList = []
    for order in rankOrder:
        orderedActiveSampleList.append(f_activeSamplesList[order])
    #print orderedActiveSampleList


    allAttributeVectors = []
    for assessor in f_assessorAveragesList:

        assessorAttributeVector = []
        for order in rankOrder:
            assessorAttributeVector.append(assessor[order, f_selectedAtt])

        allAttributeVectors.append(assessorAttributeVector)


    # return the ranked mean samples and ranked samples for each assessor
    return sampleScores, allAttributeVectors, orderedActiveSampleList
"""


def get_min_pos(_array):
    min_pos = 0
    min_val = _array[0]
    arr_len = len(_array)
    if arr_len == 1: 
        return 0
    else:
        for i in range(1, arr_len):
            if isinstance(_array[i], (float, int)) and min_val > _array[i]:
                min_val = _array[i]
                min_pos = i
        return min_pos



def sort_indices(mean_array):
    _mean_array = list(mean_array.copy())
    indices_sorted = []   
    while len(indices_sorted) < len(_mean_array):
        pos = get_min_pos(_mean_array)
        indices_sorted.append(pos)
        _mean_array[pos] = '*'
    return indices_sorted 
    
    

def profileCalc(s_data, attribute, active_assessors, active_samples, averages_on):
    cols = len(active_samples)
    if averages_on:
        rows = len(active_assessors) 
    else:
        rows = len(active_assessors) * len(s_data.ReplicateList)
    
    
    mean_array_sorted = zeros((cols), float)
    assessors_scores_sorted = zeros((rows, cols), float) # each row is scores for one assessor
    samples_sorted = []
    
    
    assessors_scores = zeros((rows, cols), float) # each row is scores for one assessor     
    
    if averages_on:
        for ass_ind in range(len(active_assessors)):
            # average of replicates
            average_ass_matrix = s_data.GetAssAverageMatrix(active_assessors[ass_ind], [attribute], active_samples) # only for one attribute
            #print average_ass_matrix
            assessors_scores[ass_ind, :] = average_ass_matrix[:,0] # here average_ass_matrix will be of size: len(active_samples) x 1
    else:
        m_data = s_data.GetActiveData(active_assessors=active_assessors, active_attributes=[attribute], active_samples=active_samples)
        row_ind = 0
        for ass_ind in range(len(active_assessors)):
                for rep_ind in range(len(s_data.ReplicateList)):
                    assessors_scores[row_ind, :] = m_data[ass_ind, :, rep_ind, 0] # Note: only one attribute
                    row_ind += 1
            
       
    mean_array = average(assessors_scores, 0)
    indices_sorted = sort_indices(mean_array)
    
    #print indices_sorted
    
    for ind in range(cols):
        ind_sort = indices_sorted[ind]
        
        samples_sorted.append(active_samples[ind_sort])
        
        mean_array_sorted[ind] = mean_array[ind_sort]
        
        assessors_scores_sorted[:, ind] = assessors_scores[:, ind_sort]
    
    
    return mean_array_sorted, assessors_scores_sorted, samples_sorted, mean_array, assessors_scores



def profilePlotter(s_data, plot_data, num_subplot=[1,1,1], **kwargs):
    #(f_sparseMatrix, f_activeAssessorsList, f_activeSamplesList, f_attributesList, f_selectedAttribute):
    """
    Function for plotting Profile Plot in PanelCheck (some small modifications
    need to be made before implemented into PanelCheck).
    """
    
    if "selection" in kwargs:
        selection = kwargs["selection"]
    else:
        selection = [0, 0]
        
    if "selection" in plot_data.special_opts:
        selection = plot_data.special_opts["selection"]
    
    samples_averages_on = False
    increasing_intensity_on = False
    
    # use sample averages (0|1)
    if selection[0] == 0:
        samples_averages_on = True
    # use increasing intensity (0|1)
    if selection[1] == 0:
        increasing_intensity_on = True
    
    
    f_selectedAttribute = plot_data.tree_path[0]
    
    """
    # Compute average matrix for each active assessor for all active samples
    # and store them in list
    assArraysList = []
    for assessor in plot_data.activeAssessorsList:
        spAss, assSampAv = s_data.GetAssessorAverageMatrix(assessor)
        activeSamplesAveragesList = []
        for sample in plot_data.activeSamplesList:
            activeSamplesAveragesList.append(spAss[sample])
        activeSamplesAverages = array(vstack(activeSamplesAveragesList))
        assArraysList.append(activeSamplesAverages)


    # Find out at which position the selected attribute can be found in the
    # attributes list
    positionSelectedAttribute = s_data.AttributeList.index(f_selectedAttribute)


    # Yield results from the profilePlotCalc function that does the numerical
    # calculations. This is made in this way, such that the function also can
    # be used interactively
    #mean, assessorsLines = profilePlotCalc(assArraysList, positionSelectedAttribute, f_activeSamplesList)
    results = profilePlotCalc(assArraysList, positionSelectedAttribute, plot_data.activeSamplesList)
    #print results
    mean = results[0]
    assessorsLines = results[1]
    orderedActiveSamplesList = results[2]
    #print orderedActiveSamplesList
    """
    
    mean_sorted, assessors_lines, samples_sorted, mean_unsorted, assessors_lines_unsorted  = profileCalc(s_data, f_selectedAttribute, plot_data.activeAssessorsList, plot_data.activeSamplesList, samples_averages_on)
    
    
    if increasing_intensity_on:
        mean = mean_sorted
        samples = samples_sorted
        assessors_scores = assessors_lines
    else:
        mean = mean_unsorted
        samples = plot_data.activeSamplesList
        assessors_scores = assessors_lines_unsorted
    
    #print mean
    #print samples
    
    # Figure
    replot = False; subplot = plot_data.overview_plot; scatter_width = 35
    if plot_data.fig != None: replot = True
    else: plot_data.fig = Figure(None)
    if subplot: # is subplot
        plot_data.ax = plot_data.fig.add_subplot(num_subplot[0], num_subplot[1], num_subplot[2])
        scatter_width = 15
    else: plot_data.ax = axes_create(plot_data.view_legend, plot_data.fig)
    ax = plot_data.ax; fig = plot_data.fig

    # Plotting the results (here just for testing purposes; will not be
    # implemented like this in PanelCheck)
    
    
    _range = arange(0, len(samples))
    # Fist plot the ranked samples mean for the selected attribute as a thick 
    # black line
    ax.plot(_range + 0.5, mean, 'k-', label='mean', linewidth=3)

    # Now plot assessors
    colors = ['r-', 'g-', 'c-', 'y-', 'k-', 'b-', 'r--', 'g--', 'c--', 'y--', 'k--', 'b--', 'r-.', 'g-.', 'c-.', 'y-.', 'k-.', 'b-.']
    c_index = 0
    
  
    colors = assign_colors(s_data.AssessorList, ["rep"])
    
    
    
    plotList = []; resultList = []
    emptyLine = ['']
    _list = ['']
    _list.extend(samples)
    resultList.append(_list)
    
    _list = []
    _list.append("Mean")
    _list.extend(str_row(mean))
    resultList.append(_list)
    resultList.append(emptyLine)
    
    linestyles = ['-', '--', '-.', ':']
    _list = []
    _legend_texts = []
    
    if samples_averages_on:
        for assessor in range(len(plot_data.activeAssessorsList)):
            _numericData = []
            plotList.append(ax.plot(_range + 0.5, assessors_scores[assessor], colors[(plot_data.activeAssessorsList[assessor], "rep")][0], label=plot_data.activeAssessorsList[assessor], linewidth=1))
            _numericData.append(plot_data.activeAssessorsList[assessor])
            _legend_texts.append(plot_data.activeAssessorsList[assessor])
            for x in assessors_scores[assessor]:
                _numericData.append(num2str(x, fmt="%.2f"))
            resultList.append(_numericData)
            #c_index += 1
            #if c_index == len(colors): c_index = 0

    else:
        ind = 0
        for ass_ind in range(len(plot_data.activeAssessorsList)):
            for rep_ind in range(len(s_data.ReplicateList)):
                _numericData = []
                ls_ind = rep_ind
                if ls_ind > len(linestyles)-1:
                    ls_ind = 0
                plotList.append(ax.plot(_range + 0.5, assessors_scores[ind], colors[(plot_data.activeAssessorsList[ass_ind], "rep")][0], linestyle=linestyles[ls_ind], label=plot_data.activeAssessorsList[ass_ind], linewidth=1))
                _numericData.append(plot_data.activeAssessorsList[ass_ind] + " Rep " + str(rep_ind+1) )
                _legend_texts.append(plot_data.activeAssessorsList[ass_ind] + " " + str(rep_ind+1) )
                for x in assessors_scores[ind]:
                    _numericData.append(num2str(x, fmt="%.2f"))
                resultList.append(_numericData)
                ind += 1
        
            
    ax.grid(plot_data.view_grid)
    if plot_data.view_legend:
        h, l = ax.get_legend_handles_labels()
        fig.legend(h,l)

        #_legend_texts.append(''); _legend_texts.append('Mean')
        #plotList.append(None); 
        #plotList.append(Line2D([],[], color = "#000000", linewidth=3))
        #fig.legend(plotList, _legend_texts, 'upper right')    


    y_lims = ax.get_ylim()
    
    # xmax = number of samples tested
    limits = [0, len(samples), plot_data.limits[2], plot_data.limits[3]]
    if not subplot:
        axes_setup(ax, "", "Score", 'Profile plot: ' + f_selectedAttribute, limits)
        ax.set_xticks(_range + 0.5)
        set_xlabeling(ax, samples)
        if len(samples) > 9:
            set_xlabeling_rotation(ax, 'vertical')
    else:
        axes_setup(ax, "", "", 'Profile: ' + f_selectedAttribute, limits, font_size=10)
##    ind = len(orderedActiveSamplesList)
##    #orderedActiveSamplesList = ['a','b','c','d','e','f','g']
##    xticks(ind, tuple(orderedActiveSamplesList))

    #title('Attribute: ' + f_selectedAttribute)
    #ylabel('score')
    #xlabel('tested samples')

    #show()

    
    pointAndLabelList = []
    
    
    frame_colored = colored_frame(s_data, plot_data, plot_data.activeAttributesList, plot_data.tree_path[0])
    if frame_colored:
        significance_legend(plot_data, pos='lower right')
    
    print plot_data.collection_calc_data["p_matr"]
    
    #update plot-data variables:
    plot_data.point_lables = pointAndLabelList
    
    rawDataList = raw_data_grid(s_data, plot_data)
    
    plot_data.numeric_data = resultList
    plot_data.raw_data = rawDataList
    plot_data.plot_type = "profile"
    plot_data.point_lables_type = 0    
    
    
    return plot_data



def profileOverviewPlotter(s_data, plot_data, **kwargs):
    """
    Overview plot
    """
    itemID_list = [] # takes part in what to be plotted
    for att in s_data.AttributeList:
        itemID_list.append([att])
    return OverviewPlotter(s_data, plot_data, itemID_list, profilePlotter, s_data.AttributeList, special_selection=kwargs["selection"])    