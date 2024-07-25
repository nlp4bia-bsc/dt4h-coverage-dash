import pandas as pd
def generate_df_codes(df_data, df_vars, debug=False):

    # Make copies of the dataframes to avoid modifying the originals
    df_data = df_data.copy()
    df_vars = df_vars.copy()

    df_data = process_composites(df_data, df_vars)

    df_code_ovr = df_vars[["ID", "name", "code", "term", "semantic_tag"]].merge(
                                                                            df_data[['code', 'span', 'semantic_rel']].reset_index(), 
                                                                            on='code', 
                                                                            how='left'
                                                                        ).fillna("NOT_FOUND")

    # assert (df_code_ovr["semantic_rel"] == "COMPOSITE").sum() > 0, "NO COMPOSITES FOUND"

    # Group by 'code', 'span', and 'semantic_rel', then count occurrences
    df_code_ovr = df_code_ovr.groupby(['ID', 'name', 'code', 'span', 'term', 'semantic_rel', 'semantic_tag']).size().reset_index(name='count').sort_values(by="count", ascending=False)

    # Set count to 0 for entries with 'span' marked as "NOT_FOUND"
    df_code_ovr.loc[df_code_ovr.span == "NOT_FOUND", "count"] = 0

    # Rename columns for clarity
    df_code_ovr.columns = ['ID', 'name', 'code', 'span', 'term', 'semantic_rel', 'semantic_tag', 'count']

    
    df_code_ovr["found"] = df_code_ovr["span"] != "NOT_FOUND"

    # Include column of count by code
    df_code_count = df_code_ovr.groupby(["ID"]).aggregate({"count":"sum"}).reset_index()
    df_count_group = df_code_count.groupby("ID").aggregate({"count":"sum"}).reset_index()
    df_code_ovr = df_code_ovr.merge(df_count_group, on="ID", suffixes=('', '_ID'))

    # Include columns of count by semantic_rel
    df_code_rel = df_code_ovr.groupby(["ID", "semantic_rel"]).aggregate({"count":"sum"}).reset_index()
    df_code_rel = df_code_rel.pivot(index="ID", columns="semantic_rel", values="count").fillna(0).reset_index()
    df_code_ovr = df_code_ovr.merge(df_code_rel, on="ID").sort_values(by="count", ascending=False)

    if debug:
        # Print the shape of the resulting dataframe
        print("Shape:", df_code_ovr.shape)
        print("Unique codes:", df_code_ovr["ID"].nunique())
        # Print the number of codes not found (count is 0)
        print("Codes not found:", df_code_ovr[~df_code_ovr["found"]].code.nunique())

        # Print the top 10 codes by count in markdown format
        print(df_code_ovr.head().to_markdown(), "\n")

        # Print the bottom 10 codes by count in markdown format
        print(df_code_ovr.tail().to_markdown(), "\n")

    return df_code_ovr


def process_composites(df, df_vars):
    '''
    Function to extract composite codes. Get the first code that is in the list of variables.
    '''

    df_data = df.copy()
    df_vars = df_vars.copy()

    # Get the unique codes from the variables dataframe to process the composites
    ls_var_codes = df_vars["code"].drop_duplicates().tolist()

    # Merge df_variables with df_symptemist on 'code', filling missing values with "NOT_FOUND"
    df_data_comp = df_data[df_data["semantic_rel"] == "COMPOSITE"].copy()
    df_data_comp["code_list"] = df_data_comp["code"].str.split("+")
    df_data_comp["var_code"] = df_data_comp["code_list"].apply(lambda code: [c for c in code if c in ls_var_codes][0] if any(c in ls_var_codes for c in code) else code[0])
    df_data_comp["var_code"] = df_data_comp["var_code"].astype(str)
    df_data_comp.code = df_data_comp.var_code

    # Process composites
    df_data_no_comp = df_data[df_data["semantic_rel"] != "COMPOSITE"].copy()

    # Once composites have a single code instead of a list, concatenate the dataframes
    df_data = pd.concat([df_data_no_comp, df_data_comp], ignore_index=True)

    return df_data
