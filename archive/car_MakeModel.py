import pandas as pd
from pathlib import Path

## Get Data
MAKE_NAMES = 'SP2022project_data/make2020.csv'
CAR_SALES = 'SP2022project_data/Car_sales_data.csv'
NHTSA_DATA = 'SP2022project_data/NHTSA_2010-2020.csv'

makeData = pd.read_csv(MAKE_NAMES)
carSales = pd.read_csv(CAR_SALES)
carSales = carSales.dropna() #drop NaN rows
nhtsaData = pd.read_csv(NHTSA_DATA)

other_import = set()
other_make = set()
other_domestic = set()
other_indx = [] ## Collect indices for "Other" so that we don't have to compare them later

## Create Copies of Car sales data to manipulate strings
carMake = carSales.copy()
carModel = carSales.copy()
carMake.rename(columns={"Make_Model":"Make"}, inplace=True)
carModel.rename(columns={"Make_Model":"Model"}, inplace=True)

make_names = makeData["text"]
drop_indexes = []

## Get Make names of those listed under 'Other'
for i in range(0, nhtsaData.shape[0]):
    ## Test for "Other Import"
    if nhtsaData.iloc[i,3] == 69:
        other_indx.append(i)
        if "other" not in str(nhtsaData.iloc[i,7]).lower() and \
           "unknown" not in str(nhtsaData.iloc[i,7]).lower():
            other_import.add(nhtsaData.iloc[i,7]) 
    elif nhtsaData.iloc[i,3] == 98:
        other_indx.append(i)
        if "other" not in str(nhtsaData.iloc[i,7]).lower() and \
           "unknown" not in str(nhtsaData.iloc[i,7]).lower():
            other_make.add(nhtsaData.iloc[i,7])
    elif nhtsaData.iloc[i,3] == 29:
        other_indx.append(i)
        if "other" not in str(nhtsaData.iloc[i,7]).lower() and \
           "unknown" not in str(nhtsaData.iloc[i,7]).lower():
            other_domestic.add(nhtsaData.iloc[i,7])
    elif nhtsaData.iloc[i,3] == 99:
        other_indx.append(i)

## Separate Make names and Model names from Car_sales_data.csv
## Create 2 new columns 'Make' and 'Model'
## Replace MakeModel and separate them
for mn in make_names:
    for cm in range(0, carMake.shape[0]):
        if "Mercedes-AMG" in carMake.iloc[cm,0]:
            carMake.iloc[cm,0] = carMake.iloc[cm,0].replace(carMake.iloc[cm,0], "Mercedes-Benz AMG GT S")
        
        if mn in carMake.iloc[cm,0]:
            ## Replace the space after the Make name too so there are no trailing spaces
            new_model = carMake.iloc[cm,0].replace(mn+" ", "")
            carMake.iloc[cm,0] = mn
            carModel.iloc[cm,0] = new_model
            
## Rename Makes to match naming convention in NHTSA
## Replace the space after the Make name too so there are no trailing spaces
for cm in range(0, carMake.shape[0]):
    if "Bentley" in carMake.iloc[cm,0]:
        new_model = carMake.iloc[cm,0].replace("Bentley ", "")
        carModel.iloc[cm,0] = new_model
        carMake.iloc[cm,0] = "Rolls Royce/Bentley"
    elif "Buick" in carMake.iloc[cm,0]:
        new_model = carMake.iloc[cm,0].replace("Buick ", "")
        carModel.iloc[cm,0] = new_model
        carMake.iloc[cm,0] = "Buick / Opel"
    elif "Hummer" in carMake.iloc[cm,0]:
        carModel.iloc[cm,0] = "Hummer"
        carMake.iloc[cm,0] = "AM General"
    elif "Jeep" in carMake.iloc[cm,0]:
        new_model = carMake.iloc[cm,0].replace("Jeep ", "")
        carModel.iloc[cm,0] = new_model
        carMake.iloc[cm,0] = "Jeep / Kaiser-Jeep / Willys- Jeep"
    elif "Kia" in carMake.iloc[cm,0]:
        new_model = carMake.iloc[cm,0].replace("Kia ", "")
        carModel.iloc[cm,0] = new_model
        carMake.iloc[cm,0] = "KIA"
    elif "Nissan" in carMake.iloc[cm,0]:
        new_model = carMake.iloc[cm,0].replace("Nissan ", "")
        carModel.iloc[cm,0] = new_model
        carMake.iloc[cm,0] = "Nissan/Datsun"
    elif "RLX/RL" in carModel.iloc[cm,0]:
        carModel.iloc[cm,0] = "RL/RXL"

    ## Remove Genesis and Ram
    ## Both are not in NHTSA and would mess up joins
    if "Genesis" in carMake.iloc[cm,0]:
        drop_indexes.append(cm)
    if "Ram" in carMake.iloc[cm,0]:
        drop_indexes.append(cm)
        
