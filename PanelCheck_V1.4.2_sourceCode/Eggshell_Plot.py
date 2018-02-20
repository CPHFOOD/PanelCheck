#!/usr/bin/env python

from Plot_Tools import *


def EggshellPlotter(s_data, plot_data, num_subplot=[1,1,1], **kwargs):
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
    
    @type s_data.AssessorList:     list
    @param s_data.AssessorList:    Contains all assessors from original data set
    
    @type s_data.SampleList:       list
    @param s_data.SampleList:      Contains all samples from original data set
    
    @type s_data.ReplicateList:    list
    @param s_data.ReplicateList:   Contains all replicates original from data set
    
    @type s_data.AttributeList:    list
    @param s_data.AttributeList:   Contains all attributes original from data set
    
    @type itemID:     list
    @param itemID:    Conatins which item in the tree was double-clicked
    
    ActiveSample_list: Is created from ActiveAssessors (dictionary) and is
    used for iterating through the active asessors
    ActiveSample_list: list
    """
    #print itemID, ' was selected'

    activeAssessorsList = plot_data.activeAssessorsList
    activeAttributesList = plot_data.activeAttributesList
    activeSamplesList = plot_data.activeSamplesList
    itemID = plot_data.tree_path
    
    
    if len(activeAssessorsList) < 1: #no active assessors
        dlg = wx.MessageDialog(None, 'No assessors are active in CheckBox',
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
    
    
    
    # Figure
    replot = False; subplot = plot_data.overview_plot
    if plot_data.fig != None: replot = True
    else: plot_data.fig = Figure(None)
    if subplot: # is subplot
        plot_data.ax = plot_data.fig.add_subplot(num_subplot[0], num_subplot[1], num_subplot[2])
    else: plot_data.ax = axes_create(plot_data.view_legend, plot_data.fig)
    ax = plot_data.ax; fig = plot_data.fig
    
    
    # Construction of Tucker1-matrix, where assessor matrices are 
    # put beside each other starting with assessor1, then assessor 2
    # and so on
    numberOfAssessors = len(activeAssessorsList)
    numberOfSamples = len(activeSamplesList)
    numberOfReplicates = len(s_data.ReplicateList)
    
    RankMatrix = zeros((numberOfSamples, numberOfAssessors), float)
    
    # This matrix contains the average score (over replicates) that one
    # assessor gives for a particular sample.
    SampleScoreAverageMatrix = zeros((numberOfSamples, numberOfAssessors), float)
  
    # This finds out which attribute was selected using the index
    # method for lists
    attributePosition = s_data.AttributeList.index(itemID[0])
    
    # Here starts the calculation of the rank matrix containing the
    # rankings for all samples for all assessors.
    for assessor in activeAssessorsList:
        #print assessor, itemID
        
        # Average values (over all replicates) and sample name of each sample 
        # are collected in a dictionary first. 
        rankSampleDictionary = {}
        
        # Here starts calculation sample average over replicates
        for sample in activeSamplesList:
            #print sample
            
            sum = 0
            for replicate in s_data.ReplicateList:
                value = s_data.SparseMatrix[(assessor, sample, replicate)][attributePosition]
                sum = sum + float(value)
            
            average_ = sum / len(s_data.ReplicateList)
            #rankSampleDictionary[sample] = str(average_)
            rankSampleDictionary[sample] = average_
            #print assessor, sample, rankSampleDictionary[sample]
            SampleScoreAverageMatrix[activeSamplesList.index(sample)][activeAssessorsList.index(assessor)] = average_
        
        
        # Average and sample names are put in tuples that are stored in a
        # tupleList. (average, item)
        # The average is first in the tuple in order to enable sorting by
        # size of the average.
        tupleList = []
        for item in rankSampleDictionary.keys():
            newTuple = (rankSampleDictionary[item], item)
            tupleList.append(newTuple)
        
        # tupleList is sorted and reversed, such that the highest values
        # come first and the lowest last.
        tupleList.sort()
##        print tupleList
##        print
        tupleList.reverse()
##        print tupleList
##        print
        
        samplesAndRanks = {}
        # Here starts the calcuation of the rankings
        #print '*** calc of rankings ***'
        equalList = []
        indexList = []
        
        # Check items from first to next-to-last
        for item in range(len(tupleList) - 1):
            
            #print item, tupleList[item]
            # If the actual item and the following one (runner up) 
            # ARE EQUAL do this:
            if tupleList[item][0] == tupleList[item + 1][0]:
                
                # If items are not on equalList, put them there
                if tupleList[item] not in equalList:
                    equalList.append(tupleList[item])
                    indexList.append(tupleList.index(tupleList[item]) + 1)
                
                # The runner-up item is also added to the equalList
                equalList.append(tupleList[item + 1])
                indexList.append(tupleList.index(tupleList[item + 1]) + 1)
                
                
                # This one is for the case when the last item in the tupleList
                # is equal to the next-to-last.
                if item == (len(tupleList) - 2):
                    
                    checkSum = 0
                    for rawRanks in indexList:
                        checkSum = checkSum + rawRanks
                    realRanks = float(checkSum) / float(len(indexList))
                    
                    for sampleNames in equalList:
                        samplesAndRanks[sampleNames[1]] = realRanks
                
                # Go back to loop and check whether the next item is also 
                # equal to the actual item
                continue
            
            #print '\n'#'it gets here'
            
            # This here calculates the common rank for those samples that
            # have the same average value for the specific assessor
            if len(equalList) > 0:
                
                checkSum = 0
                for rawRanks in indexList:
                    checkSum = checkSum + rawRanks
                realRanks = float(checkSum) / float(len(indexList))
                
                for sampleNames in equalList:
                    samplesAndRanks[sampleNames[1]] = realRanks
            
            
            # If the actual item and the runner-up ARE NOT EQUAL, do
            # the following:
            if tupleList[item][0] > tupleList[item + 1][0]:
                
                if tupleList[item] not in equalList:
                    realRank = tupleList.index(tupleList[item]) + 1
                    
                    samplesAndRanks[tupleList[item][1]] = float(realRank)
            
            
            # Empty the lists that are used for equal items. They will be
            # filled again when new equal items come up again
            equalList = []
            indexList = []
            
            # This is the last comparison between the next to last item
            # and the last item
            if item == (len(tupleList) - 2):
                
                # If the equal list is empty, then the last item gets the 
                # lowest rank, which is the length of the tuple list
                if len(equalList) == 0:
                    samplesAndRanks[tupleList[item + 1][1]] = len(tupleList)
        
        #print samplesAndRanks
        #print
        
        for samples in activeSamplesList:
            RankMatrix[activeSamplesList.index(samples)][activeAssessorsList.index(assessor)] = samplesAndRanks[samples]
            
##    print tupleList
##    print
    
    #print
    #print 'Rank Matrix'
    #print RankMatrix
    #print
    
##    copyOfRankMatrix = RankMatrix.copy()
##    
##    # Carrying out PCA for determination of the consensus ranking
##    PCAanalysis = PCA(copyOfRankMatrix, 1)
##    scores = PCAanalysis.GetScores()
    
    # 02.11.2005
    # This is a new part of the RankMatrix calculations. After checking with
    # Per Lea it was shown that the ranks in the RankMatrix should be inversed
    # from those ranks that we have calculated. 
    # That is, the sample with rank 1 should actually be rank = numberOfSamples.
    # The next few lines of code inverse the ranking and put them in the
    # right way. Instead of rewriting the whole ranking algorithm, we do this
    # since this is a much simplier way to do it.
    # inversedRank = (numberOfSamples + 1) - rank
    
    InverseRankMatrix = zeros((numberOfSamples, numberOfAssessors), float)
    
    for sample in range(numberOfSamples):
        
        for assessor in range(numberOfAssessors):
            
            InverseRankMatrix[sample][assessor] = numberOfSamples + 1 - RankMatrix[sample][assessor]
    
    #print
    #print InverseRankMatrix
    #print 
    #print SampleScoreAverageMatrix
    
    #sampleRankAverage = average(RankMatrix, axis=0, weights=None)
    # --- only for Masked Arrays
    
    # Transpose the SampleScoreAverageMatrix and get score average for each
    # sample over all assessors
    #print SampleScoreAverageMatrix
    #print SampleScoreAverageMatrix.transpose()
    sampleRankAverage = average(SampleScoreAverageMatrix.transpose(), 0)
    #print sampleRankAverage
    #print
    
    # Calculate average for each sample over all assessors and then sort averages
    # by size to find the consensus ranking
    sampleList = []
    for sample in range(len(activeSamplesList)):
        newTuple = (sampleRankAverage[sample], activeSamplesList[sample])
        #print newTuple
        sampleList.append(newTuple)
    
    sampleList.sort()
    #print
    #print s_data.SampleList
    #print
    #s_data.SampleList.reverse()
    #print s_data.SampleList
    
    #print
    #print '***sorted***'
    #for sample in sampleList:
    #    print sample
    
    # This matrix contains the ranks of each sample for each assessor, however
    # they are sorted according to consensus rank
    consensusRankedMatrix = zeros((numberOfSamples, numberOfAssessors), float)
    #print
    for sample in range(len(sampleList)):
        indexedSample = sampleList[sample][1]
        indexedRowVector = InverseRankMatrix[activeSamplesList.index(indexedSample)]
        
        consensusRankedMatrix[sample] = indexedRowVector
        
    #print 'consensusRankedMatrix'
    #print consensusRankedMatrix
    
    
    # This matrix contains the cumulative ranks that are necessary for
    # further calculation
    cumulativeRankedMatrix = zeros((numberOfSamples, numberOfAssessors), float)
    
    for assessor in range(numberOfAssessors):
        
        culSum = 0
        for sample in range(numberOfSamples):
            culSum = culSum + consensusRankedMatrix[sample][assessor]
            cumulativeRankedMatrix[sample][assessor] = culSum
            
    #print
    #print 'cumulativeRankedMatrix'
    #print cumulativeRankedMatrix
    
    
    # This matrix contains the final values that are to be plotted in the
    # eggshell plot.
    eggshellMatrix = zeros((numberOfSamples, numberOfAssessors), float)
    #print
    for sample in range(1, numberOfSamples + 1):
        equ_i = float((numberOfSamples + 1) * sample) / 2
        #print 'equ_i = ', equ_i
        
        eggshellMatrix[sample - 1] = cumulativeRankedMatrix[sample - 1] - equ_i
        #print eggshellMatrix[sample - 1]
        #print cumulativeRankedMatrix[sample - 1]
    
    
    #print
    #print 'eggshellMatrix'
    #print eggshellMatrix
    
    print
    
    # Calculation of the eggshell-baseline
    baseline = []
    for sample in range(1, numberOfSamples + 1):
        equ_i = float((numberOfSamples + 1) * sample) / 2
        min_i = float(sample * (sample + 1)) / 2
        
        b_i = min_i - equ_i
        #print b_i
        
        baseline.append(b_i)
    
    
    print
    # Here starts the plotting procedure
    # ----------------------------------
    ax.grid(plot_data.view_grid)
    
    # Collect info for legend
    plotList = []
    
    
    # This plots the baseline of the eggshell plot
    x_values = arange(1, numberOfSamples + 1)
    y_values = baseline
    ax.plot(x_values, y_values, 'm-', linewidth=2)
    
    assessorPlotSettings = ['r-', 'g-', 'c-', 'y-', 'k-', 'b-', 'r--', 'g--', 'c--', 'y--', 'k--', 'b--', 'r-.', 'g-.', 'c-.', 'y-.', 'k-.', 'b-.']
    
    
    colors = assign_colors(s_data.AssessorList, ["rep"])
    
    y_max = baseline[0]
    
    c_index = 0
    linestyle = "-"
    
    for assessor in range(numberOfAssessors):
        y_values = eggshellMatrix[:, assessor]
        if y_max < max(eggshellMatrix[:, assessor]):
            y_max = max(eggshellMatrix[:, assessor])
            
        #print 'y_max = ', y_max
        if assessor > (numberOfAssessors*0.5):
            linestyle = "--"
        
        #ax.plot(x_values, y_values, color=colors[(activeAssessorsList[assessor], "rep")][0], linestyle=linestyle, label=activeAssessorsList[assessor])
        plotList.append(ax.plot(x_values, y_values, color=colors[(activeAssessorsList[assessor], "rep")][0], linestyle=linestyle, label=activeAssessorsList[assessor]))
        #c_index += 1
        #if c_index >= len(assessorPlotSettings):
        #    c_index = 0
        
    # If 'Legend' is activated by user
    if plot_data.view_legend:
        h, l = ax.get_legend_handles_labels()
        fig.legend(h,l)
        #fig.legend(plotList, activeAssessorsList, 'upper right')
    
    # Defining the titles, axes names, etc
    myTitle = 'Eggshell plot: ' + itemID[0]
    min_x_scale = 0
    max_x_scale = numberOfSamples + 1
    min_y_scale = min(baseline) - (y_max - min(baseline)) * 0.05
    max_y_scale = y_max + (y_max - min(baseline)) * 0.1
    if not subplot: 
        axes_setup(ax, 'consensus ranking', 'value', myTitle, [min_x_scale, max_x_scale, min_y_scale, max_y_scale])
    else: axes_setup(ax, '', '', myTitle, [min_x_scale, max_x_scale, min_y_scale, max_y_scale], font_size=10)
    
    # Starting generation of the list that contains the raw data
    # that is shown in "Raw Data" when pushing the button in the plot
    emptyLine = ['']
    
    
    rawDataList = raw_data_grid(s_data, plot_data)
    
    # Starting generation of the list that contains the data
    # that is shown in "Numerical Results"
    resultList = []
    emptyLine = ['']
    headerResults = ['EGGSHELL MATRIX']
    resultList.append(headerResults)
    resultList.append(emptyLine)
    
    header1Eggshell = [itemID[0], 'low intensity']
    for sample in range(len(activeSamplesList) - 1):
        header1Eggshell.append('')
    header1Eggshell[-1] = 'high intensity'
    
    header2Eggshell = ['Samples']
    samples = []
    for sample in sampleList:
        samples.append(sample[1])
        header2Eggshell.append(sample[1])
    
    resultList.append(header1Eggshell)
    resultList.append(header2Eggshell)
    emptyLine = ['']
    
    for assessor in activeAssessorsList:
        assessorLine = [assessor]
        eggshellValues = eggshellMatrix[:, activeAssessorsList.index(assessor)]
        assessorLine.extend(eggshellValues)
        resultList.append(assessorLine)
    
    consensusLine = ['Consensus']
    consensusLine.extend(baseline)
    resultList.append(consensusLine)
    
    if not subplot: 
        set_xlabeling(ax, samples, font_size=10)
        if len(samples) > 11:
            set_xlabeling_rotation(ax, 'vertical')
    
    frame_colored = colored_frame(s_data, plot_data, activeAttributesList, itemID[0])
    if frame_colored:
        significance_legend(plot_data, pos='lower right')
    
    #update plot-data variables:
    plot_data.raw_data = rawDataList
    plot_data.numeric_data = resultList
    plot_data.plot_type = "egg"

    #Frame draw, for standard Matplotlib frame only use show()
    return plot_data
    
def EggshellOverviewPlotter(s_data, plot_data, **kwargs):
    """
    Overview plot
    """
    itemID_list = [] # takes part in what to be plotted
    for att in s_data.AttributeList:
        itemID_list.append([att])
    return OverviewPlotter(s_data, plot_data, itemID_list, EggshellPlotter, s_data.AttributeList)