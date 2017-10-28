"""
vislualize shows all targets and the starting point in a scatter plot
"""
from loon import load
from bokeh.plotting import figure, show

# load data
_, _, _, STARTING_CELL, TARGET_CELLS, WIND = load(
    "loon_r70_c300_a8_radius7_saturation_250.in")

# prepare data
ROWS = [cell["pos"].r for cell in TARGET_CELLS]
COLUMNS = [cell["pos"].c for cell in TARGET_CELLS]

# create plot
PLT = figure(title="target cells", x_axis_label='x', y_axis_label='y')
PLT.sizing_mode = 'stretch_both'

# render data as circles
PLT.circle(COLUMNS, ROWS, size=5, color="navy", alpha=0.5, legend="Target")
PLT.circle(STARTING_CELL.c, STARTING_CELL.r, size=20,
           color="green", alpha=0.5, legend="Start")
PLT.legend.location = "bottom_right"

# show the results
show(PLT)
