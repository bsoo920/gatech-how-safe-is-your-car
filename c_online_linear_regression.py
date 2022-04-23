import csv as csv
import numpy as np
import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt
import platform 
from b_offline_data_processing import aggregate

##-----Set up Server-----##
import flask as fl
import flask_cors as fl_c
app = fl.Flask(__name__)
fl_c.CORS(app)
year_input = 0
make_input = ""
model_input = ""

def getData(verbose=False):
    # get master aggregate
    dfMasterCrashAgg = pd.read_pickle('program_data/master_crash_aggregate.pkl')
    
    # get sales data    
    dfSales = pd.read_pickle('program_data/sales_melted.pkl')
    
    if verbose:
	    print(dfMasterCrashAgg[:5])
	    print(dfSales[:5])
    
    return dfMasterCrashAgg, dfSales    
    
def reaggregate( dfCrashAgg, groupBy=None):
    # If groupBy==None, then no further aggregation is done, i.e. use agg level of dfCrashAgg.
    # Otherwise groupBy should be list of columns, e.g. ['MOD_YEAR', 'Make_ID', 'ACC_YEAR']

    if groupBy != None:
        df = aggregate( dfCrashAgg, groupBy=groupBy )
    else:
        df = dfCrashAgg
    
    return df

# df_sales:  
#      Make_Name Model_Name  Model_ID  Make_ID  Sales_Year  Sales
# 3        Acura        MDX       421       54        2005  57948
# 610      Acura        MDX       421       54        2006  54121
# 1217     Acura        MDX       421       54        2007  58606

def lookupSales(dfSales, Sales_Year=None, Make_ID=None, Model_ID=None, verbose=False ):
    '''
    Get closest Sales_Year sales.
    E.g. if 2000 is requested, 2005 sales is returned since that's the earliest sales data available.
    
    if Model_ID==None, then Make level sales will be returned.
    '''
    
    if Sales_Year==None and Make_ID==None and Model_ID==None:
        df = dfSales[['Sales']].agg('sum')
        year, sales =  None, df.tolist()[0]

    else:

        condition = []
        if Sales_Year != None:
            condition.append(f'Sales_Year>={Sales_Year}')
        if Make_ID != None:
            condition.append(f'Make_ID=={Make_ID}')
        if Model_ID != None:
            condition.append(f'Model_ID=={Model_ID}')
        
        condition = ' and '.join(condition)
        
            
        df = dfSales.query(condition)

        if df.empty:
            year, sales = None, None
        
        else:
            # further sales aggregation needed
            grains = ['Make_ID','Model_ID','Sales_Year']

            if Make_ID==None:
                grains.remove('Make_ID')

            if Model_ID==None:
                grains.remove('Model_ID')

            if Sales_Year==None:
                grains.remove('Sales_Year')

            df = df.groupby( grains ) \
                    .agg(Sales=pd.NamedAgg(column='Sales', aggfunc=sum)) \
                    .reset_index()

            if Sales_Year!=None:
                year, sales = df.Sales_Year.tolist()[0], df.Sales.tolist()[0]
            else:
                year, sales =                      None, df.Sales.tolist()[0]

                
    if verbose:
        print(condition)
        print('year',year,'sales',sales)
        print()

    return year, sales

