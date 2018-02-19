#!/usr/bin/env python


from Plot_Tools import *




def ManhattanCalc(X, PCs=14, standardize=False):
    """

    Find explained variable variances for each PC of a PCA using either SVD or NIPALS, on the given data matrix X.


    @param X: 2-dimensional matrix of number data
    @type X: numpy array

    @param PCs: maximum number of Principal Components (only used for PCA by NIPALS)
    @type PCs: int

    @param standardize: wheter X should be standardized or not
    @type standardize: bool


    @return: Scores (2d numpy array), Loadings (2d numpy array), Explained variable variances (2d numpy array)
    """


    (rows, cols) = shape(X)



    # E[0]
    E0 = mean_center(X)

    if standardize:
        E0 = standardization(E0)

    # total residual variance for PC[0] (calculating from E[0])
    # for E[0] the total residual variance is 100%
    tot_residual_variance_0 = 0

    # get variable residual variances for E[0] (used for normalization of residual variable variances of E[i])
    variable_residual_variances_0 = zeros((cols), float)
    for var_ind in range(cols):
        variable_residual_variances_0[var_ind] = sum(E0[:, var_ind]**2)
    #tot_residual_variance_0 = sum(tot_variable_residual_variances_0)

    # Scores
    # T[1] ... T[PCs]

    # Loadings
    # P[1] ... P[PCs]

    # E
    # E-matrix[1] ... E-matrix[PCs]


    Scores, Loadings, E = PCA(X, standardize=standardize, PCs=PCs, E_matrices=True, nipals=True)
    #print "pca done"

    (objects, variables) = shape(E[0])
    actual_PCs = len(E)


    explained_variable_variances = zeros((actual_PCs, variables), float)

    variable_residual_variances_i = zeros((variables), float)
    #variable_cloumn_squares = zeros((objects), float)

    # for each PC
    for i in range(actual_PCs):
        for var_ind in range(variables):

            # calculate residual variable variances for PC[i] and current variable
            # normalize for current variable
            variable_residual_variances_i[var_ind] = sum(E[i, :, var_ind]**2) / float(variable_residual_variances_0[var_ind])

        # calculate explained variance for all variables for PC[i]
        explained_variable_variances[i, :] =  1.0 - variable_residual_variances_i[:]

    return [Scores, Loadings, explained_variable_variances]




def get_leave_out_variables(X):
    """
    Find attribute vectors that should be left out. Return indices of attributes left out and updated X.

    @param X: 2-dimensional matrix of number data
    @type X: numpy array

    @return: list of ints, 2d numpy array
    """

    (rows, cols) = shape(X)

    # E[0]
    E0 = mean_center(X)


    # check for variables to be left out:
    leave_out_inds = []
    for var_ind in range(cols):
        variable_residual_var = sum(E0[:, var_ind]**2)
        if abs(variable_residual_var) < 0.000000001:
            leave_out_inds.append(var_ind)



    # update X
    if len(leave_out_inds) > 0:
        print "leave out:"
        print leave_out_inds

        X_ = zeros((rows, cols-len(leave_out_inds)))
        ind = 0
        for var_ind in range(cols):
            if var_ind not in leave_out_inds:
                X_[:, ind] = X[:, var_ind]
                ind += 1
        X = X_

    return leave_out_inds, X



def get_dataset(s_data, plot_data, active_assessor):
    """
    Get active averaged data for current assessor


    @param s_data: Sensory data (the complete set)
    @type s_data: SenosoryData class

    @param plot_data: Plot configurations, active lists, matplotlib objects and various values handled by Plot_Frame.
    @type plot_data: PlotData class

    @param active_assessor: current active assessor
    @type active_assessor: string

    @return: 2d numpy array
    """

    # active_replicates=[s_data.ReplicateList[0]] # with first replicates only
    return s_data.GetAssessorAveragedDataAs2DARRAY(active_samples=plot_data.activeSamplesList, active_attributes=plot_data.activeAttributesList, active_assessor=active_assessor)



