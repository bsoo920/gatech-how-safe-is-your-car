import csv as csv

import numpy as np
import pandas as pd
from IPython.display import display

start_yr = 2016
end_yr = 2020

#TODO: BRIGHT: get 2005-2020 fars data
#easily creates a name list for pulling in csv filenames
def file_namer(startYR, endYR, name):
    #number range in list format
    #name = string name of file
    name_list = []
    for year in list(range(startYR, endYR+1)):
        name_list.append(name + str(year) + '.CSV')
    return name_list

#creates a set of a column for future filtering
def get_setlist(filenames, col):
    #filenames = a list of filenames/.CSVs
    #col = the column name to create a set out of
    df_final = pd.DataFrame(columns=['year', 'make', 'model'])
    for file in filenames:
        df = pd.read_csv(file, encoding='latin1', header=0).astype(str)

        df_final = pd.concat([df_final, df], ignore_index=True)
    return set(df_final[col])
makemod_filenames = file_namer(start_yr, end_yr, '')
make_set = get_setlist(makemod_filenames, col='make')
print(make_set)
mod_set = get_setlist(makemod_filenames, col='model')
print(mod_set)

def Load_NHTSA_Data(filenames, start_yr):
    # todo: addstate,state#,yearofaccidenttoeachcsvNHTSA,case#
    # todo: age of vehicle column
    old_cols = ['MOD_YEAR', 'MAKENAME', 'MAK_MODNAME', 'BODY_TYPNAME', 'DEATHS']
    df_final = pd.DataFrame(columns=['mod_year', 'Make', 'Model', 'BODY_TYPNAME'])
    # read through each filename in filenames
    start_cnt = start_yr
    for i, file in enumerate(filenames):

        df = pd.read_csv(file, encoding='latin1', header=0, usecols=old_cols).astype(str)
        # print(df.isna().sum())
        df.rename(columns={"MOD_YEAR": "mod_year",
                           "MAKENAME": "Make",
                           "MAK_MODNAME": "Model",
                           "DEATHS": "Deaths"
                           }, inplace=True)
        # TODO: melirose: get sales data, and integer column for deaths
        df['Deaths'] = df["Deaths"].astype('int32') #Convert deaths col to int
        df = df[~df['Make'].str.contains("Unknown")] # filter out Unknown rows
        df = df[df['Deaths'] > 0] #Filter for fatalities only
        df.drop('Deaths', axis=1, inplace=True) #drop death column

        if i == 0:
            df["case_year"] = str(start_yr).strip()
        else:
            start_cnt += 1
            df["case_year"] = str(start_cnt).strip()

        for i, v in enumerate(df["Model"]):
            print(i)
            print(v)
            #if i in make_set:
            #    df["Model"]
            break


        #df_makes = df["Model"].str.split(" ", n=2, expand=True)
        #print(df_makes.columns.tolist())
        #df_makes.drop(0, axis=1, inplace=True)
        #print(df_makes)
        #df_makes_select = df_makes[[-1]].agg('-'.join, axis=1)
        #print(df_makes_select[0:10])
        # create new model col in main df
        #df['Model_1'] = df_makes[1]

        # kill white spaces across all cols
        #df = df.apply(lambda x: x.str.strip())

        # deal with possible NAs
        df['mod_year'].fillna('0', inplace=True)
        df.fillna('unknown', inplace=True)
        #df['Model'].fillna('unknown', inplace=True)
        # create final df by concating the old with the new trimmed df

        df_final = pd.concat([df_final, df], ignore_index=True)

    #df_final.drop_duplicates(inplace=True, ignore_index=True)
    return df_final


# list file names to concat into one df
filenames = file_namer(2016, 2020, 'Vehicle')
NHTSA_Data = Load_NHTSA_Data(filenames, start_yr)
print(NHTSA_Data)
compression_opts = dict(method='zip', archive_name='NHTSA.csv')

#NHTSA_Data.to_csv('NHTSA.zip', index=False, compression=compression_opts)

def Load_Sales_Data(filename):
    keep_cols = ['Make', 'Model', '2016', '2017', '2018', '2019', '2020']
    df = pd.read_csv('Car_sales_data.csv', encoding='latin1', header=0, usecols=keep_cols).astype(str)
    return df






#sales_data = Load_Sales_Data('marklines2016-2021.csv')
#print(sales_data)

#final_df = pd.merge(NHTSA_Data, sales_data, on=['Make'])
#print(final_df)
#print(len(final_df))
compression_opts = dict(method='zip', archive_name='NHTSA-SalesData_MAKE.csv')

#final_df.to_csv('NHTSA-SalesData_MAKE.zip', index=False, compression=compression_opts)