#!/usr/bin/env python

from Plot_Tools import *



def numerical_data_add_average_mat(resultList, average_mat, activeAttributesList, activeSamplesList):
 
    headerLine = ['Averaged data:']
    resultList.append(headerLine)
    attributesLine = ['Samples']
    attributesLine.extend(activeAttributesList)
    resultList.append(attributesLine)
        
    # Fill in the average-matrix
    for sample in range(len(activeSamplesList)):
        sampleLine = [activeSamplesList[sample]]
        valuesArray = average_mat[sample,:]
        for value in valuesArray:
            sampleLine.append(num2str(value, fmt="%.2f"))
        resultList.append(sampleLine)
    return resultList




def PCA_plotter(s_data, plot_data, num_subplot=[1,1,1], selection=0, pc_x=0, pc_y=1):
    """
    This is the PCA plot function. It plots the PCA scores of the averaged 
    matrix (over assessors and replicates).
    

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
    
    @type sampleList:       list
    @param sampleList:      Contains all samples from original data set
    
    @type s_data.ReplicateList:    list
    @param s_data.ReplicateList:   Contains all replicates original from data set
    
    @type s_data.AttributeList:    list
    @param s_data.AttributeList:   Contains all attributes original from data set
    
    @type itemID[0]:     list
    @param itemID[0]:    Conatins which item in the tree was double-clicked
    
    ActiveSample_list: Is created from ActiveAssessors (dictionary) and is
    used for iterating through the active asessors
    ActiveSample_list: list
    """

    activeAssessorsList = plot_data.activeAssessorsList[:]
    activeAttributesList = plot_data.activeAttributesList[:]
    activeSamplesList = plot_data.activeSamplesList[:]
    itemID = plot_data.tree_path
    interact = False # interactivity on or off
    
    title_pca_type = ""
    if selection == 1: 	title_pca_type = "Standardized: "
    else: 		title_pca_type = "Original: "
    
    #print itemID[0], ' was selected'
    
    if len(activeAssessorsList) < 1: #no active assessors
        dlg = wx.MessageDialog(None, 'No assessors are active in CheckBox',
                               'Error Message',
                               wx.OK | wx.ICON_INFORMATION)
        dlg.ShowModal()
        dlg.Destroy()
        return
    if len(activeAttributesList) < 3: #no active assessors
        dlg = wx.MessageDialog(None, 'There must be a minimum of 3 attributes.',
                               'Error Message',
                               wx.OK | wx.ICON_INFORMATION)
        dlg.ShowModal()
        dlg.Destroy()
        return
    if len(activeSamplesList) < 3: #no active samples
        dlg = wx.MessageDialog(None, 'There must be a minimum of 3 samples.',
                               'Error Message',
                               wx.OK | wx.ICON_INFORMATION)
        dlg.ShowModal()
        dlg.Destroy()
        return    
    
    # Construction of consensus matrix depending on which tab is active
    numberOfAssessors = len(activeAssessorsList)
    numberOfAttributes = len(activeAttributesList)
    numberOfSamples = len(activeSamplesList)
    numberOfReplicates = len(s_data.ReplicateList)
    pointAndLabelList = []
 
    
    # 'Standardized' tab is active then standardize data, calculate average
    # and compute the required values
    if selection == 1:
        print 'do standardisation'
        
        # Construct a list that contains the data of each active assessor.
        # First construct a list (oneAssessorList) for each assessor that 
        # contains all the objects (floatRow). Then convert it so array. 
        # In the end, put the array in to another list (allAssessorsList).
        allAssessorsList = []            
        for assessor in activeAssessorsList:
            oneAssessorList = []
            
            for sample in activeSamplesList:
                
                for replicate in s_data.ReplicateList:
                    dataRow = s_data.SparseMatrix[(assessor, sample, replicate)]
                    
                    # Here all strings from s_data.SparseMatrix are converted to floats
                    floatRow = []
                    for eachValue in dataRow:
                        floatRow.append(float(eachValue))

                    # Leave out the values of those attributes that are not
                    # selected
                    newFloatRow = []
                    for attribute in s_data.AttributeList:
                        if attribute in activeAttributesList:
                            newFloatRow.append(floatRow[s_data.AttributeList.index(attribute)])
                    
                    oneAssessorList.append(newFloatRow)
            
            # Convert to array and then append to list
            allAssessorsList.append(array(oneAssessorList))
        
            
        # Now check each assessor for STD=0
        # by calculating a matrix that contains the STD's for each
        # assessor. Also averages for each assessor are calculated.
        STDmatrix = zeros((1, len(activeAttributesList)), float)
        #print STDmatrix
        meanMatrix = zeros((1, len(activeAttributesList)), float)
        
        leaveOutAtts = []
        for assessor in allAssessorsList:
            
            check = array(STD(assessor, 0), copy=False)
            assMean = array(average(assessor, 0), copy=False)
            #ipshell()
            STDmatrix = vstack((STDmatrix, check))
            meanMatrix = vstack((meanMatrix, assMean))
            
            newCheck = check.tolist()
            
            position = 0
            for item in newCheck:
                
                if item == 0.0:
                    
                    if position not in leaveOutAtts:
                        leaveOutAtts.append(position)
                position += 1
        
        leaveOutAtts.sort()
        leaveOutAttributes = []
        for badAtt in leaveOutAtts:
            leaveOutAttributes.append(activeAttributesList[badAtt])
        
        # Leave out the first row that has only zeros
        STDarray = STDmatrix[1:,:].copy()
        meanMatrix = meanMatrix[1:,:].copy()
        
        
        # Now that we know which attributes give STD=0 for at least
        # one assessor we do the following:
        # 1. Inform user about it with a message box
        # 2. Create a new array with STD's that has no STD=0 
        #   dim (activeAssors x (activeAttributes - badAttributes))
        
        # Point 1.
        if len(leaveOutAttributes) > 0:
            messagePart1 = 'The following attributes were left out of the analysis because \nfor one or more assessors the standard deviation is 0: \n'
            
            messagePart2 = leaveOutAttributes[0]
            for atts in leaveOutAttributes:
                if messagePart2 == atts:
                    pass
                else:
                    messagePart2 = messagePart2 + ', ' + atts
            
            messagePart3 = '\n\nPlease uncheck these attributes to avoid this message.'
                
            message = messagePart1 + messagePart2 + messagePart3
            
            dlg = wx.MessageDialog(None, message,
                               'Important information',
                               wx.OK | wx.ICON_INFORMATION)
            dlg.ShowModal()
            dlg.Destroy()
        
        
        # Point 2.
        realSTDarray = zeros((1, len(activeAssessorsList)), float)
        realAssMeanArray = zeros((1, len(activeAssessorsList)), float)
                    
        for attribute in range(len(activeAttributesList)):
            checkCol = STDarray[:, attribute]
            checkCol2 = meanMatrix[:, attribute]
            #ipshell()
            if 0 in checkCol:
                #print 'zero in column ', attribute
                pass
                
            else:
                realSTDarray = vstack((realSTDarray, checkCol))
                realAssMeanArray = vstack((realAssMeanArray, checkCol2))
        
        
        nextSTDarray = realSTDarray[1:,:].copy()
        finalSTDarray = transpose(nextSTDarray)
        
        nextAssMeanArray = realAssMeanArray[1:,:].copy()
        finalAssMeanArray = transpose(nextAssMeanArray)
        
        #print finalSTDarray
        #print
        #print finalAssMeanArray
        
        for attribute in leaveOutAttributes:
            activeAttributesList.remove(attribute)
        #print activeAttributesList
            
    
    elif selection == 0:
        print 'do average'
        
    # Constructing average matrices:
    # - sampleAverageMatrix for each sample
    # - averageMatrix for all samples
    # - assessorAverageMatrix for each assessor
    rowsAverageMatrix = len(activeSamplesList)
    columns = len(activeAttributesList)
    replicates = len(s_data.ReplicateList)
    
    rowsSampleAverageMatrix = replicates * len(activeAssessorsList)
    averageMatrix = zeros((rowsAverageMatrix, columns), float)
    
    
    for sample in activeSamplesList:
        
        constructSampleAverageMatrix = zeros((1, columns), float)
        for assessor in activeAssessorsList:
            
                for replicate in s_data.ReplicateList:
                    
                    valueCollectionList = []
                    for attribute in activeAttributesList:
                        if selection == 1: # average std
                            value = float(s_data.SparseMatrix[(assessor,sample,replicate)][s_data.AttributeList.index(attribute)])
                            STDvalue = finalSTDarray[activeAssessorsList.index(assessor), activeAttributesList.index(attribute)]
                            averValue = finalAssMeanArray[activeAssessorsList.index(assessor), activeAttributesList.index(attribute)]
                            calc = (value - averValue) / STDvalue
                            #print value, averValue,STDvalue, calc
                            
                            #print finalSTDarray[activeAssessorsList.index(assessor), activeAttributesList.index(attribute)]
                            valueCollectionList.append((value - averValue) / STDvalue)
                        
                        elif selection == 0: # average original
                            value = float(s_data.SparseMatrix[(assessor,sample,replicate)][s_data.AttributeList.index(attribute)])
                            valueCollectionList.append(value)
                        
                    oneMatrixRow = array(valueCollectionList)
                        
                        
                    #print '*******************************'
                    constructSampleAverageMatrix = vstack((constructSampleAverageMatrix, oneMatrixRow))
        
        # Remove first row that contains only zeros
        sampleAverageMatrix = constructSampleAverageMatrix[1:,:].copy()
        #print sampleAverageMatrix
        
        # Now calculate average for that sample and copy values
        # in to averageMatrix
        sampleAverage = average(sampleAverageMatrix, 0)
        averageMatrix[activeSamplesList.index(sample)] = sampleAverage.copy()
    
    averageMatrixForAnalysis = averageMatrix.copy()
    
    #ipshell()
    
    # Do PCA and get all results
    #PCAanalysis = PCA(averageMatrixForAnalysis.copy(), 1)
    #scores = PCAanalysis.GetScores()
    #loadings = PCAanalysis.GetLoadings()
    #corrLoadings = PCAanalysis.GetCorrelationLoadings()
    #transCorrLoadings = transpose(corrLoadings)
    #explVar = PCAanalysis.GetExplainedVariances()
    scores, loadings, explVar = PCA(averageMatrixForAnalysis)
    explVar = list(explVar)
    corrLoadings = CorrelationLoadings(averageMatrixForAnalysis, scores)
    transCorrLoadings = transpose(corrLoadings)      
    
    
    font = {'family'     : 'sans-serif',
                    'color'      : 'k',
                    'weight' : 'normal',
                    'size'   : 11,
                    }
    
    # Starting generation of the list that contains the raw data
    # that is shown in "Raw Data" when pushing the button in the plot
    
    
    rawDataList = raw_data_grid(s_data, plot_data)
    
    
    resultList = []
    emptyLine = ['']
    
    # Continue building resultList
    # Limiting PC's in 'Numeric Results' to 10
    [PCs, activeAttributes] = shape(corrLoadings)
    [Samples, PCs] = shape(scores)
    
    maxPCs = 10
    [Samples, PCs] = shape(scores)
    if PCs < maxPCs:
        maxPCs = PCs
    
    
    #print itemID[0]
    
    # Figure
    aspect = plot_data.aspect; legend = 0
    if itemID[0] == "PCA Explained Variance": aspect = 'auto'
    if itemID[0] == "Spiderweb Plot": legend = plot_data.view_legend
    
    replot = False; subplot = plot_data.overview_plot
    if plot_data.fig != None: replot = True
    else: plot_data.fig = Figure(None)
    if subplot: # is subplot
        plot_data.ax = plot_data.fig.add_subplot(num_subplot[0], num_subplot[1], num_subplot[2], aspect=aspect)
    else: plot_data.ax = axes_create(legend, plot_data.fig, aspect=aspect)
    ax = plot_data.ax; fig = plot_data.fig    
    
    # for choice: PCA Scores
    # **********************
    if itemID[0] == u'PCA Scores':
        # This constructs the resultList that shows the sample scores
        # in 'Show Data'
        
        interact = True

        numerical_data_add_average_mat(resultList, averageMatrix, activeAttributesList, activeSamplesList)
        
        resultList.append(emptyLine)
        resultList.append(emptyLine)
        resultList.append(emptyLine)
        
        
        #headerLine = ['PCA scores']
        #resultList.append(headerLine)
        #resultList.append(emptyLine)
        
        matrixHeaderLine = ['']
        
        
        numerical_data_add_scores(scores, activeSamplesList, maxPCs, resultList)
       
        
        
        resultList.append(emptyLine)
        resultList.append(emptyLine)
        resultList.append(emptyLine)
        
        
        headerExplainedVariance = ['EXPLAINED VARIANCE']
        resultList.append(headerExplainedVariance)
        
        varianceLine = ['']
        
        for variance in explVar:
            #print type(explVar)
            #print explVar.index(variance)
            if explVar.index(variance) == maxPCs:
                break
            value = str(round(variance * 100, 1)) + '%'
            varianceLine.append(value)
        
        resultList.append(varianceLine)
        
        
        # Here the construction of the score plot starts
        # -----------------------------------------------------

        ax.grid(plot_data.view_grid)
        
 	# Get the first and second column from the scores matrix
        scoresXCoordinates = take(scores, (pc_x,), 1)
        scoresYCoordinates = take(scores, (pc_y,), 1)
                
        # Catch max and min values in PC1 and PC2 scores
        # for defining axis-limits in the common scores plot.
        x_max = ceil(max(scoresXCoordinates))
        x_min = floor(min(scoresXCoordinates))
                
        y_max = ceil(max(scoresYCoordinates))
        y_min = floor(min(scoresYCoordinates))
                
        # Defining the titles, axes names, etc
        myTitle = title_pca_type + 'PCA scores'
        xAx = 'PC'+str(pc_x+1)+' (' + str(round(explVar[pc_x] * 100, 1)) + '%)'
        yAx = 'PC'+str(pc_y+1)+' (' + str(round(explVar[pc_y] * 100, 1)) + '%)'
                
        axes_setup(ax, xAx, yAx, myTitle, [x_min, x_max, y_min, y_max])
        
        scores_x = []
        for element in scoresXCoordinates:
            scores_x.append(element[0])
        #print scoresXCoordinates; print scores_x
        scores_y = []
        for element in scoresYCoordinates: 
            scores_y.append(element[0])
        #print scoresYCoordinates; print scores_y
        
        ax.scatter(scores_x, scores_y, s=25, c='b', marker='s')
        
        #ax.plot([x_min, x_max], [0, 0], 'b--')
        #ax.plot([0, 0], [y_min, y_max], 'b--')
        #axes_setup(ax, xAx, yAx, myTitle, [x_min, x_max, y_min, y_max])
        
        lims = []
        xlims = ax.get_xlim()
	ylims = ax.get_ylim()
	lims.append(xlims[0]); lims.append(xlims[1])
	lims.append(ylims[0]); lims.append(ylims[1])
	
	map(lambda x: round(x*10)/10.0, lims) # maps func(x)=round(x*10)/10.0 for all elements in list
	
	ax.plot([lims[0], lims[1]], [0, 0], 'b--')
        ax.plot([0, 0], [lims[2], lims[3]], 'b--')
        
        axes_setup(ax, xAx, yAx, myTitle, lims)
        
        
        for sample in range(len(activeSamplesList)):
            
            textXCoord = scoresXCoordinates[sample] + (x_max + abs(x_min)) * 0.015
            textYCoord = scoresYCoordinates[sample] - (y_max + abs(y_min)) * 0.01
            
            #print activeSamplesList[sample], textXCoord, textYCoord
            
            
            ax.text(textXCoord[0], textYCoord[0], activeSamplesList[sample], font)
            pointAndLabelList.append([scoresXCoordinates[sample], scoresYCoordinates[sample], "PCA Scores: " + activeSamplesList[sample], [activeSamplesList[sample]] ])
    
    
    
    # for choice: PCA Loadings
    # ************************
    elif itemID[0] == u'PCA Loadings':
        # This constructs the resultList that shows the sample scores
        # in 'Show Data'
        
        
        numerical_data_add_average_mat(resultList, averageMatrix, activeAttributesList, activeSamplesList)
        
        
        
        resultList.append(emptyLine)
        resultList.append(emptyLine)
        resultList.append(emptyLine)
        
        matrixHeaderLine = ['']
        
        numerical_data_add_loadings(loadings, activeAttributesList, maxPCs, resultList)
           
        resultList.append(emptyLine)
        resultList.append(emptyLine)
        resultList.append(emptyLine)


        
        explVarHeaderLine = ['']
        
        for PC in range(1, maxPCs + 1):
            columnHeader = 'PC ' + str(PC)
            explVarHeaderLine.append(columnHeader)        
        
        headerExplainedVariance = ['EXPLAINED VARIANCE:']
        resultList.append(headerExplainedVariance)
        resultList.append(explVarHeaderLine)
        
        varianceLine = ['']
        
        for variance in explVar:
            #print type(explVar)
            #print explVar.index(variance)
            if explVar.index(variance) == maxPCs:
                break
            value = str(round(variance * 100, 1)) + '%'
            varianceLine.append(value)
        
        resultList.append(varianceLine)
    
        
        # Here the construction of the score plot starts
        # -----------------------------------------------------

        ax.grid(plot_data.view_grid)
        
        # Get the first and second column from the scores matrix
        loadingsXCoordinates = loadings[pc_x,:].copy()
        loadingsYCoordinates = loadings[pc_y,:].copy()
                
        # Catch max and min values in PC1 and PC2 scores
        # for defining axis-limits in the common scores plot.
        x_max = ceil(max(loadingsXCoordinates))
        x_min = floor(min(loadingsXCoordinates))
                
        y_max = ceil(max(loadingsYCoordinates))
        y_min = floor(min(loadingsYCoordinates))
                
        # Defining the titles, axes names, etc
        myTitle = title_pca_type + 'PCA loadings'
        xAx = 'PC'+str(pc_x+1)+' (' + str(round(explVar[pc_x] * 100, 1)) + '%)'
        yAx = 'PC'+str(pc_y+1)+' (' + str(round(explVar[pc_y] * 100, 1)) + '%)'               
         
        ax.scatter(loadingsXCoordinates, loadingsYCoordinates, s=25, c='r', marker='s')
        
        lims = []
        xlims = ax.get_xlim()
	ylims = ax.get_ylim()
	lims.append(xlims[0]); lims.append(xlims[1])
	lims.append(ylims[0]); lims.append(ylims[1])
	
	map(lambda x: round(x*10)/10.0, lims) # maps func(x)=round(x*10)/10.0 for all elements in list
	
	ax.plot([lims[0], lims[1]], [0, 0], 'b--')
        ax.plot([0, 0], [lims[2], lims[3]], 'b--')
        
        axes_setup(ax, xAx, yAx, myTitle, lims)
        
        for attribute in range(len(activeAttributesList)):
            
            textXCoord = loadingsXCoordinates[attribute] + (x_max + abs(x_min)) * 0.015
            textYCoord = loadingsYCoordinates[attribute] - (y_max + abs(y_min)) * 0.01
            
            #print activeAttributesList[attribute], textXCoord, textYCoord
            
            ax.text(textXCoord, textYCoord, 
                    activeAttributesList[attribute],
                    font)
            pointAndLabelList.append([loadingsXCoordinates[attribute], loadingsYCoordinates[attribute], "PCA Loadings: " + activeAttributesList[attribute]])



    # for choice: PCA correlation loadings
    # ************************************
    elif itemID[0] == u'PCA Correlation Loadings':
        
        # Create figure for correlation loadings plot
        # -------------------------------------------

        ax.grid(plot_data.view_grid)
        
        # Create circles and plot them
        t = arange(0.0, 2*pi, 0.01)
        
        # Compuing the outer circle
        xcords = cos(t)
        ycords = sin(t)
        
        # Plotting outer circle
        ax.plot(xcords, ycords, 'b-')
        
        # Computing inner circle
        xcords50percent = 0.707 * cos(t)
        ycords50percent = 0.707 * sin(t)
        
        # Plotting inner circle
        ax.plot(xcords50percent, ycords50percent, 'b-')
        
        # Plotting the correlation loadings
        # Using 'scatter' instead of 'plot', since this allows sizable points
        # in plot
        xCorrLoadings = corrLoadings[pc_x]
        yCorrLoadings = corrLoadings[pc_y]
        
        ax.scatter(xCorrLoadings, yCorrLoadings, s=10, c='w', marker='o')
        
        textXCoord = xCorrLoadings + 0.02
        textYCoord = yCorrLoadings - 0.022
        
        font = {'family'     : 'sans-serif',
                'color'      : 'k',
                'weight' : 'normal',
                'size'   : 13,
                }
        
        # Plot label of each variable
        for coords in range(len(activeAttributesList)):
            #print activeAttributesList[coords]
            ax.text(textXCoord[coords], textYCoord[coords], 
                    activeAttributesList[coords],
                            font)
        
        
        # Defining the titles, axes names, etc
        myTitle = title_pca_type + 'PCA Correlation loadings'
        xAx = 'PC'+str(pc_x+1)+' (' + str(round(explVar[pc_x] * 100, 1)) + '%)'
        yAx = 'PC'+str(pc_y+1)+' (' + str(round(explVar[pc_y] * 100, 1)) + '%)'
                
        axes_setup(ax, xAx, yAx, myTitle, [-1, 1, -1, 1])
                
        matrixHeaderLine = ['']
                
        #for points and labels:
        xCorrs = corrLoadings[pc_x]
        yCorrs = corrLoadings[pc_y]
        for i in range(len(xCorrs)):
            #pointAndLabelList.append([xCorrs[i],yCorrs[i], activeAttributesList[i+1]])
            pointAndLabelList.append([xCorrs[i],yCorrs[i], activeAttributesList[i]])
            
        
        
        numerical_data_add_loadings(corrLoadings, activeAttributesList, maxPCs, resultList, header_txt='CORRELATION LOADINGS:')
        
        
        resultList.append(emptyLine)
        resultList.append(emptyLine)
        resultList.append(emptyLine)
        
        
        explVarHeaderLine = ['']
        
        for PC in range(1, maxPCs + 1):
            columnHeader = 'PC ' + str(PC)
            explVarHeaderLine.append(columnHeader)
        
        
        headerExplainedVariance = ['EXPLAINED VARIANCE:']
        resultList.append(headerExplainedVariance)
        resultList.append(explVarHeaderLine)
        
        varianceLine = ['']
        
        for variance in explVar:
            #print type(explVar)
            #print explVar.index(variance)
            if explVar.index(variance) == maxPCs:
                break
            value = str(round(variance * 100, 1)) + '%'
            varianceLine.append(value)
        
        resultList.append(varianceLine)
        
    
    
    # for choice: PCA explaned variance
    # ************************************
    elif itemID[0] == u'PCA Explained Variance':
        
        # Create figure for correlation loadings plot
        # -------------------------------------------

        ax.grid(plot_data.view_grid)
        
        # Defining the titles, axes names, etc
        myTitle = title_pca_type + 'PCA explained variance'
        xAx = '# of principal components'
        yAx = 'Explained variance [%]'
        
        axes_setup(ax, xAx, yAx, myTitle, [0, maxPCs, 0, 100])
        
        # Calculate cumulative explained variance for plot
        cumulativeExplVar = [0]
        for var in range(0, maxPCs):
            cumVar = cumulativeExplVar[-1] + (explVar[var] * 100)
            cumulativeExplVar.append(cumVar)
        
        ax.plot(cumulativeExplVar, 'b-')
        
        _range = arange(maxPCs+1)
        ax.set_xticks(_range)
        
        
        numerical_data_add_average_mat(resultList, averageMatrix, activeAttributesList, activeSamplesList)
        

        resultList.append(emptyLine)
        resultList.append(emptyLine)
        resultList.append(emptyLine)
        
        matrixHeaderLine = ['']
        
        for PC in range(1, maxPCs + 1):
            columnHeader = 'PC ' + str(PC)
            matrixHeaderLine.append(columnHeader)
        
        headerExplainedVariance = ['EXPLAINED VARIANCE']
        resultList.append(headerExplainedVariance)
        resultList.append(emptyLine)
        resultList.append(matrixHeaderLine)
        
        varianceLine = ['expl. var']
        
        for variance in explVar:
            #print type(explVar)
            #print explVar.index(variance)
            if explVar.index(variance) == maxPCs:
                break
            value = str(round(variance * 100, 1)) + '%'
            varianceLine.append(value)
        
        resultList.append(varianceLine)
        
        cumulativeLine = ['cumulative']
        # Get rid of the zero-value in first position
        # that has been used for plotting line (see above)
        del cumulativeExplVar[0]
        for variance in cumulativeExplVar:
            #print type(explVar)
            #print explVar.index(variance)
            if cumulativeExplVar.index(variance) == maxPCs:
                break
            value = str(round(variance, 1)) + '%'
            cumulativeLine.append(value)
        
        resultList.append(cumulativeLine)
 
 
 
 
        
    elif itemID[0] == u'Spiderweb Plot':
        if selection == 1: 
            spiderweb_plot(ax, fig, plot_data, averageMatrixForAnalysis, activeAttributesList, selection, pointAndLabelList, _title="Standardized")
        else: 
            spiderweb_plot_lim(ax, fig, plot_data, averageMatrixForAnalysis, activeAttributesList, selection, pointAndLabelList, _title="Original")
        

        numerical_data_add_average_mat(resultList, averageMatrix, activeAttributesList, activeSamplesList)



    elif itemID[0] == u'Bi-Plot':

        xAx = 'PC'+str(pc_x+1)+' (' + str(round(explVar[pc_x] * 100, 1)) + '%)'
        yAx = 'PC'+str(pc_y+1)+' (' + str(round(explVar[pc_y] * 100, 1)) + '%)'

        lims = [-1.2, 1.2, -1.2, 1.2]
        ax.plot([lims[0], lims[1]], [0, 0], 'b--')
        ax.plot([0, 0], [lims[2], lims[3]], 'b--')
        ax.grid(plot_data.view_grid)
        
        scaled_scores_x, scaled_scores_y, scaled_loadings_x, scaled_loadings_y = biplot(ax, fig, scores, loadings, pc_x=pc_x, pc_y=pc_y)
        
        axes_setup(ax, xAx, yAx, title_pca_type + "Bi-Plot", lims)

        font1 = {'family'     : 'sans-serif',
                'color'      : 'b',
                'weight' : 'normal',
                'size'   : 13}

        font2 = {'family'     : 'sans-serif',
                'color'      : 'r',
                'weight' : 'normal',
                'size'   : 13}

        
        scaled_scores_x_list = []
        scaled_scores_y_list = []
        scaled_loadings_x_list = []
        scaled_loadings_y_list = []
        
        for sample in range(len(activeSamplesList)):
            
            textXCoord = scaled_scores_x[sample] + 0.02 # +1% of x length
            textYCoord = scaled_scores_y[sample]
            
            ax.text(textXCoord, textYCoord, activeSamplesList[sample], font1)
            pointAndLabelList.append([scaled_scores_x[sample], scaled_scores_y[sample], "Scaled PCA Scores: " + activeSamplesList[sample]])
           
            scaled_scores_x_list.append(num2str(scaled_scores_x[sample]))
            scaled_scores_y_list.append(num2str(scaled_scores_y[sample]))           

        for attribute in range(len(activeAttributesList)):
            
            textXCoord = scaled_loadings_x[attribute] + 0.02 # +1% of x length
            textYCoord = scaled_loadings_y[attribute]
            
            ax.text(textXCoord, textYCoord, 
                    activeAttributesList[attribute],
                    font2)
            pointAndLabelList.append([scaled_loadings_x[attribute], scaled_loadings_y[attribute], "Scaled PCA Loadings: " + activeAttributesList[attribute]])

            scaled_loadings_x_list.append(num2str(scaled_loadings_x[attribute]))
            scaled_loadings_y_list.append(num2str(scaled_loadings_y[attribute]))


        
        numerical_data_add_average_mat(resultList, averageMatrix, activeAttributesList, activeSamplesList)

            
        resultList.append([""])
        resultList.append([""])
        resultList.append([""])
        
        resultList.append(["Scaled Scores:"])
        _line = ['']; _line.extend(activeSamplesList)
        resultList.append(_line)
        _line = ["PC" + str(pc_x + 1)]; _line.extend(scaled_scores_x_list)
        resultList.append(_line)
        _line = ["PC" + str(pc_y + 1)]; _line.extend(scaled_scores_y_list)
        resultList.append(_line)
            
        resultList.append([""])
        resultList.append([""])
        resultList.append([""])
        
        resultList.append(["Scaled Loadings:"])
        _line = ['']; _line.extend(activeAttributesList)
        resultList.append(_line)
        _line = ["PC" + str(pc_x + 1)]; _line.extend(scaled_loadings_x_list)
        resultList.append(_line)
        _line = ["PC" + str(pc_y + 1)]; _line.extend(scaled_loadings_y_list)
        resultList.append(_line)        
        
        
    #update plot-data variables:
    plot_data.point_lables = pointAndLabelList
    plot_data.raw_data = rawDataList
    plot_data.numeric_data = resultList
    plot_data.plot_type = "consensus"
    plot_data.special_opts["dclick_plot"] = "line_samp"
    plot_data.special_opts["interactivity_on"] = interact
    plot_data.point_lables_type = 0
    plot_data.max_PCs = maxPCs
    plot_data.selection = selection

    #Frame draw, for standard Matplotlib frame only use show()
    return plot_data




