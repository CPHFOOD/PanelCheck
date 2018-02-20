#!/usr/bin/env python

from copy import deepcopy, copy

class PlotData:
    """
    Class containing settings for a general plot.
    """
    def __init__(self, active_ass=[], active_att=[], active_samp=[], \
                       tree_path=[], view_grid=False, view_legend=False):
        # gui selections:
        self.activeAssessorsList = active_ass
        self.activeAttributesList = active_att
        self.activeSamplesList = active_samp
        self.tree_path = tree_path # path selection in tree (old itemID)
        self.view_grid = view_grid
        self.view_legend = view_legend
        self.overview_plot = False
        self.aspect = 'auto'

        # standard plot data:
        self.error = -1 # -1 (not checked), 0 (no errors), 1 (errors)
        self.fig = None # matplotlib Figure
        self.ax = None # matplotlib Axes
        self.limits = [0.0, 1.0, 0.0, 1.0] # axes limits [xmin, xmax, ymin, ymax]

        self.raw_data = [] # raw data scores (for viewing in grid frame)
        self.raw_data_mv_pos = []
        self.numeric_data = [] # numerical data of the calculations (for viewing in grid frame)
        self.numeric_data_config = {}

        self.special_opts = {}

        self.point_lables = []
        self.point_lables_type = 0 # 0: points, 1: lines
        self.plot_type = "general plot" # plot identification (name)


    def actives_changed(self, active_ass=[], active_att=[], active_samp=[]):
        """
        Returns True if active-lists of assessors, attributes or samples have been changed.
        If there is no change it returns False.
        """
        if not self.activeAssessorsList == active_ass: return True # not equal, actives changed
        if not self.activeAttributesList == active_att: return True # not equal, actives changed
        if not self.activeSamplesList == active_samp: return True # not equal, actives changed
        return False # no change



    def set_limits(self, new_limits):
        """
        Sets new limits, with error checking.
        """
        if isinstance(new_limits, (list, tuple)):
            if len(new_limits) == 4:
                for limit in new_limits:
                    if not isinstance(limit, (int, float)): return False
                self.limits = new_limits
                return True
            else: return False
        else: return False


    def copy_data_to(self, dest):
        dest.activeAssessorsList = copy(self.activeAssessorsList)
        dest.activeAttributesList = copy(self.activeAttributesList)
        dest.activeSamplesList = copy(self.activeSamplesList)
        dest.tree_path = copy(self.tree_path)
        dest.view_grid = copy(self.view_grid)
        dest.view_legend = copy(self.view_legend)
        dest.overview_plot = copy(self.overview_plot)
        dest.aspect = copy(self.aspect)

        dest.raw_data = copy(self.raw_data)
        dest.raw_data_mv_pos= copy(self.raw_data_mv_pos)
        dest.numeric_data=copy(self.numeric_data)
        dest.numeric_data_config= copy(self.numeric_data_config)

        dest.special_opts = copy(self.special_opts)

        dest.point_lables= copy(self.point_lables)
        dest.point_lables_type= copy(self.point_lables_type)
        dest.plot_type= copy(self.plot_type)


class MM_ANOVA_PlotData(PlotData):
    def __init__(self, active_ass=[], active_att=[], active_samp=[], tree_path=[], view_grid=False, view_legend=False):
        PlotData.__init__(self, active_ass, active_att, active_samp, tree_path, view_grid, view_legend)
        self.sensmixed_data = None
        self.accepted_active_attributes = []
        self.p_matr = None

    def copy_data(self, obj): # copy from obj
        self.sensmixed_data = deepcopy(obj.sensmixed_data)
        self.accepted_active_attributes = deepcopy(obj.accepted_active_attributes)
        self.raw_data_mv_pos = deepcopy(obj.raw_data_mv_pos)
        self.p_matr = deepcopy(obj.p_matr)


class ANOVA_PlotData(PlotData):
    def __init__(self, active_ass=[], active_att=[], active_samp=[], tree_path=[], view_grid=False, view_legend=False):
	PlotData.__init__(self, active_ass, active_att, active_samp, tree_path, view_grid, view_legend)
	self.ANOVA_F = None
	self.ANOVA_p = None
	self.ANOVA_MSE = None
	self.F_signifcances = None
	self.p_matr = None

    def copy_data(self, obj): # copy from obj
        self.ANOVA_F = deepcopy(obj.ANOVA_F)
        self.ANOVA_p = deepcopy(obj.ANOVA_p)
	self.ANOVA_MSE = deepcopy(obj.ANOVA_MSE)
	self.F_signifcances = deepcopy(obj.F_signifcances)
        self.raw_data = deepcopy(obj.raw_data)
        self.raw_data_mv_pos = deepcopy(obj.raw_data_mv_pos)
        self.numeric_data = deepcopy(obj.numeric_data)
        self.p_matr = deepcopy(obj.p_matr)


class PCA_PlotData(PlotData):
    # Only used in Tucker1. One should rather use CollectionCalcPlotData, not this class
    # Tucker1 should also be updated to use CollectionCalcPlotData
    def __init__(self, active_ass=[], active_att=[], active_samp=[], tree_path=[], view_grid=False, view_legend=False):
	PlotData.__init__(self, active_ass, active_att, active_samp, tree_path, view_grid, view_legend)
	self.Scores = None
	self.Loadings = None
	self.E = None
	self.CorrLoadings = None
	self.selection = None
	self.newActiveAttributesList = None
	self.max_PCs = None
	self.numeric_data_tucker1matrix = None
	self.p_matr = None

    def copy_data(self, obj): # copy from obj
        # used for tucker1
	self.Scores = deepcopy(obj.Scores)
	self.Loadings = deepcopy(obj.Loadings)
	self.E = deepcopy(obj.E)
	self.CorrLoadings = deepcopy(obj.CorrLoadings)
	self.selection = deepcopy(obj.selection)
	self.newActiveAttributesList = deepcopy(obj.newActiveAttributesList)
	self.max_PCs = deepcopy(obj.max_PCs)
	self.raw_data = deepcopy(obj.raw_data)
	self.raw_data_mv_pos = deepcopy(obj.raw_data_mv_pos)
	self.numeric_data_tucker1matrix = deepcopy(obj.numeric_data_tucker1matrix)
	self.p_matr = deepcopy(obj.p_matr)




class CollectionCalcPlotData(PlotData):
    def __init__(self, active_ass=[], active_att=[], active_samp=[], tree_path=[], view_grid=False, view_legend=False):
	PlotData.__init__(self, active_ass, active_att, active_samp, tree_path, view_grid, view_legend)

	# data you want to keep for a possible new plot
	self.collection_calc_data = {} # for general purpose use (i.e. as Dict of variables)

    def copy_data(self, obj): # copy from obj
        self.collection_calc_data = deepcopy(obj.collection_calc_data)
        self.raw_data_mv_pos = deepcopy(obj.raw_data_mv_pos)