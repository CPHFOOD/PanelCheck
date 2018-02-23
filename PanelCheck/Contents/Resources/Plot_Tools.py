#!/usr/bin/env python

"""
Plot tools module
"""
import wx, os, sys  
import codecs
import math, string # required python modules
import pandas as pd
from rpy2 import *
from rpy2.robjects import r, pandas2ri
import rpy2.robjects as ro
pandas2ri.activate()
#from types import *

import matplotlib
#matplotlib.use('WXAgg')
#for custom matplotlib drawing
from matplotlib.artist import Artist
from matplotlib.collections import LineCollection, PolyCollection
from matplotlib.cm import ScalarMappable
from matplotlib.colorbar import Colorbar
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.figure import Figure
from matplotlib.ticker import FixedLocator
from matplotlib.patches import Patch, Polygon, Rectangle, Circle, bbox_artist, draw_bbox
from matplotlib.lines import Line2D
#from matplotlib.font_manager import FontProperties
#from matplotlib.transforms import Bbox, Value, get_bbox_transform, bbox_all,\
#     unit_bbox, inverse_transform_bbox, lbwh_to_bbox
#for custom matplotlib drawing

"""
from numpy import array, arange, average, floor, ceil, sqrt, diag, dot, take, std, arange, hstack, vstack, \
     reshape, transpose, trace, mat, shape, zeros, pi, cos, sin
from sensorytools import STD, center
from scipy.stats import f_oneway, fprob
from scipy.linalg import svd
"""


from Progress_Info import Progress
from PlotData import *
from numpy import transpose
#from numpy import average

from Math_Tools import *


from copy import deepcopy, copy

def save_rdata_file(df, filename):
    r_data = ro.conversion.py2ri(transpose(df))
    ro.r.assign("my_df", r_data)
    ro.r("save(my_df, file='{}')".format(filename))
    os.chmod(filename, 0o777)

def data_frame(data):
    #data = pd.DataFrame(data)
#    print(data)
    r_dataframe = ro.conversion.py2ri(transpose(data))
#    save_rdata_file(data,'/Users/linder2411/Desktop/r_data.Rdata')
    return r_dataframe

# custom colormap
colormaps = {}
color_dict = {'red': ((0.0, 0.0, 0.0),
                 (0.5, 0.5, 0.5),
                 (1.0, 1.0, 1.0)),
       'green': ((0.0, 0.0, 0.0),
                 (0.5, 0.5, 0.5),
                 (1.0, 1.0, 1.0)),
        'blue': ((0.0, 0.0, 0.0),
                 (0.5, 0.5, 0.5),
                 (1.0, 1.0, 1.0))}


color_dict_green = {'red': ((0.0, 0.0, 0.0),
                 (0.5, 0.0, 0.0),
                 (1.0, 0.0, 0.0)),
       'green': ((0.0, 0.0, 0.0),
                 (0.5, 0.5, 0.5),
                 (1.0, 1.0, 1.0)),
        'blue': ((0.0, 0.0, 0.0),
                 (0.5, 0.0, 0.0),
                 (1.0, 0.0, 0.0))}

# manhattan night
color_dict2 = {'red': ((0.0, 0.0, 0.0),
                 (0.7, 0.0, 1.0),
                 (1.0, 1.0, 1.0)),
         'green': ((0.0, 0.0, 0.0),
                   (0.7, 0.0, 0.7),
                   (1.0, 1.0, 1.0)),
         'blue': ((0.0, 0.0, 0.0),
                  (0.7, 1.0, 0.0),
                  (1.0, 1.0, 1.0))}


# manhattan sunset
color_dict3 = {'red': ((0.0, 0.8, 0.8),
                 (0.7, 1.0, 0.0),
                 (1.0, 0.3, 0.3)),
         'green': ((0.0, 0.0, 0.0),
                   (0.7, 0.7, 0.0),
                   (1.0, 0.3, 0.3)),
         'blue': ((0.0, 0.0, 0.0),
                  (0.7, 0.0, 0.0),
                  (1.0, 0.3, 0.3))}


# Manhattan Colormap
colormaps['manhattan'] = LinearSegmentedColormap('manhattan', color_dict, 256)





