# given a rubric, fetches all peer review scores given to desired assignment using that rubric

# import modules

from pip._vendor import requests
import pandas as pd
from xlsxwriter import Workbook

#target filepath and name for output excel file
filepath = "your filename here" #YOUR FILEPATH AND NAME HERE
filepath = filepath + ".xlsx"

# put the course, rubric, and assignment ids here

rubric_id = 35235
course_id = 143616
assignment_id = 875141

# if your api key is in a text file, put the filepath here
#with open("/Users/georgeqiao/Desktop/ATG/PythonScripts/CanvasAPIKey.txt", 'r') as text:
    #key = text.read()

# headers with token
token = 'Bearer ' + key #paste api access token here, after the space after the word Bearer
headers = {'Authorization': token}



# API Call to get information from the rubric, including assessments made with that rubric and associations of that rubric with courses / assignments

rubric = requests.get("https://canvas.harvard.edu/api/v1/courses/%d/rubrics/%d"%(course_id, rubric_id), params="include[]=assessments&include[]=associations", headers = headers)
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



# get all submissions to all desired assignments. We will use this to find reviewees in the for loop below
submissions_data = []


submissions = requests.get("https://canvas.harvard.edu/api/v1/courses/%d/assignments/%d/submissions?per_page=100"%(course_id, assignment_id), headers = headers)
submissions_data.extend(submissions.json())

while "next" in submissions.links:
        
    submissions = requests.get(submissions.links['next']['url'], headers = headers)
    submissions_data.extend(submissions.json())



# store the name of the reviewer, the submission id of the work being reviewed, and the score given for each assessment in a list of dictionaries
clean=[]

# get user json data, then make dict where keys are user id and value is user name
user_data = []
course_users = requests.get("https://canvas.harvard.edu/api/v1/courses/%s/users?per_page=100"%course_id, headers = headers)
user_data.extend(course_users.json())
while "next" in course_users.links:
    course_users = requests.get(course_users.links['next']['url'], headers = headers)
    user_data.extend(course_users.json())

user_dict = {}
for user in user_data:
    user_dict[user['id']] = user['name']

for a in assessments:

    #initalize dictionary, which will hold reviewer name, reviewee name, and score for each assessment
    dict = {}

    # find username of reviewer
    if a['assessor_id'] in user_dict:
        reviewer_name = user_dict[a["assessor_id"]]
        
    else:
        reviewer_name = 'missing'

    dict["reviewer"] = reviewer_name

    # find reviewee's submission by matchin the id of the submission with the artifact_id of the rubric assessments

    for i in range(len(submissions_data)):
        if (submissions_data[i]["id"] == a["artifact_id"]):
            
            #find name of reviewee
            if submissions_data[i]["user_id"] in user_dict:
                reviewee_name = user_dict[submissions_data[i]["user_id"]]
            else:
                reviewee_name = "missing"
            dict["reviewee"] = reviewee_name
            break
    
    dict["score"] = a["score"]

    print("Reviewer: "+dict["reviewer"]+" Reviewee "+dict["reviewee"]+" Score "+str(dict["score"]))

    # add this dictionary to the cleaned up array of assessments
    clean.append(dict)

df = pd.DataFrame.from_dict(clean)  
df.to_excel(filepath) 
print("Done!")