def get_normalized_color(rgb, color_range=(0.0, 255.0)):
    """

    Normalize R, G and B to a specific color range

    @param rgb: Input RGB color
    @type rgb: tuple


    @param color_range: Color range for normalization
    @type color_range: tuple

    @return: New RGB tuple

    """

    # rgb is a tuple of (red, green, blue)
    # crange is a tupe of color range
    # scaling to range [0.0, 1.0]

    # find min and max
    ind_1 = 1; ind_2 = 0
    if color_range[0] > color_range[1]:
        ind_1 = 0; ind_2 = 1


    #range length (difference):
    range_length =  (color_range[ind_1]) - (color_range[ind_2])

    # scale:
    new_r = rgb[0] / (range_length)
    new_g = rgb[1] / (range_length)
    new_b = rgb[2] / (range_length)
    return (new_r, new_g, new_b)



def get_plot_data_matrix(c_data, plot_data, projection_type, current_active):
    """

    Get the plot matrix data for the current Manhattan plot.


    @param c_data: Collection of calculated data (for each assessor)
    @type c_data: dict

    @param plot_data: Plot configurations, active lists, matplotlib objects and various values handled by Plot_Frame.
    @type plot_data: PlotData class

    @param projection_type: Which type of projection for current plot
    @type projection_type: string

    @param current_active: Current active assessor or variable
    @type current_active: string


    @return: 2d numpy array

    """

    if projection_type == "manhattan_ass":
        if len(c_data[current_active]) == 4:
            return c_data[current_active][2], c_data[current_active][3] # explained_variable_variances for current assessor is returned
        else:
            return c_data[current_active][2], plot_data.activeAttributesList

    elif projection_type == "manhattan_att":

        # pointer to active assessors list
        active_assessors = plot_data.activeAssessorsList



        # get information about calculated data
        if not c_data[active_assessors[0]] == None:
            (PCs, num_vars) = shape(c_data[active_assessors[0]][2])

        else:
            #print "c_data["+ active_assessors[0] +"] == None"
            return None # failed

        # leave out assessor?:
        var_inds = []; new_active_ass = []
        for ass_ind in range(len(active_assessors)):
            (temp_PCs, num_vars) = shape(c_data[active_assessors[ass_ind]][2])
            if temp_PCs < PCs:
                PCs = temp_PCs

            if len(c_data[active_assessors[ass_ind]]) == 4:
                if current_active in c_data[active_assessors[ass_ind]][3]:
                    new_active_ass.append(active_assessors[ass_ind])
                    active_att = c_data[active_assessors[ass_ind]][3]
                    # index pos of current active variable:
                    active_var_pos = active_att.index(current_active)
                    var_inds.append(active_var_pos)
                #else: leave out assessor
            else:
                new_active_ass.append(active_assessors[ass_ind])
                # index pos of current active variable:
                active_var_pos = plot_data.activeAttributesList.index(current_active)
                var_inds.append(active_var_pos)


        # create a data matrix with variable variances for current variable and all active assessors
        all_current_active_variable_variances = zeros((PCs, len(new_active_ass)), float)

        # fetch data:
        for ind in range(len(new_active_ass)): # for each assessor
            all_current_active_variable_variances[0:PCs, ind] = c_data[new_active_ass[ind]][2][0:PCs, var_inds[ind]]

        return all_current_active_variable_variances, new_active_ass



    else:
        print "Projection type not correct"
        return None # failed



