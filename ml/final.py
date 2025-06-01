from loader import  extract_text
from data.preprocess import clean_text
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords
import requests
import re

#input json:{"target_job_desc": "", "cv":""}
def gemma_response(input_json):
    response = requests.post("http://localhost:8000/score/gemma/invoke", json={"input": input_json})
    return response.json()["output"]

def mistral_response(input_json):
    response = requests.post("http://localhost:8000/score/mistral/invoke", json={"input": input_json})
    return response.json()["output"]

docs = extract_text("data/yavancv.pdf") #this is a list of documents
cv = clean_text(docs[0].page_content)

print(cv, "\n\n\n")

input_json = {
    "target_job_desc": 'data scientist (contractor) bangalore, in responsibilities we are looking for a capable data scientist to join the analytics team, reporting locally in india bangalore. this persons responsibilities include research, design and development of machine learning and deep learning algorithms to tackle a variety of fraud oriented challenges. the data scientist will work closely with software engineers and program managers to deliver end-to-end products, including: data collection in big scale and analysis, exploring different algorithmic approaches, model development, assessment and validation all the way through production. qualifications at least 3 years of hands-on development of complex machine learning models using modern frameworks and tools, ideally python based. solid understanding of statistics and applied mathematics creative thinker with a proven ability to tackle open problems and apply non-trivial solutions. experience in software development using python, java or a similar language. any graduate or m.sc. in computer science, mathematics or equivalent, preferably in machine learning ability to write clean and concise code quick learner, independent, methodical, and detail oriented. team player, positive attitude, collaborative, good communication skills. dedicated, makes things happen. flexible, capable of making decisions in an ambiguous and changing environment. advantages: prior experience as a software developer or data engineer advantage experience with big data advantage experience with spark big advantage experience with deep learning frameworks (pytorch, tensorflow, keras) advantage. experience in the telecommunication domain and/or fraud prevention - advantage',
    "cv": cv
}

print(mistral_response(input_json))