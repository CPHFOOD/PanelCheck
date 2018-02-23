#-------------------------------------------------------------------------------
# Name:        mvt.py (missing value tools)
# Purpose:     module containing missing value tools
#
# Author:      Oliver Tomic, Matforsk, Aas, Norway (www.matforsk.no)
#
# Created:     13/09/2007
# Copyright:   (c) Oliver Tomic, 2007
# Licence:     GNU GPL
#-------------------------------------------------------------------------------
#!/usr/bin/env python
import random
import numpy
import numpy.linalg
import pca_module


def RAG(rows, cols):
    """
    This is the Random Array Generator:
    -----------------------------------

    Generates an array with random numbers/floats from a uniform distribution.
    
    INPUT PARAMETERS:
    rows: number of rows of the generated random array
    cols: number of columns of the generated random array
    """

    # Compute total number of elements in random array
    noOfElements = rows * cols


    # Generate the random numbers from a uniform distribution and store in list
    all = []
    for ind in range(noOfElements):
        all.append(random.uniform(0,100))


    # Convert list with random floats into array and reshape into
    # desired dimension
    randArr = numpy.array(all).reshape(rows, cols)
    

    # Return the generated random array
    return randArr




def MVG(arr, perc):
    """
    This is the Missing Values Generator:
    -------------------------------------

    Generates missing values in the submitted array.

    INPUT PARAMETERS:
    arr: submitted array
    perc: percentage of missing values in the submitted array
    """

    # Determine number of rows, columns and total number of elements
    rows, cols = numpy.shape(arr)
    noOfElements = rows * cols


    # Compute number of missing elements based on submitted percentage
    noOfMissingElements = int(round(noOfElements * float(perc)/100, 0))


    # Create a list that holds randomly chosen indices where NaN will be
    # inserted
    indicesList = []
    while 1:
        rand_row = random.randint(0,rows - 1)
        rand_col = random.randint(0,cols - 1)
        newIndexList = [rand_row, rand_col]

        if newIndexList not in indicesList:
            indicesList.append([rand_row, rand_col])

        if len(indicesList) == noOfMissingElements: break


    # Make copy of submitted array and insert NaN's according to indices
    X_missing = arr.copy()

    for ind in indicesList:
        X_missing[ind[0],ind[1]] = numpy.nan


    # Return array with missing values
    return X_missing




def MVA(arr):
    """
    This is the Missing Values Analyser:
    -------------------------------------

    Analyses the submitted array conerning missing values.

    arr: submitted array

    The dictionary contains the following analysis results:

    rowMeans: holds row means of each row without NaN's
    rowComplete: indicates completeness in % of each row

    colMeans: holds column means of each column without NaN's
    colComplete: indicates completeness in % of each column

    noMissing: number of NaN's in array
    percMissing: indicates how many % of array are NaN

    NaNpos: positions/indices of NaN's in array
    grandMean: grand mean of array without NaN's
    
    """

    # Determine number of rows, columns and total number of elements
    rows, cols = numpy.shape(arr)
    noOfElements = rows * cols


    # Compute the row means without the Nan's
    nan_rowMeansList = []
    rowsCompletenessList = []

    for ind in range(rows):

        realNumbers = []
        for subInd in arr[ind, :]:
            if numpy.isfinite(subInd) == True:
                realNumbers.append(subInd)

        nan_rowMean = sum(realNumbers)/len(realNumbers)
        nan_rowMeansList.append(nan_rowMean)

        rowCompleteness = float(len(realNumbers)) / cols * 100
        rowsCompletenessList.append(rowCompleteness)


    # Store results in dictionary
    results = {}
    results['rowMeans'] = nan_rowMeansList
    results['rowComplete'] = rowsCompletenessList


    # Compute the column means without the Nan's
    nan_colMeansList = []
    colsCompletenessList = []

    for ind in range(cols):

        realNumbers = []
        for subInd in arr[:, ind]:
            if numpy.isfinite(subInd) == True:
                realNumbers.append(subInd)

        nan_colMean = sum(realNumbers)/len(realNumbers)
        nan_colMeansList.append(nan_colMean)

        colsCompleteness = float(len(realNumbers)) / rows * 100
        colsCompletenessList.append(colsCompleteness)


    results['colMeans'] = nan_colMeansList
    results['colComplete'] = colsCompletenessList


    # Compute grand mean and locate missing values, percentage of missing values
    # and number of missing values
    realNumbers = []
    positions = []
    for index, element in numpy.ndenumerate(arr):
        if numpy.isfinite(element) == True:
            realNumbers.append(element)
        else:
            positions.append(index)

    numberOfMissingValues = len(positions)
    percMissingValues = float(numberOfMissingValues) / noOfElements
    grandMean = float(sum(realNumbers)) / len(realNumbers)

    results['noMissing'] = numberOfMissingValues
    results['percMissing'] = percMissingValues
    results['grandMean'] = grandMean
    results['NaNpos'] = positions
    

    # Return dictionary with all results
    return results

    