def get_numerical_data_manhattan(active_assessors, active_attributes, plot_data, s_data, c_data):
    """

    Create numerical data for grid view.


    @param active_assessors: Currently active assessors
    @type active_assessors: list of strings

    @param active_attributes: Currently active attributes
    @type active_attributes: list of strings

    @param plot_data: Plot configurations, active lists, matplotlib objects and various values handled by Plot_Frame.
    @type plot_data: PlotData class

    @param c_data: Collection of calculated data (for each assessor)
    @type c_data: dict

    @return: list of lists of strings

    """

    # c_data with: explained variances for each attribute
    # T, P, explained_variable_variances = ManhattanCalc(m_data, PCs=max_number_of_PCs)
    #
    # ass_data = c_data['assessor1']
    # ass_data[0] = Scores, ass_data[1] = Loadings, ass_data[2] = explained_variable_variances




    numericDataList = []
    emptyline = ['']
    headerline = ['Numerical Manhattan Data']
    underline =     ['========================']
    numericDataList.append(headerline)
    numericDataList.append(underline)
    numericDataList.append(emptyline)


    if len(active_assessors) == 1:



        headerline = ['Attributes left out:']
        if len(c_data[active_assessors[0]]) == 4:
            actives = c_data[active_assessors[0]][3]; not_in = []
            for att in plot_data.activeAttributesList:
                if att not in actives:
                    not_in.append(att)
            if len(not_in) > 0:
                headerline.extend(not_in)
                numericDataList.append(headerline)
                numericDataList.append(emptyline)



        headerline = ['Cumulative expl. variable variances:']
        numericDataList.append(headerline)

        headerline = ['']
        headerline.extend(active_attributes)
        numericDataList.append(headerline)
        for PC_i in range(len(c_data[active_assessors[0]][2])): # for each PC
            dataline = []; pc_str = "PC" + str(PC_i+1)
            dataline.append(pc_str)
            for att_ind in range(len(active_attributes)):
                dataline.append(num2str(c_data[active_assessors[0]][2][PC_i, att_ind] * 100.0, fmt="%.3f") + "%")

            numericDataList.append(dataline)

        numericDataList.append(emptyline)
        numericDataList.append(emptyline)
        numericDataList.append(emptyline)

        headerline = ['Scores:']
        numericDataList.append(headerline)
        for PC_i in range(len(c_data[active_assessors[0]][1])): # for each PC
            dataline = []; pc_str = "PC" + str(PC_i+1)
            dataline.append(pc_str)

            # complete data:
            #for samp_ind in range(len(plot_data.activeSamplesList) * len(s_data.ReplicateList)):
            #    dataline.append(c_data[active_assessors[0]][0][samp_ind, PC_i])


            # averaged data:
            for samp_ind in range(len(plot_data.activeSamplesList)):
                dataline.append(num2str(c_data[active_assessors[0]][0][samp_ind, PC_i]))

            if PC_i == 0:
                headerline = ['']
                for samp in plot_data.activeSamplesList:
                    # complete data:
                    #for rep in s_data.ReplicateList:
                    #    headerline.append(samp + " - " + rep)


                    # averaged data:
                    headerline.append(samp)
                numericDataList.append(headerline)

            numericDataList.append(dataline)


        numericDataList.append(emptyline)
        numericDataList.append(emptyline)
        numericDataList.append(emptyline)

        headerline = ['Loadings:']
        numericDataList.append(headerline)
        headerline = ['']
        headerline.extend(active_attributes)
        numericDataList.append(headerline)
        for PC_i in range(len(c_data[active_assessors[0]][1])): # for each PC
            dataline = []; pc_str = "PC" + str(PC_i+1)
            dataline.append(pc_str)
            for att_ind in range(len(active_attributes)):
                dataline.append(num2str(c_data[active_assessors[0]][1][PC_i, att_ind]))

            numericDataList.append(dataline)

    elif len(active_attributes) == 1:

        headerline = ['Cumulative expl. variable variances:']
        numericDataList.append(headerline)

        headerline = ['']
        headerline.extend(active_assessors)
        numericDataList.append(headerline)
        (PCs, num_vars) = shape(c_data[active_assessors[0]][2])
        for ass_ind in range(len(active_assessors)):
            (temp_PCs, num_vars) = shape(c_data[active_assessors[ass_ind]][2])
            if temp_PCs < PCs:
                PCs = temp_PCs


        active_att_ind = plot_data.activeAttributesList.index(active_attributes[0])
        for PC_i in range(PCs): # for each PC
            dataline = []; pc_str = "PC" + str(PC_i+1)
            dataline.append(pc_str)
            for ass_ind in range(len(active_assessors)):
                if len(c_data[active_assessors[ass_ind]]) == 4:
                    if active_attributes[0] in c_data[active_assessors[ass_ind]][3]:
                        active_att = c_data[active_assessors[ass_ind]][3]
                        # index pos of current active variable:
                        active_att_ind = active_att.index(active_attributes[0])
                        dataline.append(num2str(c_data[active_assessors[ass_ind]][2][PC_i, active_att_ind] * 100.0, fmt="%.3f") + "%")
                else:
                    # index pos of current active variable:
                    active_att_ind = plot_data.activeAttributesList.index(active_attributes[0])
                    dataline.append(num2str(c_data[active_assessors[ass_ind]][2][PC_i, active_att_ind] * 100.0, fmt="%.3f") + "%")

            numericDataList.append(dataline)
    return numericDataList




