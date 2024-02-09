# getRoles retrieves all TFs and Enhanced CAs from the course.
# countGraders figures out how many grades were given by each TF/ECA for given assignment
# outputs Excel File "GradeCounts.xlsx" with names of graders and # graded for each

# import modules

import sys
import json
from pip._vendor import requests
import pandas as pd
from xlsxwriter import Workbook

# headers with token

token = #ENTER API ACCESS TOKEN AS STRING
headers = {'Authorization': token}

# enter the course_id and assignment_id here

desired_course = #ENTER COURSE ID NUMBER
desired_assignment = #ENTER ASSIGNMENT ID NUMBER
desired_roles = ["Enhanced Course Assistant", "Teaching Fellow"]

# given a course id, fetches info of all users with desired roles
def getRoles(course_id, roles):
    
    desired_users = []

    # for each desired role, add all users with that role
    for role in roles:
        
        # API Call
        enrollments = requests.get("https://canvas.harvard.edu/api/v1/courses/%s/enrollments?per_page=10" %str(course_id), params="role[]=%s" %role, headers = headers)
        raw = enrollments.json()
        
    
        # handle Canvas pagination
        while "next" in enrollments.links:
            
            enrollments = requests.get(enrollments.links['next']['url'], headers = headers)
            raw.extend(enrollments.json())

        # record the id, name, and role of each user
        for i in range(len(raw)):
            user_info = {}
            user_info["id"] =  raw[i]["user_id"]
            user_info["name"] =  raw[i]["user"]["name"]
            user_info["role"] =  role      
            desired_users.append(user_info)

    return desired_users

# given an assignment id
def countGraders(course_id, assignment_id, graders):

    # dictionary where keys are grader ids and values are number of submissions graded
    grader_counts = {}
    for grader in graders:
        grader_counts[grader] = 0

    # API call
    submissions = requests.get("https://canvas.harvard.edu/api/v1/courses/%s/assignments/%s/submissions" %(str(course_id), str(assignment_id)), headers = headers)
    raw = submissions.json()

    # handle Canvas pagination
    while "next" in submissions.links:     
        submissions = requests.get(submissions.links['next']['url'], headers = headers)
        raw.extend(submissions.json())
    
    # record number of graded submissions for each grader
    for i in range(len(raw)):
        for grader in graders:
            if raw[i]["grader_id"] == grader:
                grader_counts[grader] += 1

    return grader_counts

graders = getRoles(desired_course, desired_roles)

grader_ids = []

for grader in graders:
    grader_ids.append(grader["id"])

counts = countGraders(desired_course, desired_assignment, grader_ids)

final_data = {}

for grader in graders:
    final_data[grader["name"]] = counts[grader["id"]]

df = pd.DataFrame(data=final_data, index=[0])
df = (df.T)
df.to_excel('GradeCounts.xlsx') 
print("Done!")
    