def spiderweb_plot(ax, fig, plot_data, averageMatrix, activeAttributes, selection, pointAndLabelList, _title="Original"):
    """
    """
    print "spiderweb plot"
    ax.grid(plot_data.view_grid)


    font = {'family'     : 'sans-serif',
                'color'      : 'k',
                'weight' : 'normal',
                'size'   : 13}
    
    max_values = zeros((averageMatrix.shape[0]), float)
    min_values = zeros((averageMatrix.shape[0]), float)
    for row_ind in range(averageMatrix.shape[0]):
        max_values[row_ind] = max(averageMatrix[row_ind,:])
        min_values[row_ind] = min(averageMatrix[row_ind,:])

    
    max_value = max(max_values) 
    min_value = min(min_values) 
    top_lvl = int(ceil(max_value))
    bottom_lvl = int(floor(min_value))
    
    num_of_vars = len(activeAttributes)
    num_of_samps = len(plot_data.activeSamplesList)
    
    vertices_circles = []
    vertices_lines = []
    
    origo = array([0.0, 0.0], float)
    angle_step = float(360.0 / float(num_of_vars))
    unit = (2*top_lvl)*0.01 # 1 % 
    

    diff = 0.0
    if bottom_lvl < 0:
        diff = -bottom_lvl
    
    for lvl in range(bottom_lvl, top_lvl+1):
        
        vec = array([0.0, float(lvl+diff)], float)
        points = []
        
        current_angle = 0.0
        
        for att_ind in range(num_of_vars):    
            # set current angle
            if att_ind > 0:
                current_angle += angle_step
                #if current_angle > 360.0:
                #    current_angle = current_angle - 360.0

                # rotate vector:
                current_vec = rotate_vec2d(vec, current_angle)
            else:
                current_vec = vec
            
            points.append(current_vec)
            
            if lvl == top_lvl:
                vertices_lines.append([origo, current_vec])
        
        points.append(points[0]) # encircle
        
        vertices_circles.append(points)
        
        # add level number
        ax.text(-(6*unit), (lvl+diff)-unit, str(lvl), font)        
        
        
    ##print "circles"
    ##print vertices_circles
    
    ##print "lines"
    ##print vertices_lines
    
    lc_1 = LineCollection(vertices_circles, colors='#999999')
    lc_2 = LineCollection(vertices_lines, colors='#999999')
    ax.add_collection(lc_1)
    ax.add_collection(lc_2)
    
    
    x_values = []
    y_values = []
    vertices_rings = []
    ring_colors = []
    c_ind = 0
    # add sample "rings" to plot
    for samp_ind in range(num_of_samps):
        
        
        ring = []
        x_vals = zeros((num_of_vars), float)
        y_vals = zeros((num_of_vars), float)
        
        for att_ind in range(num_of_vars):
            # normalize value
            value = averageMatrix[samp_ind, att_ind]
            norm_val = (value+diff) / float(top_lvl+diff)
            
            top_xy = vertices_lines[att_ind][1]
            val_x = lerp(0.0, top_xy[0], norm_val)
            val_y = lerp(0.0, top_xy[1], norm_val)
            
            ring.append((val_x, val_y))
            x_vals[att_ind] = val_x
            y_vals[att_ind] = val_y
            
        x_values.append(x_vals.copy())
        y_values.append(y_vals.copy())
            
        ring.append(ring[0]) # encircle
        vertices_rings.append(ring)
        ring_colors.append(colors_rgb_list[c_ind])
        
        c_ind += 1
        if c_ind >= len(colors_rgb_list):
            c_ind = 0

    lc_3 = LineCollection(vertices_rings, colors=ring_colors)
    ax.add_collection(lc_3)
    
    # add sample-ring points
    for samp_ind in range(num_of_samps):
        ax.scatter(x_values[samp_ind], y_values[samp_ind], s=40, color=ring_colors[samp_ind], marker='o')
        for att_ind in range(num_of_vars):
            value = averageMatrix[samp_ind, att_ind]
            pointAndLabelList.append([x_values[samp_ind][att_ind], y_values[samp_ind][att_ind], plot_data.activeSamplesList[samp_ind] + ": " + str(value)])

    
    # add attribute names
    center_lim = 25*unit; over = unit; under = 3*unit
    for att_ind in range(num_of_vars):
        if att_ind == 0:
                txt = ax.text(0, top_lvl + diff + 2*unit, activeAttributes[att_ind], font)
                txt.set_horizontalalignment('center')            
        else:
		top_xy = vertices_lines[att_ind][1]
		if top_xy[1] > 0:
		    if top_xy[0] > center_lim:
			txt = ax.text(top_xy[0], top_xy[1] + over, activeAttributes[att_ind], font)
			txt.set_horizontalalignment('left')
		    elif top_xy[0] < -center_lim:
			txt = ax.text(top_xy[0], top_xy[1] + over, activeAttributes[att_ind], font)
			txt.set_horizontalalignment('right')
		    else:
			txt = ax.text(top_xy[0], top_xy[1] + over, activeAttributes[att_ind], font)
			txt.set_horizontalalignment('center')
		else:
		    if top_xy[0] > center_lim:
			txt = ax.text(top_xy[0], top_xy[1] - under, activeAttributes[att_ind], font)
			txt.set_horizontalalignment('left')
		    elif top_xy[0] < -center_lim:
			txt = ax.text(top_xy[0], top_xy[1] - under, activeAttributes[att_ind], font)
			txt.set_horizontalalignment('right')
		    else:
			txt = ax.text(top_xy[0], top_xy[1] - under, activeAttributes[att_ind], font)
			txt.set_horizontalalignment('center')


    if plot_data.view_legend:
	plotList = []
	for samp_ind in range(num_of_samps):
	    plotList.append(Line2D([],[], color = ring_colors[samp_ind], linewidth=5))
	fig.legend(plotList, plot_data.activeSamplesList, 'upper right')
	
            
    top_lvl_lim = top_lvl + diff + (10*unit)
    lims = [-top_lvl_lim - (10*unit), top_lvl_lim + (10*unit), -top_lvl_lim, top_lvl_lim]
    axes_setup(ax, "", "", _title + ": Spider Plot", lims)    
    



