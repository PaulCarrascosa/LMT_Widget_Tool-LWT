import sys
sys.path.insert(1, "../")

from IPython.display import Markdown, display, clear_output
import ipywidgets as widgets
from ipywidgets import *
from tkinter.filedialog import askopenfilename
from lmtanalysis.FileUtil import getCsvFileToProcess
import matplotlib
import matplotlib.pyplot as plt
# from matplotlib.patches import Patch
import numpy as np
import pandas as pd
import seaborn as sns
import dabest
import random
import re
import os
import csv
import itertools
import scipy
from scipy import stats
from scipy.stats import wilcoxon
import statsmodels
import statsmodels.api as sm
import statsmodels.formula.api as smf
from statsmodels.formula.api import ols
from tabulate import tabulate
import warnings

warnings.filterwarnings('ignore')

# global df
# global genos
# global selected_genos
# global pivot_df2
# global merged_df
# global selected_genos
# global temp_df_loop1
# global df_new

pd.set_option('display.max_columns', None)
pd.set_option('max_colwidth', None)

# Read csv
path = getCsvFileToProcess()
df = pd.read_csv(path)

# Replacement of injections
remplacement = {'weekend1': '(1)weekend1', '1-3NaCl': '(2)3NaCl',
                '2-1Amphet': '(3)1Amphet', '3-1Amphet': '(4)1Amphet',
                '4-1Amphet': '(5)1Amphet', 'weekend2': '(6)weekend2',
                '5-3Amphet': '(7)3Amphet', '6-3Amphet': '(8)3Amphet',
                '7-3Amphet': '(9)3Amphet', 'LMT1-2mo - Copy': 'LMT1-2mo',
                'LMT2-3mo - Copy' : 'LMT2-3mo', 'LMT3-4mo - Copy' : 'LMT3-4mo',
                'LMT1-2 mo-(3 nights) - Copy' : 'LMT1-2mo', 'LMT1-2mo-(EXTRA DAY) - Copy' : 'LMT1-2mo'}

# Using the "replace" method to replace values
df['Injection'] = df['Injection'].replace(remplacement)

# Ipywidgets buttons arrangement
style = {'description_width': '100px'}
layout = widgets.Layout(width='300px',
                        height='25px')
# Buttons 'reset selection'
plot_reset = widgets.Button(description='Reset selection')
stat_reset = widgets.Button(description='Reset selection')

# Tab1 : Selection of behaviors to analyze
animalnumber = widgets.SelectMultiple(options=['Isolated beh. (eg:Rearing, SAP,...)', 'Beh. involving 2 mice',
                                               'Beh. involving 3 mice', 'Beh. involving 4 mice'],
                                      rows=4,
                                      description='Behaviors to analyze',
                                      style={'description_width': '120px'},
                                      layout=widgets.Layout(width='330px'),
                                      disabled=False)

# Selection of analysis type "Number" or "Duration"
data_type = ["Number of events", "Event duration"]
choicetype = widgets.Dropdown(options=data_type,
                              value=data_type[0],
                              description='Type',
                              style={'description_width': '120px'},
                              disable=False)

# Definition of variables
date = df["Date"].unique()


# Cage defs
# Custom sort function
def cle_tri_inj(element):
    # Use a regular expression to find the first digit in the element
    match = re.search(r'\d', element)

    if match:
        # If a digit is found, assign it to the first digit
        first_digit = int(match.group())

        # Use a second regular expression to find the second digit
        match2 = re.search(r'(\d+)(?=\D*$)', element)
        second_digit = int(match2.group()) if match2 else 0

        # Return a tuple to sort based on the two digits
        return (first_digit, second_digit)
    else:
        # If no digit is found, assign 0 for both digits
        return (0, 0)


injection = sorted(df["Injection"].unique(), key=cle_tri_inj)


# injection = sorted(df["Injection"].unique())

# Cage defs
# Custom sort function
# def cle_tri_cage(element):
#     # Separate the prefix "Cage" from the number
#     prefixe, nombre = element.split("Cage")
#     return (int(nombre), prefixe)

def cle_tri_cage(element):
    # Extract the number after "Cage"
    nombre_str = element[len("Cage"):]

    # Convert the integer number for to sort
    return int(nombre_str)


# Sort the list using the custom sort function
cage = sorted(df["Cage"].unique(), key=cle_tri_cage)
# cage = df["Cage"].unique()
night_phase = sorted(df["Night-Phase"].unique())
event = df["name"].unique()
stats = ['Linear Mixed Model', 'ANOVA']

# Create widgets
# drop_injection_plot = selection of injection day for plots
drop_injection_plot = widgets.SelectMultiple(options=injection,
                                             rows=len(injection),
                                             description='Injection',
                                             disabled=False)

# drop_cage_plot = selection of cage for plots
drop_cage_plot = widgets.SelectMultiple(options=cage,
                                        rows=5,
                                        description='Cage',
                                        disabled=False)

# drop_event = selection of behavior for plots
drop_event = widgets.Dropdown(options=event,
                              value=event[1],
                              description='Event:',
                              disabled=False)

# # drop_night_plot = selection of night for plots
# drop_night_plot = widgets.SelectMultiple(options=night_phase,
#                                          rows=5,
#                                          description='Night_Phase',
#                                          disabled=False)

# drop_stat = selection of stats type (currently only the Mixed-Model)
drop_stat = widgets.Dropdown(options=stats,
                             value=stats[0],
                             description='Statistic:',
                             style=style,
                             disabled=False)

# drop_injection_plot = selection of injection day for stats
drop_injection_stat = widgets.SelectMultiple(options=injection,
                                             rows=len(injection),
                                             description='Injection',
                                             style=style,
                                             disabled=False)

# drop_cage_plot = selection of cage for stats
drop_cage_stat = widgets.SelectMultiple(options=cage,
                                        rows=5,
                                        description='Cage',
                                        style=style,
                                        disabled=False)

# # drop_night_stat = selection of night for stats
# drop_night_stat = widgets.SelectMultiple(options=night_phase,
#                                          rows=5,
#                                          description='Night_Phase',
#                                          style=style,
#                                          disabled=False)

# Create widget for folder name
nom_dossier_plots = widgets.Text(placeholder='Type here',
                           description='Folder name:',
                           style=style,
                           disabled=False)

# Create widget for folder name
nom_dossier_stats = widgets.Text(placeholder='Type here',
                           description='Folder name:',
                           style = style,
                           disabled=False)

# Create button widget for plots
plotbutton = widgets.Button(description="Plots exportation",
                            layout = layout,
                            style = style)

# Create button widget for stats plots
statbutton = widgets.Button(description="Stats plots exportation",
                            layout=layout,
                            style=style)

# Create IntRangeSlider widget
range_slide_plot = widgets.IntRangeSlider(value=[0, max(df['Bin'])],
                                     min=0,
                                     max=max(df['Bin']),step=1,
                                     description='Bins :',
                                     disabled=False,
                                     continuous_update=False,
                                     orientation='horizontal',
                                     readout=True,
                                     readout_format='d')

# Create IntRangeSlider widget
range_slide_stats = widgets.IntRangeSlider(value=[0, max(df['Bin'])],
                                     min=0,
                                     max=max(df['Bin']),step=1,
                                     description='Bins :',
                                     disabled=False,
                                     continuous_update=False,
                                     orientation='horizontal',
                                     readout=True,
                                     readout_format='d')

# Create button widget for data retrieval
recup_data = widgets.Button(description="Data exportation",
                            layout = layout,
                            style = style)

# Genotype selection
genos = widgets.SelectMultiple(options=df.GenoA.unique(),
                               rows=len(df.GenoA.unique()),
                               description='Genotypes',
                               style = style,
                               disabled=False)

selected_genos = genos.value

def get_data_stats(recup_data):
    current_directory = os.getcwd()
    # Create the full path to the 'results' folder
    results_directory = os.path.join(current_directory, 'results')

    # Ensure that the 'results' folder exists, if not, create it
    if not os.path.exists(results_directory):
        os.makedirs(results_directory)
    # Create the full path to the 'result_df.csv' file in the 'results' folder
    result_df.to_csv(os.path.join(results_directory, 'result_df.csv'), index=False)

recup_data.on_click(get_data_stats)

# Assign the function 'results_update_dropdown' to the 'plotbutton' button
def get_plots_button(plotbutton):
    interactive_results_plots = widgets.interactive_output(results_update_dropdown,
                                                           {'date': drop_injection_plot,
                                                            'cage': drop_cage_plot,
                                                            # 'night_phase': drop_night_plot,
                                                            'event': drop_event,
                                                            'range_slide_plot': range_slide_plot})

# Associate the on_button_click function with the button click event
plotbutton.on_click(get_plots_button)

# Assign the function 'results_update_stats' to the 'statbutton' button
def get_plots_stats_button(statbutton):
    interactive_results_stats = widgets.interactive_output(results_update_stats,
                                                           {'date': drop_injection_stat,
                                                            'genos': genos,
                                                            'cage': drop_cage_stat,
                                                            # 'night_phase': drop_night_stat,
                                                            'event': drop_event,
                                                            'choice_type': choicetype,
                                                            'range_slide_stats': range_slide_stats})


# Associate the on_button_click function with the button click event
statbutton.on_click(get_plots_stats_button)

output = widgets.Output()

# Associate widgets with tabs
box1 = VBox([plot_reset,
             range_slide_plot,
             drop_injection_plot,
             drop_cage_plot,
             # drop_night_plot,
             drop_event,
             nom_dossier_plots,
             plotbutton])
box2 = VBox([stat_reset,
             range_slide_stats,
             genos,
             # drop_stat,
             drop_injection_stat,
             drop_cage_stat,
             # drop_night_stat,
             drop_event,
             nom_dossier_stats,
             statbutton,
             recup_data])

# Create the tab for the widgets
tab0 = widgets.VBox(children=[animalnumber, choicetype])
tab1 = widgets.Tab(children=[box1])
tab2 = widgets.VBox(children=[box2])
tab1.children = (tab0,) + tab1.children + tab2.children
tab1.set_title(0, 'Animals')
tab1.set_title(1, 'Plots')
tab1.set_title(2, 'Stats')

# Display the tab
# display(tab1)

