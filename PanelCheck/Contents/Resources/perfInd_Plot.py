# -*- coding: utf-8 -*-
"""
Created on Mon Feb 13 09:59:22 2012

@author: oliver.tomic

@purpose: module that contains function that computes performance indices
for sensory data.
"""

# Import necessary modules

from __future__ import division
from Plot_Tools import *
from PanelCheck_Tools import *
import numpy as np
#import statTools as st
import pyper, math

import scipy.stats as scist
import random as rnd
import perfInd_Data as pid



class PerfIndData:
    def __init__(self, res, etype, comp, numberOfSamples, numberOfAttributes):

        self.res = res
        self.etype = etype

        if etype == "agr":
            self.prod = res["AGR prod"]
            self.att = res["AGR att"]
            self.average = res['AGR aver']
            self.prod_p = res['AGR prod pVal']
            self.att_p = res['AGR att pVal']
            self.prod_coll = []
            self.att_coll = []

        elif etype == "rep":
            self.prod = res["REP prod"]
            self.att = res["REP att"]
            self.average = res['REP aver']
            self.prod_p = res['REP prod pVal']
            self.att_p = res['REP att pVal']
            self.prod_coll = res['REP prod coll']
            self.att_coll = res['REP att coll']


        if comp == "RV":
            self.sign_val_1 = pid.get_sign_level(pid.RV1_1, numberOfSamples, numberOfAttributes)
            self.sign_val_5 = pid.get_sign_level(pid.RV1_5, numberOfSamples, numberOfAttributes)
            self.sign_val_10 = pid.get_sign_level(pid.RV1_10, numberOfSamples, numberOfAttributes)
        else:
            self.sign_val_1 = pid.get_sign_level(pid.RV2_1, numberOfSamples, numberOfAttributes)
            self.sign_val_5 = pid.get_sign_level(pid.RV2_5, numberOfSamples, numberOfAttributes)
            self.sign_val_10 = pid.get_sign_level(pid.RV2_10, numberOfSamples, numberOfAttributes)


        self.average_prod = np.average(self.prod)
        self.std_prod = np.std(self.prod, ddof=1)
        self.std_prod_upper = self.average_prod + self.std_prod
        self.std_prod_lower = self.average_prod - self.std_prod

        self.average_att = np.average(self.att)
        self.std_att = np.std(self.att)
        self.std_att_upper = self.average_att + self.std_att
        self.std_att_lower = self.average_att - self.std_att

    def get_config(self, vtype, elements, plot_title, curr_lvl):

        conf_dict = {}
        conf_dict["elements"] = elements
        conf_dict["target"] = curr_lvl
        conf_dict["etype"] = self.etype
        conf_dict["vtype"] = plot_title
        conf_dict["title"] = plot_title
        conf_dict["slvl1"] = self.sign_val_1
        conf_dict["slvl5"] = self.sign_val_5
        conf_dict["slvl10"] = self.sign_val_10


        if vtype == "att":
            conf_dict["values"] = self.att
            conf_dict["average"] = self.average_att
            conf_dict["upper_std"] = self.std_att_upper
            conf_dict["lower_std"] = self.std_att_lower
        else:
            conf_dict["values"] = self.prod
            conf_dict["average"] = self.average_prod
            conf_dict["upper_std"] = self.std_prod_upper
            conf_dict["lower_std"] = self.std_prod_lower
        return conf_dict


def calcAGR(s_data, plot_data, sigLvl=0.05, permutationTestEnabled = False):

    assessorList = plot_data.activeAssessorsList
    attributeList = plot_data.activeAttributesList
    sampleList = plot_data.activeSamplesList
    replicateList = s_data.ReplicateList
    sparseMatrix = s_data.SparseMatrix
    itemID = plot_data.tree_path


    numberOfAssessors = len(assessorList)
    numberOfAttributes = len(attributeList)
    numberOfSamples = len(sampleList)
    numberOfReplicates = len(s_data.ReplicateList)

    lables = s_data.LabelList
    sensory = s_data

    numOfPerm = 999

    method = plot_data.special_opts["comp"]
    agr = plot_data.special_opts["agr"] # target level

    progress_value = 0
    progress = Progress(None)
    progress.set_gauge(value=progress_value, text="Calculating AGR...\n")


    # Convert attribute names from unicode to latin-1. Unicode makes
    # PypeR or R crash and needs to be converted prior to submittng
    # list through PypeR.
    colNames = lables + attributeList
    convColNames = []
    for attribute in colNames:
        convColNames.append(attribute.encode("latin-1"))

    # Create temporary dictionary which stores computation results. Will be
    # removed when function is finished.
    res = {}

#==============================================================================
#     AGR computations
#==============================================================================
    print '*** AGR ***'
    # First collect all assessor average matrices in one list.
    assAverArrList = []
    for ass in assessorList:
        arrSP, arr = sensory.GetAssessorAverageData(ass)
        assAverArrList.append(arr)

    # Now compute consensus matrices where always the particular assessor at
    # han is left out. That means, the first consensus matrix is computed
    # without assessor 1, the second without assessor 2, etc. This allows for
    # comparing the data of one assessor against a consensus without the
    # particular assessor being included in the consensus.
    specConsList = []
    for assInd, ass in enumerate(assessorList):

        popList = assAverArrList[:]
        popList.pop(assInd)

        rows, cols = np.shape(popList[0])
        sumArr = np.zeros((rows, cols))

        for subAssInd, subAss in enumerate(popList):
            sumArr = np.add(sumArr, subAss)

        specConsArr = sumArr / len(popList)
        specConsList.append(specConsArr)


    # Centre individual and consensus arrays in a seperate loop instead of
    # doing this every time before the arrays are submitted to the RV2
    # coefficient. In this way centring is done far less often saving
    # computation time.
    centAssAverArrList = []
    centSpecConsList = []
    centTransAssAverArrList = []
    centTransSpecConsList = []

    for assIndex, ass in enumerate(assessorList):

        # Centred individual arrays
        centAssArr = st.centre(assAverArrList[assIndex], axis=0)
        centAssAverArrList.append(centAssArr)

        # Centred specific consensus arrays
        centSpecConsArr = st.centre(specConsList[assIndex], axis=0)
        centSpecConsList.append(centSpecConsArr)

        # Centred then transposed individual arrays
        centTransAssArr = np.transpose(st.centre(assAverArrList[assIndex]))#, axis=0)
        centTransAssAverArrList.append(centTransAssArr)

        # Centred then transposed specific consensus arrays
        centTransSpecConsArr = np.transpose(st.centre(specConsList[assIndex]))#, axis=0)
        centTransSpecConsList.append(centTransSpecConsArr)


    # Compute Rv coefficient between average scores of each assessor and
    # specific  consensus.
    assObjRVcoeffList = []
    assVarRVcoeffList = []

    assObjRVpValList = []
    assVarRVpValList = []

    step = 100 / len(assessorList)

    for assIndex, ass in enumerate(assessorList):

        # Compute RV's for objects
        objectData = [centSpecConsList[assIndex], centAssAverArrList[assIndex]]

        if method == 'RV':
            coeffMat = st.RVcoeff(objectData)
        elif method == 'RV2':
            coeffMat = st.RV2coeff(objectData)

        coeff = coeffMat[0,1]
        objCoeff100 = round(coeff * 100, 1)
        assObjRVcoeffList.append(objCoeff100)

        if permutationTestEnabled:
            pVal = permuationTestRV(objectData, RVtype=method, numPerm=numOfPerm, sigLevel=sigLvl)
            assObjRVpValList.append(pVal)

        # Compute RV's for variables
        variableData = [centTransSpecConsList[assIndex], \
                centTransAssAverArrList[assIndex]]

        if method == 'RV':
            coeffMat = st.RVcoeff(variableData)
        elif method == 'RV2':
            coeffMat = st.RV2coeff(variableData)

        coeff = coeffMat[0,1]
        varCoeff100 = round(coeff * 100, 1)
        assVarRVcoeffList.append(varCoeff100)

        if permutationTestEnabled:
            pVal = permuationTestRV(variableData, RVtype=method, numPerm=numOfPerm, sigLevel=sigLvl)
            assVarRVpValList.append(pVal)

        progress_value += step
        progress.set_gauge(value=progress_value)

    AGRAver = np.average(np.array([assObjRVcoeffList, assVarRVcoeffList]), 0)

    # Collect compuation results and return when finished
    res['AGR prod'] = assObjRVcoeffList
    res['AGR att'] = assVarRVcoeffList
    res['AGR aver'] = AGRAver
    res['AGR prod pVal'] = assObjRVpValList
    res['AGR att pVal'] = assVarRVpValList

    progress.set_gauge(value=100, text="Done\n")
    progress.Destroy()
    return res



def calcREP(s_data, plot_data, permutationTestEnabled = False):

    assessorList = plot_data.activeAssessorsList
    attributeList = plot_data.activeAttributesList
    sampleList = plot_data.activeSamplesList
    replicateList = s_data.ReplicateList
    sparseMatrix = s_data.SparseMatrix
    itemID = plot_data.tree_path


    numberOfAssessors = len(assessorList)
    numberOfAttributes = len(attributeList)
    numberOfSamples = len(sampleList)
    numberOfReplicates = len(s_data.ReplicateList)

    lables = s_data.LabelList
    sensory = s_data

    numOfPerm = 999

    method = plot_data.special_opts["comp"]
    repLvl = plot_data.special_opts["rep"]
    if plot_data.special_opts["lvl"] == "same for all":
        repLvl = plot_data.special_opts["agr"]


    progress_value = 0
    progress = Progress(None)
    progress.set_gauge(value=progress_value, text="Calculating REP...\n")



    # Convert attribute names from unicode to latin-1. Unicode makes
    # PypeR or R crash and needs to be converted prior to submittng
    # list through PypeR.
    colNames = lables + attributeList
    convColNames = []
    for attribute in colNames:
        convColNames.append(attribute.encode("latin-1"))

    # Create temporary dictionary which stores computation results. Will be
    # removed when function is finished.
    res = {}