def spiderweb_plot_lim(ax, fig, plot_data, averageMatrix, activeAttributes, selection, pointAndLabelList, _title="Original"):
    """
    """
    print "spiderweb plot"
    ax.grid(plot_data.view_grid)


    font = {'family'     : 'sans-serif',
                'color'      : 'k',
                'weight' : 'normal',
                'size'   : 13}
    
    max_values = zeros((averageMatrix.shape[0]), float)
    for row_ind in range(averageMatrix.shape[0]):
        max_values[row_ind] = max(averageMatrix[row_ind,:])


    top_lvl = int(ceil(plot_data.limits[3])) # ymax
    bottom_lvl = int(floor(plot_data.limits[2])) # ymin
    step_lvl = int(ceil((top_lvl - bottom_lvl) * 0.1))
    
    max_value = max(max_values) 
    #top_lvl = int(ceil(max_value))
    num_of_vars = len(activeAttributes)
    num_of_samps = len(plot_data.activeSamplesList)
    
    vertices_circles = []
    vertices_lines = []
    
    origo = array([0.0, 0.0], float)
    angle_step = float(360.0 / float(num_of_vars))
    unit = (2*top_lvl)*0.01 # 1 % 
    
    
    diff = 0.0
    if bottom_lvl < 0:
        diff = -bottom_lvl
        
    top_scale_lvl = top_lvl
    
    
    for lvl in range(bottom_lvl, top_lvl+step_lvl, step_lvl):
        
        vec = array([0.0, float(lvl+diff)], float)
        points = []
        
        current_angle = 0.0
        
        for att_ind in range(num_of_vars):    
            # set current angle
            if att_ind > 0:
                current_angle += angle_step
                #if current_angle > 360.0:
                #    current_angle = current_angle - 360.0

                # rotate vector:
                current_vec = rotate_vec2d(vec, current_angle)
            else:
                current_vec = vec
            
            points.append(current_vec)
            
            if lvl >= top_lvl:
                top_scale_lvl = lvl
                vertices_lines.append([origo, current_vec])
        
        points.append(points[0]) # encircle
        
        vertices_circles.append(points)
        
        # add level number
        ax.text(-(2*unit), (lvl+diff)-(0.5*unit), str(lvl), font)        
        
    ##print "circles"
    ##print vertices_circles
    
    ##print "lines"
    ##print vertices_lines
    
    lc_1 = LineCollection(vertices_circles, colors='#999999')
    lc_2 = LineCollection(vertices_lines, colors='#999999')
    ax.add_collection(lc_1)
    ax.add_collection(lc_2)
    
    
    x_values = []
    y_values = []
    vertices_rings = []
    ring_colors = []
    c_ind = 0
    # add sample "rings" to plot
    for samp_ind in range(num_of_samps):
        
        
        ring = []
        x_vals = zeros((num_of_vars), float)
        y_vals = zeros((num_of_vars), float)
        
        for att_ind in range(num_of_vars):
            # normalize value
            value = averageMatrix[samp_ind, att_ind]
            top_xy = vertices_lines[att_ind][1]
            
            norm_val = (value + diff) / float(top_scale_lvl + diff)           
            
            val_x = lerp(0.0, top_xy[0], norm_val)
            val_y = lerp(0.0, top_xy[1], norm_val)
            
            ring.append((val_x, val_y))
            x_vals[att_ind] = val_x
            y_vals[att_ind] = val_y
            
        x_values.append(x_vals.copy())
        y_values.append(y_vals.copy())
            
        ring.append(ring[0]) # encircle
        vertices_rings.append(ring)
        ring_colors.append(colors_rgb_list[c_ind])
        
        c_ind += 1
        if c_ind >= len(colors_rgb_list):
            c_ind = 0

    lc_3 = LineCollection(vertices_rings, colors=ring_colors)
    ax.add_collection(lc_3)
    
    # add sample-ring points
    for samp_ind in range(num_of_samps):
        ax.scatter(x_values[samp_ind], y_values[samp_ind], s=40, color=ring_colors[samp_ind], marker='o')
        for att_ind in range(num_of_vars):
            value = averageMatrix[samp_ind, att_ind]
            pointAndLabelList.append([x_values[samp_ind][att_ind], y_values[samp_ind][att_ind], plot_data.activeSamplesList[samp_ind] + ": " + str(value)])

    
    # add attribute names
    center_lim = 25*unit; over = unit; under = 3*unit
    for att_ind in range(num_of_vars):
        if att_ind == 0:
                txt = ax.text(0, top_lvl + diff + 2*unit, activeAttributes[att_ind], font)
                txt.set_horizontalalignment('center')            
        else:
		top_xy = vertices_lines[att_ind][1]
		if top_xy[1] > 0:
		    if top_xy[0] > center_lim:
			txt = ax.text(top_xy[0], top_xy[1] + over, activeAttributes[att_ind], font)
			txt.set_horizontalalignment('left')
		    elif top_xy[0] < -center_lim:
			txt = ax.text(top_xy[0], top_xy[1] + over, activeAttributes[att_ind], font)
			txt.set_horizontalalignment('right')
		    else:
			txt = ax.text(top_xy[0], top_xy[1] + over, activeAttributes[att_ind], font)
			txt.set_horizontalalignment('center')
		else:
		    if top_xy[0] > center_lim:
			txt = ax.text(top_xy[0], top_xy[1] - under, activeAttributes[att_ind], font)
			txt.set_horizontalalignment('left')
		    elif top_xy[0] < -center_lim:
			txt = ax.text(top_xy[0], top_xy[1] - under, activeAttributes[att_ind], font)
			txt.set_horizontalalignment('right')
		    else:
			txt = ax.text(top_xy[0], top_xy[1] - under, activeAttributes[att_ind], font)
			txt.set_horizontalalignment('center')


    if plot_data.view_legend:
	plotList = []
	for samp_ind in range(num_of_samps):
	    plotList.append(Line2D([],[], color = ring_colors[samp_ind], linewidth=5))
	fig.legend(plotList, plot_data.activeSamplesList, 'upper right')
	
            
    top_lvl_lim = top_lvl + diff + (5*unit)
    lims = [-top_lvl_lim - (10*unit), top_lvl_lim + (10*unit), -top_lvl_lim, top_lvl_lim]
    axes_setup(ax, "", "", _title + ": Spider Plot", lims)    
    

    