def IA(arr, initVal, noFactors, noIterations):
    """
    This is the Iterative Algorithm estimating missing values using either:
        - column mean
        - row mean
        - grand mean
        - cross mean
    

    INPUT:
    ------

    arr: submitted array
    initVal: what are the initial values for the NaN's
        - 0: column mean
        - 1: row mean
        - 2: grand mean
        - 3: cross mean (mean of row and column mean)
    noFactors: number of PC's to be used for prediction of matrix with imputed values
    noIterations: number of iterations to be run to final predicted matrix with imputed values



    OUTPUT:
    -------

    Array with predicted values in place of the missing values

    """
    newArr = arr.copy()
    #print newArr

    # Determine number of rows, columns and total number of elements
    rows, cols = numpy.shape(newArr)
    noOfElements = rows * cols


    # Compute the row means without the Nan's
    nan_rowMeansList = []
    rowsCompletenessList = []

    for ind in range(rows):

        realNumbers = []
        for subInd in newArr[ind, :]:
            if numpy.isfinite(subInd) == True:
                realNumbers.append(subInd)

        nan_rowMean = sum(realNumbers)/len(realNumbers)
        nan_rowMeansList.append(nan_rowMean)

        rowCompleteness = float(len(realNumbers)) / cols * 100
        rowsCompletenessList.append(rowCompleteness)


    # Compute the column means without the Nan's
    nan_colMeansList = []
    colsCompletenessList = []

    for ind in range(cols):

        realNumbers = []
        for subInd in newArr[:, ind]:
            if numpy.isfinite(subInd) == True:
                realNumbers.append(subInd)

        if len(realNumbers) == 0:
            return 'aborted'

        nan_colMean = sum(realNumbers)/len(realNumbers)
        nan_colMeansList.append(nan_colMean)

        colsCompleteness = float(len(realNumbers)) / rows * 100
        colsCompletenessList.append(colsCompleteness)



    # Compute grand mean and locate missing values, percentage of missing values
    # and number of missing values
    realNumbers = []
    positions = []
    for index, element in numpy.ndenumerate(X_m):
        if numpy.isfinite(element) == True:
            realNumbers.append(element)
        else:
            positions.append(index)

    numberOfMissingValues = len(positions)
    percMissingValues = float(numberOfMissingValues) / noOfElements
    grandMean = float(sum(realNumbers)) / len(realNumbers)


    
    # Here starts the iterative algorithm
    if initVal == 0:
        #print 'column mean'
        for ind in positions:
            #print ind
            newArr[ind[0], ind[1]] = nan_colMeansList[ind[1]]

    elif initVal == 1:
        #print 'row mean'
        for ind in positions:
            #print ind
            newArr[ind[0], ind[1]] = nan_rowMeansList[ind[0]]


    elif initVal == 2:
        #print 'grand mean'
        for ind in positions:
            #print ind
            newArr[ind[0], ind[1]] = grandMean

    elif initVal == 3:
        #print 'cross mean'
        for ind in positions:
            #print ind
            newArr[ind[0], ind[1]] = (nan_colMeansList[ind[1]] + nan_rowMeansList[ind[0]]) / 2


