import sys

sys.path.insert(1, "../")

from IPython.display import Markdown, display, clear_output
import ipywidgets as widgets
from ipywidgets import *
from tkinter.filedialog import askopenfilename
from lmtanalysis.FileUtil import getCsvFileToProcess
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
import dabest
import random
import os
import csv
import itertools
import scipy
from scipy import stats
from scipy.stats import wilcoxon
import statsmodels
import statsmodels.api as sm
import statsmodels.formula.api as smf
from tabulate import tabulate
import warnings

warnings.filterwarnings('ignore')

pd.set_option('display.max_columns', None)
pd.set_option('max_colwidth', None)

# Read csv
path = getCsvFileToProcess()
df = pd.read_csv(path)

# Remplacement des injections
remplacement = {'weekend1': '(1)weekend1', '1-3NaCl': '(2)3NaCl',
                '2-1Amphet': '(3)1Amphet', '3-1Amphet': '(4)1Amphet',
                '4-1Amphet': '(5)1Amphet', 'weekend2': '(6)weekend2',
                '5-3Amphet': '(7)3Amphet', '6-3Amphet': '(8)3Amphet',
                '7-3Amphet': '(9)3Amphet'}

# Utilisation de la méthode "replace" pour remplacer les valeurs
df['Injection'] = df['Injection'].replace(remplacement)

# Définition de variables
date = df["Date"].unique()
injection = df["Injection"].unique()
cage = df["Cage"].unique()
night_phase = df["Night-Phase"].unique()
event = df["name"].unique()

# Organisation boutons Ipywidgets
style = {'description_width': '100px'}
layout = widgets.Layout(width='300px',
                        height='25px')
# Boutons 'reset selection'
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

# Selection du type d'analyse "Number" ou "Duration"
data_type = ["Number of events", "Event duration"]
choicetype = widgets.Dropdown(options=data_type,
                              value=data_type[0],
                              description='Type',
                              style={'description_width': '120px'},
                              disable=False)

# Selection pour les Repeated Measures de Dabest
dabest_type = ["1", "2", "3"]
statstype = widgets.Dropdown(options=dabest_type,
                             value=dabest_type[0],
                             description='Repetition (in days)',
                             disabled=False,
                             layout=widgets.Layout(width='300px', height='25px'),
                             style={'description_width': '200px'})

# Créations des widgets
# drop_injection_plot = sélection du jour de l'injection pour les plots
drop_injection_plot = widgets.SelectMultiple(options=injection,
                                             rows=5,
                                             description='Injection',
                                             disabled=False)

# drop_cage_plot = sélection de la cage pour les plots
drop_cage_plot = widgets.SelectMultiple(options=cage,
                                        rows=5,
                                        description='Cage',
                                        disabled=False)

# drop_event = sélection du comportement pour les plots
drop_event = widgets.Dropdown(options=event,
                              value=event[1],
                              description='Event:',
                              disabled=False)

# drop_night_plot = sélection de la nuit pour les plots
drop_night_plot = widgets.SelectMultiple(options=night_phase,
                                         rows=5,
                                         description='Night_Phase',
                                         disabled=False)

# drop_stat = sélection du type de stats (pour l'instant que le Mixed-Model
stats = ['Mixed Model', 'Non-Mixed Model']
drop_stat = widgets.Dropdown(options=stats,
                             value=stats[0],
                             description='Statistic:',
                             style=style,
                             disabled=False)

# drop_injection_plot = sélection du jour de l'injection pour les stats
drop_injection_stat = widgets.SelectMultiple(options=injection,
                                             rows=5,
                                             description='Injection',
                                             style=style,
                                             disabled=False)

# drop_cage_plot = sélection de la cage pour les stats
drop_cage_stat = widgets.SelectMultiple(options=cage,
                                        rows=5,
                                        description='Cage',
                                        style=style,
                                        disabled=False)

# drop_night_plot = sélection de la nuit pour les stats
drop_night_stat = widgets.SelectMultiple(options=night_phase,
                                         rows=5,
                                         description='Night_Phase',
                                         style=style,
                                         disabled=False)

# création widget nom_fichier
nom_dossier = widgets.Text(placeholder='Type here',
                           description='Folder name:',
                           style=style,
                           disabled=False)

# création du widget bouton
statbutton = widgets.Button(description="Stats exportation",
                            layout=layout,
                            style=style)

# création du widget IntRangeSlider
range_slide_plot = widgets.IntRangeSlider(value=[0, max(df['Bin'])],
                                     min=0,
                                     max=max(df['Bin']),step=1,
                                     description='Bins :',
                                     disabled=False,
                                     continuous_update=False,
                                     orientation='horizontal',
                                     readout=True,
                                     readout_format='d')

