# This script aims to import both the Numpy binary file
# and the SQLite3 binary file from the app/data folder
# and recombine them into a single pandas DataFrame

import numpy as np
import pandas as pd
import sqlite3
import os

# Paths to import from
DATA_DIR = os.path.join("app", "data")
NPY_PATH = os.path.join(DATA_DIR, "humidity_matrix.npy")
DB_PATH  = os.path.join(DATA_DIR, "environment.db")

# Load Numpy matrix
humidity_matrix = np.load(NPY_PATH)
# Demonstration; remove in production
print("Humidity matrix:")
print(humidity_matrix)

# Load SQLite3 database into DataFrame
con = sqlite3.connect(DB_PATH)
garden_dataframe = pd.read_sql("SELECT * FROM environment", con)
con.close()

# Recombine both matrix and DataFrame
garden_dataframe["humidity_matrix"] = \
garden_dataframe["matrix_id"].apply(lambda _: humidity_matrix.tolist())

# Demonstration; remove in production
print("Combined DataFrame:")
print(garden_dataframe)