# List of existing events in the current databases
event_options = {
    'Isolated beh. (eg:Rearing, SAP,...)': ["Move isolated", "Rearing", "Rear isolated", "Stop isolated", "SAP", "Distance"],
    'Beh. involving 2 mice': ["Contact", "Oral-oral Contact", "Oral-genital Contact", "Side by side Contact",
                              "Side by side Contact, opposite way", "Social approach", "Social escape",
                              "Approach contact", "Approach rear", "Break contact", "Get away",
                              "FollowZone Isolated", "Train2", "Group2"],
    'Beh. involving 3 mice': ["Group3"],
    'Beh. involving 4 mice': ["Group4", "Nest3", "Nest4"]}


# Update the events (drop_event) based on the selection of the 'animalnumber' widget
def update_event_options(change):
    selected_animalnumber = animalnumber.value
    selected_options = []
    for behavior in selected_animalnumber:
        selected_options += event_options[behavior]
    drop_event.options = selected_options


animalnumber.observe(update_event_options, names='value')


# Function to update selections in the 'Plot' tab after clicking the 'plot_reset' button
def reset_plot_selections(plot_reset):
    drop_injection_plot.value = ()
    drop_cage_plot.options = df['Cage'].unique()
    # drop_night_plot.options = df['Night-Phase'].unique()


plot_reset.on_click(reset_plot_selections)


# Function to update selections in the 'Stat' tab after clicking the 'stat_reset' button
def reset_stats_selections(stat_reset):
    drop_injection_stat.value = ()
    drop_cage_stat.options = df['Cage'].unique()
    # drop_night_stat.options = df['Night-Phase'].unique()


stat_reset.on_click(reset_stats_selections)

# To select multiple dates
def update_options_plot(change):
    # Filter DataFrame based on selected values in drop_injection_plot
    filtered_df = df[df['Injection'].isin(drop_injection_plot.value)]

    # Update drop_cage_plot options with unique values from the "Cage" column for filtered data
    cage_options_plot = filtered_df['Cage'].unique()
    drop_cage_plot.options = cage_options_plot

    # Retain selected values in drop_cage_plot if still valid after updating options
    drop_cage_plot.value = list(set(drop_cage_plot.value)
                                & set(cage_options_plot))

    # # Update drop_night_plot options with unique values from the "Night-Phase" column for filtered data
    # night_options_plot = filtered_df['Night-Phase'].unique()
    # drop_night_plot.options = night_options_plot
    #
    # # Retain selected values in drop_night_plot if still valid after updating options
    # drop_night_plot.value = list(set(drop_night_plot.value)
    #                              & set(night_options_plot))


# Assign the update_options function to the "observe" event of drop_injection_plot
drop_injection_plot.observe(update_options_plot, names='value')


def update_options_stat(change):
    # Filter DataFrame based on selected values in drop_injection_stat
    filtered_df = df[df['Injection'].isin(drop_injection_stat.value)]

    # Update drop_cage_stat options with unique values from the "Cage" column for filtered data
    cage_options_stats = filtered_df['Cage'].unique()
    drop_cage_stat.options = cage_options_stats

    # Retain selected values in drop_cage_stat if still valid after updating options
    drop_cage_stat.value = list(set(drop_cage_stat.value)
                                & set(cage_options_stats))

    # # Update drop_night_stat options with unique values from the "Night-Phase" column for filtered data
    # night_options_stats = filtered_df['Night-Phase'].unique()
    # drop_night_stat.options = night_options_stats
    #
    # # Retain selected values in drop_night_stat if still valid after updating options
    # drop_night_stat.value = list(set(drop_night_stat.value)
    #                              & set(night_options_stats))


# Assign the update_options function to the "observe" event of drop_injection_stat
drop_injection_stat.observe(update_options_stat, names='value')


def update_temp_df(change):
    # Update temp_df based on the current widget selection
    global temp_df
    temp_df = df[(df["Injection"].isin(drop_injection_plot.value))
                 & (df["Cage"].isin(drop_cage_plot.value))
                 & (df["name"] == drop_event.value)]
                 # & (df["Night-Phase"].isin(drop_night_plot.value))]


# Initialize temp_df based on the initial widget selection
temp_df = df[(df["Injection"].isin(drop_injection_plot.value))
             & (df["Cage"].isin(drop_cage_plot.value))
             & (df["name"] == drop_event.value)]
             # & (df["Night-Phase"].isin(drop_night_plot.value))]

# Observe widgets to update temp_df when the selection is changed
drop_injection_plot.observe(update_temp_df, 'value')
drop_cage_plot.observe(update_temp_df, 'value')
drop_event.observe(update_temp_df, 'value')
# drop_night_plot.observe(update_temp_df, 'value')

# colors for plots
colors = {j: sns.color_palette("husl", len(df.GenoA.unique()))[i] for i, j in enumerate(sorted(df.GenoA.unique()))}

# Fonction pour afficher le plot en fonction des choix de l'utilisateur
def update_dropdown(date, cage, event, range_slide_plot):
    '''
    This function will compute the 'number of event' or the 'event duration' per bin for each mice in the cage
    '''
    clear_output()
    min_value_plot, max_value_plot = range_slide_plot
    sns.set(font_scale=1.2, style='ticks')
    if choicetype.value == 'Number of events':
        for date_val, cage_val, night_phase_val in itertools.product(date, cage, night_phase):
            display(Markdown(
                f"""<h3>LMT session = {date_val}<br>Cage = {cage_val} <br>Event = {drop_event.value}
                    <br>Phase = {night_phase_val} </h3>"""))
            temp_df_loop0 = df[(df["Injection"] == date_val)
                               & (df["Cage"] == cage_val)
                               & (df["name"] == drop_event.value)
                               & (df["Night-Phase"] == night_phase_val)]
            # Créer un nouveau dataframe avec toutes les colonnes de l'ancien dataframe
            df_new0 = temp_df_loop0.copy()
            # Ajouter une colonne avec la somme des numberOfEvents de chaque RFidA de chaque Bin
            df_new0['new_numbersOfEvents'] = df_new0.groupby(['Bin', 'RFidA'])['numberOfEvents'].transform('sum')
            # Supprimer les lignes utilisées pour faire la somme
            df_new0 = df_new0.drop_duplicates(subset=['Bin', 'RFidA'],
                                            keep='last')
            df_new0 = df_new0[(df_new0['Bin'] >= min_value_plot) & (df_new0['Bin'] <= max_value_plot)]
            fig, ax1 = plt.subplots(figsize=(18, 12))
            ax2 = fig.add_axes([1, 0.25, 0.25, 0.5])
            sns.lineplot(data=df_new0,
                         y='new_numbersOfEvents',
                         x='Bin',
                         hue="GenoA",
                         style='RFidA',
                         palette=colors,
                         ax=ax1)
            ax1.set_title(f'Numbers of {drop_event.value} per bin of each mouse')
            ax1.set_ylabel(f'Numbers of {drop_event.value}')
            sns.barplot(data=df_new0,
                        y='new_numbersOfEvents',
                        x="GenoA",
                        palette=colors,
                        ax=ax2)
            ax2.set_title("Barplot which shows the number of events")
            plt.show()
    elif choicetype.value == 'Event duration':
        for date_val, cage_val, night_phase_val in itertools.product(date, cage, night_phase):
            display(Markdown(
                f"""<h3>LMT session = {date_val}<br>Cage = {cage_val} <br>Event = {drop_event.value}
                    <br>Phase = {night_phase_val} </h3>"""))
            temp_df_loop0 = df[(df["Injection"] == date_val)
                               & (df["Cage"] == cage_val)
                               & (df["name"] == drop_event.value)
                               & (df["Night-Phase"] == night_phase_val)]
            # Créer un nouveau dataframe avec toutes les colonnes de l'ancien dataframe
            df_new0 = temp_df_loop0.copy()
            # Ajouter une colonne avec la somme des numberOfEvents de chaque RFidA de chaque Bin
            df_new0['new_totallength'] = df_new0.groupby(['Bin', 'RFidA'])['totalLength'].transform('sum')
            # Supprimer les lignes utilisées pour faire la somme
            df_new0 = df_new0.drop_duplicates(subset=['Bin', 'RFidA'],
                                            keep='last')
            df_new0 = df_new0[(df_new0['Bin'] >= min_value_plot) & (df_new0['Bin'] <= max_value_plot)]
            fig, ax1 = plt.subplots(figsize=(18, 12))
            ax2 = fig.add_axes([1, 0.25, 0.25, 0.5])
            sns.lineplot(data=df_new0,
                         y='new_totallength',
                         x='Bin',
                         hue="GenoA",
                         style='RFidA',
                         palette=colors,
                         ax=ax1)
            ax1.set_title(f'Duration of {drop_event.value} per bin of each mouse')
            ax1.set_ylabel(f'Duration of {drop_event.value}')
            sns.barplot(data=df_new0,
                        y='new_totallength',
                        x="GenoA",
                        palette=colors,
                        ax=ax2)
            ax2.set_title("Barplot which shows the duration of events")
            plt.show()

