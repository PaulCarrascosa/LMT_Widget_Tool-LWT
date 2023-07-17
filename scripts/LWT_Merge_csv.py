import sys
sys.path.insert(1, "../")

import pandas as pd
import warnings
warnings.simplefilter(action='ignore')
import os
import glob
import csv
import shutil
import tkinter as tk
from tkinter.dialog import Dialog
from tkinter import filedialog
from tkinter.filedialog import askdirectory


def window():
    root = tk.Tk()
    root.withdraw()
    root.update()

    d = Dialog(title="Select folder for processing", text="Select folder for processing", bitmap='question',
        strings=('Folder', 'Cancel'), default=0)

    root.focus_force()
    folder = None
    if (d.num == 0):
        folder = askdirectory(title="Choose a folder where your .csv files to merge are located")

    d.destroy()
    root.destroy()

    return folder

def Merge():
    """
    Cette fonction permet de fusionner tous les fichiers CSV d'un dossier sélectionné en un seul fichier CSV.

    Instructions :
    1. Une boîte de dialogue s'ouvre pour sélectionner un dossier contenant les fichiers CSV.
    2. Vous devez spécifier le nom du nouveau dossier à créer où les fichiers seront déplacés.
    3. Les fichiers CSV du dossier sélectionné seront déplacés vers le nouveau dossier.
    4. Tous les fichiers CSV du nouveau dossier seront fusionnés en un seul fichier CSV.
    5. Le nouveau fichier fusionné sera enregistré dans le nouveau dossier avec un nom spécifié.

    Note :
    - Assurez-vous d'avoir les modules os, shutil, glob et pandas importés.
    - Si vous avez une colonne "Unnamed: 0" dans vos fichiers CSV, utilisez la ligne `df_append.pop("Unnamed: 0")`
      pour la supprimer avant de fusionner les fichiers.
    - Assurez-vous que votre code appelle la fonction window() pour afficher la boîte de dialogue de sélection
      du dossier.

    Exemple d'utilisation :
    Merge()
    """

    # # Ouvrir une boîte de dialogue pour sélectionner un dossier
    path = window()

    # spécifier le nom du nouveau dossier à créer
    input_new_file = input("Put the name of your folder that will be created :")
    new_folder = input_new_file

    # spécifier le chemin du dossier où les fichiers .csv se trouvent
    root = path

    # spécifier le chemin du dossier où le nouveau dossier sera créé
    final_file = path

    # vérifier si le dossier existe déjà
    if os.path.exists(os.path.join(final_file, new_folder)):
        # si oui, le supprimer
        os.rmdir(os.path.join(final_file, new_folder))

    # créer le nouveau dossier dans le dossier de destination
    new_path = os.path.join(final_file, new_folder)
    os.makedirs(new_path)

    # parcourir tous les fichiers dans le dossier initial
    for file in os.listdir(root):

        # vérifier si le fichier est un fichier .csv
        if file.endswith(".csv"):

            # spécifier le chemin complet du fichier
            path2 = os.path.join(root, file)

            # déplacer le fichier vers le nouveau dossier
            shutil.move(path2, new_path)

    #read the path
    file_path = path+"/"+new_folder+"/"
    os.chdir(path+"/"+new_folder+"/")
    #list all the files from the directory
    file_list = os.listdir(file_path)

    #list all csv files only
    csv_files = glob.glob('*.{}'.format('csv'))
    print(csv_files)

    df_append = pd.DataFrame()  # append all files together

    for file in csv_files:
        df_temp = pd.read_csv(file)
        df_append = df_append.append(df_temp, ignore_index=True)

    print("##################################################################################")
    print("##################################################################################")
    print("######################### Folder created & files moved ###########################")

    df_append.pop("Unnamed: 0") #Add this line if there is a column named "Unnamed: 0"
    name_new_file = input("What's the name of your merged file ?")
    df_append.to_csv(path+"/"+new_folder+"/"+name_new_file+".csv")

    print("##################################################################################")
    print("##################################################################################")
    print("####################### Merged file created with success #########################")
