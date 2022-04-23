from c_online_linear_regression import *

##-----Set up Server-----##
import flask as fl
import flask_cors as fl_c
app = fl.Flask(__name__)
fl_c.CORS(app)
year_input = 0
make_input = ""
model_input = ""

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

    _,_, fatality = linear_regress(dfMasterCrashAgg
        , f'{year_name} {make_name} {model_name} ({usedYear} sales of {sales} vehicles)'
        , regress_String, denom=sales, showPlot=False, savePlot=True);

    response["fatality"] = np.ceil(fatality)
    print("Normalized annual fatality rate of ", fatality);
    return response


if __name__ == '__main__':
    app.run(host="127.0.0.1", port=8888)
