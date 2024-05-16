import sys
sys.path.insert(1, "../")
import os
import sqlite3
from lmtanalysis.FileUtil import getFilesToProcess, getFolderToProcess

# Select the file for processing
files = getFilesToProcess()

def SplitDatabase():
    """
        Function to split a SQLite database into multiple databases based on 'night' events.

        This function prompts the user to specify a new folder name where the split databases will be saved.
        Then it processes each input database file, extracts 'night' events, and creates separate databases
        for each 'night' event, saving them in the specified folder.
        """
    # # Select the file for processing
    # files = getFilesToProcess()

    # Ensure there are files to process
    if not files:
        print("You have to select a least")
    else:
        # Use the first file to extract the directory
        first_file = files[0]
        initial_folder = os.path.dirname(first_file)

        # Ask the user for the new folder name
        new_folder_name = input("Enter the name of the new folder: ")

        # Concatenate the new folder with the initial directory
        save_folder = os.path.join(initial_folder, new_folder_name)

        # Check if the folder exists, if not, create it
        if not os.path.exists(save_folder):
            os.makedirs(save_folder)

        # Select the folder where the files will be created
        target_folder = getFolderToProcess()

        # Ensure the target folder is selected
        if not target_folder:
            print("No target folder selected. End of script.")
        else:
            # Call the function to process the files
            processFiles(files, save_folder)

            print("Database splited.")

def add_missing_columns(cursor, table_name, required_columns):
    cursor.execute(f"PRAGMA table_info('{table_name}')")
    existing_columns = set(row[1] for row in cursor.fetchall())

    missing_columns = set(required_columns) - existing_columns
    for column in missing_columns:
        cursor.execute(f"ALTER TABLE {table_name} ADD COLUMN {column} TEXT;")