#==============================================================================
#     REP computations
#==============================================================================
    print '*** REP ***'
    # Collect arrays based on a specific replicate. Do this for each assessor.
    # That means: 1 array for ass1-rep1, 1 array for ass1-rep2, etc.
    allAssRepList = []
    allTransAssRepList = []

    for ass in assessorList:
        allRepList = []
        allTransRepList = []

        for rep in replicateList:
            arrSparse, arr = sensory.GetAssessorReplicateData(ass, rep)
            allRepList.append(st.centre(arr, axis=0))
            #allTransRepList.append(st.centre(np.transpose(arr), axis=0))
            allTransRepList.append(np.transpose(st.centre(arr, axis=0)))

        allAssRepList.append(allRepList)
        allTransAssRepList.append(allTransRepList)

    # Now run through all pairs of arrays. The code with 'partCoeffList'
    # computes the average over all Rv's in the data matrix that is 'above'
    # the diagonal in coeffMat. With three replicates the coeffMat is of
    # dimension 3x3 and therefore 3 values need to be extracted from coeffMat
    # and the average is to be computed.
    repObjRVcoeffList = []
    repVarRVcoeffList = []
    repObjCollection = []
    repVarCollection = []

    repObjRVpValList = []
    repVarRVpValList = []

    step =  100 / len(assessorList)

    for ind, name in enumerate(assessorList):

        #coeffMat = st.RV2coeff(data)
        if method == 'RV':
            coeffMat = st.RVcoeff(allAssRepList[ind])
        elif method == 'RV2':
            coeffMat = st.RV2coeff(allAssRepList[ind])

        objCoeffList = []

        for subInd in range(1,len(allAssRepList[ind])):
            partObjCoeffList = np.diagonal(coeffMat, offset=subInd)
            objCoeffList.extend(partObjCoeffList)

        coeff100 = np.average(objCoeffList) * 100
        repObjRVcoeffList.append(round(coeff100, 1))
        repObjCollection.append(objCoeffList)

        if permutationTestEnabled:
            pVal = permuationTestRV(allAssRepList[ind], RVtype=method, numPerm=numOfPerm)
            repObjRVpValList.append(pVal)

        # Compute REP indices for variables
        if method == 'RV':
            coeffMat = st.RVcoeff(allTransAssRepList[ind])
            print "RV"
        elif method == 'RV2':
            coeffMat = st.RV2coeff(allTransAssRepList[ind])
            print "RV2"

        varCoeffList = []

        for subInd in range(1,len(allTransAssRepList[ind])):
            partVarCoeffList = np.diagonal(coeffMat, offset=subInd)
            varCoeffList.extend(partVarCoeffList)

        coeff100 = np.average(varCoeffList) * 100
        repVarRVcoeffList.append(round(coeff100, 1))
        repVarCollection.append(varCoeffList)

        if permutationTestEnabled:
            pVal = permuationTestRV(allTransAssRepList[ind], RVtype=method, numPerm=numOfPerm)
            repVarRVpValList.append(pVal)

        progress_value += step
        progress.set_gauge(value=progress_value)

    REPAver = np.average(np.array([repObjRVcoeffList, repVarRVcoeffList]), 0)

    res['REP prod'] = repObjRVcoeffList
    res['REP att'] = repVarRVcoeffList
    res['REP aver'] = REPAver
    res['REP prod coll'] = repObjCollection
    res['REP att coll'] = repVarCollection
    res['REP prod pVal'] = repObjRVpValList
    res['REP att pVal'] = repVarRVpValList

    print "REP prod"
    print repObjRVcoeffList

    print "REP att"
    print repVarRVcoeffList

    progress.set_gauge(value=100, text="Done\n")
    progress.Destroy()
    return res


def calcDIS(s_data, plot_data):

    assessorList = plot_data.activeAssessorsList
    attributeList = plot_data.activeAttributesList
    sampleList = plot_data.activeSamplesList
    replicateList = s_data.ReplicateList
    sparseMatrix = s_data.SparseMatrix
    itemID = plot_data.tree_path


    progress_value = 0
    progress = Progress(None)
    progress.set_gauge(value=progress_value, text="Calculating DIS...\n")

    i = 1
    assIndList = []
    for a in s_data.AssessorList:
        if a in assessorList:
            assIndList.append(i)
        i+=1
    i = 1
    sampIndList = []
    for s in s_data.SampleList:
        if s in sampleList:
            sampIndList.append(i)
        i+=1
    i = 1
    repIndList = []
    for r in s_data.ReplicateList:
        if r in replicateList:
            repIndList.append(i)
        i+=1

    numberOfAssessors = len(assessorList)
    numberOfAttributes = len(attributeList)
    numberOfSamples = len(sampleList)
    numberOfReplicates = len(s_data.ReplicateList)

    lables = s_data.LabelList
    sensory = s_data


    method = plot_data.special_opts["comp"]
    dis = plot_data.special_opts["dis"]
    if plot_data.special_opts["lvl"] == "same for all":
        dis = plot_data.special_opts["agr"]

    current_abspath = os.path.dirname( os.path.realpath( __file__ ) )


    # Convert attribute names from unicode to latin-1. Unicode makes
    # PypeR or R crash and needs to be converted prior to submittng
    # list through PypeR.
    colNames = lables + attributeList
    convColNames = []
    for attribute in colNames:
        convColNames.append(attribute.encode("latin-1"))

    # Create temporary dictionary which stores computation results. Will be
    # removed when function is finished.
    res = {}

#==============================================================================
#     DIS computations
#==============================================================================
    # STEP 1: Computations using Per Brockhoffs senseMixed R code
    # which is a two way ANOVA with assessors as random main effect
    print '*** DIS ***'

    # STEP 1.1: Compuations for data from whole panel except specific assessor
    # This is where the p values are stored for the panel (excluding the
    # particular assessor) and the particular assessor.
    pValsPanel = []
    pValsAss = []

    # Start PypeR, set working directory and source Per's R function
    r = pyper.R(RCMD=current_abspath + "/R-2.3.1/bin/R")
    print current_abspath + "/R-2.3.1/bin/R"
    new_path = current_abspath.replace("/", "/")
    print new_path
    r('dir <-"' + new_path + '/R_scripts"')


    #r = pyper.R(RCMD="C:/Program Files/R/R-2.3.1/bin/R")
    #r('dir <-"C:/PanelCheck/installers/PI code/PI"')
    r('setwd(dir)')
    r('source("sensmixedVer4.2.R")')

    print "step 1"
    # STEP 1:
    # First run 2-way ANOVA to find out how many attributes are significant
    # based on the scores from the whole panel
    allPanelSignList = []
    specRawDataList = []


    step = 100 / len(assessorList)

    # Get keys/lables and data from whole panel, except for specific assessor.
    # This will later be used to computed ANOVA and provide # of sign
    # attributes for the panel, but without specific assessor.
    for exclAss in assessorList:

        # Collect keys and data in list that will be converted to arrays later
        keysList = []
        dataList = []

        # Loop through all assessors
        assInd = 0
        for ass in assessorList:

            if exclAss == ass:
                assInd+=1
                continue

            sampInd = 0
            # Loop through all samples
            for samp in sampleList:

                repInd = 0
                # Loop through all replicates
                for rep in replicateList:

                    # Create key that is used to extract intensity scores. Keys
                    # and data are appended to the lists.
                    k = (ass, samp, rep)
                    keysList.append(np.array((assIndList[assInd], sampIndList[sampInd], repIndList[repInd])))

                    # Convert data from strings (as provided in sparse matrix)
                    # to floats so that compuations can be done.
                    dataStrList = sparseMatrix[k]
                    dataFloatList = []
                    for item in dataStrList:
                        floatItem = float(item)
                        dataFloatList.append(floatItem)
                    dataList.append(dataFloatList)
                    repInd+=1
                sampInd+=1
            assInd+=1

        # Convert lists to arrays.
        keysArr = np.array(keysList)
        dataArr = np.array(dataList)

        specRawDataList.append([keysArr, dataArr])


#        # Convert all entries from unicode to latin-1. Unicode makes
#        # PypeR or R crash and needs to be converted prior to submitting
#        # array through PypeR.
#        for ind, val in np.ndenumerate(keysArr):
#            keysArr[ind] = val.encode("latin-1")

        print dataArr
        print keysArr

        print "transmit arrays to R"
        # Now transmit arrays to R via PypeR. These numpy arrays are of type
        # matrix in R
        r['scores'] = dataArr
        r['keys'] = keysArr

        print "Transform matrices in R"
        # Transform matrices in R into data frames prior to concatenating keys
        # and scores. If concatenating matrices is done before transforming
        # into data frames the resulting matrix will be filled with only
        # strings. Strings cannot not be handled by Per's senseMixed function.
        # By transforming into data frames first the and then concatenating
        # intital type will be kept (keys stay strings and data stay floats).
        r('dfKeys <- as.data.frame(keys)')
        r('dfScores <- as.data.frame(scores)')

        # Collect keys and scores in one R data frame. Also add column names.
        r('allData <- cbind(dfKeys, dfScores)')
        r['colNames'] = convColNames
        r('colnames(allData) <- colNames')

        print "Run Per's function"
        # Run Per's function with cunstructed data frame
        r('res <- sensmixedVer42(allData)')
        per = r['res']

        #per1 = per[0]
        per2 = per[1]
        #per3 = per[2]
        #per4 = per[3]

        # Extract 2-way ANOVA p-values for product effect
        pVals = per2[6,:]
        pValsPanel.append(pVals[:])

        # Count how many attributes the panels finds to be significant at 5% level.
        signList = []
        for item in pVals:
            print item
            if item < 0.05:
                signList.append(item)

        print; print len(signList)
        allPanelSignList.append(signList)
        print '---------'

        progress_value += step
        progress.set_gauge(value=progress_value)


    # STEP 1.2:
    # This is where the 2-way ANOAV is computed for the whole panel on data
    # from ALL assessors
    # Submit data set to R via PypeR and run Per's senseMixed R function
    allScores = sensory.MatrixData().copy()
    keysArr = sensory.MatrixLables().copy()

    r['scores'] = allScores
    r['keys'] = keysArr

    r('dfKeys <- as.data.frame(keys)')
    r('dfScores <- as.data.frame(scores)')
    r('allData <- cbind(dfKeys, dfScores)')
    r('colnames(allData) <- colNames')

    r('res <- sensmixedVer42(allData)')
    perAll = r['res']
    perAll2 = perAll[1]


    # Extract 2-way ANOVA p-values for product effect
    pValsAll = perAll2[6,:]
    #pValsPanelAll.append(pValsAll[:])

    # Count how many attributes the panels finds to be significant at 5% level.
    signListAll = []
    for item in pValsAll:
        print item
        if item < 0.05:
            signListAll.append(item)

    print; print 'all:', len(signListAll)
    print '---------'


    # STEP 2:
    # From here the assessor-wise one-way ANOVA is run.

    # Collect arrays from each assessor.
    allAssList = []
    for ass in assessorList:
        arrSparse, arr = sensory.GetAssessorData(ass)
        allAssList.append(arr)

    # Construct string for exec command, such that it can be used in the
    # f_oneway function
    strComm = 'scist.f_oneway('
    for ind,samp in enumerate(sampleList):

        #partStr = 'groups[{0}]'.format(ind) # for Python 2.7
        partStr = 'groups[%d]' %ind

        if ind == 0:
            strComm = strComm + partStr

        elif ind == len(sampleList)-1:
            strComm = strComm + ',' + partStr + ')'

        else:
            strComm = strComm + ',' + partStr


    strComm = 'oneway = ' + strComm

    # Loop through all assessors and attributes and collect number of
    # attributes significant at 5% level
    DISCountList = []
    DISList = []
    groupsDict = {}

    for assInd, ass in enumerate(assessorList):
        assDISList = []
        pValsAssSubList = []

        for attInd, att in enumerate(attributeList):

            attributeData = allAssList[assInd][:,attInd]
            groups = np.split(attributeData, len(sampleList))
            exec(strComm)

            groupsDict[(assInd, attInd)] = groups
            pValsAssSubList.append(oneway[1])
            if oneway[1] < 0.05:
                assDISList.append(oneway[1])

        DISCountList.append(len(assDISList))
        DISInd = float(len(assDISList)) / \
                float(len(allPanelSignList[assInd])) * 100
        DISList.append(round(DISInd, 1))

        pValsAss.append(pValsAssSubList)

    # Construct list with number of significant number of variables for those
    # cases where the specific assessor is left out.
    DISCountListPanel = []
    for subList in allPanelSignList:
        DISCountListPanel.append(len(subList))

    # Compute DIS for number of significant variables per individual relative
    # to total number of tested attributes
    DISList2 = []
    for ind, ass in enumerate(DISCountList):
        perc = float(DISCountList[ind]) / float(len(attributeList)) * 100
        DISList2.append(round(perc, 1))


    res['DIS count ind'] = DISCountList
    res['DIS count all_ex1'] = DISCountListPanel
    res['DIS'] = DISList
    res['DIS2'] = DISList2
    res['DIS sign all panel'] = len(signListAll)

    progress.set_gauge(value=100, text="Done\n")
    progress.Destroy()
    return res