##    # XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
##    # Plotting for ONE convergence process
##    x_ax = [0]
##    y_ax = [1]
##    pylab.plot(x_ax, y_ax, 'r--')
##    pylab.show()
##    # XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX

    # Carrying out iterations
    for iters in range(noIterations):
        #print 'ITERATION: ', iters
        
        analysis = PCA(newArr, 0)
        scores = analysis.GetScores()
        loadings = analysis.GetLoadings()


        if noFactors == 1:
            # Predict new array using ONE principal component
            pc1scores = numpy.transpose(numpy.mat(scores[:,0]))
            pc1loadings = numpy.mat(loadings[0,:])
            predMatrix = numpy.dot(pc1scores, pc1loadings)
            predArr = numpy.array(predMatrix)

        elif noFactors == 2:
            # Predict new array using ONE principal component
            pc1scores = numpy.transpose(numpy.mat(scores[:,0]))
            pc2scores = numpy.transpose(numpy.mat(scores[:,1]))
            
            pc1loadings = numpy.mat(loadings[0,:])
            pc2loadings = numpy.mat(loadings[1,:])

            predMatrix = numpy.dot(pc1scores, pc1loadings) + numpy.dot(pc2scores, pc2loadings)
            predArr = numpy.array(predMatrix)

        elif noFactors == 3:
            # Predict new array using ONE principal component
            pc1scores = numpy.transpose(numpy.mat(scores[:,0]))
            pc2scores = numpy.transpose(numpy.mat(scores[:,1]))
            pc3scores = numpy.transpose(numpy.mat(scores[:,2]))

            pc1loadings = numpy.mat(loadings[0,:])
            pc2loadings = numpy.mat(loadings[1,:])
            pc3loadings = numpy.mat(loadings[2,:])

            predMatrix = numpy.dot(pc1scores, pc1loadings) + numpy.dot(pc2scores, pc2loadings) + numpy.dot(pc3scores, pc3loadings)
            predArr = numpy.array(predMatrix)
            

        newArr_pred = newArr.copy()
        for ind in positions:
            newArr_pred[ind[0], ind[1]] = predArr[ind[0], ind[1]]


        residuals = numpy.sum(numpy.square(newArr - newArr_pred))

##        # XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
##        # Plotting convergence processs for ONE run
##        x_ax.append(iters)
##        y_ax.append(residuals)
##        pylab.plot(x_ax, y_ax, 'r--')
##        #print residuals
##        # XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX

        newArr = newArr_pred.copy()


    # Return dictionary with all results
    return newArr
    



