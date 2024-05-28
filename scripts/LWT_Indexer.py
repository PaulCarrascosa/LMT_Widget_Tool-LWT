import sys
sys.path.insert(1, "../")

from IPython.display import display
from ipywidgets import *
from lmtanalysis.FileUtil import getCsvFileToProcess
import ast
import pandas as pd
import numpy as np
import warnings

warnings.filterwarnings('ignore')

event_options_index = {
    '1': ["Move", "Move isolated", "Rearing", "Rear isolated", "Stop isolated",
          "WallJump", "SAP", "Huddling", "WaterPoint", "Distance"],
    '2': ["Contact", "Oral-oral Contact", "Oral-genital Contact", "Side by side Contact",
          "Side by side Contact, opposite way", "Social approach", "Social escape",
          "Approach contact", "Approach rear", "Break contact", "Get away",
          "FollowZone Isolated", "Train2", "Group2"],
    '3': ["Group3"],
    '4': ["Group4", "Nest4"]
}

def save_csv(df, file_name):
    file_name_with_extension = file_name + ".csv"
    df.to_csv(file_name_with_extension, index=False)
    print("CSV file saved successfully.")

def create_new_column(b, df, cage_dropdown, rfida_select):
    selected_cage = cage_dropdown.value

    # Obtenir les valeurs sélectionnées dans le widget SelectMultiple
    selected_rfida_values = [rfida.split()[0] for rfida in rfida_select.value]

    # Créer la colonne 'LMT-indexer' si elle n'existe pas déjà
    if 'LMT-indexer' not in df.columns:
        df['LMT-indexer'] = ''

    # Assigner les valeurs sélectionnées sous forme de liste uniquement aux lignes correspondant à la cage sélectionnée
    for index, rfida_value in df.loc[df['Cage'] == selected_cage].iterrows():
        df.at[index, 'LMT-indexer'] = [int(rfida) for rfida in selected_rfida_values]

def update_rfida_options(change, df, rfida_select):
    selected_cage = change.new
    rfida_select.options = get_rfida_values(selected_cage, df)

def get_rfida_values(selected_cage, df):
    if selected_cage:
        rfida_values = df[df['Cage'] == selected_cage]['RFidA'].unique()
        genoa_values = df[df['Cage'] == selected_cage]['GenoA']
        rfida_options = [f"{rfid} ({genoa})" for rfid, genoa in zip(rfida_values, genoa_values)]
        return rfida_options
    else:
        return []


