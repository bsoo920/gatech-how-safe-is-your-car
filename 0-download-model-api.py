import requests
import csv
from datetime import datetime
import os
import pandas as pd
dir = 'NHTSA-FARS-download/'


# # Download from "make" API, which returns same data from 2010-2020 (except 2010 & 2011 had 2 fewer rows), and that pre-2010 gives errors.
year=2020
file = f'{dir}make{year}.csv'

urlMakes = f"https://crashviewer.nhtsa.dot.gov/CrashAPI/definitions/GetVariableAttributes?variable=make&caseYear={year}&format=csv"
r = requests.get(urlMakes, allow_redirects=True)
open(file, 'wb').write(r.content)

print(year, 'success', datetime.now().strftime("%d/%m/%Y %H:%M:%S"))

makes = csv.reader( open(file,'r'))
next(makes)     #skip header row

for [makeID, make, _, _] in makes:
    # makes when iterated through:
    # ['id', 'text', 'from_year', 'to_year']
    # ['54', 'Acura', '1994', '']
    # ['31', 'Alfa Romeo', '1994', '']

    # models API is also cumulative in nature, so just final year needed.
    year=2020

    try:
        url = f"https://crashviewer.nhtsa.dot.gov/CrashAPI/definitions/GetVariableAttributesForModel?variable=model&caseYear={year}&make={makeID}&format=csv"
        rModels = requests.get(url, allow_redirects=True)

        # os.makedirs(dir+make, exist_ok = True)
        make = make.replace('/','-')
        open( f"{dir}model-lookup/{make}_models{year}.csv", "wb" ).write(rModels.content)
        print('success:', datetime.now().strftime("%d/%m/%Y %H:%M:%S"), year, makeID, make)

    except Exception as e:
        print('FAILED:', datetime.now().strftime("%d/%m/%Y %H:%M:%S"), year, makeID, make, '\n', e)

    # break