# 14 colors:
colors_hex_list = ['#FF0000', '#00F600', '#1111FF', '#FFCC00', '#CF00F6', '#00F6CF',
          '#444444', '#999999',
          '#f27200', '#016f28','#840084' , '#0082a2']

# 14 colors:
colors_rgb_list = [(1, 0, 0), (0, 0.866667, 0), (0, 0, 1), (1, 0.8, 0), (0.8, 0, 0.933333), (0, 0.933333, 0.733333),
                   (0.4, 0.4, 0.4), (0.8, 0.8, 0.8),
                   (0.666667, 0.4, 0.4), (0.4, 0.666667, 0.4), (0.4, 0.4, 0.666667), (0.666667, 0.6, 0.4), (0.666667, 0.4, 0.6), (0.4, 0.666667, 0.6)]


def assign_colors(assessorList, replicateList):
    """
    Returns color dictionary
    Assigns same color for each assessor (for both active and non-active assessors).

    keys: (Assessor, Replicate)
    value: [color, shape]
    """

    # Symbols list, used in all plots
    all_colors = ['#FF0000', '#00F600', '#1111FF', '#FFCC00', '#CF00F6', '#00F6CF',
          '#444444', '#999999',
          '#f27200', '#016f28','#840084' , '#0082a2']
    #all_colors = [(0.75,0.0,0.0), (1.0,0.33,0.33), (0.66,0.66,0.0), (1.0,0.5,0.0), (0.33,0.75,0.0), (0.33,1.0,0.33), (0.33,0.66,0.66), (0.0,0.9,0.9), (0.33,0.5,0.75), (0.5,0.33,1.0), (0.66,0.0,0.66), (0.9,0.0,0.75)]
    """
          b  : blue
          g  : green
          r  : red
          c  : cyan
          m  : magenta
          y  : yellow
          k  : black
          w  : white
    """
    #all_colors = []
    #for r in range(0,10):
    #    for g in range(0, 10):
    #        for b in range(0, 10):
    #             color = (r*0.1, g*0.1, b*0.1)
    #             all_colors.append([color])
    shapes = ['o', 'd', 's', '^', '>', 'v', '<', 'p', 'h', '8']
    """
        's' : square
        'o' : circle
        '^' : triangle up
        '>' : triangle right
        'v' : triangle down
        '<' : triangle left
        'd' : diamond
        'p' : pentagram
        'h' : hexagon
        '8' : octagon
    """

    index = 0; i_max = len(all_colors); rep_max = len(shapes)

    colors = {}

    for ass in assessorList:
        rep_index = 0
        for rep in replicateList:
            colors[(ass,rep)] = [all_colors[index], shapes[rep_index]]
            rep_index += 1
            if rep_index >= rep_max: rep_index = 0
        index += 1
        if index >= i_max: index = 0


    return colors



def set_xlabeling(ax, x_string_list, font_size=13, x_positions=None):
    """
    Sets x-labels by given x_string_list onto ax
    """
    font = {'fontname'   : 'Arial Narrow',
        'color'      : 'black',
        'fontweight' : 'normal',
        'fontsize'   : font_size}

    amount = len(x_string_list)

    if x_positions == None or (len(x_positions) != len(x_string_list)):
        # arangement of lables for step=1.0

        x_range = ax.get_xlim()
        start_x = (x_range[1]-(amount))/2
        part = ((x_range[1]-2*start_x)/amount)
        spacer = part/2

        x_positions = []
        for i in range(0 , amount):
            x_positions.append(start_x + spacer + i*part)

    #print tickPositions
    locator = FixedLocator(x_positions)
    ax.xaxis.set_major_locator(locator)
    ax.set_xticklabels(x_string_list, font)



def set_ylabeling(ax, y_string_list, font_size=13):
    """
    Sets x-labels by given x_string_list onto ax
    """
    font = {'fontname'   : 'Arial Narrow',
        'color'      : 'black',
        'fontweight' : 'normal',
        'fontsize'   : font_size}

    amount = len(y_string_list)
    y_range = ax.get_ylim()
    start_y = (y_range[1]-amount)/2
    part = ((y_range[1]-2*start_y)/amount)
    spacer = part/2

    y_positions = []
    for i in range(0 , amount):
        y_positions.append(start_y + spacer + i*part)

    #print tickPositions
    locator = FixedLocator(y_positions)
    ax.yaxis.set_major_locator(locator)
    ax.set_yticklabels(y_string_list, font)