def get_raw_data_manhattan(active_assessors, active_attributes, plot_data, s_data):
    """
    Create raw data for grid view.

    @param active_assessors: Currently active assessors
    @type active_assessors: list of strings

    @param active_attributes: Currently active attributes
    @type active_attributes: list of strings


    @param plot_data: Plot configurations, active lists, matplotlib objects and various values handled by Plot_Frame.
    @type plot_data: PlotData class

    @param s_data: Sensory data (the complete set)
    @type s_data: SenosoryData

    @return: list of lists of strings

    """

    """
    rawDataList = []
    emptyLine = ['']
    headerRawData = ['Raw Data']
    underline = ['========']
    rawDataList.append(headerRawData)
    rawDataList.append(underline)
    rawDataList.append(emptyLine)

    attributeLine = ['Assessor', 'Sample', 'Replicate']
    attributeLine.extend(active_attributes)
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
    """

    return raw_data_grid(s_data, plot_data, active_assessors=active_assessors)


def ManhattanPlotImage(s_data, plot_data, m_data, col_list, cmap=None):
    """

    Produces a polygon collection (Vector Image) for plot_data.ax (matplotlib axes) based on a given 2d matrix of values 0.0 - 1.0.
    Adds the collection to the axes object of plot_data.


    @param s_data: Sensory data (the complete set)
    @type s_data: SenosoryData class

    @param plot_data: Plot configurations, active lists, matplotlib objects and various values handled by PlotFrame.
    @type plot_data: PlotData class

    @param m_data: current plot data matrix, of explained variable variances for each PC
    @type m_data: 2d numpy array

    @return: matplotlib.collections.PolygonCollection class and Points & Lables list


    """


    (rows, cols) = shape(m_data)

    dy = 1.0 # height step size
    dx = 1.0 # width step size

    vertices = []
    facecolors = []
    edgecolors = []

    pointAndLabelList = []

    ########## setting vertices: ##########
    y_value = rows
    for row in range(0, rows):
        y_value -= 1
        for col in range(0, cols):

            x1 = col*dx
            x2 = x1+dx

            y1 = row*dy
            y2 = y1+dy

            # the four xy points: upper-left upper-right lower-left lower-right
            xy = ((x1, y1), (x2, y1), (x2, y2), (x1, y2))
            vertices.append(xy)

            expl_variance = "%.3f" % (100.0*m_data[y_value][col])
            pointAndLabelList.append([x1+0.5, y1+0.5, "(PC" + str(y_value+1) + ", " + col_list[col] + ", Explained variance: " + expl_variance + "%)"])


            # get color for current quad
            if cmap == None:
                _color = get_normalized_color((m_data[y_value][col], m_data[y_value][col], m_data[y_value][col]), color_range=(0.0, 1.0))
            else:
                _color = cmap(m_data[y_value][col])

            facecolors.append(_color)
            edgecolors.append(_color)



    # init of PolyCollection
    # using PolyCollection and not QuadMesh because PolyCollection supports ScalarMappable (like colormap)

    collection = PolyCollection(vertices, facecolors=facecolors, edgecolors=edgecolors)

    plot_data.ax.add_collection(collection)

    return collection, pointAndLabelList # Vector image added successfully



def set_manhattan_colorbar(fig, colormap):
    """

    Sets a colorbar for a figure with a given colormap.

    @param fig: Current figure
    @type fig: matplotlib.figure.Figure class

    @param colormap: The colormap for the colorbar
    @type colormap: matplotlib.colors.LinearSegmentedColormap class

    @return: matplotlib.colorbar.Colorbar class

    """

    # set color map mappable
    colormap_mappable = ScalarMappable(cmap=colormap)

    colormap_mappable.set_array(array([100, 0]))
    #colormap_mappable.set_clim(vmin=(100, 0))
    colorbar = fig.colorbar(colormap_mappable)
    # flip colorbar vertically
    #colormap_mappable.colorbar[1].invert_yaxis()

    colorbar.set_label('Explained Variance [%]')
    return colorbar


