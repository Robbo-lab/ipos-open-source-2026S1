# This is an example of what the microcontroller would produce in a garden.
# We have a potted plant with soil. The soil has humidity between 1 and 0.
# The microcontroller pulls data from all plants and stores them in a matrix.
# We store the matrix in a Numpy array.

# We also collect values of date, temperature and garden name inside a pandas.
# We store a reference to the matrix inside the pandas since both work together.

# To export the Numpy array and DataFrame, we convert the Numpy array
# into a Numpy binary file and the DataFrame into an SQLite3 binary file.

# Both files are stored inside app/data.
# The script to recombine those files are inside services/recombine.py

import numpy as np
import pandas as pd

import datetime
import os
import sqlite3

# Invent matrix
matrix_simulation = np.array([[1., 0.], [0., 1.]]) # unit matrix 2×2
matrix_id = 1 # storing a link into the dataframe

# Invent DataFrame
dataframe_simulation = pd.DataFrame([{
    "matrix_id":   matrix_id,
    "garden_name": "Gardenia",
    "date":        datetime.date.today().isoformat(),
    "temperature": 25.0,
}])

# Setup paths for export
DATA_DIR = os.path.join("app", "data")
NPY_PATH = os.path.join(DATA_DIR, "humidity_matrix.npy")
DB_PATH  = os.path.join(DATA_DIR, "environment.db")
 
os.makedirs(DATA_DIR, exist_ok=True)

# Export our matrix into Numpy binary
np.save(NPY_PATH, matrix_simulation)

# Export our DataFrame into SQLite3 binary
con = sqlite3.connect(DB_PATH) # it creates it if nonexistent
dataframe_simulation.to_sql("environment", con, if_exists="replace", index=False)
con.close()