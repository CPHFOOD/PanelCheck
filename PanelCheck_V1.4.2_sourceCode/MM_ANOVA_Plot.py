#!/usr/bin/env python

import os, sys # for Rpy i/o sources (for correct paths for the scripts)
from Plot_Tools import *
import pandas as pd
#import rpy2.rpy_classic as rpy
from rpy2.rpy_classic import *
from rpy2 import *
from rpy2.robjects import r, pandas2ri
import rpy2.robjects as ro
pandas2ri.activate()
from numpy import transpose,array,asarray

def load_mm_anova_data(s_data, plot_data, one_rep=False):

    activeAssessorsList = plot_data.activeAssessorsList
    activeAttributesList = plot_data.activeAttributesList
    plot_data.accepted_active_attributes = plot_data.activeAttributesList
    new_active_attributes_list = activeAttributesList
    activeSamplesList = plot_data.activeSamplesList
    itemID = plot_data.tree_path

    if plot_data.sensmixed_data == None:

        matrix_num_lables = s_data.MatrixNumLables(assessors=activeAssessorsList, samples=activeSamplesList)
        matrix_selected_scores = s_data.MatrixDataSelected(assessors=activeAssessorsList, attributes=activeAttributesList, samples=activeSamplesList)

        matrix_selected_scores, out_cols = check_columns(matrix_selected_scores)

        add_p_matr = True
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
            plot_data.accepted_active_attributes = new_active_attributes_list
            show_info_msg(msg) 
           

        lables = [s_data.ass_index, s_data.samp_index, s_data.rep_index]
        for i in range(s_data.value_index, len(new_active_attributes_list)-len(out_cols)+s_data.value_index):
            lables.append(i)

        _list = []
        for att_ind in range(len(new_active_attributes_list)):
                if att_ind not in out_cols:
                    _list.append(new_active_attributes_list[att_ind])
                    #plot_data.accepted_active_attributes = _list
                    #add_p_matr = False
                else:
                    lables = [s_data.ass_index, s_data.samp_index, s_data.rep_index]
                    for i in range(s_data.value_index, len(new_active_attributes_list)+s_data.value_index):
		            lables.append(i)
                    #plot_data.accepted_active_attributes = plot_data.activeAttributesList
        print matrix_num_lables


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
        part = raw[:,:]

		# Constructing the data frame in R:
		# Switch to 'no conversion', such that everything that is created now
		# is an R object and NOT Python object (in this case 'frame' and 'names').
        set_default_mode(NO_CONVERSION)
        names = r.get('names<-')

        frame = ro.conversion.py2ri(part)
        frame = names(frame, lables)
		#r.print_(frame)


		# Switch back to basic conversion, so that variable res (see below) will be a
		# python list and NOT a R object
        set_default_mode(BASIC_CONVERSION)


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
		    if add_p_matr:
		        plot_data.p_matr = res[2][6]
		    else:
		        plot_data.p_matr = None


        plot_data.sensmixed_data = res

	#print res

        os.chdir(last_dir) # go back
        progress.set_gauge(value=100, text="Done\n")
        progress.Destroy()
        return res

    else:
        return plot_data.sensmixed_data



def str_significance(values):
    str_values = []
    for value in values:
        if value == 0:
            str_values.append("ns")
        elif value == 1:
            str_values.append("p<0.05")
        elif value == 2:
            str_values.append("p<0.01")
        elif value == 3:
            str_values.append("p<0.001")
    return str_values






def get_grid_data(s_data, plot_data, f_mat, p_mat, lsd_mat, plot_type):
    """
    """
    activeAssessorsList = plot_data.activeAssessorsList
    activeAttributesList = plot_data.accepted_active_attributes
    activeSamplesList = plot_data.activeSamplesList
    itemID = plot_data.tree_path

    # colors:   grey       yellow     orange      red
    colors = ['#999999', '#FFD800', '#FF8A00', '#E80B0B']

    if plot_data.raw_data == []:
        raw_data = []; numeric_data = []
        newline = ['\n']
        numeric_data.append(newline)
        p_matr1 = []
        p_matr2 = []
        config = {}

        if plot_type == "3way":
            _types = ['Assessor Effect','Product Effect', 'Replicate Effect','Assessor*Product Interaction', 'Product*Replicate Interaction', 'Assessor*Replicate Interaction']
            p_matr1 = p_mat[7]
            p_matr2 = p_mat[9]
        elif plot_type == "2way":
            _types = ['Assessor Effect','Product Effect','Assessor*Product Interaction']
            p_matr1 = p_mat[4]
            p_matr2 = p_mat[5]
        elif plot_type == "2way1rep":
            _types = ['Assessor Effect','Product Effect']
            p_matr1 = p_mat[1]
            #p_matr2 = p_list[5]


        #lsd_types = ['LSD values', 'Bonferroni LSD values']


        # add header text
        numeric_data.append(['']); _index = 1
        numeric_data[_index].extend(activeAttributesList)
        numeric_data.append(newline); _index += 1


        # get active data
        m_data = s_data.GetActiveData(active_assessors=activeAssessorsList, active_samples=activeSamplesList, active_attributes=activeAttributesList)

        # calculate sample averages
        samples_averages = {}
        ass_att_matrix = zeros((len(activeAssessorsList), len(activeAttributesList)), float)
        samp_ind = 0
        for sample in activeSamplesList:
            ass_ind = 0
            for ass in activeAssessorsList:
                att_matrix = m_data[ass_ind, samp_ind, :]
                # average all replicates
                ass_att_matrix[ass_ind] = average(att_matrix, 0)
                ass_ind += 1

            # average all assessors
            sample_averages_matrix = average(ass_att_matrix, 0)
            temp = [sample]
            temp.extend(str_row(sample_averages_matrix, fmt="%.3f"))
            numeric_data.append(temp)
            _index += 1
            samp_ind += 1

        numeric_data.append(newline); _index += 1
        
        
        """
        numeric_data.append(["F prod"]); _index += 1
        numeric_data[_index].extend(str_row(f_mat[1]))

        row_ind = 1
        for p_val in p_matr1:
            key = (_index, row_ind)
            config[key] = {"back_color": colors[int(p_val)]}
            row_ind += 1
        """


        if plot_type == "2way1rep":
            numeric_data.append(newline); _index += 1
            for ind in range(len(f_mat)):
                        numeric_data.append([_types[ind] + " (F values)"]); _index += 1
    			numeric_data[_index].extend(str_row(f_mat[ind]))
    			#numeric_data.append(["p-values"]); _index += 1
    			#numeric_data[_index].extend(str_row(p_mat[ind], fmt="%.3f")) # p_matr2
    			numeric_data.append(newline); _index += 1
        else:
            #numeric_data.append(["F ass*prod interaction"]); _index += 1
            #numeric_data[_index].extend(str_row(f_mat[2]))
            #row_ind = 1
            #for p_val in p_matr2:
            #    key = (_index, row_ind)
            #    config[key] = {"back_color": colors[int(p_val)]}
            #    row_ind += 1

            #numeric_data.append(["F prod / F ass*prod interaction"]); _index += 1
            #temp = []
            #for ind in range(len(f_mat[1])):
            #    temp.append(num2str(f_mat[1][ind]/f_mat[2][ind]))
            #numeric_data[_index].extend(temp)
            #numeric_data.append(newline); _index += 1

            for ind in range(len(f_mat)):
    			numeric_data.append([_types[ind] + " (F values)"]); _index += 1
    			numeric_data[_index].extend(str_row(f_mat[ind]))
    			numeric_data.append(["p-values"]); _index += 1
    			numeric_data[_index].extend(str_row(p_mat[ind], fmt="%.3f")) # p_matr2
    			numeric_data.append(newline); _index += 1

        numeric_data.append(["LSD"]); _index += 1
        numeric_data[_index].extend(str_row(lsd_mat[0]))
        numeric_data.append(["Bonferroni LSD"]); _index += 1
        numeric_data[_index].extend(str_row(lsd_mat[1]))


        plot_data.numeric_data_config = config
        raw_data = raw_data_grid(s_data, plot_data)
        return raw_data, numeric_data
    else:
        return plot_data.raw_data, plot_data.numeric_data








