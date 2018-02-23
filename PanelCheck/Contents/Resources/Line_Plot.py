#!/usr/bin/env python

from Plot_Tools import *

##from IPython.Shell import IPShellEmbed
##ipshell = IPShellEmbed()


def SampleLinePlotter(s_data, plot_data, num_subplot=[1,1,1], **kwargs):
    """
    This function generates the line plot for a specific sample. The number
    of assessors and attributes can be chosen in the checkListBoxes in the
    GUI.

    @type selection: int
    @param selection: Not used in this plotter

    @type drawSettings:     list
    @param drawSettings:    List of settings on how to draw the figure. [grid?, legend?, legend_position, x_y_Limits]

    @type s_data.SparseMatrix:     dictionary
    @param s_data.SparseMatrix:    Complete dictionary type of Matrix with all values

    @type noOfWindows:      integer
    @param noOfWindows:     nteger value for the new window

    @type insideItemID:     pyData
    @param insideItemID:    pyData from wxTree

    @type s_data.AssessorList:     list
    @param s_data.AssessorList:    Complete list of ALL assessors

    @type s_data.ReplicateList:    list
    @param s_data.ReplicateList:   Complete list of ALL replicates

    @type s_data.AttributeList:    list
    @param s_data.AttributeList:   Complete list of ALL attributes

    @type ActiveAssessors:  dictionary
    @param ActiveAssessors: Contains the active/checked assessors

    @type ActiveAttributes:  dictionary
    @param ActiveAttributes: Contains the active/checked attributes
    """
    # Create a list with active (checked in CheckListBox) assessors/attributes
    # that is chronologically sorted as in original file. Just doing
    # .keys() and .sort() is not enough, since only alphabetical order
    # is given.
    activeAssessorsList = plot_data.activeAssessorsList
    activeAttributesList = plot_data.activeAttributesList
    itemID = plot_data.tree_path

    plottingSparseMatrix = {}

    # Error check: are there any values in activeAssessorsList?
    if len(activeAssessorsList) < 1:
        dlg = wx.MessageDialog(None, 'No assessors checked in CheckBox',
                               'Error Message',
                               wx.OK | wx.ICON_INFORMATION)
        dlg.ShowModal()
        dlg.Destroy()
        return


    # Here a list is created that contains the positions
    # of the active attributes. This is needed in the next
    # step, when the plottings_data.SparseMatrix is created.
    activeAttributeIndexList = []
    for attribute in activeAttributesList:

        positionSpecificAttribute = s_data.AttributeList.index(attribute)
        activeAttributeIndexList.append(positionSpecificAttribute)



    # Here the plottings_data.SparseMatrix is calculated. A flat matrix is also
    # constructed during the process, that makes construction of an "normal" array
    # easier.
    flatMatrixList = []
    for assessor in activeAssessorsList:

        for replicate in s_data.ReplicateList:

            itemToupleKey = (assessor, itemID[0], replicate)

            specificList = []
            for attribute in activeAttributeIndexList:

                specificList.append(s_data.SparseMatrix[itemToupleKey][attribute])

            plottingSparseMatrix[itemToupleKey] = specificList
            for singleValues in plottingSparseMatrix[itemToupleKey]:
                flatMatrixList.append(float(singleValues))

    #print flatMatrixList

    # Here the flatMatrixList is converted into the plottingMatrix array.
    plottingMatrix = reshape(array(flatMatrixList, float), (len(plottingSparseMatrix), -1))
    meanVector = average(plottingMatrix, 0)
    dimensions = plottingMatrix.shape


    # Starting generation of the list that contains the raw data
    # that is shown in "Raw Data" when pushing the button in the plot
    emptyLine = ['']


    rawDataList = raw_data_grid(s_data, plot_data, active_samples=[itemID[0]])

    #print dimensions

    # If number of activeAttributes is less than full the following applies.
    # The maximum value for the x-Axis needs to be adjusted to the number
    # of active attributes.
    # drawSettings[3][1] conatins the maximum value for the X-axis.
    originalX_AxeValue = plot_data.limits[1]
    if dimensions[1] < len(s_data.AttributeList):
        print 'other scale for x'
        print plot_data.limits
        plot_data.limits[1] = dimensions[1] + 1

    #print plottingMatrix


    # Finding the maximun and minimum values in the plottingMatrix
    ##    yMin_values = array([])
    ##    yMax_values = array([])
    ##    ySTD_values = array([])

    yMin_values = []
    yMax_values = []
    ySTD_values = []

    for eachAttribute in range(dimensions[1]):
        column = take(plottingMatrix, (eachAttribute,), 1)
        #print column
        #deviation = round(std(column), 3)
        ##        yMin_values = concatenate((yMin_values, (min(column))))
        ##        yMax_values = concatenate((yMax_values, (max(column))))
        ##        ySTD_values = concatenate((ySTD_values, (std(column))))


        lowestValue = min(column)
        highestValue = max(column)
        deviation = round(std(column), 3)
        yMin_values.append(lowestValue[0])
        yMax_values.append(highestValue[0])
        ySTD_values.append(deviation)

    #print yMin_values
    #print yMax_values

    # Vectors that plot the average values of all sensors
    x_values = arange(1, dimensions[1] + 1)
    y_values = meanVector


    # Starting generation of the list that contains the data
    # that is shown in "Show Data"
    resultList = []
    sampleHeaderLine = ['Sample: ']
    sampleHeaderLine.extend(itemID)
    resultList.append(sampleHeaderLine)
    resultList.append(emptyLine)
    attributeLineNumericalResults = ['']
    attributeLineNumericalResults.extend(activeAttributesList)
    resultList.append(attributeLineNumericalResults)


    # Adding the mean, max value, min value and std for each
    # attribute to the data grid
    _line = ['PANEL MEAN']
    for x in meanVector:
        _line.append(num2str(x, fmt="%.2f"))
    resultList.append(_line)

    _line = ['MIN']
    for x in yMin_values:
        _line.append(num2str(x, fmt="%.2f"))
    resultList.append(_line)

    _line = ['MAX']
    for x in yMax_values:
        _line.append(num2str(x, fmt="%.2f"))
    resultList.append(_line)

    _line = ['STD']
    for x in ySTD_values:
        _line.append(num2str(x, fmt="%.2f"))
    resultList.append(_line)

    #ipshell()

    # Figure
    replot = False; subplot = plot_data.overview_plot; scatter_width = 35
    if plot_data.fig != None: replot = True
    else: plot_data.fig = Figure(None)
    if subplot: # is subplot
        plot_data.ax = plot_data.fig.add_subplot(num_subplot[0], num_subplot[1], num_subplot[2])
        scatter_width = 15
    else: plot_data.ax = axes_create(plot_data.view_legend, plot_data.fig)
    ax = plot_data.ax; fig = plot_data.fig

    # From here the matplotlib plotting procedure starts
    #symbolList = ['ro', 'go', 'co', 'mo', 'yo', 'ko', 'bo', 'wo']#, 'rs', 'gs','cs', 'ms']

    # This is the new symbolList that allows more nuanced colours than the
    # default colours.
    # Check out 'http://www.visibone.com/colorlab/' for HTML colour codes
    symbolList = [['r', 'o'], ['g', 'o'], ['c', 'o'], ['m', 'o'], ['y', 'o'],
                    ['k', 'o'], ['b', 'o'], ['#666666', 'o'], ['#00FF00', 'o'],
                    ['#00FFFF', 'o'], ['#999999', 'o'], ['#993333', 'o'],
                    ['#CCCCFF', 'o'], ['#FF3300', 'o'], ['#00FFCC', 'o'],
                    ['#00CCFF', 'o'], ['#009999', 'o'], ['#660033', 'o'],
                    ['#CC00FF', 'o'], ['#CC3300', 'o'], ['#00CCCC', 'o']]




    # The following 2 lines of code make it possible to open a
    # new window every time an item on the wxTreeCtrl is
    # double-clicked

    # Plots the line with average values for all enabled assessors
    ax.plot(x_values, y_values, '-')

    # This plots the vertical lines using the minimum and maximum values from
    # the plottingMatrix
    vertices = []
    for atts in range(dimensions[1]):
        #ax.vlines([x_values[atts]], [yMin_values[atts]], [yMax_values[atts]], fmt='b')
        vertices.append(((x_values[atts], yMin_values[atts]),(x_values[atts], yMax_values[atts])))



    lc = LineCollection(vertices, colors='#0000FF')
    plot_data.ax.add_collection(lc)



