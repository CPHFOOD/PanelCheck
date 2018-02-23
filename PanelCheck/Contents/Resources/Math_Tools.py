#!/usr/bin/env python

"""
This module lets PanelCheck access many mathematical methods defined by numpy and scipy 
and there are also some custom made specialized methods for use in creating many of the plots.

"""

# numpy methods available after: from Math_Tools import *
from numpy import array, ndarray, arange, average, concatenate, floor, ceil, sqrt, diag, dot, take, std, arange, hstack, vstack, \
     reshape, transpose, trace, mat, shape, zeros, pi, cos, sin, sum

# scipy methods available after: from Math_Tools import *
from scipy.linalg import svd

# PCA related methods:
from pca_module import mean_center, standardization, PCA_nipals2, PCA_svd, CorrelationLoadings




#################### PREPROCESSING OF DATA-SETS ####################   

def center(X): # alias to mean_center
    return mean_center(X)
    
def stand(X): # alias to standardization
    return standardization(X)

def normalize(X, norm_value=1.0):
    # new_X will be normalized to range: [0, norm_value]
    new_X = zeros(shape(X), float)
    X_min = min(X)
    if X_min >= 0:
        X_sum = sum(X) / float(norm_value)
        new_X = X / X_sum
    else:
        new_X = X + abs(X_min)
        new_X_sum = sum(new_X) / float(norm_value)
        new_X = new_X / new_X_sum
    return new_X 


 
def STD(Y, selection):
    """
    This function computes the standard deviation of an array either column-wise
    (selection = 0) or row-wise (selection = 1).
    """
    # First make a copy of input matrix and make it a matrix with float
    # elements
    X = Y.copy()
    numberOfObjects, numberOfVariables = shape(X)
    variablesMeans = average(X, 0)
    objectsMeans = average(X, 1)
    

    # STD of columns
    if selection == 0:
        # Now center and divide by standard deviation
        for row in range(0, numberOfObjects):
            X[row] = X[row] - variablesMeans

        # Now compute squares, sum up over columns and divide by (n-1) and
        # take squre root
        X = X * X
        X = sum(X, 0)
        X = X / (numberOfObjects - 1)
        X = sqrt(X)


    # STD of rows
    if selection == 1:
        # Now center and divide by standard deviation
        for col in range(0, numberOfVariables):
            X[:, col] = X[:, col] - objectsMeans

        # Now compute squares, sum up over columns and divide by (n-1) and
        # take squre root
        X = X * X
        X = sum(X, 1)
        X = X / (numberOfVariables - 1)
        X = sqrt(X)

    return X  






#################### UNIVARIATE: ANOVA ####################
def ANOVA(s_data, plot_data, active_data=None):
    """
    Calculate general ANOVA
    
    
    @param active_data: The total active data set as a 4d array: active_data[ass_ind, samp_ind, rep_ind, att_ind]
    @type active_data: numpy array
    
    """
    if active_data == None:
        active_data = s_data.GetActiveData(active_assessors=plot_data.activeAssessorsList, active_attributes=plot_data.activeAttributesList, active_samples=plot_data.activeSamplesList)
    
    print "Calculate ANOVA"
    
    preANOVA_matrix = zeros((len(plot_data.activeAssessorsList), len(plot_data.activeAttributesList), len(plot_data.activeSamplesList), len(s_data.ReplicateList)), float)
    
    print shape(preANOVA_matrix)
    print len(preANOVA_matrix)
    
    # step, for one (assessor, attribute)-segment of sample scores for one replicate 
    dx = len(plot_data.activeSamplesList)      
    
    for ass_ind in range(len(plot_data.activeAssessorsList)):
        for att_ind in range(len(plot_data.activeAttributesList)):    
                        
            for samp_ind in range(len(plot_data.activeSamplesList)):
                for rep_ind in range(len(s_data.ReplicateList)):
                    preANOVA_matrix[ass_ind, att_ind, samp_ind, rep_ind] = active_data[ass_ind, samp_ind, rep_ind, att_ind]
            
    
    ANOVA_F_list = []
    ANOVA_p_list = []
    ANOVA_MSE_list = []
    max_F = 0; max_p = 0; max_MSE = 0
    
    for ass_ind in range(len(plot_data.activeAssessorsList)):
        ANOVA_F_list.append([])
        ANOVA_p_list.append([])
        ANOVA_MSE_list.append([])    
        for att_ind in range(len(plot_data.activeAttributesList)):
        
		ANOVAresults = f_oneway(preANOVA_matrix[ass_ind, att_ind])

		if isinstance(ANOVAresults[1], (int , float)): # if p value not '*'
		    F_val = round(ANOVAresults[0], 2) 
		    if max_F < F_val:
			max_F = F_val

		    p_val = round(ANOVAresults[1], 3)
		    # Determine highest p value for setting limits in the
		    # p*MSE plot
		    if max_p < p_val:
			max_p = p_val 
		else:
		    F_val = ANOVAresults[0]
		    p_val = ANOVAresults[1]

		MSE_val = round(ANOVAresults[2], 4)


		# Determine highest MSE value for setting limits in the
		# p*MSE plot
		if max_MSE < MSE_val:
		    max_MSE = MSE_val

		ANOVA_F_list[ass_ind].append(F_val)
		ANOVA_p_list[ass_ind].append(p_val)
		ANOVA_MSE_list[ass_ind].append(MSE_val)           
       
    # Here the scanning for the F values at 5% and 1% significance
    # value starts. 'DF sample' and 'DF error' stay the same and
    # F is increased by 0.01 until p values goes down to 0.05
    # which is the 5% significance level.
    # 'DF sample' will be no. of samples - 1
    # 'DF error' will be the same as number of samples
    F = 0.01
    i = 0; max_i = 10000
    F001_found = False; F005_found = False
    while (i < max_i) and not (F001_found and F005_found):
            
            if i == max_i-1: # reached max number of iterations:
                raise Exception, "ANOVA Error: Too many iteration when scanning for 1% and 5% signifcance levels."
            
            # using last ANOVA results array
	    pValue = fprob(ANOVAresults[3], ANOVAresults[4], F)
	    
	    if not F005_found:
	        if pValue <= 0.05:
		    F_005 = F
		    F005_found = True
		    print "F at 5% sign.level: " + str(F)
	    
	    if not F001_found:
	        if pValue <= 0.01:
		    F_001 = F
		    F001_found = True
		    print "F at 1% sign.level: " + str(F)
	    
	    F += 0.01
	    i += 1
    
    print "scan iterations: " + str(i) + "\n"
    
    
    return ANOVA_F_list, ANOVA_p_list, ANOVA_MSE_list, [F_001, F_005]



 
 
 
