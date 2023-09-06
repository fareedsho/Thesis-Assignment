from bokeh.models import ColumnDataSource, HoverTool, LassoSelectTool, CustomJS
from bokeh.plotting import figure, curdoc
from bokeh.layouts import column
import pandas as pd

csv_file_path = 'Synthetic_2_classifiers.csv'
df = pd.read_csv(csv_file_path)

df['Acorrect'] = df.apply(lambda row: row['label'] == row['classifierA_predicted_label'], axis=1)
df['Bcorrect'] = df.apply(lambda row: row['label'] == row['classifierB_predicted_label'], axis=1)
df['Onecorrect'] = df.apply(lambda row: (row['label'] == row['classifierA_predicted_label']) ^ (row['label'] == row['classifierB_predicted_label']), axis=1)
df['Bothwrong'] = df.apply(lambda row: row['label'] != row['classifierA_predicted_label'] and row['label'] != row['classifierB_predicted_label'], axis=1)
df['Bothcorrect'] = df.apply(lambda row: row['label'] == row['classifierA_predicted_label'] and row['label'] == row['classifierB_predicted_label'], axis=1)
df['classifier A - Correctly Predicted Dog'] = df.apply(lambda row: row['label'] == row['classifierA_predicted_label'] and row['label'] == 'dog', axis=1)
df['classifier A - Correctly Predicted Cat'] = df.apply(lambda row: row['label'] == row['classifierA_predicted_label'] and row['label'] == 'cat', axis=1)
df['classifier B - Correctly Predicted Dog'] = df.apply(lambda row: row['label'] == row['classifierB_predicted_label'] and row['label'] == 'dog', axis=1)
df['classifier B - Correctly Predicted Cat'] = df.apply(lambda row: row['label'] == row['classifierB_predicted_label'] and row['label'] == 'cat', axis=1)

def create_data_sources(df):
    data = {
        "Categories": [
            "classifier A - Correctly Predicted Dog",
            "classifier B - Correctly Predicted Dog",
            "classifier A - Correctly Predicted Cat",
            "classifier B - Correctly Predicted Cat",
        ],
        "Count": [
            (df['classifier A - Correctly Predicted Dog']).sum(),
            (df['classifier B - Correctly Predicted Dog']).sum(),
            (df['classifier A - Correctly Predicted Cat']).sum(),
            (df['classifier B - Correctly Predicted Cat']).sum(),
        ],
        "Bothcorrect": [
            ((df['classifier A - Correctly Predicted Dog'] & df['Bothcorrect']).sum()),
            ((df['classifier B - Correctly Predicted Dog'] & df['Bothcorrect']).sum()),
            ((df['classifier A - Correctly Predicted Cat'] & df['Bothcorrect']).sum()),
            ((df['classifier B - Correctly Predicted Cat'] & df['Bothcorrect']).sum()),
        ],
        "TotalCount": [
            (df['label'] == 'dog').sum(),
            (df['label'] == 'dog').sum(),
            (df['label'] == 'cat').sum(),
            (df['label'] == 'cat').sum(),
        ],
    }
    
    source = ColumnDataSource(data=data)
    
    total_count_source = ColumnDataSource(data=dict(
        x=["classifier A - Correctly Predicted Dog", ],
        TotalCount=[(df['label'] == 'dog').sum()],
        x1=["classifier B - Correctly Predicted Cat"],
        TotalCount1=[(df['label'] == 'cat').sum()]
    ))
    
    return source, total_count_source

def create_bar_chart(source, total_count_source):
    custom_ticks_dog = ["classifier A - Correctly Predicted Dog", "classifier B - Correctly Predicted Dog"]
    custom_ticks_cat = ["classifier A - Correctly Predicted Cat", "classifier B - Correctly Predicted Cat"]
    
    p_bar = figure(x_range=custom_ticks_dog + ["  "] + custom_ticks_cat, height=800, width=800,
                   title="Customized Vertical Bar Chart", toolbar_location=None, tools="")
    
    total_count_color = "red"
    total_count_color1 = "blue"
    
    p_bar.vbar(x="x", top="TotalCount", width=2.5, source=total_count_source, color=total_count_color, alpha=0.10, legend_label="Total Count")
    p_bar.vbar(x="x1", top="TotalCount1", width=2.5, source=total_count_source, color=total_count_color1, alpha=0.10, legend_label="Total Count")
    
    p_bar.vbar(x="Categories", top="Count", width=0.4, source=source,  color="#4D4D4D")
    p_bar.vbar(x="Categories", top="Bothcorrect", width=0.4, source=source, color="Black", alpha=1, legend_label="Bothcorrect")
    
    p_bar.yaxis.axis_label = "Count"
    p_bar.xaxis.major_label_orientation = "vertical"
    
    p_bar.legend.title = "Legend"
    p_bar.legend.label_text_font_size = "12px"
    
    return p_bar

