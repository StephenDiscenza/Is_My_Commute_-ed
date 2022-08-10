# Is My Commute !@#$ed?
## Video Demo:  <URL HERE>
## Description:
Living in NYC inevitably means experiencing the joys of our miserably maintained subway system. Very often a 30 minute commute turns into a 60 minute odyssey highlighting the decline of American society. There are a nearly infinite number of things that can go wrong and it's very hard to tell how bad a particular trip is going to be, but it would be nice to know ahead of time that it's probably not going to be good. There currently exists a site called (with censoring) istheltrain!@#$ed.com which does exactly this. I've decided to do the same for any commute, including those spanning multiple subway lines.  
  
Users can input any number of commutes each with any number of legs, meaning segments of different lines. These commutes are checked for current alerts and scored according to the severity of those alerts. A result is returned to the user as well as the text for the alerts found.

### Files:
The project is a Python Flask web app organized very similarly to week 9's finance homework. The templates folder contains all HTML files, the static folder has mostly boilerplate stuff plus a couple javascript files and one css file, and the app directory contains these folders plus all the Python files.  
  
The Python files are slightly different than the week 9 example. Instead of having everything in one app.py file there is an \_\_init\_\_.py which is responsible for getting the app running and then a routes.py file which contains all the endpoint logic. Additionally, there are three helper files which contain some functions used as part of various endpoints' logic. This was done just to keep the routes file from getting cluttered. 
  
Outside of the app directory is a requirements.txt file which lists all the packages/libraries used in the project. 

## Set Up
There is some quirkiness with the required packages. In particular the most recent version of protobuf, included when installing gtfs-realtime-bindings is broken. As a workaround, you can uninstall protobuf and reinstall it with:  
- pip install protobuf==3.20.1

The project also requires an env variable with the name: MTA_API_KEY  
to be set with a key for MTA's realtime data. Signing up to get a key is free and can be done here: https://api.mta.info/#/signup  

## Running the App
It's generally best practice to create a virtual environment and I suggest that here as well. After installing all the packages defined in the requirements.txt file, navigate to the outermost directory of this project (the one containing the app directory) and execute the flask run command. 

## Improvements
Some general areas for improvement are: 
- Looking into a more robust algorithm for determining whether a commute is !@#$ed. At the moment alerts anywhere along the line count the same no matter their proximity to stops used in the commute. 
- Testing algorithm against historical data
- Allowing users to delete legs when adding and editing commutes. At present, once a leg is added it can't be removed without deleting the commute record entirely. This is considered a minor inconvenience since there aren't likely to be more than 3 or 4 legs in any given commute.
    