def biplot(ax, fig, scores, loadings, pc_x=0, pc_y=1):
    """
    Does scale and creates biplot.
    """
    print "biplot"
    
    # get scaled values (numpy arrays):
    scaled_scores_x, scaled_scores_y, scaled_loadings_x, scaled_loadings_y = BiplotCalc(scores, loadings, pc_x=pc_x, pc_y=pc_y)
       
    
    ax.scatter(scaled_scores_x, scaled_scores_y, s=25, c='b', marker='s')
    ax.scatter(scaled_loadings_x, scaled_loadings_y, s=25, c='r', marker='s')
    
    return scaled_scores_x, scaled_scores_y, scaled_loadings_x, scaled_loadings_y
    

        
        


def BiplotCalc(scores, loadings, pc_x=0, pc_y=1):
    """
    This function computes the scaled scores and loadings of biplots for any
    two given principal components
    """

    horScores = scores[:, pc_x]
    vertScores = scores[:, pc_y]
    horLoadings = loadings[pc_x, :]
    vertLoadings = loadings[pc_y, :]
    
    # Find absolute values for submitted scores and loadings
    abs_horScores = abs(horScores)
    abs_vertScores = abs(vertScores)
    
    abs_horLoadings = abs(horLoadings)
    abs_vertLoadings = abs(vertLoadings)
    
    
    # Find highest absoulte value for submitted scores and loading. Needed
    # for scaling
    max_horScores = max(abs_horScores)
    max_vertScores = max(abs_vertScores)
    
    max_horLoadings = max(abs_horLoadings)
    max_vertLoadings = max(abs_vertLoadings)
    
    
    # Scale all submitted scores and loadings by dividing through max values
    # computed above
    scaled_horScores = horScores / max_horScores
    scaled_vertScores = vertScores / max_vertScores
    
    scaled_horLoadings = horLoadings / max_horLoadings
    scaled_vertLoadings = vertLoadings / max_vertLoadings
    
    
    return scaled_horScores, scaled_vertScores, scaled_horLoadings, scaled_vertLoadings
    