# Fonction pour afficher le plot en fonction des choix de l'utilisateur
def results_update_dropdown(date, cage, event, range_slide_plot):
    '''
    This function will compute the 'number of event' or the 'event duration' per bin for each mice in the cage
    '''
    # Créer un nouveau dossier pour les fichiers
    new_folder_path = str(nom_dossier_plots.value)
    if not os.path.exists(new_folder_path):
        os.makedirs(new_folder_path)
    for r_drop_event_plot in drop_event.options:
        clear_output()
        min_value_plot, max_value_plot = range_slide_plot
        sns.set(font_scale=1.2, style='ticks')
        if choicetype.value == 'Number of events':
            for idx, (date_val, cage_val, night_phase_val) in enumerate(itertools.product(date, cage, night_phase)):
                display(Markdown(
                    f"""<h3>LMT session = {date_val}<br>Cage = {cage_val} <br>Event = {drop_event.value}
                    <br>Phase = {night_phase_val} </h3>"""))
                temp_df_loop0 = df[(df["Injection"] == date_val)
                                   & (df["Cage"] == cage_val)
                                   & (df["name"] == r_drop_event_plot)
                                   & (df["Night-Phase"] == night_phase_val)]
                # Créer un nouveau dataframe avec toutes les colonnes de l'ancien dataframe
                df_new0 = temp_df_loop0.copy()
                # Ajouter une colonne avec la somme des numberOfEvents de chaque RFidA de chaque Bin
                df_new0['new_numbersOfEvents'] = df_new0.groupby(['Bin', 'RFidA'])['numberOfEvents'].transform('sum')
                # Supprimer les lignes utilisées pour faire la somme
                df_new0 = df_new0.drop_duplicates(subset=['Bin', 'RFidA'],
                                                keep='last')
                df_new0 = df_new0[(df_new0['Bin'] >= min_value_plot) & (df_new0['Bin'] <= max_value_plot)]
                fig, ax1 = plt.subplots(figsize=(18, 12))
                ax2 = fig.add_axes([1, 0.25, 0.25, 0.5])
                sns.lineplot(data=df_new0,
                             y='new_numbersOfEvents',
                             x='Bin',
                             hue="GenoA",
                             style='RFidA',
                             palette=colors,
                             ax=ax1)
                ax1.set_title(f'Numbers of {r_drop_event_plot} per bin of each mouse of {date_val} in {cage_val}')
                ax1.set_ylabel(f'Numbers of {r_drop_event_plot}')
                sns.barplot(data=df_new0,
                            y='new_numbersOfEvents',
                            x="GenoA",
                            palette=colors,
                            ax=ax2)
                ax2.set_title("Barplot which shows the number of events")
                image_file_path = os.path.join(new_folder_path, f'NumberofEvent_{date_val}_{cage_val}_night{night_phase_val}_{r_drop_event_plot}.png')
                plt.savefig(image_file_path,
                            dpi=300,
                            bbox_inches='tight')
                plt.close(fig)
        elif choicetype.value == 'Event duration':
            for idx, (date_val, cage_val, night_phase_val) in enumerate(itertools.product(date, cage, night_phase)):
                display(Markdown(
                    f"""<h3>LMT session = {date_val}<br>Cage = {cage_val} <br>Event = {drop_event.value}
                    <br>Phase = {night_phase_val} </h3>"""))
                temp_df_loop0 = df[(df["Injection"] == date_val)
                                   & (df["Cage"] == cage_val)
                                   & (df["name"] == r_drop_event_plot)
                                   & (df["Night-Phase"] == night_phase_val)]
                # Créer un nouveau dataframe avec toutes les colonnes de l'ancien dataframe
                df_new0 = temp_df_loop0.copy()
                # Ajouter une colonne avec la somme des numberOfEvents de chaque RFidA de chaque Bin
                df_new0['new_totallength'] = df_new0.groupby(['Bin', 'RFidA'])['totalLength'].transform('sum')
                # Supprimer les lignes utilisées pour faire la somme
                df_new0 = df_new0.drop_duplicates(subset=['Bin', 'RFidA'],
                                                keep='last')
                df_new0 = df_new0[(df_new0['Bin'] >= min_value_plot) & (df_new0['Bin'] <= max_value_plot)]
                fig, ax1 = plt.subplots(figsize=(18, 12))
                ax2 = fig.add_axes([1, 0.25, 0.25, 0.5])
                sns.lineplot(data=df_new0,
                             y='new_totallength',
                             x='Bin',
                             hue="GenoA",
                             style='RFidA',
                             palette=colors,
                             ax=ax1)
                ax1.set_title(f'Duration of {r_drop_event_plot} per bin of each mouse of {date_val} in {cage_val}')
                ax1.set_ylabel(f'Duration of {r_drop_event_plot}')
                sns.barplot(data=df_new0,
                            y='new_totallength',
                            x="GenoA",
                            palette=colors,
                            ax=ax2)
                ax2.set_title("Barplot which shows the duration of events")
                image_file_path = os.path.join(new_folder_path, f'Eventduration_{date_val}_{cage_val}_night{night_phase_val}_{r_drop_event_plot}.png')
                plt.savefig(image_file_path,
                            dpi=300,
                            bbox_inches='tight')
                plt.close(fig)
        else :
            return