# création du widget IntRangeSlider
range_slide_stats = widgets.IntRangeSlider(value=[0, max(df['Bin'])],
                                     min=0,
                                     max=max(df['Bin']),step=1,
                                     description='Bins :',
                                     disabled=False,
                                     continuous_update=False,
                                     orientation='horizontal',
                                     readout=True,
                                     readout_format='d')

# Affectation de la fonction 'results_update_stats' au bouton 'statbutton'
def get_plots_stats_button(statbutton):
    interactive_results_stats = widgets.interactive_output(results_update_stats,
                                                           {'date': drop_injection_stat,
                                                            'cage': drop_cage_stat,
                                                            'night_phase': drop_night_stat,
                                                            'event': drop_event,
                                                            'choice_type': choicetype,
                                                            'stats_type': statstype,
                                                            'range_slide_stats': range_slide_stats})


# Associer la fonction on_button_click à l'événement de clic du bouton
statbutton.on_click(get_plots_stats_button)

# Association des widgets aux onglets
box1 = VBox([plot_reset,
             range_slide_plot,
             drop_injection_plot,
             drop_cage_plot,
             drop_night_plot,
             drop_event])
box2 = VBox([stat_reset,
             range_slide_stats,
             drop_stat,
             drop_injection_stat,
             drop_cage_stat,
             drop_night_stat,
             drop_event,
             statstype,
             nom_dossier,
             statbutton])

# Création de l'onglet pour les widgets
tab0 = widgets.VBox(children=[animalnumber, choicetype])
tab1 = widgets.Tab(children=[box1])
tab2 = widgets.VBox(children=[box2])
tab1.children = (tab0,) + tab1.children + tab2.children
tab1.set_title(0, 'Animals')
tab1.set_title(1, 'Plot')
tab1.set_title(2, 'Stats')

# Affichage de tab
# display(tab1)

# Liste des évènements existants dans les bases de données actuelles
event_options = {
    'Isolated beh. (eg:Rearing, SAP,...)': ["Move isolated", "Rearing", "Rear isolated", "Stop isolated", "SAP", "Distance"],
    'Beh. involving 2 mice': ["Contact", "Oral-oral Contact", "Oral-genital Contact", "Side by side Contact",
                              "Side by side Contact, opposite way", "Social approach", "Social escape",
                              "Approach contact", "Approach rear", "Break contact", "Get away",
                              "FollowZone Isolated", "Train2", "Group2"],
    'Beh. involving 3 mice': ["Group3"],
    'Beh. involving 4 mice': ["Group4", "Nest3", "Nest4"]}


# Mise à jour des évènements (drop_event) en fonction de la sélection du widget 'animalnumber'
def update_event_options(change):
    selected_animalnumber = animalnumber.value
    selected_options = []
    for behavior in selected_animalnumber:
        selected_options += event_options[behavior]
    drop_event.options = selected_options


animalnumber.observe(update_event_options, names='value')


# Fonction de mise à jour des sélections de l'onglet 'Plot' après clic du bouton 'plot_reset'
def reset_plot_selections(plot_reset):
    drop_injection_plot.value = ()
    drop_cage_plot.options = df['Cage'].unique()
    drop_night_plot.options = df['Night-Phase'].unique()


plot_reset.on_click(reset_plot_selections)


# Fonction de mise à jour des sélections de l'onglet 'Stat' après clic du bouton 'stat_reset'
def reset_stats_selections(stat_reset):
    drop_injection_stat.value = ()
    drop_cage_stat.options = df['Cage'].unique()
    drop_night_stat.options = df['Night-Phase'].unique()


stat_reset.on_click(reset_stats_selections)

# Pour sélectionner plusieurs Dates
def update_options_plot(change):
    # Filtrer les données du DataFrame en fonction des valeurs sélectionnées dans drop_injection_plot
    filtered_df = df[df['Injection'].isin(drop_injection_plot.value)]

    # Mettre à jour les options de drop_cage_plot avec les valeurs uniques de la colonne "Cage" pour les données filtrées
    cage_options_plot = filtered_df['Cage'].unique()
    drop_cage_plot.options = cage_options_plot

    # Conserver les valeurs sélectionnées dans drop_cage_plot si elles sont encore valides après la mise à jour des options
    drop_cage_plot.value = list(set(drop_cage_plot.value)
                                & set(cage_options_plot))

    # Mettre à jour les options de drop_night_plot avec les valeurs uniques de la colonne "Night-Phase" pour les données filtrées
    night_options_plot = filtered_df['Night-Phase'].unique()
    drop_night_plot.options = night_options_plot

    # Conserver les valeurs sélectionnées dans drop_night_plot si elles sont encore valides après la mise à jour des options
    drop_night_plot.value = list(set(drop_night_plot.value)
                                 & set(night_options_plot))