def linear_regress(dfCrashAgg, name, filterCondition, denom=None, showPlot=True):
    k = name

    if filterCondition==None:
        v = dfCrashAgg
    else:
        v = dfCrashAgg.query(filterCondition)
    
    if v.empty:
        return None,None,None
    
    # start of linear regression calculation
    # create lists for year and fatalities to iterate through
    x_years = v['ACC_YEAR'].to_list()
    y_fatal = v['fatalities'].to_list()
    
    if denom != None:
        y_fatal = [y/(denom/1e6) for y in y_fatal]
        permillion = ' per million cars'
    else:
        permillion = ''
    
    yearOne = min(x_years)

    # find number of years of data
    num_years = len(x_years)

    # get regression coefficients for all data provided at least 2 years of data
    # otherwise coefficients = None and assign coefficients to coeff_all dictionary

    slope, intercept, initFatality = None, None, None
    if num_years > 1:
        slope, intercept = np.polyfit(x_years, y_fatal, 1)
        y_cal2 = []
        for m in range(len(x_years)):
            y_cal2.append(x_years[m]*slope + intercept)

    # print linear regression on top of scatter plot (if slope != None)
    if  slope != None:   
        initFatality = slope * yearOne + intercept
            
        fig,ax = plt.subplots()
        ax.scatter(x_years,y_fatal)
        ax.set_title(k)
            
        ax.plot(x_years, y_cal2, 'r') 
        ax.xaxis.set_major_formatter(mpl.ticker.StrMethodFormatter('{x:4.0f}'))
        ax.xaxis.set_label_text('accident year')
        ax.yaxis.set_label_text('annual fatality' + permillion)

        if showPlot:
            plt.show()        
            print(k)
            print(f'Slope {slope} intercept {intercept}')
            print(f'Initial fatality rate is {initFatality} per year')
        else:
            # FROM: 2012 Acura (All Models) (2012 sales of 156216 vehicles)
            # TO  : 2012 Acura (All Models)
            name = name[:name.rfind('(')-1]

            if platform.system() == "Windows":
                plt.savefig("graphs\\" + name + ".png", bbox_inches="tight", dpi=70)
            elif platform.system() == "Darwin" or platform.system() == "Linux":
                plt.savefig("graphs/" + name + ".png", bbox_inches="tight", dpi=70)
    
    return slope, intercept, initFatality


def summarize_by_makeyear( dfCrashAgg, modelYrStart, modelYrEnd, makes_dict, dfSales=pd.DataFrame()
                         , showLinearRegress=False): 
    # **************************
    # BY MANUFACTURER **********
    # **************************
    # if dfSales is provided, it'll be used for normalization
    
    df = reaggregate(dfCrashAgg, groupBy=['MOD_YEAR', 'Make_ID', 'ACC_YEAR'])
    series={}    
    
    for makeName,ID in makes_dict.items():
        Make_ID  = ID['Make_ID']
        # Model_ID = ID['Model_ID']
        condition = f'Make_ID=={Make_ID}'  #' and Model_ID=={Model_ID}'
        
        x,y=[],[]
        for modelYear in range(modelYrStart, modelYrEnd + 1):
            
            if not dfSales.empty:
                year, sales = lookupSales(
                    dfSales, Sales_Year=modelYear, Make_ID=Make_ID, Model_ID=None, verbose=False)
                
                # sales could be None if not found
                if sales != None:
                    salesTitle = f' ({year} sales of {sales} vehicles)'
                    
            else:
                sales = None
                salesTitle = ''
            
            if dfSales.empty or sales!=None:
                _,_, initFatality = linear_regress(
                      dfCrashAgg      = df
                    , name            = f'{modelYear} {makeName} {salesTitle}'
                    , filterCondition = f'MOD_YEAR=={modelYear} and ACC_YEAR>=MOD_YEAR and '+condition
                    , denom           = sales
                    , showPlot        = showLinearRegress
                    )

                if initFatality != None:
                    x.append(modelYear)
                    y.append(initFatality)
        
        series[makeName] = [x,y]

    fig, ax = plt.subplots()

    i=1
    for makeName,data in series.items():
        if i<=10:
            fmt='solid'
        elif i<=20:
            fmt='dashed'
        else:
            fmt='dashdot'

        ax.plot(data[0], data[1], linestyle=fmt, label=makeName)
        i+=1
    
    if not dfSales.empty:
        permillion = ' per million cars'
    else:
        permillion = ''
    
    ax.set_xlabel('Model Year')  # Add an x-label to the axes.
    ax.set_ylabel('Annual Fatalities' + permillion)  # Add a y-label to the axes.
    ax.xaxis.set_major_formatter(mpl.ticker.StrMethodFormatter('{x:4.0f}'))
    ax.legend()
    plt.show()