def MixModel_ANOVA_Plotter_2way1rep(s_data, plot_data, num_subplot=[1,1,1], **kwargs):
	"""
	Mixed Modal ANOVA Plotter

        @type selection: int
        @param selection: Not used in this plotter


	@type s_data.SparseMatrix:     dictionary
	@param s_data.SparseMatrix:    Sparse matrix that contains 3-way data from assessors

	@type s_data.SampleList:       list
	@param s_data.SampleList:      Contains all samples from original data set

	@type s_data.ReplicateList:    list
	@param s_data.ReplicateList:   Contains all replicates original from data set

	@type s_data.AttributeList:    list
	@param s_data.AttributeList:   Contains all attributes original from data set

	@type selectedItem:     list
	@param selectedItem:    Conatins which item in the tree was double-clicked

	@type y_min:            integer
	@param y_min:           indicates the highest score value given in in data set

	ActiveSample_list: Is created from ActiveAssessors (dictionary) and is
	used for iterating through the active asessors
	ActiveSample_list: list
	"""
        activeAssessorsList = plot_data.activeAssessorsList
        activeAttributesList = plot_data.activeAttributesList
        activeSamplesList = plot_data.activeSamplesList
        itemID = plot_data.tree_path

        if len(activeAssessorsList) < 2: #no active assessors
            dlg = wx.MessageDialog(None, 'Two or more Assessors must be active.',
                               'Error Message',
                               wx.OK | wx.ICON_INFORMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return

        if len(s_data.ReplicateList) > 1: #no active assessors
            dlg = wx.MessageDialog(None, 'This data set contains more than one Replicate. Use 2- or 3-way ANOVA.',
                               'Error Message',
                               wx.OK | wx.ICON_INFORMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return

        if len(activeAttributesList) < 1: #no active assessors
            dlg = wx.MessageDialog(None, 'One or more Attributes must be active',
                               'Error Message',
                               wx.OK | wx.ICON_INFORMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        if len(activeSamplesList) < 2: #no active samples
            dlg = wx.MessageDialog(None, 'A minimum of two Samples must be active.',
                               'Error Message',
                               wx.OK | wx.ICON_INFORMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return


	res = load_mm_anova_data(s_data, plot_data, one_rep=True)



	activeAttributesList = plot_data.accepted_active_attributes


        # One of these types have been selected:
        _types = ['F1', 'F2', 'F3', 'F4']
        if itemID[0] == _types[0]: # REP*SAMP vs ERROR
            _title = "Assessor Effect"
            f_matr = res[0][0]
            p_matr = res[1][0]
            print 'First if statement yields f_matr as: {}'.format(f_matr)
        elif itemID[0] == _types[1]: # SAMP*ASS vs ERROR
            _title = "Product Effect"
            f_matr = res[0][1]
            p_matr = res[1][1]
            print 'Second if statement yields f_matr as: {}'.format(f_matr)
        else:
            return # error

        f_list = []
        f_list.append(res[0][0])
        f_list.append(res[0][1])

        p_list = []
        p_list.append(res[1][0])
        p_list.append(res[1][1])

        lsd_list = []
        lsd_list.append(res[2][0])
        lsd_list.append(res[2][1])

        # Figure
        replot = False; subplot = plot_data.overview_plot; scatter_width = 35
        if plot_data.fig != None: replot = True
        else: plot_data.fig = Figure(None)
        if subplot: # is subplot
            plot_data.ax = plot_data.fig.add_subplot(num_subplot[0], num_subplot[1], num_subplot[2])
            scatter_width = 15
        else: plot_data.ax = axes_create(plot_data.view_legend, plot_data.fig)
        ax = plot_data.ax; fig = plot_data.fig


        # colors:   grey       yellow     orange      red
        colors = ['#999999', '#FFD800', '#FF8A00', '#E80B0B']

        pointAndLabelList = []

        att_indices = arange(len(activeAttributesList))
        _width = 0.75
        i = 0
        for att in s_data.AttributeList:
            if att in activeAttributesList:
                ax.bar(att_indices[i]+(1-_width)+(_width/2), f_matr[i], _width, color=colors[int(p_matr[i])], edgecolor = "#000000", linewidth=0.75)
                pointAndLabelList.append([i+1, f_matr[i], att + ": " + str(f_matr[i]), att])
                i += 1

        y_max = max(f_matr) + max(f_matr)*0.1
        limits = [0, len(activeAttributesList)+1, 0, y_max]
        ax.grid(plot_data.view_grid)


	    #texts = figlegend.get_texts()
	    #texts[0]._fontproperties.set_size(14)

        if not subplot:
	    axes_setup(ax, 'Attributes', 'F value', _title, limits)
	    set_xlabeling(ax, activeAttributesList)
	    if len(activeAttributesList) > 9:
	        set_xlabeling_rotation(ax, 'vertical')
        else:
            axes_setup(ax, '', '', _title, limits, font_size=10)
            actives_cutted = activeAttributesList[:]
            if len(activeAttributesList) > 5: # cut labels
                for i in range(len(actives_cutted)): actives_cutted[i] = actives_cutted[i][0:5] + ".."
	    set_xlabeling(ax, actives_cutted)
	    if len(activeAttributesList) > 5:
	        set_xlabeling_rotation(ax, 'vertical')


        if plot_data.view_legend:
	    plotList = [None]
	    lables = ['SIGNIFICANCE:','ns','p<0.05','p<0.01','p<0.001']
	    i = 0
	    for c in colors:
	        #p = Patch(facecolor = c)
	        #p = Rectangle((0,0), 1, 1, facecolor = c)
	        #plotList.append(p)
	        plotList.append(Line2D([],[], color = c, linewidth=5))

	        i += 1
	    #CircleLegend(fig, [['#FF0000', '#00FF00', '#0000FF'], ['dommer1', 'dommer2', 'dommer3']])
	    figlegend = fig.legend(plotList, lables, 'upper right')


	#One element in the pointAndLabelList will always contain 3 items [x, y, label]

        rawDataList, resultList = get_grid_data(s_data, plot_data, f_list, p_list, lsd_list, "2way1rep")

        #update plot-data variables:
        plot_data.point_label_line_width = _width * 0.5
        plot_data.point_lables = pointAndLabelList
        plot_data.raw_data = rawDataList
        plot_data.numeric_data = resultList
        plot_data.plot_type = "mm_anova_f_2way1rep"
        plot_data.point_lables_type = 1


        #Frame draw, for standard Matplotlib frame only use show()
        return plot_data


def MixModel_ANOVA_LSD_Plotter_2way1rep(s_data, plot_data, num_subplot=[1,1,1], **kwargs):
	"""
	Mixed Modal ANOVA Plotter

        @type selection: int
        @param selection: Not used in this plotter


	@type s_data.SparseMatrix:     dictionary
	@param s_data.SparseMatrix:    Sparse matrix that contains 3-way data from assessors

	@type s_data.SampleList:       list
	@param s_data.SampleList:      Contains all samples from original data set

	@type s_data.ReplicateList:    list
	@param s_data.ReplicateList:   Contains all replicates original from data set

	@type s_data.AttributeList:    list
	@param s_data.AttributeList:   Contains all attributes original from data set

	@type selectedItem:     list
	@param selectedItem:    Conatins which item in the tree was double-clicked

	@type y_min:            integer
	@param y_min:           indicates the highest score value given in in data set

	ActiveSample_list: Is created from ActiveAssessors (dictionary) and is
	used for iterating through the active asessors
	ActiveSample_list: list
	"""
        activeAssessorsList = plot_data.activeAssessorsList
        activeAttributesList = plot_data.activeAttributesList
        activeSamplesList = plot_data.activeSamplesList
        itemID = plot_data.tree_path



        if len(activeAssessorsList) < 2: #no active assessors
            dlg = wx.MessageDialog(None, 'Two or more Assessors must be active.',
                               'Error Message',
                               wx.OK | wx.ICON_INFORMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        if len(s_data.ReplicateList) > 1: #no active assessors
            dlg = wx.MessageDialog(None, 'This data set contains more than one Replicate. Use 2- or 3-way ANOVA.',
                               'Error Message',
                               wx.OK | wx.ICON_INFORMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        if len(activeAttributesList) < 1: #no active assessors
            dlg = wx.MessageDialog(None, 'One or more Attributes must be active',
                               'Error Message',
                               wx.OK | wx.ICON_INFORMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        if len(activeSamplesList) < 2: #no active samples
            dlg = wx.MessageDialog(None, 'A minimum of two Samples must be active.',
                               'Error Message',
                               wx.OK | wx.ICON_INFORMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return



	res = load_mm_anova_data(s_data, plot_data, one_rep=True)

	activeAttributesList = plot_data.accepted_active_attributes


        # One of these types have been selected:
        lsd_types = ['LSD1', 'LSD2']
        lsd_types_names = ['Sample means & LSD', 'Sample means & Bonferroni LSD']
        if itemID[0] == lsd_types[0]:
            _title = lsd_types_names[0]
            lsd_matr = res[2][0]
        elif itemID[0] == lsd_types[1]:
            _title = lsd_types_names[1]
            lsd_matr = res[2][1]
        else:
            return # error


        f_list = []
        f_list.append(res[0][0])
        f_list.append(res[0][1])

        p_list = []
        p_list.append(res[1][0])
        p_list.append(res[1][1])

        lsd_list = []
        lsd_list.append(res[2][0])
        lsd_list.append(res[2][1])



        att_indices = arange(len(activeAttributesList))
        num_active_samps = len(activeSamplesList)

        averages_matrix = zeros((1, len(activeAttributesList)), float)
        for samp in activeSamplesList:
            samp_scores_matrix = []; stacking = 0
            for att in activeAttributesList:
                att_column = s_data.GetAttributeData(activeAssessorsList, att, samp)
                if stacking == 0: samp_scores_matrix = att_column; stacking = 1
                else: samp_scores_matrix = vstack((samp_scores_matrix, att_column))
            samp_scores_matrix = transpose(samp_scores_matrix)

            #print samp_scores_matrix
            averages_samp = average(samp_scores_matrix, 0) # average of the attributes for a given sample

            #print averages_samp
            averages_matrix = vstack((averages_matrix, averages_samp))
        averages_matrix = averages_matrix[1:,:]
        #averages_matrix = center(averages_matrix) # centered (between all active samples)
        #print averages_matrix


        colors = ['#FF0000', '#D3A400', '#009900', '#CC00EE', '#006CFF', '#00AD94',
		  '#666666', '#A4A4A4',
		  '#B7685D', '#BDAB65', '#6CB771', '#A0699F', '#6375B5', '#77A69F']


        # Figure
        replot = False; subplot = plot_data.overview_plot; scatter_width = 35
        if plot_data.fig != None: replot = True
        else: plot_data.fig = Figure(None)
        if subplot: # is subplot
            plot_data.ax = plot_data.fig.add_subplot(num_subplot[0], num_subplot[1], num_subplot[2])
            scatter_width = 15
        else: plot_data.ax = axes_create(plot_data.view_legend, plot_data.fig)
        ax = plot_data.ax; fig = plot_data.fig


        max_aver_list = []; min_aver_list = []
        for i in range(len(activeAttributesList)):
            max_aver_list.append(max(averages_matrix[:,i]))
            min_aver_list.append(min(averages_matrix[:,i]))

        plot_data.lsd_points = []
        for i in range(len(activeAttributesList)):
            plot_data.lsd_points.append([])

        #plot_data.lsd_ypoints = [[]] * len(activeAttributesList)
        vertices = []
        extra_space = 0; c_index = 0; pointAndLabelList = []
        for i in range(len(activeSamplesList)):
            x_samples = []; y_samples = []
            for j in range(len(activeAttributesList)):
                ax.text(j+0.25+extra_space, averages_matrix[i,j], str(i+1), fontsize=13, color=colors[c_index])

                #x_samples.append(j+0.225+extra_space); y_samples.append(averages_matrix[i,j])
                plot_data.lsd_points[j].append(ax.plot([j+0.225+extra_space], [averages_matrix[i,j]], 'k'))
                #plot_data.lsd_ypoints[j].append(averages_matrix[i,j])

                pt = ((j+0.225+extra_space, averages_matrix[i,j]))
                vertices.append(pt)

                _label = "Average (" + activeSamplesList[i] + ": " + activeAttributesList[j] + ")"
                pointAndLabelList.append([j+0.25+extra_space, averages_matrix[i,j], _label])
            #ax.scatter(x_samples, y_samples, s = 2, color="#999999")
            c_index += 1
            if c_index == len(colors): c_index = 0
            if extra_space == 0.5: extra_space = 0
            else: extra_space = 0.5


        #lc = LineCollection(vertices, colors='#000000')
        #plot_data.ax.add_collection(lc)



        vertices = []
        #print plot_data.lsd_points
        plot_data.lsd_lines = []
        lsd_colors = {0.0:'#999999', 1.0:'#FFD800', 2.0:'#FF8A00', 3.0:'#E80B0B'}
        for i in range(len(activeAttributesList)):
            max_aver = max_aver_list[i]
            lsd_color = lsd_colors[res[1][1][i]]
            plot_data.lsd_lines.append(ax.plot([i+0.5, i+0.5], [max_aver, max_aver-lsd_matr[i]], lsd_color, linewidth=3))

            pt = (i+0.5, i+0.5), (max_aver, max_aver-lsd_matr[i])
            vertices.append(pt)

            set_points_in_range(ax, [max_aver, max_aver-lsd_matr[i]], i+1, plot_data.lsd_points)


        #lc2 = LineCollection(vertices, colors='#FF0000', linewidths=3)
        #plot_data.ax.add_collection(lc2)

        upperlim = max(max_aver_list) + (max(max_aver_list)-min(min_aver_list))*0.1
        limits = [0, len(activeAttributesList), min(min_aver_list), upperlim]


        vertices = []
        for att_ind in att_indices:
            pt = ((att_ind, limits[2]), (att_ind, limits[3]))
            vertices.append(pt)

        lc3 = LineCollection(vertices, colors='#000000', linestyle='dashed')
        plot_data.ax.add_collection(lc3)
        #ax.vlines(att_indices, limits[2], limits[3], fmt='k--')


        ax.grid(plot_data.view_grid)
        if plot_data.view_legend:
	    c_i = 0; plotList = []
	    # labels = activeSamplesList[:]
	    labels = []; samp_nr = 1
	    for samp in activeSamplesList:
	        #p = Patch(facecolor = colors[c_i])
	        #plotList.append(p)

	        labels.append(str(samp_nr) + ": " + samp)
	        samp_nr += 1

	        plotList.append(Line2D([],[], color = colors[c_i], linewidth=5))
	        c_i += 1
	        if c_i == len(colors): c_i = 0

	    plotList.append(None); plotList.append(None); plotList.append(None)

	    #   colors:   grey       yellow     orange      red
            s_colors = ['#999999', '#FFD800', '#FF8A00', '#E80B0B']
	    labels.extend(['', '', 'SIGNIFICANCE:','ns','p<0.05','p<0.01','p<0.001'])
	    for c in s_colors:
	        #p = Patch(facecolor = c)
	        #plotList.append(p)

	        plotList.append(Line2D([],[], color = c, linewidth=5))

	        c_i += 1
	    #CircleLegend(fig, [['#FF0000', '#00FF00', '#0000FF'], ['dommer1', 'dommer2', 'dommer3']])
	    figlegend = fig.legend(plotList, labels, 'upper right')

	    #texts = figlegend.get_texts()
	    #texts[0]._fontproperties.set_size(14)

        if not subplot:
	    axes_setup(ax, 'Attributes', 'Score', _title, limits)
	    set_xlabeling(ax, activeAttributesList)
	    if len(activeAttributesList) > 11:
	        set_xlabeling_rotation(ax, 'vertical')
        else:
            axes_setup(ax, '', '', _title, limits, font_size=10)
            actives_cutted = activeAttributesList[:]
            if len(activeAttributesList) > 5: # cut labels
                for i in range(len(actives_cutted)): actives_cutted[i] = actives_cutted[i][0:6] + ".."
	    set_xlabeling(ax, actives_cutted)
	    if len(activeAttributesList) > 7:
	        set_xlabeling_rotation(ax, 'vertical')

	#One element in the pointAndLabelList will always contain 3 items [x, y, label]

        rawDataList, resultList = get_grid_data(s_data, plot_data, f_list, p_list, lsd_list, "2way1rep")

        #update plot-data variables:
        plot_data.point_lables = pointAndLabelList
        plot_data.raw_data = rawDataList
        plot_data.numeric_data = resultList
        plot_data.plot_type = "mm_anova_lsd_2way1rep"
        plot_data.point_lables_type = 0

        #Frame draw, for standard Matplotlib frame only use show()
        return plot_data



def MixModel_ANOVA_Plotter_2way(s_data, plot_data, num_subplot=[1,1,1], **kwargs):
	"""
	Mixed Modal ANOVA Plotter

        @type selection: int
        @param selection: Not used in this plotter


	@type s_data.SparseMatrix:     dictionary
	@param s_data.SparseMatrix:    Sparse matrix that contains 3-way data from assessors

	@type s_data.SampleList:       list
	@param s_data.SampleList:      Contains all samples from original data set

	@type s_data.ReplicateList:    list
	@param s_data.ReplicateList:   Contains all replicates original from data set

	@type s_data.AttributeList:    list
	@param s_data.AttributeList:   Contains all attributes original from data set

	@type selectedItem:     list
	@param selectedItem:    Conatins which item in the tree was double-clicked

	@type y_min:            integer
	@param y_min:           indicates the highest score value given in in data set

	ActiveSample_list: Is created from ActiveAssessors (dictionary) and is
	used for iterating through the active asessors
	ActiveSample_list: list
	"""
        activeAssessorsList = plot_data.activeAssessorsList
        activeAttributesList = plot_data.activeAttributesList
        activeSamplesList = plot_data.activeSamplesList
        itemID = plot_data.tree_path
        

        if len(activeAssessorsList) < 2: #no active assessors
            dlg = wx.MessageDialog(None, 'Two or more Assessors must be active.',
                               'Error Message',
                               wx.OK | wx.ICON_INFORMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        if len(s_data.ReplicateList) < 2: #no active assessors
            dlg = wx.MessageDialog(None, 'Cannot process: There must be a minimum of two Replicates per Sample in the data set',
                               'Error Message',
                               wx.OK | wx.ICON_INFORMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        if len(activeAttributesList) < 1: #no active assessors
            dlg = wx.MessageDialog(None, 'One or more Attributes must be active',
                               'Error Message',
                               wx.OK | wx.ICON_INFORMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        if len(activeSamplesList) < 2: #no active samples
            dlg = wx.MessageDialog(None, 'A minimum of two Samples must be active.',
                               'Error Message',
                               wx.OK | wx.ICON_INFORMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return


	res = load_mm_anova_data(s_data, plot_data)
	print('yes', asarray(array(res)), 'no')
        print type(res)
        if 'ListVector' in str(type(res)):
            print 'nice'
        else:
            res = load_mm_anova_data(s_data, plot_data)


	activeAttributesList = plot_data.accepted_active_attributes

        # 0 1 2
        # One of these types have been selected:
        _types = [u'F1', u'F2', u'F3']
        if itemID[0] == _types[0]: # REP*SAMP vs ERROR
            _title = "Assessor Effect"
            f_matr = res[0].rx(8,True) # 7
            p_matr = res[2].rx(8,True) # 7
            #print 'Third if statement yields f_matr as: {} with type: {} and res[0]: with type {} and values \n {}'.format(f_matr,type(f_matr),type(res[0]),res[0])
        elif itemID[0] == _types[2]: # SAMP*ASS vs ERROR
            _title = "Product Effect"
            f_matr = res[0].rx(7,True)
            p_matr = res[2].rx(7,True)
            print 'Fourth if statement yields f_matr as: {} and res[0] as: {}'.format(f_matr,res[0])
        elif itemID[0] == _types[1]: # SAMP vs SAMP*ASS
            _title = "Assessor*Product Interaction"
            f_matr = res[0].rx(9,True)
            p_matr = res[2].rx(9,True)
            print 'Fifth if statement yields f_matr as: {} \n'.format(f_matr,res[0])
        else:
            return # error


        f_list = []
        f_list.append(res[0].rx(8,True))
        f_list.append(res[0].rx(7,True))
        f_list.append(res[0].rx(9,True))

        p_list = [] # 7,6,8
        p_list.append(res[1].rx(8,True))
        p_list.append(res[1].rx(7,True))
        p_list.append(res[1].rx(9,True))

        # p_matr2
        p_list.append(res[2].rx(8,True))
        p_list.append(res[2].rx(7,True))
        p_list.append(res[2].rx(9,True))

        lsd_list = []
        lsd_list.append(res[3].rx(2,True))
        lsd_list.append(res[3].rx(3,True))

        # Figure
        replot = False; subplot = plot_data.overview_plot; scatter_width = 35
        if plot_data.fig != None: replot = True
        else: plot_data.fig = Figure(None)
        if subplot: # is subplot
            plot_data.ax = plot_data.fig.add_subplot(num_subplot[0], num_subplot[1], num_subplot[2])
            scatter_width = 15
        else: plot_data.ax = axes_create(plot_data.view_legend, plot_data.fig)
        ax = plot_data.ax; fig = plot_data.fig


        # colors:   grey       yellow     orange      red
        colors = ['#999999', '#FFD800', '#FF8A00', '#E80B0B']

        pointAndLabelList = []

        att_indices = arange(len(activeAttributesList))
        _width = 0.75
        
        if isinstance(f_matr,float):
            y_max = f_matr + f_matr*0.1
            limits = [0, len(activeAttributesList)+1, 0, y_max]
        else:
            i = 0
            for att in s_data.AttributeList:
                if att in activeAttributesList:
                    print "Index: {} and atrribute: {}".format(i,att)
                    ax.bar(att_indices[i]+(1-_width)+(_width/2), f_matr[i], _width, color=colors[int(p_matr[i])], edgecolor = "#000000", linewidth=0.75)
                    pointAndLabelList.append([i+1, f_matr[i], att + ": " + str(f_matr[i]), att])
                    i += 1
            y_max = max(f_matr) + max(f_matr)*0.1
            limits = [0, len(activeAttributesList)+1, 0, y_max]

        ax.grid(plot_data.view_grid)


	    #texts = figlegend.get_texts()
	    #texts[0]._fontproperties.set_size(14)

        if not subplot:
	    axes_setup(ax, 'Attributes', 'F value', _title, limits)
	    set_xlabeling(ax, activeAttributesList)
	    if len(activeAttributesList) > 9:
	        set_xlabeling_rotation(ax, 'vertical')
        else:
            axes_setup(ax, '', '', _title, limits, font_size=10)
            actives_cutted = activeAttributesList[:]
            if len(activeAttributesList) > 5: # cut labels
                for i in range(len(actives_cutted)): actives_cutted[i] = actives_cutted[i][0:5] + ".."
	    set_xlabeling(ax, actives_cutted)
	    if len(activeAttributesList) > 5:
	        set_xlabeling_rotation(ax, 'vertical')


        if plot_data.view_legend:
	    plotList = [None]
	    lables = ['SIGNIFICANCE:','ns','p<0.05','p<0.01','p<0.001']
	    i = 0
	    for c in colors:
	        #p = Patch(facecolor = c)
	        #p = Rectangle((0,0), 1, 1, facecolor = c)
	        #plotList.append(p)
	        plotList.append(Line2D([],[], color = c, linewidth=5))

	        i += 1
	    #CircleLegend(fig, [['#FF0000', '#00FF00', '#0000FF'], ['dommer1', 'dommer2', 'dommer3']])
	    figlegend = fig.legend(plotList, lables, 'upper right')


	#One element in the pointAndLabelList will always contain 3 items [x, y, label]

        rawDataList, resultList = get_grid_data(s_data, plot_data, f_list, p_list, lsd_list, "2way")

        #update plot-data variables:
        plot_data.point_label_line_width = _width * 0.5
        plot_data.point_lables = pointAndLabelList
        plot_data.raw_data = rawDataList
        plot_data.numeric_data = resultList
        plot_data.plot_type = "mm_anova_f_2way"
        plot_data.point_lables_type = 1

        #Frame draw, for standard Matplotlib frame only use show()
        return plot_data


def MixModel_ANOVA_LSD_Plotter_2way(s_data, plot_data, num_subplot=[1,1,1], **kwargs):
	"""
	Mixed Modal ANOVA Plotter

        @type selection: int
        @param selection: Not used in this plotter


	@type s_data.SparseMatrix:     dictionary
	@param s_data.SparseMatrix:    Sparse matrix that contains 3-way data from assessors

	@type s_data.SampleList:       list
	@param s_data.SampleList:      Contains all samples from original data set

	@type s_data.ReplicateList:    list
	@param s_data.ReplicateList:   Contains all replicates original from data set

	@type s_data.AttributeList:    list
	@param s_data.AttributeList:   Contains all attributes original from data set

	@type selectedItem:     list
	@param selectedItem:    Conatins which item in the tree was double-clicked

	@type y_min:            integer
	@param y_min:           indicates the highest score value given in in data set

	ActiveSample_list: Is created from ActiveAssessors (dictionary) and is
	used for iterating through the active asessors
	ActiveSample_list: list
	"""
        activeAssessorsList = plot_data.activeAssessorsList
        activeAttributesList = plot_data.activeAttributesList
        activeSamplesList = plot_data.activeSamplesList
        itemID = plot_data.tree_path



        if len(activeAssessorsList) < 2: #no active assessors
            dlg = wx.MessageDialog(None, 'Two or more Assessors must be active.',
                               'Error Message',
                               wx.OK | wx.ICON_INFORMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        if len(s_data.ReplicateList) < 2: #no active assessors
            dlg = wx.MessageDialog(None, 'Cannot process: There must be a minimum of two Replicates per Sample in the data set',
                               'Error Message',
                               wx.OK | wx.ICON_INFORMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        if len(activeAttributesList) < 1: #no active assessors
            dlg = wx.MessageDialog(None, 'One or more Attributes must be active',
                               'Error Message',
                               wx.OK | wx.ICON_INFORMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        if len(activeSamplesList) < 2: #no active samples
            dlg = wx.MessageDialog(None, 'A minimum of two Samples must be active.',
                               'Error Message',
                               wx.OK | wx.ICON_INFORMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return



	res = load_mm_anova_data(s_data, plot_data)

	activeAttributesList = plot_data.accepted_active_attributes


        # One of these types have been selected:
        lsd_types = ['LSD1', 'LSD2']
        lsd_types_names = ['Sample means & LSD', 'Sample means & Bonferroni LSD']
        if itemID[0] == lsd_types[0]:
            _title = lsd_types_names[0]
            lsd_matr = res[3].rx(2,True)
        elif itemID[0] == lsd_types[1]:
            _title = lsd_types_names[1]
            lsd_matr = res[3].rx(3,True)
        else:
            return # error

        f_list = []
        f_list.append(res[0].rx(8,True))
        f_list.append(res[0].rx(7,True))
        f_list.append(res[0].rx(9,True))

        p_list = []
        p_list.append(res[1].rx(8,True))
        p_list.append(res[1].rx(7,True))
        p_list.append(res[1].rx(9,True))

        # p_matr2
        p_list.append(res[2].rx(8,True))
        p_list.append(res[2].rx(7,True))
        p_list.append(res[2].rx(9,True))

        lsd_list = []
        lsd_list.append(res[3].rx(3,True))
        lsd_list.append(res[3].rx(2,True))


        att_indices = arange(len(activeAttributesList))
        num_active_samps = len(activeSamplesList)

        averages_matrix = zeros((1, len(activeAttributesList)), float)
        for samp in activeSamplesList:
            samp_scores_matrix = []; stacking = 0
            for att in activeAttributesList:
                att_column = s_data.GetAttributeData(activeAssessorsList, att, samp)
                if stacking == 0: samp_scores_matrix = att_column; stacking = 1
                else: samp_scores_matrix = vstack((samp_scores_matrix, att_column))
            samp_scores_matrix = transpose(samp_scores_matrix)

            #print samp_scores_matrix
            averages_samp = average(samp_scores_matrix, 0) # average of the attributes for a given sample

            #print averages_samp
            averages_matrix = vstack((averages_matrix, averages_samp))
        averages_matrix = averages_matrix[1:,:]
        #averages_matrix = center(averages_matrix) # centered (between all active samples)
        #print averages_matrix


        colors = ['#FF0000', '#D3A400', '#009900', '#CC00EE', '#006CFF', '#00AD94',
		  '#666666', '#A4A4A4',
		  '#B7685D', '#BDAB65', '#6CB771', '#A0699F', '#6375B5', '#77A69F']


        # Figure
        replot = False; subplot = plot_data.overview_plot; scatter_width = 35
        if plot_data.fig != None: replot = True
        else: plot_data.fig = Figure(None)
        if subplot: # is subplot
            plot_data.ax = plot_data.fig.add_subplot(num_subplot[0], num_subplot[1], num_subplot[2])
            scatter_width = 15
        else: plot_data.ax = axes_create(plot_data.view_legend, plot_data.fig)
        ax = plot_data.ax; fig = plot_data.fig


        max_aver_list = []; min_aver_list = []
        for i in range(len(activeAttributesList)):
            max_aver_list.append(max(averages_matrix[:,i]))
            min_aver_list.append(min(averages_matrix[:,i]))

        plot_data.lsd_points = []
        for i in range(len(activeAttributesList)):
            plot_data.lsd_points.append([])

        #plot_data.lsd_ypoints = [[]] * len(activeAttributesList)
        vertices = []
        extra_space = 0; c_index = 0; pointAndLabelList = []
        for i in range(len(activeSamplesList)):
            x_samples = []; y_samples = []
            for j in range(len(activeAttributesList)):
                ax.text(j+0.25+extra_space, averages_matrix[i,j], str(i+1), fontsize=13, color=colors[c_index])

                #x_samples.append(j+0.225+extra_space); y_samples.append(averages_matrix[i,j])
                plot_data.lsd_points[j].append(ax.plot([j+0.225+extra_space], [averages_matrix[i,j]], 'k'))
                #plot_data.lsd_ypoints[j].append(averages_matrix[i,j])

                pt = ((j+0.225+extra_space, averages_matrix[i,j]))
                vertices.append(pt)

                _label = "Average (" + activeSamplesList[i] + ": " + activeAttributesList[j] + ")"
                pointAndLabelList.append([j+0.25+extra_space, averages_matrix[i,j], _label])
            #ax.scatter(x_samples, y_samples, s = 2, color="#999999")
            c_index += 1
            if c_index == len(colors): c_index = 0
            if extra_space == 0.5: extra_space = 0
            else: extra_space = 0.5


        #lc = LineCollection(vertices, colors='#000000')
        #plot_data.ax.add_collection(lc)



        vertices = []
        #print plot_data.lsd_points
        plot_data.lsd_lines = []
        lsd_colors = {0.0:'#999999', 1.0:'#FFD800', 2.0:'#FF8A00', 3.0:'#E80B0B'}
        for i in range(len(activeAttributesList)):
            max_aver = max_aver_list[i]
            lsd_color = lsd_colors[res[2].rx(6,True)[i]]
            plot_data.lsd_lines.append(ax.plot([i+0.5, i+0.5], [max_aver, max_aver-lsd_matr[i]], lsd_color, linewidth=3))

            pt = (i+0.5, i+0.5), (max_aver, max_aver-lsd_matr[i])
            vertices.append(pt)

            set_points_in_range(ax, [max_aver, max_aver-lsd_matr[i]], i+1, plot_data.lsd_points)


        #lc2 = LineCollection(vertices, colors='#FF0000', linewidths=3)
        #plot_data.ax.add_collection(lc2)

        upperlim = max(max_aver_list) + (max(max_aver_list)-min(min_aver_list))*0.1
        limits = [0, len(activeAttributesList), min(min_aver_list), upperlim]


        vertices = []
        for att_ind in att_indices:
            pt = ((att_ind, limits[2]), (att_ind, limits[3]))
            vertices.append(pt)

        lc3 = LineCollection(vertices, colors='#000000', linestyle='dashed')
        plot_data.ax.add_collection(lc3)
        #ax.vlines(att_indices, limits[2], limits[3], fmt='k--')


        ax.grid(plot_data.view_grid)
        if plot_data.view_legend:
	    c_i = 0; plotList = []
	    # labels = activeSamplesList[:]
	    labels = []; samp_nr = 1
	    for samp in activeSamplesList:
	        #p = Patch(facecolor = colors[c_i])
	        #plotList.append(p)

	        labels.append(str(samp_nr) + ": " + samp)
	        samp_nr += 1

	        plotList.append(Line2D([],[], color = colors[c_i], linewidth=5))
	        c_i += 1
	        if c_i == len(colors): c_i = 0

	    plotList.append(None); plotList.append(None); plotList.append(None)

	    #   colors:   grey       yellow     orange      red
            s_colors = ['#999999', '#FFD800', '#FF8A00', '#E80B0B']
	    labels.extend(['', '', 'SIGNIFICANCE:','ns','p<0.05','p<0.01','p<0.001'])
	    for c in s_colors:
	        #p = Patch(facecolor = c)
	        #plotList.append(p)

	        plotList.append(Line2D([],[], color = c, linewidth=5))

	        c_i += 1
	    #CircleLegend(fig, [['#FF0000', '#00FF00', '#0000FF'], ['dommer1', 'dommer2', 'dommer3']])
	    figlegend = fig.legend(plotList, labels, 'upper right')

	    #texts = figlegend.get_texts()
	    #texts[0]._fontproperties.set_size(14)

        if not subplot:
	    axes_setup(ax, 'Attributes', 'Score', _title, limits)
	    set_xlabeling(ax, activeAttributesList)
	    if len(activeAttributesList) > 11:
	        set_xlabeling_rotation(ax, 'vertical')
        else:
            axes_setup(ax, '', '', _title, limits, font_size=10)
            actives_cutted = activeAttributesList[:]
            if len(activeAttributesList) > 5: # cut labels
                for i in range(len(actives_cutted)): actives_cutted[i] = actives_cutted[i][0:6] + ".."
	    set_xlabeling(ax, actives_cutted)
	    if len(activeAttributesList) > 7:
	        set_xlabeling_rotation(ax, 'vertical')

	#One element in the pointAndLabelList will always contain 3 items [x, y, label]

        rawDataList, resultList = get_grid_data(s_data, plot_data, f_list, p_list, lsd_list, "2way")

        #update plot-data variables:
        plot_data.point_lables = pointAndLabelList
        plot_data.raw_data = rawDataList
        plot_data.numeric_data = resultList
        plot_data.plot_type = "mm_anova_lsd_2way"
        plot_data.point_lables_type = 0
        plot_data.p_matr = res[2][6] # for profile plot

        #Frame draw, for standard Matplotlib frame only use show()
        return plot_data









def MixModel_ANOVA_Plotter_3way(s_data, plot_data, num_subplot=[1,1,1], **kwargs):
	"""
	Mixed Modal ANOVA Plotter

        @type selection: int
        @param selection: Not used in this plotter


	@type s_data.SparseMatrix:     dictionary
	@param s_data.SparseMatrix:    Sparse matrix that contains 3-way data from assessors

	@type s_data.SampleList:       list
	@param s_data.SampleList:      Contains all samples from original data set

	@type s_data.ReplicateList:    list
	@param s_data.ReplicateList:   Contains all replicates original from data set

	@type s_data.AttributeList:    list
	@param s_data.AttributeList:   Contains all attributes original from data set

	@type selectedItem:     list
	@param selectedItem:    Conatins which item in the tree was double-clicked

	@type y_min:            integer
	@param y_min:           indicates the highest score value given in in data set

	ActiveSample_list: Is created from ActiveAssessors (dictionary) and is
	used for iterating through the active asessors
	ActiveSample_list: list
	"""
        activeAssessorsList = plot_data.activeAssessorsList
        activeAttributesList = plot_data.activeAttributesList
        activeSamplesList = plot_data.activeSamplesList
        itemID = plot_data.tree_path

        if len(activeAssessorsList) < 2: #no active assessors
            dlg = wx.MessageDialog(None, 'Two or more Assessors must be active.',
                               'Error Message',
                               wx.OK | wx.ICON_INFORMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        if len(s_data.ReplicateList) < 2: #no active assessors
            dlg = wx.MessageDialog(None, 'Cannot process: There must be a minimum of two Replicates per Sample in the data set',
                               'Error Message',
                               wx.OK | wx.ICON_INFORMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        if len(activeAttributesList) < 1: #no active assessors
            dlg = wx.MessageDialog(None, 'One or more Attributes must be active',
                               'Error Message',
                               wx.OK | wx.ICON_INFORMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        if len(activeSamplesList) < 2: #no active samples
            dlg = wx.MessageDialog(None, 'A minimum of two Samples must be active.',
                               'Error Message',
                               wx.OK | wx.ICON_INFORMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return


	res = load_mm_anova_data(s_data, plot_data)


	activeAttributesList = plot_data.accepted_active_attributes


        # One of these types have been selected:
        _types = ['F1', 'F2', 'F2b', 'F3', 'F4', 'F5']
        print res 
        if itemID[0] == _types[0]: # REP*SAMP vs ERROR
            _title = "Assessor Effect"
            f_matr = res[0].rx(1,True)
            p_matr = res[2].rx(1,True)
        elif itemID[0] == _types[1]: # SAMP*ASS vs ERROR
            _title = "Product Effect"
            f_matr = res[0].rx(2,True)
            p_matr = res[2].rx(2,True)
        elif itemID[0] == _types[2]:
            _title = "Replicate Effect"
            f_matr = res[0].rx(3,True)
            p_matr = res[2].rx(3,True)
        elif itemID[0] == _types[3]: # SAMP vs SAMP*ASS
            _title = "Assessor*Product Interaction"
            f_matr = res[0].rx(4,True)
            p_matr = res[2].rx(4,True)
        elif itemID[0] == _types[4]: # SAMP in 3-way mixed model
            _title = "Product*Replicate Interaction"
            f_matr = res[0].rx(6,True)
            p_matr = res[2].rx(6,True)
        elif itemID[0] == _types[5]:
            _title = "Assessor*Replicate Interaction"
            f_matr = res[0].rx(5,True)
            p_matr = res[2].rx(5,True)
        else:
            print "Error: wrong tree path id"
            return # error

        f_list = []
        f_list.append(res[0].rx(1,True))
        f_list.append(res[0].rx(2,True))
        f_list.append(res[0].rx(3,True))
        f_list.append(res[0].rx(4,True))
        f_list.append(res[0].rx(6,True))
        f_list.append(res[0].rx(5,True))


        p_list = []
        p_list.append(res[1].rx(1,True))
        p_list.append(res[1].rx(2,True))
        p_list.append(res[1].rx(3,True))
        p_list.append(res[1].rx(4,True))
        p_list.append(res[1].rx(6,True))
        p_list.append(res[1].rx(5,True))


        # p_matr2
        p_list.append(res[2].rx(1,True))
        p_list.append(res[2].rx(2,True))
        p_list.append(res[2].rx(3,True))
        p_list.append(res[2].rx(4,True))
        p_list.append(res[2].rx(6,True))
        p_list.append(res[2].rx(5,True))


        lsd_list = []
        lsd_list.append(res[3].rx(1,True))
        lsd_list.append(res[3].rx(2,True))


        # Figure
        replot = False; subplot = plot_data.overview_plot; scatter_width = 35
        if plot_data.fig != None: replot = True
        else: plot_data.fig = Figure(None)
        if subplot: # is subplot
            plot_data.ax = plot_data.fig.add_subplot(num_subplot[0], num_subplot[1], num_subplot[2])
            scatter_width = 15
        else: plot_data.ax = axes_create(plot_data.view_legend, plot_data.fig)
        ax = plot_data.ax; fig = plot_data.fig


        # colors:   grey       yellow     orange      red
        colors = ['#999999', '#FFD800', '#FF8A00', '#E80B0B']

        pointAndLabelList = []

        att_indices = arange(len(activeAttributesList))
        _width = 0.75
        j = 0
        for att in s_data.AttributeList:
            if att in activeAttributesList:
                print j
                j += 1

        print f_matr
        print len(p_matr)

        i = 0
        for att in s_data.AttributeList:
            if att in activeAttributesList:
                ax.bar(att_indices[i]+(1-_width)+(_width/2), f_matr[i], _width, color=colors[int(p_matr[i])], edgecolor = "#000000", linewidth=0.75)
                pointAndLabelList.append([i+1, f_matr[i], att + ": " + str(f_matr[i]), att])
                i += 1

        y_max = max(f_matr) + max(f_matr)*0.1
        limits = [0, len(activeAttributesList)+1, 0, y_max]
        ax.grid(plot_data.view_grid)


	    #texts = figlegend.get_texts()
	    #texts[0]._fontproperties.set_size(14)

        if not subplot:
	    axes_setup(ax, 'Attributes', 'F value', _title, limits)
	    set_xlabeling(ax, activeAttributesList)
	    if len(activeAttributesList) > 9:
	        set_xlabeling_rotation(ax, 'vertical')
        else:
            axes_setup(ax, '', '', _title, limits, font_size=10)
            actives_cutted = activeAttributesList[:]
            if len(activeAttributesList) > 5: # cut labels
                for i in range(len(actives_cutted)): actives_cutted[i] = actives_cutted[i][0:5] + ".."
	    set_xlabeling(ax, actives_cutted)
	    if len(activeAttributesList) > 5:
	        set_xlabeling_rotation(ax, 'vertical')


        if plot_data.view_legend:
	    plotList = [None]
	    lables = ['SIGNIFICANCE:','ns','p<0.05','p<0.01','p<0.001']
	    i = 0
	    for c in colors:
	        #p = Patch(facecolor = c)
	        #p = Rectangle((0,0), 1, 1, facecolor = c)
	        #plotList.append(p)
	        plotList.append(Line2D([],[], color = c, linewidth=5))

	        i += 1
	    #CircleLegend(fig, [['#FF0000', '#00FF00', '#0000FF'], ['dommer1', 'dommer2', 'dommer3']])
	    figlegend = fig.legend(plotList, lables, 'upper right')


	#One element in the pointAndLabelList will always contain 3 items [x, y, label]

        rawDataList, resultList = get_grid_data(s_data, plot_data, f_list, p_list, lsd_list, "3way")

        #update plot-data variables:
        plot_data.point_label_line_width = _width * 0.5
        plot_data.point_lables = pointAndLabelList
        plot_data.raw_data = rawDataList
        plot_data.numeric_data = resultList
        plot_data.plot_type = "mm_anova_f_3way"
        plot_data.point_lables_type = 1
        plot_data.p_matr = res[2].rx(6,True) # for profile plot

        #Frame draw, for standard Matplotlib frame only use show()
        return plot_data


def MixModel_ANOVA_LSD_Plotter_3way(s_data, plot_data, num_subplot=[1,1,1], **kwargs):
	"""
	Mixed Modal ANOVA Plotter

        @type selection: int
        @param selection: Not used in this plotter


	@type s_data.SparseMatrix:     dictionary
	@param s_data.SparseMatrix:    Sparse matrix that contains 3-way data from assessors

	@type s_data.SampleList:       list
	@param s_data.SampleList:      Contains all samples from original data set

	@type s_data.ReplicateList:    list
	@param s_data.ReplicateList:   Contains all replicates original from data set

	@type s_data.AttributeList:    list
	@param s_data.AttributeList:   Contains all attributes original from data set

	@type selectedItem:     list
	@param selectedItem:    Conatins which item in the tree was double-clicked

	@type y_min:            integer
	@param y_min:           indicates the highest score value given in in data set

	ActiveSample_list: Is created from ActiveAssessors (dictionary) and is
	used for iterating through the active asessors
	ActiveSample_list: list
	"""
        activeAssessorsList = plot_data.activeAssessorsList
        activeAttributesList = plot_data.activeAttributesList
        activeSamplesList = plot_data.activeSamplesList
        itemID = plot_data.tree_path



        if len(activeAssessorsList) < 2: #no active assessors
            dlg = wx.MessageDialog(None, 'Two or more Assessors must be active.',
                               'Error Message',
                               wx.OK | wx.ICON_INFORMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        if len(s_data.ReplicateList) < 2: #no active assessors
            dlg = wx.MessageDialog(None, 'Cannot process: There must be a minimum of two Replicates per Sample in the data set',
                               'Error Message',
                               wx.OK | wx.ICON_INFORMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        if len(activeAttributesList) < 1: #no active assessors
            dlg = wx.MessageDialog(None, 'One or more Attributes must be active',
                               'Error Message',
                               wx.OK | wx.ICON_INFORMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        if len(activeSamplesList) < 2: #no active samples
            dlg = wx.MessageDialog(None, 'A minimum of two Samples must be active.',
                               'Error Message',
                               wx.OK | wx.ICON_INFORMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return



	res = load_mm_anova_data(s_data, plot_data)

	activeAttributesList = plot_data.accepted_active_attributes


        # One of these types have been selected:
        lsd_types = ['LSD1', 'LSD2']
        lsd_types_names = ['Sample means & LSD', 'Sample means & Bonferroni LSD']
        if itemID[0] == lsd_types[0]:
            _title = lsd_types_names[0]
            lsd_matr = res[3].rx(1,True)
        elif itemID[0] == lsd_types[1]:
            _title = lsd_types_names[1]
            lsd_matr = res[3].rx(2,True)
        else:
            return # error


        f_list = []
        f_list.append(res[0].rx(1,True))
        f_list.append(res[0].rx(2,True))
        f_list.append(res[0].rx(3,True))
        f_list.append(res[0].rx(4,True))
        f_list.append(res[0].rx(6,True))
        f_list.append(res[0].rx(5,True))


        p_list = []
        p_list.append(res[1].rx(1,True))
        p_list.append(res[1].rx(2,True))
        p_list.append(res[1].rx(3,True))
        p_list.append(res[1].rx(4,True))
        p_list.append(res[1].rx(6,True))
        p_list.append(res[1].rx(5,True))


        # p_matr2
        p_list.append(res[2].rx(1,True))
        p_list.append(res[2].rx(2,True))
        p_list.append(res[2].rx(3,True))
        p_list.append(res[2].rx(4,True))
        p_list.append(res[2].rx(6,True))
        p_list.append(res[2].rx(5,True))


        lsd_list = []
        lsd_list.append(res[3].rx(1,True))
        lsd_list.append(res[3].rx(2,True))



        att_indices = arange(len(activeAttributesList))
        num_active_samps = len(activeSamplesList)

        averages_matrix = zeros((1, len(activeAttributesList)), float)
        for samp in activeSamplesList:
            samp_scores_matrix = []; stacking = 0
            for att in activeAttributesList:
                att_column = s_data.GetAttributeData(activeAssessorsList, att, samp)
                if stacking == 0: samp_scores_matrix = att_column; stacking = 1
                else: samp_scores_matrix = vstack((samp_scores_matrix, att_column))
            samp_scores_matrix = transpose(samp_scores_matrix)

            #print samp_scores_matrix
            averages_samp = average(samp_scores_matrix, 0) # average of the attributes for a given sample

            #print averages_samp
            averages_matrix = vstack((averages_matrix, averages_samp))
        averages_matrix = averages_matrix[1:,:]
        #averages_matrix = center(averages_matrix) # centered (between all active samples)
        #print averages_matrix


        colors = ['#FF0000', '#D3A400', '#009900', '#CC00EE', '#006CFF', '#00AD94',
		  '#666666', '#A4A4A4',
		  '#B7685D', '#BDAB65', '#6CB771', '#A0699F', '#6375B5', '#77A69F']


        # Figure
        replot = False; subplot = plot_data.overview_plot; scatter_width = 35
        if plot_data.fig != None: replot = True
        else: plot_data.fig = Figure(None)
        if subplot: # is subplot
            plot_data.ax = plot_data.fig.add_subplot(num_subplot[0], num_subplot[1], num_subplot[2])
            scatter_width = 15
        else: plot_data.ax = axes_create(plot_data.view_legend, plot_data.fig)
        ax = plot_data.ax; fig = plot_data.fig


        max_aver_list = []; min_aver_list = []
        for i in range(len(activeAttributesList)):
            max_aver_list.append(max(averages_matrix[:,i]))
            min_aver_list.append(min(averages_matrix[:,i]))

        plot_data.lsd_points = []
        for i in range(len(activeAttributesList)):
            plot_data.lsd_points.append([])

        #plot_data.lsd_ypoints = [[]] * len(activeAttributesList)
        vertices = []
        extra_space = 0; c_index = 0; pointAndLabelList = []
        for i in range(len(activeSamplesList)):
            x_samples = []; y_samples = []
            for j in range(len(activeAttributesList)):
                ax.text(j+0.25+extra_space, averages_matrix[i,j], str(i+1), fontsize=13, color=colors[c_index])

                #x_samples.append(j+0.225+extra_space); y_samples.append(averages_matrix[i,j])
                plot_data.lsd_points[j].append(ax.plot([j+0.225+extra_space], [averages_matrix[i,j]], 'k'))
                #plot_data.lsd_ypoints[j].append(averages_matrix[i,j])

                pt = ((j+0.225+extra_space, averages_matrix[i,j]))
                vertices.append(pt)

                _label = "Average (" + activeSamplesList[i] + ": " + activeAttributesList[j] + ")"
                pointAndLabelList.append([j+0.25+extra_space, averages_matrix[i,j], _label])
            #ax.scatter(x_samples, y_samples, s = 2, color="#999999")
            c_index += 1
            if c_index == len(colors): c_index = 0
            if extra_space == 0.5: extra_space = 0
            else: extra_space = 0.5


        #lc = LineCollection(vertices, colors='#000000')
        #plot_data.ax.add_collection(lc)



        vertices = []
        #print plot_data.lsd_points
        plot_data.lsd_lines = []
        lsd_colors = {0.0:'#999999', 1.0:'#FFD800', 2.0:'#FF8A00', 3.0:'#E80B0B'}
        for i in range(len(activeAttributesList)):
            max_aver = max_aver_list[i]
            lsd_color = lsd_colors[res[2].rx(1,True)[i]]
            plot_data.lsd_lines.append(ax.plot([i+0.5, i+0.5], [max_aver, max_aver-lsd_matr[i]], lsd_color, linewidth=3))

            pt = (i+0.5, i+0.5), (max_aver, max_aver-lsd_matr[i])
            vertices.append(pt)

            set_points_in_range(ax, [max_aver, max_aver-lsd_matr[i]], i+1, plot_data.lsd_points)


        #lc2 = LineCollection(vertices, colors='#FF0000', linewidths=3)
        #plot_data.ax.add_collection(lc2)

        upperlim = max(max_aver_list) + (max(max_aver_list)-min(min_aver_list))*0.1
        limits = [0, len(activeAttributesList), min(min_aver_list), upperlim]


        vertices = []
        for att_ind in att_indices:
            pt = ((att_ind, limits[2]), (att_ind, limits[3]))
            vertices.append(pt)

        lc3 = LineCollection(vertices, colors='#000000', linestyle='dashed')
        plot_data.ax.add_collection(lc3)
        #ax.vlines(att_indices, limits[2], limits[3], fmt='k--')


        ax.grid(plot_data.view_grid)
        if plot_data.view_legend:
	    c_i = 0; plotList = []
	    # labels = activeSamplesList[:]
	    labels = []; samp_nr = 1
	    for samp in activeSamplesList:
	        #p = Patch(facecolor = colors[c_i])
	        #plotList.append(p)

	        labels.append(str(samp_nr) + ": " + samp)
	        samp_nr += 1

	        plotList.append(Line2D([],[], color = colors[c_i], linewidth=5))
	        c_i += 1
	        if c_i == len(colors): c_i = 0

	    plotList.append(None); plotList.append(None); plotList.append(None)

	    #   colors:   grey       yellow     orange      red
            s_colors = ['#999999', '#FFD800', '#FF8A00', '#E80B0B']
	    labels.extend(['', '', 'SIGNIFICANCE:','ns','p<0.05','p<0.01','p<0.001'])
	    for c in s_colors:
	        #p = Patch(facecolor = c)
	        #plotList.append(p)

	        plotList.append(Line2D([],[], color = c, linewidth=5))

	        c_i += 1
	    #CircleLegend(fig, [['#FF0000', '#00FF00', '#0000FF'], ['dommer1', 'dommer2', 'dommer3']])
	    figlegend = fig.legend(plotList, labels, 'upper right')

	    #texts = figlegend.get_texts()
	    #texts[0]._fontproperties.set_size(14)

        if not subplot:
	    axes_setup(ax, 'Attributes', 'Score', _title, limits)
	    set_xlabeling(ax, activeAttributesList)
	    if len(activeAttributesList) > 11:
	        set_xlabeling_rotation(ax, 'vertical')
        else:
            axes_setup(ax, '', '', _title, limits, font_size=10)
            actives_cutted = activeAttributesList[:]
            if len(activeAttributesList) > 5: # cut labels
                for i in range(len(actives_cutted)): actives_cutted[i] = actives_cutted[i][0:6] + ".."
	    set_xlabeling(ax, actives_cutted)
	    if len(activeAttributesList) > 7:
	        set_xlabeling_rotation(ax, 'vertical')

	#One element in the pointAndLabelList will always contain 3 items [x, y, label]

        rawDataList, resultList = get_grid_data(s_data, plot_data, f_list, p_list, lsd_list, "3way")

        #update plot-data variables:
        plot_data.point_lables = pointAndLabelList
        plot_data.raw_data = rawDataList
        plot_data.numeric_data = resultList
        plot_data.plot_type = "mm_anova_lsd_3way"
        plot_data.point_lables_type = 0

        #Frame draw, for standard Matplotlib frame only use show()
        return plot_data


def set_points_in_range(ax, ydata, selected, point_list): # selected [1, ..., n]
        points = point_list[selected-1]
        #print points

        #print len(points)
        for p in points:
            if ydata[0] >= p[0].get_ydata()[0] and ydata[1] < p[0].get_ydata()[0]:
                # point within range
                p[0].set_marker('.')
                #p[0].set_makersize(0.5)
            else:
                p[0].set_marker('')
                #p[0].set_makersize(1)






def MixModel_ANOVA_OverviewPlotter(s_data, plot_data, *args, **kwargs):
    """
    Overview Plot
    """
    plot_type = kwargs['plot_type']

    func = None
    if plot_type == "3way":
        func = MixModel_ANOVA_Plotter_3way
        rotation_list = ['F1', 'F2', 'F2b', 'F3', 'F4', 'F5']
        itemID_list = [['F1'], ['F2'], ['F2b'], ['F3'], ['F4'], ['F5']]
    elif plot_type == "2way":
        func = MixModel_ANOVA_Plotter_2way
        rotation_list = ['F1', 'F2', 'F3']
        itemID_list = [['F1'], ['F2'], ['F3']]
    elif plot_type == "2way1rep":
        func = MixModel_ANOVA_Plotter_2way1rep
        rotation_list = ['F1', 'F2']
        itemID_list = [['F1'], ['F2']]
    else:
        print "Error: wrong plot type id_str"
        return

    return OverviewPlotter(s_data, plot_data, itemID_list, func, rotation_list)



def MixModel_ANOVA_LSD_OverviewPlotter(s_data, plot_data, *args, **kwargs):
    """
    Overview Plot
    """

    plot_type = kwargs['plot_type']

    func = None
    if plot_type == "3way":
        func = MixModel_ANOVA_LSD_Plotter_3way
    elif plot_type == "2way":
        func = MixModel_ANOVA_LSD_Plotter_2way
    elif plot_type == "2way1rep":
        func = MixModel_ANOVA_LSD_Plotter_2way1rep
    else:
        print "Error: wrong plot type id_str"
        return

    lsd_types = ['LSD1', 'LSD2']
    lsd_tree_paths = [['LSD1'], ['LSD2']]

    return OverviewPlotter(s_data, plot_data, lsd_tree_paths, func, lsd_types)