def has_error(plot_data):
    """

    Checks basic selection errors. Returns true for error or false for no error.

    @param plot_data: Plot configurations, active lists, matplotlib objects and various values handled by Plot_Frame.
    @type plot_data: PlotData class pointer

    @return: bool

    """
    if len(plot_data.activeAssessorsList) < 1:
        show_err_msg('No assessors selected.')
        return True
    if len(plot_data.activeAttributesList) < 1:
        show_err_msg('No attributes selected.')
        return True
    if len(plot_data.activeSamplesList) < 3:
        show_err_msg('Minimum 3 samples needed.')
        return True

    return False


def ManhattanPlotter(s_data, plot_data, num_subplot=[1,1,1], selection=0):
    """

    Manhattan Plot main method. Returns "filled" PlotData or None type if plotting fails.

    @param s_data: Sensory data (the complete set)
    @type s_data: SenosoryData class

    @param plot_data: Plot configurations, active lists, matplotlib objects and various values handled by PlotFrame.
    @type plot_data: PlotData class

    @param num_subplot: Subplot numbering.
    @type num_subplot: list of ints

    @param selection: PCA preprocessing selection
    @type selection: int


    @return: PlotData

    """

    current_active = plot_data.tree_path[0]
    #print current_active

    plot_data.selection = selection
    # selection = 0: raw-data
    # selection = 1: standardize
    if has_error(plot_data): return

    # PCA mode
    if selection == 0:
        standardize = False
    elif selection == 1:
        standardize = True


    view_legend = False
    # set plot projection type:
    if current_active in plot_data.activeAssessorsList:
        plot_type = "manhattan_ass"
    elif current_active in plot_data.activeAttributesList:
        plot_type = "manhattan_att"
        view_legend = plot_data.view_legend
    else:
        show_err_msg('Current active element not accepted: ' + str(current_active))
        return

    plot_data.view_legend = view_legend



    max_number_of_PCs = plot_data.maxPCs

    c_data = {} # ex: c_data['assessor1'] = [T, P, explained_variable_variances]

    if len(plot_data.collection_calc_data) > 0:
        c_data = plot_data.collection_calc_data
    else:

        msg = 'The following attributes were left out of the analysis because \nfor one or more assessors the standard deviation is 0: \n\n'
        leave_outs = False


        for active_assessor in plot_data.activeAssessorsList:

            m_data = get_dataset(s_data, plot_data, active_assessor)


            if standardize:
                leave_out_inds, X = get_leave_out_variables(m_data)
            else:
                leave_out_inds = []
                X = m_data

            if len(leave_out_inds) > 0:
                leave_outs = True
                new_active_att = []
                for att_ind in range(len(plot_data.activeAttributesList)):
                    if att_ind not in leave_out_inds:
                        new_active_att.append(plot_data.activeAttributesList[att_ind])

                msg += 'For ' + active_assessor + ': ('
                for att_ind in leave_out_inds:
                    msg += plot_data.activeAttributesList[att_ind]
                    if att_ind == leave_out_inds[-1]:
                        msg += ')\n'
                    else:
                        msg += ', '

            else:
                new_active_att = plot_data.activeAttributesList


            # ass_data[0] = Scores, ass_data[1] = Loadings, ass_data[2] = explained_variable_variances
            ass_data = ManhattanCalc(X, PCs=max_number_of_PCs, standardize=standardize)

            if len(leave_out_inds) > 0:
                ass_data.append(new_active_att)

            c_data[active_assessor] = deepcopy(ass_data)

            c_data["accepted_active_atts"] = new_active_att

        if leave_outs:
            msg += '\n\nYou can view the numerical data to see what is left out of the \nanalysis for a given plot. (Note: this message will only \nappear when data is recalculated (selection changes))'
            show_info_msg(msg)

        # store pointer to collection for usage later
        plot_data.collection_calc_data = c_data







    # get data-matrix for plotting:
    plot_data_matrix, active_list = get_plot_data_matrix(c_data, plot_data, plot_type, current_active)

    if not isinstance(plot_data_matrix, (ndarray, list)):
        raise TypeError, "plot_data_matrix is not an array object"
        #return -1 # TypeError of m_data

    (rows, cols) = shape(plot_data_matrix)

    if rows < 1 or cols < 1:
        _msg = "Cannot produce plot. All data has been left out of analysis for " + current_active + "."
        show_info_msg(_msg)
        return
        #raise ValueError, "incorret dimensions of m_data" # Error in dimensions of m_data



    # Figure
    replot = False; subplot = plot_data.overview_plot; scatter_width = 35
    if plot_data.fig != None: replot = True
    else: plot_data.fig = Figure(None)
    if subplot: # is subplot
        plot_data.ax = plot_data.fig.add_subplot(num_subplot[0], num_subplot[1], num_subplot[2])
        scatter_width = 15
    else: plot_data.ax = axes_create(view_legend, plot_data.fig)
    ax = plot_data.ax; fig = plot_data.fig




    # colormap: from Plot_Tools
    cmap = colormaps['manhattan']


    # Produce image:
    if plot_type == "manhattan_ass":
        collection, pointAndLabelList = ManhattanPlotImage(s_data, plot_data, plot_data_matrix, active_list, cmap=cmap)

        if not plot_data.overview_plot:
            # set numerical and raw data:
            plot_data.numeric_data = get_numerical_data_manhattan([current_active], active_list, plot_data, s_data, c_data)
            plot_data.raw_data = get_raw_data_manhattan([current_active], active_list, plot_data, s_data)

    elif plot_type == "manhattan_att":
        collection, pointAndLabelList = ManhattanPlotImage(s_data, plot_data, plot_data_matrix, active_list, cmap=cmap)

        if not plot_data.overview_plot:
            # set numerical and raw data:
            plot_data.numeric_data = get_numerical_data_manhattan(active_list, [current_active], plot_data, s_data, c_data)
            plot_data.raw_data = get_raw_data_manhattan(active_list, [current_active], plot_data, s_data)

        frame_colored = colored_frame(s_data, plot_data, c_data["accepted_active_atts"], current_active)
        if frame_colored:
            significance_legend(plot_data)

    set_plot_adjustments(plot_data, s_data, plot_type, shape(plot_data_matrix), current_active, active_list)




    #update plot-data variables:
    plot_data.point_lables = pointAndLabelList
    plot_data.plot_type = plot_type
    plot_data.point_lables_type = 0

    return plot_data