def processFiles(files, save_folder):
    for file_path in files:
        connection = sqlite3.connect(file_path)
        cursor = connection.cursor()

        file_name = os.path.splitext(os.path.basename(file_path))[0]

        # Check if 'FRAME' table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='FRAME';")
        frame_table_exists = cursor.fetchone()

        if frame_table_exists:
            # If 'FRAME' table exists, check the number of columns
            cursor.execute("PRAGMA table_info('FRAME')")
            frame_columns = cursor.fetchall()

            if len(frame_columns) == 4:
                # Add missing columns to 'FRAME' table
                required_columns = ['TEMPERATURE', 'HUMIDITY', 'SOUND', 'LIGHTVISIBLE', 'LIGHTVISIBLEANDIR']  # Replace with your actual column names
                add_missing_columns(cursor, 'FRAME', required_columns)

        cursor.execute("SELECT STARTFRAME, ENDFRAME FROM EVENT WHERE NAME = 'night'")
        create_table_query = cursor.fetchall()
        # print('This script will divide the input .sqlite file into different sqlite for each "night" event from the original database')
        print(f'The (start, stop) frames from {file_path} are:')
        print(create_table_query)

        for i, event in enumerate(create_table_query):
            print('     The following night is currently processed:')
            print(f"     {event}")

            start_frame = event[0]
            end_frame = event[1]

            output_file = os.path.join(save_folder, f"{file_name}-night{i + 1}.sqlite")
            new_connection = sqlite3.connect(output_file)

            new_cursor = new_connection.cursor()

            cursor.execute("SELECT sql FROM sqlite_master WHERE name='FRAME'")
            create_table_query = cursor.fetchone()[0]
            new_cursor.execute(create_table_query)

            cursor.execute("SELECT sql FROM sqlite_master WHERE name='DETECTION'")
            create_table_query = cursor.fetchone()[0]
            new_cursor.execute(create_table_query)

            cursor.execute("SELECT sql FROM sqlite_master WHERE name='EVENT'")
            create_table_query = cursor.fetchone()[0]
            new_cursor.execute(create_table_query)

            cursor.execute("SELECT sql FROM sqlite_master WHERE name='ANIMAL'")
            create_table_query = cursor.fetchone()[0]
            new_cursor.execute(create_table_query)

            cursor.execute("SELECT * FROM FRAME WHERE FRAMENUMBER BETWEEN ? AND ?", (start_frame, end_frame))
            frame_rows = cursor.fetchall()

            cursor.execute("PRAGMA table_info('FRAME')")
            columns_info = cursor.fetchall()
            # print(columns_info)

            # stmt = "INSERT INTO FRAME VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)"
            stmt = "INSERT INTO FRAME (FRAMENUMBER, TIMESTAMP, NUMPARTICLE, PAUSED, TEMPERATURE, HUMIDITY, SOUND, LIGHTVISIBLE, LIGHTVISIBLEANDIR) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)"
            new_cursor.executemany(stmt, frame_rows)

            cursor.execute("SELECT * FROM DETECTION WHERE FRAMENUMBER BETWEEN ? AND ?", (start_frame, end_frame))
            detection_rows = cursor.fetchall()

            stmt1 = "INSERT INTO DETECTION VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
            new_cursor.executemany(stmt1, detection_rows)

            new_cursor.execute("SELECT name FROM sqlite_master WHERE type='index' AND name='detectionFastLoadXYIndex'")
            existing_index = new_cursor.fetchone()

            if existing_index is None:
                new_cursor.execute(
                    "CREATE INDEX 'detectionFastLoadXYIndex' ON 'DETECTION' ('ANIMALID', 'FRAMENUMBER' ASC, 'MASS_X', 'MASS_Y')")

            new_cursor.execute("SELECT name FROM sqlite_master WHERE type='index' AND name='detectionIndex'")
            existing_index = new_cursor.fetchone()

            if existing_index is None:
                new_cursor.execute("CREATE INDEX 'detectionIndex' ON 'DETECTION' ('ID' ASC, 'FRAMENUMBER' ASC)")

            new_cursor.execute("SELECT name FROM sqlite_master WHERE type='index' AND name='detetIdIndex'")
            existing_index = new_cursor.fetchone()

            if existing_index is None:
                new_cursor.execute("CREATE INDEX 'detetIdIndex' ON 'DETECTION' ('ID' ASC)")

            new_cursor.execute("SELECT name FROM sqlite_master WHERE type='index' AND name='detframenumberIndex'")
            if existing_index is None:
                new_cursor.execute("CREATE INDEX 'detframenumberIndex' ON 'DETECTION' ('FRAMENUMBER' ASC)")

            cursor.execute("SELECT * FROM ANIMAL")
            animal_rows = cursor.fetchall()

            stmt3 = "INSERT INTO ANIMAL VALUES (?, ?, ?, ?)"
            new_cursor.execute("DELETE FROM ANIMAL")
            new_cursor.executemany(stmt3, animal_rows)

            new_cursor.execute("SELECT name FROM sqlite_master WHERE type='index' AND name='animalINDEX'")
            existing_index = new_cursor.fetchone()
            if existing_index is None:
                new_cursor.execute("CREATE INDEX 'animalIndex' ON 'ANIMAL' ('ID')")

            cursor.execute("SELECT * FROM EVENT WHERE ENDFRAME BETWEEN ? AND ?", (start_frame, end_frame))

            event_rows = cursor.fetchall()

            stmt5 = "INSERT INTO EVENT VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
            new_cursor.executemany(stmt5, event_rows)

            new_cursor.execute("SELECT name FROM sqlite_master WHERE type='index' AND name='eventEndFrameIndex'")
            existing_index = new_cursor.fetchone()
            if existing_index is None:
                new_cursor.execute("CREATE INDEX 'eventEndFrameIndex' ON 'EVENT' ('ENDFRAME' ASC)")

            new_cursor.execute("SELECT name FROM sqlite_master WHERE type='index' AND name='eventIndex'")
            existing_index = new_cursor.fetchone()
            if existing_index is None:
                new_cursor.execute("CREATE INDEX 'eventIndex' ON 'EVENT' ('ID' ASC,'STARTFRAME' ASC, 'ENDFRAME' ASC)")

            new_cursor.execute("SELECT name FROM sqlite_master WHERE type='index' AND name='eventStartFrameIndex'")
            existing_index = new_cursor.fetchone()
            if existing_index is None:
                new_cursor.execute("CREATE INDEX 'eventStartFrameIndex' ON 'EVENT' ('STARTFRAME' ASC)")

            new_cursor.execute("SELECT name FROM sqlite_master WHERE type='index' AND name='eventstartendIndex'")
            existing_index = new_cursor.fetchone()
            if existing_index is None:
                new_cursor.execute("CREATE INDEX 'eventstartendIndex' ON 'EVENT' ('STARTFRAME' ASC, 'ENDFRAME' ASC)")

            new_cursor.execute("SELECT name FROM sqlite_master WHERE type='index' AND name='indexeventidIndex'")
            existing_index = new_cursor.fetchone()
            if existing_index is None:
                new_cursor.execute("CREATE INDEX 'indexeventidIndex' ON 'EVENT' ('ID' ASC)")

            new_connection.commit()
            new_cursor.close()
            new_connection.close()

        cursor.close()
        connection.close()

# if __name__ == '__main__':
# # Appel de la fonction pour exécuter le workflow complet
# processFilesWorkflow()