def create_scatter_plot(df):
    scatter_source = ColumnDataSource(df)
    scatter_plot = figure(width=1000, height=1000, title="Scatter Plot", tools=[LassoSelectTool()])
    
    label_colors = {'dog': 'red', 'cat': 'blue'}
    
    for label, color in label_colors.items():
        label_df = df[df['label'] == label]
        scatter_plot.scatter('x', 'y', source=label_df, size=9, color=color, legend_label=label, fill_alpha=0.8)
    
    bothcorrect_df = df[df['Bothcorrect']]
    scatter_plot.scatter('x', 'y', source=bothcorrect_df, size=5, color='black', legend_label='Both Correct', fill_alpha=0.5)
    
    Onecorrect_df = df[df['Onecorrect']]
    scatter_plot.scatter('x', 'y', source=Onecorrect_df, size=5, color='gray', legend_label='Onecorrect', fill_alpha=0.3)
    
    bothwrong_df = df[df['Bothwrong']]
    scatter_plot.scatter('x', 'y', source=bothwrong_df, size=5, color='white', legend_label='Both Wrong', fill_alpha=0.14)
    
    scatter_plot.legend.title = 'Labels'
    scatter_plot.xaxis.axis_label = 'X-axis'
    scatter_plot.yaxis.axis_label = 'Y-axis'
    
    scatter_hover = HoverTool()
    scatter_hover.tooltips = [('X', '@x'), ('Y', '@y'), ('Label', '@label')]
    scatter_plot.add_tools(scatter_hover)
    
    return scatter_plot

def update_data(attrname, old_indices, new_indices):
    selected_indices = scatter_source.selected.indices
    
    selected_rows = []
    
    for i in selected_indices:
        selected_rows.append(i)
    
    filtered_data = {
        "Categories": [],
        "Count": [],
        "Bothcorrect": [],
        "label": [],
    }
    
    for i in selected_rows:
        row_index = i
        
        filtered_data["Categories"].append(source.data["Categories"][row_index])
        filtered_data["Count"].append(source.data["Count"][row_index])
        filtered_data["Bothcorrect"].append(source.data["Bothcorrect"][row_index])
        filtered_data["label"].append(source.data["label"][row_index])
    
    p_bar.data_source.data = filtered_data
    
    total_count_data = {
        "x": ["classifier A - Correctly Predicted Dog"],
        "TotalCount": [(filtered_data["label"].count('dog'))],
        "x1": ["classifier B - Correctly Predicted Cat"],
        "TotalCount1": [(filtered_data["label"].count('cat'))]
    }
    
    total_count_source.data = total_count_data
    
    p_bar.change.emit()
    total_count_source.change.emit()

source, total_count_source = create_data_sources(df)

p_bar = create_bar_chart(source, total_count_source)
scatter_plot = create_scatter_plot(df)

scatter_source = ColumnDataSource(df)
scatter_source.selected.js_on_change('indices', CustomJS(code="""
    var selected_indices = cb_obj.indices;
    
    var selected_rows = [];
    
    for (var i = 0; i < selected_indices.length; i++) {
        var index = selected_indices[i];
        selected_rows.push(index);
    }
    
    var filtered_data = {
        "Categories": [],
        "Count": [],
        "Bothcorrect": [],
        "label": [],
    };
    
    for (var i = 0; i < selected_rows.length; i++) {
        var row_index = selected_rows[i];
        
        filtered_data["Categories"].push(source.data["Categories"][row_index]);
        filtered_data["Count"].push(source.data["Count"][row_index]);
        filtered_data["Bothcorrect"].push(source.data["Bothcorrect"][row_index]);
        filtered_data["label"].push(source.data["label"][row_index]);
    }
    
    p_bar.data_source.data = filtered_data;
    
    var total_count_data = {
        "x": ["classifier A - Correctly Predicted Dog"],
        "TotalCount": [(filtered_data["label"].filter(label => label === 'dog')).length],
        "x1": ["classifier B - Correctly Predicted Cat"],
        "TotalCount1": [(filtered_data["label"].filter(label => label === 'cat')).length]
    };
    
    total_count_source.data = total_count_data;
    
    p_bar.change.emit();
    total_count_source.change.emit();
""", args={'p_bar': p_bar, 'total_count_source': total_count_source, 'source': source}))

layout = column(p_bar, scatter_plot)

curdoc().add_root(layout)