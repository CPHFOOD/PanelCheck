#!/usr/bin/env python

from numpy import average, array, ndarray, vstack, zeros, transpose, asarray

class SensoryData:
    def __init__(self, abspath):
        """
        The SensoryData class for PanelCheck
        
        @type abspath:     string
        @param abspath:    Absolute file-path for the data file to be read.
        """
        
        # absolute file path
        self.abspath = abspath
        # file name
        self.filename = ""
        # character codec set	
        self.codec = "mbcs" # extended latin-1  (might be changed during data load)
         
        self.scale_limits = () # (x_min, x_max, y_min, y_max) scale limits (to be used in some plots)
        self.real_limits = () # (x_min, x_max, y_min, y_max)    
        self.AssessorList = []
        self.SampleList = []
        self.ReplicateList = []
        self.AttributeList = []
        
        # column indices:
        self.ass_index = 0
        self.samp_index = 1
        self.rep_index = 2
        self.value_index = 3 # where score-values start
        
        self.LabelList = []
        self.ListCollection = []
        self.Matrix = []
        
        # missing values positions
        self.mv_pos = {}
        self.mv_inf = {}
        self.has_mv = False
        
        # dictionary, self.SparseMatrix[(assessor, sample, replicate)] will point to ndarray (numpy array)
        self.SparseMatrix = {}



    def MatrixData(self):
        """
        Creates and returns the loaded data in an array.
        """
        if len(self.Matrix) < 1:
            # Get rid of labels in each list collection
            # Needs to be done since labels can be text
            newListCollection = []
            for eachList in self.ListCollection:
                newList = eachList[3:]
                newListCollection.append(newList)

        
            # Get dimensions/size of loaded data
            numRows = len(newListCollection)
            numCols = len(newListCollection[0])
        
        
            # Create new array with the size of the loaded data (from file)
            # containing zeros. 
            self.Matrix = zeros((numRows,numCols), float)
        
        
            # Fill the array with the loaded data from Matrix
            for rows in range(0, numRows):
                for cols in range(0, numCols):
                    self.Matrix[rows][cols] = float(newListCollection[rows][cols])
                    
        return self.Matrix

    def MatrixLables(self):
        """
        Returns lables of the loaded data in an array.
        """

        # Get rid of labels in each list collection
        # Needs to be done since labels can be text
        self.newListCollection = []
        for eachList in self.ListCollection:
            newList = eachList[0:3]
            self.newListCollection.append(newList)

        self.lablesMatrix = asarray(self.newListCollection)

        return self.lablesMatrix
        
    
    def MatrixDataSelected(self, assessors=[], attributes=[], samples=[]):
        """
        Creates and returns the loaded data in an array.
        """
        if len(assessors) < 1: assessors = self.AssessorList
        if len(attributes) < 1: attributes = self.AttributeList
        if len(samples) < 1: samples = self.SampleList        
       
        scores_selected_matrix = zeros((1, len(attributes)), float)
        for assessor in assessors:
            for sample in samples:
	        for replicate in self.ReplicateList:
		    scoresVector = self.SparseMatrix[assessor, sample, replicate]
                    scoresVectorFloats = []

                    for att in attributes:
                        _index = self.AttributeList.index(att)
                        scoresVectorFloats.append(scoresVector[_index])
                    scores_selected_matrix = vstack((scores_selected_matrix, array(scoresVectorFloats)))
        
        return scores_selected_matrix[1:,:]
        
        

    def MatrixNumLables(self, assessors=[], samples=[]):
        """
        Returns numeric lables of selected loaded data in an array.
        """
        if len(assessors) < 1: assessors = self.AssessorList
        if len(samples) < 1: samples = self.SampleList
        
        lables_selected_matrix = zeros((1, 3), int)
        for assessor in assessors:
	    for sample in samples:
                for replicate in self.ReplicateList:
		    row = [0, 0, 0]
		    row[self.ass_index] = self.AssessorList.index(assessor)
		    row[self.samp_index] = self.SampleList.index(sample)
		    row[self.rep_index] = self.ReplicateList.index(replicate)
		    lables_selected_matrix = vstack((lables_selected_matrix, array(row, copy=False)))
                    
        return lables_selected_matrix[1:,:]
        
    
    
    def get_MAX_MIN_Values(self):
        """
        Returns a list of maximum and minimum values for x and y scale.
        [x_min, x_max, y_min, y_max]
        """
        self.min_max_values = [-1,1,-1,1]
        self.min_max_values[2] = float(self.SparseMatrix[(self.AssessorList[0],self.SampleList[0],self.ReplicateList[0])][0])
        self.min_max_values[3] = float(self.SparseMatrix[(self.AssessorList[0],self.SampleList[0],self.ReplicateList[0])][0])
        for ass in self.AssessorList:
            for samp in self.SampleList:
                for rep in self.ReplicateList:
                    values = self.SparseMatrix[(ass,samp,rep)]
                    for value in values:
                        if self.min_max_values[2] > float(value):
                            self.min_max_values[2] = float(value) #new y_min value
                        if self.min_max_values[3] < float(value):
                            self.min_max_values[3] = float(value) #new y_max value
        self.min_max_values[0] = 0 #x_min
        self.min_max_values[1] = len(self.AttributeList) + 1 #x_max
        return self.min_max_values
    
    

    def Lables(self):
        """
        Returns list of lables that are contained in data file.
        """
        return self.LabelList
             
        

    
    def Attributes(self):
        """
        Returns list of attributes that are contained in data file.
        """
        return self.AttributeList
    
    
    def Assessors(self):
        """
        Returns list of assessors that are contained in data file.
        """
        return self.AssessorList
    
    
    def Replicates(self):
        """
        Returns list of replicates that are contained in data file.
        """
        return self.ReplicateList


    def Samples(self):
        """
        Returns list of samples that are contained in data file.
        """
        return self.SampleList
    
    
    def SparseMatrixData(self):
        """
        This function returns a spase matrix (e.g. python directory) that
        contains the sensory data. The data can be accessessed by:
        
        SparseMatrix[(Assessor, Sample, Replicate)]
        
        where Assessor, Sample and Replicate are strings. All three of them
        can be fetched from their respective lists.
        """

        return self.SparseMatrix


    def GetAssessorData(self, assessor):
        """
        This function returns the sensory data of an assessor in:
        1. A spase matrix (e.g. python directory) that contains the sensory data
           that can be accessed with a combination of keys (ass,samp,rep)
        2. An array that contains only the numerical values

        sensory = SensoData(filename)
        sparseMatrix, array = sensory.GetAssessorData('assessorX')
        """
        
        specSparseMatrix = {}
        specMatrixDataStrings = []

        for sample in self.SampleList:
            
            for replicate in self.ReplicateList:
                
                specSparseMatrix[(assessor, sample, replicate)] = self.SparseMatrix[(assessor, sample, replicate)]
                specMatrixDataStrings.append(self.SparseMatrix[(assessor, sample, replicate)])

        specMatrixDataList = []
        
        # Convert the list with strings into an array with floats
        for mainList in specMatrixDataStrings:

            subList = []
            for values in mainList:
                numValue = float(values)
                subList.append(numValue)

            specMatrixDataList.append(subList)
                
        specMatrixData = array(specMatrixDataList)

        return specSparseMatrix, specMatrixData
    
    
    
    def GetSampleData(self, sample):
        """
        This function returns the sensory data of a sample in:
        1. A spase matrix (e.g. python directory) that contains the sensory data
           that can be accessed with a combination of keys (ass,samp,rep)
        2. An array that contains only the numerical values

        sensory = SensoData(filename)
        sparseMatrix, array = sensory.GetSampleData('sampleX')
        """

        specSparseMatrix = {}
        specMatrixDataStrings = []

        for assessor in self.AssessorList:

            for replicate in self.ReplicateList:

                specSparseMatrix[(assessor, sample, replicate)] = self.SparseMatrix[(assessor, sample, replicate)]
                specMatrixDataStrings.append(self.SparseMatrix[(assessor, sample, replicate)])

        specMatrixDataList = []

        # Convert the list with strings into an array with floats
        for mainList in specMatrixDataStrings:

            subList = []
            for values in mainList:
                numValue = float(values)
                subList.append(numValue)

            specMatrixDataList.append(subList)

        specMatrixData = array(specMatrixDataList)

        return specSparseMatrix, specMatrixData
    
    
    
    def GetReplicateData(self, replicate):
        """
        This function returns the sensory data of a replicate in:
        1. A spase matrix (e.g. python directory) that contains the sensory data
           that can be accessed with a combination of keys (ass,samp,rep)
        2. An array that contains only the numerical values

        sensory = SensoData(filename)
        sparseMatrix, array = sensory.GetReplicateData('replicateX')
        """

        specSparseMatrix = {}
        specMatrixDataStrings = []

        for assessor in self.AssessorList:

            for sample in self.SampleList:

                specSparseMatrix[(assessor, sample, replicate)] = self.SparseMatrix[(assessor, sample, replicate)]
                specMatrixDataStrings.append(self.SparseMatrix[(assessor, sample, replicate)])

        specMatrixDataList = []

        # Convert the list with strings into an array with floats
        for mainList in specMatrixDataStrings:

            subList = []
            for values in mainList:
                numValue = float(values)
                subList.append(numValue)

            specMatrixDataList.append(subList)

        specMatrixData = array(specMatrixDataList)

        return specSparseMatrix, specMatrixData
    
    
    
    def GetConsensus(self):
        """
        This function returns the consensus matrix, which is the ordinary
        average matrix with sample averages computed over assessors and
        replicates

        sensory = SensoData(filename)
        sparseMatrix, array = sensory.GetConsensus()
        """

        consensusSparseMatrix = {}
        consensusList = []
        
        # Iterate through each sample in sampleList
        for sample in self.SampleList:
            
            # Create first row with zeros to which sample means will be stacked
            # to vertically (first row will be removed afterwards)
            sampleObjects = zeros((1, len(self.AttributeList)), float)
            for assessor in self.AssessorList:
                
                for replicate in self.ReplicateList:
                    
                    # Iteration that convert all scores from string to float
                    # in the list
                    objectWithStrings = self.SparseMatrix[(assessor, sample, replicate)]
                    objectWithFloats = []
                    for item in objectWithStrings:
                        objectWithFloats.append(float(item))

                    # Vertically stack object scores to previous array
                    sampleObjects = vstack((sampleObjects, objectWithFloats))

            # Average without first row with zeros and append means scores array
            # to consensus list
            sampleMean = average(sampleObjects[1:,:].copy(), 0)
            consensusList.append(sampleMean)
            consensusSparseMatrix[sample] = sampleMean

        # Convert list to an array and return
        consensusMatrix = array(consensusList)
        
        return consensusSparseMatrix, consensusMatrix

            

    def GetAssessorAverageMatrix(self, assessor):
        """
        This function returns the a matrix containing sample averages computed
        over replicates for the particular assessor.

        sensory = SensoData(filename)
        sparseMatrix, array = sensory.GetAssessorAverageMatrix('assessorX')
        """

        specSparseMatrix = {}

        # Create first row with zeros to which sample means will be stacked
        # to vertically (first row will be removed afterwards)
        sampleObjects = zeros((1, len(self.AttributeList)), float)

        # Iterate through all samples
        for sample in self.SampleList:

            # Collect replicates and compute average
            repObjects = zeros((1, len(self.AttributeList)), float)
            for replicate in self.ReplicateList:

                scoresVector = self.SparseMatrix[(assessor, sample, replicate)]
                scoresVectorFloats = []

                # Convert scores (type string) into scores (type float)
                for item in scoresVector:
                    item = float(item)
                    scoresVectorFloats.append(item)
                    
                floatsVector = array(scoresVectorFloats)
                repObjects = vstack((repObjects, floatsVector))
                
            sampleAverage = average(repObjects[1:,:].copy(), 0)
            sampleObjects = vstack((sampleObjects, sampleAverage))
            specSparseMatrix[sample] = sampleAverage

        return specSparseMatrix, sampleObjects[1:,:].copy()
        


    def GetAssAverageMatrix(self, assessor, active_attributes, active_samples):
        """
        Returns averaged assessor matrix
        """
        
        cols = len(active_attributes)
        rows = len(active_samples)

        average_ass_matrix = zeros((rows, cols), float)
        reduced_rep_scores = zeros((len(self.ReplicateList), cols), float)

        # Iterate through all samples
        samp_ind = 0
        for sample in active_samples:
            rep_ind = 0
            for replicate in self.ReplicateList:

                scores_vector = self.SparseMatrix[(assessor, sample, replicate)]

                # Collect scores given by active attributes:
                for i in range(len(active_attributes)):
                    att_pos = self.AttributeList.index(active_attributes[i])
                    reduced_rep_scores[rep_ind, i] = scores_vector[att_pos]
                    
                rep_ind += 1
                
            average_ass_matrix[samp_ind, :] = average(reduced_rep_scores[:,:], 0)
            samp_ind += 1

        return average_ass_matrix


    def GetSampleAverageMatrix(self, sample):
        """
        This function returns the a matrix containing the averages of the
        requested sample for each assessor. The averages are calculated for
        each assessor over replicates.

        sensory = SensoData(filename)
        sparseMatrix, array = sensory.GetSampleAverageMatrix('sampleX')
        """

        specSparseMatrix = {}

        # Create first row with zeros to which sample means will be stacked
        # to vertically (first row will be removed afterwards)
        assessorObjects = zeros((1, len(self.AttributeList)), float)

        # Iterate through all assessors
        for assessor in self.AssessorList:

            # Collect replicates and compute average
            repObjects = zeros((1, len(self.AttributeList)), float)
            for replicate in self.ReplicateList:

                scoresVector = self.SparseMatrix[(assessor, sample, replicate)]
                scoresVectorFloats = []

                # Convert scores (type string) into scores (type float)
                for item in scoresVector:
                    item = float(item)
                    scoresVectorFloats.append(item)

                floatsVector = array(scoresVectorFloats)
                repObjects = vstack((repObjects, floatsVector))

            assessorAverage = average(repObjects[1:,:].copy(), 0)
            assessorObjects = vstack((assessorObjects, assessorAverage))
            specSparseMatrix[assessor] = assessorAverage

        return specSparseMatrix, assessorObjects[1:,:].copy()
        
        
        
    def GetSampleMatrix(self, sample, activeAssessorsList, activeAttributesList):
        """
        This function returns the a matrix containing the averages of the
        requested sample for each assessor. The averages are calculated for
        each assessor over replicates.

        sensory = SensoData(filename)
        sparseMatrix, array = sensory.GetSampleAverageMatrix('sampleX')
        """

        # Create first row with zeros to which sample means will be stacked
        # to vertically (first row will be removed afterwards)
        score_matrix = zeros((1, len(activeAttributesList)), float)

        # Iterate through all assessors
        for assessor in activeAssessorsList:

            # Collect replicates and compute average
            repObjects = zeros((1, len(activeAttributesList)), float)
            for replicate in self.ReplicateList:
                scoresVector = self.SparseMatrix[(assessor, sample, replicate)]
                scoresVectorFloats = []

                for att in activeAttributesList:
                    _index = self.AttributeList.index(att)
                    scoresVectorFloats.append(scoresVector[_index])

                floatsVector = array(scoresVectorFloats)
                repObjects = vstack((repObjects[1:,:], floatsVector))
                
            score_matrix = vstack((score_matrix, floatsVector))
        
        return score_matrix[1:,:] # uppermost row is a zeros row



    def GetAttributeData(self, activeAssessorsList, attribute, sample):
        """
        Returns one data-column (as a horizontal ndarray) given by attribute and a sample
        """

        # Create first row with zeros to which sample means will be stacked
        # to vertically (first row will be removed afterwards)
        attributes = []
        _index = self.AttributeList.index(attribute)

        # Iterate through all assessors
        for assessor in activeAssessorsList:
            for replicate in self.ReplicateList:
                attributes.append(self.SparseMatrix[(assessor, sample, replicate)][_index])
        
        return array(attributes) # attribute column for given sample 
        
        
        
    def GetAssessorDataAs2DARRAY(self, active_samples=None, active_attributes=None, active_replicates=None, active_assessor=None):
        """
        Returns data matrix of active data for given assessor.
        """
        
        if active_samples == None: active_samples = self.SampleList
        if active_attributes == None: active_attributes = self.AttributeList
        if active_replicates == None: active_replicates = self.ReplicateList
        
        if active_assessor == None:
            return None # no active assessor
        
        att_indices = []
        for att in active_attributes:
            # the same order as in self.SparseMatrix:
            att_indices.append(self.AttributeList.index(att))
        
        
        m_data = zeros((len(active_samples)*len(active_replicates), len(active_attributes)), float)
        m_data_ind = 0
        
        for samp in active_samples:
            for rep in active_replicates:
                data = self.SparseMatrix[(active_assessor, samp, rep)]
                
                # fill one row in m_data:
                for ind in range(len(active_attributes)):
                    # the same order as in self.SparseMatrix, so variable values will be placed correctly
                    m_data[m_data_ind][ind] = data[att_indices[ind]]
                
                m_data_ind += 1
                
        return m_data
        


    def GetAssessorAveragedDataAs2DARRAY(self, active_samples=None, active_attributes=None, active_replicates=None, active_assessor=None):
        """
        Returns data matrix of active data for given assessor.
        
        @type active_samples: list
        @param active_samples: list of strings (active sample names)
        
        @type active_attributes: list
        @param active_attributes: list of strings (active attribute names)

        @type active_replicates: list
        @param active_replicates: list of strings (active replicate names)

        @type active_assessor: string
        @param active_assessor: the current assessor (name)
        
        @return: numpy array (2-dimensional active data for current assessor)       
        
        """
        
        if active_samples == None: active_samples = self.SampleList
        if active_attributes == None: active_attributes = self.AttributeList
        if active_replicates == None: active_replicates = self.ReplicateList
        
        if active_assessor == None:
            return None # no active assessor
        
        att_indices = []
        for att in active_attributes:
            # the same order as in self.SparseMatrix:
            att_indices.append(self.AttributeList.index(att))
        
        
        m_data = zeros((len(active_samples), len(active_attributes)), float)
        m_data_ind = 0
        
        reps_data = zeros((len(active_replicates), len(active_attributes)), float)
        
        
        for samp in active_samples:
            rep_ind = 0
            for rep in active_replicates:
                row_data = self.SparseMatrix[(active_assessor, samp, rep)]
            
          
                # fill one row in m_data:
                for ind in range(len(active_attributes)):
                    # the same order as in self.SparseMatrix, so variable values will be placed correctly
                    reps_data[rep_ind][ind] = row_data[att_indices[ind]]
                
                rep_ind += 1
            
            #print reps_data
            #print average(reps_data, 0)
            
            m_data[m_data_ind] = average(reps_data, 0)
            m_data_ind += 1
                
        return m_data


    def GetAssessorAverageData(self, assessor):
        """
        This function returns the a matrix containing sample averages computed
        over replicates for the particular assessor.

        sensory = SensoData(filename)
        sparseMatrix, array = sensory.GetAssessorAverageMatrix('assessorX')
        """

        specSparseMatrix = {}

        # Create first row with zeros to which sample means will be stacked
        # to vertically (first row will be removed afterwards)
        sampleObjects = zeros((1, len(self.AttributeList)), float)

        # Iterate through all samples
        for sample in self.SampleList:

            # Collect replicates and compute average
            repObjects = zeros((1, len(self.AttributeList)), float)
            for replicate in self.ReplicateList:

                scoresVector = self.SparseMatrix[(assessor, sample, replicate)]
                scoresVectorFloats = []

                # Convert scores (type string) into scores (type float)
                for item in scoresVector:
