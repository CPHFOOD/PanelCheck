
from numpy import *
from matplotlib import *
from matplotlib.cm import *
from matplotlib.colors import *

# custom colormap
color_dict = {'red': ((0.0, 0.0, 0.0),
		 (0.5, 0.5, 0.5),
		 (1.0, 1.0, 1.0)),
       'green': ((0.0, 0.0, 0.0),
		 (0.5, 0.5, 0.5),
		 (1.0, 1.0, 1.0)),
	'blue': ((0.0, 0.0, 0.0),
		 (0.5, 0.5, 0.5),
		 (1.0, 1.0, 1.0))}

colormap = LinearSegmentedColormap('bw', color_dict, 256)

N = 101
x = arange(0, N)           
# set color map mappable
c_map = ScalarMappable(cmap=colormap)

print colormap(0.666)