def Create_index_ED(df):
    # Conversion de 'LMT-indexer' en listes Python, si nécessaire
    if isinstance(df['LMT-indexer'].iloc[0], str):
        df['LMT-indexer'] = df['LMT-indexer'].apply(ast.literal_eval)

    # Identifier les lignes où 'RFidA' est présent dans 'LMT-indexer'
    df['is_RFidA_in_LMT_indexer'] = df.apply(lambda row: row['RFidA'] in row['LMT-indexer'], axis=1)

    # Traitement pour la clé '1'
    events_key_1 = event_options_index['1']
    df_filtered = df[df['name'].isin(events_key_1)]
    grouped = df_filtered[df_filtered['is_RFidA_in_LMT_indexer']].groupby(['Cage', 'Injection', 'name', 'Bin'])
    mean_totalLength = grouped['totalLength'].mean().reset_index(name='mean_index_ED')
    # df['normalized_index_ED'] = df['totalLength'] / df['mean_index_ED'].replace(0, pd.NA)
    df = df.merge(mean_totalLength, on=['Cage', 'Injection', 'name', 'Bin'], how='left')

    # Traitement pour la clé '2' ajusté selon la nouvelle approche
    # Préparation du DataFrame pour stocker les résultats pour la clé '2'
    sum_results_df = pd.DataFrame()

    events_to_process = event_options_index['2'] + event_options_index['3'] + event_options_index['4']

    for event in events_to_process:
        event_df = df[df['name'] == event]
        event_sum_df = event_df.groupby(['Cage', 'Injection', 'Bin', 'RFidA'])['totalLength'].sum().reset_index(
            name='sum_index_ED')
        event_sum_df['event_name'] = event
        sum_results_df = pd.concat([sum_results_df, event_sum_df], ignore_index=True)

    df['event_name'] = df['name']
    df = df.merge(sum_results_df, on=['Cage', 'Injection', 'Bin', 'RFidA', 'event_name'], how='left')
    df.drop('event_name', axis=1, inplace=True)

    # # Étape 1: Concaténer les listes d'événements pour les clés '2', '3', '4'
    # events_to_process = event_options_index['2'] + event_options_index['3'] + event_options_index['4']

    # Étape 2 et 3: Filtrer et calculer la moyenne de 'sum_index_ED'
    df_events_filtered = df[df['is_RFidA_in_LMT_indexer'] & df['name'].isin(events_to_process)]
    mean_values = df_events_filtered.groupby(['Cage', 'Injection', 'Bin', 'name'])['sum_index_ED'].mean().reset_index(
        name='mean_sum_index_ED')

    # Fusionner les moyennes calculées avec le DataFrame original
    df = pd.merge(df, mean_values, on=['Cage', 'Injection', 'Bin', 'name'], how='left')

    # Étape 4: Calculer la moyenne normalisée
    df['LMT_Index_ED'] = df.apply(
        lambda row: row['sum_index_ED'] / row['mean_sum_index_ED']
        if (row['name'] in events_to_process and
            row['mean_sum_index_ED'] and row['mean_sum_index_ED'] != 0) else np.nan,
        axis=1
    )

    # Calculez le ratio de 'totalLength' sur 'mean_totalLength' pour les événements de la clé '1'
    df['normalized_index_ED'] = df.apply(lambda row: row['totalLength'] / row['mean_index_ED']
    if not pd.isnull(row['mean_index_ED']) and row['mean_index_ED'] != 0 else np.nan, axis=1)

    # Maintenant, combinez les colonnes 'normalized_index_ED' et 'LMT_Index_ED' pour garder toutes les valeurs normalisées
    # Les valeurs de 'normalized_index_ED' remplacent les NaN dans 'LMT_Index_ED'
    df['LMT_Index_ED'] = df['LMT_Index_ED'].combine_first(df['normalized_index_ED'])

    # # Supprimez les colonnes qui ne sont plus nécessaires
    # df.drop(['normalized_index_ED', 'LMT-indexer', 'is_RFidA_in_LMT_indexer', 'mean_index_ED', 'sum_index_ED', 'mean_sum_index_ED'], axis=1, inplace=True)

    # Supprimez les colonnes qui ne sont plus nécessaires
    df.drop(['normalized_index_ED', 'mean_index_ED', 'sum_index_ED', 'mean_sum_index_ED'], axis=1, inplace=True)

    return df


