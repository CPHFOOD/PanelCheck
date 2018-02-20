#!/usr/bin/env python


from Plot_Tools import *

##from IPython.Shell import IPShellEmbed
##ipshell = IPShellEmbed()



def getTucker1Matrix(s_data, plot_data, selection):
    numberOfAssessors = len(plot_data.activeAssessorsList)
    numberOfAttributes = len(plot_data.activeAttributesList)
    numberOfSamples = len(plot_data.activeSamplesList)
    
    numberOfReplicates = len(s_data.ReplicateList)


    if selection[1] == 1: # model based on sample replicates
            Tucker1Matrix = zeros((numberOfSamples, numberOfAssessors * numberOfAttributes * numberOfReplicates), float)
            #print Tucker1Matrix
            x_len_tot = 0

            for assessor in plot_data.activeAssessorsList:
                for replicate in s_data.ReplicateList:
                    ass_rep_mat = s_data.GetAssessorDataAs2DARRAY(active_samples=plot_data.activeSamplesList, active_attributes=plot_data.activeAttributesList, active_replicates=[replicate], active_assessor=assessor)
                    #print ass_rep_mat
                    [y_len, x_len] = shape(ass_rep_mat)
                    Tucker1Matrix[:, x_len_tot:(x_len_tot+x_len)] = ass_rep_mat[:,:]

                    x_len_tot += x_len


    elif selection[1] == 0: # model based on sample averages
            Tucker1Matrix = zeros((numberOfSamples, numberOfAssessors * numberOfAttributes), float)

            for assessor in plot_data.activeAssessorsList:
                #print
                #print assessor

                for attribute in plot_data.activeAttributesList:
                    #print "---", attribute

                    for sample in plot_data.activeSamplesList:
                        #print "******", sample

                        sumReplicates = 0
                        for replicate in s_data.ReplicateList:
                            oneReplicate = s_data.SparseMatrix[(assessor, sample, replicate)]
                            positionSpecificAttribute = s_data.AttributeList.index(attribute)
                            valueSpecificAttribute = float(oneReplicate[positionSpecificAttribute])

                            sumReplicates = sumReplicates + valueSpecificAttribute

                        sampleAverage = sumReplicates / numberOfReplicates
                        #print sampleAverage

                        # Retrieve position in Matrix that is to be filled with
                        # average value
                        objectPosition = plot_data.activeSamplesList.index(sample)
                        variablePosition = plot_data.activeAssessorsList.index(assessor) * numberOfAttributes + plot_data.activeAttributesList.index(attribute)
                        Tucker1Matrix[objectPosition, variablePosition] = sampleAverage            
        
        
    leaveOutAttributes = []; newActiveAttributesList = []
    if selection[0] == 1:

        inputMatrix = Tucker1Matrix.copy()
        variableMean = average(inputMatrix, 0)
        standardDev = STD(inputMatrix, 0)


        # Go through all values in each column
        # and search for STD = 0
        leaveOutColumns = []
        for stdval in range(len(standardDev)):
            if standardDev[stdval] == 0:
                leaveOutColumns.append(stdval)




        #print 'leaveOutColumns: ', leaveOutColumns
        for col in leaveOutColumns:
            multiplyFactor = col / len(plot_data.activeAttributesList)

            attPosition = col - (multiplyFactor * len(plot_data.activeAttributesList))
            if plot_data.activeAttributesList[attPosition] not in leaveOutAttributes:
                leaveOutAttributes.append(plot_data.activeAttributesList[attPosition])



        for attribute in plot_data.activeAttributesList:
            if attribute not in leaveOutAttributes:
                newActiveAttributesList.append(attribute)

        # Changing activeAttributeList, that is leaving out the specific attributes
        # that cause division error under standardization
        # Need to do it this way, because plotting routines use 'activeAttributesList'
        # all the time.



        if selection[1] == 1: # model based on sample replicates
            # From here the Tucker-1 matrix is build anew without the specific attributes that cause
            # division error in the standardization process
            Tucker1Matrix = zeros((numberOfSamples, numberOfAssessors * len(newActiveAttributesList) * numberOfReplicates), float)
            x_len_tot = 0

            for assessor in plot_data.activeAssessorsList:
                for replicate in s_data.ReplicateList:
                    ass_rep_mat = s_data.GetAssessorDataAs2DARRAY(active_samples=plot_data.activeSamplesList, active_attributes=newActiveAttributesList, active_replicates=[replicate], active_assessor=assessor)
                    #print ass_rep_mat
                    [y_len, x_len] = shape(ass_rep_mat)
                    Tucker1Matrix[:, x_len_tot:(x_len_tot+x_len)] = ass_rep_mat[:,:]

                    x_len_tot += x_len     



        elif selection[1] == 0: # model based on sample averages

            # From here the Tucker-1 matrix is build anew without the specific attributes that cause
            # division error in the standardization process
            Tucker1Matrix = zeros((numberOfSamples, numberOfAssessors * len(newActiveAttributesList)), float)


            # Construction the new Tucker1-matrix, but this time without those
            # attributes that one or more assessors have STD = 0
            for assessor in plot_data.activeAssessorsList:

                for attribute in newActiveAttributesList:

                    for sample in plot_data.activeSamplesList:

                        sumReplicates = 0
                        for replicate in s_data.ReplicateList:
                            oneReplicate = s_data.SparseMatrix[(assessor, sample, replicate)]
                            positionSpecificAttribute = s_data.AttributeList.index(attribute)
                            valueSpecificAttribute = float(oneReplicate[positionSpecificAttribute])

                            sumReplicates = sumReplicates + valueSpecificAttribute

                        sampleAverage = sumReplicates / numberOfReplicates
                        #print sampleAverage

                        # Retrieve position in Matrix that is to be filled with
                        # average value
                        objectPosition = plot_data.activeSamplesList.index(sample)
                        variablePosition = plot_data.activeAssessorsList.index(assessor) * len(newActiveAttributesList) + newActiveAttributesList.index(attribute)
                        Tucker1Matrix[objectPosition][variablePosition] = sampleAverage        


    #print Tucker1Matrix

    return Tucker1Matrix, newActiveAttributesList, leaveOutAttributes


