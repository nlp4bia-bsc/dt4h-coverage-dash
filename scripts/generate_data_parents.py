import pandas as pd
import os
import sys
sys.path.append(os.getcwd())

from src.ontology.SnomedCT import SnomedCT

N_PARENTS = 1
DATA_FOLDER = "data/processed/"
OUTPUT_FOLDER = os.path.join(DATA_FOLDER, f"{N_PARENTS}_parents")

os.makedirs(OUTPUT_FOLDER, exist_ok=True)

relationship_file = "/home/abecerra/Documents/SnomedCT_InternationalRF2_PRODUCTION_20240901T120000Z/Full/Terminology/sct2_Relationship_Full_INT_20240901.txt"

sct = SnomedCT(file_name_rel=relationship_file, root_concept_code = "138875005", relation_types=["116680003"])

ls_corpora = ["total", "distemist", "symptemist", "medprocner", "pharmaconer"]

for corpus in ls_corpora:
    DATA = f'data/processed/{corpus}.tsv'

    df_data = pd.read_csv(DATA, sep='\t', dtype={'code': str})
    df_data["code_wp"] = df_data["code"].apply(lambda x: sct.get_parents(x))
    df_data_1p = df_data.explode(column="code_wp")

    df_data_1p.to_csv(os.path.join(OUTPUT_FOLDER, f"{corpus}.tsv"), index=False, sep="\t")
