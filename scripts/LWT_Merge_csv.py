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
from tkinter.filedialog import askdirectory, askopenfilename

def window():
    root = tk.Tk()
    root.withdraw()
    root.update()

    # Utilisez Dialog() pour afficher une boîte de dialogue de sélection
    d = Dialog(
        title="Select folder or cancel",
        text="Select folder or cancel",
        bitmap='question',
        strings=('Folder', 'Cancel'),
        default=0
    )

    # Si l'utilisateur choisit 'Cancel', terminez la fonction
    if d.num == 1:
        root.destroy()
        return None

    folder = askdirectory(title="Choose a folder where your .csv files to merge are located")
    root.destroy()
    return folder

def Merge():
    """
    This function merges all CSV files in a selected folder into a single CSV file.

    Instructions:
    1. A dialog box opens to select a folder containing CSV files.
    2. Specify the name of the new folder to create where the files will be moved.
    3. CSV files from the selected folder will be moved to the new folder.
    4. All CSV files in the new folder will be merged into a single CSV file.
    5. The new merged file will be saved in the new folder with a specified name.

    Note:
    - Ensure that the os, shutil, glob, and pandas modules are imported.
    - If you have a column "Unnamed: 0" in your CSV files, use the line `df_append.pop("Unnamed: 0")`
      to remove it before merging the files.
    - Make sure your code calls the window() function to display the folder selection dialog.

    Example Usage:
    Merge()
    """

    # Open a dialog box to select a folder
    path = window()

    # Specify the name of the new folder to create
    input_new_folder = input("Enter the name of the new folder to create: ")
    new_folder = input_new_folder

    # Specify the path of the folder where the .csv files are located
    root = path

    # Specify the path of the folder where the new folder will be created
    final_file = path

    # Check if the folder already exists
    if os.path.exists(os.path.join(final_file, new_folder)):
        # If yes, remove it
        shutil.rmtree(os.path.join(final_file, new_folder))

    # Create the new folder in the destination folder
    new_path = os.path.join(final_file, new_folder)
    os.makedirs(new_path)

    # Iterate through all files in the initial folder
    for file in os.listdir(root):

        # Check if the file is a .csv file
        if file.endswith(".csv"):

            # Specify the full path of the file
            path2 = os.path.join(root, file)

            # Move the file to the new folder
            shutil.move(path2, new_path)

    # read the path
    file_path = path+"/"+new_folder+"/"
    os.chdir(path+"/"+new_folder+"/")
    # list all the files from the directory
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
