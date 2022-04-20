import requests
from datetime import datetime
from zipfile import ZipFile
import os
dir = 'NHTSA-FARS-download/'

# datetime object containing current date and time
print(datetime.now().strftime("%d/%m/%Y %H:%M:%S"))


for yr in range(2020,1999,-1):
    yyyy=str(yr)
    url = 'https://www.nhtsa.gov/file-downloads/download?p=nhtsa/downloads/FARS/'+yyyy+'/National/FARS'+yyyy+'NationalCSV.zip'
    # https://www.nhtsa.gov/file-downloads/download?p=nhtsa/downloads/FARS/2020/National/FARS2020NationalCSV.zip

    try:
        r = requests.get(url, allow_redirects=True)
        open('NHTSA-FARS-download/FARS'+yyyy+'NationalCSV.zip', 'wb').write(r.content)

        with ZipFile(dir + 'FARS' + yyyy + 'NationalCSV.zip', 'r') as zipObject:

            for fileName in zipObject.namelist():
                if fileName.lower() == 'vehicle.csv':
                    zipObject.extract(fileName, dir)
                    os.rename(dir + fileName, dir + 'vehicle' + yyyy + '.csv')

        print(yyyy, 'success', datetime.now().strftime("%d/%m/%Y %H:%M:%S"))

    except:
        print(yyyy, 'failed')