def set_plot_adjustments(plot_data, s_data, projection_type, m_data_shape, current_active, active_list):
    """

    Sets plot labeling, grid, limits, ticks and colorbar.


    @param s_data: Sensory data (the complete set)
    @type s_data: SenosoryData class

    @param plot_data: Plot configurations, active lists, matplotlib objects and various values handled by PlotFrame.
    @type plot_data: PlotData class

    @param m_data_shape: (Width, Height) of plot matrix data
    @type m_data_shape: tuple

    @param current_active: Current active assessor or variable
    @type current_active: string

    @param active_list: Currently active assessors or attributes
    @type active_list: list of strings

    @return: None


    """

    ax = plot_data.ax
    (rows, cols) = m_data_shape

    if projection_type == "manhattan_ass":
        p_type_label = "Attribute"
        # string lists for labeling
        _range = arange(1, cols+1)
        _range = []
        for att in active_list:
            _range.append(s_data.AttributeList.index(att)+1)
        x_string_list = [str(element) for element in _range]


    elif projection_type == "manhattan_att":
        p_type_label = "Assessor"
        # string lists for labeling
        _range = arange(1, cols+1)
        _range = []
        for ass in active_list:
            _range.append(s_data.AssessorList.index(ass)+1)
        x_string_list = [str(element) for element in _range]


    # lables/ticks adjustmens
    _range = arange(1, rows+1)
    y_string_list = [str(element) for element in _range]
    y_string_list.reverse()


    ax.set_xticks(_range)


    # plot corners: xmin, xmax, ymin, ymax
    limits = [0, cols, 0, rows]

    # axes adjustments
    if not plot_data.overview_plot:
        axes_setup(ax, p_type_label, 'PC', "Manhattan Plot: " + current_active, limits)

        # horizontal labeling:
        if projection_type == "manhattan_ass":
            set_xlabeling(ax, active_list)
            if len(plot_data.activeAttributesList) > 7:
                set_xlabeling_rotation(ax, 'vertical')

        elif projection_type == "manhattan_att":
            set_xlabeling(ax, active_list)
            if len(plot_data.activeAssessorsList) > 7:
                set_xlabeling_rotation(ax, 'vertical')


        # vertical labeling:
        set_ylabeling(ax, y_string_list)
        _range = arange(0.5, (rows)+0.5, 1)
        #_range = arange(1, (rows)+1, 1)
        ax.set_yticks(_range)


        # colormap: from Plot_Tools
        cmap = colormaps['manhattan']

        # color bar
        colorbar = set_manhattan_colorbar(plot_data.fig, cmap)

    else:
        axes_setup(ax, '', '', "Manhattan Plot: " + current_active, limits, font_size=9)
        set_xlabeling(ax, x_string_list, font_size=9)
        set_ylabeling(ax, y_string_list, font_size=9)
        _range = arange(0.5, (rows)+0.5, 1)
        ax.set_yticks(_range)


    ax.grid(plot_data.view_grid)