##    # This plots all the assessors scores in the line plot with
##    # different colours/symbols for each assessor.
##    # First
##    enableds_data.AssessorList = []
##    for item in plottings_data.SparseMatrix:
##        if item[0] not in enableds_data.AssessorList:
##            enableds_data.AssessorList.append(item[0])
##
##    enableds_data.AssessorList.sort()


    # The following code handles the labelling for mouse-pointing over
    # certain points in the plot. Implemented by Henning and sligtly
    # modified by Oli.
    plotList = []
    #One element in the pointAndLabelList will always contain 3 items [x, y, label]
    pointAndLabelList = []

    #epsilon = 1% of edge length, a cirka diameter of one plot circle, this depends on figure resolution
    epsilon = (plot_data.limits[1]) *0.01
    #the accurate amount of room between each attribute line -1, with plot circle diameter of 1%
    #zero division will not happen, because with no chosen attributes: drawSettings[3][1] = 1
    maxPlotsBesideEachother = int(floor((100/plot_data.limits[1])-1))
    print "Max number of plottings beside eachother: " + str(maxPlotsBesideEachother)


    coloring_list = s_data.AssessorList
    #if "coloring" in plot_data.special_opts:
    #    if plot_data.special_opts["coloring"] == "samples":
    #        coloring_list = s_data.SampleList


    colors = assign_colors(coloring_list, s_data.ReplicateList)

    #plottings_data.AssessorList = zip(enableds_data.AssessorList,symbolList)
    #for items in plottings_data.AssessorList:
    for items in activeAssessorsList:
        checkBox = 0
        for replicate in s_data.ReplicateList:
            key = (items, itemID[0], replicate)

            if plottingSparseMatrix.has_key(key):
                #print 'yes', plottings_data.SparseMatrix[key]
                y_samples = []; x_samples = []
                for value in range(len(plottingSparseMatrix[key])):
                    ySampleValue = float(plottingSparseMatrix[key][value])
                    y_samples.append(ySampleValue)
                    label = items + ' (' + activeAttributesList[value] + ': ' + replicate +')'

                    xSampleValue = value + 1
                    #print xSampleValue, ySampleValue
                    xSampleValue = check_point(xSampleValue, ySampleValue, epsilon, pointAndLabelList, maxPlotsBesideEachother)
                    pointAndLabelList.append([xSampleValue, ySampleValue, label, 1])
                    if not checkBox:
                        #plotList.append(ax.scatter([xSampleValue], [ySampleValue], s = 30, color = symbolList[symItem][0], marker = 'o'))
                        plotList.append(ax.scatter([xSampleValue], [ySampleValue], s = scatter_width, color = colors[(items, replicate)][0], marker = colors[(items, replicate)][1]))
                        checkBox = 1

                    x_samples.append(xSampleValue)
                ax.scatter(x_samples, y_samples, s = scatter_width, color = colors[(items, replicate)][0], marker = colors[(items, replicate)][1])

    #print pointAndLabelList

    # Setting the axis parameters
    #axis([x_start, x_end, yMin, yMax])

    ax.grid(plot_data.view_grid)
    if plot_data.view_legend:
        plotList = []
        i = 0
        for a in activeAssessorsList:
            #p = Patch(facecolor = colors[(a, s_data.ReplicateList[0])][0])
            #plotList.append(p)

            plotList.append(Line2D([],[], color = colors[(a, s_data.ReplicateList[0])][0], linewidth=5))
            i += 1
        #CircleLegend(fig, [['#FF0000', '#00FF00', '#0000FF'], ['dommer1', 'dommer2', 'dommer3']])
        fig.legend(plotList, activeAssessorsList, 'upper right')

    myTitle = 'Sample line plot: ' + itemID[0]
    if not subplot:
        axes_setup(ax, 'Attributes', 'Score', myTitle, plot_data.limits)
        set_xlabeling(ax, activeAttributesList)
        if len(activeAttributesList) > 7:
            set_xlabeling_rotation(ax, 'vertical')
    else:
        axes_setup(ax, '', '', myTitle, plot_data.limits, font_size=10)

    # These four lines are for setting the maximum-value of the X-axis back
    # to its original value . Check back with code at around line 70
    try:
        plot_data.limits[1] = originalX_AxeValue

    # UnboundLocalError occurs when the number of attributes was set at
    # maximum
    except UnboundLocalError:
        pass

    #update plot-data variables:
    plot_data.point_lables = pointAndLabelList
    plot_data.raw_data = rawDataList
    plot_data.numeric_data = resultList
    plot_data.plot_type = "line_samp"
    plot_data.point_lables_type = 0

    #Frame draw, for standard Matplotlib frame only use show()
    return plot_data



