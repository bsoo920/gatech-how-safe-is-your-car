# Description
This project analyses automobile accident fatality data and sheds light on the question "Given a specific make/model/model-year (M/M/MY), what is the number of fatalities per year per million vehicles?"  It pulls data from two sources:
1. [NHTSA FARS API](https://crashviewer.nhtsa.dot.gov/CrashAPI) for fatalities data
1. [GoodCarBadCar](https://goodcarbadcar.net) for sales volume by M/M/MY

The analytics is generally done in these steps:
1. The fatalities data is used to scatter-plot fatality counts (y-axis) over accident years (x-axis) for either a specific M/M/MY, or an aggregation level of Make & Model (such as all models for a specific manufacturer).  
2. The corresponding sales volume (in millions) is then used to divide the above numbers.  This normalizes the data such that the fatality _numbers_ for different M/M/MY are converted into fatality _rates_ that can now be compared between M/M/MY's.
3. Linear regression (LR) is applied to the normalized scatter plot.
4. The first accident year of the LR is taken as the initial fatality rate for that M/M/MY.  This eliminates time-dependent factors such as mechanical breakdowns or driver behavioral changhes.
5. These "first-year" LR data points are extracted for multiple model years, so that a plot of fatality rate of a Make & Model can be plotted over model years.

Analyses 1-3 above are available via GUI driven by D3.  Analyses 1-5 are available via simple commands in Jupyter notebooks.

# Installation



# Execution




# Table Visualization
Required Libraries/Softwares:
Python 3.9 (or higher)
libraries: csv, numpy, pandas, matplotlib, matplotlib.pyplot, flask, flask_cors
Chrome v92.0 (or higher): browser to display the table visualization
Python http server (or any software capable of hosting a web server)

## Flask Setup 
make sure [Flask] (https://flask.palletsprojects.com/en/2.1.x/installation/) is installed inside Scripts folder where Python is located
1. Create a project folder and a venv folder inside the project folder 
```bash
> mkdir myproject
> cd myproject
> py -3 -m venv venv
```
2. Activate the environment
```bash
> venv\Scripts\activate
```
your shell prompt will change to show the name of the activated environment

3. Inside the activated environment, install Flask using [pip] (https://pip.pypa.io/en/stable/)
```bash
$ pip install Flask
```

## Flask CORS Setup 
make sure [Flask CORS] (https://flask-cors.readthedocs.io/en/latest/) is installed inside Scripts folder where Python is located
1. Install the extension using [pip] (https://pip.pypa.io/en/stable/)
```bash
$ pip install -U flask-cors
```

## Setting up the web server
1. Run a web server with the following command:
```bash
python -m http.server 8887 &
```

2. On a separate command prompt window, from the "Project" directory (it should be the parent directory of this file)
```bash
python c_online_linear_regression.py
```

3. Finally go to [this URL] (http://127.0.0.1:8887/visualization02.html) to open the visualization 

# Interacting with the table
## Drop downs
- Dropdown menus provides values to return within the table itself as well as feed it to "c_online_linear_regression.py"
- Dropdown options are gathered from "car_sales_ID_NoOther.csv" (in the same directory as this file)
- Once the plus button (on the right of the dropdown menus) is pressed, values are fed to "c_online_linear_regression.py" to gather the fatality 
  rate to create the bar under the "Fatality per Million Cars" column
- Values chosen within the dropdown menus will also be added to the table under their respective columns 
- The reset button (on the right of the plus button) will reset all drop down selections to "All" which is the default selection

## Table
- Table Headers "Model Year", "Make", "Model", "Fatalities per Million Cars", and "Trash" are interactible
	- Clicking "Model Year" or "Make" or "Model" or "Fatalities per Million Cars" the first time sorts each respective column in ascending 
	  order
	- Clicking "Model Year" or "Make" or "Model" or "Fatalities per Million Cars" a second time sorts each respective column in descending
	  order
	- Clicking the "Trash" header will delete all rows within the table
		- The graph, if any are displayed, will be deleted upon the deletion of all rows
- Additional buttons will appear along side each row in the table:
	- The "See Graph" button, when clicked, display the graph created within "c_online_linear_regression.py" with values from the drop down menus
		- The graph is displayed under the table with the appropriate values in the row
	- The "trash" button next to each row allows for the deletion of each singular row of which it is next to
		- The graph, if any are displayed, will be deleted upon the deletion of the row

# Foot Notes
Normalization is appplied to the y-axis only. Therefore, when "All" Model Years are selected, the data points will often appear as a straight with
a positive slope. This is because in the early "accident years", only the similarly early "model years" could contriute.