def set_sign_level_numeric_data(sign_type, plot_data, samples_count, attributes_count):
    data = pid.get_sign_level_data(sign_type)
    if data == None: show_err_msg("No data set for type: " + sign_type); return
    val = pid.get_sign_level(sign_type, samples_count, attributes_count)
    if val == None: show_err_msg("Number of samples or number of attributes is not within acctable range [3, 50]."); return

    key = (samples_count-1, attributes_count-1)
    plot_data.numeric_data_config[key] = {"back_color": '#ffaa00'} # orange

    results = []
    dataline = []; dataline.append(''); dataline.append(''); dataline.append("Number of attributes"); results.append(dataline);
    dataline = []; dataline.append(''); dataline.append('');
    for i in range(pid.MIN_COUNT_ATTRIBUTES, pid.MAX_COUNT_ATTRIBUTES + 1):
        key = (1, i-1)
        plot_data.numeric_data_config[key] = {"back_color": '#eeeeee'} # grey
        dataline.append(i)
    results.append(dataline)

    i = pid.MIN_COUNT_SAMPLES
    for row in data:
        key = (i-1, 1)
        plot_data.numeric_data_config[key] = {"back_color": '#eeeeee'} # grey

        dataline = []
        if i == 3:
            dataline.append("Number of samples"); dataline.append(i)
        else:
            dataline.append(''); dataline.append(i)
        dataline.extend(row)
        results.append(dataline)
        i+=1
    plot_data.numeric_data = results
    return plot_data