def summarize_by_modelyear( dfCrashAgg, modelYrStart, modelYrEnd, models_dict, dfSales=pd.DataFrame()
                          , showLinearRegress=False): 
    # if dfSales is provided, it'll be used for normalization
    
    series={}
    for modelName,ID in models_dict.items():
        Make_ID  = ID['Make_ID']
        Model_ID = ID['Model_ID']
        condition = f'Make_ID=={Make_ID} and Model_ID=={Model_ID}'
        
        x,y=[],[]
        for modelYear in range(modelYrStart, modelYrEnd + 1):
            
            if not dfSales.empty:
                year, sales = lookupSales(
                    dfSales, Sales_Year=modelYear, Make_ID=Make_ID, Model_ID=Model_ID, verbose=False)
                
                # sales could be None if not found
                if sales != None:
                    salesTitle = f' ({year} sales of {sales} vehicles)'
            else:
                sales = None
                salesTitle = ''
            
            if dfSales.empty or (sales!=None and sales>0):
                _,_, initFatality = linear_regress(
                      dfCrashAgg      = dfCrashAgg
                    , name            = f'{modelYear} {modelName} {salesTitle}'
                    , filterCondition = f'MOD_YEAR=={modelYear} and ACC_YEAR>=MOD_YEAR and '+condition
                    , denom           = sales
                    , showPlot        = showLinearRegress
                    )

                if initFatality != None:
                    x.append(modelYear)
                    y.append(initFatality)
        
        series[modelName] = [x,y]

    fig, ax = plt.subplots()

    i=0
    for modelName,data in series.items():
        if i<=10:
            fmt='solid'
        elif i<=20:
            fmt='dashed'
        else:
            fmt='dashdot'

        ax.plot(data[0], data[1], linestyle=fmt, label=modelName)
        i+=1
    
    if not dfSales.empty:
        permillion = ' per million cars'
    else:
        permillion = ''
    
    ax.set_xlabel('Model Year')  # Add an x-label to the axes.
    ax.set_ylabel('Annual Fatalities' + permillion)  # Add a y-label to the axes.
    ax.xaxis.set_major_formatter(mpl.ticker.StrMethodFormatter('{x:4.0f}'))
    ax.legend()
    plt.show()


@app.route("/getValues")
def getValues():
    year_input = fl.request.values.get("year", None)
    make_input = fl.request.values.get("make_ID", None)
    make_name = fl.request.values.get("make_name", None)
    model_input = fl.request.values.get("model_ID", None)
    model_name = fl.request.values.get("model_name", None)
    
    year_val = year_input
    make_val = make_input
    model_val = model_input
    year_name = year_input

    if (year_input == "None"):
        year_val = None;
        year_name = "(All Years)";
    if (make_input == "None"):
        make_val = None;
    if(model_input == "None"):
        model_val = None;

    regress_String = ""
    ## Return value
    response = {"fatality": -1};

    dfMasterCrashAgg, dfSales = getData() ##get data

    print("Values:", year_input, make_input, model_input, "being used");
    usedYear, sales = lookupSales(dfSales, Sales_Year=year_val, Make_ID=make_val, Model_ID=model_val, verbose=False)
    print("Successfully executed:", usedYear, sales);

    group = ["MOD_YEAR", "Make_ID", "Model_ID", "ACC_YEAR"];
    print("group:", group);
    if(year_input == "None"):
        group.remove("MOD_YEAR");
    if(make_input == "None"):
        group.remove("Make_ID");
    if(model_input == "None"):
        group.remove("Model_ID");

    if (year_input == "None") or (make_input == "None") or (model_input == "None"):
        dfMasterCrashAgg = reaggregate(dfMasterCrashAgg, groupBy=group);
    
    for i in range(0, len(group)):
        if group[i] != "ACC_YEAR":
            if group[i] == "MOD_YEAR":
                regress_String = regress_String + group[i] + "=="
                regress_String = regress_String + year_input + " "
            if group[i] == "Make_ID":
                regress_String = regress_String + group[i] + "=="
                regress_String = regress_String + make_input + " "
            if group[i] == "Model_ID":
                regress_String = regress_String + group[i] + "=="
                regress_String = regress_String + model_input + " "
        if i < len(group)-1:    
            regress_String = regress_String + "and "

    regress_String = regress_String + "ACC_YEAR>=MOD_YEAR";
    print(regress_String);
    # _,_, fatality = linear_regress(dfMasterCrashAgg, year_name + " " + make_name + " " + model_name, regress_String, denom=sales, showPlot=False);

    _,_, fatality = linear_regress(dfMasterCrashAgg
        , f'{year_name} {make_name} {model_name} ({usedYear} sales of {sales} vehicles)'
        , regress_String, denom=sales, showPlot=False);

    response["fatality"] = np.ceil(fatality)
    print("Normalized annual fatality rate of ", fatality);
    return response
    