def AssessorLinePlotter(s_data, plot_data, num_subplot=[1,1,1], **kwargs):
    """
    This function generates the line plot for an specific assessor for a given
    sample. The numberof assessors and attributes can be chosen in the
    checkListBoxes in the GUI.

    @type selection: int
    @param selection: Not used in this plotter

    @type drawSettings:     list
    @param drawSettings:    List of settings on how to draw the figure. [grid?, legend?, legend_position, x_y_Limits]

    @type s_data.SparseMatrix:     dictionary
    @param s_data.SparseMatrix:    Complete dictionary type of Matrix with all values

    @type noOfWindows:      integer
    @param noOfWindows:     nteger value for the new window

    @type insideItemID:     pyData
    @param insideItemID:    pyData from wxTree

    @type s_data.AssessorList:     list
    @param s_data.AssessorList:    Complete list of ALL assessors

    @type s_data.ReplicateList:    list
    @param s_data.ReplicateList:   Complete list of ALL replicates

    @type s_data.AttributeList:    list
    @param s_data.AttributeList:   Complete list of ALL attributes

    @type ActiveAssessors:  dictionary
    @param ActiveAssessors: Contains the active/checked assessors

    @type ActiveAttributes:  dictionary
    @param ActiveAttributes: Contains the active/checked attributes
    """
    activeAssessorsList = plot_data.activeAssessorsList
    activeAttributesList = plot_data.activeAttributesList
    itemID = plot_data.tree_path

    # Create a list with active (checked in CheckListBox) attributes
    # that is chronologically sorted as in original file. Just doing
    # .keys() and .sort() is not enough, since only alphabetical order
    # is given.
    plottingSparseMatrix = {}
    assessorPlottingSparseMatrix = {}


    # Check weather the selected item is in the collectedActiveItemsList.
    # If not, an error message is activated.
    if itemID[1] not in activeAssessorsList:
        dlg = wx.MessageDialog(None, 'The assessor is not checked in CheckBox',
                               'Error Message',
                               wx.OK | wx.ICON_INFORMATION)
        dlg.ShowModal()
        dlg.Destroy()

    else:

        # Here a list is created that contains the positions
        # of the active attributes. This is needed in the next
        # step, when the plottings_data.SparseMatrix is created.
        activeAttributeIndexList = []

        for attribute in activeAttributesList:

            positionSpecificAttribute = s_data.AttributeList.index(attribute)
            activeAttributeIndexList.append(positionSpecificAttribute)


        # Here the plottings_data.SparseMatrix is calculated. A flat matrix is also
        # constructed during the process, that makes construction of an "normal" array
        # easier.
        flatMatrixList = []
        for assessor in activeAssessorsList:

            for replicate in s_data.ReplicateList:

                itemToupleKey = (assessor, itemID[0], replicate)

                specificList = []
                for attribute in activeAttributeIndexList:

                    specificList.append(s_data.SparseMatrix[itemToupleKey][attribute])

                plottingSparseMatrix[itemToupleKey] = specificList
                for singleValues in plottingSparseMatrix[itemToupleKey]:
                    flatMatrixList.append(float(singleValues))

        #print flatMatrixList

        # Here the flatMatrixList is converted into the plottingMatrix array.
        plottingMatrix = reshape(array(flatMatrixList, float), (len(plottingSparseMatrix), -1))
        meanVector = average(plottingMatrix, 0)
        dimensions = plottingMatrix.shape


        # Starting generation of the list that contains the data
        # that is shown in "Show Data"
        emptyLine = ['']



        rawDataList = raw_data_grid(s_data, plot_data, active_assessors=[itemID[1]], active_samples=[itemID[0]])

        # Here the plottings_data.SparseMatrix is calculated. A flat matrix is also
        # constructed during the process, that makes construction of an "normal" array
        # easier.
        assessorFlatMatrixList = []
        for replicate in s_data.ReplicateList:

            itemToupleKey = (itemID[1], itemID[0], replicate)

            assessorSpecificList = []
            for attribute in activeAttributeIndexList:

                assessorSpecificList.append(s_data.SparseMatrix[itemToupleKey][attribute])

            assessorPlottingSparseMatrix[itemToupleKey] = assessorSpecificList
            for singleValues in assessorPlottingSparseMatrix[itemToupleKey]:
                assessorFlatMatrixList.append(float(singleValues))

        #print assessorFlatMatrixList

        # Here the assessorFlatMatrixList is converted into the assessorPlottingMatrix array.
        assessorPlottingMatrix = reshape(array(assessorFlatMatrixList, float), (len(assessorPlottingSparseMatrix), -1))
        assessorMeanVector = average(assessorPlottingMatrix, 0)
        assessorDimensions = assessorPlottingMatrix.shape

        #print assessorPlottingMatrix
        #print assessorDimensions


        # If number of activeAttributes is less then full.
        # drawSettings[3][1] conatins the maximum value for the X-axis.
        originalX_AxeValue = plot_data.limits[1]
        if dimensions[1] < len(s_data.AttributeList):
            print 'other scale for x'
            print plot_data.limits
            plot_data.limits[1] = dimensions[1] + 1


        # Finding the maximun and minimum values in the assessorPlottingMatrix
        yMin_values = []
        yMax_values = []
        ySTD_values = []

        for eachAttribute in range(assessorDimensions[1]):
            column = take(assessorPlottingMatrix, (eachAttribute,), 1)
            #print column
            lowestValue = min(column)
            highestValue = max(column)
            deviation = round(std(column), 3)
            yMin_values.append(lowestValue[0])
            yMax_values.append(highestValue[0])
            ySTD_values.append(deviation)


        # Vectors that plot the average values of all assessors
        x_values = arange(1, dimensions[1]+1)
        y_values = meanVector
        y_assessor_values = assessorMeanVector


        # Starting generation of the list that contains the data
        # that is shown in "Show Data"
        resultList = []
        sampleHeaderLine = ['Sample/Assessor: ']
        sampleHeaderLine.extend(itemID)
        resultList.append(sampleHeaderLine)
        resultList.append(emptyLine)
        attributeLineNumericalResults = ['']
        attributeLineNumericalResults.extend(activeAttributesList)
        resultList.append(attributeLineNumericalResults)





        _line = ['PANEL MEAN']
        for x in meanVector:
            _line.append(num2str(x, fmt="%.2f"))
        resultList.append(_line)


        _line = [itemID[1] + ' MEAN']
        for x in assessorMeanVector:
            _line.append(num2str(x, fmt="%.2f"))
        resultList.append(_line)

        _line = ['MIN']
        for x in yMin_values:
            _line.append(num2str(x, fmt="%.2f"))
        resultList.append(_line)

        _line = ['MAX']
        for x in yMax_values:
            _line.append(num2str(x, fmt="%.2f"))
        resultList.append(_line)

        _line = ['STD']
        for x in ySTD_values:
            _line.append(num2str(x, fmt="%.2f"))
        resultList.append(_line)


        replot = False; subplot = plot_data.overview_plot; scatter_width = 35
        if plot_data.fig != None: replot = True
        else: plot_data.fig = Figure(None)
        if subplot: # is subplot
            plot_data.ax = plot_data.fig.add_subplot(num_subplot[0], num_subplot[1], num_subplot[2])
            scatter_width = 15
        else: plot_data.ax = axes_create(0, plot_data.fig)
        ax = plot_data.ax; fig = plot_data.fig

        # Plots the line with average values for all enabled assessors
        ax.plot(x_values, y_values, 'r--')
        ax.plot(x_values, y_assessor_values, 'b-')



        # This plots the vertical lines using the minimum and maximum values from
        # the plottingMatrix
        #for atts in range(dimensions[1]):
        #    ax.vlines([x_values[atts]], [yMin_values[atts]], [yMax_values[atts]], fmt='b')




        vertices = []
        for atts in range(dimensions[1]):
        #ax.vlines([x_values[atts]], [yMin_values[atts]], [yMax_values[atts]], fmt='b')
            vertices.append(((x_values[atts], yMin_values[atts]),(x_values[atts], yMax_values[atts])))

        lc = LineCollection(vertices, colors='#0000FF')
        plot_data.ax.add_collection(lc)

        #print assessorPlottings_data.SparseMatrix


        # The following code handles the labelling for mouse-pointing over
        # certain points in the plot. Implemented by Henning and sligtly
        # modified by Oli.

        #One element in the pointAndLabelList will always contain 3 items [x, y, label]
        pointAndLabelList = []

        #epsilon = 1% of edge length, a cirka diameter of one plot circle, this depends on figure resolution
        epsilon = (plot_data.limits[1]) *0.01
        #the accurate amount of room between each attribute line -1, with plot circle diameter of 1%
        #zero division will not happen, because with no chosen attributes: drawSettings[3][1] = 1
        maxPlotsBesideEachother = int(floor((100/plot_data.limits[1])-1))
        print "Max number of plottings beside eachother: " + str(maxPlotsBesideEachother)




        coloring_type = 0 # assessors
        if "coloring" in plot_data.special_opts:
            if plot_data.special_opts["coloring"] == "samples":
                coloring_type = 1 # samples

                coloring_list = s_data.SampleList

        if coloring_type == 1:
            coloring_list = s_data.SampleList
        else:
            coloring_list = s_data.AssessorList

        colors = assign_colors(coloring_list, s_data.ReplicateList)

        # This plots all the assessor scores in the line plot
        for items in assessorPlottingSparseMatrix:
            #print plottings_data.SparseMatrix[items]
            x_samples = []
            y_samples = []
            for values in range(len(assessorPlottingSparseMatrix[items])):
                #print values
                ySampleValue = float(assessorPlottingSparseMatrix[items][values])
                y_samples.append(ySampleValue)
                xSampleValue = values + 1
                label = activeAttributesList[values] + ': ' + items[2]

                #print xSampleValue, ySampleValue
                xSampleValue = check_point(xSampleValue, ySampleValue, epsilon, pointAndLabelList, maxPlotsBesideEachother)
                pointAndLabelList.append([xSampleValue, ySampleValue, label, 1])
                x_samples.append(xSampleValue)
            ax.scatter(x_samples, y_samples, s = scatter_width, color = colors[(items[coloring_type], items[2])][0], marker = colors[(items[coloring_type], items[2])][1])


        #axis([x_start, x_end, yMin, yMax])
        ax.grid(plot_data.view_grid)

        """
        if plot_data.view_legend:
            plotList = []
            i = 0
            for a in activeAssessorsList:
                p = Patch(facecolor = colors[(a, s_data.ReplicateList[0])][0])
                plotList.append(p)
                i += 1
            #CircleLegend(fig, [['#FF0000', '#00FF00', '#0000FF'], ['dommer1', 'dommer2', 'dommer3']])
            fig.legend(plotList, activeAssessorsList, 'upper right', handlelen = 0.02)
        """



        myTitle = 'Sample line plot: ' + itemID[0] + ', ' + itemID[1]
        if not subplot:
            axes_setup(ax, 'Attributes', 'Score', myTitle, plot_data.limits)
            set_xlabeling(ax, activeAttributesList)
            if len(activeAttributesList) > 7:
                set_xlabeling_rotation(ax, 'vertical')
        else: axes_setup(ax, '', '', myTitle, plot_data.limits, font_size=10)
        # These four lines are for setting the maximum-value of the X-axis back
        # to its original value . Check back with code at around line 70
        try:
            plot_data.limits[1] = originalX_AxeValue

        # UnboundLocalError occurs when the number of attributes was set at
        # maximum
        except UnboundLocalError:
            pass

        #update plot-data variables:
        plot_data.point_lables = pointAndLabelList
        plot_data.raw_data = rawDataList
        plot_data.numeric_data = resultList
        plot_data.plot_type = "line_ass"
        plot_data.point_lables_type = 0

        #Frame draw, for standard Matplotlib frame only use show()
        return plot_data