def Tucker1PCA(Tucker1Matrix, selection):
	if selection[0] == 1:
	    scores, loadings, explVar = PCA(Tucker1Matrix, standardize=True)
	else:
	    scores, loadings, explVar = PCA(Tucker1Matrix, standardize=False)

	explVar = list(explVar)
	
	return scores, loadings, explVar


def Tucker1Plotter(s_data, plot_data, num_subplot=[1,1,1], selection=[0,0], pc_x=0, pc_y=1):
    """
    This function generates the Tucker-1 plots, both Common Score Plot,
    Correlation Loadings focused on assessor and Correlation Loadings focused
    on attributes.
    
    @type selection: int
    @param selection: PCA mode selection
    
    
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

    activeAssessorsList = plot_data.activeAssessorsList[:]
    activeAttributesList = plot_data.activeAttributesList[:]
    activeSamplesList = plot_data.activeSamplesList[:]
    itemID = plot_data.tree_path  


    # Construction of Tucker1-matrix, where assessor matrices are 
    # put beside each other starting with assessor1, then assessor 2
    # and so on
    PCAmodeSelected = selection
    numberOfAssessors = len(activeAssessorsList)
    numberOfAttributes = len(activeAttributesList)
    numberOfSamples = len(activeSamplesList)
    numberOfReplicates = len(s_data.ReplicateList)
    pointAndLabelList = []
    
   
    
    # Create a list with active (checked in CheckListBox) assessors/attributes
    # that is chronologically sorted as in original file. Just doing
    # .keys() and .sort() is not enough, since only alphabetical order
    # is given. 

    
    # Constructs a list that contains all active assessors AND attributes AND
    # 'Common Scores'.
    # This is necessary for easier check whether double clicked item
    # can be plotted or a error message must be shown.
    collectedActiveItemsList = activeAssessorsList[:]
    collectedActiveItemsList.extend(activeAttributesList[:])
    collectedActiveItemsList.append(u'Common Scores')
    
    
    # Check wether the selected item is in the collectedActiveItemsList.
    # If not, an error message is activated.
    if itemID[0] not in collectedActiveItemsList:
        dlg = wx.MessageDialog(None, 'The assessor or attribute is not active in CheckBox',
                               'Error Message',
                               wx.OK | wx.ICON_INFORMATION)
        dlg.ShowModal()
        dlg.Destroy()

    else:
        # Calculation have requirements, test: activeSamplesList must have minimum 2 values
        if len(activeSamplesList) < 3:
            dlg = wx.MessageDialog(None, 'Minimum 3 samples needed.',
                               'Error Message',
                               wx.OK | wx.ICON_INFORMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        # Calculation have requirements, test: numberOfReplicates must be minimum 2
        if numberOfAttributes < 1:
            dlg = wx.MessageDialog(None, 'There must be a minimum of 1 attribute.',
                               'Error Message',
                               wx.OK | wx.ICON_INFORMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        
        
        # Continue here if no error message
        # ---------------------------------
        # Fill the Tucker1Matrix with values averaged over replicates
        
##        fileNameTucker1 = 'Tucker1Matrix.txt'
##        output = open(fileNameTucker1, 'w')
        
        newActiveAttributesList_old = []; calculated = False
        print(plot_data.Scores)
        print(type(plot_data.Scores))
        if not (plot_data.Scores is None):
            print 'hi'    
            calculated = True
        
        print PCAmodeSelected
	
	# If the user selects standardization of data for Tucker-1
	# This is a procedure to check which attributes have to be left out
	# before being sent to the PCA class
	# In the process the Tucker-1 matrix will be built again without
	# those specific attributes.        
        if not calculated or PCAmodeSelected[0] == 1:        
                Tucker1Matrix, newActiveAttributesList, leaveOutAttributes  = getTucker1Matrix(s_data, plot_data, PCAmodeSelected)
		
                #print plot_data.newActiveAttributesList
                #print newActiveAttributesList
	        
	        if plot_data.newActiveAttributesList != None and len(plot_data.newActiveAttributesList) > 0:
	            newActiveAttributesList_old = plot_data.newActiveAttributesList
                    
                    if itemID[0] in activeAttributesList and itemID[0] not in newActiveAttributesList:
			message = itemID[0] + ' was left out of the analysis because for one or \nmore assessors the standard deviation is 0: \n'

			dlg = wx.MessageDialog(None, message,
					   'Important information',
					   wx.OK | wx.ICON_INFORMATION)
			dlg.ShowModal()
			dlg.Destroy()                    
                    
	            if equal_lists(newActiveAttributesList_old, newActiveAttributesList):
	                print newActiveAttributesList_old
	                activeAttributesList = newActiveAttributesList_old
	                calculated = True # use calculated values
	            else:
	                calculated = False
	        else:
	            calculated = False
	        
	        if not calculated and selection[0] == 1:

		    # Changing activeAttributeList, that is leaving out the specific attributes
		    # that cause division error under standardization
		    # Need to do it this way, because plotting routines use 'activeAttributesList'
		    # all the time.
                    

		    # If user double-clicks on an attribute in control tree which is
		    # left out from analysis, then show message window
		    if itemID[0] in leaveOutAttributes:
			message = itemID[0] + ' was left out of the analysis because for one or \nmore assessors the standard deviation is 0: \n'

			dlg = wx.MessageDialog(None, message,
					   'Important information',
					   wx.OK | wx.ICON_INFORMATION)
			dlg.ShowModal()
			dlg.Destroy()
			if not plot_data.overview_plot:
			    return


		    # If some attributes had to be left out then inform user
		    if len(leaveOutAttributes) > 0:
			messagePart1 = 'The following attributes were left out of the analysis because \nfor one or more assessors the standard deviation is 0: \n'

			messagePart2 = leaveOutAttributes[0]
			for atts in leaveOutAttributes:
			    if messagePart2 == atts:
				pass
			    else:
				messagePart2 = messagePart2 + ', ' + atts

			messagePart3 = '\n\nPlease uncheck these attributes to avoid this message.\nYou can activate them again when standardization is switched off.'

			message = messagePart1 + messagePart2 + messagePart3

			dlg = wx.MessageDialog(None, message,
					   'Important information',
					   wx.OK | wx.ICON_INFORMATION)
			dlg.ShowModal()
			dlg.Destroy()
			if len(activeAttributesList) == 0: return
		    
		    activeAttributesList = newActiveAttributesList[:]
			
		    plot_data.newActiveAttributesList = newActiveAttributesList[:] # re-calculation needed
		    
		    


        if calculated: # use calculated values:
            
		scores = plot_data.Scores
		loadings = plot_data.Loadings
		explVar = plot_data.E
        	
        	corrLoadings = plot_data.CorrLoadings
	        transCorrLoadings = transpose(corrLoadings) 
	        
		rawDataList = plot_data.raw_data
		
		# first part
		resultList1 = plot_data.numeric_data_tucker1matrix
		
		maxPCs = plot_data.max_PCs


        else: # values not calculated yet

                scores, loadings, explVar = Tucker1PCA(Tucker1Matrix, selection)
	
                plot_data.Scores = scores
        	plot_data.Loadings = loadings
        	plot_data.E = explVar  
        	
        	corrLoadings = CorrelationLoadings(Tucker1Matrix, scores)
        	plot_data.CorrLoadings = corrLoadings 
	        transCorrLoadings = transpose(corrLoadings)       
		       
		# Continue building resultList
		# Limiting PC's in 'Numeric Results' to 10
		[PCs, Tucker1Attributes] = shape(corrLoadings)
		[Samples, PCs] = shape(scores)
		
		maxPCs = 10
		[samples, PCs] = shape(scores)
		if PCs < maxPCs:
	            maxPCs = PCs     
        

		# Start of generating the resultList for case that standardization
		# is NOT activated (this before PCA analysis, because Tucker1Matrix
		# will be changed/standardized in PCA class)
	        if selection[0] == 0:
	
		    resultList1 = []
		    emptyLine = ['']

		    # This constructs the resultList that shows the sample scores
		    # in 'Show Data'
		    headerLine = ['TUCKER-1 MATRIX:']
		    resultList1.append(headerLine)

		    matrixHeaderLine = ['']

                    if selection[1] == 0: # model based on sample averages
                            for assessor in activeAssessorsList:

                                for attribute in activeAttributesList:

                                    columnHeader = assessor + ' - ' + attribute
                                    matrixHeaderLine.append(columnHeader)


                    elif selection[1] == 1: # model based on sample replicates
                            for assessor in activeAssessorsList:

                                for attribute in activeAttributesList:

                                    for rep in s_data.ReplicateList:
                                        columnHeader = assessor + ' - ' + rep + ' - ' + attribute
                                        matrixHeaderLine.append(columnHeader)

		    resultList1.append(matrixHeaderLine)

		    for sample in activeSamplesList:
			sampleRow = [sample]
			for x in Tucker1Matrix[activeSamplesList.index(sample)]:
			    sampleRow.append(num2str(x, fmt="%.2f"))
			resultList1.append(sampleRow)

		    resultList1.append(emptyLine)
		    resultList1.append(emptyLine)
		    resultList1.append(emptyLine)


		# selection has to be increased by one, since in the GUI
		# selections are RawData = 0 and Standardized = 1
		# In the PCA module PCA on mean-centered data = 1 and 
		# PCA on standardized data = 2
		# that is: RawData (in GUI) = PCA on mean-centered data in PCA module
		#          Standardized (in GUI) = PCA on standardized data in PCA module
		#PCAanalysis = PCA(Tucker1Matrix, selection + 1)
		#scores = PCAanalysis.GetScores()
		#corrLoadings = PCAanalysis.GetCorrelationLoadings()
		#transCorrLoadings = transpose(corrLoadings)
		#explVar = PCAanalysis.GetExplainedVariances()
		#print corrLoadings[0:3] 
	
        
		# Start of generating the resultList for case that standardization
		# IS activated
		if selection[0] == 1:
		    resultList1 = []
		    emptyLine = ['']

		    # This constructs the resultList that shows the sample scores
		    # in 'Show Data'
		    headerLine = ['TUCKER-1 MATRIX:']
		    resultList1.append(headerLine)

		    matrixHeaderLine = ['']

                    if selection[1] == 0: # model based on sample averages
                            for assessor in activeAssessorsList:

                                for attribute in activeAttributesList:

                                    columnHeader = assessor + ' - ' + attribute
                                    matrixHeaderLine.append(columnHeader)


                    elif selection[1] == 1: # model based on sample replicates
                            for assessor in activeAssessorsList:

                                for attribute in activeAttributesList:

                                    for rep in s_data.ReplicateList:
                                        columnHeader = assessor + ' - ' + rep + ' - ' + attribute
                                        matrixHeaderLine.append(columnHeader)

		    resultList1.append(matrixHeaderLine)

		    for sample in activeSamplesList:
			sampleRow = [sample]
			for x in Tucker1Matrix[activeSamplesList.index(sample)]:
			    sampleRow.append(num2str(x, fmt="%.2f"))
			resultList1.append(sampleRow)

		    resultList1.append(emptyLine)
		    resultList1.append(emptyLine)
		    resultList1.append(emptyLine)


		# Starting generation of the list that contains the raw data
		# that is shown in "Raw Data" when pushing the button in the plot
		rawDataList = []
		emptyLine = ['']
		headerRawData = ['Raw Data']
		underline = ['========']
		rawDataList.append(headerRawData)
		rawDataList.append(underline)
		rawDataList.append(emptyLine)

		attributeLine = ['Assessor', 'Sample', 'Replicate']
		attributeLine.extend(activeAttributesList)
		rawDataList.append(attributeLine)
		emptyLine = ['']

		for assessor in activeAssessorsList:

		    for sample in activeSamplesList:

			for replicate in s_data.ReplicateList:

			    attributeValues = []
			    for attribute in activeAttributesList:
				singleAttributeValue = s_data.SparseMatrix[(assessor, sample, replicate)][s_data.AttributeList.index(attribute)]
				attributeValues.append(singleAttributeValue)

			    dataLine = [assessor, sample, replicate]
			    dataLine.extend(attributeValues)
			    rawDataList.append(dataLine)
        
                
                rawDataList = raw_data_grid(s_data, plot_data)
                
                plot_data.numeric_data_tucker1matrix = resultList1
        
        
        frame_colored = False
	view_legend = False
	if itemID[0] in activeAttributesList:
	    view_legend = plot_data.view_legend
        plot_data.view_legend = view_legend
        
        
   
        resultList = deepcopy(resultList1)
        
        # Figure
        replot = False; subplot = plot_data.overview_plot
        if plot_data.fig != None: replot = True
        else: plot_data.fig = Figure(None)
        if subplot: # is subplot
            plot_data.ax = plot_data.fig.add_subplot(num_subplot[0], num_subplot[1], num_subplot[2], aspect=plot_data.aspect)
        else: plot_data.ax = axes_create(view_legend, plot_data.fig, aspect=plot_data.aspect)
        ax = plot_data.ax; fig = plot_data.fig
        
        # This is the switch between 'Common Scores' plot and the correlation
        # loadings plot.
        if itemID[0] == u'Common Scores':
            # Here the construction of the common score plot starts
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
            myTitle = 'Tucker1 - common scores: '
            xAx = 'PC'+str(pc_x+1)+' (' + str(round(explVar[pc_x] * 100, 1)) + '%)'
            yAx = 'PC'+str(pc_y+1)+' (' + str(round(explVar[pc_y] * 100, 1)) + '%)'
            
            axes_setup(ax, xAx, yAx, myTitle, [x_min, x_max, y_min, y_max])
            
            scores_x = []
            for element in scoresXCoordinates: scores_x.append(element[0])
            scores_y = []
            for element in scoresYCoordinates: scores_y.append(element[0])
            
            ax.scatter(scores_x, scores_y, s=25, c='b', marker='s')
            ax.plot(ax.get_xlim(), [0, 0], 'b--')
            ax.plot([0, 0], ax.get_ylim(), 'b--')
            
            font_size = 11
            if plot_data.overview_plot: font_size=9
            font = {'family'     : 'sans-serif',
                        'color'      : 'k',
                        'weight' : 'normal',
                        'size'   : font_size,
                        }
            
            for sample in range(len(activeSamplesList)):
                
                textXCoord = scoresXCoordinates[sample] + (x_max + abs(x_min)) * 0.015
                textYCoord = scoresYCoordinates[sample] - (y_max + abs(y_min)) * 0.01
                
                #print activeSamplesList[sample], textXCoord, textYCoord
                
                
                ax.text(textXCoord[0], textYCoord[0], 
                        activeSamplesList[sample],
                        font)
                pointAndLabelList.append([scoresXCoordinates[sample], scoresYCoordinates[sample], "Common Scores: " + activeSamplesList[sample], [activeSamplesList[sample]] ])
                        
            
            
            numerical_data_add_scores(scores, activeSamplesList, maxPCs, resultList, header_txt="COMMON SCORES:")
            
            
            resultList.append([''])
            resultList.append([''])
            resultList.append([''])
            
            
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
            
                                  
            #update plot-data variables:
            plot_data.point_lables = pointAndLabelList
            plot_data.raw_data = rawDataList
            plot_data.numeric_data = resultList
            plot_data.plot_type = "tucker1"
            plot_data.special_opts["dclick_plot"] = "line_samp"
            plot_data.point_lables_type = 0
            plot_data.max_PCs = maxPCs 
            plot_data.selection = PCAmodeSelected
            
        else:
            
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
            # Unsing 'scatter' instead of 'plot', since this allows sizable points
            # in plot
            xCorrLoadings = corrLoadings[pc_x]
            yCorrLoadings = corrLoadings[pc_y]
            #ax.plot(xCorrLoadings, -yCorrLoadings, 'ro')
            #print type(xCorrLoadings)
            #print "****************************"
            #print corrLoadings[0]
            #print "****************************"
            #print shape(corrLoadings[0]) 
            #ipshell()
            ax.scatter(xCorrLoadings, yCorrLoadings, s=10, color='#ffffff', marker='o', edgecolor='#888888')
               
            
            # Plot the specific assessor/attribute:
            # First the case when an assessor is selected
            
            # In case of a selected assessor
            if itemID[0] in activeAssessorsList:
                # Find out where in the activeAssessorList the selected assessor is.
                # Depending on the position the correlation loadings will be picked.
                specificPositionAssessor = activeAssessorsList.index(itemID[0])
                
                lowerLimit = specificPositionAssessor * len(activeAttributesList)
                upperLimit = (specificPositionAssessor * len(activeAttributesList)) + len(activeAttributesList)
                
                specificAssessorXCoordinates = corrLoadings[pc_x][lowerLimit:upperLimit]
                specificAssessorYCoordinates = corrLoadings[pc_y][lowerLimit:upperLimit]
                
                # Plot one correlation loading pair (PC1, PC2) at a time. In this
                # way those pairs with (0,0) can be left out. (0,0) should actually
                # be 'NaN', but they got the value 0 in the PCA routine for simplicity
                # reasons.
                for coords in range(len(specificAssessorXCoordinates)):
                    if (specificAssessorXCoordinates[coords] == 0) and (specificAssessorXCoordinates[coords] == 0):
                        pass
                    else:
                        spesAssXCoord = specificAssessorXCoordinates[coords]
                        spesAssYCoord = specificAssessorYCoordinates[coords]
                        
                        width = 25
                        if plot_data.overview_plot: width = 15
                        ax.scatter([spesAssXCoord], [spesAssYCoord], s=width, c='r', marker='o')
                        
                        textXCoord = spesAssXCoord + 0.025
                        textYCoord = spesAssYCoord - 0.015
                        
                        font_size = 13
                        if plot_data.overview_plot: font_size = 9
                        font = {'family'     : 'monospace',
                                'color'      : 'red',
                                'weight' : 'normal',
                                'size'   : font_size,
                                }
                        
                        ax.text(textXCoord, textYCoord, 
                                activeAttributesList[coords],
                                font)
                           
                        # adding to pointAndLabelList 
                        #pointAndLabelList.append([spesAssXCoord, spesAssYCoord, activeAttributesList[coords]])
            
            
            # In case of a selected attribute
            elif itemID[0] in activeAttributesList:
            
                
                #print itemID[0]
                print selection
                
                frame_colored = colored_frame(s_data, plot_data, activeAttributesList, itemID[0])
                
                if selection[1] == 0:
                        # Find out where in the activeAttributeList the selected attribute is.
                        # Depending on the position the correlation loadings will be picked.
                        specificPositionAttribute = activeAttributesList.index(itemID[0])

                        # specificAttributeSequence contains the correct positions of the
                        # columns in the corrLoadings-matrix for each assessor.
                        specificAttributeSequence = []
                        for position in range(numberOfAssessors):
                            newPosition = position * len(activeAttributesList) + specificPositionAttribute
                            specificAttributeSequence.append(newPosition)

                        # Plot the selected attribute one at a time (PC1, PC2). 
                        for coords in specificAttributeSequence:
                            spesAttXCoord = corrLoadings[pc_x][coords]
                            spesAttYCoord = corrLoadings[pc_y][coords]
                            specificAssessor = specificAttributeSequence.index(coords)

                            # If the coordinates were (0,0) then they actually should
                            # have been 'Nan'. This happens in the PCA module.
                            if (spesAttXCoord == 0) and (spesAttYCoord == 0):
                                pass
                            else:
                                width = 65
                                if plot_data.overview_plot: width = 35
                                ax.scatter([spesAttXCoord], [spesAttYCoord], s=width, c='m', marker='d')

                                textXCoord = spesAttXCoord + 0.025
                                textYCoord = spesAttYCoord - 0.015

                                font_size = 13
                                if plot_data.overview_plot: font_size = 9
                                font = {'family'     : 'monospace',
                                        'color'      : 'm',
                                        'weight' : 'normal',
                                        'size'   : font_size,
                                        }

                                ax.text(textXCoord, textYCoord, 
                                        activeAssessorsList[specificAssessor],
                                        font)
                                
                        # adding to pointAndLabelList 
                        #pointAndLabelList.append([spesAttXCoord, spesAttYCoord, activeAssessorsList[specificAssessor]])
            
                elif selection[1] == 1:
                
                        print "sample replicates"
                        #print len(activeAssessorsList) * len(s_data.ReplicateList)
                        #print 
                        #print len(corrLoadings[pc_x])
                        #print len(corrLoadings[pc_y])

                        # Find out where in the activeAttributeList the selected attribute is.
                        # Depending on the position the correlation loadings will be picked.
                        specificPositionAttribute = activeAttributesList.index(itemID[0])

                        # specificAttributeSequence contains the correct positions of the
                        # columns in the corrLoadings-matrix for each assessor.
                        specificAttributeSequence = []
                        counter = 0
                        
                        for ass in activeAssessorsList:
                            for rep_ind in range(len(s_data.ReplicateList)):

                                newPosition = counter * len(activeAttributesList) + specificPositionAttribute
                                specificAttributeSequence.append([newPosition, ass + '-' + str(rep_ind+1)])
                                counter += 1                     
                        
                        

                        print specificAttributeSequence


                        # Plot the selected attribute one at a time (PC1, PC2). 
                        for coords in specificAttributeSequence:
                            #if coords[0] > len(corrLoadings[pc_x])-1 or coords[0] > len(corrLoadings[pc_y])-1:
                            #    break
                                
                            spesAttXCoord = corrLoadings[pc_x][coords[0]]
                            spesAttYCoord = corrLoadings[pc_y][coords[0]]

                            # If the coordinates were (0,0) then they actually should
                            # have been 'Nan'. This happens in the PCA module.
                            if (spesAttXCoord == 0) and (spesAttYCoord == 0):
                                pass
                            else:
                                width = 65
                                if plot_data.overview_plot: width = 35
                                ax.scatter([spesAttXCoord], [spesAttYCoord], s=width, c='m', marker='d')

                                textXCoord = spesAttXCoord + 0.02
                                textYCoord = spesAttYCoord - 0.022

                                font_size = 13
                                if plot_data.overview_plot: font_size = 9
                                font = {'family'     : 'monospace',
                                        'color'      : 'm',
                                        'weight' : 'normal',
                                        'size'   : font_size,
                                        }

                                ax.text(textXCoord, textYCoord, 
                                        coords[1],
                                        font)           

            
            # Defining the titles, axes names, etc
            myTitle = 'Tucker1 - correlation loadings: ' + itemID[0]
            xAx = 'PC'+str(pc_x+1)+' (' + str(round(explVar[pc_x] * 100, 1)) + '%)'
            yAx = 'PC'+str(pc_y+1)+' (' + str(round(explVar[pc_y] * 100, 1)) + '%)'
            
            if not plot_data.overview_plot:
                axes_setup(ax, xAx, yAx, myTitle, [-1, 1, -1, 1])
            else:
                myTitle = 'Tucker1 - corr. loadings: ' + itemID[0]
                axes_setup(ax, "", "", myTitle, [-1, 1, -1, 1], font_size=10)
                
            
            if frame_colored and itemID[0] in activeAttributesList:
                significance_legend(plot_data)
                

            
            matrixHeaderLine = ['']
            emptyLine = ['']
            pointAndLabelSelection = []
            
            
            if selection[1] == 0: # model based on sample averages
                    for assessor in activeAssessorsList:

                        for attribute in activeAttributesList:

                            columnHeader = assessor + ' - ' + attribute
                            matrixHeaderLine.append(columnHeader)
                            pointAndLabelSelection.append([assessor, attribute])
                            
                            
            elif selection[1] == 1: # model based on sample replicates
                    for assessor in activeAssessorsList:

                        for attribute in activeAttributesList:
                            
                            for rep in s_data.ReplicateList:
                                columnHeader = assessor + ' - ' + rep + ' - ' + attribute
                                matrixHeaderLine.append(columnHeader)
                                pointAndLabelSelection.append([assessor, attribute])                
            
            
            #for points and labels:
            xCorrs = corrLoadings[pc_x]
            yCorrs = corrLoadings[pc_y]
            for i in range(len(xCorrs)):
                pointAndLabelList.append([xCorrs[i],yCorrs[i], matrixHeaderLine[i+1], pointAndLabelSelection[i]])
                
            
            headerLine = ['CORRELATION LOADINGS:']
            resultList.append(headerLine)         
            resultList.append(matrixHeaderLine)
            
            for PC in range(1, maxPCs + 1):
                PCrow = ['PC ' + str(PC)]
                #print PC, PCrow
                PCrow.extend(str_row(corrLoadings[PC - 1], fmt="%.3f"))
                resultList.append(PCrow)
                        
            
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
            
            #update plot-data variables:
            plot_data.point_lables = pointAndLabelList
            plot_data.raw_data = rawDataList
            plot_data.numeric_data = resultList
            plot_data.plot_type = "tucker1"
            plot_data.special_opts["dclick_plot"] = "corr"
            plot_data.point_lables_type = 0
            plot_data.max_PCs = maxPCs
            plot_data.selection = PCAmodeSelected
        
        
        #Frame draw, for standard Matplotlib frame only use show()
        return plot_data


def Tucker1AssOverviewPlotter(s_data, plot_data, pca_mode_select):
    # Overview plot #  
    itemID_list = [] # takes part in what to be plotted (tree path)
    for ass in plot_data.activeAssessorsList:
        itemID_list.append([ass])
    return OverviewPlotter(s_data, plot_data, itemID_list, Tucker1Plotter, plot_data.activeAssessorsList, special_selection=pca_mode_select)    



def Tucker1AttOverviewPlotter(s_data, plot_data, pca_mode_select):
    # Overview plot #
    itemID_list = [] # takes part in what to be plotted (tree path)
    for att in plot_data.activeAttributesList:
        itemID_list.append([att])
    return OverviewPlotter(s_data, plot_data, itemID_list, Tucker1Plotter, plot_data.activeAttributesList, special_selection=pca_mode_select)
    
  