if __name__ == '__main__':
    app.run(host="127.0.0.1", port=8888)

'''    
    dfMasterCrashAgg, dfSales = getData(verbose=True)

    # test lookupSales
    lookupSales(dfSales, Sales_Year=2005, Make_ID=49, Model_ID=40, verbose=True) #camry
    lookupSales(dfSales, 2005, 49, None , True)  # toyota
    lookupSales(dfSales, 2005, 49, 4000 , True)  # non-existent model

    # test linear regression    
    linear_regress(dfMasterCrashAgg,'camry' , "MOD_YEAR==1999 and Make_ID==49 and Model_ID==40 ") 
    # with sales volume normalization
    year, sales = lookupSales(dfSales, Sales_Year=1999, Make_ID=49, Model_ID=40, verbose=True) #camry
    linear_regress(dfMasterCrashAgg,'camry' , "MOD_YEAR==1999 and Make_ID==49 and Model_ID==40", denom=sales) 


    #test re-aggregate & linear regression at Make level   
    dfCrashAggByMake = reaggregate(dfMasterCrashAgg, groupBy=['MOD_YEAR', 'Make_ID', 'ACC_YEAR'])
    linear_regress(dfCrashAggByMake,'toyota' , "MOD_YEAR==1999 and Make_ID==49 ")  
    # with sales volume normalization
    year, sales = lookupSales(dfSales, Sales_Year=1999, Make_ID=49, Model_ID=None, verbose=True) #camry
    print('Year & sales used are', year,',', sales)
    _,_, fatality = linear_regress(dfCrashAggByMake,'toyota' , "MOD_YEAR==1999 and Make_ID==49 ", denom=sales)     
    print('fatality is ', fatality) 

    # test summarize_by_makeyear (manufacturer)
    x = {}
    x['toyota'] = {'Make_ID':49}   
    x['ford'  ] = {'Make_ID':12}   
    modelYrStart=2004
    modelYrEnd  =2006
    
    summarize_by_makeyear( dfMasterCrashAgg, modelYrStart, modelYrEnd, makes_dict=x)    
    # with normalization
    summarize_by_makeyear( dfMasterCrashAgg, modelYrStart, modelYrEnd, makes_dict=x, dfSales=dfSales)


    # test summarize_by_modelyear (make & model)
    x = {}
    x['tacoma']        = {'Make_ID':49, 'Model_ID':472}   
    x['mustang']       = {'Make_ID':12, 'Model_ID':3  } 
    x['ford_f_series'] = {'Make_ID':12, 'Model_ID':481}   
    
    summarize_by_modelyear( dfMasterCrashAgg, modelYrStart, modelYrEnd, models_dict=x)
    # with normalization
    summarize_by_modelyear( dfMasterCrashAgg, modelYrStart, modelYrEnd, models_dict=x, dfSales=dfSales)
'''

    

    