def perfindPlotter(s_data, plot_data, num_subplot=[1,1,1], **kwargs):
    """
    This function computes performance indices for assessors from a sensory
    panel.
    """
    print "perf ind plotter function..."

    assessorList = plot_data.activeAssessorsList
    attributeList = plot_data.activeAttributesList
    sampleList = plot_data.activeSamplesList
    replicateList = s_data.ReplicateList
    sparseMatrix = s_data.SparseMatrix

    numberOfAssessors = len(assessorList)
    numberOfAttributes = len(attributeList)
    numberOfSamples = len(sampleList)
    numberOfReplicates = len(s_data.ReplicateList)


    agr_lvl = plot_data.special_opts["agr"]
    rep_lvl = plot_data.special_opts["rep"]
    dis_lvl = plot_data.special_opts["dis"]
    lvl = plot_data.special_opts["lvl"]
    comp = plot_data.special_opts["comp"]
    target_lvl = plot_data.special_opts["target_lvl"]
    sign_lvl_1 = plot_data.special_opts["1_sign_lvl"]
    sign_lvl_5 = plot_data.special_opts["5_sign_lvl"]
    sign_lvl_10 = plot_data.special_opts["10_sign_lvl"]

    plot_data.plot_type = "perf_ind"
    plotType = plot_data.tree_path[0]
    print "tree path: " + plotType
    plot_data.special_opts["plot_frame"] = True
    resultList = []


    recalc = plot_data.special_opts["recalc"]

    plot_data.numeric_data_config = {}



    sign_val_1 = pid.get_sign_level(pid.RV1_1, numberOfSamples, numberOfAttributes)
    if sign_val_1 == None:
        show_err_msg("Number of samples or number of attributes is not within acctable range [3, 50]."); return



    # calculate and setup numeric data
    if plotType == u'AGR prod':
        if recalc or not plot_data.collection_calc_data.has_key("AGR"):
            res = calcAGR(s_data, plot_data)
            plot_data.collection_calc_data["AGR"] = res
        else:
            res = plot_data.collection_calc_data["AGR"]


        curr_lvl = agr_lvl
        agr = PerfIndData(res, "agr", comp, numberOfSamples, numberOfAttributes)
        conf_dict = agr.get_config("prod", assessorList, plotType, curr_lvl)


        dataline = []; dataline.append('Assessors'); dataline.extend(assessorList); resultList.append(dataline)
        dataline = []; dataline.append('AGR prod'); dataline.extend(agr.prod); resultList.append(dataline)
        dataline = []; dataline.append('AGR average'); dataline.extend(agr.average); resultList.append(dataline)
        dataline = []; dataline.append('Upper STD'); dataline.append(agr.std_prod_upper); resultList.append(dataline)
        dataline = []; dataline.append('Lower STD'); dataline.append(agr.std_prod_lower); resultList.append(dataline)

        dataline = []; resultList.append(dataline)
        dataline = []; dataline.append('Method'); dataline.append(comp); resultList.append(dataline)
        dataline = []; dataline.append('1% sign. level'); dataline.append(agr.sign_val_1); resultList.append(dataline)
        dataline = []; dataline.append('5% sign. level'); dataline.append(agr.sign_val_5); resultList.append(dataline)
        dataline = []; dataline.append('10% sign. level'); dataline.append(agr.sign_val_10); resultList.append(dataline)
        dataline = []; dataline.append('Target level'); dataline.append(curr_lvl); resultList.append(dataline)
        plot_data.numeric_data = resultList

        # make plot
        makePlot(plot_data, num_subplot, conf_dict, target_lvl, sign_lvl_1, sign_lvl_5, sign_lvl_10)

    elif plotType == u'AGR att':
        if recalc or not plot_data.collection_calc_data.has_key("AGR"):
            res = calcAGR(s_data, plot_data)
            plot_data.collection_calc_data["AGR"] = res
        else:
            res = plot_data.collection_calc_data["AGR"]

        curr_lvl = agr_lvl
        agr = PerfIndData(res, "agr", comp, numberOfSamples, numberOfAttributes)
        conf_dict = agr.get_config("att", assessorList, plotType, curr_lvl)

        dataline = []; dataline.append('Assessors'); dataline.extend(assessorList); resultList.append(dataline)
        dataline = []; dataline.append('AGR att'); dataline.extend(agr.att); resultList.append(dataline)
        dataline = []; dataline.append('AGR average'); dataline.extend(agr.average); resultList.append(dataline)
        dataline = []; dataline.append('Upper STD'); dataline.append(agr.std_prod_upper); resultList.append(dataline)
        dataline = []; dataline.append('Lower STD'); dataline.append(agr.std_prod_lower); resultList.append(dataline)



        dataline = []; resultList.append(dataline)
        dataline = []; dataline.append('Method'); dataline.append(comp); resultList.append(dataline)
        dataline = []; dataline.append('1% sign. level'); dataline.append(agr.sign_val_1); resultList.append(dataline)
        dataline = []; dataline.append('5% sign. level'); dataline.append(agr.sign_val_5); resultList.append(dataline)
        dataline = []; dataline.append('10% sign. level'); dataline.append(agr.sign_val_10); resultList.append(dataline)
        dataline = []; dataline.append('Target level'); dataline.append(curr_lvl); resultList.append(dataline)
        plot_data.numeric_data = resultList


        # make plot
        makePlot(plot_data, num_subplot, conf_dict, target_lvl, sign_lvl_1, sign_lvl_5, sign_lvl_10)


    elif plotType == u'p values for AGR and REP':
        if numberOfReplicates == 1:
            show_err_msg("Number of replicates must be 2 or more."); return
        res_agr = calcAGR(s_data, plot_data, permutationTestEnabled = True)
        res_rep = calcREP(s_data, plot_data, permutationTestEnabled = True)

        curr_lvl = agr_lvl
        agr = PerfIndData(res_agr, "agr", comp, numberOfSamples, numberOfAttributes)
        rep = PerfIndData(res_rep, "rep", comp, numberOfSamples, numberOfAttributes)
        conf_dict = agr.get_config("att", assessorList, plotType, curr_lvl)

        dataline = []; dataline.append('Assessors'); dataline.extend(assessorList); resultList.append(dataline)
        dataline = []; dataline.append('AGR prod p'); dataline.extend(agr.prod_p); resultList.append(dataline)
        dataline = []; dataline.append('AGR att p'); dataline.extend(agr.att_p); resultList.append(dataline)
        dataline = []; dataline.append('REP prod p'); dataline.extend(rep.prod_p); resultList.append(dataline)
        dataline = []; dataline.append('REP att p'); dataline.extend(rep.att_p); resultList.append(dataline)

        dataline = []; resultList.append(dataline)
        dataline = []; dataline.append('Method'); dataline.append(comp); resultList.append(dataline)
        dataline = []; dataline.append('1% sign. level'); dataline.append(rep.sign_val_1); resultList.append(dataline)
        dataline = []; dataline.append('5% sign. level'); dataline.append(rep.sign_val_5); resultList.append(dataline)
        dataline = []; dataline.append('10% sign. level'); dataline.append(rep.sign_val_10); resultList.append(dataline)
        dataline = []; dataline.append('Target level'); dataline.append(curr_lvl); resultList.append(dataline)
        plot_data.numeric_data = resultList

        # make plot
        #makePlot(plot_data, num_subplot, conf_dict)
        plot_data.special_opts["plot_frame"] = False


    elif plotType == u'REP prod':
        if numberOfReplicates == 1:
            show_err_msg("Number of replicates must be 2 or more."); return
        if recalc or not plot_data.collection_calc_data.has_key("REP"):
            res_rep = calcREP(s_data, plot_data)
            plot_data.collection_calc_data["REP"] = res_rep
        else:
            res_rep = plot_data.collection_calc_data["REP"]

        curr_lvl = rep_lvl
        rep = PerfIndData(res_rep, "rep", comp, numberOfSamples, numberOfAttributes)
        conf_dict = rep.get_config("prod", assessorList, plotType, curr_lvl)

        dataline = []; dataline.append('Assessors'); dataline.extend(assessorList); resultList.append(dataline)
        dataline = []; dataline.append('REP prod'); dataline.extend(rep.prod); resultList.append(dataline)
        dataline = []; dataline.append('REP att'); dataline.extend(rep.att); resultList.append(dataline)
        dataline = []; dataline.append('Upper STD'); dataline.append(rep.std_prod_upper); resultList.append(dataline)
        dataline = []; dataline.append('Lower STD'); dataline.append(rep.std_prod_lower); resultList.append(dataline)

        dataline = []; resultList.append(dataline)
        dataline = []; dataline.append('Method'); dataline.append(comp); resultList.append(dataline)
        dataline = []; dataline.append('1% sign. level'); dataline.append(rep.sign_val_1); resultList.append(dataline)
        dataline = []; dataline.append('5% sign. level'); dataline.append(rep.sign_val_5); resultList.append(dataline)
        dataline = []; dataline.append('10% sign. level'); dataline.append(rep.sign_val_10); resultList.append(dataline)
        dataline = []; dataline.append('Target level'); dataline.append(curr_lvl); resultList.append(dataline)
        plot_data.numeric_data = resultList


        # make plot
        makePlot(plot_data, num_subplot, conf_dict, target_lvl, sign_lvl_1, sign_lvl_5, sign_lvl_10)


    elif plotType == u'REP att':
        if numberOfReplicates == 1:
            show_err_msg("Number of replicates must be 2 or more."); return
        if recalc or not plot_data.collection_calc_data.has_key("REP"):
            res_rep = calcREP(s_data, plot_data)
            plot_data.collection_calc_data["REP"] = res_rep
        else:
            res_rep = plot_data.collection_calc_data["REP"]

        curr_lvl = rep_lvl
        rep = PerfIndData(res_rep, "rep", comp, numberOfSamples, numberOfAttributes)
        conf_dict = rep.get_config("att", assessorList, plotType, curr_lvl)

        dataline = []; dataline.append('Assessors'); dataline.extend(assessorList); resultList.append(dataline)
        dataline = []; dataline.append('REP prod'); dataline.extend(rep.prod); resultList.append(dataline)
        dataline = []; dataline.append('REP att'); dataline.extend(rep.att); resultList.append(dataline)
        dataline = []; dataline.append('Upper STD'); dataline.append(rep.std_att_upper); resultList.append(dataline)
        dataline = []; dataline.append('Lower STD'); dataline.append(rep.std_att_lower); resultList.append(dataline)

        dataline = []; resultList.append(dataline)
        dataline = []; dataline.append('Method'); dataline.append(comp); resultList.append(dataline)
        dataline = []; dataline.append('1% sign. level'); dataline.append(rep.sign_val_1); resultList.append(dataline)
        dataline = []; dataline.append('5% sign. level'); dataline.append(rep.sign_val_5); resultList.append(dataline)
        dataline = []; dataline.append('10% sign. level'); dataline.append(rep.sign_val_10); resultList.append(dataline)
        dataline = []; dataline.append('Target level'); dataline.append(curr_lvl); resultList.append(dataline)
        plot_data.numeric_data = resultList


        # make plot
        makePlot(plot_data, num_subplot, conf_dict, target_lvl, sign_lvl_1, sign_lvl_5, sign_lvl_10)

    elif plotType == u'DIS total':
        if numberOfReplicates == 1:
            show_err_msg("Number of replicates must be 2 or more."); return
        if recalc or not plot_data.collection_calc_data.has_key("DIS"):
            res_dis = calcDIS(s_data, plot_data)
            plot_data.collection_calc_data["DIS"] = res_dis
        else:
            res_dis = plot_data.collection_calc_data["DIS"]

        
        curr_lvl = dis_lvl
        dataline = []; dataline.append('DIS count ind'); dataline.extend(res_dis['DIS count ind']); resultList.append(dataline)
        dataline = []; dataline.append('DIS count all_ex1'); dataline.extend(res_dis['DIS count all_ex1'])
        dataline = []; dataline.append('DIS'); dataline.extend(res_dis['DIS']); resultList.append(dataline)
        dataline = []; dataline.append('DIS2'); dataline.extend(res_dis['DIS2']); resultList.append(dataline)
        dataline = []; dataline.append('DIS sign all panel'); dataline.append(res_dis['DIS sign all panel']); resultList.append(dataline)
        plot_data.numeric_data = resultList
        
        
        conf_dict = {}
        conf_dict["elements"] = assessorList #res_dis['DIS count ind']
        conf_dict["values1"] = res_dis['DIS']
        #conf_dict["values2"] = res_dis['DIS2']
        conf_dict["title"] = plotType  
        conf_dict["vType"] = plotType
        conf_dict["target"] = curr_lvl

        # make plot
        makePlotDIS(plot_data, num_subplot, conf_dict, target_lvl)
        #plot_data.special_opts["plot_frame"] = False

    elif plotType == u"DIS panel-1":
        if numberOfReplicates == 1:
            show_err_msg("Number of replicates must be 2 or more."); return
        if recalc or not plot_data.collection_calc_data.has_key("DIS"):
            res_dis = calcDIS(s_data, plot_data)
            plot_data.collection_calc_data["DIS"] = res_dis
        else:
            res_dis = plot_data.collection_calc_data["DIS"]

        curr_lvl = dis_lvl
        dataline = []; dataline.append('DIS count ind'); dataline.extend(res_dis['DIS count ind']); resultList.append(dataline)
        dataline = []; dataline.append('DIS count all_ex1'); dataline.extend(res_dis['DIS count all_ex1'])
        dataline = []; dataline.append('DIS'); dataline.extend(res_dis['DIS']); resultList.append(dataline)
        dataline = []; dataline.append('DIS2'); dataline.extend(res_dis['DIS2']); resultList.append(dataline)
        dataline = []; dataline.append('DIS sign all panel'); dataline.append(res_dis['DIS sign all panel']); resultList.append(dataline)
        plot_data.numeric_data = resultList

        conf_dict = {}
        conf_dict["elements"] = assessorList #res_dis['DIS count ind']
        conf_dict["values1"] = res_dis['DIS2']
        #conf_dict["values2"] = res_dis['DIS']
        conf_dict["title"] = plotType
        conf_dict["vType"] = plotType
        conf_dict["target"] = curr_lvl


        # make plot
        makePlotDIS(plot_data, num_subplot, conf_dict, target_lvl)
        #plot_data.special_opts["plot_frame"] = False


    elif plotType == u'RV for 1% sign. level':
        plot_data.special_opts["plot_frame"] = False
        return set_sign_level_numeric_data(pid.RV1_1, plot_data, numberOfSamples, numberOfAttributes)

    elif plotType == u'RV for 5% sign. level':
        plot_data.special_opts["plot_frame"] = False
        return set_sign_level_numeric_data(pid.RV1_5, plot_data, numberOfSamples, numberOfAttributes)

    elif plotType == u'RV for 10% sign. level':
        plot_data.special_opts["plot_frame"] = False
        return set_sign_level_numeric_data(pid.RV1_10, plot_data, numberOfSamples, numberOfAttributes)

    elif plotType == u'RV2 for 1% sign. level':
        plot_data.special_opts["plot_frame"] = False
        return set_sign_level_numeric_data(pid.RV2_1, plot_data, numberOfSamples, numberOfAttributes)

    elif plotType == u'RV2 for 5% sign. level':
        plot_data.special_opts["plot_frame"] = False
        return set_sign_level_numeric_data(pid.RV2_5, plot_data, numberOfSamples, numberOfAttributes)

    elif plotType == u'RV2 for 10% sign. level':
        plot_data.special_opts["plot_frame"] = False
        return set_sign_level_numeric_data(pid.RV2_10, plot_data, numberOfSamples, numberOfAttributes)

    elif plotType == u'Indices table':
        plot_data.special_opts["plot_frame"] = False
        if numberOfReplicates == 1:
            if recalc or not plot_data.collection_calc_data.has_key("AGR"):
                res_agr = calcAGR(s_data, plot_data)
                plot_data.numeric_data_config["AGR"] = res_agr
            else:
                res_agr = plot_data.collection_calc_data["AGR"]

            curr_lvl = agr_lvl
            agr = PerfIndData(res_agr, "agr", comp, numberOfSamples, numberOfAttributes)            
            dataline = []; dataline.append('Assessors'); dataline.extend(assessorList); dataline.append("Average"); dataline.append("STD"); resultList.append(dataline)

            dataline = []; dataline.append('AGR prod'); dataline.extend(agr.prod); dataline.append(round(agr.average_prod, 2)); dataline.append(round(agr.std_prod, 2)); resultList.append(dataline)
            dataline = []; dataline.append('AGR att'); dataline.extend(agr.att); dataline.append(round(agr.average_att, 2)); dataline.append(round(agr.std_att, 2)); resultList.append(dataline)
            dataline = []; dataline.append(''); resultList.append(dataline)
            
            dataline = []; dataline.append("Total # of attr"); resultList.append(dataline)
            dataline = []; dataline.append(numberOfAttributes); resultList.append(dataline)
            
        else:
            if recalc or not plot_data.collection_calc_data.has_key("AGR"):
                res_agr = calcAGR(s_data, plot_data)
                plot_data.numeric_data_config["AGR"] = res_agr
            else:
                res_agr = plot_data.collection_calc_data["AGR"]

            if recalc or not plot_data.collection_calc_data.has_key("REP"):
                res_rep = calcREP(s_data, plot_data)
                plot_data.collection_calc_data["REP"] = res_rep
            else:
                res_rep = plot_data.collection_calc_data["REP"]

            if recalc or not plot_data.collection_calc_data.has_key("DIS"):
                res_dis = calcDIS(s_data, plot_data)
                plot_data.collection_calc_data["DIS"] = res_dis
            else:
                res_dis = plot_data.collection_calc_data["DIS"]

            curr_lvl = agr_lvl
            agr = PerfIndData(res_agr, "agr", comp, numberOfSamples, numberOfAttributes)
            rep = PerfIndData(res_rep, "rep", comp, numberOfSamples, numberOfAttributes)

            dataline = []; dataline.append('Assessors'); dataline.extend(assessorList); dataline.append("Average"); dataline.append("STD"); resultList.append(dataline)

            dataline = []; dataline.append('AGR prod'); dataline.extend(agr.prod); dataline.append(round(agr.average_prod, 2)); dataline.append(round(agr.std_prod, 2)); resultList.append(dataline)
            dataline = []; dataline.append('AGR att'); dataline.extend(agr.att); dataline.append(round(agr.average_att, 2)); dataline.append(round(agr.std_att, 2)); resultList.append(dataline)
            dataline = []; dataline.append(''); resultList.append(dataline)
            dataline = []; dataline.append('REP prod'); dataline.extend(rep.prod); dataline.append(round(rep.average_prod, 2)); dataline.append(round(rep.std_prod, 2)); resultList.append(dataline)
            dataline = []; dataline.append('REP att'); dataline.extend(rep.att); dataline.append(round(rep.average_att, 2)); dataline.append(round(rep.std_att, 2)); resultList.append(dataline)
            dataline = []; dataline.append(''); resultList.append(dataline)

            curr_lvl = dis_lvl
            dataline = []; dataline.append('DIS total'); dataline.extend(res_dis['DIS2']); resultList.append(dataline)
            dataline = []; dataline.append('DIS panel-1'); dataline.extend(res_dis['DIS']); resultList.append(dataline)
            dataline = []; dataline.append(''); resultList.append(dataline)
            dataline = []; dataline.append(''); resultList.append(dataline)
            dataline = []; dataline.append(''); resultList.append(dataline)

            dataline = []; dataline.append('Assessors'); dataline.extend(assessorList); dataline.append("# sign attr panel"); dataline.append("Total # of attr"); resultList.append(dataline)
            dataline = []; dataline.append('# sign attr individ'); dataline.extend(res_dis['DIS count ind']); resultList.append(dataline)
            dataline = []; dataline.append('# sign attr panel ex individ'); dataline.extend(res_dis['DIS count all_ex1']); dataline.append(res_dis['DIS sign all panel']); dataline.append(numberOfAttributes); resultList.append(dataline)

            #dataline = []; dataline.append('DIS sign all panel'); dataline.append(res_dis['DIS sign all panel']); resultList.append(dataline) dataline.append(length(attributeList));
            print res_dis.keys()
            print 'active attributes list: ', len(attributeList)

        plot_data.numeric_data = resultList

    plot_data.raw_data = raw_data_grid(s_data, plot_data)
    return plot_data