def set_xlabeling_rotation(ax, rotation, fontsize=10):
    """
    rotation: 'horizontal', 'vertical' or angle
    """
    fig = ax.figure
    bboxes = []
    for xtick_label in ax.get_xticklabels():
        xtick_label._rotation = rotation
        #bbox = xtick_label.get_window_extent()
        # the figure transform goes from relative coords->pixels and we
        # want the inverse of that
        #bboxi = bbox.inverse_transformed(fig.transFigure)
        #bboxes.append(bboxi)

    # this is the bbox that bounds all the bboxes, again in relative
    # figure coords
    #bbox = Bbox.union(bboxes)
    #if fig.subplotpars.bottom < bbox.height:
        # we need to move it over
        #fig.subplots_adjust(bottom=1.1*bbox.height) # pad a little

        #xtick_label._fontproperties.set_size(fontsize)

        # cut label:
        #print xtick_label.get_text()
        #if num_of_chars > 0 and num_of_chars < len(xtick_label._text):
        #    xtick_label.set_text(xtick_label.get_text()[0:num_of_chars] + "..")
        #    print xtick_label.get_text()


def set_axis_labelsize(ax, fontsize):
    for text_element in ax.get_xticklabels():
        text_element._fontproperties.set_size(fontsize)
    for text_element in ax.get_yticklabels():
        text_element._fontproperties.set_size(fontsize)


def axes_create(legend, fig, aspect='auto'):
    """
    Creates figure axes.

    @type legend: boolean
    @param legend: Whether legend is on or off.
    """
    ax = 0
    if(legend): #if legend to be drawn
        ax = fig.add_axes([0.1, 0.1, 0.65, 0.8], aspect=aspect) #[left, bottom, width, height]
    else:
        ax = fig.add_axes([0.1, 0.1, 0.8, 0.8], aspect=aspect) #[left, bottom, width, height]
    return ax



def axes_setup(ax, xLabel, yLabel, title, limits, font_size=13):
    """
    Sets up the axes.

    @type ax: object
    @param ax: Axes to be worked on.

    @type title: string
    @param title: Axes title.

    @type xLabel: string
    @param xLabel: Label name under the x-axes.

    @type yLabel: string
    @param yLabel: Label name left of the y-axes.

    @type limits: list
    @param limits: Limits for the axes. [x_min, x_max, y_min, y_max]
    """
    font = {'fontname'   : 'Arial Narrow',
            'color'      : 'black',
            'fontweight' : 'normal',
            'fontsize'   : font_size}


    # Settings for the labels in the plot
    ax.set_xlabel(xLabel, font)
    ax.set_ylabel(yLabel, font)
    ax.set_title(title, font)
    ax.set_xlim(limits[0], limits[1])
    ax.set_ylim(limits[2], limits[3])




def check_point(x, y, epsilon, pointAndLabelList, max):
    """
    If a plotting point is at the exact same point as another, it will be
    moved -epsilon on the x-axis. Returns the new x value.
    """
    for point in pointAndLabelList:
        if point[0] == x and point[1] == y:
            if point[3] < max:
                x = x - epsilon*point[3]
                point[3] += 1
                return x
    return x



def equal_lists(listA, listB):
    a = len(listA)
    b = len(listB)
    if a != b: return False

    for i in range(a):
        if listA[i] != listB[i]: return False
    return True



def show_err_msg(msg):
    dlg = wx.MessageDialog(None, msg, 'Error Message',
                       wx.OK | wx.ICON_INFORMATION)
    dlg.ShowModal()
    dlg.Destroy()



def show_info_msg(msg):
    dlg = wx.MessageDialog(None, msg, 'Important Information',
                       wx.OK | wx.ICON_INFORMATION)
    dlg.ShowModal()
    dlg.Destroy()



def show_msg(msg, title):
    dlg = wx.MessageDialog(None, msg, title,
                       wx.OK | wx.ICON_INFORMATION)
    dlg.ShowModal()
    dlg.Destroy()