def ManhattanAssOverviewPlotter(s_data, plot_data, selection=0):
    """
    Overview Plot (assessor)

    @param s_data: Sensory data (the complete set)
    @type s_data: SenosoryData class

    @param plot_data: Plot configurations, active lists, matplotlib objects and various values handled by PlotFrame.
    @type plot_data: PlotData class

    @param selection: PCA preprocessing selection
    @type selection: int


    @return: PlotData


    """

    pydata_list = []
    if plot_data.tree_path == ["Overview Plot (assessors)"]:
        for ass in plot_data.activeAssessorsList:
            pydata_list.append([ass])
        rotation_list = plot_data.activeAssessorsList[:]

    plot_data.fig = Figure(None)
    plot_data.fig.add_axes([0.45, 0.05, 0.45, 0.9], frameon=False, visible=False)

    # colormap: from Plot_Tools
    cmap = colormaps['manhattan']
    colorbar = set_manhattan_colorbar(plot_data.fig, cmap)

    res = OverviewPlotter(s_data, plot_data, pydata_list, ManhattanPlotter, rotation_list, special_selection=selection)


    if res == None: return None

    res.fig.subplots_adjust(left=0.05, bottom=0.05, right=0.80, top=0.95, wspace=0.15, hspace=0.3)


    return res



def ManhattanAttOverviewPlotter(s_data, plot_data, selection=0):
    """
    Overview Plot (attributes)

    @param s_data: Sensory data (the complete set)
    @type s_data: SenosoryData class

    @param plot_data: Plot configurations, active lists, matplotlib objects and various values handled by PlotFrame.
    @type plot_data: PlotData class

    @param selection: PCA preprocessing selection
    @type selection: int


    @return: PlotData

    """

    pydata_list = []
    if plot_data.tree_path == ["Overview Plot (attributes)"]:
        for att in plot_data.activeAttributesList:
            pydata_list.append([att])
        rotation_list = plot_data.activeAttributesList[:]

    plot_data.fig = Figure(None)

    if plot_data.view_legend:
        plot_data.fig.add_axes([0.375, 0.05, 0.375, 0.9], frameon=False, visible=False)
    else:
        plot_data.fig.add_axes([0.45, 0.05, 0.45, 0.9], frameon=False, visible=False)


    # colormap: from Plot_Tools
    cmap = colormaps['manhattan']
    colorbar = set_manhattan_colorbar(plot_data.fig, cmap)


    res = OverviewPlotter(s_data, plot_data, pydata_list, ManhattanPlotter, rotation_list, special_selection=selection)

    if res == None: return None


    #res.fig.add_axes([0.45, 0.05, 0.45, 0.9], frameon=False, visible=False)


    if plot_data.view_legend:
        res.fig.subplots_adjust(left=0.05, bottom=0.05, right=0.65, top=0.95, wspace=0.15, hspace=0.3)
    else:
        res.fig.subplots_adjust(left=0.05, bottom=0.05, right=0.80, top=0.95, wspace=0.15, hspace=0.3)



    return res