def makePlot(plot_data, num_subplot, conf_dict, target_on, s1, s5, s10):

    elements = conf_dict["elements"] # attributes|assessors
    y_values = conf_dict["values"] # agr|rep
    value_type = conf_dict["vtype"] # agr|rep
    title = conf_dict["title"] # att|prod


    print "making perf ind plot..."

    # Figure
    replot = True; subplot = plot_data.overview_plot; scatter_width = 35
    if plot_data.fig != None: replot = True
    else: plot_data.fig = Figure(None)
    if subplot: # is subplot
        plot_data.ax = plot_data.fig.add_subplot(num_subplot[0], num_subplot[1], num_subplot[2])
        scatter_width = 15
    else: plot_data.ax = axes_create(plot_data.view_legend, plot_data.fig)
    ax = plot_data.ax; fig = plot_data.fig

    limits = [1, len(elements)+1, 0, 100]
    if not subplot:
        axes_setup(ax, '', '', title, limits)
        set_xlabeling(ax, elements)
        if len(elements) > 7:
            set_xlabeling_rotation(ax, 'vertical')
    else:
        axes_setup(ax, '', '', title, limits, font_size=10)


    ax.grid(plot_data.view_grid)

    lines = []
    lables = []

    slvl1 = []
    slvl5 = []
    slvl10 = []
    target_lvl = []
    aver = []
    upper_std = []
    lower_std = []
    x_values = []
    x_values_elements = []
    for i in range(1, len(y_values)+1):
        x_values_elements.append(i)
    for i in range(0, len(elements)+2):
        slvl1.append(conf_dict["slvl1"])
        slvl5.append(conf_dict["slvl5"])
        slvl10.append(conf_dict["slvl10"])
        target_lvl.append(conf_dict["target"])
        aver.append(conf_dict["average"])
        upper_std.append(conf_dict["upper_std"])
        lower_std.append(conf_dict["lower_std"])
        x_values.append(i)



    colors = ['#0037CC', '#FF8A00', '#FFD800', '#999999', '#29CC29', '#000000', '#000000', '#000000']
    linestyles = ['-', '--', '--', '--', '-', '-', ':', ':']

    ind = 0
    print x_values; print y_values
    lines.append(ax.plot(x_values_elements, y_values, color=colors[ind], linestyle=linestyles[ind], linewidth=2))
    lables.append(value_type)
    ind += 1

    if s1:
        lines.append(ax.plot(x_values, slvl1, color=colors[ind], linestyle=linestyles[ind]))
        lables.append("1% sign. level")
    ind += 1
    if s5:
        lines.append(ax.plot(x_values, slvl5, color=colors[ind], linestyle=linestyles[ind]))
        lables.append("5% sign. level")
    ind += 1
    if s10:
        lines.append(ax.plot(x_values, slvl10, color=colors[ind], linestyle=linestyles[ind]))
        lables.append("10% sign. level")
    ind += 1
    if target_on:
        lines.append(ax.plot(x_values, target_lvl, color=colors[ind], linestyle=linestyles[ind], linewidth=2))
        lables.append("Target level")
    ind += 1
    lines.append(ax.plot(x_values, aver, color=colors[ind], linestyle=linestyles[ind])); ind += 1
    lables.append("Average")

    lines.append(ax.plot(x_values, upper_std, color=colors[ind], linestyle=linestyles[ind])); ind += 1
    lables.append("Upper STD")

    lines.append(ax.plot(x_values, lower_std, color=colors[ind], linestyle=linestyles[ind])); ind += 1
    lables.append("Lower STD")

    pointAndLabelList = []
    for i in range(len(y_values)):
        pointAndLabelList.append([i+1, y_values[i], elements[i], 1])
        ax.scatter([i+1], [y_values[i]], s = scatter_width, color = '#0037CC', marker = 's')



    if not subplot:
        figlegend = fig.legend(lines, lables, 'upper right')
    else:
        lables[0] = "prod/att"
        figlegend = fig.legend(lines, lables, 'upper right')
        
    min1 = min(min(y_values), min(y_values))-10
    max1 = max(max(y_values), max(y_values))+10
    if min1 > 0: min1 = 0
    if max1 < 110: max1 = 110    
    ax.set_ylim([min1,max1])



    #update plot-data variables:
    plot_data.point_lables = pointAndLabelList
    plot_data.point_lables_type = 0


def makePlotDIS(plot_data, num_subplot, conf_dict, target_on):

    y_values1 = conf_dict["values1"] 
    #y_values2 = conf_dict["values2"] 
    title = conf_dict["title"] # att|prod
    vType = conf_dict["vType"] # att|prod

    
    elements = []
    for e in conf_dict["elements"]:
        elements.append(str(e))
    
    print "making perf ind DIS plot..."

    # Figure
    replot = True; subplot = plot_data.overview_plot; scatter_width = 35
    if plot_data.fig != None: replot = True
    else: plot_data.fig = Figure(None)
    if subplot: # is subplot
        plot_data.ax = plot_data.fig.add_subplot(num_subplot[0], num_subplot[1], num_subplot[2])
        scatter_width = 15
    else: plot_data.ax = axes_create(plot_data.view_legend, plot_data.fig)
    ax = plot_data.ax; fig = plot_data.fig

    limits = [1, len(elements)+1, 0, 100]
    if not subplot:
        axes_setup(ax, '', '', title, limits)
        set_xlabeling(ax, elements)
        if len(elements) > 7:
            set_xlabeling_rotation(ax, 'vertical')
    else:
        axes_setup(ax, '', '', title, limits, font_size=10)


    ax.grid(plot_data.view_grid)

    lines = []
    lables = []

    aver = []
    target_lvl = []
    x_values = []
    x_values_elements = []
    for i in range(1, len(y_values1) + 1):
        x_values_elements.append(i)
    
    for i in range(0, len(elements)+2):
        target_lvl.append(conf_dict["target"])
        x_values.append(i)

    colors = ['#FF8A00', '#29CC29', '#FFD800', '#999999', '#29CC29', '#000000', '#000000', '#000000']
    linestyles = ['-', '-', '--', '-', '-', ':', ':']

    ind = 0
    print x_values; print y_values1; #print y_values2
    lines.append(ax.plot(x_values_elements, y_values1, color=colors[ind], linestyle=linestyles[ind], linewidth=2)); ind += 1
    #lines.append(ax.plot(x_values_elements, y_values2, color=colors[ind], linestyle=linestyles[ind], linewidth=2)); ind += 1
    lables.append('DIS')
    if target_on:
        lines.append(ax.plot(x_values, target_lvl, color=colors[ind], linestyle=linestyles[ind], linewidth=2))
        lables.append("Target level")
    ind += 1

    pointAndLabelList = []
    for i in range(len(y_values1)):
        pointAndLabelList.append([i+1, y_values1[i], str(elements[i]), 1])
        ax.scatter([i+1], [y_values1[i]], s = scatter_width, color = '#FF8A00', marker = 's')
    #for i in range(len(y_values2)):
    #    pointAndLabelList.append([i+1, y_values2[i], elements[i], 1])
    #    ax.scatter([i+1], [y_values2[i]], s = scatter_width, color = '#0037CC', marker = 's')        

    if not subplot:
        figlegend = fig.legend(lines, lables, 'upper right')
    else:
        figlegend = fig.legend(lines, lables, 'lower right')
    #ax.set_ylim([min(min(y_values1), min(y_values1))-10,max(max(y_values1), max(y_values1))+10])

    min1 = min(min(y_values1), min(y_values1))-10
    max1 = max(max(y_values1), max(y_values1))+10
    if min1 > 0: min1 = 0
    if max1 < 110: max1 = 110    
    ax.set_ylim([min1,max1])

    #update plot-data variables:
    plot_data.point_lables = pointAndLabelList
    plot_data.point_lables_type = 0