#################### MULTIVARIATE: PRINCIPAL COMPONENT ANALYSIS #################### 
def PCA(X, standardize=False, PCs=10, E_matrices=False, nipals=False):
    #(objects, variables) = shape(X)
    
    if nipals:
        return PCA_nipals2(X, standardize=standardize, PCs=PCs, E_matrices=E_matrices) # nipals using numpy array (fast for large datasets)
    else:
        return PCA_svd(X, standardize=standardize)    
         
    # for usage of PCA with NIPALS, use:   PCA_nipals2(X, PCs)
    # for usage of PCA with SVD, use:      PCA_svd(X)      
      
      

#################### GENERAL TOOLS ####################

def rotate_vec2d(vec, angle): # vector is rotated around origo by the given angle
    angle_rad = angle * (pi/180.0)
    vec2 = array([0,0], float)
    vec2[0] = cos(angle_rad)*vec[0] - sin(angle_rad)*vec[1]
    vec2[1] = sin(angle_rad)*vec[0] + cos(angle_rad)*vec[1]
    return vec2



def lerp(a, b, t): # linear interpolation
     return float(a * (1 - t) + b * t)


#################### SCIPY CODE (somewhat modified code needed from stats.py) ####################      

import scipy.special as special
import numpy as np


fprob = special.fdtrc

     
def _chk_asarray(a, axis):
    if axis is None:
        a = np.ravel(a)
        outaxis = 0
    else:
        a = np.asarray(a)
        outaxis = axis
    return a, outaxis
    


def ss(a, axis=0):
    """Squares each value in the passed array, adds these squares, and returns the
    result.

    Parameters
    ----------
    a : array
    axis : int or None

    Returns
    -------
    The sum along the given axis for (a*a).
    """
    a, axis = _chk_asarray(a, axis)
    return np.sum(a*a, axis)

  
def square_of_sums(a, axis=0):
    """Adds the values in the passed array, squares that sum, and returns the
result.

Returns: the square of the sum over axis.
"""
    a, axis = _chk_asarray(a, axis)
    s = np.sum(a,axis)
    if not np.isscalar(s):
        return s.astype(float)*s
    else:
        return float(s)*s


def f_oneway(ass_arrays):
    """
Performs a 1-way ANOVA, returning an F-value and probability given
any number of groups.  From Heiman, pp.394-7.

Usage:   f_oneway (*args)    where *args is 2 or more arrays, one per
                                  treatment group
Returns: f-value, probability
"""
    #na = len(args)            # ANOVA on 'na' groups, each in it's own array
    #tmp = map(array,args)
    #alldata = concatenate(args)
    
    na = len(ass_arrays)
    tmp = map(array,ass_arrays)
    
    alldata = np.concatenate(ass_arrays)
    
    bign = len(alldata)
    sstot = ss(alldata)-(square_of_sums(alldata)/float(bign))
    ssbn = 0
    for a in ass_arrays:
        ssbn = ssbn + square_of_sums(array(a))/float(len(a))
    ssbn = ssbn - (square_of_sums(alldata)/float(bign))
    sswn = sstot-ssbn
    dfbn = na-1 # DF assessors/sample
    dfwn = bign - na # DF Error
    msb = ssbn/float(dfbn) # MSA for assessor/sample
    msw = sswn/float(dfwn) # MSE for error
##    print msb, msw
##    print
    
    
    # Everything in the 'if' part is new. The original formula had no 'if'
    # test (everything original is found under 'else'). Had to change this, since 'Division
    # by zero' occured when the assessor gave the same value for all samples.
    if msw < 1e-10:
        f = '*'
        prob = '*'
        
##        print 'F = ', f, '; p = ', prob
##        print dfbn, dfwn
##        print
    
    else:
        f = msb/msw # F value
        
        if f < 0:
            f = 0.0
            prob = 1.0
        else:
            prob = fprob(dfbn,dfwn,f)
        
        #print 'F = ', f, '; p = ', prob
        #print 'msb = ', msb, '; msw = ', msw
        #print dfbn, dfwn
        #print
    
    return f, prob, msw, dfbn, dfwn#, msb, 