from bokeh.plotting import figure, show, output_file
from bokeh.palettes import cividis
from bokeh.models import ColumnDataSource, Legend
import pandas as pd

def plot(df):
    # give each distinct plan an ID
    df['plan_id'] = df.groupby(['plan']).ngroup()
    # get the count associated with each plan ID
    plan_sizes = df.groupby(['plan']).size()

    num_distinct_plans = df['plan_id'].nunique()
    # create a list of colors based on the number of distinct plans
    cols = cividis(num_distinct_plans)
    # populate other columns in the dataframe based on this. these are useful plot variables
    df['color'] = df.apply(lambda row: cols[row.plan_id], axis=1)
    df['coverage'] = df.apply(lambda row: "{:.2f}".format((plan_sizes[row.plan_id] * 100) / len(df.index)), axis=1)

    p = figure(title="Plan Diagram", x_axis_label='Supplier', y_axis_label='Lineitem')

    legend_it = []

    for col in cols:
        df_temp = df[df['color'] == col]
        coverage = df_temp['coverage'].iloc[0]
        ds = ColumnDataSource(df_temp)
        rec = p.rect(x='s_acctbal_partition', y='l_quantity_partition', width=1, height=1, source=ds,
           color='color')
        legend_it.append((coverage, [rec]))

    legend = Legend(items=legend_it, location=(0, 60))
    p.add_layout(legend, 'right')

    output_file("plan_diagram.html", title="plan_diagram.py example")
    show(p)