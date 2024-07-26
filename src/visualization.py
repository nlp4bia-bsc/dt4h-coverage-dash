import pandas as pd
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.graph_objects as go

from src.preprocessing import generate_df_codes


def generate_report_table(ls_corpora):
    df_report = pd.DataFrame()
    ls_figures = []
    for corpus in ls_corpora:
        _, output = report_corpus(corpus, show=False)
        df_report_i = output[0]
        figures = output[1:]
        df_report_i["corpus"] = corpus
        df_report = pd.concat([df_report, df_report_i])

        ls_figures.extend(figures)

    # show the count_ID, total_mentions and total_ratio for each corpus using ID as index
    df_out = df_report.pivot(index=["ID", "name", "term"], columns="corpus", values=["count_ID", "total_mentions", "total_ratio"])
    df_out.columns = [f"{col}_{sub}" for col, sub in df_out.columns]
    df_out = df_out.sort_values(by=list(df_out.columns)[0], ascending=False)

    df_out = df_out.reset_index()

    return df_out, ls_figures

def report_corpus(corpus, show=True, debug=False):
    DATA = f'data/processed/{corpus}.tsv'
    DATA_VAR = 'data/variables/processed/variables.tsv'

    print(f"Loading data from {DATA}")
    df_data = pd.read_csv(DATA, sep='\t', dtype={'code': str})
    df_var = pd.read_csv(DATA_VAR, sep='\t', dtype={'code': str})

    df_code_ovr = generate_df_codes(df_data=df_data, df_vars=df_var, debug=debug)

    output = plot_code_distribution(df_code_ovr, corpus=corpus, show=show)
    return df_code_ovr, output

def plot_code_distribution(df, corpus=None, show=True):

    ls_semantic_rel = df["semantic_rel"].unique().tolist()
    # Filter the dataframe to exclude rows where 'span' is "NOT_FOUND"
    df = df.copy()
    df["ID+term"] = df["ID"] + "-" + df["name"] + " (" + df["term"] + ")"
    df_found = df.loc[(df["span"] != "NOT_FOUND"), :].copy()
    df_count_rel = df_found[["ID+term"] + ls_semantic_rel + ["count_ID"]].melt(id_vars=["ID+term", "count_ID"], var_name="semantic_rel", value_name="count").drop_duplicates()
    df_n_founds = df[["ID", "found"]].drop_duplicates()

    # Assuming df_found and df_n_founds are already defined

    # Create the pie charts

    fig01 = px.pie(df_n_founds, names='found', title='Found Variables')
    fig01.update_traces(textinfo='label+percent+value')

    fig02 = px.pie(df_found.drop_duplicates(subset=["ID"]), names='semantic_tag', title='Semantic Tag Distribution')
    fig02.update_traces(textinfo='label+percent+value')

    fig03 = px.pie(df_found, names='semantic_rel', title='Semantic Relationship Distribution')
    fig03.update_traces(textinfo='label+percent+value')


    # Create a subplot layout with 1 row and 2 columns
    fig0 = make_subplots(rows=1, cols=3, subplot_titles=("Found Variables", "Semantic Tag Distribution", "Semantic Relationship Distribution (Total Mentions)"),
                            specs=[[{"type": "pie"}] * 3])
    

    # Add the pie charts to the subplots
    fig0.add_trace(fig01.data[0], row=1, col=1)
    fig0.add_trace(fig02.data[0], row=1, col=2)
    fig0.add_trace(fig03.data[0], row=1, col=3)

    # Update the layout to adjust the title and other settings
    fig0.update_layout(title_text="Distribution of Semantic Relationships and Found Codes", showlegend=False,
                      height=600)
    
    if corpus is not None:
        fig0.update_layout(
            title_text=f"{corpus.upper()}: Overview of Data Attributes",
            title_font_size=24,  # Adjust the size as needed
            title_font_family="Arial",  # You can change the font if you prefer
            title_font_color="black",  # Adjust the color as needed
            title_x=0.5,  # Center the title horizontally
            title_xanchor='center'  # Ensure the title is centered
        )

    # print(df_count_rel[df_count_rel.term.str.contains("Diabetes")].to_markdown())
    # Assuming df_aggregated is correctly aggregated data
    n_terms = df_found["ID+term"].nunique()
    n_show = 25

    fig1 = px.bar(df_count_rel.sort_values(by="count_ID", ascending=True),
                y='ID+term', x='count', color='semantic_rel', 
                title=f'Codes by Semantic Relationship [Variable Name (SNOMED term)] <Zoom {n_show} out of {n_terms} terms; zoom out to see all>',
                labels={'count': 'Count', 'ID+term': 'Name'},
                orientation='h')
    
    fig1.update_layout(
                           height=600,
                            yaxis=dict(
                                        range=[n_terms - n_show, n_terms],
                                        tickmode='linear',
                                        dtick=1,
                                    )
                                    )
    
    # Create a bar chart for all the found codes by count
    # ls_IDs = df_found.sort_values(by="count_ID", ascending=False)["ID+term"].unique().tolist()[:25]
    fig2 = px.bar(df_found.sort_values(by="count_ID", ascending=True),
                y='ID+term', x='count', color='span', title=f'Codes Distribution [Variable Name (SNOMED term)] <Zoom {n_show} out of {n_terms} terms; zoom out to see all>',
                labels={'count': 'Count', 'ID+term': 'Name'},
                orientation='h')
    
    fig2.update_layout(showlegend=False, 
                           height=600,
                            yaxis=dict(
                                        range=[n_terms - n_show, n_terms],
                                        tickmode='linear',
                                        dtick=1,
                                    )
                                    )

    df_report = df[["ID", "name", "term", "count_ID"]].drop_duplicates().sort_values(by="ID")
    df_report["total_mentions"] = df_report["count_ID"].sum()
    df_report["total_ratio"] = df_report["count_ID"]/df_report["count_ID"].sum()
    df_report.fillna(0, inplace=True)

    # # Create a Plotly Table
    # figtab = go.Figure(data=[go.Table(
    #     header=dict(values=list(df_report.columns),
    #                 fill_color='paleturquoise',
    #                 align='left'),
    #     cells=dict(values=[df_report[col] for col in df_report.columns],
    #             fill_color='lavender',
    #             align='left'))
    # ])

    # # Update layout
    # figtab.update_layout(
    #     title_text="Data Table",
    #     title_x=0.5
    # )

    if show:
        fig0.show()
        fig1.show()
        fig2.show()
        # figtab.show()

    return df_report, fig0, fig1, fig2 #, figtab