def ReplicateLinePlotter(s_data, plot_data, **kwargs):
    """
    This function generates the line plot for a specific replicate of a
    given assessor for a given sample. The numberof assessors and attributes
    can be chosen in the checkListBoxes in the GUI.

    @type drawSettings:     list
    @param drawSettings:    List of settings on how to draw the figure. [grid?, legend?, legend_position, x_y_Limits]

    @type s_data.SparseMatrix:     dictionary
    @param s_data.SparseMatrix:    Complete dictionary type of Matrix with all values

    @type noOfWindows:      integer
    @param noOfWindows:     nteger value for the new window

    @type insideItemID:     pyData
    @param insideItemID:    pyData from wxTree

    @type s_data.AssessorList:     list
    @param s_data.AssessorList:    Complete list of ALL assessors

    @type s_data.ReplicateList:    list
    @param s_data.ReplicateList:   Complete list of ALL replicates

    @type s_data.AttributeList:    list
    @param s_data.AttributeList:   Complete list of ALL attributes

    @type ActiveAssessors:  dictionary
    @param ActiveAssessors: Contains the active/checked assessors

    @type ActiveAttributes:  dictionary
    @param ActiveAttributes: Contains the active/checked attributes
    """

    activeAssessorsList = plot_data.activeAssessorsList
    activeAttributesList = plot_data.activeAttributesList
    itemID = plot_data.tree_path

    # Create a list with active (checked in CheckListBox) attributes
    # that is chronologically sorted as in original file. Just doing
    # .keys() and .sort() is not enough, since only alphabetical order
    # is given.
    plottingSparseMatrix = {}
    replicatePlottingSparseMatrix = {}

    replot = False
    if plot_data.fig != None: replot = True

    # Check weather the selected item is in the collectedActiveItemsList.
    # If not, an error message is activated.
    if itemID[1] not in activeAssessorsList:
        dlg = wx.MessageDialog(None, 'The assessor is not checked in CheckBox',
                               'Error Message',
                               wx.OK | wx.ICON_INFORMATION)
        dlg.ShowModal()
        dlg.Destroy()
        return

    else:

        # Here a list is created that contains the positions
        # of the active attributes. This is needed in the next
        # step, when the plottings_data.SparseMatrix is created.
        activeAttributeIndexList = []
        for attribute in activeAttributesList:

            positionSpecificAttribute = s_data.AttributeList.index(attribute)
            activeAttributeIndexList.append(positionSpecificAttribute)


        # Here the plottings_data.SparseMatrix is calculated. A flat matrix is also
        # constructed during the process, that makes construction of an "normal" array
        # easier.
        flatMatrixList = []
        for assessor in activeAssessorsList:

            for replicate in s_data.ReplicateList:

                itemToupleKey = (assessor, itemID[0], replicate)

                specificList = []
                for attribute in activeAttributeIndexList:

                    specificList.append(s_data.SparseMatrix[itemToupleKey][attribute])

                plottingSparseMatrix[itemToupleKey] = specificList
                for singleValues in plottingSparseMatrix[itemToupleKey]:
                    flatMatrixList.append(float(singleValues))

        #print flatMatrixList

        # Here the flatMatrixList is converted into the plottingMatrix array.
        plottingMatrix = reshape(array(flatMatrixList, float), (len(plottingSparseMatrix), -1))
        meanVector = average(plottingMatrix, 0)
        dimensions = plottingMatrix.shape


        # The specific part for the replicate
        replicateFlatMatrixList = []

        # Here the plottings_data.SparseMatrix is calculated. A flat matrix is also
        # constructed during the process, that makes construction of an "normal" array
        # easier.
        itemToupleKey = (itemID[1], itemID[0], itemID[2])
        replicateSpecificList = []
        for attribute in activeAttributeIndexList:

            replicateSpecificList.append(s_data.SparseMatrix[itemToupleKey][attribute])

        replicatePlottingSparseMatrix[itemToupleKey] = replicateSpecificList
        for singleValues in replicatePlottingSparseMatrix[itemToupleKey]:
            replicateFlatMatrixList.append(float(singleValues))

        #print replicateFlatMatrixList

        # Here the replicateFlatMatrixList is converted into the replicatePlottingMatrix array.
        replicatePlottingMatrix = reshape(array(replicateFlatMatrixList, float), (len(replicatePlottingSparseMatrix), -1))
        replicateMeanVector = average(replicatePlottingMatrix, 0)
        replicateDimensions = replicatePlottingMatrix.shape

        #print replicatePlottingMatrix
        #print replicateDimensions



        emptyLine = ['']

        rawDataList = raw_data_grid(s_data, plot_data, active_assessors=[itemID[1]], active_samples=[itemID[0]], active_replicates=[itemID[2]])


        # Starting generation of the list that contains the data
        # that is shown in "Show Data"
        resultList = []
        sampleHeaderLine = ['Sample/Assessor/Replicate: ']
        sampleHeaderLine.extend(itemID)
        resultList.append(sampleHeaderLine)
        resultList.append(emptyLine)
        attributeLineNumericalResults = ['']
        attributeLineNumericalResults.extend(activeAttributesList)
        resultList.append(attributeLineNumericalResults)


        # Adding the replicate value and mean value over panel

        _line = ['PANEL MEAN']
        for x in meanVector:
            _line.append(num2str(x, fmt="%.2f"))
        resultList.append(_line)


        _line = [itemID[1]]
        for x in replicateMeanVector:                   # 2012-06-18: attributeValues does not exist. What is correct here?????
            _line.append(num2str(x, fmt="%.2f")) 
        resultList.append(_line)



        # If number of activeAttributes is less then full.
        # drawSettings[3][1] conatins the maximum value for the X-axis.
        originalX_AxeValue = plot_data.limits[1]
        if dimensions[1] < len(s_data.AttributeList):
            print 'other scale for x'
            print plot_data.limits
            print '\n'
            plot_data.limits[1] = dimensions[1] + 1

        if not replot:
            plot_data.fig = Figure(None)

        #axes positioning
        plot_data.ax = axes_create(0, plot_data.fig)
        ax = plot_data.ax; fig = plot_data.fig

        # Vectors that plot the average values of all assessors
        x_values = arange(1, replicateDimensions[1]+1)
        y_values = meanVector
        y_replicate_values = replicateMeanVector


        # Plots the line with average values for all enabled assessors
        ax.plot(x_values, y_values, 'r--')
        ax.plot(x_values, y_replicate_values, 'b-')
        x_values_rep = []
        y_values_rep = []


        # The following code handles the labelling for mouse-pointing over
        # certain points in the plot. Implemented by Henning and sligtly
        # modified by Oli.

        #One element in the pointAndLabelList will always contain 3 items [x, y, label]
        pointAndLabelList = []

        #epsilon = 1% of edge length, a cirka diameter of one plot circle, this depends on figure resolution
        epsilon = (plot_data.limits[1]) *0.01
        #the accurate amount of room between each attribute line -1, with plot circle diameter of 1%
        #zero division will not happen, because with no chosen attributes: drawSettings[3][1] = 1
        maxPlotsBesideEachother = int(floor((100/plot_data.limits[1])-1))
        print "Max number of plottings beside eachother: " + str(maxPlotsBesideEachother)


        colors = assign_colors(s_data.AssessorList, s_data.ReplicateList)

        # This plots the assessor's replicate scores
        for values in range(len(plottingSparseMatrix[itemToupleKey])):
            #print values
            ySampleValue = float(plottingSparseMatrix[itemToupleKey][values])
            xSampleValue = values + 1

            #print xsampleValue, ySampleValue
            x_values_rep.append(xSampleValue)
            y_values_rep.append(ySampleValue)
            xSampleValue = check_point(xSampleValue, ySampleValue, epsilon, pointAndLabelList, maxPlotsBesideEachother)
            pointAndLabelList.append([xSampleValue, ySampleValue, activeAttributesList[values], 0])
            ax.scatter([xSampleValue], [ySampleValue], s = 30, color = colors[(itemID[1], itemID[2])][0], marker = colors[(itemID[1], itemID[2])][1])

        #lines between the replicate scores
        #ax.plot(x_values_rep, y_values_rep , color='b')


        #axis([x_start, x_end, yMin, yMax])
        ax.grid(plot_data.view_grid)
        myTitle = 'Sample line plot: ' + itemID[0] + ', ' + itemID[1] + ', ' + itemID[2]
        axes_setup(ax, 'Attributes', 'Score', myTitle, plot_data.limits)

        # These four lines are for setting the maximum-value of the X-axis back
        # to its original value . Check back with code at around line 70
        try:
            plot_data.limits[1] = originalX_AxeValue

        # UnboundLocalError occurs when the number of attributes was set at
        # maximum
        except UnboundLocalError:
            pass


        set_xlabeling(ax, activeAttributesList)
        if len(activeAttributesList) > 7:
            set_xlabeling_rotation(ax, 'vertical')

        #update plot-data variables:
        plot_data.point_lables = pointAndLabelList
        plot_data.raw_data = rawDataList
        plot_data.numeric_data = resultList
        plot_data.plot_type = "line_rep"
        plot_data.point_lables_type = 0

        #Frame draw, for standard Matplotlib frame only use show()
        return plot_data



