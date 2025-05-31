from loader import  extract_text, extract_jd_text
# from data.preprocess import clean_text
import requests

#input json:{"target_job_desc": "", "cv":""}
def llm_response(input_json):
    response = requests.post("http://localhost:8000/score/invoke", json={"input": input_json})
    return response.json()["output"]

input_json = {
    "target_job_desc": "we are looking for hire experts flutter developer. so you are eligible this post then apply your resume. job types: full-time, part-time salary: 20,000.00 - 40,000.00 per month benefits: flexible schedule food allowance schedule: day shift supplemental pay: joining bonus overtime pay experience: total work: 1 year (preferred) housing rent subsidy: yes industry: software development work remotely: temporarily due to covid-19",
    "cv": " : as a recent graduate in computer science with 6-months of experience in flutter, i am excited to apply for the position of flutter developer at your company. though i have not worked with android studio, i am willing to learn and adapt as per the requirement. i have experience in handling user-friendly ui based on requirements in a flutter and knowledge of firebase. i am comfortable working with cross-platform frameworks. while i have not worked with location services and video recording, i am eager to learn and implement them. i am a strong team player with a commitment to perfection and am ready to face new challenges."    
}

print(llm_response(input_json))