############### general raw data ###############
def raw_data_grid(s_data, plot_data, active_assessors=None, active_attributes=None, active_samples=None, active_replicates=None):
    """
    Returns string array of raw data. For use in Grid.
    Raw data based on the active lists.
    """
    rawDataList = []
    emptyLine = ['']
    headerRawData = ['Raw Data']
    underline = ['========']


    if active_assessors == None:
        active_assessors = plot_data.activeAssessorsList
    if active_attributes == None:
        active_attributes = plot_data.activeAttributesList
    if active_samples == None:
        active_samples = plot_data.activeSamplesList
    if active_replicates == None:
        active_replicates = s_data.ReplicateList


    att_indices = []
    for att in active_attributes:
        # the same order as in self.SparseMatrix:
        att_indices.append(s_data.AttributeList.index(att))




    if s_data.has_mv:
        print "has missing values"
        line_ind = 0; missing_pos = []
        rawDataList.append(headerRawData)
        rawDataList.append(underline)
        rawDataList.append(emptyLine)
        line_ind += 4

        attributeLine = ['Assessor', 'Sample', 'Replicate']
        attributeLine.extend(plot_data.activeAttributesList)
        rawDataList.append(attributeLine)

        for assessor in active_assessors:

            for sample in active_samples:

                for replicate in active_replicates:

                    attributeValues = []
                    for att_ind in att_indices:
                        singleAttributeValue = s_data.SparseMatrix[(assessor, sample, replicate)][att_ind]
                        attributeValues.append(singleAttributeValue)

                    col_ind = 0
                    if (assessor, sample, replicate) in s_data.mv_pos:
                        for att_ind in att_indices:
                            if att_ind in s_data.mv_pos[(assessor, sample, replicate)]:
                                missing_pos.append((line_ind, col_ind+3))
                            col_ind += 1

                    dataLine = [assessor, sample, replicate]
                    dataLine.extend(attributeValues)
                    rawDataList.append(dataLine)
                    line_ind += 1
        plot_data.raw_data_mv_pos = missing_pos
        return rawDataList
    else:

        rawDataList.append(headerRawData)
        rawDataList.append(underline)
        rawDataList.append(emptyLine)

        attributeLine = ['Assessor', 'Sample', 'Replicate']
        attributeLine.extend(plot_data.activeAttributesList)
        rawDataList.append(attributeLine)

        for assessor in active_assessors:

            for sample in plot_data.activeSamplesList:

                for replicate in s_data.ReplicateList:

                    attributeValues = []
                    for attribute in plot_data.activeAttributesList:
                        singleAttributeValue = s_data.SparseMatrix[(assessor, sample, replicate)][s_data.AttributeList.index(attribute)]
                        attributeValues.append(singleAttributeValue)

                    dataLine = [assessor, sample, replicate]
                    dataLine.extend(attributeValues)
                    rawDataList.append(dataLine)
        return rawDataList



############### numerical data for ANOVA ###############
def numerical_data_grid(s_data, plot_data, ANOVA_F, ANOVA_p, ANOVA_MSE, F_signifcances):
    """
    Return list of numerical data
    """
    resultList = []
    emptyLine = ['']
    numericResultsHeader = ['ANOVA (one-way) results']
    underline = ['================']
    resultList.append(numericResultsHeader)
    resultList.append(underline)
    resultList.append(emptyLine)
    resultList.append(['F @ 1% significance level:', str(F_signifcances[0])])
    resultList.append(['F @ 5% significance level:', str(F_signifcances[1])])
    resultList.append(emptyLine)

    for ass_ind in range(len(plot_data.activeAssessorsList)):

        assessorLine = [plot_data.activeAssessorsList[ass_ind], '', '', '', '']
        headerLine = ['Nr.', 'Attribute', 'F value', 'p value', 'MSE value']
        resultList.append(assessorLine)
        resultList.append(headerLine)

        for att_ind in range(len(plot_data.activeAttributesList)):

            actual_att_ind = s_data.AttributeList.index(plot_data.activeAttributesList[att_ind])
            # Constructing the line that contains calculation-results
            valueLine = [actual_att_ind+1, plot_data.activeAttributesList[att_ind], num2str(ANOVA_F[ass_ind][att_ind], fmt="%.2f"), num2str(ANOVA_p[ass_ind][att_ind]), num2str(ANOVA_MSE[ass_ind][att_ind], fmt="%.2f")]
            resultList.append(valueLine)
        resultList.append(emptyLine)

    return resultList



