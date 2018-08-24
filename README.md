# aemvl-backend
Python-based webserver for querying airborne electromagnetics data.

## Getting Started
Clone the repository to aemvl-backend:  
`git clone git@github.com:CSIRO-GeoscienceAnalytics/aemvl-backend.git`  
`cd aemvl-backend`  

Install Conda 
https://www.anaconda.com/download/

Run the following commands:  
`conda create --name aemvl-backend python=3.5`  

Linux Only:  
`source activate aemvl-backend`  

Windows Only:  
`activate aemvl-backend`  

`Set environment variable if not set. E.g.: GDAL_DATA=C:\Anaconda3\envs\aemvl-backend\Library\share\epsg_csv`  

`conda install --file requirements.txt`  
`cp aemvl-backend.config.default aemvl-backend.config`  
`# Edit the settings in aemvl-backend.config`  
`python main.py`  

Run tests (if on Windows you'll need to install bash and curl. I recommend using https://www.cygwin.com/ to install them):  
`cd tests`  
`./curl_test.sh http://localhost:8080`
