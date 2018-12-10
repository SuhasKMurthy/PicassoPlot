from bokeh.plotting import figure, show, output_file
from bokeh.palettes import cividis
from bokeh.models import ColumnDataSource, Legend

import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import Patch
from matplotlib import cm
from mpl_toolkits.mplot3d import Axes3D

import pandas as pd
import numpy as np



import math

# def plot_bokeh(df):
#     # give each distinct plan an ID
#     df['plan_id'] = df.groupby(['plan']).ngroup()
#     # get the count associated with each plan ID
#     plan_sizes = df.groupby(['plan']).size()
#
#     num_distinct_plans = df['plan_id'].nunique()
#     # create a list of colors based on the number of distinct plans
#     cols = cividis(num_distinct_plans)
#     # populate other columns in the dataframe based on this. these are useful plot variables
#     df['color'] = df.apply(lambda row: cols[row.plan_id], axis=1)
#     df['coverage'] = df.apply(lambda row: "{:.2f}".format((plan_sizes[row.plan_id] * 100) / len(df.index)), axis=1)
#
#     p = figure(title="Plan Diagram", x_axis_label='Supplier', y_axis_label='Lineitem')
#
#     legend_it = []
#
#     for col in cols:
#         df_temp = df[df['color'] == col]
#         coverage = df_temp['coverage'].iloc[0]
#         ds = ColumnDataSource(df_temp)
#         rec = p.rect(x='s_acctbal_partition', y='l_quantity_partition', width=1, height=1, source=ds,
#            color='color')
#         legend_it.append((coverage, [rec]))
#
#     legend = Legend(items=legend_it, location=(0, 60))
#     p.add_layout(legend, 'right')
#
#     output_file("plan_diagram.html", title="plan_diagram.py example")
#     show(p)

def plot(df, labels):
    x_label, y_label = labels
    # give each distinct plan an ID
    df['plan_id'] = df.groupby(['plan']).ngroup()
    # get the count associated with each plan ID
    plan_sizes = df.groupby(['plan']).size()

    num_distinct_plans = df['plan_id'].nunique()
    # create a list of colors based on the number of distinct plans
    # cols = cividis(num_distinct_plans)
    cols = np.random.rand ( num_distinct_plans, 3)
    # populate other columns in the dataframe based on this. these are useful plot variables
    df['color'] = df.apply(lambda row: cols[row.plan_id], axis=1)
    #df['coverage'] = df.apply(lambda row: "{:.2f}".format((plan_sizes[row.plan_id] * 100) / len(df.index)), axis=1)

    grid_size = math.sqrt(len(df.index))

    fig = plt.figure(figsize=plt.figaspect(0.5))

    ax = fig.add_subplot(1, 2, 1)

    ax.set_xlim([1, grid_size+1])
    ax.set_ylim([1, grid_size+1])
    ax.set_xlabel(x_label)
    ax.set_ylabel(y_label)
    ax.set_title("Plan Diagram")

    for index, row in df.iterrows():
        rect = patches.Rectangle((int(row['foo']), int(row['bar'])), 1, 1, edgecolor='r', fc=row['color'])
        ax.add_patch(rect)

    id_cov = []
    for i in range(num_distinct_plans):
	id_cov.append([i, "{:.2f}".format( plan_sizes[i]*100.0/len(df.index) ) ])
    
    id_cov_sorted = sorted(id_cov, key = lambda x:x[1], reverse=True)
    
    legend_it = []
    for pid, coverage in id_cov_sorted:
	leg_item = Patch(facecolor=cols[pid], edgecolor='r', label=str(coverage))
	legend_it.append(leg_item)
    #for col in cols:
    #    df_temp = df[df['color'] == col]
    #    coverage = df_temp['coverage'].iloc[0]
    #    leg_item = Patch(facecolor=col, edgecolor='r', label=str(coverage))
    #    legend_it.append(leg_item)

    ax.legend(handles=legend_it, bbox_to_anchor=(1, 0.5), loc='center left')

    ax2 = fig.add_subplot(1, 2, 2, projection='3d')
    max_cost = df['cost'].max()
    df['cost'] = df['cost']/max_cost

    ax2.set_xlim([0, grid_size + 1])
    ax2.set_ylim([0, grid_size + 1])
    ax2.set_zlim([0, 1])
    ax2.set_xlabel(x_label)
    ax2.set_ylabel(y_label)
    ax2.set_zlabel('Normalized Cost')
    ax2.set_title('Cost Diagram')

    ax2 = fig.gca(projection='3d')
    x = np.arange(1, int(grid_size)+1)
    y = np.arange(1, int(grid_size)+1)
    X,Y = np.meshgrid(x,y)
    z = df['cost'].values.reshape((int(grid_size),int(grid_size)))
    ax2.plot_surface(Y,X,z,rstride=1, cstride=1, cmap=cm.coolwarm)

    plt.show()