def average_data(s_data, plot_data, selection=0):
    activeAssessorsList = plot_data.activeAssessorsList[:]
    activeAttributesList = plot_data.activeAttributesList[:]
    activeSamplesList = plot_data.activeSamplesList[:]
    
    # 'Standardized' tab is active then standardize data, calculate average
    # and compute the required values
    if selection == 1:
        print 'do standardisation'
        
        # Construct a list that contains the data of each active assessor.
        # First construct a list (oneAssessorList) for each assessor that 
        # contains all the objects (floatRow). Then convert it so array. 
        # In the end, put the array in to another list (allAssessorsList).
        allAssessorsList = []            
        for assessor in activeAssessorsList:
            oneAssessorList = []
            
            for sample in activeSamplesList:
                
                for replicate in s_data.ReplicateList:
                    dataRow = s_data.SparseMatrix[(assessor, sample, replicate)]
                    
                    # Here all strings from s_data.SparseMatrix are converted to floats
                    floatRow = []
                    for eachValue in dataRow:
                        floatRow.append(float(eachValue))

                    # Leave out the values of those attributes that are not
                    # selected
                    newFloatRow = []
                    for attribute in s_data.AttributeList:
                        if attribute in activeAttributesList:
                            newFloatRow.append(floatRow[s_data.AttributeList.index(attribute)])
                    
                    oneAssessorList.append(newFloatRow)
            
            # Convert to array and then append to list
            allAssessorsList.append(array(oneAssessorList))
        
            
        # Now check each assessor for STD=0
        # by calculating a matrix that contains the STD's for each
        # assessor. Also averages for each assessor are calculated.
        STDmatrix = zeros((1, len(activeAttributesList)),float)
        meanMatrix = zeros((1, len(activeAttributesList)), float)
        
        leaveOutAtts = []
        for assessor in allAssessorsList:
            
            check = array(STD(assessor, 0), copy=False)
            assMean = array(average(assessor, 0), copy=False)
            
            STDmatrix = vstack((STDmatrix, check))
            meanMatrix = vstack((meanMatrix, assMean))
            
            newCheck = check.tolist()
            
            position = 0
            for item in newCheck:
                
                if item == 0.0:
                    
                    if position not in leaveOutAtts:
                        leaveOutAtts.append(position)
                position += 1
        
        leaveOutAtts.sort()
        leaveOutAttributes = []
        for badAtt in leaveOutAtts:
            leaveOutAttributes.append(activeAttributesList[badAtt])
        
        # Leave out the first row that has only zeros
        STDarray = STDmatrix[1:,:].copy()
        meanMatrix = meanMatrix[1:,:].copy()
        
        
        # Now that we know which attributes give STD=0 for at least
        # one assessor we do the following:
        # 1. Inform user about it with a message box
        # 2. Create a new array with STD's that has no STD=0 
        #   dim (activeAssors x (activeAttributes - badAttributes))
        
        # Point 1.
        if len(leaveOutAttributes) > 0:
            messagePart1 = 'The following attributes were left out of the analysis because \nfor one or more assessors the standard deviation is 0: \n'
            
            messagePart2 = leaveOutAttributes[0]
            for atts in leaveOutAttributes:
                if messagePart2 == atts:
                    pass
                else:
                    messagePart2 = messagePart2 + ', ' + atts
            
            messagePart3 = '\n\nPlease uncheck these attributes to avoid this message.'
                
            message = messagePart1 + messagePart2 + messagePart3
            
            dlg = wx.MessageDialog(None, message,
                               'Important information',
                               wx.OK | wx.ICON_INFORMATION)
            dlg.ShowModal()
            dlg.Destroy()
        
        
        # Point 2.
        realSTDarray = zeros((1, len(activeAssessorsList)), float)
        realAssMeanArray = zeros((1, len(activeAssessorsList)), float)
                    
        for attribute in range(len(activeAttributesList)):
            checkCol = STDarray[:, attribute]
            checkCol2 = meanMatrix[:, attribute]
            #ipshell()
            if 0 in checkCol:
                #print 'zero in column ', attribute
                pass
                
            else:
                realSTDarray = vstack((realSTDarray, checkCol))
                realAssMeanArray = vstack((realAssMeanArray, checkCol2))
        
        
        nextSTDarray = realSTDarray[1:,:].copy()
        finalSTDarray = transpose(nextSTDarray)
        
        nextAssMeanArray = realAssMeanArray[1:,:].copy()
        finalAssMeanArray = transpose(nextAssMeanArray)
        
        #print finalSTDarray
        #print
        #print finalAssMeanArray
        
        for attribute in leaveOutAttributes:
            activeAttributesList.remove(attribute)
        #print activeAttributesList
            
    
    elif selection == 0:
        print 'do average'

    # Constructing average matrices:
    # - sampleAverageMatrix for each sample
    # - averageMatrix for all samples
    # - assessorAverageMatrix for each assessor
    rowsAverageMatrix = len(activeSamplesList)
    columns = len(activeAttributesList)
    replicates = len(s_data.ReplicateList)
    
    rowsSampleAverageMatrix = replicates * len(activeAssessorsList)
    averageMatrix = zeros((rowsAverageMatrix, columns), float)
    
    
    for sample in activeSamplesList:
        
        constructSampleAverageMatrix = zeros((1, columns), float)
        for assessor in activeAssessorsList:
            
                for replicate in s_data.ReplicateList:
                    
                    valueCollectionList = []
                    for attribute in activeAttributesList:
                        if selection == 1:
                            value = float(s_data.SparseMatrix[(assessor,sample,replicate)][s_data.AttributeList.index(attribute)])
                            STDvalue = finalSTDarray[activeAssessorsList.index(assessor), activeAttributesList.index(attribute)]
                            averValue = finalAssMeanArray[activeAssessorsList.index(assessor), activeAttributesList.index(attribute)]
                            calc = (value - averValue) / STDvalue
                            #print value, averValue,STDvalue, calc
                            
                            #print finalSTDarray[activeAssessorsList.index(assessor), activeAttributesList.index(attribute)]
                            valueCollectionList.append((value - averValue) / STDvalue)
                        
                        elif selection == 0:
                            value = float(s_data.SparseMatrix[(assessor,sample,replicate)][s_data.AttributeList.index(attribute)])
                            valueCollectionList.append(value)
                        
                    oneMatrixRow = array(valueCollectionList)
                    #print oneMatrixRow.shape
                        
                        
                    #print '*******************************'
                    constructSampleAverageMatrix = vstack((constructSampleAverageMatrix, oneMatrixRow))
        
        # Remove first row that contains only zeros
        sampleAverageMatrix = constructSampleAverageMatrix[1:,:].copy()
        
        # Now calculate average for that sample and copy values
        # in to averageMatrix
        sampleAverage = average(sampleAverageMatrix, 0)
        averageMatrix[activeSamplesList.index(sample)] = sampleAverage.copy()
    
    return averageMatrix, activeAttributesList