def permuationTestRV(arrList, RVtype='RV2', numPerm=999, sigLevel=0.05):
    """
    This function carries out a permutation test for RV / mod RV / adj RV. It
    returns a p value based on a number of iterations.
    """
    # First make a copy of array list, because the copy will be altered during
    # the construction of list with pair-wise combinations of arrays.
    arrListCopy = arrList[:]

    # arrList can contain multiple arrays, not only just two. This is why a
    # process is needed that finds all possible pairwise combinations
    # of the provided arrays.
    dataPairsList = []

    for origInd in range(len(arrList) - 1):

        if len(arrListCopy) == 1:
            break

        elif len(arrListCopy) == 2:
            dataList = arrListCopy
            dataPairsList.append(dataList)

        else:
            for arrInd, arr in enumerate(arrListCopy):
                firstArr = arrListCopy[0]
                nextArr = arrListCopy[arrInd+1]
                dataList = [firstArr, nextArr]
                dataPairsList.append(dataList)

                if arrInd == (len(arrListCopy) - 2):
                    arrListCopy.pop(0)
                    continue
    # Collect all permuted p values in a list which is eventually returned by
    # this function.
    pValList = []

    # Now do permutation test for all pairwise combinations of arrays
    for arrCombList in dataPairsList:

        # First compute RV or RV2
        if RVtype == 'RV':
            coeffMat = st.RVcoeff(arrCombList)
        elif RVtype == 'RV2':
            coeffMat = st.RV2coeff(arrCombList)
        value = coeffMat[0,1]

        # Check array dimensions for one of the arrays. It doesn't matter which one,
        # since we are interested only in number of rows. Number of columns in
        # any of arrays is non-relevant for permutation.
        rows, cols = np.shape(arrList[1])

        # Construct a list with a range of numbers. This list will be shuffled later
        # below in the permutation test, providing a new order of the rows in the
        # permuted array.
        rowOrder = range(rows)

        # Run permutation loop.
        permCoeffList = []
        for run in range(numPerm):

            rnd.shuffle(rowOrder)
            permArray = np.zeros((rows, cols))

            for num in range(rows):
                permArray[num,:] = arrCombList[1][rowOrder[num],:]

            data = [arrList[0], permArray]

            if RVtype == 'RV':
                coeffMat = st.RVcoeff(data)
            elif RVtype == 'RV2':
                coeffMat = st.RV2coeff(data)
            permCoeffList.append(coeffMat[0,1])

        # Now sort the list Rv coefficients from permuatation. This is done, such that
        # one can find significance values.
        permCoeffList.sort()

        # Compute the position permuted RV at the required signficance level.
        # if permuted RV (at requiered sign level) > RV ==> RV not significant
        # if permuted RV (at requiered sign level) < RV ==> RV significant
        sigPos = int(round((numPerm + 1) * (1-sigLevel)))

        sig = permCoeffList[sigPos]

        #print '{0} = '.format(RVtype), value # for Python 2.7
        #print 'permuted {0} at {1}%: '.format(RVtype,str(int(sigLevel * 100))), sig # for Python 2.7

        print '%s = ' % RVtype, value
        #print 'permuted %s at s% ' % (RVtype, str(sigLevel * 100)), sig
        print 'permuted', RVtype, 'at', str(sigLevel * 100), sig

        # Compute permutated p value
        # Find out where the initial RV is located in the sorted list of
        # permuted RV coefficients. Permuted p value is then number of RV's bigger
        # than the initial one divided by number of permuation runs + 1.
        for ind, val in enumerate(permCoeffList):
            if val > value:
                break

        # Need to use a float for computation of p value. numPerm is an integer
        # which is why p would always become exactly 0.
        #floatNumPerm = float(numPerm)
        p = ((numPerm + 1) - (ind - 1)) / (numPerm + 1)
        print 'p =', p
        print

        pValList.append(p)
        #pValList.append(round(p, 3))

    return pValList
    #return [pValList, sig]


# Function for cross validation of AGR_prod
def cv_AGR_prod(s_data, plot_data, dbclkAss):

    actAssList = plot_data.activeAssessorsList
    actSampList = plot_data.activeSamplesList
    repList = s_data.ReplicateList
    actAttList = plot_data.activeAttributesList
    sMat = s_data.SparseMatrix
    rvType = plot_data.special_opts["comp"]


    print 'cv of AGR prod'
    print '--------------'
    print actAssList
    print actSampList
    print actAttList
    print dbclkAss
    print rvType
    print


    # First get average matrix for the double-clicked assessor
    specArrSP, specArr = s_data.GetAssessorAverageData(dbclkAss)

    # Now get consensus for all active assessors EXCEPT the double clicked
    red_actAssList = actAssList[:]
    red_actAssList.pop(actAssList.index(dbclkAss))

    rows, cols = np.shape(specArr)
    sumArr = np.zeros((rows, cols))

    redArrList = []
    for ass in red_actAssList:
        arrSP, arr = s_data.GetAssessorAverageData(ass)
        sumArr = np.add(sumArr, arr)
        redArrList.append(sumArr)

    specConsArr = sumArr / len(red_actAssList)

    # +++++++++++++++++++++++
    # THIS IS PANELCHECK CODE
    # Now compute RV or RV2 between consensus without double-clicked assessor
    # and the data from the double-clicked assessor

    # First compute value that is in the grid and that was double clicked on.
    # This will be the dashed line in the influence plot

    # Center both arrays
    cent_specArr = st.centre(specArr)
    cent_specConsArr = st.centre(specConsArr)

    # Check whether RV or RV2 was chosen by user and compute reference value
    data = [cent_specArr, cent_specConsArr]
    if rvType == 'RV':
        coeffMat = st.RVcoeff(data)
    elif rvType == 'RV2':
        coeffMat = st.RV2coeff(data)

    refValue = round(coeffMat[0,1] * 100, 1)
    print refValue

    # Then compute RV or RV2 for each time one sample is left out.
    dropSampList = []
    sampValueList = []

    for ind in range(np.shape(specArr)[0]):

        subList = []
        subM1 = np.delete(cent_specArr, ind, 0)
        subM2 = np.delete(cent_specConsArr, ind, 0)
        subList.append(subM1)
        subList.append(subM2)

        dropSampList.append(subList)

        if rvType == 'RV':
            subValue = st.RVcoeff(subList)[0,1]
        elif rvType == 'RV2':
            subValue = st.RV2coeff(subList)[0,1]

        sampValueList.append(round(subValue * 100, 1))

    print sampValueList

    plot_data.fig = Figure(None)
    elements = actSampList
    titleString = 'AGR prod cross validation: Assessor ' + dbclkAss + ': '
    plotTypeLabel = 'AGR prod'
    makeCvAgrPlot(plot_data, [1,1,1], sampValueList, refValue, elements, titleString, dbclkAss, plotTypeLabel)


    return refValue, sampValueList




# Function for cross validation of AGR_att
def cv_AGR_att(s_data, plot_data, dbclkAss):

    actAssList = plot_data.activeAssessorsList
    actSampList = plot_data.activeSamplesList
    repList = s_data.ReplicateList
    actAttList = plot_data.activeAttributesList
    sMat = s_data.SparseMatrix
    rvType = plot_data.special_opts["comp"]


    print 'cv of AGR att'
    print '--------------'
    print actAssList
    print actSampList
    print actAttList
    print dbclkAss
    print rvType
    print



    # First get average matrix for the double-clicked assessor
    specArrSP, specArr = s_data.GetAssessorAverageData(dbclkAss)

    # Now get consensus for all active assessors EXCEPT the double clicked
    red_actAssList = actAssList[:]
    red_actAssList.pop(actAssList.index(dbclkAss))

    rows, cols = np.shape(specArr)
    sumArr = np.zeros((rows, cols))

    redArrList = []
    for ass in red_actAssList:
        arrSP, arr = s_data.GetAssessorAverageData(ass)
        sumArr = np.add(sumArr, arr)
        redArrList.append(sumArr)

    specConsArr = sumArr / len(red_actAssList)

    print "CV AGR ATT ---- 1"

    # +++++++++++++++++++++++
    # THIS IS PANELCHECK CODE
    # Now compute RV or RV2 between consensus without double-clicked assessor
    # and the data from the double-clicked assessor

    # First compute value that is in the grid and that was double clicked on.
    # This will be the dashed line in the influence plot

    # Center both arrays
    tr_cent_specArr = np.transpose(st.centre(specArr))
    tr_cent_specConsArr = np.transpose(st.centre(specConsArr))

    # Check whether RV or RV2 was chosen by user and compute reference value
    data = [tr_cent_specArr, tr_cent_specConsArr]
    if rvType == 'RV':
        coeffMat = st.RVcoeff(data)
    elif rvType == 'RV2':
        coeffMat = st.RV2coeff(data)

    refValue = round(coeffMat[0,1] * 100, 1)
    print refValue

    # Then compute RV or RV2 for each time one sample is left out.
    dropAttList = []
    sampValueList = []

    for ind in range(np.shape(specArr)[1]):

        subList = []
        subM1 = np.delete(tr_cent_specArr, ind, 0)
        subM2 = np.delete(tr_cent_specConsArr, ind, 0)
        subList.append(subM1)
        subList.append(subM2)

        dropAttList.append(subList)

        if rvType == 'RV':
            subValue = st.RVcoeff(subList)[0,1]
        elif rvType == 'RV2':
            subValue = st.RV2coeff(subList)[0,1]

        sampValueList.append(round(subValue * 100, 1))

    print "CV AGR ATT ---- 2"
    print(sampValueList, len(sampValueList))

    plot_data.fig = Figure(None)
    elements = actAttList
    titleString = 'AGR att cross validation: Assessor ' + dbclkAss
    plotTypeLabel = 'AGR att'
    makeCvAgrPlot(plot_data, [1,1,1], sampValueList, refValue, elements, titleString, dbclkAss, plotTypeLabel)

    return refValue, sampValueList