############### numerical data part PCA scores ###############
def numerical_data_add_scores(scores_array, object_names, maxPCs, numeric_data=[], header_txt='PCA scores:'):

    headerLine = [header_txt]
    numeric_data.append(headerLine)

    (rows, cols) = scores_array.shape

    matrixHeaderLine = ['']
    for PC in range(maxPCs):
        matrixHeaderLine.append('PC ' + str(PC + 1))
    numeric_data.append(matrixHeaderLine)

    for obj_ind in range(rows):
        scoresRow = [object_names[obj_ind]]
        scores = []
        for PC in range(maxPCs):
            scores.append(num2str(scores_array[obj_ind, PC]))
        scoresRow.extend(scores)
        numeric_data.append(scoresRow)

    return numeric_data

############### numerical data part PCA loadings ###############
def numerical_data_add_loadings(loadings_array, variable_names, maxPCs, numeric_data=[], header_txt='PCA loadings:'):

    headerLine = [header_txt]
    numeric_data.append(headerLine)

    matrixHeaderLine = ['']
    matrixHeaderLine.extend(variable_names)
    numeric_data.append(matrixHeaderLine)

    (rows, cols) = loadings_array.shape

    for PC in range(maxPCs):
        loadingsRow = ['PC ' + str(PC + 1)]
        loadings = []
        for var_ind in range(cols):
            loadings.append(num2str(loadings_array[PC, var_ind]))
        loadingsRow.extend(loadings)
        numeric_data.append(loadingsRow)

    return numeric_data


############### numerical data single row ###############
def str_row(a, fmt="%.2f"):
    _list = []
    for x in a:
        _list.append(num2str(x, fmt=fmt))
    return _list

def num2str(x, fmt='%.3f'):
    if isinstance(x, (float, int)):
        return fmt % (x)
    else:
        return x


############### general test methods ###############

def check_columns(X):
    """
    Check that columns vectors do not have STD=0. For STD=0 the column/attribute vector must be removed
    for current analysis.
    """

    (rows, cols) = shape(X)
    out_cols = []
    in_cols = []

    for col_ind in range(cols):
        #print std(X[:, col_ind])

        if std(X[:, col_ind]) == 0:
            out_cols.append(col_ind)
        else:
            in_cols.append(col_ind)

    if len(out_cols) == 0:
        return X, []
    else:
        new_X = zeros((rows, len(in_cols)), float)
        new_col_ind = 0
        for col_ind in in_cols:
            new_X[:, new_col_ind] = X[:, col_ind]
            new_col_ind += 1

        return new_X, out_cols




############### R script (attribute significance) ###############

