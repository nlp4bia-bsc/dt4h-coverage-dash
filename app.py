import pandas as pd
import matplotlib.pyplot as plt

from dash import Dash, dcc, html, dash_table, Input, Output
import src.visualization as viz

# List of available corpora
ls_corpora = ["distemist", "symptemist", "medprocner"]

# Initialize the Dash app
app = Dash(__name__,
           url_base_pathname='/coverage/',
)

# Define the layout of the app
app.layout = html.Div([
    html.H1("Variable Coverage Analysis DT4H"),
    html.A("Variables List", href="https://docs.google.com/spreadsheets/d/1GM17jnZop0eHSYaWKccVhp4pdbX58IEuSLXsiYg4GUQ/edit?gid=0#gid=0"),
    html.P("Select the corpora to compare"),
    
    dcc.Dropdown(
        id='corpora-dropdown',
        options=[{'label': corpus, 'value': corpus} for corpus in ls_corpora],
        value=[],  # Default selected values
        multi=True
    ),

    html.Div(id='graphs-container'),
    html.Div(id='table-container')
])

# Callback to update the graphs and table based on selected corpora
@app.callback(
    [Output('graphs-container', 'children'),
     Output('table-container', 'children')],
    [Input('corpora-dropdown', 'value')]
)
def update_content(selected_corpora):
    if not selected_corpora:
        # Return empty components if no corpora are selected
        return html.Div(), html.Div()
    
    # Generate report data and figures based on the selected corpora
    df_out, ls_figures = viz.generate_report_table(selected_corpora)
    
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

    app.run_server(port=port)