## For makes under "Other Import", "Other Make", "Other Domestic"
## Replace Make names as such and Model name will be the Make name
for cm in range(0, carMake.shape[0]):
    for oi in other_import:
        if oi == "Mini-Cooper":
            oi = "Mini Cooper"
        if oi in carMake.iloc[cm,0] and oi != "McLaren":
            ## Excluding McLaren as Mercedes has a Model named McLaren and there is no
            ## McLaren Make in Car Sales data. Leaving it in would cause problems.
            carMake.iloc[cm,0] = "Other Import"
            carModel.iloc[cm,0] = oi
    for od in other_domestic:
        if od in carMake.iloc[cm,0]:
            carMake.iloc[cm,0] = "Other Domestic"
            carModel.iloc[cm,0] = od          

## Drop rows
carMake.drop(drop_indexes, inplace=True)
carModel.drop(drop_indexes, inplace=True)
carMakes = set(carMake["Make"])
        
## Turn Model and Make into Series to add to DF
carModel = carModel["Model"]
carMakeModel = carMake.join(carModel)
print(carMakeModel)

## Create csv file
#filepath = Path("OUT_data/car_sales_MakeModel.csv")
#carMakeModel.to_csv(filepath, index=False)

## Replace Model names in NHTSA with Model names in carMakeModel
print("Cleaning up NHTSA Model names...")
test = nhtsaData.iloc[:5000,:].copy()
for i in range(0, test.shape[0]):
    if i not in other_indx:
        ## For time sake, skip Model names that are already one word (AKA already clean)
        ## And only compare Makes that are in Car_sales_data
        if test.iloc[i,4] in carMakes:
            split = str(test.iloc[i,7]).split("/")
            split02 = str(split[0]).split(" ")
            if len(split) > 1 or len(split02) > 1 and "unknown" not in str(split[0]).lower()\
               and "other" not in str(split[0]).lower() and "or greater" not in str(split[0])\
               and "pickup" not in str(split[0]).lower() and "medium" not in str(split[0]).lower()\
               and "and over" not in str(split[0]) and "minivan" not in str(split[0]).lower():
                for cmm in range(0, carMakeModel.shape[0]):
                    if str(carMakeModel.iloc[cmm,0]) in str(test.iloc[i,7]):
                        test.iloc[i,7] = test.iloc[i,7].replace(carMakeModel.iloc[cmm,0]+" ", "") #Take out Make name
                    if str(carMakeModel.iloc[cmm,18]) in str(test.iloc[i,7]) and \
                       str(carMakeModel.iloc[cmm,0]) == str(test.iloc[i,4]):
                        if str(carMakeModel.iloc[cmm,18]) != "RL" and \
                           str(carMakeModel.iloc[cmm,18]) != "RLX":
                            test.iloc[i,7] = test.iloc[i,7].replace\
                                            (test.iloc[i,7], carMakeModel.iloc[cmm, 18])

print("Cleaning done")
## Write to csv file
filepath = Path("OUT_data/NHTSA_cleanModel.csv")
test.to_csv(filepath, index=False)
#nhtsaData.to_csv(filepath, index=False)