def attribute_significance(s_data, plot_data, one_rep=False):

    activeAssessorsList = plot_data.activeAssessorsList
    activeAttributesList = plot_data.activeAttributesList
    activeSamplesList = plot_data.activeSamplesList
    new_active_attributes_list = activeAttributesList

    matrix_num_lables = s_data.MatrixNumLables(assessors=activeAssessorsList, samples=activeSamplesList)
    matrix_selected_scores = s_data.MatrixDataSelected(assessors=activeAssessorsList, attributes=activeAttributesList, samples=activeSamplesList)


    matrix_selected_scores, out_cols = check_columns(matrix_selected_scores)
    if len(out_cols) > 0:
        msg = "For the selected samples the standard deviation\nover all assessors is 0 for the following attributes:\n"
        for col_ind in out_cols:
            msg += plot_data.activeAttributesList[col_ind] + "\n"

        msg += "\nThese attributes were left out of the analysis."


        new_active_attributes_indices = []
        new_active_attributes_list = []
        for att_ind in range(len(plot_data.activeAttributesList)):
            if att_ind not in out_cols:
                new_active_attributes_indices.append(att_ind)

        for att_ind in new_active_attributes_indices:
            new_active_attributes_list.append(plot_data.activeAttributesList[att_ind])

        matrix_selected_scores = s_data.MatrixDataSelected(assessors=activeAssessorsList, attributes=new_active_attributes_list, samples=activeSamplesList)

        #show_info_msg(msg)

        lables = [s_data.ass_index, s_data.samp_index, s_data.rep_index]
        for i in range(s_data.value_index, len(new_active_attributes_list)+s_data.value_index):
            lables.append(i)

        #return None
    else:
        lables = [s_data.ass_index, s_data.samp_index, s_data.rep_index]
        for i in range(s_data.value_index, len(activeAttributesList)+s_data.value_index):
            lables.append(i)


    if isinstance(plot_data, (CollectionCalcPlotData)):
        plot_data.collection_calc_data["accepted_active_attributes"] = new_active_attributes_list
    else:
        plot_data.accepted_active_attributes = new_active_attributes_list


    raw = hstack((matrix_num_lables, matrix_selected_scores))

    progress = Progress(None)
    progress.set_gauge(value=0, text="Using R...\n")
    # Cannot use unicode-strings, since it causes rpy to crash.
    # Need to convert unicode-strings to non-unicode strings



    # get program absolute-path:
    pathname = os.path.dirname(sys.argv[0])
    progPath = os.path.abspath(pathname).decode(sys.getfilesystemencoding())
    last_dir = os.getcwdu()
    os.chdir(progPath) # go to program path (for R script source)



    # Need to transpose the raw data matrix since rpy transposes when transferring
    # it to an R-data frame
    part = transpose(raw[:,:])

    # Constructing the data frame in R:
    # Switch to 'no conversion', such that everything that is created now
    # is an R object and NOT Python object (in this case 'frame' and 'names').
    # set_default_mode(NO_CONVERSION)
    names = r.get('names<-')
    
    frame = data_frame(part)
    frame = names(frame, lables)
    #r.print_(frame)


    # Switch back to basic conversion, so that variable res (see below) will be a
    # python list and NOT a R object
    # set_default_mode(BASIC_CONVERSION)


    # Now running Per's R-function to analyse the constructed data frame. All
    # calculation results are stored in python dictionary 'res'. The dictionary
    # contains the matrices 'Fmatr' (res[0]), 'Pmatr' (res[1]) and
    # 'LSDmatr' (res[2]).
    # Each of them has dimension:(8 rows) x (no. of attributes).

    # First initialise Per's function, then run it with our data-frame.
    if one_rep:
        script_source = 'source(\"R_scripts/sensmixedNoRepVer1.1.R\")'
        progress.set_gauge(value=7, text="Running R script...\n")
        r(script_source)
        res = r.sensmixedNoRep11(frame)
    else:
        script_source = 'source(\"R_scripts/sensmixedVer4.2.R\")'
        progress.set_gauge(value=7, text="Running R script...\n")
        r(script_source)
        res = r.sensmixedVer42(frame)


    os.chdir(last_dir) # go back
    progress.set_gauge(value=100, text="Done\n")
    progress.Destroy()
    if one_rep:
        return res[1].rx(1,True) # Product Effect p-matrix
    else:
        return res[2].rx(6,True) # Product Effect p-matrix




def colored_frame(s_data, plot_data, active_att_list, active_att):

    if len(s_data.ReplicateList) == 1:
        one_rep = True
    else:
        one_rep = False

    #try:
    if isinstance(plot_data, (CollectionCalcPlotData)):
        print("collection_calc")
        if not plot_data.collection_calc_data.has_key("p_matr"):
            plot_data.collection_calc_data["p_matr"] = attribute_significance(s_data, plot_data, one_rep=one_rep) # Product Effect p-matrix
        elif plot_data.collection_calc_data["p_matr"] == None:
            plot_data.collection_calc_data["p_matr"] = attribute_significance(s_data, plot_data, one_rep=one_rep) # Product Effect p-matrix
        else:
            pass #ok
        p_matr = plot_data.collection_calc_data["p_matr"]
    else:
        if not hasattr(plot_data, "p_matr"):
            plot_data.p_matr = attribute_significance(s_data, plot_data, one_rep=one_rep) # Product Effect p-matrix
        elif plot_data.p_matr == None:
            plot_data.p_matr = attribute_significance(s_data, plot_data, one_rep=one_rep) # Product Effect p-matrix
        else:
            pass #ok
        p_matr = plot_data.p_matr

    lsd_colors = {0.0:'#999999', 1.0:'#FFD800', 2.0:'#FF8A00', 3.0:'#E80B0B'}


    # if index list
    if isinstance(active_att_list[0], (int)):
        temp = []
        for ind in active_att_list:
            temp.append(s_data.AttributeList[ind])
        active_atts = temp
    else:
        active_atts = active_att_list

    if isinstance(plot_data, (CollectionCalcPlotData)):
        active_atts = plot_data.collection_calc_data["accepted_active_attributes"]
    elif isinstance(plot_data, (MM_ANOVA_PlotData)):
        active_atts = plot_data.accepted_active_attributes

    #print active_att
    #print plot_data.ax.get_legend_handles_labels()

    if p_matr == None:
        print "Cannot set frame color: STD=0 for one or more attributes"
        return False
    elif len(p_matr) != len(active_atts):
        print "Cannot set frame color: length of p list != length of active attributes list"
        return False

    if active_att not in active_atts:
        print "Cannot set frame color: active attribute index not valid"
        return False

    current_att_ind = active_atts.index(active_att)

    print current_att_ind


    # set frame coloring:
    #ax.set_axis_bgcolor(lsd_colors[p_matr[current_att_ind]])
    plot_data.ax.set_facecolor(lsd_colors[p_matr[current_att_ind]])

    #if plot_data.overview_plot:
    #    plot_data.ax.set_linewidth(3)
    #else:
    #    plot_data.ax.set_linewidth(3)

    return True
    #except: return


