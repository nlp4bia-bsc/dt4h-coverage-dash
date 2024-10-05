import pandas as pd
import matplotlib.pyplot as plt
from dash import Dash, dcc, html, dash_table, Input, Output

import src.visualization as viz

N_MAX_PARENTS = 1

# List of available corpora
ls_corpora = ["total", "distemist", "symptemist", "medprocner", "pharmaconer", "cardioccc_temu", "cardioccc_deepspanorm"]
ls_possible_parents = range(N_MAX_PARENTS + 1)

# Initialize the Dash app
app = Dash(__name__,
           url_base_pathname='/coverage/',
)

# Define the layout of the app
app.layout = html.Div(children=[
    html.H1("Variable Coverage Analysis DT4H", style={'color': 'black', 'fontSize': '36px'}),
    html.A("Variables List", href="https://docs.google.com/spreadsheets/d/1GM17jnZop0eHSYaWKccVhp4pdbX58IEuSLXsiYg4GUQ/edit?usp=sharing", style={'color': 'blue', 'fontSize': '20px'}),
    html.P("Select the corpora to compare"),
    
    dcc.Dropdown(
        id='corpora-dropdown',
        options=[{'label': corpus, 'value': corpus} for corpus in ls_corpora],
        value=[],  # Default selected values
        multi=True
    ),

    html.P("Select the amount of parents you want to check (default 0)"),

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

# Callback to update the graphs and table based on selected corpora
@app.callback(
    [Output('graphs-container', 'children'),
     Output('table-container', 'children')],
    [Input('corpora-dropdown', 'value'),
     Input('n_parents-dropdown', 'value')]
)
def update_content(selected_corpora, selected_n_parents):

    if not selected_corpora:
        # Return empty components if no corpora are selected
        return html.Div(), html.Div()
    
    # Generate report data and figures based on the selected corpora
    df_out, ls_figures = viz.generate_report_table(selected_corpora, n_parents=selected_n_parents)
    
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
