import pandas as pd
import matplotlib.pyplot as plt
from dash import Dash, dcc, html, dash_table, Input, Output

import src.visualization as viz
import src.config as config

N_MAX_PARENTS = 1

# List of available corpora
ls_projects = ["DT4H", "Baritone", "CHAGAS"]
ls_corpora = ["total", "distemist", "symptemist", "medprocner", "pharmaconer", "cardioccc_temu", "cardioccc_deepspanorm"]
ls_possible_parents = range(N_MAX_PARENTS + 1)
d_variables_list = {"DT4H": "https://docs.google.com/spreadsheets/d/1GM17jnZop0eHSYaWKccVhp4pdbX58IEuSLXsiYg4GUQ/edit?usp=sharing",
                    "CHAGAS": "https://docs.google.com/spreadsheets/d/1YDBJ-vSYBcZNSIaoF2UFPE_BJgcJXQ4eXrFEiwAr50k/edit?gid=0#gid=0"}

# Initialize the Dash app
app = Dash(__name__,
           url_base_pathname='/coverage/',
)

# Define the layout of the app
app.layout = html.Div(children=[
            config.TOP_DIV,
            
            html.Div(id='variables-link-container'),
            
            html.P("Select project", style=config.PAR_STYLE),
            dcc.Dropdown(
                id='project-dropdown',
                options=[{'label': project, 'value': project} for project in ls_projects],
                value=[],  # Default selected values
                multi=False
            ),
            
            html.P("Select the corpus in which you want to check the variables (total combines symptoms, diseases, drugs and procedures)",
                   style=config.PAR_STYLE),

            dcc.Dropdown(
                id='corpora-dropdown',
                options=[{'label': corpus, 'value': corpus} for corpus in ls_corpora],
                value="total",  # Default selected values
                multi=False
            ),

            html.P("By default, annotations can be more precise than the variables, so we can compare the variables with concept first N parents.\n Select the number of parents to consider for the comparison",
                   style=config.PAR_STYLE),
            html.P(),
            dcc.Dropdown(
                id='n_parents-dropdown',
                options=[{'label': f"{n_parents} parents", 'value': n_parents} for n_parents in ls_possible_parents],
                value=0,  # Default selected values
                multi=False
            ),


            # Wrapping the output components in dcc.Loading
            dcc.Loading(
                id="loading-1",
                type="circle",
                children=[
                    html.Div(id='graphs-container'),
                    html.Div(id='table-container')
                ])
        ])

@app.callback(
    Output('variables-link-container', 'children'),
    [Input('project-dropdown', 'value')]
)
def update_variables_link(selected_project):
    if not selected_project:
        return html.Div("Select a project to see its Variables List.", style={"color": "gray"})
    
    project_url = d_variables_list.get(selected_project, None)
    if not project_url:
        return html.Div("No Variables List available for the selected project.", style={"color": "red"})
    
    return html.A("Variables List", href=project_url, style={'color': 'blue', 'fontSize': '20px'})


# Callback to update the graphs and table based on selected corpora
@app.callback(
    [Output('graphs-container', 'children'),
     Output('table-container', 'children')],
    [Input('project-dropdown', 'value'),
     Input('corpora-dropdown', 'value'),
     Input('n_parents-dropdown', 'value')]
)
def update_content(selected_project, selected_corpora, selected_n_parents):
    import os
    if (not selected_project):
        return html.Div(), html.Div()
    elif (not os.path.exists(f"data/variables/{selected_project}/processed/variables.tsv")):
        warning_message = html.Div(
            "Warning: The required variables file is missing.",
            style={"color": "red", "fontWeight": "bold"}
        )
        return warning_message, html.Div() 

    if not selected_corpora:
        # Return empty components if no corpora are selected
        return html.Div(), html.Div()
        
    # Generate report data and figures based on the selected corpora
    df_out, ls_figures = viz.generate_report_table(selected_project, selected_corpora, n_parents=selected_n_parents)
    
    # Create the graph components
    graphs = [dcc.Graph(figure=fig) for fig in ls_figures]
    
    # Create the table component
    data_table = dash_table.DataTable(
        id='datatable-interactivity',
        columns=[{"name": i, "id": i} for i in df_out.columns],
        data=df_out.to_dict('records'),
        filter_action="native",
        sort_action="native",
        sort_mode="multi",
        column_selectable="single",
        row_selectable="multi",
        selected_columns=[], 
        selected_rows=[],
        page_action="native",
        page_current=0,
        page_size=20,
    )
    
    return graphs, data_table

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=8001)
    args = parser.parse_args()
    port = args.port

    app.run_server(port=port, debug=True)
