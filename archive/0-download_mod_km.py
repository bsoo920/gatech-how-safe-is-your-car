import requests
import os
import pandas as pd
dir = 'NHTSA-FARS-download/'


id_list = []
model_list = []
make_list = []
year_list = []

for year in range(2010, 2017):

    for make in range(1, 100):

        url = "https://crashviewer.nhtsa.dot.gov/CrashAPI/definitions/GetVariableAttributesForModel?variable=model&caseYear=%d&make=%d&format=json" % (year, make)
        r = requests.get(url, allow_redirects=True)
        data = r.json()
        results = data['Results'][0]

        for element in results:
            id_list.append(element['ID'])
        for element in results:
            model_list.append(element['MODELNAME'])
        for element in results:
            make_list.append(make)
        for element in results:
            year_list.append(year)

df = pd.DataFrame(list(zip(id_list, make_list, model_list, year_list)), columns=['ID', 'Make_ID', 'Model', 'Case_Year'])
df.to_csv('query_models.csv', index=False)