def SampleLineOverviewPlotter(s_data, plot_data, **kwargs):
    """
    Sample Line Overview Plot
    """

    #axes positioning

    """
    num_plots = len(s_data.SampleList)
    num_edge = int(ceil(sqrt(num_plots)))
    #print num_edge

    sampList = copy.copy(s_data.SampleList)
    item = []
    item.append(sampList[0])

    progress = Progress(None)
    progress.set_gauge(value=0, text="Calculating...\n")
    part = int(round(100/num_plots)); val = part

    res = SampleLinePlotter(drawSettings, item, s_data, activeAssessorsList, activeAttributesList, activeSamplesList, num_subplot=[num_edge, num_edge, 1])
    txt = sampList[0] + " done\n"
    progress.set_gauge(value=val, text=txt)

    del sampList[0]

    fig = res[0]
    num = 2
    for samp_plot in sampList:
        item = []
        item.append(samp_plot)
        SampleLinePlotter(drawSettings, item, s_data, activeAssessorsList, activeAttributesList, activeSamplesList, fig=fig, num_subplot=[num_edge, num_edge, num])
        num += 1
        txt = samp_plot + " done\n"
        val += part
        progress.set_gauge(value=val, text=txt)

    progress.Destroy()

    if drawSettings[1]: r = 0.8 # has legend
    else: r = 0.95
    fig.subplots_adjust(left=0.05, bottom=0.05, right=r, top=0.95, wspace=0.15, hspace=0.25)

    return res
    """

    itemID_list = [] # takes part in what to be plotted
    for samp in s_data.SampleList:
        itemID_list.append([samp])
    return OverviewPlotter(s_data, plot_data, itemID_list, SampleLinePlotter, s_data.SampleList)



