import csv as csv

import numpy as np
import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plot

# from IPython.display import display
#todo: age of vehicle column
#todo:addstate,state#,yearofaccidenttoeachcsvNHTSA,case#

# set directory and use prior code to read in car sales data
dir2 = 'Melirose/'

nrows = None        #set to None to read all

df_original = pd.read_csv(f'{dir2}car_sales_MakeModel.csv', encoding='latin1', header=0, nrows=nrows)  #.astype(str)      # , dtype={'DEATHS':'int32'}

print('** df_original **')
print(df_original.head())
print(" ")
print("number of records is ", len(df_original))

# rearrange as make, model, then list of years
df_rearranged = df_original[['Make', 'Model', '2005', '2006', '2007', '2008', '2009', '2010', '2011', '2012', '2013', '2014', '2015', '2016', '2017', '2018', '2019', '2020', '2021']]
print(" ")
print('** df_rearranged **')
print(df_rearranged.head())
print(" ")
print("number of records is ", len(df_rearranged))


# references:https://stackoverflow.com/questions/51256565/a-pandas-column-of-float-turns-out-to-be-object#:~  
#    :text=pd.merge%20%28Investments1%2CInvestments2%2C%20how%20%3D%20%22outer%22%2C%20left_on%20%3D%20left_key%2C,you%20wish%20to%20proceed%20you%20should%20use%20pd.concat
#            https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.melt.html
#            https://stackoverflow.com/questions/34830597/pandas-melt-function

# use pandas melt to list sales in one column and sales year (== mod_year) in another column

df_melted = pd.melt(df_rearranged, id_vars = ['Make', 'Model'], value_vars = ['2005', '2006', '2007', '2008', '2009', '2010', '2011', '2012', '2013', '2014', '2015', '2016', '2017', '2018', '2019', '2020', '2021'], \
                    var_name = 'MOD_YEAR', value_name = 'Sales')

df_melted['MOD_YEAR'] = df_melted['MOD_YEAR'].transform(int)

print("")
df_melted['Sales'] = df_melted['Sales'].transform(int)

# rename columns to merge with FARS data subset
df_melted = df_melted.rename(columns = {'Make': "MAKE_NAME", 'Model': 'MODEL_NAME'})

print(" ")
print('** df_melted **')
print(df_melted.head())
print(" ")
print("number of records is ", len(df_melted))
print(" ")

# read in NHTSA_join data without the sales data

df_NHTSA = pd.read_csv(f'{dir2}NHTSA_ver4.csv', encoding='latin1', header=0,  nrows=nrows)  

# create dictionary to get numerical make ID and model ID to correpond to make/model names in sales data

list_1st = df_NHTSA['Make_ID'].to_list()
list_2nd = df_NHTSA['Make_Name_x'].to_list()
list_3rd = df_NHTSA['Model_ID'].to_list()
list_4th = df_NHTSA['modelname'].to_list()
make_dict = {}
model_dict = {}

for j in range(len(list_1st)):
    if list_1st[j] not in make_dict:
        make_dict[list_1st[j]] = list_2nd[j]
    if list_1st[j] not in model_dict:
        model_dict[list_1st[j]] = {}
        if list_3rd[j] not in model_dict[list_1st[j]]:
            model_dict[list_1st[j]][list_3rd[j]] = list_4th[j]
    elif list_3rd[j] not in model_dict[list_1st[j]]:
        model_dict[list_1st[j]][list_3rd[j]] = list_4th[j]

# load 
dir = 'NHTSA-FARS-download/'
usecols = ['MOD_YEAR', 'MAKE', 'MODEL', 'BODY_TYP','DEATHS']
startYR, endYR = 2005, 2015
nrows = None        #set to None to read all

df_final = None # pd.DataFrame(columns=usecols)
for year in list(range(startYR, endYR + 1)):

    print('reading', year)
    df = pd.read_csv(f'{dir}vehicle{year}.csv', encoding='latin1', header=0, usecols=usecols
                     , nrows=nrows)  #.astype(str)      # , dtype={'DEATHS':'int32'}
    df['YEAR'] = year
    # print(df[:5])

    if df_final is None:
        df_final = df
    else:
        df_final = pd.concat([df_final, df], ignore_index=True)

print('aggregating...')
# print('** df_final **')
# print(df_final.info())

df_agg = df_final.groupby(['MOD_YEAR', 'MAKE', 'MODEL','BODY_TYP','YEAR']) \
    .agg(fatalities=pd.NamedAgg(column='DEATHS', aggfunc=sum)) \
    .reset_index()

print(df_agg[:20])

def get_make_name(make_num):
    if make_num in make_dict:
        return make_dict[make_num]
    else:
        return None

def get_model_name(make_num, model_num):
    if make_num not in model_dict:
        return None
    if model_num in model_dict[make_num]:
        return model_dict[make_num][model_num]
    else:
        return None
#  References:  
#       https://stackoverflow.com/questions/32277473/merge-two-dataframes-based-on-multiple-keys-in-pandas
#       https://stackoverflow.com/questions/13331698/how-to-apply-a-function-to-two-columns-of-pandas-dataframe
#
#  Add names for Make and Model using dictionary
df_agg['MAKE_NAME'] = df_agg['MAKE'].apply(get_make_name)
df_agg['MODEL_NAME'] = df_agg.apply(lambda x: get_model_name(x['MAKE'],x['MODEL']), axis = 1) 
                                
print("  ")
print(df_agg[:20])
print("Number of records is ", len(df_agg))
print(" ")
# limit records to models > 2004  since sales is 2005+
df_aggX = df_agg[df_agg["MOD_YEAR"]>2004]
print("Number of records model year > 2004 is ", len(df_aggX))
print(" ")
#print(df_aggX.dtypes)
#print(df_melted.dtypes)
#  Eliminate records where Make_name or Model_name is "None"
df_aggY = df_aggX[df_aggX["MAKE_NAME"] != None]
df_aggZ = df_aggY[df_aggY["MODEL_NAME"] != None]
print("  ")
print("Number of records after removing MAKE_NAME, MODEL_NAME == None is ", len(df_aggZ))
print(" ")
# Merge FARS data with sales data
df_combo = pd.merge(df_agg, df_melted, how = 'inner')
print("  ")
print('** df_combo **')
print(df_combo.head())
print(" ")
print("number of records after combining with sales is ", len(df_combo))
print(" ")
df_comboB = df_combo[df_combo['Sales'] != 0.0]
print(" ")
print("number of records after removing sales of 0.0 is ", len(df_comboB))
print(" ")
# sample = df_agg[(df_agg.MAKE=='49') & (df_agg.MODEL=='40')  & (df_agg.MOD_YEAR=='1999')]
# print(sample[:5])
print(df_comboB[1000:1020])

