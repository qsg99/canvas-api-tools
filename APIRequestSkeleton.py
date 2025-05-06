# import modules
import json
from pip._vendor import requests
import pandas as pd
from xlsxwriter import Workbook

#target filepath and name for output excel file
filepath = "filepath here" #YOUR FILEPATH AND NAME HERE
filepath = filepath + ".xlsx"

# put ids of endpoints you are interested in here

course_id = 6617


# if your api key is in a text file, put the filepath here
with open("/Users/georgeqiao/Desktop/ATG/PythonScripts/ExEdAPIKey.txt", 'r') as text:
    key = text.read()

# headers with token
token = 'Bearer ' + key #paste api access token here, after the space after the word Bearer
headers = {'Authorization': token}

#GENERAL LEADING LINES END HERE

# get all submissions to all desired assignments. We will use this to find reviewees in the for loop below
#enrollments_data = []


#enrollments = requests.get("https://exed.canvas.harvard.edu/api/v1/courses/6617/enrollments?per_page=100", headers = headers)
#enrollments_data.extend(enrollments.json())

#while "next" in enrollments.links:
        
    #enrollments = requests.get(enrollments.links['next']['url'], headers = headers)
    #enrollments_data.extend(enrollments.json())

#print(len(enrollments_data))

print("Done!")