def update_stats(date, genos, cage, event, choice_type, range_slide_stats):
    '''
    This function will return a figure with 3 plots:
    . The first with the dabest package that will compare the selected data (eg. NaCl/Amphet)
    . The second with the dabest package that will compare the different injections
    . The third that is the summary of the statsmodels.stats.descriptivestats.describe() function
    '''
    global pivot_df2
    global merged_df
    global selected_genos
    global temp_df_loop1
    global image_file_path
    clear_output()
    new_column_names = []
    dfs = []
    ids = [i for i in df.GenoA.unique()]
    min_value_stats, max_value_stats = range_slide_stats

    if choicetype.value == 'Number of events':
        # temp_df_loop1 = df[(df["GenoA"].isin(list(genos.value)))]
        for date_val, genos_val, cage_val, night_phase_val in itertools.product(date, genos, cage, night_phase):
            # display(Markdown(f"""<h3>L'analyse est réalisée sur {animalnumber.value[0]} souris, l'injection
            # choisie est '{date_val}',
            # il s'agit de la {cage_val} pour l'évènement '{drop_event.value}' durant la phase {night_phase_val}
            # de nuit !</h3>"""))
            temp_df_loop1 = df[(df["Injection"] == date_val)
                               & (df["GenoA"] == genos_val)
                               & (df["Cage"] == cage_val)
                               & (df["name"] == drop_event.value)
                               & (df["Night-Phase"] == night_phase_val)]
            # Créer un nouveau dataframe avec toutes les colonnes de l'ancien dataframe
            df_new = temp_df_loop1.copy()
            # df_new = df_new[df_new['GenoA'].isin(selected_genos)]
            # Ajouter une colonne avec la somme des numberOfEvents de chaque RFidA de chaque Bin
            df_new['new_numbersOfEvents'] = df_new.groupby(['Bin', 'RFidA'])['numberOfEvents'].transform('sum')
            # Supprimer les lignes utilisées pour faire la somme
            df_new = df_new.drop_duplicates(subset=['Bin', 'RFidA'],
                                            keep='last')
            df_new = df_new[(df_new['Bin'] >= min_value_stats) & (df_new['Bin'] <= max_value_stats)]
            # fig, ax1 = plt.subplots(figsize=(10,4))
            # ax2 = fig.add_axes([1, 0.25, 0.25, 0.5])
            # sns.barplot(data=df_new, y='new_numbersOfEvents', x="GenoA", palette={'Amphet':'red', 'NaCl':'blue'}, ax=ax2)
            # ax2.set_title("A barplot")
            # plt.show()
            dfs.append(df_new)

        if not dfs:
            return

        else:
            merged_df = pd.concat(dfs)
            merged_df['new_cage'] = merged_df['Cage'].str.extract('(\d+)').astype(int)
            global df_lm
            global result_df
            global two_groups_paired_baseline
            global column_index
            df_lm = merged_df.copy()
            df_lm = merged_df.groupby(['new_cage', 'RFidA', 'GenoA', 'Date'])['new_numbersOfEvents'].sum().reset_index()

            # Compute Linear Mixed Models stats

            if drop_stat.value == "Linear Mixed Model":
                ssdd = statsmodels.stats.descriptivestats.describe(df_lm,
                                                                   stats=['mean', 'std_err', 'std', 'median'])
                model = smf.mixedlm("new_numbersOfEvents ~ GenoA",
                                    df_lm,
                                    groups='new_cage')  # Creates the model
                result = model.fit()  # Run model

                # df_lm['Dates'] = df_lm.groupby('RFidA')['Date'].transform(lambda x: ', '.join(x.astype(str)))
                # Utilisez groupby et cumcount pour attribuer des valeurs "1", "2" ou "3" en fonction de l'ordre des dates pour chaque RFidA
                # df_lm['New_Column'] = df_lm.groupby('RFidA').cumcount() + 1
                # df_lm['New_Column'] = df_lm['New_Column'].astype(str)
                df_lm = df_lm.sort_values(by=['RFidA', 'new_cage', 'Date']).reset_index(drop=True)

                new_df = df_lm.loc[:, ['new_cage', 'RFidA']]

                # Récupérez les valeurs de sélections dans le widget
                name_selections = list(drop_injection_stat.value)

                num_select = len(name_selections)

                # Ajoutez une colonne 'Injection' au DataFrame
                df_lm['Injection'] = [name_selections[i % num_select] for i in range(len(df_lm))]

                # Créez un dictionnaire pour stocker les données pivotées
                pivot_data = {'new_cage': [], 'RFidA': []}
                for injection in name_selections:
                    pivot_data[injection] = []

                # Parcourez les lignes du premier DataFrame
                for _, row in df_lm.iterrows():
                    liste_newcage = row['new_cage']
                    liste_RFidA = row['RFidA']
                    liste_injection = row['Injection']
                    liste_nbevents = row['new_numbersOfEvents']

                    # Vérifiez si la valeur de 'Injection' est dans la liste sélectionnée
                    if liste_injection in name_selections:
                        pivot_data['new_cage'].append(liste_newcage)
                        pivot_data['RFidA'].append(liste_RFidA)
                        for selected_injection in name_selections:
                            if selected_injection == liste_injection:
                                pivot_data[selected_injection].append(liste_nbevents)
                            else:
                                pivot_data[selected_injection].append(None)

                # Créez un DataFrame à partir du dictionnaire pivoté
                pivot_df = pd.DataFrame(pivot_data)

                # Fusionnez df2 avec le DataFrame pivoté
                result_df = pd.merge(new_df, pivot_df, on=['new_cage', 'RFidA'], how='left')

                # Groupez le résultat par 'new_cage' et 'RFidA' et agrégez les valeurs
                result_df = result_df.groupby(['new_cage', 'RFidA'])[name_selections].first().reset_index()

                # Replace values NaN by 'None'
                result_df = result_df.fillna('0')
                result_df.reset_index(drop=True, inplace=True)
                result_df.insert(0, 'Index', range(len(result_df)))

                # Reinitialize the index of the 2nd df
                new_df = new_df.reset_index(drop=True)

                # Convert all columns except 'Index', 'new_cage' and 'RFidA' in int64
                result_df[result_df.columns.difference(['Index', 'new_cage', 'RFidA'])] = result_df[
                    result_df.columns.difference(['Index', 'new_cage', 'RFidA'])].astype('int64')
                result_df
                pivot_df2 = df_lm.pivot(index=['RFidA', 'new_cage'],
                                        columns='Date',
                                        values='new_numbersOfEvents').reset_index()
                pivot_df2.sort_values('new_cage',
                                      inplace=True)

                # Initializing for dabest
                two_groups_paired_baseline = dabest.load(data=result_df,
                                                         idx=list(drop_injection_stat.value),
                                                         id_col="Index",
                                                         paired='baseline')

                fig, axs = plt.subplots(1, 3,
                                        figsize=(30, 12))
                fig.subplots_adjust(wspace=0.8)

                # 1er plot
                plotdabest = dabest.load(data=df_lm,
                                         x="GenoA",
                                         y="new_numbersOfEvents",
                                         idx=list(genos),
                                         id_col="new_cage")

                # Tracer le graphique
                plotdabest.mean_diff.plot(ax=axs[0],
                                          color_col='new_cage')
                axs[0].set_title(f"""Sum of numberOfEvents per Cage for the '{drop_event.value}' event""",
                                 loc='left')

                # 2ème plot
                if len(drop_injection_stat.value) == 2:
                    ax1 = two_groups_paired_baseline.mean_diff.plot(color_col='new_cage',
                                                                    ax=axs[1])
                    axs[1].legend(title='Cage',
                                  labels=result_df['new_cage'].unique(),
                                  frameon=False,
                                  loc=(1.62, 0.75))
                elif len(drop_injection_stat.value) > 2:
                    ax1 = two_groups_paired_baseline.mean_diff.plot(color_col='new_cage',
                                                                    ax=axs[1])
                    axs[1].legend(title='Cage',
                                  labels=result_df['new_cage'].unique(),
                                  frameon=False,
                                  loc=(0.95, 0.75))

                # 3ème plot
                axs[2].axis('off')
                table0 = tabulate(ssdd,
                                  headers="keys",
                                  colalign=("center", "center", "center", "center", "center"))
                axs[2].annotate(table0,
                                xy=(-0.45, 0.75),
                                xycoords='axes fraction',
                                fontsize=10, va='top',
                                family='monospace')
                table1 = tabulate(result.summary().tables[0],
                                  colalign=("center", "center", "center", "center", "center"))
                axs[2].annotate(table1,
                                xy=(-0.45, 0.55),
                                xycoords='axes fraction',
                                fontsize=10,
                                va='top',
                                family='monospace')
                table2 = tabulate(result.summary().tables[1],
                                  headers="keys",
                                  tablefmt="plain",
                                  colalign=("center", "center", "center", "center", "center", "center", "center"))
                axs[2].annotate(table2,
                                xy=(-0.45, 0.35),
                                xycoords='axes fraction',
                                fontsize=10,
                                va='top',
                                family='monospace')

                df_lm = df_lm.rename(columns={'new_cage': 'Cage', 'new_numbersOfEvents': 'NumberOfEvents'})

    #             elif drop_stat.value == "ANOVA":
    #                 # 1
    #                 # model = smf.ols("new_numbersOfEvents ~ GenoA", data=df_lm)
    #                 # anova_result = sm.stats.anova_lm(model.fit())
    #                 # print(anova_result)
    #                 # 2
    #                 anova_result = smf.ols("new_numbersOfEvents ~ GenoA", data=df_lm).fit()
    #                 # print(anova_result.summary())
    #                 pivot_df2 = df_lm.pivot(index=['RFidA', 'new_cage'],
    #                                         columns='Date',
    #                                         values='new_numbersOfEvents').reset_index()
    #                 pivot_df2.sort_values('new_cage',
    #                                       inplace=True)

    #                 # Récupérez les valeurs de sélections dans le widget
    #                 name_selections = list(drop_injection_stat.value)

    #                 ##### MARCHE SI LES VALEURS SONT COLLéES (PAR DE NAN ENTRE 2 VALEURS)
    #                 # Remplissez les colonnes avec la somme des colonnes existantes à partir de la deuxième colonne
    #                 for i in range(1, num_selections + 1):
    #                     column_name = name_selections[i-1]
    #                     start_column = i + 1  # Commencez à partir de la colonne suivante (index + 1)
    #                     step = num_selections  # Utilisez un pas égal au nombre de sélections
    #                     pivot_df2[column_name] = pivot_df2.iloc[:, start_column::step].sum(axis=1)
    #                     new_column_names.append(column_name)  # Ajoutez le nom de la colonne à la liste

    #                 # création de la colonne avec l'index
    #                 pivot_df2.reset_index(inplace=True)
    #                 pivot_df2.index = range(len(pivot_df2))
    #                 pivot_df2.index.name = 'Index'
    #                 pivot_df2['Index'] = pivot_df2.index.astype(int)

    #                 two_groups_paired_baseline = dabest.load(data=pivot_df2,
    #                                                              idx=new_column_names,
    #                                                              id_col="Index",
    #                                                              paired='baseline')

    #                 fig, axs = plt.subplots(1, 3,
    #                                         figsize=(30, 12))
    #                 fig.subplots_adjust(wspace=0.8)

    #                 # 1er plot
    #                 plotdabest = dabest.load(data=df_lm,
    #                                          x="GenoA",
    #                                          y="new_numbersOfEvents",
    #                                          idx=ids,
    #                                          id_col="new_cage")

    #                 # Tracer le graphique
    #                 plotdabest.mean_diff.plot(ax=axs[0],
    #                                           color_col='new_cage')
    #                 axs[0].set_title(f"""Sum of numberOfEvents per Cage for the '{drop_event.value}' event""",
    #                                  loc='left')

    #                 # 2ème plot
    #                 if len(drop_injection_stat.value) == 2:
    #                     ax1 = two_groups_paired_baseline.mean_diff.plot(color_col='new_cage',
    #                                                                     ax=axs[1])
    #                     axs[1].legend(title='Cage',
    #                                   labels=pivot_df2['new_cage'].unique(),
    #                                   frameon=False,
    #                                   loc=(1.62, 0.75))
    #                 elif len(drop_injection_stat.value) > 2:
    #                     ax1 = two_groups_paired_baseline.mean_diff.plot(color_col='new_cage',
    #                                                                     ax=axs[1])
    #                     axs[1].legend(title='Cage',
    #                                   labels=pivot_df2['new_cage'].unique(),
    #                                   frameon=False,
    #                                   loc=(0.95, 0.75))

    #                 # 3ème plot
    #                 axs[2].set_position([0.7, 0.1, 0.4, 0.8])  # Ajuster la position et la taille
    #                 axs[2].axis('off')
    #                 # Annotation de texte pour le modèle ajusté
    #                 axs[2].text(0.5, 0.5, str(anova_result.summary()), fontsize=12, family='monospace', ha='right', va='center')
    #                 # axs[2].text(0.1, 0.5, str(anova_result.summary()), fontsize=10, family='monospace')
    #                 # table0 = tabulate(anova_result,
    #                 #                   headers="keys",
    #                 #                   colalign=("center", "center", "center", "center", "center"))
    #                 # axs[2].annotate(table0,
    #                 #                 xy=(-0.25, 0.75),
    #                 #                 xycoords='axes fraction',
    #                 #                 fontsize=10, va='top',
    #                 #                 family='monospace')
    #                 # table1 = tabulate(anova_result.summary().tables[0],
    #                 #                   colalign=("center", "center", "center", "center", "center"))
    #                 # axs[2].annotate(table1,
    #                 #                 xy=(-0.25, 0.55),
    #                 #                 xycoords='axes fraction',
    #                 #                 fontsize=10,
    #                 #                 va='top',
    #                 #                 family='monospace')
    #                 # table2 = tabulate(anova_result.summary().tables[1],
    #                 #                   headers="keys",
    #                 #                   tablefmt="plain",
    #                 #                   colalign=("center", "center", "center", "center", "center", "center", "center"))
    #                 # axs[2].annotate(table2,
    #                 #                 xy=(-0.25, 0.35),
    #                 #                 xycoords='axes fraction',
    #                 #                 fontsize=10,
    #                 #                 va='top',
    #                 #                 family='monospace')

    elif choicetype.value == 'Event duration':
        for date_val, genos_val, cage_val, night_phase_val in itertools.product(date, genos, cage, night_phase):
            temp_df_loop1 = df[(df["Injection"] == date_val)
                               & (df["GenoA"] == genos_val)
                               & (df["Cage"] == cage_val)
                               & (df["name"] == drop_event.value)
                               & (df["Night-Phase"] == night_phase_val)]
            # Créer un nouveau dataframe avec toutes les colonnes de l'ancien dataframe
            df_new = temp_df_loop1.copy()
            # Ajouter une colonne avec la somme des numberOfEvents de chaque RFidA de chaque Bin
            df_new['new_totallength'] = df_new.groupby(['Bin', 'RFidA'])['totalLength'].transform('sum')
            # Supprimer les lignes utilisées pour faire la somme
            df_new = df_new.drop_duplicates(subset=['Bin', 'RFidA'],
                                            keep='last')
            df_new = df_new[(df_new['Bin'] >= min_value_stats) & (df_new['Bin'] <= max_value_stats)]
            dfs.append(df_new)

        if not dfs:
            return

        else:
            merged_df = pd.concat(dfs)
            merged_df['new_cage'] = merged_df['Cage'].str.extract('(\d+)').astype(int)
            df_lm = merged_df.copy()
            df_lm = merged_df.groupby(['new_cage', 'RFidA', 'GenoA', 'Date'])['new_totallength'].sum().reset_index()

            if drop_stat.value == "Linear Mixed Model":
                ssdd = statsmodels.stats.descriptivestats.describe(df_lm,
                                                                   stats=['mean', 'std_err', 'std', 'median'])
                model = smf.mixedlm("new_totallength ~ GenoA",
                                    df_lm,
                                    groups='new_cage')  # Creates the model
                result = model.fit()  # Run model

                df_lm = df_lm.sort_values(by=['RFidA', 'new_cage', 'Date']).reset_index(drop=True)

                new_df = df_lm.loc[:, ['new_cage', 'RFidA']]

                # Récupérez les valeurs de sélections dans le widget
                name_selections = list(drop_injection_stat.value)

                num_select = len(name_selections)

                # Ajoutez une colonne 'Injection' au DataFrame
                df_lm['Injection'] = [name_selections[i % num_select] for i in range(len(df_lm))]

                # Créez un dictionnaire pour stocker les données pivotées
                pivot_data = {'new_cage': [], 'RFidA': []}
                for injection in name_selections:
                    pivot_data[injection] = []

                # Parcourez les lignes du premier DataFrame
                for _, row in df_lm.iterrows():
                    liste_newcage = row['new_cage']
                    liste_RFidA = row['RFidA']
                    liste_injection = row['Injection']
                    liste_nbevents = row['new_totallength']

                    # Vérifiez si la valeur de 'Injection' est dans la liste sélectionnée
                    if liste_injection in name_selections:
                        pivot_data['new_cage'].append(liste_newcage)
                        pivot_data['RFidA'].append(liste_RFidA)
                        for selected_injection in name_selections:
                            if selected_injection == liste_injection:
                                pivot_data[selected_injection].append(liste_nbevents)
                            else:
                                pivot_data[selected_injection].append(None)

                # Créez un DataFrame à partir du dictionnaire pivoté
                pivot_df = pd.DataFrame(pivot_data)

                # Fusionnez df2 avec le DataFrame pivoté
                result_df = pd.merge(new_df, pivot_df, on=['new_cage', 'RFidA'], how='left')

                # Groupez le résultat par 'new_cage' et 'RFidA' et agrégez les valeurs
                result_df = result_df.groupby(['new_cage', 'RFidA'])[name_selections].first().reset_index()

                # Remplacez les valeurs NaN par 'None'
                result_df = result_df.fillna('0')
                result_df.reset_index(drop=True, inplace=True)
                result_df.insert(0, 'Index', range(len(result_df)))

                # Réinitialisez l'index du deuxième DataFrame
                new_df = new_df.reset_index(drop=True)

                # Convertir toutes les colonnes sauf 'Index', 'new_cage', et 'RFidA' en int64
                result_df[result_df.columns.difference(['Index', 'new_cage', 'RFidA'])] = result_df[
                    result_df.columns.difference(['Index', 'new_cage', 'RFidA'])].astype('int64')
                result_df
                pivot_df2 = df_lm.pivot(index=['RFidA', 'new_cage'],
                                        columns='Date',
                                        values='new_totallength').reset_index()
                pivot_df2.sort_values('new_cage',
                                      inplace=True)

                two_groups_paired_baseline = dabest.load(data=result_df,
                                                         idx=list(drop_injection_stat.value),
                                                         id_col="Index",
                                                         paired='baseline')

                fig, axs = plt.subplots(1, 3,
                                        figsize=(30, 12))
                fig.subplots_adjust(wspace=0.8)

                # 1er plot
                plotdabest = dabest.load(data=df_lm,
                                         x="GenoA",
                                         y="new_totallength",
                                         idx=list(genos),
                                         id_col="new_cage")

                # Tracer le graphique
                plotdabest.mean_diff.plot(ax=axs[0],
                                          color_col='new_cage')
                axs[0].set_title(f"""Sum of totalLength per Cage for the '{drop_event.value}' event""",
                                 loc='left')

                # 2ème plot
                if len(drop_injection_stat.value) == 2:
                    ax1 = two_groups_paired_baseline.mean_diff.plot(color_col='new_cage',
                                                                    ax=axs[1])
                    axs[1].legend(title='Cage',
                                  labels=result_df['new_cage'].unique(),
                                  frameon=False,
                                  loc=(1.62, 0.75))
                elif len(drop_injection_stat.value) > 2:
                    ax1 = two_groups_paired_baseline.mean_diff.plot(color_col='new_cage',
                                                                    ax=axs[1])
                    axs[1].legend(title='Cage',
                                  labels=result_df['new_cage'].unique(),
                                  frameon=False,
                                  loc=(0.95, 0.75))

                # 3ème plot
                axs[2].axis('off')
                table0 = tabulate(ssdd,
                                  headers="keys",
                                  colalign=("center", "center", "center", "center", "center"))
                axs[2].annotate(table0,
                                xy=(-0.45, 0.75),
                                xycoords='axes fraction',
                                fontsize=10, va='top',
                                family='monospace')
                table1 = tabulate(result.summary().tables[0],
                                  colalign=("center", "center", "center", "center", "center"))
                axs[2].annotate(table1,
                                xy=(-0.45, 0.55),
                                xycoords='axes fraction',
                                fontsize=10,
                                va='top',
                                family='monospace')
                table2 = tabulate(result.summary().tables[1],
                                  headers="keys",
                                  tablefmt="plain",
                                  colalign=("center", "center", "center", "center", "center", "center", "center"))
                axs[2].annotate(table2,
                                xy=(-0.45, 0.35),
                                xycoords='axes fraction',
                                fontsize=10,
                                va='top',
                                family='monospace')

                df_lm = df_lm.rename(columns={'new_cage': 'Cage', 'new_totallength': 'Totallength'})