# Function for cross validation of REP_prod
def cv_REP_prod(s_data, plot_data, dbclkAss):

    actAssList = plot_data.activeAssessorsList
    actSampList = plot_data.activeSamplesList
    repList = s_data.ReplicateList
    actAttList = plot_data.activeAttributesList
    sMat = s_data.SparseMatrix
    rvType = plot_data.special_opts["comp"]


    print 'cv of REP prod'
    print '--------------'
    print actAssList
    print actSampList
    print actAttList
    print dbclkAss
    print rvType
    print


    if len(repList) <= 1: return

    # Collect replicate arrays for double-clicked assessor
    repArrList = []

    # Loop through all replicates
    for repInd in repList:
        print repInd

        # First get average matrix for the double-clicked assessor
        repArrSP, repArr = s_data.GetAssessorReplicateData(dbclkAss, repInd)
        repArrList.append(repArr)


    # Now compute RV or RV2 between all replicate matrices. Three different
    # cases need to be considered.
    # Case 1: data has only one replicate
    # Case 1: data has two replicates
    # Case 2: data has more than two replicates

    # Loop through repArrList and center all arrays
    iterList = []
    for arr in repArrList:
        c_arr = st.centre(arr)
        tr_c_arr = np.transpose(c_arr)
        #iterList.append(tr_c_arr)
        iterList.append(c_arr)

    # Construct a list with all possible pairwise combinations arrays in repArrList
    combList = list(combinations(iterList, 2))
    combNameList = list(combinations(repList, 2))

    results = {}

    plot_data.fig = Figure(None)
    num = 1
    num_plots = len(combList)
    if num_plots > 1:
        num = 1
    num_edge = int(ceil(sqrt(num_plots)))

    # Now run RV2 computations for all possible pair-wise combinations
    for pairInd, pair in enumerate(combList):


        # *************** INFLUENCE REP prod ***************
        if rvType == 'RV':
            coeffMat = st.RVcoeff(pair)
        elif rvType == 'RV2':
            coeffMat = st.RV2coeff(pair)

        refValue = round(coeffMat[0,1] * 100, 1)

        dropSampList = []
        sampValueList = []

        for ind in range(np.shape(pair[0])[0]):

            subList = []
            subM1 = np.delete(pair[0], ind, 0)
            subM2 = np.delete(pair[1], ind, 0)
            subList.append(subM1)
            subList.append(subM2)

            dropSampList.append(subList)

            if rvType == 'RV':
                subValue = st.RVcoeff(subList)[0,1]
            elif rvType == 'RV2':
                subValue = st.RV2coeff(subList)[0,1]

            sampValueList.append(round(subValue * 100, 1))

        results[combNameList[pairInd]] = [refValue, sampValueList]


        elements = actSampList
        # TODO (Henning): Active attributes in case of ONE plot?
        if num_plots == 1:
            elements = actSampList

        titleString = 'REP prod cross validation: Assessor ' + dbclkAss + \
                ' - rep ' + combNameList[pairInd][0] + \
                ' vs rep ' + combNameList[pairInd][1]
        plotTypeLabel = 'REP prod'
        makeCvRepPlot(plot_data, [num_edge,num_edge,num], sampValueList, refValue, elements, pair, pairInd, titleString, dbclkAss, plotTypeLabel)
        num += 1

    return results


# Function for cross validation of REP_att
def cv_REP_att(s_data, plot_data, dbclkAss):

    actAssList = plot_data.activeAssessorsList
    actSampList = plot_data.activeSamplesList
    repList = s_data.ReplicateList
    actAttList = plot_data.activeAttributesList
    sMat = s_data.SparseMatrix
    rvType = plot_data.special_opts["comp"]


    print 'cv of REP att'
    print '--------------'
    print actAssList
    print actSampList
    print actAttList
    print dbclkAss
    print rvType
    print



    if len(repList) <= 1: return

    # Collect replicate arrays for double-clicked assessor
    repArrList = []

    # Loop through all replicates
    for repInd in repList:
        print repInd

        # First get average matrix for the double-clicked assessor
        repArrSP, repArr = s_data.GetAssessorReplicateData(dbclkAss, repInd)
        repArrList.append(repArr)



    # Now compute RV or RV2 between all replicate matrices. Three different
    # cases need to be considered.
    # Case 1: data has only one replicate
    # Case 1: data has two replicates
    # Case 2: data has more than two replicates

    # Loop through repArrList and center all arrays
    iterList = []
    for arr in repArrList:
        c_arr = st.centre(arr)
        tr_c_arr = np.transpose(c_arr)
        iterList.append(tr_c_arr)

    # Construct a list with all possible pairwise combinations arrays in repArrList
    combList = list(combinations(iterList, 2))
    combNameList = list(combinations(repList, 2))

    results = {}

    plot_data.fig = Figure(None)
    num = 1
    num_plots = len(combList)
    if num_plots > 1:
        num = 1
    num_edge = int(ceil(sqrt(num_plots)))


    # Now run RV2 computations for all possible pair-wise combinations
    for pairInd, pair in enumerate(combList):


        # *************** INFLUENCE REP att ***************
        if rvType == 'RV':
            coeffMat = st.RVcoeff(pair)
        elif rvType == 'RV2':
            coeffMat = st.RV2coeff(pair)

        refValue = round(coeffMat[0,1] * 100, 1)

        dropSampList = []
        sampValueList = []

        for ind in range(np.shape(pair[0])[0]):

            subList = []
            subM1 = np.delete(pair[0], ind, 0)
            subM2 = np.delete(pair[1], ind, 0)
            subList.append(subM1)
            subList.append(subM2)

            dropSampList.append(subList)

            if rvType == 'RV':
                subValue = st.RVcoeff(subList)[0,1]
            elif rvType == 'RV2':
                subValue = st.RV2coeff(subList)[0,1]

            sampValueList.append(round(subValue * 100, 1))

        results[combNameList[pairInd]] = [refValue, sampValueList]


        elements = actAttList
        titleString = 'REP att cross validation: Assessor ' + dbclkAss + \
            ' - rep ' + combNameList[pairInd][0] + \
            ' vs rep ' + combNameList[pairInd][1]
        plotTypeLabel = "Rep att"
        makeCvRepPlot(plot_data, [num_edge,num_edge,num], sampValueList, refValue, elements, pair, pairInd, titleString, dbclkAss, plotTypeLabel)
        num += 1


    return results



def makeCvAgrPlot(plot_data, num_subplot, sampValueList, refValue, elements, titleString, dbclkAss, plotTypeLabel):

    print "making perf ind cv plot..."

    print "---  STEP 1  ---"

    # Figure
    replot = True; subplot = True; scatter_width = 35
    if plot_data.fig != None: replot = True
    else: plot_data.fig = Figure(None)
    if subplot: # is subplot
        plot_data.ax = plot_data.fig.add_subplot(num_subplot[0], num_subplot[1], num_subplot[2])
        scatter_width = 15
    else: plot_data.ax = axes_create(plot_data.view_legend, plot_data.fig)
    ax = plot_data.ax; fig = plot_data.fig

    print "---  STEP 2  ---"


    #left = range(len(plot_data.activeSamplesList))
    left = range(len(sampValueList))
    xlimit = left[-1] + 2

    print "---  STEP 2.2  ---"
    print left
    print len(sampValueList)
    ax.bar(left, sampValueList, color='g')

    print "---  STEP 3  ---"


    font = {'fontname'   : 'Arial Narrow',
            'color'      : 'black',
            'fontweight' : 'normal',
            'fontsize'   : 10}

    print "---  STEP 4  ---"

    # Plot horizontal line indicating original index without leaving out
    # objects.
    plotValue = refValue
    ax.plot([-1,xlimit],[plotValue,plotValue], 'r--', label='all samples included')
    ax.set_xlim(0,xlimit-1)
    xticksStr = []
    xticks = []
    for tick in range(1,len(plot_data.activeAttributesList)+1):
        xticksStr.append(str(tick))
        xticks.append(tick-0.5)
    ax.set_xticks(xticks)
    ax.set_xticklabels(elements, font, rotation=0, ha='center')
    ax.set_ylabel(plotTypeLabel, font)
    ax.set_title(titleString, font)



def makeCvRepPlot(plot_data, num_subplot, sampValueList, refValue, elements, pair, pairInd, titleString, dbclkAss, plotTypeLabel):

    print "making perf ind cv plot..."



    # Figure
    replot = True; subplot = True; scatter_width = 35
    if plot_data.fig != None: replot = True
    else: plot_data.fig = Figure(None)
    if subplot: # is subplot
        plot_data.ax = plot_data.fig.add_subplot(num_subplot[0], num_subplot[1], num_subplot[2])
        scatter_width = 15
    else: plot_data.ax = axes_create(plot_data.view_legend, plot_data.fig)
    ax = plot_data.ax; fig = plot_data.fig




    left = range(np.shape(pair[0])[0])
    xlimit = left[-1] + 2
    ax.bar(left, sampValueList, color='g')

    font = {'fontname'   : 'Arial Narrow',
            'color'      : 'black',
            'fontweight' : 'normal',
            'fontsize'   : 10}

    # Plot horizontal line indicating original index without leaving out
    # objects.
    plotValue = refValue
    ax.plot([-1,xlimit],[plotValue,plotValue], 'r--', label='all samples included')
    ax.set_xlim(0,xlimit-1)
    xticksStr = []
    xticks = []
    for tick in range(1,np.shape(pair[0])[0]+1):
        xticksStr.append(str(tick))
        xticks.append(tick-0.5)
    ax.set_xticks(xticks)
    ax.set_xticklabels(elements, font, rotation=0, ha='center')
    ax.set_ylabel(plotTypeLabel, font)
    ax.set_title(titleString, font)

    print "********************************************"
    print
    print elements
    print

def makeCvRepPlot2(plot_data, num_subplot, sampValueList, refValue, elements, titleString, dbclkAss, plotTypeLabel):

    print "making perf ind cv plot..."



    # Figure
    replot = True; subplot = True; scatter_width = 35
    if plot_data.fig != None: replot = True
    else: plot_data.fig = Figure(None)
    if subplot: # is subplot
        plot_data.ax = plot_data.fig.add_subplot(num_subplot[0], num_subplot[1], num_subplot[2])
        scatter_width = 15
    else: plot_data.ax = axes_create(plot_data.view_legend, plot_data.fig)
    ax = plot_data.ax; fig = plot_data.fig




    left = range(np.shape(pair[0])[0])
    xlimit = left[-1] + 2
    ax.bar(left, sampValueList, color='g')

    font = {'fontname'   : 'Arial Narrow',
            'color'      : 'black',
            'fontweight' : 'normal',
            'fontsize'   : 10}

    # Plot horizontal line indicating original index without leaving out
    # objects.
    plotValue = refValue
    ax.plot([-1,xlimit],[plotValue,plotValue], 'r--', label='all samples included')
    ax.set_xlim(0,xlimit-1)
    xticksStr = []
    xticks = []
    for tick in range(1,np.shape(pair[0])[0]+1):
        xticksStr.append(str(tick))
        xticks.append(tick-0.5)
    ax.set_xticks(xticks)
    ax.set_xticklabels(elements, font, rotation=0, ha='center')
    ax.set_ylabel(plotTypeLabel, font)
    ax.set_title(titleString, font)



