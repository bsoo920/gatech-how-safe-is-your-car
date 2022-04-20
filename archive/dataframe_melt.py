

import csv as csv

import numpy as np
import pandas as pd


# references: https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.melt.html
#             https://stackoverflow.com/questions/34830597/pandas-melt-function

dir = 'Melirose/'

nrows = None        #set to None to read all

df_original = pd.read_csv(f'{dir}car_sales_MakeModel.csv', encoding='latin1', header=0, nrows=nrows)  #.astype(str)      # , dtype={'DEATHS':'int32'}

print('** df_original **')
print(df_original.head())
print(" ")
print("number of records is ", len(df_original))

df_rearranged = df_original[['Make', 'Model', '2005', '2006', '2007', '2008', '2009', '2010', '2011', '2012', '2013', '2014', '2015', '2016', '2017', '2018', '2019', '2020', '2021']]
print(" ")
print('** df_rearranged **')
print(df_rearranged.head())
print(" ")
print("number of records is ", len(df_rearranged))

df_melted = pd.melt(df_rearranged, id_vars = ['Make', 'Model'], value_vars = ['2005', '2006', '2007', '2008', '2009', '2010', '2011', '2012', '2013', '2014', '2015', '2016', '2017', '2018', '2019', '2020', '2021'], \
                    var_name = 'Sales_Year', value_name = 'Sales')



print(" ")
print('** df_rearranged **')
print(df_melted.head())
print(" ")
print("number of records is ", len(df_melted))
print(" ")

print("part of dataframe")
print(" ")
print(df_melted[5500:5520])