def significance_legend(plot_data, pos='upper right'):
    # colors:   grey       yellow     orange      red
    _colors = ['#999999', '#FFD800', '#FF8A00', '#E80B0B']
    if plot_data.view_legend:
        plotList = [None]
        lables = ['Prod. sign.\n(2-way ANOVA):','ns','p<0.05','p<0.01','p<0.001']
        i = 0
        for c in _colors:
            plotList.append(Line2D([],[], color = c, linewidth=5))
            i += 1

        figlegend = plot_data.fig.legend(plotList, lables, pos)





############### General Plot Methods ###############

def OverviewPlotter(s_data, plot_data, itemID_list, plotter, current_list, special_selection=0):
    """
    Overview Plot
    """
    print "Overview plot (general method)"
    #print special_selection

    plot_data.overview_plot = True

    font = {'fontname'   : 'Arial Narrow',
            'color'      : 'black',
            'fontweight' : 'normal',
            'fontsize'   : 9}

    num_plots = len(current_list)
    if num_plots == 0: show_err_msg('No plots to view. Check selections.'); return

    num_edge = int(ceil(sqrt(num_plots)))
    #print num_edge

    c_list = current_list[:]

    progress = Progress(None)
    progress.set_gauge(value=0, text="Calculating...\n")
    part = int(ceil(100/num_plots)); val = part

    plot_data.tree_path = itemID_list[0]
    plot_data = plotter(s_data, plot_data, num_subplot=[num_edge, num_edge, 1], selection=special_selection)

    print plot_data

    txt = c_list[0] + " done\n"
    progress.set_gauge(value=val, text=txt)

    del c_list[0]

    if plot_data == None:
        progress.Destroy()
        print "Error: no plot data"
        return # plotting failed

    fig = plot_data.fig # will have multiple axes objects
    ax = plot_data.ax
    print ax

    # text_element is matplotlib Text class
    for text_element in ax.get_xticklabels():
        text_element._fontproperties.set_size(9)
    for text_element in ax.get_yticklabels():
        text_element._fontproperties.set_size(9)
    #setp(ax.get_xticklabels(), fontsize=9)
    #setp(ax.get_yticklabels(), fontsize=9)
    num = 2
    for c_plot in c_list:
        plot_data.tree_path = itemID_list[num-1]
        plot_data = plotter(s_data, plot_data, num_subplot=[num_edge, num_edge, num], selection=special_selection)

        ax = plot_data.ax # pointer to last ax object added
        for text_element in ax.get_xticklabels():
            text_element._fontproperties.set_size(9)
        for text_element in ax.get_yticklabels():
            text_element._fontproperties.set_size(9)
        #setp(ax.get_xticklabels(), fontsize=9)
        #setp(ax.get_yticklabels(), fontsize=9)

        num += 1
        txt = c_plot + " done\n"
        val += part
        progress.set_gauge(value=val, text=txt)

    progress.Destroy()

    if plot_data.view_legend: r = 0.8 # has legend
    else: r = 0.95

    plot_data.fig.subplots_adjust(left=0.05, bottom=0.05, right=r, top=0.95, wspace=0.15, hspace=0.3)

    return plot_data