def combinations(iterable, r):
    # combinations('ABCD', 2) --> AB AC AD BC BD CD
    # combinations(range(4), 3) --> 012 013 023 123
    pool = tuple(iterable)
    n = len(pool)
    if r > n:
        return
    indices = range(r)
    yield tuple(pool[i] for i in indices)
    while True:
        for i in reversed(range(r)):
            if indices[i] != i + n - r:
                break
        else:
            return
        indices[i] += 1
        for j in range(i+1, r):
            indices[j] = indices[j-1] + 1
        yield tuple(pool[i] for i in indices)


def resultsTable(resultsDict):
    """
    This function puts all results from performanceIndices into an Excel file.
    """
    fileName = resultsDict['fileName']
    assessorList = resultsDict['assessorList']
    attributeList = resultsDict['attributeList']
    method = resultsDict['method']

    assObjRVcoeffList = resultsDict['AGR prod']
    assVarRVcoeffList = resultsDict['AGR att']
    AGRAver = resultsDict['AGR aver']
    assObjRVpValList = resultsDict['AGR prod pVal']
    assVarRVpValList = resultsDict['AGR att pVal']

    repObjRVcoeffList = resultsDict['REP prod']
    repVarRVcoeffList = resultsDict['REP att']
    REPAver = resultsDict['REP aver']
    repObjRVpValList = resultsDict['REP prod pVal']
    repVarRVpValList = resultsDict['REP att pVal']

    DISList = resultsDict['DIS']
    DISList2 = resultsDict['DIS2']
    DISInd = resultsDict['DIS count ind']
    DISPanel_ex1 = resultsDict['DIS count all_ex1']
    DISAllPanel = resultsDict['DIS sign all panel']

    """
    wb = xlwt.Workbook()
    sheetName = fileName[:-4]
    ws = wb.add_sheet(sheetName)

    font0 = xlwt.Font()
    font0.bold = True
    style0 = xlwt.XFStyle()
    style0.font = font0

    font1 = xlwt.Font()
    font1.colour_index = 4 # BLUE
    font1.bold = True
    style1 = xlwt.XFStyle()
    style1.font = font1

    # Write first row with assessor names
    ws.write(0,0,'Assessors',style0)

    for ind, ass in enumerate(assessorList):
        ws.write(0,ind+1,ass,style0)

    ws.write(0,ind+2,'PANEL',style1)
    ws.write(0,ind+3,'PANEL STD',style1)


    # Write row holding AGR indices for samples
    ws.write(1,0,'AGR products')

    for ind, ass in enumerate(assObjRVcoeffList):
        ws.write(1,ind+1,ass)

    AGRpanelAver_obj = np.average(np.array(assObjRVcoeffList))
    AGRpanelSTD_obj = np.std(np.array(assObjRVcoeffList), ddof=1)
    ws.write(1,ind+2,round(AGRpanelAver_obj,1),style1)
    ws.write(1,ind+3,round(AGRpanelSTD_obj,1),style1)


    # Write row holding AGR indices for attributes
    ws.write(2,0,'AGR attributes')

    for ind, ass in enumerate(assVarRVcoeffList):
        ws.write(2,ind+1,ass)

    AGRpanelAver_var = np.average(np.array(assVarRVcoeffList))
    AGRpanelSTD_var = np.std(np.array(assVarRVcoeffList), ddof=1)
    ws.write(2,ind+2,round(AGRpanelAver_var,1),style1)
    ws.write(2,ind+3,round(AGRpanelSTD_var,1),style1)


    # Write row holding average AGR indices
    ws.write(3,0,'AGR', style0)

    for ind, ass in enumerate(AGRAver):
        ws.write(3,ind+1,ass, style0)

    AGRpanelAver = np.average(np.array(AGRAver))
    AGRpanelSTD = np.std(np.array(AGRAver), ddof=1)
    ws.write(3,ind+2,round(AGRpanelAver,1),style1)
    ws.write(3,ind+3,round(AGRpanelSTD,1),style1)


    # Write row holding REP indices for samples
    ws.write(6,0,'REP samples')

    for ind, ass in enumerate(repObjRVcoeffList):
        ws.write(6,ind+1,ass)

    REPpanelAver_obj = np.average(np.array(repObjRVcoeffList))
    REPpanelSTD_obj = np.std(np.array(repObjRVcoeffList), ddof=1)
    ws.write(6,ind+2,round(REPpanelAver_obj,1),style1)
    ws.write(6,ind+3,round(REPpanelSTD_obj,1),style1)


    # Write row holding REP indices for attributes
    ws.write(7,0,'REP attributes')

    for ind, ass in enumerate(repVarRVcoeffList):
        ws.write(7,ind+1,ass)

    REPpanelAver_var = np.average(np.array(repVarRVcoeffList))
    REPpanelSTD_var = np.std(np.array(repVarRVcoeffList), ddof=1)
    ws.write(7,ind+2,round(REPpanelAver_var,1),style1)
    ws.write(7,ind+3,round(REPpanelSTD_var,1),style1)


    # Write row holding average AGR indices
    ws.write(8,0,'REP', style0)

    for ind, ass in enumerate(REPAver):
        ws.write(8,ind+1,ass, style0)

    REPpanelAver = np.average(np.array(REPAver))
    REPpanelSTD = np.std(np.array(REPAver), ddof=1)
    ws.write(8,ind+2,round(REPpanelAver,1),style1)
    ws.write(8,ind+3,round(REPpanelSTD,1),style1)


    # Write row holding number of significant attributes for each assessor
    ws.write(11,0,'# sign individ', style0)

    for ind, ass in enumerate(DISInd):
        ws.write(11,ind+1,ass)

    # Write number of significant attributes for whole panel
    ws.write(11,ind+2,round(DISAllPanel), style1)

    # Write total number of attributes in profiling
    #totalAtt = 'out of {0}'.format(len(attributeList)) # for Python 2.7
    totalAtt = 'out of %d' % (len(attributeList))
    ws.write(11, ind+3, totalAtt, style1)


    # Write row holding number of significant attributes panel, however
    # without the specific assessor
    ws.write(12,0,'# sign panel-1', style0)

    for ind, ass in enumerate(DISPanel_ex1):
        ws.write(12,ind+1,ass)


    # Write row holding DIS indices relative to panel without specific
    # assessor
    ws.write(13,0,'DIS rel panel', style0)

    for ind, ass in enumerate(DISList):
        ws.write(13,ind+1, ass, style0)
#
#    DISpanelAver = np.average(np.array(DISList))
#    DISpanelSTD = np.std(np.array(DISList), ddof=1)
#    ws.write(13,ind+2,round(DISpanelAver), style1)
#    ws.write(13,ind+3,round(DISpanelSTD,1),style1)


    # Write row holding DIS indices relative to total number of attributes
    ws.write(14,0,'DIS rel tot', style0)

    for ind, ass in enumerate(DISList2):
        ws.write(14,ind+1,ass, style0)

    DISpanelAver2 = np.average(np.array(DISList2))
    DISpanelSTD2 = np.std(np.array(DISList2), ddof=1)
    ws.write(14,ind+2,round(DISpanelAver2), style1)
    ws.write(14,ind+3,round(DISpanelSTD2,1),style1)


    # ------------------------------------------------------------------------
    # From here on permuted p values for the above AGR and REP indices will be
    # written.

    # Write first row with assessor names. Doing this again to make it look
    # more structured.
    ws.write(18,0,'Assessors',style0)

    for ind, ass in enumerate(assessorList):
        ws.write(18,ind+1,ass,style0)


    # Write row holding p values for AGR indices for samples
    ws.write(19,0,'AGR prod p')

    for ind, ass in enumerate(assObjRVpValList):
        ws.write(19,ind+1,ass[0])


    # Write row holding p values for AGR indices for attributes
    ws.write(20,0,'AGR att p')

    for ind, ass in enumerate(assVarRVpValList):
        ws.write(20,ind+1,ass[0])


    space = len(repObjRVpValList[0])
    print space
    # Write row holding p values for REP indices for samples
    ws.write(23,0,'REP prod p')

    for ind, ass in enumerate(repObjRVpValList):
        for combInd, combVal in enumerate(repObjRVpValList[ind]):
            ws.write(23+combInd,ind+1,combVal)

    nextPos = 23 + space
    # Write row holding p values for REP indices for attributes
    ws.write(nextPos,0,'REP att p')

    for ind, ass in enumerate(repVarRVpValList):
        for combInd, combVal in enumerate(repVarRVpValList[ind]):
            ws.write(nextPos+combInd,ind+1,combVal)



    resultFileName = sheetName + '_PI_' + method + '_NEW.xls'
    wb.save(resultFileName)
    """


def perfind_OverviewPlotter(s_data, plot_data, **kwargs):
    """
    Overview Plot
    """
    
    
    numberOfReplicates = len(s_data.ReplicateList)
    
    if numberOfReplicates == 1:
        rotation_list = []
        rotation_list.append(u'AGR prod')
        rotation_list.append(u'AGR att')

        tree_paths = []
        tree_paths.append([u'AGR prod'])
        tree_paths.append([u'AGR att'])
        plot_data.special_opts["recalc"] = False
        return OverviewPlotter(s_data, plot_data, tree_paths, perfindPlotter, rotation_list)    
        
    else:

        rotation_list = []
        rotation_list.append(u'AGR prod')
        rotation_list.append(u'AGR att')
        rotation_list.append(u'REP prod')
        rotation_list.append(u'REP att')
        rotation_list.append(u'DIS total')
        rotation_list.append(u'DIS panel-1')

        tree_paths = []
        tree_paths.append([u'AGR prod'])
        tree_paths.append([u'AGR att'])
        tree_paths.append([u'REP prod'])
        tree_paths.append([u'REP att'])
        tree_paths.append([u'DIS total'])
        tree_paths.append([u'DIS panel-1'])
        #rotation_list.append(u'DIS total')
        #rotation_list.append(u'DIS panel-1')
        #rotation_list.append(u'p values for AGR and REP')
        plot_data.special_opts["recalc"] = False
        return OverviewPlotter(s_data, plot_data, tree_paths, perfindPlotter, rotation_list)