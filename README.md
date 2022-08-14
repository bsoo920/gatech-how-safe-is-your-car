# Intro
_"**How safe is your car**, especially when compared to other similar vehicles?"_ is the question that I wanted to answer by leading a team of 4 for a [Data & Visual Analytics graduate class](https://omscs.gatech.edu/cse-6242-data-visual-analytics) project at GeorgiaTech.  I conceived and architected the project, and wrote the majority of the python code (except for `d_gui_d3.py`) (see [commits](https://github.com/bsoo920/gatech-how-safe-is-your-car/commits/main)).

# 3-minute intro video
[![IMAGE ALT TEXT HERE](https://img.youtube.com/vi/a0d3QQtqGzE/1.jpg)](https://www.youtube.com/watch?v=a0d3QQtqGzE)

# Description
This project analyses automobile accident fatality data and sheds light on the question "Given a specific make/model/model-year (M/M/MY), what is the number of fatalities per year per million vehicles?"  It pulls data from two sources:
1. [NHTSA FARS API](https://crashviewer.nhtsa.dot.gov/CrashAPI) for fatalities data
1. [GoodCarBadCar](https://goodcarbadcar.net) for sales volume by M/M/MY

The analytics is generally done in these steps:
1. The fatalities data is used to scatter-plot fatality counts (y-axis) over accident years (x-axis) for either a specific M/M/MY, or an aggregation level of Make & Model (such as all models for a specific manufacturer).  (The terms "make" and "manufacturer" are used interchangeably in this project.)  
2. The corresponding sales volume (in millions) is then used to divide the above numbers.  This normalizes the data such that the fatality _numbers_ for different M/M/MY are converted into fatality _rates_ that can now be compared between M/M/MY's.
3. Linear regression (LR) is applied to the normalized scatter plot.
4. The first accident year of the LR is taken as the initial fatality rate for that M/M/MY.  This eliminates time-dependent factors such as mechanical breakdowns or driver behavioral changhes.
5. These "first-year" LR data points are extracted for multiple model years, so that a plot of fatality rate of a Make & Model can be plotted over model years.

Analyses 1-3 above are available via GUI driven by D3.  Analyses 1-5 are available via simple commands in Jupyter notebooks.

# Installation
#### Requirements:
All setup steps are done at command line or in Terminal, unless otherwise stated.
- Python 3.9 (or higher) 
- Python libraries: numpy, pandas, matplotlib, flask, flask_cors
- Chrome v92.0 (or higher)

### Initial Data Setup
#### NHTSA FARS API
1. Execute `python`[`a_download_crash.py`](a_download_crash.py) - this downloads crash data into [`NHTSA-FARS-download/`](NHTSA-FARS-download)
2. Execute `python`[`a_download_modelID_lookup.py`](a_download_modelID_lookup.py) - this downloads:
     1. List of vehicle makes & IDs into [`NHTSA-FARS-download/make2020.csv`](NHTSA-FARS-download/make2020.csv)
     2. List of vehicle models & IDs (by make) into [`NHTSA-FARS-download/model-lookup/`](NHTSA-FARS-download/model-lookup)
#### GoodCarBadCar
1. Go to [GoodCarBadCar](https://goodcarbadcar.net) and manually download sales data.
2. Manually clean up the data. See history of [`car_sales_ID_NoOther.csv`](car_sales_ID_NoOther.csv).

### Data Pre-processing
1. Execute `python`[`b_offline_data_processing.py`](b_offline_data_processing.py) which does the following:
    1. Reads and aggregates crash data to the M/M/MY level and saves pandas dataframe as a pickle `.pkl` file.
    2. Reads the sales data and transposes it to database table format and saves as `.pkl` file.

# Execution
### Analytics GUI
From root directory of this project:
1. Start http server by executing `python -m http.server 8887`  (To end session, issue `Ctrl+C`)
2. Start analytics service by executing `python`[`d_gui_d3.py`](d_gui_d3.py)
3. Go to http://127.0.0.1:8887/visualization02.html in Chrome
4. Have fun!
<img width="1024" alt="d3portal" src="https://user-images.githubusercontent.com/26016937/184518690-ca484db5-d117-488a-a002-d955fcc6ec5e.png">

### Ad-hoc analytics
The following `.ipynb` files in the root directory are Jupyter notebooks that can be viewed directly on Github for past run results.  Generally an `xxx.ipynb` gives a high level analysis, while `xxx_details.ipynb` gives a granular breakdown.

**Non-normalized** fatality rates of select **manufacturers** across various model years:
- [`ex_makes.ipynb`](ex_makes.ipynb)
    - [`ex_makes_details.ipynb`](ex_makes_details.ipynb) - A breakdown of the above, showing the linear regression done on each make & model year.

The two notebooks below are the **normalized** versions of the two above:
- [`ex_makes_normalized.ipynb`](ex_makes_normalized.ipynb)
    - [`ex_makes_normalized_details.ipynb`](ex_makes_normalized_details.ipynb)

**Normalized** fatality rates of select **make & models** across various model years:
- [`ex_models_normalized.ipynb`](ex_models_normalized.ipynb) (image below)
    - [`ex_models_normalized_details.ipynb`](ex_models_normalized_details.ipynb) - A breakdown of the above, showing the linear regression done on each make & model year.
<img width="1774" alt="adhoc" src="https://user-images.githubusercontent.com/26016937/184518706-91da5e72-7425-4bb6-b996-ad967840cc23.png">

### Interactive ad-hoc analytics in Jupyter notebook
- [ex_playground.ipynb](ex_playground.ipynb) is an introductory notebook for getting familiar with running ad hoc analysis in this project.
- All `.ipynb` files above can also be opened in Jupyter notebook and editd with various parameters to run different analyses.