def LSA(arr, noFactors, noIterations):
    """
    This is the Least Squares Algorithm estimating missing values using either:
        - column mean
        - row mean
        choosing always the one with the smalles variation.



    INPUT:
    ------

    arr: submitted array
    noFactors: number of PC's to be used for prediction of matrix with imputed values
    noIterations: number of iterations to be run to final predicted matrix with imputed values



    OUTPUT:
    -------

    Array with predicted values in place of the missing values

    """
    newArr = arr.copy()
    #print newArr


    # Determine number of rows, columns and total number of elements
    rows, cols = numpy.shape(newArr)
    noOfElements = rows * cols


    # Compute the row means without the Nan's
    nan_rowMeansList = []
    nan_rowSTDsList = []
    rowsCompletenessList = []

    for ind in range(rows):

        realNumbers = []
        for subInd in newArr[ind, :]:
            if numpy.isfinite(subInd) == True:
                realNumbers.append(subInd)

        nan_rowMean = sum(realNumbers)/len(realNumbers)
        nan_rowMeansList.append(nan_rowMean)

        nan_rowSTD = numpy.std(realNumbers)
        nan_rowSTDsList.append(nan_rowSTD)

        rowCompleteness = float(len(realNumbers)) / cols * 100
        rowsCompletenessList.append(rowCompleteness)


    # Compute the column means without the Nan's
    nan_colMeansList = []
    nan_colSTDsList = []
    colsCompletenessList = []

    for ind in range(cols):

        realNumbers = []
        for subInd in newArr[:, ind]:
            if numpy.isfinite(subInd) == True:
                realNumbers.append(subInd)

        if len(realNumbers) == 0:
            return 'aborted'

        nan_colMean = sum(realNumbers)/len(realNumbers)
        nan_colMeansList.append(nan_colMean)

        nan_colSTD = numpy.std(realNumbers)
        nan_colSTDsList.append(nan_colSTD)

        colsCompleteness = float(len(realNumbers)) / rows * 100
        colsCompletenessList.append(colsCompleteness)


    # Compute grand mean and locate missing values, percentage of missing values
    # and number of missing values
    realNumbers = []
    positions = []

    for index, element in numpy.ndenumerate(newArr):
        if numpy.isfinite(element) == True:
            realNumbers.append(element)
        else:
            positions.append(index)

    numberOfMissingValues = len(positions)
    percMissingValues = float(numberOfMissingValues) / noOfElements
    grandMean = float(sum(realNumbers)) / len(realNumbers)


    # Create array C that holds 1 for elements that are not missing and 0 for
    # the elements that are missing
    C = numpy.ones((rows, cols), float)

    for elements in positions:
        C[elements[0], elements[1]] = 0
    

    # Check which has the lower variation, row or column. Impute the mean of the
    # one with the lower variation.
    for element in (positions):
        spec_rowSTD = nan_rowSTDsList[element[0]]
        spec_colSTD = nan_colSTDsList[element[1]]

        if spec_rowSTD < spec_colSTD:
            imputeValue = nan_rowMeansList[element[0]]
        else:
            imputeValue = nan_colMeansList[element[1]]

        newArr[element[0], element[1]] = imputeValue



    F_old = 1.0e06
    # Run iterations until changes in F are less than 1.0e-05
    for iter in range(noIterations):
        
        # Do PCA and retrieve loadings that are necessary for iteration
        analysis = PCA(newArr, 0)
        scores = analysis.GetScores()
        loadings = analysis.GetLoadings()


        # Compute arrays A_i and t
        A_i = numpy.zeros((cols, noFactors), float)
        p = loadings[0:noFactors, :]
        A_i_List = []

        for sample in range(rows):

            for attribute in range(cols):

                for PC in range(noFactors):
                    A_i[attribute, PC] = C[sample, attribute] * loadings[PC, attribute]

            A_i_List.append(A_i)

        t = numpy.zeros((rows, noFactors), float)


        # Compute scores array t
        for sample in range(rows):

            x_i = newArr[sample, :]
            t_i = numpy.dot(numpy.dot(x_i, A_i), numpy.linalg.inv(numpy.dot(numpy.transpose(A_i), A_i)))
            t[sample, :] = t_i.copy()


        # Computing F_i for all samples
        #for iter in range(noIterations):
        F_i_List = []

        for sample in range(rows):

            partF_i_List = []

            for attribute in range(cols):

                sumTerm2 = 0
                for PC in range(noFactors):

                    term2 = t[sample, PC] * A_i_List[sample][attribute, PC]
                    sumTerm2 = sumTerm2 + term2

                partF_i = numpy.square(newArr[sample, attribute] - sumTerm2)
                partF_i_List.append(partF_i)

            F_i = sum(partF_i_List)
            F_i_List.append(F_i)


        # Compute F over all samples and after that predict new array with
        # given loadings and updated scores
        F = sum(F_i_List)
        #print
        #print 'Run: ', iter, '    F: ', F

        if noFactors == 1:
            pc1scores = numpy.transpose(numpy.mat(t[:,0]))

            pc1loadings = numpy.mat(loadings[0,:])

            predMatrix = numpy.dot(pc1scores, pc1loadings)
            predArr = numpy.array(predMatrix)

        if noFactors == 2:
            pc1scores = numpy.transpose(numpy.mat(t[:,0]))
            pc2scores = numpy.transpose(numpy.mat(t[:,1]))

            pc1loadings = numpy.mat(loadings[0,:])
            pc2loadings = numpy.mat(loadings[1,:])

            predMatrix = numpy.dot(pc1scores, pc1loadings) + numpy.dot(pc2scores, pc2loadings)
            predArr = numpy.array(predMatrix)

        if noFactors == 3:
            pc1scores = numpy.transpose(numpy.mat(t[:,0]))
            pc2scores = numpy.transpose(numpy.mat(t[:,1]))
            pc3scores = numpy.transpose(numpy.mat(t[:,2]))

            pc1loadings = numpy.mat(loadings[0,:])
            pc2loadings = numpy.mat(loadings[1,:])
            pc3loadings = numpy.mat(loadings[2,:])

            predMatrix = numpy.dot(pc1scores, pc1loadings) + numpy.dot(pc2scores, pc2loadings) + numpy.dot(pc3scores, pc3loadings)
            predArr = numpy.array(predMatrix)

        newArr = predArr.copy()

        if (F_old - F) < 1.0e-05:
            break

        F_old = F


    # Take predicted values from last (converged) array and replace missing
    # values in original data array with the predicted values
    finalArr = arr.copy()
    #print finalArr

    for element in positions:
        finalArr[element[0], element[1]] = newArr[element[0], element[1]]

    #print finalArr

    # Return array with predicted values for those that were missing
    return finalArr




