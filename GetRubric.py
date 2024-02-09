# given a rubric, fetches all peer review scores given to desired assignments using that rubric

# import modules
import json
from pip._vendor import requests
import pandas as pd
from xlsxwriter import Workbook

# put the course, rubric, and assignment ids here

rubric_id = #ENTER RUBRIC ID HERE
course_id = #ENTER COURSE ID HERE
assignment_ids = #ENTER ASSIGNMENT IDS AS A PYTHON LIST HERE

# headers with token

token = #ENTER API TOKEN HERE
headers = {'Authorization': token}


# API Call to get information from the rubric, including assessments made with that rubric

rubric = requests.get("https://canvas.harvard.edu/api/v1/courses/%d/rubrics/%d"%(course_id, rubric_id), params="include[]=assessments", headers = headers)
data = rubric.json()

# store all assessments made with the rubric
assessments = data["assessments"]

# initialize cleaner array of assessments
clean = []

# get all submissions to all desired assignments. We will use this to find reviewees in the for loop below
submissions_data = []
for id in assignment_ids:

    submissions = requests.get("https://canvas.harvard.edu/api/v1/courses/%d/assignments/%d/submissions?per_page=100"%(course_id, id), headers = headers)
    submissions_data.extend(submissions.json())
    
    while "next" in submissions.links:
            
        submissions = requests.get(submissions.links['next']['url'], headers = headers)
        submissions_data.extend(submissions.json())


# store the name of the reviewer, the submission id of the work being reviewed, and the score given for each assessment
for a in assessments:

    #initalize dictionary, which will hold reviewer name, reviewee name, and score for each assessment
    dict = {}

    # find username of reviewer
    user = requests.get("https://canvas.harvard.edu/api/v1/users/%s" %a["assessor_id"], headers = headers)
    data = user.json()
    dict["reviewer"] = data["name"]

    # find reviewee's submission
    found_reviewee = False
    for i in range(len(submissions_data)):
        if (submissions_data[i]["id"] == a["artifact_id"]):

            #find name of reviewee
            reviewee = requests.get("https://canvas.harvard.edu/api/v1/users/%s" %submissions_data[i]["user_id"], headers=headers)
            r_data = reviewee.json()
            dict["reviewee"] = r_data["name"]
            found_reviewee = True
            break

    # if not found store reviewee name as missing
    
    if not(found_reviewee):
        dict["reviewee"] = "missing"
    
    dict["score"] = a["score"]

    print("Reviewer: "+dict["reviewer"]+" Reviewee "+dict["reviewee"]+" Score "+str(dict["score"]))

    # add this dictionary to the cleaned up array of assessments
    clean.append(dict)

df = pd.DataFrame.from_dict(clean)  
df.to_excel('PeerReviewScores.xlsx') 
print("Done!")