def results_update_stats(date, genos, cage, event, choice_type, range_slide_stats):
    '''
    This function will return a figure with 3 plots:
    . The first with the dabest package that will compare the selected data (eg. NaCl/Amphet)
    . The second with the dabest package that will compare the different injections
    . The third that is the summary of the statsmodels.stats.descriptivestats.describe() function
    '''
    global pivot_df2
    global merged_df
    global selected_genos
    global temp_df_loop1
    global df_new
    clear_output()
    new_column_names = []
    dfs = []
    ids = [i for i in df.GenoA.unique()]
    min_value_stats, max_value_stats = range_slide_stats
    if drop_stat.value == "Linear Mixed Model":
        # Créer un nouveau dossier pour les fichiers
        new_folder_path = str(nom_dossier_stats.value)
        if not os.path.exists(new_folder_path):
            os.makedirs(new_folder_path)
        if choicetype.value == 'Number of events':
            # temp_df_loop1 = df[(df["GenoA"].isin(list(genos.value)))]
            for date_val, genos_val, cage_val, night_phase_val in itertools.product(date, genos, cage, night_phase):
                # display(Markdown(f"""<h3>L'analyse est réalisée sur {animalnumber.value[0]} souris, l'injection
                # choisie est '{date_val}',
                # il s'agit de la {cage_val} pour l'évènement '{drop_event.value}' durant la phase {night_phase_val}
                # de nuit !</h3>"""))
                temp_df_loop1 = df[(df["Injection"] == date_val)
                                   & (df["GenoA"] == genos_val)
                                   & (df["Cage"] == cage_val)
                                   & (df["name"] == drop_event.value)
                                   & (df["Night-Phase"] == night_phase_val)]
                # Créer un nouveau dataframe avec toutes les colonnes de l'ancien dataframe
                df_new = temp_df_loop1.copy()
                # df_new = df_new[df_new['GenoA'].isin(selected_genos)]
                # Ajouter une colonne avec la somme des numberOfEvents de chaque RFidA de chaque Bin
                df_new['new_numbersOfEvents'] = df_new.groupby(['Bin', 'RFidA'])['numberOfEvents'].transform('sum')
                # Supprimer les lignes utilisées pour faire la somme
                df_new = df_new.drop_duplicates(subset=['Bin', 'RFidA'],
                                                keep='last')
                df_new = df_new[(df_new['Bin'] >= min_value_stats) & (df_new['Bin'] <= max_value_stats)]
                # fig, ax1 = plt.subplots(figsize=(10,4))
                # ax2 = fig.add_axes([1, 0.25, 0.25, 0.5])
                # sns.barplot(data=df_new, y='new_numbersOfEvents', x="GenoA", palette={'Amphet':'red', 'NaCl':'blue'}, ax=ax2)
                # ax2.set_title("A barplot")
                # plt.show()
                dfs.append(df_new)

            if not dfs:
                return

            else:
                merged_df = pd.concat(dfs)
                merged_df['new_cage'] = merged_df['Cage'].str.extract('(\d+)').astype(int)
                global df_lm
                global result_df
                global two_groups_paired_baseline
                global column_index
                df_lm = merged_df.copy()
                df_lm = merged_df.groupby(['new_cage', 'RFidA', 'GenoA', 'Date'])['new_numbersOfEvents'].sum().reset_index()

                # Compute Linear Mixed Models stats

                if drop_stat.value == "Linear Mixed Model":
                    ssdd = statsmodels.stats.descriptivestats.describe(df_lm,
                                                                       stats=['mean', 'std_err', 'std', 'median'])
                    model = smf.mixedlm("new_numbersOfEvents ~ GenoA",
                                        df_lm,
                                        groups='new_cage')  # Creates the model
                    result = model.fit()  # Run model

                    # df_lm['Dates'] = df_lm.groupby('RFidA')['Date'].transform(lambda x: ', '.join(x.astype(str)))
                    # Utilisez groupby et cumcount pour attribuer des valeurs "1", "2" ou "3" en fonction de l'ordre des dates pour chaque RFidA
                    # df_lm['New_Column'] = df_lm.groupby('RFidA').cumcount() + 1
                    # df_lm['New_Column'] = df_lm['New_Column'].astype(str)
                    df_lm = df_lm.sort_values(by=['RFidA', 'new_cage', 'Date']).reset_index(drop=True)

                    new_df = df_lm.loc[:, ['new_cage', 'RFidA']]

                    # Récupérez les valeurs de sélections dans le widget
                    name_selections = list(drop_injection_stat.value)

                    num_select = len(name_selections)

                    # Ajoutez une colonne 'Injection' au DataFrame
                    df_lm['Injection'] = [name_selections[i % num_select] for i in range(len(df_lm))]

                    # Créez un dictionnaire pour stocker les données pivotées
                    pivot_data = {'new_cage': [], 'RFidA': []}
                    for injection in name_selections:
                        pivot_data[injection] = []

                    # Parcourez les lignes du premier DataFrame
                    for _, row in df_lm.iterrows():
                        liste_newcage = row['new_cage']
                        liste_RFidA = row['RFidA']
                        liste_injection = row['Injection']
                        liste_nbevents = row['new_numbersOfEvents']

                        # Vérifiez si la valeur de 'Injection' est dans la liste sélectionnée
                        if liste_injection in name_selections:
                            pivot_data['new_cage'].append(liste_newcage)
                            pivot_data['RFidA'].append(liste_RFidA)
                            for selected_injection in name_selections:
                                if selected_injection == liste_injection:
                                    pivot_data[selected_injection].append(liste_nbevents)
                                else:
                                    pivot_data[selected_injection].append(None)

                    # Créez un DataFrame à partir du dictionnaire pivoté
                    pivot_df = pd.DataFrame(pivot_data)

                    # Fusionnez df2 avec le DataFrame pivoté
                    result_df = pd.merge(new_df, pivot_df, on=['new_cage', 'RFidA'], how='left')

                    # Groupez le résultat par 'new_cage' et 'RFidA' et agrégez les valeurs
                    result_df = result_df.groupby(['new_cage', 'RFidA'])[name_selections].first().reset_index()

                    # Replace values NaN by 'None'
                    result_df = result_df.fillna('0')
                    result_df.reset_index(drop=True, inplace=True)
                    result_df.insert(0, 'Index', range(len(result_df)))

                    # Reinitialize the index of the 2nd df
                    new_df = new_df.reset_index(drop=True)

                    # Convert all columns except 'Index', 'new_cage' and 'RFidA' in int64
                    result_df[result_df.columns.difference(['Index', 'new_cage', 'RFidA'])] = result_df[result_df.columns.difference(['Index', 'new_cage', 'RFidA'])].astype('int64')
                    result_df
                    pivot_df2 = df_lm.pivot(index=['RFidA', 'new_cage'],
                                            columns='Date',
                                            values='new_numbersOfEvents').reset_index()
                    pivot_df2.sort_values('new_cage',
                                          inplace=True)

                    # Initializing for dabest
                    two_groups_paired_baseline = dabest.load(data=result_df,
                                                                 idx=list(drop_injection_stat.value),
                                                                 id_col="Index",
                                                                 paired='baseline')

                    fig, axs = plt.subplots(1, 3,
                                            figsize=(30, 12))
                    fig.subplots_adjust(wspace=0.8)

                    # 1er plot
                    plotdabest = dabest.load(data=df_lm,
                                             x="GenoA",
                                             y="new_numbersOfEvents",
                                             idx=list(genos),
                                             id_col="new_cage")

                    # Tracer le graphique
                    plotdabest.mean_diff.plot(ax=axs[0],
                                              color_col='new_cage')
                    axs[0].set_title(f"""Sum of numberOfEvents per Cage for the '{drop_event.value}' event""",
                                     loc='left')

                    # 2ème plot
                    if len(drop_injection_stat.value) == 2:
                        ax1 = two_groups_paired_baseline.mean_diff.plot(color_col='new_cage',
                                                                        ax=axs[1])
                        axs[1].legend(title='Cage',
                                      labels=result_df['new_cage'].unique(),
                                      frameon=False,
                                      loc=(1.62, 0.75))
                    elif len(drop_injection_stat.value) > 2:
                        ax1 = two_groups_paired_baseline.mean_diff.plot(color_col='new_cage',
                                                                        ax=axs[1])
                        axs[1].legend(title='Cage',
                                      labels=result_df['new_cage'].unique(),
                                      frameon=False,
                                      loc=(0.95, 0.75))

                    # 3ème plot
                    axs[2].axis('off')
                    table0 = tabulate(ssdd,
                                      headers="keys",
                                      colalign=("center", "center", "center", "center", "center"))
                    axs[2].annotate(table0,
                                    xy=(-0.45, 0.75),
                                    xycoords='axes fraction',
                                    fontsize=10, va='top',
                                    family='monospace')
                    table1 = tabulate(result.summary().tables[0],
                                      colalign=("center", "center", "center", "center", "center"))
                    axs[2].annotate(table1,
                                    xy=(-0.45, 0.55),
                                    xycoords='axes fraction',
                                    fontsize=10,
                                    va='top',
                                    family='monospace')
                    table2 = tabulate(result.summary().tables[1],
                                      headers="keys",
                                      tablefmt="plain",
                                      colalign=("center", "center", "center", "center", "center", "center", "center"))
                    axs[2].annotate(table2,
                                    xy=(-0.45, 0.35),
                                    xycoords='axes fraction',
                                    fontsize=10,
                                    va='top',
                                    family='monospace')
                    image_file_path = os.path.join(new_folder_path, f'{drop_event.value}.png')
                    plt.savefig(image_file_path, dpi=300, bbox_inches='tight')
                    plt.close(fig)

                    df_lm = df_lm.rename(columns={'new_cage': 'Cage', 'new_numbersOfEvents': 'NumberOfEvents'})

        elif choicetype.value == 'Event duration':
            for date_val, genos_val, cage_val, night_phase_val in itertools.product(date, genos, cage, night_phase):
                temp_df_loop1 = df[(df["Injection"] == date_val)
                                   & (df["GenoA"] == genos_val)
                                   & (df["Cage"] == cage_val)
                                   & (df["name"] == drop_event.value)
                                   & (df["Night-Phase"] == night_phase_val)]
                # Créer un nouveau dataframe avec toutes les colonnes de l'ancien dataframe
                df_new = temp_df_loop1.copy()
                # Ajouter une colonne avec la somme des numberOfEvents de chaque RFidA de chaque Bin
                df_new['new_totallength'] = df_new.groupby(['Bin', 'RFidA'])['totalLength'].transform('sum')
                # Supprimer les lignes utilisées pour faire la somme
                df_new = df_new.drop_duplicates(subset=['Bin', 'RFidA'],
                                                keep='last')
                df_new = df_new[(df_new['Bin'] >= min_value_stats) & (df_new['Bin'] <= max_value_stats)]
                dfs.append(df_new)

            if not dfs:
                return

            else:
                merged_df = pd.concat(dfs)
                merged_df['new_cage'] = merged_df['Cage'].str.extract('(\d+)').astype(int)
                df_lm = merged_df.copy()
                df_lm = merged_df.groupby(['new_cage', 'RFidA', 'GenoA', 'Date'])['new_totallength'].sum().reset_index()

                if drop_stat.value == "Linear Mixed Model":
                    ssdd = statsmodels.stats.descriptivestats.describe(df_lm,
                                                                       stats=['mean', 'std_err', 'std', 'median'])
                    model = smf.mixedlm("new_totallength ~ GenoA",
                                        df_lm,
                                        groups='new_cage')  # Creates the model
                    result = model.fit()  # Run model

                    df_lm = df_lm.sort_values(by=['RFidA', 'new_cage', 'Date']).reset_index(drop=True)

                    new_df = df_lm.loc[:, ['new_cage', 'RFidA']]

                    # Récupérez les valeurs de sélections dans le widget
                    name_selections = list(drop_injection_stat.value)

                    num_select = len(name_selections)

                    # Ajoutez une colonne 'Injection' au DataFrame
                    df_lm['Injection'] = [name_selections[i % num_select] for i in range(len(df_lm))]

                    # Créez un dictionnaire pour stocker les données pivotées
                    pivot_data = {'new_cage': [], 'RFidA': []}
                    for injection in name_selections:
                        pivot_data[injection] = []

                    # Parcourez les lignes du premier DataFrame
                    for _, row in df_lm.iterrows():
                        liste_newcage = row['new_cage']
                        liste_RFidA = row['RFidA']
                        liste_injection = row['Injection']
                        liste_nbevents = row['new_totallength']

                        # Vérifiez si la valeur de 'Injection' est dans la liste sélectionnée
                        if liste_injection in name_selections:
                            pivot_data['new_cage'].append(liste_newcage)
                            pivot_data['RFidA'].append(liste_RFidA)
                            for selected_injection in name_selections:
                                if selected_injection == liste_injection:
                                    pivot_data[selected_injection].append(liste_nbevents)
                                else:
                                    pivot_data[selected_injection].append(None)

                    # Créez un DataFrame à partir du dictionnaire pivoté
                    pivot_df = pd.DataFrame(pivot_data)

                    # Fusionnez df2 avec le DataFrame pivoté
                    result_df = pd.merge(new_df, pivot_df, on=['new_cage', 'RFidA'], how='left')

                    # Groupez le résultat par 'new_cage' et 'RFidA' et agrégez les valeurs
                    result_df = result_df.groupby(['new_cage', 'RFidA'])[name_selections].first().reset_index()

                    # Remplacez les valeurs NaN par 'None'
                    result_df = result_df.fillna('0')
                    result_df.reset_index(drop=True, inplace=True)
                    result_df.insert(0, 'Index', range(len(result_df)))

                    # Réinitialisez l'index du deuxième DataFrame
                    new_df = new_df.reset_index(drop=True)

                    # Convertir toutes les colonnes sauf 'Index', 'new_cage', et 'RFidA' en int64
                    result_df[result_df.columns.difference(['Index', 'new_cage', 'RFidA'])] = result_df[result_df.columns.difference(['Index', 'new_cage', 'RFidA'])].astype('int64')
                    result_df
                    pivot_df2 = df_lm.pivot(index=['RFidA', 'new_cage'],
                                            columns='Date',
                                            values='new_totallength').reset_index()
                    pivot_df2.sort_values('new_cage',
                                          inplace=True)

                    two_groups_paired_baseline = dabest.load(data=result_df,
                                                                 idx=list(drop_injection_stat.value),
                                                                 id_col="Index",
                                                                 paired='baseline')

                    fig, axs = plt.subplots(1, 3,
                                            figsize=(30, 12))
                    fig.subplots_adjust(wspace=0.8)

                    # 1er plot
                    plotdabest = dabest.load(data=df_lm,
                                             x="GenoA",
                                             y="new_totallength",
                                             idx=list(genos),
                                             id_col="new_cage")

                    # Tracer le graphique
                    plotdabest.mean_diff.plot(ax=axs[0],
                                              color_col='new_cage')
                    axs[0].set_title(f"""Sum of totalLength per Cage for the '{drop_event.value}' event""",
                                     loc='left')

                    # 2ème plot
                    if len(drop_injection_stat.value) == 2:
                        ax1 = two_groups_paired_baseline.mean_diff.plot(color_col='new_cage',
                                                                        ax=axs[1])
                        axs[1].legend(title='Cage',
                                      labels=result_df['new_cage'].unique(),
                                      frameon=False,
                                      loc=(1.62, 0.75))
                    elif len(drop_injection_stat.value) > 2:
                        ax1 = two_groups_paired_baseline.mean_diff.plot(color_col='new_cage',
                                                                        ax=axs[1])
                        axs[1].legend(title='Cage',
                                      labels=result_df['new_cage'].unique(),
                                      frameon=False,
                                      loc=(0.95, 0.75))

                    # 3ème plot
                    axs[2].axis('off')
                    table0 = tabulate(ssdd,
                                      headers="keys",
                                      colalign=("center", "center", "center", "center", "center"))
                    axs[2].annotate(table0,
                                    xy=(-0.45, 0.75),
                                    xycoords='axes fraction',
                                    fontsize=10, va='top',
                                    family='monospace')
                    table1 = tabulate(result.summary().tables[0],
                                      colalign=("center", "center", "center", "center", "center"))
                    axs[2].annotate(table1,
                                    xy=(-0.45, 0.55),
                                    xycoords='axes fraction',
                                    fontsize=10,
                                    va='top',
                                    family='monospace')
                    table2 = tabulate(result.summary().tables[1],
                                      headers="keys",
                                      tablefmt="plain",
                                      colalign=("center", "center", "center", "center", "center", "center", "center"))
                    axs[2].annotate(table2,
                                    xy=(-0.45, 0.35),
                                    xycoords='axes fraction',
                                    fontsize=10,
                                    va='top',
                                    family='monospace')
                    image_file_path = os.path.join(new_folder_path, f'{drop_event.value}.png')
                    plt.savefig(image_file_path, dpi=300, bbox_inches='tight')
                    plt.close(fig)

                    df_lm = df_lm.rename(columns={'new_cage': 'Cage', 'new_totallength': 'Totallength'})
        else :
            return
    else :
        return

