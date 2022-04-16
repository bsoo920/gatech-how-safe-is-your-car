import requests
import csv
from datetime import datetime
import os
import pandas as pd
dir = 'NHTSA-FARS-download/'


id_list = []
model_list = []
make_list = []
year_list = []

# Download from "make" API, which returns same data from 2010-2020 (except 2010 & 2011 had 2 fewer rows), and that pre-2010 gives errors.
year=2020
urlMakes = f"https://crashviewer.nhtsa.dot.gov/CrashAPI/definitions/GetVariableAttributes?variable=make&caseYear={year}&format=csv"
r = requests.get(urlMakes, allow_redirects=True)
open(dir+'make%d.csv' % (year), 'wb').write(r.content)      # downloading for reference only
print(year, 'success', datetime.now().strftime("%d/%m/%Y %H:%M:%S"))

makes = csv.reader( r.text.splitlines())
next(makes)     #skip header row
for [makeID, make, _, _] in makes:
    # makes when iterated through:
    # ['id', 'text', 'from_year', 'to_year']
    # ['54', 'Acura', '1994', '']
    # ['31', 'Alfa Romeo', '1994', '']

    # models API is also cumulative in nature, so just final year needed.
    year=2020

    url = f"https://crashviewer.nhtsa.dot.gov/CrashAPI/definitions/GetVariableAttributesForModel?variable=model&caseYear={year}&make={makeID}&format=csv"
    rModels = requests.get(url, allow_redirects=True)

    # os.makedirs(dir+make, exist_ok = True)
    open( f"{dir}models/{make}_models{year}.csv", "wb" ).write(rModels.content)
    print(year, makeID, make, 'success', datetime.now().strftime("%d/%m/%Y %H:%M:%S"))

    break
