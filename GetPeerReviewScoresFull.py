# given a rubric, fetches all peer review scores given to desired assignment using that rubric, as well as detailed rubric breakdown information
# this script will create a spreadsheet with peer review information, and save it in the same folder where the script is located

# import modules
import json
from pip._vendor import requests
import pandas as pd
import os
from xlsxwriter import Workbook

# the location of this python file
script_dir = os.path.dirname(os.path.abspath(__file__))


#target filepath and name for output excel file
filename = "07.01.25Test1" #YOUR FILEPATH AND NAME HERE
filename = filename + ".xlsx"

filepath = os.path.join(script_dir, filename)

# put the course, rubric, and assignment ids here

rubric_id = 32329
course_id = 143616
assignment_id = 907485

# if your api key is in a text file, use these lines to read the key from the text file
with open("Desktop/ATG/PythonScripts/CanvasAPIKey.txt", 'r') as text:
    key = text.read()
    

# headers with token
#paste api access token here if it is not in a text file
#key = ''
token = 'Bearer ' + key 
headers = {'Authorization': token}



def get_assessments(course_id, rubric_id, assignment_id, headers):
    # API Call to get information from the rubric, including assessments made with that rubric and associations of that rubric with courses / assignments

    rubric = requests.get("https://canvas.harvard.edu/api/v1/courses/%d/rubrics/%d"%(course_id, rubric_id), params="include[]=assessments&include[]=associations&style=full", headers = headers)
    data = rubric.json()



    # get associations of the rubric - this is a list of assignments and other objects the rubric is linked to

    associations = data["associations"]

    #find the rubric_association_id of the desired assignment - this will let us pull the correct assessments out of the rubric

    association_id = 0
    for association in associations:
        if association["association_id"] == assignment_id:
            association_id = association["id"]
            break

    #get all assessments made using this rubric
    all_assessments = data["assessments"]

    # store only assessments with the desired rubric_association_id, i.e. only assessments from the desired assignment
    assessments = []

    for a in all_assessments:
        if a["rubric_association_id"] == association_id:
            assessments.append(a)
    return assessments


def get_submissions(course_id, assignment_id, headers):
    # get all submissions to all desired assignments. We will use this to find reviewees in the for loop below
    submissions_data = []


    submissions = requests.get("https://canvas.harvard.edu/api/v1/courses/%d/assignments/%d/submissions?per_page=100"%(course_id, assignment_id), headers = headers)
    submissions_data.extend(submissions.json())

    while "next" in submissions.links:
            
        submissions = requests.get(submissions.links['next']['url'], headers = headers)
        submissions_data.extend(submissions.json())
    return submissions_data


def get_users(course_id, headers):
    # get json data for all users in course
    user_data = []
    course_users = requests.get("https://canvas.harvard.edu/api/v1/courses/%s/users?per_page=100"%course_id, headers = headers)

    user_data.extend(course_users.json())
    while "next" in course_users.links:
        course_users = requests.get(course_users.links['next']['url'], headers = headers)
        user_data.extend(course_users.json())

    #make a dictionary where keys are user id and value is user name
    user_dict = {}
    
    for user in user_data:
        user_dict[user['id']] = {'name':user['name'], 'SIS_ID':user['sis_user_id']}
    return user_dict

def get_criteria(course_id, rubric_id, headers):
    #returns a dict where keys are criteria id and values are criteria descriptions
    rubric = requests.get("https://canvas.harvard.edu/api/v1/courses/%d/rubrics/%d"%(course_id, rubric_id), params="include[]=assessments&include[]=associations&style=full", headers = headers)
    data = rubric.json()
    criteria = data['criteria']
    crit_dict = {}
    for crit in criteria:
        crit_dict[crit['id']] = crit['description']
    return crit_dict

user_dict = get_users(course_id, headers)
submissions_data = get_submissions(course_id, assignment_id, headers)
assessments = get_assessments(course_id, rubric_id, assignment_id, headers)
crit_dict = get_criteria(course_id, rubric_id, headers)

#this list will store dictionaries that contain information for each peer review
clean=[]

#get course information
course = requests.get("https://canvas.harvard.edu/api/v1/courses/%d/"%(course_id), headers = headers)
course = course.json()
course_name = course['name']

#get assignment information
assignment = requests.get("https://canvas.harvard.edu/api/v1/courses/%d/assignments/%d"%(course_id, assignment_id), headers = headers)
assignment = assignment.json()
assignment_name = assignment['name']

for a in assessments:

    #initalize a dictionary, which will hold all information for each assessment
    dict = {}


    dict['course_id'] = course_id
    dict['course_name'] = course_name
    dict['assignment_name'] = assignment_name

    # find username of reviewer
    if a['assessor_id'] in user_dict:
        reviewer_name = user_dict[a["assessor_id"]]['name']
        reviewer_sis = user_dict[a["assessor_id"]]['SIS_ID']

        
    else:
        reviewer_name = 'missing'
        reviewer_sis ='missing'


    dict["reviewer"] = reviewer_name
    dict['reviewer_sis'] = reviewer_sis
    dict['reviewer_id'] = a['assessor_id']
    


    # find reviewee's submission by matchin the id of the submission with the artifact_id of the rubric assessments
    submission_found = False
    for i in range(len(submissions_data)):
        if (submissions_data[i]["id"] == a["artifact_id"]):
            submission_found = True
            match_submission = submissions_data[i] 

            #find name of reviewee
            if match_submission["user_id"] in user_dict:
                reviewee_name = user_dict[match_submission["user_id"]]['name']
                reviewee_sis = user_dict[match_submission["user_id"]]['SIS_ID']
            else:
                reviewee_name = "missing"
                reviewee_sis = 'missing'
            dict["reviewee"] = reviewee_name
            dict['reviewee_sis'] = reviewee_sis
            dict['reviewee_id'] = match_submission["user_id"]
            dict['submission_timestamp'] = match_submission['submitted_at']
            dict['submission_attempt'] = match_submission['attempt']
            dict['submission_state'] = match_submission['workflow_state']
            break

    if submission_found == False:
        dict["reviewee"] = 'missing'
        dict['reviewee_sis'] = 'missing'
        dict['reviewee_id'] = 'missing'
        
        dict['submission_timestamp'] = 'missing'
        dict['submission_attempt'] = 'missing'
        dict['submission_state'] = 'missing'
    
    
    # for each criterium, get what the reviewer left for that reviewee in that criterium
    for d in a['data']:
        dict[crit_dict[d['criterion_id']]] = d['description']
    
    dict["score"] = a["score"]
    print("Reviewer: "+dict["reviewer"]+" Reviewee "+dict["reviewee"]+" Score "+str(dict["score"]))

    # add this dictionary to the cleaned up array of assessments
    clean.append(dict)

df = pd.DataFrame.from_dict(clean)  
df.to_excel(filepath) 
print("Done!")