def Start_Analyzis():
    # Launch to analyze the data
    display(tab1)
    interactive_plot = widgets.interactive_output(update_dropdown,
                                                  {'date': drop_injection_plot,
                                                   'cage': drop_cage_plot,
                                                   # 'night_phase': drop_night_plot,
                                                   'event': drop_event,
                                                   'range_slide_plot': range_slide_plot})
    display(interactive_plot)

    interactive_stats = widgets.interactive_output(update_stats,
                                                   {'date': drop_injection_stat,
                                                    'genos': genos,
                                                    'cage': drop_cage_stat,
                                                    # 'night_phase': drop_night_stat,
                                                    'event': drop_event,
                                                    'choice_type': choicetype,
                                                    'range_slide_stats': range_slide_stats})
    display(interactive_stats)


# def results_update_stats(date, genos, cage, night_phase, event, choice_type, range_slide_stats):
#     '''
#     Same figure as the 'update_stats'
#     This function is just for the widget 'statbutton' that will return plot of each values in the widget 'drop_event' in a new folder
#     named by the user. Relaunch the cell if another folder need to be created
#     '''
#     for r_drop_event in drop_event.options:
#         clear_output()
#         new_column_names_clk = []
#         ids = [i for i in df.GenoA.unique()]
#         min_value_stats, max_value_stats = range_slide_stats
#         dfs_clk = []
#         if drop_stat.value == "Linear Mixed Model":
#             # Créer un nouveau dossier pour les fichiers
#             new_folder_path = str(nom_dossier_stats.value)
#             if not os.path.exists(new_folder_path):
#                 os.makedirs(new_folder_path)
#             if choicetype.value == 'Number of events':
#                 for date_val, genos_val, cage_val, night_phase_val in itertools.product(date, genos, cage, night_phase):
#                     temp_df_loop_clk = df[(df["Injection"] == date_val)
#                                           & (df["GenoA"] == genos_val)
#                                           & (df["Cage"] == cage_val)
#                                           & (df["name"] == r_drop_event)
#                                           & (df["Night-Phase"] == night_phase_val)]
#                     # Créer un nouveau dataframe avec toutes les colonnes de l'ancien dataframe
#                     df_new_clk = temp_df_loop_clk.copy()
#                     # Ajouter une colonne avec la somme des numberOfEvents de chaque RFidA de chaque Bin
#                     df_new_clk['new_numbersOfEvents'] = df_new_clk.groupby(['Bin', 'RFidA'])[
#                         'numberOfEvents'].transform('sum')
#                     # Supprimer les lignes utilisées pour faire la somme
#                     df_new_clk = df_new_clk.drop_duplicates(subset=['Bin', 'RFidA'], keep='last')
#                     df_new_clk = df_new_clk[
#                         (df_new_clk['Bin'] >= min_value_stats) & (df_new_clk['Bin'] <= max_value_stats)]
#                     dfs_clk.append(df_new_clk)
#                 merged_df_clk = pd.concat(dfs_clk)
#                 merged_df_clk['new_cage'] = merged_df_clk['Cage'].str.extract('(\d+)').astype(int)
#                 df_lm_clk = merged_df_clk.copy()
#                 df_lm_clk = merged_df_clk.groupby(['new_cage', 'RFidA',
#                                                    'GenoA', 'Date'])['new_numbersOfEvents'].sum().reset_index()
#                 ssdd_clk = statsmodels.stats.descriptivestats.describe(df_lm_clk,
#                                                                        stats=['mean', 'std_err', 'std', 'median'])
#                 model_clk = smf.mixedlm("new_numbersOfEvents ~ GenoA",
#                                         df_lm_clk,
#                                         groups='new_cage')  # Creates the model
#                 result_clk = model_clk.fit()  # Run model
#
#                 df_lm_clk['Dates'] = df_lm_clk.groupby('RFidA')['Date'].transform(lambda x: ', '.join(x.astype(str)))
#                 # Utilisez groupby et cumcount pour attribuer des valeurs "1", "2" ou "3" en fonction de l'ordre des dates pour chaque RFidA
#                 df_lm_clk['New_Column'] = df_lm_clk.groupby('RFidA').cumcount() + 1
#                 df_lm_clk['New_Column'] = df_lm_clk['New_Column'].astype(str)
#                 df_lm_clk = df_lm_clk.sort_values(by=['RFidA', 'new_cage', 'Date']).reset_index(drop=True)
#
#                 new_df_clk = df_lm_clk.loc[:, ['new_cage', 'RFidA']]
#
#                 # Récupérez le nombre de sélections dans le widget
#                 num_selections_clk = len(drop_injection_stat.value)
#
#                 # Récupérez les valeurs de sélections dans le widget
#                 name_selections_clk = list(drop_injection_stat.value)
#
#                 num_select_clk = len(name_selections_clk)
#
#                 # Ajoutez une colonne 'Injection' au DataFrame
#                 df_lm_clk['Injection'] = [name_selections_clk[i % num_select_clk] for i in range(len(df_lm_clk))]
#
#                 # Créez un dictionnaire pour stocker les données pivotées
#                 pivot_data_clk = {'new_cage': [], 'RFidA': []}
#                 for injection in name_selections_clk:
#                     pivot_data_clk[injection] = []
#
#                 # Parcourez les lignes du premier DataFrame
#                 for _, row in df_lm_clk.iterrows():
#                     liste_newcage_clk = row['new_cage']
#                     liste_RFidA_clk = row['RFidA']
#                     liste_injection_clk = row['Injection']
#                     liste_nbevents_clk = row['new_numbersOfEvents']
#
#                     # Vérifiez si la valeur de 'Injection' est dans la liste sélectionnée
#                     if liste_injection_clk in name_selections_clk:
#                         pivot_data_clk['new_cage'].append(liste_newcage_clk)
#                         pivot_data_clk['RFidA'].append(liste_RFidA_clk)
#                         for selected_injection in name_selections_clk:
#                             if selected_injection == liste_injection_clk:
#                                 pivot_data_clk[selected_injection].append(liste_nbevents_clk)
#                             else:
#                                 pivot_data_clk[selected_injection].append(None)
#
#                 # Créez un DataFrame à partir du dictionnaire pivoté
#                 pivot_df_clk = pd.DataFrame(pivot_data_clk)
#
#                 # Fusionnez df2 avec le DataFrame pivoté
#                 result_df_clk = pd.merge(new_df_clk, pivot_df_clk, on=['new_cage', 'RFidA'], how='left')
#
#                 # Groupez le résultat par 'new_cage' et 'RFidA' et agrégez les valeurs
#                 result_df_clk = result_df_clk.groupby(['new_cage', 'RFidA'])[name_selections_clk].first().reset_index()
#
#                 # Remplacez les valeurs NaN par 'None'
#                 result_df_clk = result_df_clk.fillna('0')
#                 result_df_clk.reset_index(drop=True, inplace=True)
#                 result_df_clk.insert(0, 'Index', range(len(result_df_clk)))
#
#                 # Réinitialisez l'index du deuxième DataFrame
#                 new_df_clk = new_df_clk.reset_index(drop=True)
#
#                 # Convertir toutes les colonnes sauf 'Index', 'new_cage', et 'RFidA' en int64
#                 result_df_clk[result_df_clk.columns.difference(['Index', 'new_cage', 'RFidA'])] = result_df_clk[
#                     result_df_clk.columns.difference(['Index', 'new_cage', 'RFidA'])].astype('int64')
#                 result_df_clk
#                 pivot_df2_clk = df_lm_clk.pivot(index=['RFidA', 'new_cage'],
#                                                 columns='Date',
#                                                 values='new_numbersOfEvents').reset_index()
#                 pivot_df2_clk.sort_values('new_cage',
#                                           inplace=True)
#
#                 two_groups_paired_baseline_clk = dabest.load(data=result_df_clk,
#                                                              idx=list(drop_injection_stat.value),
#                                                              id_col="Index",
#                                                              paired='baseline')
#
#                 fig, axs = plt.subplots(1, 3,
#                                         figsize=(30, 12))
#                 fig.subplots_adjust(wspace=0.8)
#
#                 # 1er plot
#                 plotdabest_clk = dabest.load(data=df_lm_clk,
#                                              x="GenoA",
#                                              y="new_numbersOfEvents",
#                                              idx=list(genos),
#                                              id_col="new_cage")
#
#                 # Tracer le graphique
#                 plotdabest_clk.mean_diff.plot(ax=axs[0],
#                                               color_col='new_cage')
#                 axs[0].set_title(f"""Sum of numberOfEvents per Cage for the '{drop_event.value}' event""",
#                                  loc='left')
#
#                 # 2ème plot
#                 if len(drop_injection_stat.value) == 2:
#                     ax1 = two_groups_paired_baseline_clk.mean_diff.plot(color_col='new_cage',
#                                                                         ax=axs[1])
#                     axs[1].legend(title='Cage',
#                                   labels=result_df_clk['new_cage'].unique(),
#                                   frameon=False,
#                                   loc=(1.62, 0.75))
#                 elif len(drop_injection_stat.value) > 2:
#                     ax1 = two_groups_paired_baseline_clk.mean_diff.plot(color_col='new_cage',
#                                                                         ax=axs[1])
#                     axs[1].legend(title='Cage',
#                                   labels=result_df_clk['new_cage'].unique(),
#                                   frameon=False,
#                                   loc=(0.95, 0.75))
#
#                 # 3ème plot
#                 axs[2].axis('off')
#                 table0 = tabulate(ssdd_clk,
#                                   headers="keys",
#                                   colalign=("center", "center", "center", "center", "center"))
#                 axs[2].annotate(table0,
#                                 xy=(-0.45, 0.75),
#                                 xycoords='axes fraction',
#                                 fontsize=10, va='top',
#                                 family='monospace')
#                 table1 = tabulate(result_clk.summary().tables[0],
#                                   colalign=("center", "center", "center", "center", "center"))
#                 axs[2].annotate(table1,
#                                 xy=(-0.45, 0.55),
#                                 xycoords='axes fraction',
#                                 fontsize=10,
#                                 va='top',
#                                 family='monospace')
#                 table2 = tabulate(result_clk.summary().tables[1],
#                                   headers="keys",
#                                   tablefmt="plain",
#                                   colalign=("center", "center", "center", "center", "center", "center", "center"))
#                 axs[2].annotate(table2,
#                                 xy=(-0.45, 0.35),
#                                 xycoords='axes fraction',
#                                 fontsize=10,
#                                 va='top',
#                                 family='monospace')
#                 image_file_path = os.path.join(new_folder_path, f'{r_drop_event}.png')
#                 plt.savefig(image_file_path,
#                             dpi=300,
#                             bbox_inches='tight')
#                 plt.close(fig)
#             elif choicetype.value == 'Event duration':
#                 for date_val, cage_val, night_phase_val in itertools.product(date, cage, night_phase):
#                     temp_df_loop_clk = df[(df["Injection"] == date_val)
#                                           & (df["Cage"] == cage_val)
#                                           & (df["name"] == r_drop_event)
#                                           & (df["Night-Phase"] == night_phase_val)]
#                     # Créer un nouveau dataframe avec toutes les colonnes de l'ancien dataframe
#                     df_new_clk = temp_df_loop_clk.copy()
#                     # Ajouter une colonne avec la somme des numberOfEvents de chaque RFidA de chaque Bin
#                     df_new_clk['new_totallength'] = df_new_clk.groupby(['Bin',
#                                                                         'RFidA'])['totalLength'].transform('sum')
#                     # Supprimer les lignes utilisées pour faire la somme
#                     df_new_clk = df_new_clk.drop_duplicates(subset=['Bin', 'RFidA'],
#                                                             keep='last')
#                     df_new_clk = df_new_clk[
#                         (df_new_clk['Bin'] >= min_value_stats) & (df_new_clk['Bin'] <= max_value_stats)]
#                     dfs_clk.append(df_new_clk)
#                 merged_df_clk = pd.concat(dfs_clk)
#                 merged_df_clk['new_cage'] = merged_df_clk['Cage'].str.extract('(\d+)').astype(int)
#                 df_lm_clk = merged_df_clk.copy()
#                 df_lm_clk = merged_df_clk.groupby(['new_cage', 'RFidA',
#                                                    'GenoA', 'Date'])['new_totallength'].sum().reset_index()
#                 ssdd_clk = statsmodels.stats.descriptivestats.describe(df_lm_clk,
#                                                                        stats=['mean', 'std_err', 'std', 'median'])
#                 model_clk = smf.mixedlm("new_totallength ~ GenoA",
#                                         df_lm_clk,
#                                         groups='new_cage')  # Creates the model
#                 result_clk = model_clk.fit()  # Run model
#
#                 df_lm_clk['Dates'] = df_lm_clk.groupby('RFidA')['Date'].transform(lambda x: ', '.join(x.astype(str)))
#                 # Utilisez groupby et cumcount pour attribuer des valeurs "1", "2" ou "3" en fonction de l'ordre des dates pour chaque RFidA
#                 df_lm_clk['New_Column'] = df_lm_clk.groupby('RFidA').cumcount() + 1
#                 df_lm_clk['New_Column'] = df_lm_clk['New_Column'].astype(str)
#                 df_lm_clk = df_lm_clk.sort_values(by=['RFidA', 'new_cage', 'Date']).reset_index(drop=True)
#
#                 new_df_clk = df_lm_clk.loc[:, ['new_cage', 'RFidA']]
#
#                 # Récupérez le nombre de sélections dans le widget
#                 num_selections = len(drop_injection_stat.value)
#
#                 # Récupérez les valeurs de sélections dans le widget
#                 name_selections_clk = list(drop_injection_stat.value)
#
#                 num_select_clk = len(name_selections_clk)
#
#                 # Ajoutez une colonne 'Injection' au DataFrame
#                 df_lm_clk['Injection'] = [name_selections_clk[i % num_select_clk] for i in range(len(df_lm_clk))]
#
#                 # Créez un dictionnaire pour stocker les données pivotées
#                 pivot_data_clk = {'new_cage': [], 'RFidA': []}
#                 for injection in name_selections_clk:
#                     pivot_data_clk[injection] = []
#
#                 # Parcourez les lignes du premier DataFrame
#                 for _, row in df_lm_clk.iterrows():
#                     liste_newcage_clk = row['new_cage']
#                     liste_RFidA_clk = row['RFidA']
#                     liste_injection_clk = row['Injection']
#                     liste_nbevents_clk = row['new_totallength']
#
#                     # Vérifiez si la valeur de 'Injection' est dans la liste sélectionnée
#                     if liste_injection_clk in name_selections_clk:
#                         pivot_data_clk['new_cage'].append(liste_newcage_clk)
#                         pivot_data_clk['RFidA'].append(liste_RFidA_clk)
#                         for selected_injection in name_selections_clk:
#                             if selected_injection == liste_injection_clk:
#                                 pivot_data_clk[selected_injection].append(liste_nbevents_clk)
#                             else:
#                                 pivot_data_clk[selected_injection].append(None)
#
#                 # Créez un DataFrame à partir du dictionnaire pivoté
#                 pivot_df_clk = pd.DataFrame(pivot_data_clk)
#
#                 # Fusionnez df2 avec le DataFrame pivoté
#                 result_df_clk = pd.merge(new_df_clk, pivot_df_clk, on=['new_cage', 'RFidA'], how='left')
#
#                 # Groupez le résultat par 'new_cage' et 'RFidA' et agrégez les valeurs
#                 result_df_clk = result_df_clk.groupby(['new_cage', 'RFidA'])[name_selections_clk].first().reset_index()
#
#                 # Remplacez les valeurs NaN par 'None'
#                 result_df_clk = result_df_clk.fillna('0')
#                 result_df_clk.reset_index(drop=True, inplace=True)
#                 result_df_clk.insert(0, 'Index', range(len(result_df_clk)))
#
#                 # Réinitialisez l'index du deuxième DataFrame
#                 new_df_clk = new_df_clk.reset_index(drop=True)
#
#                 # Convertir toutes les colonnes sauf 'Index', 'new_cage', et 'RFidA' en int64
#                 result_df_clk[result_df_clk.columns.difference(['Index', 'new_cage', 'RFidA'])] = result_df_clk[
#                     result_df_clk.columns.difference(['Index', 'new_cage', 'RFidA'])].astype('int64')
#                 result_df_clk
#                 pivot_df2_clk = df_lm_clk.pivot(index=['RFidA', 'new_cage'],
#                                                 columns='Date',
#                                                 values='new_totallength').reset_index()
#                 pivot_df2_clk.sort_values('new_cage',
#                                           inplace=True)
#
#                 two_groups_paired_baseline = dabest.load(data=result_df_clk,
#                                                          idx=list(drop_injection_stat.value),
#                                                          id_col="Index",
#                                                          paired='baseline')
#
#                 fig, axs = plt.subplots(1, 3,
#                                         figsize=(30, 12))
#                 fig.subplots_adjust(wspace=0.8)
#
#                 # 1er plot
#                 plotdabest = dabest.load(data=df_lm_clk,
#                                          x="GenoA",
#                                          y="new_totallength",
#                                          idx=list(genos),
#                                          id_col="new_cage")
#
#                 # Tracer le graphique
#                 plotdabest.mean_diff.plot(ax=axs[0],
#                                           color_col='new_cage')
#                 axs[0].set_title(f"""Sum of totalLength per Cage for the '{drop_event.value}' event""",
#                                  loc='left')
#
#                 # 2ème plot
#                 if len(drop_injection_stat.value) == 2:
#                     ax1 = two_groups_paired_baseline.mean_diff.plot(color_col='new_cage',
#                                                                     ax=axs[1])
#                     axs[1].legend(title='Cage',
#                                   labels=result_df_clk['new_cage'].unique(),
#                                   frameon=False,
#                                   loc=(1.62, 0.75))
#                 elif len(drop_injection_stat.value) > 2:
#                     ax1 = two_groups_paired_baseline.mean_diff.plot(color_col='new_cage',
#                                                                     ax=axs[1])
#                     axs[1].legend(title='Cage',
#                                   labels=result_df_clk['new_cage'].unique(),
#                                   frameon=False,
#                                   loc=(0.95, 0.75))
#
#                 # 3ème plot
#                 axs[2].axis('off')
#                 table0 = tabulate(ssdd_clk,
#                                   headers="keys",
#                                   colalign=("center", "center", "center", "center", "center"))
#                 axs[2].annotate(table0,
#                                 xy=(-0.45, 0.75),
#                                 xycoords='axes fraction',
#                                 fontsize=10, va='top',
#                                 family='monospace')
#                 table1 = tabulate(result_clk.summary().tables[0],
#                                   colalign=("center", "center", "center", "center", "center"))
#                 axs[2].annotate(table1,
#                                 xy=(-0.45, 0.55),
#                                 xycoords='axes fraction',
#                                 fontsize=10,
#                                 va='top',
#                                 family='monospace')
#                 table2 = tabulate(result_clk.summary().tables[1],
#                                   headers="keys",
#                                   tablefmt="plain",
#                                   colalign=("center", "center", "center", "center", "center", "center", "center"))
#                 axs[2].annotate(table2,
#                                 xy=(-0.45, 0.35),
#                                 xycoords='axes fraction',
#                                 fontsize=10,
#                                 va='top',
#                                 family='monospace')
#                 image_file_path = os.path.join(new_folder_path, f'{r_drop_event}.png')
#                 plt.savefig(image_file_path,
#                             dpi=300,
#                             bbox_inches='tight')
#                 plt.close(fig)
#             else:
#                 return
#         else:
#             return

# interactive_plot = widgets.interactive_output(update_dropdown,
#                                               {'date': drop_injection_plot,
#                                                'cage': drop_cage_plot,
#                                                'night_phase': drop_night_plot,
#                                                'event': drop_event})
# display(interactive_plot)
#
# interactive_stats = widgets.interactive_output(update_stats,
#                                                {'date': drop_injection_stat,
#                                                 'cage': drop_cage_stat,
#                                                 'night_phase': drop_night_stat,
#                                                 'event': drop_event,
#                                                 'choice_type':choicetype})
# display(interactive_stats)
