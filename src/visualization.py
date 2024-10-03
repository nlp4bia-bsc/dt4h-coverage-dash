import pandas as pd
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.graph_objects as go

from src.preprocessing import generate_df_codes


def generate_report_table(ls_corpora, n_parents):
    df_report = pd.DataFrame()
    ls_figures = []
    for corpus in ls_corpora:
        _, output = report_corpus(corpus, show=False, n_parents=n_parents)
        df_report_i = output[0]
        figures = output[1:]
        df_report_i["corpus"] = corpus
        df_report = pd.concat([df_report, df_report_i])

        ls_figures.extend(figures)

    # show the count_ID, total_mentions and total_ratio for each corpus using ID as index
    df_out = df_report.pivot(index=["ID", "name", "term", "label", "label_corpus"], columns="corpus", values=["count_ID", "mentions", "ratio"])
    df_out.columns = [f"{col}_{sub}" for col, sub in df_out.columns]
    df_out = df_out.sort_values(by=list(df_out.columns)[0], ascending=False)

    df_out = df_out.reset_index()

    return df_out, ls_figures

def report_corpus(corpus, n_parents, show=True, debug=False):
    if n_parents == 0:
        DATA = f'data/processed/{corpus}.tsv'
    else:
        DATA = f'data/processed/{n_parents}_parents/{corpus}.tsv'

    DATA_VAR = 'data/variables/processed/variables.tsv'

    print(f"Loading data from {DATA}")
    df_data = pd.read_csv(DATA, sep='\t', dtype={'code': str})
    df_var = pd.read_csv(DATA_VAR, sep='\t', dtype={'code': str})

    df_code_ovr = generate_df_codes(df_data=df_data, df_vars=df_var, n_parents=n_parents, debug=debug)

    output = plot_code_distribution(df_code_ovr, corpus=corpus, show=show)
    return df_code_ovr, output

def plot_code_distribution(df, corpus, show=True):

   #### Variables ####
    color_sequence = [ '#1EE132', '#9E8C88']

    #### Data Preparation for Visualization ####
    # Filter the dataframe to exclude rows where 'span' is "NOT_FOUND"
    df = df.copy()
    # Create a new column with the ID, name, and term concatenated for better visualization
    df["ID+term"] = df["ID"] + "-" + df["name"] + " (" + df["term"] + ")"

    # Dataframe to plot the distribution of found variables by semantic tag
    df_sem_tag = df.drop_duplicates(subset=["ID", "label", "found"]).copy()
    df_sem_tag["found"] = df_sem_tag["found"].replace({True: "Found", False: "Not Found"})        # Avoid True/False in the plot
    df_sem_tag = df_sem_tag.groupby(["label", "found"]).size().reset_index(name="count")   # Count the occurrences by semantic tag and found/not found

    # Calculate the total counts by semantic tag to compute percentages and merge the dataframes
    total_counts = df_sem_tag.groupby("label").aggregate({"count":"sum"})\
                                .reset_index()\
                                .rename(columns={"count":"total"})
    df_sem_tag = df_sem_tag.merge(total_counts, on="label")
    df_sem_tag["percentage"] = df_sem_tag["count"] / df_sem_tag["total"]                          # Calculate the percentage of found/not found by semantic tag
    df_sem_tag = df_sem_tag.sort_values(by=["found", "total"], ascending=[True, False])           # Sort the dataframe to display the highest counts first

    # Dataframe to plot the statistics of the found variables
    df_found = df.loc[(df["span"] != "NOT_FOUND"), :].copy()
    df_n_founds = df[["ID", "found"]].drop_duplicates()
    df_n_founds["found"] = df_n_founds["found"].replace({True: "Found", False: "Not Found"})

    # Dataframe to plot the distribution of semantic relationships
    ls_semantic_rel = df["semantic_rel"].unique().tolist()                                        # Get the unique semantic relationships and semantic tags
    sel_cols = ["ID+term"] + ls_semantic_rel + ["count_ID"]
    df_count_rel = df_found[sel_cols].melt(id_vars=["ID+term", "count_ID"], var_name="semantic_rel", value_name="count")\
                                     .drop_duplicates()

    #### Visualization ####
    # 1. Create a bar chart for the distribution of found variables by semantic tag
    fig_top = px.bar(df_sem_tag,
                        y='label', x='count', color='found',
                        color_discrete_sequence=color_sequence,
                        orientation='h',
                        barmode='stack',  # Add this line to stack the bars
                        title='Coverage by Semantic Tag',
                        labels={'count': 'Count', 'label': 'Semantic Tag', 'text': 'Percentage'},
                        text=(df_sem_tag["percentage"] * 100).round(2).astype(str) + "%")  # Display percentages with %
    
    # Add an annotation below the plot
    fig_top.add_annotation(
        text="Figure: Distribution of found codes by NLP4BIA semantic tag",
        xref="paper", yref="paper",  # Coordinates refer to the entire paper space
        x=0, y=-0.3,  # Position the annotation below the plot
        showarrow=False,
        font=dict(size=18, color="black"),
        align="left",

    )

    # Reverse the order of the y-axis to display the highest counts at the top
    fig_top.update_layout(yaxis=dict(autorange="reversed"), margin=dict(t=50, b=100))

    
    fig_top.update_layout(
        title_text=f"{corpus.upper()}: Overview of Data Attributes",
        title_font_size=24,  # Adjust the size as needed
        title_font_family="Arial",  # You can change the font if you prefer
        title_font_color="black",  # Adjust the color as needed
        title_x=0.5,  # Center the title horizontally
        title_xanchor='center'  # Ensure the title is centered
    )

    # 2. Create pie charts for the distribution of found variables, semantic tags, and semantic relationships
    # Create the pie charts
    fig01 = px.pie(df_n_founds, names='found', title='Found Variables')
    fig01.update_traces(textinfo='label+percent+value')

    fig02 = px.pie(df_found.drop_duplicates(subset=["ID"]), names='label', title='Semantic Tag Distribution of Found Codes')
    fig02.update_traces(textinfo='label+percent+value')

    fig03 = px.pie(df_found, names='semantic_rel', title='Semantic Relationship Distribution')
    fig03.update_traces(textinfo='label+percent+value')

    # Create a subplot layout with 1 row and 2 columns
    fig0 = make_subplots(rows=1, cols=3, subplot_titles=("Found Variables", "Semantic Tag Distribution of Found Codes", "Semantic Relationship Distribution (Total Mentions)"),
                            specs=[[{"type": "pie"}, {"type":"pie"}, {"type":"pie"}]])

    # Add the pie charts to the subplots
    fig0.add_trace(fig01.data[0], row=1, col=1)
    fig0.add_trace(fig02.data[0], row=1, col=2)
    fig0.add_trace(fig03.data[0], row=1, col=3)

    # Update the layout to adjust the title and other settings
    fig0.update_layout(title_text="Distribution of Semantic Relationships and Found Codes", showlegend=False,
                      height=600)

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
    # .drop_duplicates(subset=["code", "span", "label"])
    # Create a bar chart for all the found codes by count
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

    df_report = df[["ID", "name", "term", "label", "label_corpus", "count_ID"]].drop_duplicates().sort_values(by="ID")
    df_report["mentions"] = df_report["count_ID"].sum()
    df_report["ratio"] = df_report["count_ID"]/df_report["count_ID"].sum()
    df_report.fillna(0, inplace=True)

    if show:
        fig_top.show()
        fig0.show()
        fig1.show()
        fig2.show()
        # figtab.show()

    return df_report, fig_top, fig0, fig1, fig2 #, figtab