#                    print type(item)
#                    print item
#                    print scoresVector
#                    print; print
                    item = float(item)
                    scoresVectorFloats.append(item)

                floatsVector = array(scoresVectorFloats)
                repObjects = vstack((repObjects, floatsVector))

            sampleAverage = average(repObjects[1:,:].copy(), 0)
            sampleObjects = vstack((sampleObjects, sampleAverage))
            specSparseMatrix[sample] = sampleAverage

        return specSparseMatrix, sampleObjects[1:,:].copy()



    def GetAssessorReplicateData(self, assessor, replicate):
        """
        This function returns the sensory data of a specified assessor-replicate
        combination in:
        1. A sparse matrix (e.g. python directory) that contains the sensory data
           that can be accessed with a combination of keys (ass,samp,rep)
        2. An array that contains only the numerical values

        sensory = SensoData(filename)
        sparseMatrix, array = sensory.GetAssessorReplicateData('assessorX', 'replicateY')
        """

        specSparseMatrix = {}
        specMatrixDataStrings = []

        for sample in self.SampleList:

            specSparseMatrix[(assessor, sample, replicate)] = self.SparseMatrix[(assessor, sample, replicate)]
            specMatrixDataStrings.append(self.SparseMatrix[(assessor, sample, replicate)])

        specMatrixDataList = []

        # Convert the list with strings into an array with floats
        for mainList in specMatrixDataStrings:

            subList = []
            for values in mainList:
                numValue = float(values)
                subList.append(numValue)

            specMatrixDataList.append(subList)

        specMatrixData = array(specMatrixDataList)

        return specSparseMatrix, specMatrixData
        
        
    def GetActiveData(self, active_assessors=None, active_attributes=None, active_samples=None, active_replicates=None):
        
        # About return matrix:
        # ====================
        # Each row contains the active variables (sorted equally on each row, by active variables which contains the names).
        #
        # Rows of active variables are sorted firstly by Assessor, secondly by Sample and thirdly by Replicate:
        #
        # first row for:  Assessor1, Sample1, Replicate_1
        # second row for: Assessor1, Sample1, Replicate_2
        # ...
        #                 Assessor1, Sample1, Replicate_N
        #                 Assessor1, Sample2, Replicate_1
        #                 Assessor1, Sample2, Replicate_2
        # ...
        #                 Assessor1, Sample2, Replicate_N
        # ... etc.
        # 
        # for all active samples
        # and for all active assessors
        
        # number of rows     =   len(active_assessors)*len(active_samples)*len(active_replicates)
        # number of columns  =   len(active_attributes)


        if active_samples == None: active_samples = self.SampleList
        if active_assessors == None: active_assessors = self.AssessorList
        if active_attributes == None: active_attributes = self.AttributeList
        if active_replicates == None: active_replicates = self.ReplicateList

        att_indices = []
        for att in active_attributes:
            # the same order as in self.SparseMatrix:
            att_indices.append(self.AttributeList.index(att))

        m_data = zeros((len(active_assessors), len(active_samples), len(active_replicates), len(active_attributes)), float)
        ass_ind = 0
            
        for ass in active_assessors:
            
            samp_ind = 0
            for samp in active_samples:
                
                rep_ind = 0
                for rep in active_replicates:
                
                    data = self.SparseMatrix[(ass, samp, rep)]
                
                    # fill one row in m_data:
                    for ind in range(len(att_indices)):
                        # the same order as in self.SparseMatrix, so variable values will be placed correctly
                        m_data[ass_ind, samp_ind, rep_ind, ind] = data[att_indices[ind]]
                
                    rep_ind += 1
                samp_ind += 1
            ass_ind += 1
        
        
        return m_data
       