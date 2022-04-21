import csv as csv
import numpy as np
import pandas as pd


def readCrashData(accYearStart, accYearEnd, nrows=None):
    dir = 'NHTSA-FARS-download/'
    usecols = ['MOD_YEAR', 'MAKE', 'MODEL', 'DEATHS']

    dfCrash = None
    for accYear in range(accYearStart, accYearEnd + 1):

        print( accYear,'', end='')
        df = pd.read_csv(
            f'{dir}vehicle{accYear}.csv', encoding='latin1', header=0, usecols=usecols, nrows=nrows)  
            #.astype(str)      # , dtype={'DEATHS':'int32'}        

        df['ACC_YEAR'] = accYear
        if dfCrash is None:
            dfCrash = df
        else:
            dfCrash = pd.concat([dfCrash, df], ignore_index=True)
    
    print('')
    dfCrash = dfCrash.rename(columns = {'MAKE':'Make_ID', 'MODEL':'Model_ID', 'DEATHS':'fatalities'})

    return dfCrash


def aggregate(dfCrash, filterCondition='MOD_YEAR>=1999', groupBy=['MOD_YEAR', 'Make_ID', 'Model_ID','ACC_YEAR']):
    # print('filtering by',filterCondition, ', aggregating by',groupBy)

    dfCrashAgg = dfCrash.query(filterCondition).groupby(groupBy) \
        .agg(fatalities=pd.NamedAgg(column='fatalities', aggfunc=sum)) \
        .reset_index()

    return dfCrashAgg


def getSales( verbose=False, nrows = None):
    dir = 'car_sales_data/'

    df_original = pd.read_csv(f'{dir}car_sales_ID_NoOther.csv', encoding='latin1', header=0, nrows=nrows)

    df_melted = pd.melt(df_original
                        , id_vars = ['Make_Name', 'Model_Name','Model_ID','Make_ID']
                        , value_vars = [str(x) for x in range(2005,2021+1)]
                        , var_name = 'Sales_Year'
                        , value_name = 'Sales'
                       ).astype( {'Model_ID':'int32','Make_ID':'int32', 'Sales_Year':'int32', 'Sales':'int32'})  
    
    if verbose:
              
        print("df_original number of records is ", len(df_original))
#         print(df_original.dtypes)  
        
        print("df_melted number of records is ", len(df_melted))
#         print(df_melted.dtypes)

#         print(df_melted[5500:5520])
#         print(df_melted.query('Sales!="0"')[:20])
        print(df_melted.query('Make_Name=="Acura" and Model_Name=="MDX"'))
        print(df_melted.query('Make_Name=="Tesla" or  Model_Name=="Tesla"'))
        
        test2 = df_melted.query('Make_ID==49 and Model_ID==40 and Sales_Year==2005')
        print(test2)
        print(test2.dtypes)

    return df_melted


if __name__ == '__main__':

    df_agg = aggregate( readCrashData(accYearStart=2000, accYearEnd=2020)
                       ,filterCondition = 'MOD_YEAR>=1999'
                       ,groupBy = ['MOD_YEAR', 'Make_ID', 'Model_ID','ACC_YEAR']
                      )
    df_agg.to_pickle( 'program_data/master_crash_aggregate.pkl')
    
    # test aggregate
    dfMasterCrashAgg = pd.read_pickle('program_data/master_crash_aggregate.pkl')
    print(dfMasterCrashAgg[:5])

    # get sales data
    df = getSales(verbose=True)
    df.to_pickle( 'program_data/sales_melted.pkl')
    
    dfSales = pd.read_pickle('program_data/sales_melted.pkl')
    print(dfSales[:5])