def IMP(arr):
    """
    This imputes (zeroth order) missing values using either:
        - column mean
        - row mean
        choosing always the one with the smalles variation.



    INPUT:
    ------

    arr: submitted array



    OUTPUT:
    -------

    Array with predicted values in place of the missing values

    """
    newArr = arr.copy()
    #print newArr


    # Determine number of rows, columns and total number of elements
    rows, cols = numpy.shape(newArr)
    noOfElements = rows * cols


    # Compute the row means without the Nan's
    nan_rowMeansList = []
    nan_rowSTDsList = []
    rowsCompletenessList = []

    for ind in range(rows):

        realNumbers = []
        for subInd in newArr[ind, :]:
            if numpy.isfinite(subInd) == True:
                realNumbers.append(subInd)

        nan_rowMean = sum(realNumbers)/len(realNumbers)
        nan_rowMeansList.append(nan_rowMean)

        nan_rowSTD = numpy.std(realNumbers)
        nan_rowSTDsList.append(nan_rowSTD)

        rowCompleteness = float(len(realNumbers)) / cols * 100
        rowsCompletenessList.append(rowCompleteness)


    # Compute the column means without the Nan's
    nan_colMeansList = []
    nan_colSTDsList = []
    colsCompletenessList = []

    for ind in range(cols):

        realNumbers = []
        for subInd in newArr[:, ind]:
            if numpy.isfinite(subInd) == True:
                realNumbers.append(subInd)

        if len(realNumbers) == 0:
            return 'aborted'

        nan_colMean = sum(realNumbers)/len(realNumbers)
        nan_colMeansList.append(nan_colMean)

        nan_colSTD = numpy.std(realNumbers)
        nan_colSTDsList.append(nan_colSTD)

        colsCompleteness = float(len(realNumbers)) / rows * 100
        colsCompletenessList.append(colsCompleteness)


    # Compute grand mean and locate missing values, percentage of missing values
    # and number of missing values
    realNumbers = []
    positions = []

    for index, element in numpy.ndenumerate(newArr):
        if numpy.isfinite(element) == True:
            realNumbers.append(element)
        else:
            positions.append(index)

    numberOfMissingValues = len(positions)
    percMissingValues = float(numberOfMissingValues) / noOfElements
    grandMean = float(sum(realNumbers)) / len(realNumbers)


    # Check which has the lower variation, row or column. Impute the mean of the
    # one with the lower variation.
    for element in (positions):
        spec_rowSTD = nan_rowSTDsList[element[0]]
        spec_colSTD = nan_colSTDsList[element[1]]

        if spec_rowSTD < spec_colSTD:
            imputeValue = nan_rowMeansList[element[0]]
        else:
            imputeValue = nan_colMeansList[element[1]]

        newArr[element[0], element[1]] = imputeValue


    # Return array with imputed values
    return newArr




# Main program
if __name__ == '__main__':
    # Import necessary modules
    import random
    import numpy
    import numpy.linalg
    import scipy.io
    import pylab
    import pca_module

    # Import necessary self-made modules
    from pca import PCA

    # Read data set from text file
    X = scipy.io.read_array('ostaver.txt', separator='\t', linesep='\n')

##    X_list = [[4,17,21,21],[5,2,22,5],[9,10,1,2],[13,34,13,9],[17,1,2,3],[21,22,23,24]]
##    X = numpy.array(X_list, float)
##    print X
##    print

##    # First generate a random array
##    X = RAG(6,4)

##    # Create a copy of submitted matrix and insert missing values
##    X_m = MVG(X, 15)
##
##    # Testing the LSA algorithm
##    X_p = LSA(X_m, 2, 10)




    # Loop that runs a certain number of simulations
    skipped = 0
    resList = []
    for runs in range(1):
        print 'RUN ', runs

        # Create a copy of submitted matrix and insert missing values
        X_m = MVG(X, 5)
        #scipy.io.write_array('X_m.txt', X_m, separator='\t', linesep='\n')

        # Analyse the array with missing values
        #diagnosis = MVA(X_m)

        # Now use the new prediciton/imputation function
        #X_p = IA(X_m, 0, 1, 20)
        #X_p = LSA(X_m, 3, 5)
        #X_p = IMP(X_m)

        T, P, E = pca_module.PCA_nipals2(X, standardize=False, E_matrices=False)
        print 'jippiiiiiiiiiiiiii'
        scipy.io.write_array('X_m.txt', X_m, separator='\t', linesep='\n')
        scipy.io.write_array('T.txt', T, separator='\t', linesep='\n')
        scipy.io.write_array('P.txt', P, separator='\t', linesep='\n')
        scipy.io.write_array('E.txt', E, separator='\t', linesep='\n')
        break
        

        if X_p == 'aborted':
            print 'aborted'
            skipped = skipped + 1
            continue
        #scipy.io.write_array('X_p.txt', X_p, separator='\t', linesep='\n')

        # Subtract array with predicted values from original array, then
        # square it and finally sum up all residuals
        resArr = X - X_p
        resList.append(numpy.sum(numpy.square(resArr)))

    # Compute average residual for the given number of runs
    avRes = sum(resList) / len(resList)
    #print avRes
    #print 'Skipped: ', skipped

    X_all = numpy.vstack((X, X_m, X_p))

    scipy.io.write_array('X_all.txt', X_all, separator='\t', linesep='\n')
    

    
        