def Averaged_Data_Grid(s_data, plot_data, num_subplot=[1,1,1], selection=0): 
    """
    Creates a grid of averaged data.
    

    @type s_data.SparseMatrix:     dictionary
    @param s_data.SparseMatrix:    Sparse matrix that contains 3-way data from assessors
    
    @type ActiveAssessors:  dictionary
    @param ActiveAssessors: Contains assessors that were selected/checked by the user
                            in the assessor-checkListBox
    
    @type ActiveSamples:    dictionary
    @param ActiveSamples:   Contains samples that were selected/checked by the user
                            in the sample-checkListBox
      
    @type s_data.ReplicateList:    list
    @param s_data.ReplicateList:   Contains all replicates original from data set
    
    @type s_data.AttributeList:    list
    @param s_data.AttributeList:   Contains all attributes original from data set
    """
    activeAssessorsList = plot_data.activeAssessorsList[:]
    activeAttributesList = plot_data.activeAttributesList[:]
    activeSamplesList = plot_data.activeSamplesList[:]
    itemID = plot_data.tree_path
    
    
    if len(activeAssessorsList) < 1: #no active assessors
        dlg = wx.MessageDialog(None, 'No assessors are active in CheckBox',
                               'Error Message',
                               wx.OK | wx.ICON_INFORMATION)
        dlg.ShowModal()
        dlg.Destroy()
        return
    if len(activeAttributesList) < 1: #no active assessors
        dlg = wx.MessageDialog(None, 'No attributes are active in CheckBox',
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
    
    averageMatrixForAnalysis, activeAttributes = average_data(s_data, plot_data, selection=selection)
    
    resultList = []
    
    numerical_data_add_average_mat(resultList, averageMatrixForAnalysis, activeAttributes, activeSamplesList)
            
    frameName = "Consensus Data (Original)"
    if selection == 1:
        frameName = "Consensus Data (Standardized)"
    return frameName, resultList
    
    
    
    
    
    
    
    
    
    
    
    
    
    
#!/usr/bin/env python

#-------------------------------------------------------------------------------
# Name:        statis.py
# Purpose:     Calculate consensus with STATIS for sensory data
#
# Author:      Oliver Tomic, Matforsk (www.matforsk.no/panelcheck)
#
# Created:     24/04/2007
# Copyright:   (c) Oto 2007
# Licence:     GNU GPL
#-------------------------------------------------------------------------------


def statisX(f_assMatricesList, choice):
    """
    STATIS-X function

    choice = 0: uses covariance
    choice = 1: uses correlation
    """
    
    print 'STATIS-X'
    if choice == 0:
        print 'using COV'
    elif choice == 1:
        print 'using CORR'
    else:
        print 'input error - choice must take value 0 or 1'
        return None

    # Find dimensions of assessor matrices
    rows, cols = shape(f_assMatricesList[0])


    # Center all assessor matrices before STATIS computations
    cent_assMatrices = []
    for ass in f_assMatricesList:
        centMat = center(ass)
        cent_assMatrices.append(centMat)


    # Now calculate matrix holding COVARIANCES of each possible
    # assessor-assessor combination and the total variance
    allCovs = []
    oneRowCovs = []
    for ass1 in cent_assMatrices:
        for ass2 in cent_assMatrices:
            covtotal = trace(dot(ass1.transpose(), ass2)) / shape(ass1)[0]
            oneRowCovs.append(covtotal)
        allCovs.append(oneRowCovs)
        oneRowCovs = []

    allCovsMat = array(allCovs)
    totVar = diag(allCovsMat)


    # Calculate matrix holding CORRELATIONS of each possible
    # assessor-assessor combination
    newList = []
    for ass1 in range(len(cent_assMatrices)):
        new_ass = cent_assMatrices[ass1] / sqrt(totVar[ass1])
        newList.append(new_ass)

    allCorrs = []
    oneRowCorrs = []
    for ass1 in newList:
        for ass2 in newList:
            corrtotal = trace(dot(ass1.transpose(), ass2)) / shape(ass1)[0]
            oneRowCorrs.append(corrtotal)
        allCorrs.append(oneRowCorrs)
        oneRowCorrs = []

    allCorrsMat = array(allCorrs)


    # Now compute eigenvectors according to users choice based on either
    # the covariances or correlations
    if choice == 0:
        [U, S, V] = svd(allCovsMat)
        
    elif choice == 1:
        [U, S, V] = svd(allCorrsMat)


    # Now get first eigenvector which holds eigenvalues that will be
    # computed to weights
    eigVec1 = U[:,0]


    # Check how many negative values are given in the first eigenvector
    testVec = eigVec1 > 0
    testList = list(testVec)
    numberOfFalses = testList.count(False)


    # If more than half of the values are negative, then multiply with -1
    if numberOfFalses >= len(testVec)/2:
        eigVec1 = eigVec1 * -1


    # Now calculate weights
    weights = eigVec1 * eigVec1


    # Now construct consensus by multiplying each assessor's data with its
    # weight and then sum up all over all assessors
    consensus = zeros((rows, cols), float)
    for ass in range(len(f_assMatricesList)):
        consensus = consensus + f_assMatricesList[ass] * weights[ass]


    # Store all results in a list and return it
    results = [consensus, weights, allCorrsMat, allCovsMat]
    return results



def STATIS_AssWeight_Plotter(s_data, plot_data, num_subplot=[1,1,1], selection=0):    
    activeAssessorsList = plot_data.activeAssessorsList[:]
    activeAttributesList = plot_data.activeAttributesList[:]
    activeSamplesList = plot_data.activeSamplesList[:]
    itemID = plot_data.tree_path  
    
    #print itemID[0], ' was selected'
    
    if len(activeAssessorsList) < 1: #no active assessors
        dlg = wx.MessageDialog(None, 'No assessors are active in CheckBox',
                               'Error Message',
                               wx.OK | wx.ICON_INFORMATION)
        dlg.ShowModal()
        dlg.Destroy()
        return
    if len(activeAttributesList) < 1: #no active assessors
        dlg = wx.MessageDialog(None, 'No attributes are active in CheckBox',
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

    # Compute average matrix for each assessor and store it in list
    assMatricesList = []
    for assessor in plot_data.activeAssessorsList:
        assSampAv = s_data.GetAssAverageMatrix(assessor, activeAttributesList, activeSamplesList)
        assMatricesList.append(assSampAv)


    # Use STATIS-X function
    # statisMethod(listHoldingMatrices, choice)
    # choice = 0: statis based on covariance
    # choice = 1: statis based on correlation    
    results = statisX(assMatricesList, selection)
    if results == None: 
        dlg = wx.MessageDialog(None, 'Error in code. Wrong selection choice.',
                               'Error Message',
                               wx.OK | wx.ICON_INFORMATION)
        dlg.ShowModal()
        dlg.Destroy()
        return
    
    
    # Figure
    replot = False; subplot = plot_data.overview_plot; scatter_width = 35
    if plot_data.fig != None: replot = True
    else: plot_data.fig = Figure(None)
    if subplot: # is subplot
        plot_data.ax = plot_data.fig.add_subplot(num_subplot[0], num_subplot[1], num_subplot[2])
        scatter_width = 15
    else: plot_data.ax = axes_create(0, plot_data.fig)
    ax = plot_data.ax; fig = plot_data.fig
    
    
    ax.grid(plot_data.view_grid)
    
    ind = arange(1, len(results[1]) + 1)
    width = 0.35
    ax.bar(ind - (width/2), results[1], width, color = "#0000ff")
    
    
    y_lims = ax.get_ylim()
    

    # xmax = number of samples tested
    limits = [0, len(plot_data.activeAssessorsList)+1, 0, y_lims[1] + y_lims[1]*0.05]
    
    axes_setup(ax, "", "Weight", "STATIS: Assessor Weights", limits)
    
    indANDwidth = []
    for vals in ind:
        indANDwidth.append(vals)
    
    ax.set_xticks(indANDwidth)
    ax.set_xticklabels(plot_data.activeAssessorsList)    
    if len(plot_data.activeAssessorsList) > 9:
        set_xlabeling_rotation(ax, 'vertical')
    pointAndLabelList = []
    resultList = []
    resultList.append(plot_data.activeAssessorsList)
    _line = []
    for value in results[1]:
        _line.append(num2str(value))
    resultList.append(_line)
    
    #update plot-data variables:
    plot_data.point_lables = pointAndLabelList
    plot_data.raw_data = raw_data_grid(s_data, plot_data)
    plot_data.numeric_data = resultList
    plot_data.plot_type = "statis_consensus"
    plot_data.point_lables_type = 0
    plot_data.max_PCs = 0 # NOT TO BE USED (only for compatibility)
    plot_data.selection = selection # 0: covariance, 1: correlation    
    return plot_data
    


def STATIS_PCA_Plotter(s_data, plot_data, num_subplot=[1,1,1], selection=0, pc_x=0, pc_y=1):
    """
    This is the PCA plot function. It plots the PCA scores of the averaged 
    matrix (over assessors and replicates).
    

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
    
    @type sampleList:       list
    @param sampleList:      Contains all samples from original data set
    
    @type s_data.ReplicateList:    list
    @param s_data.ReplicateList:   Contains all replicates original from data set
    
    @type s_data.AttributeList:    list
    @param s_data.AttributeList:   Contains all attributes original from data set
    
    @type itemID[0]:     list
    @param itemID[0]:    Conatins which item in the tree was double-clicked
    
    ActiveSample_list: Is created from ActiveAssessors (dictionary) and is
    used for iterating through the active asessors
    ActiveSample_list: list
    """

    activeAssessorsList = plot_data.activeAssessorsList[:]
    activeAttributesList = plot_data.activeAttributesList[:]
    activeSamplesList = plot_data.activeSamplesList[:]
    itemID = plot_data.tree_path  
    
    #print itemID[0], ' was selected'
    
    if len(activeAssessorsList) < 1: #no active assessors
        dlg = wx.MessageDialog(None, 'No assessors are active in CheckBox',
                               'Error Message',
                               wx.OK | wx.ICON_INFORMATION)
        dlg.ShowModal()
        dlg.Destroy()
        return
    if len(activeAttributesList) < 1: #no active assessors
        dlg = wx.MessageDialog(None, 'No attributes are active in CheckBox',
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

    # Compute average matrix for each assessor and store it in list
    assMatricesList = []
    for assessor in plot_data.activeAssessorsList:
        assSampAv = s_data.GetAssAverageMatrix(assessor, activeAttributesList, activeSamplesList)
        assMatricesList.append(assSampAv)
    
    #print assMatricesList
    
    
    # Use STATIS-X function
    # statisMethod(listHoldingMatrices, choice)
    # choice = 0: statis based on covariance
    # choice = 1: statis based on correlation    
    results = statisX(assMatricesList, selection)
    if results == None: 
        dlg = wx.MessageDialog(None, 'Error in code. Wrong selection choice.',
                               'Error Message',
                               wx.OK | wx.ICON_INFORMATION)
        dlg.ShowModal()
        dlg.Destroy()
        return

    
    # Construction of consensus matrix depending on which tab is active
    numberOfAssessors = len(activeAssessorsList)
    numberOfAttributes = len(activeAttributesList)
    numberOfSamples = len(activeSamplesList)
    numberOfReplicates = len(s_data.ReplicateList)
    pointAndLabelList = []
 
    
    averageMatrix = results[0] # consensus
    averageMatrixForAnalysis = averageMatrix.copy()
    
    # Do PCA and get all results
    #PCAanalysis = PCA(averageMatrixForAnalysis, 1)
    
    #scores = PCAanalysis.GetScores()
    #loadings = PCAanalysis.GetLoadings()
    #corrLoadings = PCAanalysis.GetCorrelationLoadings()
    #transCorrLoadings = transpose(corrLoadings)
    #explVar = PCAanalysis.GetExplainedVariances()
    
    scores, loadings, explVar = PCA(averageMatrixForAnalysis)
    explVar = list(explVar)
    corrLoadings = CorrelationLoadings(averageMatrixForAnalysis, scores)
    transCorrLoadings = transpose(corrLoadings)          
    
    font = {'family'     : 'sans-serif',
                    'color'      : 'k',
                    'weight' : 'normal',
                    'size'   : 11,
                    }
    
    # Starting generation of the list that contains the raw data
    # that is shown in "Raw Data" when pushing the button in the plot
    
    resultList = []
    emptyLine = ['']
    
    # Continue building resultList
    # Limiting PC's in 'Numeric Results' to 10
    [PCs, activeAttributes] = shape(corrLoadings)
    [Samples, PCs] = shape(scores)
    
    maxPCs = 10
    [Samples, PCs] = shape(scores)
    if PCs < maxPCs:
        maxPCs = PCs
    
    
    # Figure
    aspect = plot_data.aspect; legend_on = False
    if itemID[0] == "PCA Explained Variance": aspect = 'auto'
    if itemID[0] == "Spiderweb Plot": legend_on = plot_data.view_legend
    
    replot = False; subplot = plot_data.overview_plot
    if plot_data.fig != None: replot = True
    else: plot_data.fig = Figure(None)
    if subplot: # is subplot
        plot_data.ax = plot_data.fig.add_subplot(num_subplot[0], num_subplot[1], num_subplot[2], aspect=aspect)
    else: plot_data.ax = axes_create(legend_on, plot_data.fig, aspect=aspect)
    ax = plot_data.ax; fig = plot_data.fig    
    
    
    
    interact = False
    
    
    # for choice: PCA Scores
    # **********************
    if itemID[0] == u'PCA Scores':
        # This constructs the resultList that shows the sample scores
        # in 'Show Data'
        
        
        interact = True
        
        numerical_data_add_average_mat(resultList, averageMatrix, activeAttributesList, activeSamplesList)
        
        matrixHeaderLine = ['']
        
        resultList.append(emptyLine)
        resultList.append(emptyLine)
        resultList.append(emptyLine)
        
        
        numerical_data_add_scores(scores, activeSamplesList, maxPCs, resultList)
 
 
        explVarHeaderLine = ['']
        
        for PC in range(1, maxPCs + 1):
            columnHeader = 'PC ' + str(PC)
            explVarHeaderLine.append(columnHeader)        
        
        resultList.append(emptyLine)
        resultList.append(emptyLine)
        resultList.append(emptyLine)
        headerExplainedVariance = ['EXPLAINED VARIANCE']
        resultList.append(headerExplainedVariance)
        resultList.append(explVarHeaderLine)
        
        varianceLine = ['']
        
        for variance in explVar:
            #print type(explVar)
            #print explVar.index(variance)
            if explVar.index(variance) == maxPCs:
                break
            value = str(round(variance * 100, 1)) + '%'
            varianceLine.append(value)
        
        resultList.append(varianceLine)
        
        
        # Here the construction of the score plot starts
        # -----------------------------------------------------

        ax.grid(plot_data.view_grid)
        
 	# Get the first and second column from the scores matrix
        scoresXCoordinates = take(scores, (pc_x,), 1)
        scoresYCoordinates = take(scores, (pc_y,), 1)
                
        # Catch max and min values in PC1 and PC2 scores
        # for defining axis-limits in the common scores plot.
        x_max = ceil(max(scoresXCoordinates))
        x_min = floor(min(scoresXCoordinates))
                
        y_max = ceil(max(scoresYCoordinates))
        y_min = floor(min(scoresYCoordinates))
                
        # Defining the titles, axes names, etc
        myTitle = 'STATIS: PCA scores'
        xAx = 'PC'+str(pc_x+1)+' (' + str(round(explVar[pc_x] * 100, 1)) + '%)'
        yAx = 'PC'+str(pc_y+1)+' (' + str(round(explVar[pc_y] * 100, 1)) + '%)'
                
        axes_setup(ax, xAx, yAx, myTitle, [x_min, x_max, y_min, y_max])
        
        scores_x = []
        for element in scoresXCoordinates:
            scores_x.append(element[0])
        #print scoresXCoordinates; print scores_x
        scores_y = []
        for element in scoresYCoordinates: 
            scores_y.append(element[0])
        #print scoresYCoordinates; print scores_y
        
        ax.scatter(scores_x, scores_y, s=25, c='b', marker='s')
        
        #ax.plot([x_min, x_max], [0, 0], 'b--')
        #ax.plot([0, 0], [y_min, y_max], 'b--')
        #axes_setup(ax, xAx, yAx, myTitle, [x_min, x_max, y_min, y_max])
        
        lims = []
        xlims = ax.get_xlim()
	ylims = ax.get_ylim()
	lims.append(xlims[0]); lims.append(xlims[1])
	lims.append(ylims[0]); lims.append(ylims[1])
	
	map(lambda x: round(x*10)/10.0, lims) # maps func(x)=round(x*10)/10.0 for all elements in list
	
	ax.plot([lims[0], lims[1]], [0, 0], 'b--')
        ax.plot([0, 0], [lims[2], lims[3]], 'b--')
        
        axes_setup(ax, xAx, yAx, myTitle, lims)
        
        
        for sample in range(len(activeSamplesList)):
            
            textXCoord = scoresXCoordinates[sample] + (x_max + abs(x_min)) * 0.015
            textYCoord = scoresYCoordinates[sample] - (y_max + abs(y_min)) * 0.01
            
            #print activeSamplesList[sample], textXCoord, textYCoord
            
            
            ax.text(textXCoord[0], textYCoord[0], activeSamplesList[sample], font)
            pointAndLabelList.append([scoresXCoordinates[sample], scoresYCoordinates[sample], "PCA Scores: " + activeSamplesList[sample], [activeSamplesList[sample]] ])
    
    
    
    # for choice: PCA Loadings
    # ************************
    elif itemID[0] == u'PCA Loadings':
        # This constructs the resultList that shows the sample scores
        # in 'Show Data'
        
        
        numerical_data_add_average_mat(resultList, averageMatrix, activeAttributesList, activeSamplesList)
        
        matrixHeaderLine = ['']
        
        
        resultList.append(emptyLine)
        resultList.append(emptyLine)
        resultList.append(emptyLine)
        
        
        numerical_data_add_loadings(loadings, activeAttributesList, maxPCs, resultList)
        
 
        resultList.append(emptyLine)
        resultList.append(emptyLine)
        resultList.append(emptyLine)
        

        explVarHeaderLine = ['']
        
        for PC in range(1, maxPCs + 1):
            columnHeader = 'PC ' + str(PC)
            explVarHeaderLine.append(columnHeader)
        
        headerExplainedVariance = ['EXPLAINED VARIANCE']
        resultList.append(headerExplainedVariance)
        resultList.append(explVarHeaderLine)
        
        varianceLine = ['']
        
        for variance in explVar:
            #print type(explVar)
            #print explVar.index(variance)
            if explVar.index(variance) == maxPCs:
                break
            value = str(round(variance * 100, 1)) + '%'
            varianceLine.append(value)
        
        resultList.append(varianceLine)
    
        
        # Here the construction of the score plot starts
        # -----------------------------------------------------

        ax.grid(plot_data.view_grid)
        
        # Get the first and second column from the scores matrix
        loadingsXCoordinates = loadings[pc_x,:].copy()
        loadingsYCoordinates = loadings[pc_y,:].copy()
                
        # Catch max and min values in PC1 and PC2 scores
        # for defining axis-limits in the common scores plot.
        x_max = ceil(max(loadingsXCoordinates))
        x_min = floor(min(loadingsXCoordinates))
                
        y_max = ceil(max(loadingsYCoordinates))
        y_min = floor(min(loadingsYCoordinates))
                
        # Defining the titles, axes names, etc
        myTitle = 'STATIS: PCA loadings'
        xAx = 'PC'+str(pc_x+1)+' (' + str(round(explVar[pc_x] * 100, 1)) + '%)'
        yAx = 'PC'+str(pc_y+1)+' (' + str(round(explVar[pc_y] * 100, 1)) + '%)'               
         
        ax.scatter(loadingsXCoordinates, loadingsYCoordinates, s=25, c='r', marker='s')
        
        lims = []
        xlims = ax.get_xlim()
	ylims = ax.get_ylim()
	lims.append(xlims[0]); lims.append(xlims[1])
	lims.append(ylims[0]); lims.append(ylims[1])
	
	map(lambda x: round(x*10)/10.0, lims) # maps func(x)=round(x*10)/10.0 for all elements in list
	
	ax.plot([lims[0], lims[1]], [0, 0], 'b--')
        ax.plot([0, 0], [lims[2], lims[3]], 'b--')
        
        axes_setup(ax, xAx, yAx, myTitle, lims)
        
        for attribute in range(len(activeAttributesList)):
            
            textXCoord = loadingsXCoordinates[attribute] + (x_max + abs(x_min)) * 0.015
            textYCoord = loadingsYCoordinates[attribute] - (y_max + abs(y_min)) * 0.01
            
            #print activeAttributesList[attribute], textXCoord, textYCoord
            
            ax.text(textXCoord, textYCoord, 
                    activeAttributesList[attribute],
                    font)
            pointAndLabelList.append([loadingsXCoordinates[attribute], loadingsYCoordinates[attribute], "PCA Loadings: " + activeAttributesList[attribute]])



    # for choice: PCA correlation loadings
    # ************************************
    elif itemID[0] == u'PCA Correlation Loadings':
        
        # Create figure for correlation loadings plot
        # -------------------------------------------

        ax.grid(plot_data.view_grid)
        
        # Create circles and plot them
        t = arange(0.0, 2*pi, 0.01)
        
        # Compuing the outer circle
        xcords = cos(t)
        ycords = sin(t)
        
        # Plotting outer circle
        ax.plot(xcords, ycords, 'b-')
        
        # Computing inner circle
        xcords50percent = 0.707 * cos(t)
        ycords50percent = 0.707 * sin(t)
        
        # Plotting inner circle
        ax.plot(xcords50percent, ycords50percent, 'b-')
        
        # Plotting the correlation loadings
        # Using 'scatter' instead of 'plot', since this allows sizable points
        # in plot
        xCorrLoadings = corrLoadings[pc_x]
        yCorrLoadings = corrLoadings[pc_y]
        
        ax.scatter(xCorrLoadings, yCorrLoadings, s=10, c='w', marker='o')
        
        textXCoord = xCorrLoadings + 0.02
        textYCoord = yCorrLoadings - 0.022
        
        font = {'family'     : 'sans-serif',
                'color'      : 'k',
                'weight' : 'normal',
                'size'   : 13,
                }
        
        # Plot label of each variable
        for coords in range(len(activeAttributesList)):
            #print activeAttributesList[coords]
            ax.text(textXCoord[coords], textYCoord[coords], 
                    activeAttributesList[coords],
                            font)
        
        
        # Defining the titles, axes names, etc
        myTitle = 'STATIS: PCA Correlation loadings'
        xAx = 'PC'+str(pc_x+1)+' (' + str(round(explVar[pc_x] * 100, 1)) + '%)'
        yAx = 'PC'+str(pc_y+1)+' (' + str(round(explVar[pc_y] * 100, 1)) + '%)'
                
        axes_setup(ax, xAx, yAx, myTitle, [-1, 1, -1, 1])
                
        matrixHeaderLine = ['']
                
        #for points and labels:
        xCorrs = corrLoadings[pc_x]
        yCorrs = corrLoadings[pc_y]
        for i in range(len(xCorrs)):
            #pointAndLabelList.append([xCorrs[i],yCorrs[i], activeAttributesList[i+1]])
            pointAndLabelList.append([xCorrs[i],yCorrs[i], activeAttributesList[i]])
            
        
        
        numerical_data_add_loadings(corrLoadings, activeAttributesList, maxPCs, resultList, header_txt='CORRELATION LOADINGS:')
        
     
        resultList.append(emptyLine)
        resultList.append(emptyLine)
        resultList.append(emptyLine)
        
        
        explVarHeaderLine = ['']
        
        for PC in range(1, maxPCs + 1):
            columnHeader = 'PC ' + str(PC)
            explVarHeaderLine.append(columnHeader)
        
        
        headerExplainedVariance = ['EXPLAINED VARIANCE']
        resultList.append(headerExplainedVariance)
        resultList.append(explVarHeaderLine)
        
        varianceLine = ['']
        
        for variance in explVar:
            #print type(explVar)
            #print explVar.index(variance)
            if explVar.index(variance) == maxPCs:
                break
            value = str(round(variance * 100, 1)) + '%'
            varianceLine.append(value)
        
        resultList.append(varianceLine)
        
    
    
    # for choice: PCA explaned variance
    # ************************************
    elif itemID[0] == u'PCA Explained Variance':
        
        # Create figure for correlation loadings plot
        # -------------------------------------------

        ax.grid(plot_data.view_grid)
        
        # Defining the titles, axes names, etc
        myTitle = 'STATIS: PCA explained variance'
        xAx = '# of principal components'
        yAx = 'Explained variance [%]'
        
        axes_setup(ax, xAx, yAx, myTitle, [0, maxPCs, 0, 100])
        
        # Calculate cumulative explained variance for plot
        cumulativeExplVar = [0]
        for var in range(0, maxPCs):
            cumVar = cumulativeExplVar[-1] + (explVar[var] * 100)
            cumulativeExplVar.append(cumVar)
        
        ax.plot(cumulativeExplVar, 'b-')
        
        _range = arange(maxPCs+1)
        ax.set_xticks(_range)        
        
        # Construct resultList
        
        numerical_data_add_average_mat(resultList, averageMatrixForAnalysis, activeAttributesList, activeSamplesList)
        

        resultList.append(emptyLine)
        resultList.append(emptyLine)
        resultList.append(emptyLine)
        
        matrixHeaderLine = ['']
        
        for PC in range(1, maxPCs + 1):
            columnHeader = 'PC ' + str(PC)
            matrixHeaderLine.append(columnHeader)
        
        headerExplainedVariance = ['EXPLAINED VARIANCE']
        resultList.append(headerExplainedVariance)
        resultList.append(emptyLine)
        resultList.append(matrixHeaderLine)
        
        varianceLine = ['expl. var']
        
        for variance in explVar:
            #print type(explVar)
            #print explVar.index(variance)
            if explVar.index(variance) == maxPCs:
                break
            value = str(round(variance * 100, 1)) + '%'
            varianceLine.append(value)
        
        resultList.append(varianceLine)
        
        cumulativeLine = ['cumulative']
        # Get rid of the zero-value in first position
        # that has been used for plotting line (see above)
        del cumulativeExplVar[0]
        for variance in cumulativeExplVar:
            #print type(explVar)
            #print explVar.index(variance)
            if cumulativeExplVar.index(variance) == maxPCs:
                break
            value = str(round(variance, 1)) + '%'
            cumulativeLine.append(value)
        
        resultList.append(cumulativeLine)



    elif itemID[0] == u'Spiderweb Plot':        
        spiderweb_plot_lim(ax, fig, plot_data, averageMatrixForAnalysis, activeAttributesList, selection, pointAndLabelList, _title="STATIS")
        
        numerical_data_add_average_mat(resultList, averageMatrixForAnalysis, activeAttributesList, activeSamplesList)




    elif itemID[0] == u'Bi-Plot':
    
        xAx = 'PC'+str(pc_x+1)+' (' + str(round(explVar[pc_x] * 100, 1)) + '%)'
        yAx = 'PC'+str(pc_y+1)+' (' + str(round(explVar[pc_y] * 100, 1)) + '%)'

        lims = [-1.2, 1.2, -1.2, 1.2]
        ax.plot([lims[0], lims[1]], [0, 0], 'b--')
        ax.plot([0, 0], [lims[2], lims[3]], 'b--')
        ax.grid(plot_data.view_grid)
        
        scaled_scores_x, scaled_scores_y, scaled_loadings_x, scaled_loadings_y = biplot(ax, fig, scores, loadings, pc_x=pc_x, pc_y=pc_y)
        
        axes_setup(ax, xAx, yAx, "STATIS: Bi-Plot", lims)


        font1 = {'family'     : 'sans-serif',
                'color'      : 'b',
                'weight' : 'normal',
                'size'   : 13}

        font2 = {'family'     : 'sans-serif',
                'color'      : 'r',
                'weight' : 'normal',
                'size'   : 13}


        scaled_scores_x_list = []
        scaled_scores_y_list = []
        scaled_loadings_x_list = []
        scaled_loadings_y_list = []

        for sample in range(len(activeSamplesList)):
            
            textXCoord = scaled_scores_x[sample] + 0.02 # +1% of x length
            textYCoord = scaled_scores_y[sample]
            
            ax.text(textXCoord, textYCoord, activeSamplesList[sample], font1)
            pointAndLabelList.append([scaled_scores_x[sample], scaled_scores_y[sample], "Scaled PCA Scores: " + activeSamplesList[sample]])

            scaled_scores_x_list.append(num2str(scaled_scores_x[sample]))
            scaled_scores_y_list.append(num2str(scaled_scores_y[sample]))   
            
            
            
        for attribute in range(len(activeAttributesList)):
            
            textXCoord = scaled_loadings_x[attribute] + 0.02 # +1% of x length
            textYCoord = scaled_loadings_y[attribute]
            
            ax.text(textXCoord, textYCoord, 
                    activeAttributesList[attribute],
                    font2)
            pointAndLabelList.append([scaled_loadings_x[attribute], scaled_loadings_y[attribute], "Scaled PCA Loadings: " + activeAttributesList[attribute]])
            
            scaled_loadings_x_list.append(num2str(scaled_loadings_x[attribute]))
            scaled_loadings_y_list.append(num2str(scaled_loadings_y[attribute]))        
        
        numerical_data_add_average_mat(resultList, averageMatrixForAnalysis, activeAttributesList, activeSamplesList)

       

            
        resultList.append([""])
        resultList.append([""])
        resultList.append([""])
        
        resultList.append(["Scaled Scores:"])
        _line = ['']; _line.extend(activeSamplesList)
        resultList.append(_line)
        _line = ["PC" + str(pc_x + 1)]; _line.extend(scaled_scores_x_list)
        resultList.append(_line)
        _line = ["PC" + str(pc_y + 1)]; _line.extend(scaled_scores_y_list)
        resultList.append(_line)
            
        resultList.append([""])
        resultList.append([""])
        resultList.append([""])
        
        resultList.append(["Scaled Loadings:"])
        _line = ['']; _line.extend(activeAttributesList)
        resultList.append(_line)
        _line = ["PC" + str(pc_x + 1)]; _line.extend(scaled_loadings_x_list)
        resultList.append(_line)
        _line = ["PC" + str(pc_y + 1)]; _line.extend(scaled_loadings_y_list)
        resultList.append(_line)     



   
        
    #update plot-data variables:
    plot_data.point_lables = pointAndLabelList
    plot_data.raw_data = raw_data_grid(s_data, plot_data)
    plot_data.numeric_data = resultList
    plot_data.plot_type = "statis_consensus"
    plot_data.special_opts["dclick_plot"] = "line_samp"
    plot_data.special_opts["interactivity_on"] = interact    
    plot_data.point_lables_type = 0
    plot_data.max_PCs = maxPCs
    plot_data.selection = selection # 0: covariance, 1: correlation  

    #Frame draw, for standard Matplotlib frame only use show()
    return plot_data



def STATIS_Averaged_Data_Grid(s_data, plot_data, num_subplot=[1,1,1], selection=0): 
    """
    
    """
    activeAssessorsList = plot_data.activeAssessorsList[:]
    activeAttributesList = plot_data.activeAttributesList[:]
    activeSamplesList = plot_data.activeSamplesList[:]
    itemID = plot_data.tree_path
    
    
    if len(activeAssessorsList) < 1: #no active assessors
        dlg = wx.MessageDialog(None, 'No assessors are active in CheckBox',
                               'Error Message',
                               wx.OK | wx.ICON_INFORMATION)
        dlg.ShowModal()
        dlg.Destroy()
        return
    if len(activeAttributesList) < 1: #no active assessors
        dlg = wx.MessageDialog(None, 'No attributes are active in CheckBox',
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


    # Compute average matrix for each assessor and store it in list
    assMatricesList = []
    for assessor in plot_data.activeAssessorsList:
        assSampAv = s_data.GetAssAverageMatrix(assessor, activeAttributesList, activeSamplesList)
        assMatricesList.append(assSampAv)


    # Use STATIS-X function
    # statisMethod(listHoldingMatrices, choice)
    # choice = 0: statis based on covariance
    # choice = 1: statis based on correlation    
    results = statisX(assMatricesList, selection)
    if results == None: 
        dlg = wx.MessageDialog(None, 'Error in code. Wrong selection choice.',
                               'Error Message',
                               wx.OK | wx.ICON_INFORMATION)
        dlg.ShowModal()
        dlg.Destroy()
        return
    
    
    averageMatrixForAnalysis = results[0] # consensus
    
    resultList = []
    
    
    numerical_data_add_average_mat(resultList, averageMatrixForAnalysis, activeAttributesList, activeSamplesList)
    
            
    frameName = "STATIS Consensus Data (Covariance)"
    if selection == 1:
        frameName = "STATIS Consensus Data (Correlation)"
    return frameName, resultList