def AssessorLineOverviewPlotter(s_data, plot_data, **kwargs):
    """
    Assessor Line Overview Plot
    """
    itemID_list = [] # takes part in what to be plotted
    for ass in plot_data.activeAssessorsList:
        itemID_list.append([plot_data.tree_path[0], ass])
    return OverviewPlotter(s_data, plot_data, itemID_list, AssessorLinePlotter, plot_data.activeAssessorsList)




"""
    # Forsok paa optimalisering av SampleLinePlotter:


    num_of_att = len(activeAttributesList)
    num_of_ass = len(activeAssessorsList)
    num_of_rep = len(s_data.ReplicateList)


    scores_matrix = zeros((num_of_ass*num_of_rep, num_of_att), float)


    y = 0
    for rep in s_data.s_data.ReplicateList:
        for ass in activeAssessorsList:
            x = 0
            for att in activeAttributesList:
                att_index = s_data.AttributeList.index(att)
                scores_matrix[y,x] = s_data.SparseMatrix[(ass,itemID[0],rep)][att_index]
                x += 1
            y += 1



    y = 0
    for rep in s_data.s_data.ReplicateList:
        for ass in activeAssessorsList:
            for att_index in range(num_of_att):
                y_samp = scores_matrix[y, att_index]
                xSampleValue = check_point(x_values[att_index], y_samp, epsilon, pointAndLabelList, maxPlotsBesideEachother)
                ax.scatter([xSampleValue], [y_samp], s = scatter_width, color = colors[(ass, rep)][0], marker = colors[(ass, rep)][1])
                label = ass + ' (' + activeAttributesList[att_index] + ': ' + rep +')'
                pointAndLabelList.append([xSampleValue, y_samp, label, 1])
            y += 1
"""
