"""
Created on 17 January 2024

@author: P. Carrascosa
"""

"""
This code must be used with Jupyter Notebook or Jupyter Lab. It will allows you to change your genotypes in your
databases one by one.
The Goal is to then use an ipywidget tool, based on dataframes to compute Graphs and mixed model statistics.
"""

import sys
sys.path.insert(1, "../")
from lmtanalysis.FileUtil import getOneFileToProcess
import sqlite3
import os
import pandas as pd
from IPython.display import display, clear_output
from ipywidgets import interact_manual, interact, widgets, interactive_output, Output
import warnings
warnings.filterwarnings('ignore')

def connect_to_database():
    # Connect to the SQLite database
    file = getOneFileToProcess()
    conn = sqlite3.connect(file)
    return conn, file

def load_initial_data(conn):
    # Load data from the table into a DataFrame
    query = "SELECT * FROM ANIMAL;"
    df_sqlite = pd.read_sql_query(query, conn)
    return df_sqlite

def display_initial_table(df_sqlite):
    # Display the initial table
    df_display = display(df_sqlite, display_id='df_display')
    return df_display

def update_genotype(Selected_ID, Genotype, conn, df_display, file):
    try:
        # Start an SQLite transaction
        conn.execute("BEGIN;")

        # Update the database
        update_query = f"UPDATE ANIMAL SET GENOTYPE = ? WHERE ID = ?;"
        conn.execute(update_query, (Genotype, Selected_ID))

        # Commit the transaction
        conn.execute("COMMIT;")

        # Extract only the file name from the full path
        file_name = os.path.basename(file)
        print(f"Change applied to SQLite database {file_name} !")

        # Reload the DataFrame after modifications
        query = "SELECT * FROM ANIMAL;"
        df_sqlite = pd.read_sql_query(query, conn)

        # Clear the current display content
        clear_output(wait=True)

        # Display the updated table in the same display
        df_display.update(df_sqlite)

    except Exception as e:
        # Rollback in case of an error
        conn.execute("ROLLBACK;")
        print("Error:", str(e))

def close_connection(conn, output_widget):
    # Close the SQLite database connection
    conn.close()

    # Display the message in the specified Output widget
    with output_widget:
        clear_output(wait=True)
        print("Connection to the database closed! If you want to change another genotype in the same database, launch the cell again!")

def ChangeGenotypes():
    # Initial setup
    conn, file = connect_to_database()
    df_sqlite = load_initial_data(conn)
    df_display = display_initial_table(df_sqlite)

    # Create an Output widget for displaying messages
    output_widget = Output()

    # Function to update the value in the specified column
    @interact_manual(Selected_ID=df_sqlite['ID'], Genotype=widgets.Text(value=df_sqlite['GENOTYPE'].iloc[0]))
    def interact_update_genotype(Selected_ID, Genotype):
        update_genotype(Selected_ID, Genotype, conn, df_display, file)

    # Button to close the connection
    close_button = widgets.Button(description="Close Connection")
    close_button.on_click(lambda x: close_connection(conn, output_widget))

    # Display the widgets
    display(close_button, output_widget)

# if __name__ == '__main__':
#     ChangeGenotypes()

# # Run the main function
# ChangeGenotypes()