# Assigner la fonction update_options à l'événement "observe" de drop_injection_plot
drop_injection_plot.observe(update_options_plot, names='value')


def update_options_stat(change):
    # Filtrer les données du DataFrame en fonction des valeurs sélectionnées dans drop_injection_stat
    filtered_df = df[df['Injection'].isin(drop_injection_stat.value)]

    # Mettre à jour les options de drop2 avec les valeurs uniques de la colonne "Cage" pour les données filtrées
    cage_options_stats = filtered_df['Cage'].unique()
    drop_cage_stat.options = cage_options_stats

    # Conserver les valeurs sélectionnées dans drop2 si elles sont encore valides après la mise à jour des options
    drop_cage_stat.value = list(set(drop_cage_stat.value)
                                & set(cage_options_stats))

    # Mettre à jour les options de drop4 avec les valeurs uniques de la colonne "Night-Phase" pour les données filtrées
    night_options_stats = filtered_df['Night-Phase'].unique()
    drop_night_stat.options = night_options_stats

    # Conserver les valeurs sélectionnées dans drop4 si elles sont encore valides après la mise à jour des options
    drop_night_stat.value = list(set(drop_night_stat.value)
                                 & set(night_options_stats))


# Assigner la fonction update_options à l'événement "observe" de drop_injection_stat
drop_injection_stat.observe(update_options_stat, names='value')


def update_temp_df(change):
    # Mise à jour de temp_df en fonction de la sélection actuelle des widgets
    global temp_df
    temp_df = df[(df["Injection"].isin(drop_injection_plot.value))
                 & (df["Cage"].isin(drop_cage_plot.value))
                 & (df["name"] == drop_event.value)
                 & (df["Night-Phase"].isin(drop_night_plot.value))]


# Initialisation de temp_df en fonction de la sélection initiale des widgets
temp_df = df[(df["Injection"].isin(drop_injection_plot.value))
             & (df["Cage"].isin(drop_cage_plot.value))
             & (df["name"] == drop_event.value)
             & (df["Night-Phase"].isin(drop_night_plot.value))]

# Observation des widgets pour mettre à jour temp_df lorsque la sélection est modifiée
drop_injection_plot.observe(update_temp_df, 'value')
drop_cage_plot.observe(update_temp_df, 'value')
drop_event.observe(update_temp_df, 'value')
drop_night_plot.observe(update_temp_df, 'value')

# colors for plots
colors = {j: sns.color_palette("husl", len(df.GenoA.unique()))[i] for i, j in enumerate(sorted(df.GenoA.unique()))}


# Fonction pour afficher le plot en fonction des choix de l'utilisateur
def update_dropdown(date, cage, night_phase, event, range_slide_plot):
    '''
    This function will compute the 'number of event' or the 'event duration' per bin for each mice in the cage
    '''
    clear_output()
    min_value_plot, max_value_plot = range_slide_plot
    sns.set(font_scale=1.2, style='ticks')
    if choicetype.value == 'Number of events':
        for date_val, cage_val, night_phase_val in itertools.product(date, cage, night_phase):
            display(Markdown(
                f"""<h3>L'analyse est réalisée sur {animalnumber.value[0]} souris, l'injection choisie est '{date_val}', 
                             il s'agit de la {cage_val} pour l'évènement '{drop_event.value}' durant la phase {night_phase_val}
                             de nuit !</h3>"""))
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
                f"""<h3>L'analyse est réalisée sur {animalnumber.value[0]} souris, l'injection choisie est '{date_val}', 
                             il s'agit de la {cage_val} pour l'évènement '{drop_event.value}' durant la phase {night_phase_val}
                             de nuit !</h3>"""))
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


# ids = [i for i in df.GenoA.unique()]