def Create_index_NOE(df):
    # Conversion de 'LMT-indexer' en listes Python, si nécessaire
    if isinstance(df['LMT-indexer'].iloc[0], str):
        df['LMT-indexer'] = df['LMT-indexer'].apply(ast.literal_eval)

    # Identifier les lignes où 'RFidA' est présent dans 'LMT-indexer'
    df['is_RFidA_in_LMT_indexer'] = df.apply(lambda row: row['RFidA'] in row['LMT-indexer'], axis=1)

    # Dictionnaire des options d'événements
    event_options_index = {
        '1': ["Move", "Move isolated", "Rearing", "Rear isolated", "Stop isolated",
              "WallJump", "SAP", "Huddling", "WaterPoint", "Distance"],
        '2': ["Contact", "Oral-oral Contact", "Oral-genital Contact", "Side by side Contact",
              "Side by side Contact, opposite way", "Social approach", "Social escape",
              "Approach contact", "Approach rear", "Break contact", "Get away",
              "FollowZone Isolated", "Train2", "Group2"],
        '3': ["Group3"],
        '4': ["Group4", "Nest4"]
    }

    # Traitement pour la clé '1'
    events_key_1 = event_options_index['1']
    df_filtered = df[df['name'].isin(events_key_1)]
    grouped = df_filtered[df_filtered['is_RFidA_in_LMT_indexer']].groupby(['Cage', 'Injection', 'name', 'Bin'])
    mean_numberOfEvents = grouped['numberOfEvents'].mean().reset_index(name='mean_index_NOE')
    # df['normalized_index_ED'] = df['numberOfEvents'] / df['mean_index_ED'].replace(0, pd.NA)
    df = df.merge(mean_numberOfEvents, on=['Cage', 'Injection', 'name', 'Bin'], how='left')

    # Traitement pour la clé '2' ajusté selon la nouvelle approche
    # Préparation du DataFrame pour stocker les résultats pour la clé '2'
    sum_results_df = pd.DataFrame()

    events_to_process = event_options_index['2'] + event_options_index['3'] + event_options_index['4']

    for event in events_to_process:
        event_df = df[df['name'] == event]
        event_sum_df = event_df.groupby(['Cage', 'Injection', 'Bin', 'RFidA'])['numberOfEvents'].sum().reset_index(
            name='sum_index_NOE')
        event_sum_df['event_name'] = event
        sum_results_df = pd.concat([sum_results_df, event_sum_df], ignore_index=True)

    df['event_name'] = df['name']
    df = df.merge(sum_results_df, on=['Cage', 'Injection', 'Bin', 'RFidA', 'event_name'], how='left')
    df.drop('event_name', axis=1, inplace=True)

    # # Étape 1: Concaténer les listes d'événements pour les clés '2', '3', '4'
    # events_to_process = event_options_index['2'] + event_options_index['3'] + event_options_index['4']

    # Étape 2 et 3: Filtrer et calculer la moyenne de 'sum_index_ED'
    df_events_filtered = df[df['is_RFidA_in_LMT_indexer'] & df['name'].isin(events_to_process)]
    mean_values = df_events_filtered.groupby(['Cage', 'Injection', 'Bin', 'name'])['sum_index_NOE'].mean().reset_index(
        name='mean_sum_index_NOE')

    # Fusionner les moyennes calculées avec le DataFrame original
    df = pd.merge(df, mean_values, on=['Cage', 'Injection', 'Bin', 'name'], how='left')

    # Étape 4: Calculer la moyenne normalisée
    df['LMT_Index_NOE'] = df.apply(
        lambda row: row['sum_index_NOE'] / row['mean_sum_index_NOE']
        if (row['name'] in events_to_process and
            row['mean_sum_index_NOE'] and row['mean_sum_index_NOE'] != 0) else np.nan,
        axis=1
    )

    # Calculez le ratio de 'numberOfEvents' sur 'mean_numberOfEvents' pour les événements de la clé '1'
    df['normalized_index_NOE'] = df.apply(lambda row: row['numberOfEvents'] / row['mean_index_NOE']
    if not pd.isnull(row['mean_index_NOE']) and row['mean_index_NOE'] != 0 else np.nan, axis=1)

    # Maintenant, combinez les colonnes 'normalized_index_ED' et 'LMT_Index_NOE' pour garder toutes les valeurs normalisées
    # Les valeurs de 'normalized_index_ED' remplacent les NaN dans 'LMT_Index_NOE'
    df['LMT_Index_NOE'] = df['LMT_Index_NOE'].combine_first(df['normalized_index_NOE'])

    # # Supprimez les colonnes qui ne sont plus nécessaires
    # df.drop(['normalized_index_ED', 'LMT-indexer', 'is_RFidA_in_LMT_indexer', 'mean_index_ED', 'sum_index_ED', 'mean_sum_index_ED'], axis=1, inplace=True)

    # Supprimez les colonnes qui ne sont plus nécessaires
    df.drop(['normalized_index_NOE', 'mean_index_NOE', 'sum_index_NOE', 'mean_sum_index_NOE'], axis=1, inplace=True)

    return df