def update_stats(date, cage, night_phase, event, choice_type, stats_type, range_slide_stats):
    '''
    This function will return a figure with 3 plots:
    . The first with the dabest package that will compare the selected data (eg. NaCl/Amphet)
    . The second with the dabest package that will compare the different injections
    . The third that is the summary of the statsmodels.stats.descriptivestats.describe() function
    '''
    clear_output()
    dfs = []
    ids = [i for i in df.GenoA.unique()]
    min_value_stats, max_value_stats = range_slide_stats
    if choicetype.value == 'Number of events':
        for date_val, cage_val, night_phase_val in itertools.product(date, cage, night_phase):
            # display(Markdown(f"""<h3>L'analyse est réalisée sur {animalnumber.value[0]} souris, l'injection 
            # choisie est '{date_val}', 
            # il s'agit de la {cage_val} pour l'évènement '{drop_event.value}' durant la phase {night_phase_val} 
            # de nuit !</h3>"""))
            temp_df_loop1 = df[(df["Injection"] == date_val)
                               & (df["Cage"] == cage_val)
                               & (df["name"] == drop_event.value)
                               & (df["Night-Phase"] == night_phase_val)]
            # Créer un nouveau dataframe avec toutes les colonnes de l'ancien dataframe
            df_new = temp_df_loop1.copy()
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
            df_lm = merged_df.copy()
            df_lm = merged_df.groupby(['new_cage', 'RFidA', 'GenoA', 'Date'])['new_numbersOfEvents'].sum().reset_index()
            # Compute Mixed Models stats

            if drop_stat.value == "Mixed Model":
                ssdd = statsmodels.stats.descriptivestats.describe(df_lm,
                                                                   stats=['mean', 'std_err', 'std', 'median'])
                model = smf.mixedlm("new_numbersOfEvents ~ GenoA",
                                    df_lm,
                                    groups='new_cage')  # Creates the model
                result = model.fit()  # Run model
                pivot_df2 = df_lm.pivot(index=['RFidA', 'new_cage'],
                                        columns='Date',
                                        values='new_numbersOfEvents').reset_index()
                pivot_df2.sort_values('new_cage',
                                      inplace=True)

                # Créer les 4 nouvelles colonnes et les remplir avec les valeurs de la 3ème colonne à la dernière colonne
                pivot_df2['Control'] = pivot_df2.iloc[:, 2::4].sum(axis=1)
                pivot_df2['Day1'] = pivot_df2.iloc[:, 3::4].sum(axis=1)
                pivot_df2['Day2'] = pivot_df2.iloc[:, 4::4].sum(axis=1)
                pivot_df2['Day3'] = pivot_df2.iloc[:, 5::4].sum(axis=1)

                # création de la colonne avec l'index
                pivot_df2.reset_index(inplace=True)
                pivot_df2.index = range(len(pivot_df2))
                pivot_df2.index.name = 'Index'
                pivot_df2['Index'] = pivot_df2.index.astype(int)

                if len(drop_injection_stat.value) == 2:
                    two_groups_paired_baseline = dabest.load(data=pivot_df2,
                                                             idx=("Control", "Day1"),
                                                             id_col="Index",
                                                             paired='baseline')
                elif len(drop_injection_stat.value) == 3:
                    two_groups_paired_baseline = dabest.load(data=pivot_df2,
                                                             idx=("Control", "Day1", "Day2"),
                                                             id_col="Index",
                                                             paired='baseline')
                elif len(drop_injection_stat.value) == 4:
                    two_groups_paired_baseline = dabest.load(data=pivot_df2,
                                                             idx=("Control", "Day1", "Day2", "Day3"),
                                                             id_col="Index",
                                                             paired='baseline')

                fig, axs = plt.subplots(1, 3,
                                        figsize=(30, 12))
                fig.subplots_adjust(wspace=0.8)

                # 1er plot
                plotdabest = dabest.load(data=df_lm,
                                         x="GenoA",
                                         y="new_numbersOfEvents",
                                         idx=ids,
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
                                  labels=pivot_df2['new_cage'].unique(),
                                  frameon=False,
                                  loc=(1.62, 0.75))
                elif len(drop_injection_stat.value) > 2:
                    ax1 = two_groups_paired_baseline.mean_diff.plot(color_col='new_cage',
                                                                    ax=axs[1])
                    axs[1].legend(title='Cage',
                                  labels=pivot_df2['new_cage'].unique(),
                                  frameon=False,
                                  loc=(0.95, 0.75))

                # 3ème plot
                axs[2].axis('off')
                table0 = tabulate(ssdd,
                                  headers="keys",
                                  colalign=("center", "center", "center", "center", "center"))
                axs[2].annotate(table0,
                                xy=(-0.25, 0.75),
                                xycoords='axes fraction',
                                fontsize=10, va='top',
                                family='monospace')
                table1 = tabulate(result.summary().tables[0],
                                  colalign=("center", "center", "center", "center", "center"))
                axs[2].annotate(table1,
                                xy=(-0.25, 0.55),
                                xycoords='axes fraction',
                                fontsize=10,
                                va='top',
                                family='monospace')
                table2 = tabulate(result.summary().tables[1],
                                  headers="keys",
                                  tablefmt="plain",
                                  colalign=("center", "center", "center", "center", "center", "center", "center"))
                axs[2].annotate(table2,
                                xy=(-0.25, 0.35),
                                xycoords='axes fraction',
                                fontsize=10,
                                va='top',
                                family='monospace')

            else:
                return

    elif choicetype.value == 'Event duration':
        for date_val, cage_val, night_phase_val in itertools.product(date, cage, night_phase):
            # display(Markdown(f"<h3>L'analyse est réalisée sur {animalnumber.value[0]} souris, 
            # l'injection choisie est '{date_val}', il s'agit de la {cage_val} pour l'évènement 
            # '{drop_event.value}' durant la phase {night_phase_val} de nuit !</h3>"))
            temp_df_loop1 = df[(df["Injection"] == date_val)
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
            # fig, ax1 = plt.subplots(figsize=(10,4))
            # ax2 = fig.add_axes([1, 0.25, 0.25, 0.5])
            # sns.barplot(data=df_new, y='new_totallength', x="GenoA", palette={'Amphet':'red', 'NaCl':'blue'}, ax=ax2)
            # ax2.set_title("A barplot")
            # plt.show()
            dfs.append(df_new)

        if not dfs:
            return

        else:
            merged_df = pd.concat(dfs)
            merged_df['new_cage'] = merged_df['Cage'].str.extract('(\d+)').astype(int)
            df_lm = merged_df.copy()
            df_lm = merged_df.groupby(['new_cage', 'RFidA', 'GenoA', 'Date'])['new_totallength'].sum().reset_index()

            if drop_stat.value == "Mixed Model":
                ssdd = statsmodels.stats.descriptivestats.describe(df_lm,
                                                                   stats=['mean', 'std_err', 'std', 'median'])
                model = smf.mixedlm("new_totallength ~ GenoA",
                                    df_lm,
                                    groups='new_cage')  # Creates the model
                result = model.fit()  # Run model
                pivot_df2 = df_lm.pivot(index=['RFidA', 'new_cage'],
                                        columns='Date',
                                        values='new_totallength').reset_index()
                pivot_df2.sort_values('new_cage',
                                      inplace=True)

                # Créer les 4 nouvelles colonnes et les remplir avec les valeurs de la 3ème colonne à la dernière colonne
                pivot_df2['Control'] = pivot_df2.iloc[:, 2::4].sum(axis=1)
                pivot_df2['Day1'] = pivot_df2.iloc[:, 3::4].sum(axis=1)
                pivot_df2['Day2'] = pivot_df2.iloc[:, 4::4].sum(axis=1)
                pivot_df2['Day3'] = pivot_df2.iloc[:, 5::4].sum(axis=1)

                # création de la colonne avec l'index
                pivot_df2.reset_index(inplace=True)
                pivot_df2.index = range(len(pivot_df2))
                pivot_df2.index.name = 'Index'
                pivot_df2['Index'] = pivot_df2.index.astype(int)

                if len(drop_injection_stat.value) == 2:
                    two_groups_paired_baseline = dabest.load(data=pivot_df2,
                                                             idx=("Control", "Day1"),
                                                             id_col="Index",
                                                             paired='baseline')
                elif len(drop_injection_stat.value) == 3:
                    two_groups_paired_baseline = dabest.load(data=pivot_df2,
                                                             idx=("Control", "Day1", "Day2"),
                                                             id_col="Index",
                                                             paired='baseline')
                elif len(drop_injection_stat.value) == 4:
                    two_groups_paired_baseline = dabest.load(data=pivot_df2,
                                                             idx=("Control", "Day1", "Day2", "Day3"),
                                                             id_col="Index",
                                                             paired='baseline')

                fig, axs = plt.subplots(1, 3,
                                        figsize=(25, 10))
                fig.subplots_adjust(wspace=0.5)

                # 1er plot
                plotdabest = dabest.load(data=df_lm,
                                         x="GenoA",
                                         y="new_totallength",
                                         idx=ids,
                                         id_col="new_cage")

                # Tracer le graphique
                first = plotdabest.mean_diff.plot(color_col='new_cage',
                                                  ax=axs[0])
                axs[0].set_title(f"""Sum of totalLength per Cage for the '{drop_event.value}' event""", loc='left')

                # 2ème plot
                if len(drop_injection_stat.value) == 2:
                    ax1 = two_groups_paired_baseline.mean_diff.plot(color_col='new_cage',
                                                                    ax=axs[1])
                    axs[1].legend(title='Cage',
                                  labels=pivot_df2['new_cage'].unique(),
                                  frameon=False,
                                  loc=(1.62, 0.75))
                elif len(drop_injection_stat.value) > 2:
                    ax1 = two_groups_paired_baseline.mean_diff.plot(color_col='new_cage',
                                                                    ax=axs[1])
                    axs[1].legend(title='Cage',
                                  labels=pivot_df2['new_cage'].unique(),
                                  frameon=False,
                                  loc=(0.95, 0.75))

                # 3ème plot
                axs[2].axis('off')
                table0 = tabulate(ssdd,
                                  headers="keys",
                                  colalign=("center", "center", "center", "center", "center"))
                axs[2].annotate(table0,
                                xy=(-0.25, 0.75),
                                xycoords='axes fraction',
                                fontsize=10,
                                va='top',
                                family='monospace')
                table1 = tabulate(result.summary().tables[0],
                                  colalign=("center", "center", "center", "center", "center"))
                axs[2].annotate(table1,
                                xy=(-0.25, 0.55),
                                xycoords='axes fraction',
                                fontsize=10,
                                va='top',
                                family='monospace')
                table2 = tabulate(result.summary().tables[1],
                                  headers="keys",
                                  tablefmt="plain",
                                  colalign=("center", "center", "center", "center", "center", "center", "center"))
                axs[2].annotate(table2,
                                xy=(-0.25, 0.35),
                                xycoords='axes fraction',
                                fontsize=10,
                                va='top',
                                family='monospace')

            else:
                return

def results_update_stats(date, cage, night_phase, event, choice_type, stats_type, range_slide_stats):
    '''
    Same figure as the 'update_stats'
    This function is just for the widget 'statbutton' that will return plot of each values in the widget 'drop_event' in a new folder
    named by the user. Relaunch the cell if another folder need to be created
    '''
    for r_drop_event in drop_event.options:
        clear_output()
        ids = [i for i in df.GenoA.unique()]
        min_value_stats, max_value_stats = range_slide_stats
        dfs_clk = []
        if drop_stat.value == "Mixed Model":
            # Créer un nouveau dossier pour les fichiers
            new_folder_path = str(nom_dossier.value)
            if not os.path.exists(new_folder_path):
                os.makedirs(new_folder_path)
            if choicetype.value == 'Number of events':
                for date_val, cage_val, night_phase_val in itertools.product(date, cage, night_phase):
                    temp_df_loop_clk = df[(df["Injection"] == date_val)
                                          & (df["Cage"] == cage_val)
                                          & (df["name"] == r_drop_event)
                                          & (df["Night-Phase"] == night_phase_val)]
                    # Créer un nouveau dataframe avec toutes les colonnes de l'ancien dataframe
                    df_new_clk = temp_df_loop_clk.copy()
                    # Ajouter une colonne avec la somme des numberOfEvents de chaque RFidA de chaque Bin
                    df_new_clk['new_numbersOfEvents'] = df_new_clk.groupby(['Bin',
                                                                            'RFidA'])['numberOfEvents'].transform('sum')
                    # Supprimer les lignes utilisées pour faire la somme
                    df_new_clk = df_new_clk.drop_duplicates(subset=['Bin', 'RFidA'],
                                                            keep='last')
                    df_new_clk = df_new_clk[(df_new_clk['Bin'] >= min_value_stats) & (df_new_clk['Bin'] <= max_value_stats)]
                    dfs_clk.append(df_new_clk)
                merged_df_clk = pd.concat(dfs_clk)
                merged_df_clk['new_cage'] = merged_df_clk['Cage'].str.extract('(\d+)').astype(int)
                df_lm_clk = merged_df_clk.copy()
                df_lm_clk = merged_df_clk.groupby(['new_cage', 'RFidA',
                                                   'GenoA', 'Date'])['new_numbersOfEvents'].sum().reset_index()
                ssdd = statsmodels.stats.descriptivestats.describe(df_lm_clk,
                                                                   stats=['mean', 'std_err', 'std', 'median'])
                model = smf.mixedlm("new_numbersOfEvents ~ GenoA",
                                    df_lm_clk,
                                    groups='new_cage')
                result = model.fit()
                pivot_df_clk = df_lm_clk.pivot(index=['RFidA', 'new_cage'],
                                               columns='Date',
                                               values='new_numbersOfEvents').reset_index()
                pivot_df_clk.sort_values('new_cage',
                                         inplace=True)

                # Créer les 4 nouvelles colonnes et les remplir avec les valeurs de la 3ème colonne à la dernière colonne
                pivot_df_clk['Control'] = pivot_df_clk.iloc[:, 2::4].sum(axis=1)
                pivot_df_clk['Day1'] = pivot_df_clk.iloc[:, 3::4].sum(axis=1)
                pivot_df_clk['Day2'] = pivot_df_clk.iloc[:, 4::4].sum(axis=1)
                pivot_df_clk['Day3'] = pivot_df_clk.iloc[:, 5::4].sum(axis=1)

                # création de la colonne avec l'index
                pivot_df_clk.reset_index(inplace=True)
                pivot_df_clk.index = range(len(pivot_df_clk))
                pivot_df_clk.index.name = 'Index'
                pivot_df_clk['Index'] = pivot_df_clk.index.astype(int)

                if len(drop_injection_stat.value) == 2:
                    two_groups_paired_baseline_clk = dabest.load(data=pivot_df_clk,
                                                             idx=("Control", "Day1"),
                                                             id_col="Index",
                                                             paired='baseline')
                elif len(drop_injection_stat.value) == 3:
                    two_groups_paired_baseline_clk = dabest.load(data=pivot_df_clk,
                                                             idx=("Control", "Day1", "Day2"),
                                                             id_col="Index",
                                                             paired='baseline')
                elif len(drop_injection_stat.value) == 4:
                    two_groups_paired_baseline_clk = dabest.load(data=pivot_df_clk,
                                                             idx=("Control", "Day1", "Day2", "Day3"),
                                                             id_col="Index",
                                                             paired='baseline')

                fig, axs = plt.subplots(1, 3,
                                        figsize=(25, 10))
                fig.subplots_adjust(wspace=0.5)

                # 1er plot
                plotdabest_clk = dabest.load(data=df_lm_clk,
                                             x="GenoA",
                                             y="new_numbersOfEvents",
                                             idx=ids,
                                             id_col="new_cage")

                # Tracer le graphique
                plotdabest_clk.mean_diff.plot(ax=axs[0],
                                              color_col='new_cage')
                axs[0].set_title(f"""Sum of numberOfEvents per Cage for the '{r_drop_event}' event""",
                                 loc='left')

                # 2ème plot
                if len(drop_injection_stat.value) == 2:
                    ax1 = two_groups_paired_baseline_clk.mean_diff.plot(color_col='new_cage',
                                                                    ax=axs[1])
                    axs[1].legend(title='Cage',
                                  labels=pivot_df_clk['new_cage'].unique(),
                                  frameon=False,
                                  loc=(1.62, 0.75))
                elif len(drop_injection_stat.value) > 2:
                    ax1 = two_groups_paired_baseline_clk.mean_diff.plot(color_col='new_cage',
                                                                    ax=axs[1])
                    axs[1].legend(title='Cage',
                                  labels=pivot_df_clk['new_cage'].unique(),
                                  frameon=False,
                                  loc=(0.95, 0.75))

                # 3ème plot
                axs[2].axis('off')
                table0 = tabulate(ssdd,
                                  headers="keys",
                                  colalign=("center", "center", "center", "center", "center"))
                axs[2].annotate(table0,
                                xy=(-0.25, 0.75),
                                xycoords='axes fraction',
                                fontsize=10,
                                va='top',
                                family='monospace')
                table1 = tabulate(result.summary().tables[0],
                                  colalign=("center", "center", "center", "center", "center"))
                axs[2].annotate(table1,
                                xy=(-0.25, 0.55),
                                xycoords='axes fraction',
                                fontsize=10,
                                va='top',
                                family='monospace')
                table2 = tabulate(result.summary().tables[1],
                                  headers="keys",
                                  tablefmt="plain",
                                  colalign=("center", "center", "center", "center", "center", "center", "center"))
                axs[2].annotate(table2,
                                xy=(-0.25, 0.35),
                                xycoords='axes fraction',
                                fontsize=10,
                                va='top',
                                family='monospace')
                image_file_path = os.path.join(new_folder_path, f'{r_drop_event}.png')
                plt.savefig(image_file_path,
                            dpi=300,
                            bbox_inches='tight')
                plt.close(fig)
            elif choicetype.value == 'Event duration':
                for date_val, cage_val, night_phase_val in itertools.product(date, cage, night_phase):
                    temp_df_loop_clk = df[(df["Injection"] == date_val)
                                          & (df["Cage"] == cage_val)
                                          & (df["name"] == r_drop_event)
                                          & (df["Night-Phase"] == night_phase_val)]
                    # Créer un nouveau dataframe avec toutes les colonnes de l'ancien dataframe
                    df_new_clk = temp_df_loop_clk.copy()
                    # Ajouter une colonne avec la somme des numberOfEvents de chaque RFidA de chaque Bin
                    df_new_clk['new_totallength'] = df_new_clk.groupby(['Bin',
                                                                        'RFidA'])['totalLength'].transform('sum')
                    # Supprimer les lignes utilisées pour faire la somme
                    df_new_clk = df_new_clk.drop_duplicates(subset=['Bin', 'RFidA'],
                                                            keep='last')
                    df_new_clk = df_new_clk[(df_new_clk['Bin'] >= min_value_stats) & (df_new_clk['Bin'] <= max_value_stats)]
                    dfs_clk.append(df_new_clk)
                merged_df_clk = pd.concat(dfs_clk)
                merged_df_clk['new_cage'] = merged_df_clk['Cage'].str.extract('(\d+)').astype(int)
                df_lm_clk = merged_df_clk.copy()
                df_lm_clk = merged_df_clk.groupby(['new_cage', 'RFidA',
                                                   'GenoA', 'Date'])['new_totallength'].sum().reset_index()
                ssdd = statsmodels.stats.descriptivestats.describe(df_lm_clk,
                                                                   stats=['mean', 'std_err', 'std', 'median'])
                model = smf.mixedlm("new_totallength ~ GenoA",
                                    df_lm_clk,
                                    groups='new_cage')
                result = model.fit()
                pivot_df_clk = df_lm_clk.pivot(index=['RFidA', 'new_cage'],
                                               columns='Date',
                                               values='new_totallength').reset_index()
                pivot_df_clk.sort_values('new_cage',
                                         inplace=True)

                # Créer les 4 nouvelles colonnes et les remplir avec les valeurs de la 3ème colonne à la dernière colonne
                pivot_df_clk['Control'] = pivot_df_clk.iloc[:, 2::4].sum(axis=1)
                pivot_df_clk['Day1'] = pivot_df_clk.iloc[:, 3::4].sum(axis=1)
                pivot_df_clk['Day2'] = pivot_df_clk.iloc[:, 4::4].sum(axis=1)
                pivot_df_clk['Day3'] = pivot_df_clk.iloc[:, 5::4].sum(axis=1)

                # création de la colonne avec l'index
                pivot_df_clk.reset_index(inplace=True)
                pivot_df_clk.index = range(len(pivot_df_clk))
                pivot_df_clk.index.name = 'Index'
                pivot_df_clk['Index'] = pivot_df_clk.index.astype(int)

                if len(drop_injection_stat.value) == 2:
                    two_groups_paired_baseline_clk = dabest.load(data=pivot_df_clk,
                                                             idx=("Control", "Day1"),
                                                             id_col="Index",
                                                             paired='baseline')
                elif len(drop_injection_stat.value) == 3:
                    two_groups_paired_baseline_clk = dabest.load(data=pivot_df_clk,
                                                             idx=("Control", "Day1", "Day2"),
                                                             id_col="Index",
                                                             paired='baseline')
                elif len(drop_injection_stat.value) == 4:
                    two_groups_paired_baseline_clk = dabest.load(data=pivot_df_clk,
                                                             idx=("Control", "Day1", "Day2", "Day3"),
                                                             id_col="Index",
                                                             paired='baseline')

                fig, axs = plt.subplots(1, 3,
                                        figsize=(25, 10))
                fig.subplots_adjust(wspace=0.5)

                # 1er plot
                plotdabest_clk = dabest.load(data=df_lm_clk,
                                             x="GenoA",
                                             y="new_totallength",
                                             idx=ids,
                                             id_col="new_cage")

                # Tracer le graphique
                plotdabest_clk.mean_diff.plot(ax=axs[0],
                                              color_col='new_cage')
                axs[0].set_title(f"""Sum of totalLength per Cage for the '{r_drop_event}' event""",
                                 loc='left')

                # 2ème plot
                if len(drop_injection_stat.value) == 2:
                    ax1 = two_groups_paired_baseline_clk.mean_diff.plot(color_col='new_cage',
                                                                        ax=axs[1])
                    axs[1].legend(title='Cage',
                                  labels=pivot_df_clk['new_cage'].unique(),
                                  frameon=False,
                                  loc=(1.62, 0.75))
                elif len(drop_injection_stat.value) > 2:
                    ax1 = two_groups_paired_baseline_clk.mean_diff.plot(color_col='new_cage',
                                                                        ax=axs[1])
                    axs[1].legend(title='Cage',
                                  labels=pivot_df_clk['new_cage'].unique(),
                                  frameon=False,
                                  loc=(0.95, 0.75))

                # 3ème plot
                axs[2].axis('off')
                table0 = tabulate(ssdd, headers="keys",
                                  colalign=("center", "center", "center", "center", "center"))
                axs[2].annotate(table0,
                                xy=(-0.25, 0.75),
                                xycoords='axes fraction',
                                fontsize=10,
                                va='top',
                                family='monospace')
                table1 = tabulate(result.summary().tables[0],
                                  colalign=("center", "center", "center", "center", "center"))
                axs[2].annotate(table1,
                                xy=(-0.25, 0.55),
                                xycoords='axes fraction',
                                fontsize=10,
                                va='top',
                                family='monospace')
                table2 = tabulate(result.summary().tables[1],
                                  headers="keys",
                                  tablefmt="plain",
                                  colalign=("center", "center", "center", "center", "center", "center", "center"))
                axs[2].annotate(table2,
                                xy=(-0.25, 0.35),
                                xycoords='axes fraction',
                                fontsize=10,
                                va='top',
                                family='monospace')
                image_file_path = os.path.join(new_folder_path, f'{r_drop_event}.png')
                plt.savefig(image_file_path,
                            dpi=300,
                            bbox_inches='tight')
                plt.close(fig)
            else:
                return
        else:
            return

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
#                                                 'choice_type':choicetype,
#                                                 'stats_type':statstype})
# display(interactive_stats)