def Create_indexer():
    global df

    # Read csv
    path = getCsvFileToProcess()
    df = pd.read_csv(path)

    # Replacement dictionary
    remplacement = {'weekend1': '(1)weekend1', '1-3NaCl': '(2)3NaCl',
                    '2-1Amphet': '(3)1Amphet', '3-1Amphet': '(4)1Amphet',
                    '4-1Amphet': '(5)1Amphet', 'weekend2': '(6)weekend2',
                    '5-3Amphet': '(7)3Amphet', '6-3Amphet': '(8)3Amphet',
                    '7-3Amphet': '(9)3Amphet', 'LMT1-2mo - Copy': 'LMT1-2mo',
                    'LMT2-3mo - Copy': 'LMT2-3mo', 'LMT3-4mo - Copy': 'LMT3-4mo',
                    'LMT1-2 mo-(3 nights) - Copy': 'LMT1-2mo', 'LMT1-2mo-(EXTRA DAY) - Copy': 'LMT1-2mo',
                    '(3)NaCl-wkn1': '(3)NaCl', '(4)CNO-wkn1': '(4)CNO', 4849288: 'WT', 4849182: 'WT', 4849442: 'KO',
                    4849389: 'KO', 4849170: 'KO', 4849177: 'WT', 4849082: 'WT', 4849418: 'KO', 4849401: 'KO',
                    4849123: 'KO',
                    4849495: 'WT', 4849417: 'WT', 4849247: 'KO', 4849551: 'KO', 4849446: 'WT', 4849435: 'WT'}

    ######################################################################################
    '''
    Use if you want to change genotype names or something else
    '''

    # Function to replace genotype values based on the replacement dictionary
    def replace_values(row, col_rfid, col_geno):
        for col_rfid, col_geno in zip(col_rfid, col_geno):
            rfid = row[col_rfid]
            if rfid in remplacement:
                row[col_geno] = remplacement[rfid]
        return row

    # Columns for RFID and genotype
    col_rfid = ['RFidA', 'RFidB', 'RFidC', 'RFidD']
    col_geno = ['GenoA', 'GenoB', 'GenoC', 'GenoD']

    # Apply the function to each row of the df between RFids and Genos
    df = df.apply(replace_values, args=(col_rfid, col_geno), axis=1)
    #
    # # Using the "replace" method to replace values
    # df['Injection'] = df['Injection'].replace(remplacement)
    # # df[['RFidB', 'RFidC', 'RFidD']] = df[['RFidB', 'RFidC', 'RFidD']].astype(int)
    #
    # df.to_csv('Bon_Merged.csv', index=False)

    ######################################################################################

    ######################################################################################
    '''
    Use if you want to copy Distance data in NumberofEvents column
    '''

    # # Use the loc method to both select and copy
    # df.loc[df['name'] == 'Distance', 'numberOfEvents'] = df.loc[df['name'] == 'Distance', 'totalLength'].values
    #
    # # Save the modified DataFrame to a new CSV file
    # df.to_csv('Nouveau_Bon_Merged.csv', index=False)

    ######################################################################################

    # Ipywidgets buttons arrangement
    style = {'description_width': '100px'}
    layout = widgets.Layout(width='300px', height='25px')

    # Create widgets
    # Buttons 'reset selection'
    index_reset = widgets.Button(description='Reset selection')

    # dropdown for Cage selection for LMT-indexer
    cage_dropdown_index = widgets.Dropdown(options=df['Cage'].unique(),
                                           description='Cage',
                                           style={'description_width': '120px'},
                                           layout=widgets.Layout(width='330px')
                                           )

    # dropdown for RFidA selection for LMT-indexer
    rfida_select_index = widgets.SelectMultiple(description='RFidA (Genos)',
                                                style={'description_width': '120px'},
                                                layout=widgets.Layout(width='330px')
                                                )

    # button for LMT-indexer column creation
    LMT_indexer_button = widgets.Button(description='Create LMT-indexer column',
                                         layout=layout,
                                         style=style)

    # button for LMT-indexes column creation
    LMT_index_button = widgets.Button(description='Compute LMT-index column',
                                        layout=layout,
                                        style=style)

    # Create a Text widget to input the file name
    file_name_text_csv = widgets.Text(description="File Name", value="Name of your new csv file")

    # Create a button to save the modified CSV file
    save_button_csv = widgets.Button(description="Save Dataframe into CSV file",
                                     layout=layout,
                                     style=style)

    def Create_indexes(b):
        # Utilisez df_example ou remplacez par le nom de votre DataFrame
        global df
        df = Create_index_ED(df)
        df = Create_index_NOE(df)

    LMT_index_button.on_click(Create_indexes)

    def modify_and_save(b):
        file_name = file_name_text_csv.value
        df.rename(columns={'Unnamed: 0': ''}, inplace=True)
        save_csv(df, file_name)

    save_button_csv.on_click(modify_and_save)
    LMT_indexer_button.on_click(lambda b: create_new_column(b, df, cage_dropdown_index, rfida_select_index))
    cage_dropdown_index.observe(lambda change: update_rfida_options(change, df, rfida_select_index), names='value')

    # Update RFidA options based on Cage selection initially
    rfida_select_index.options = get_rfida_values(cage_dropdown_index.value, df)

    # Organizing widgets into a single tab
    tab_contents = [
        cage_dropdown_index,
        rfida_select_index,
        LMT_indexer_button,
        LMT_index_button,
        file_name_text_csv,
        save_button_csv
        # LMT_indexer_button_ED
    ]
    tab = widgets.Tab()
    tab.children = [VBox(tab_contents)]
    tab.set_title(0, 'LMT-Index')

    display(tab)
