import spacy
import os
import csv
import fitz
from spacy.lang.en.stop_words import STOP_WORDS
import re
from dateutil import parser

# Load the spaCy NLP model
nlp = spacy.load("en_core_web_lg")

# Example job description
# job_description = "We are looking for a software engineer with experience in Python and Java.and also work in machine learing."
with open("job_description.txt","r") as f:
    data = f.read()
    job_description = re.sub(r'\s+', ' ', data).strip()
    
# skill
skills = ['Python','java','machine learing','nlp','c','pandas','numpy','ai']

# Preprocess the job description and skills
job_description_tokens = [token.text.lower() for token in nlp(job_description) if not token.is_stop and not token.is_punct]
skill_tokens = [skill.lower() for skill in skills]

# json_file_
skills = "jz_skill_patterns.jsonl"

#Adding pipe to pretrianed model
ruler = nlp.add_pipe("entity_ruler", before="ner")

# For skills extraction
ruler.from_disk(skills)

# Create a directory to store the output files
output_dir = 'resume_scores12'
if not os.path.exists(output_dir):
    os.mkdir(output_dir)

# Initialize a list to store the output data
output_data = []

folder_path = "/home/indianic/Desktop/sentimate/resume_ranking/AI_ML_CVs"


## Function sections

def find_links(resume_text):
    # Regular expression pattern to match URLs
    url_pattern = re.compile(r'https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+')

    # Find all URLs in the resume text
    urls = re.findall(url_pattern, resume_text)
    return list(urls)

# def calculate_experience_score(resume_text):
#     # Define regular expressions to match common work experience phrases
#     regexes = [
#         r'(\d+)\s*(years?|yrs?)\s*(of)?\s*experience',
#         r'experience\s*of\s*(\d+)\s*(years?|yrs?)',
#         r'(\d+)\s*(years?|yrs?)\s*(\d+)?\s*(months?|mos?)\s*(of)?\s*experience'
#     ]
    
#     # Apply regular expressions to the resume text
#     experience_phrases = []
#     for regex in regexes:
#         matches = re.findall(regex, resume_text, re.IGNORECASE)
#         if matches:
#             experience_phrases.extend(matches)
    
#     # Calculate total years of experience
#     total_years = 0
#     for phrase in experience_phrases:
#         years, months = 0, 0
#         if len(phrase) == 2:
#             years = int(phrase[0])
#         elif len(phrase) == 4:
#             years = int(phrase[0])
#             months = int(phrase[2])
#         total_years += years + (months / 12)
    
#     # Apply Spacy to extract job titles and check for seniority keywords
#     doc = nlp(resume_text)
#     seniority_keywords = ['senior', 'lead', 'manager', 'director', 'vp', 'president']
#     job_titles = []
#     for ent in doc.ents:
#         if ent.label_ == 'JOB_TITLE':
#             job_titles.append(ent.text.lower())
    
#     # Calculate seniority score based on job titles
#     seniority_score = 0
#     for job_title in job_titles:
#         for keyword in seniority_keywords:
#             if keyword in job_title:
#                 seniority_score += 1
    
#     # Calculate final work experience score
#     experience_score = (total_years * 10) + (seniority_score * 5)
#     return experience_score

def extract_experience_advanced(resume_text):
    doc = nlp(resume_text)
    
    patterns = [
        r"(\d+)\s*(?:year[s]?)?\s*(?:of)?\s*(?:experience|exp)(?:\s*(?:in)?\s*([a-z\s]+))?",  # e.g., 5 years of experience in software development
        r"(\d+)\s*(?:years?)-(?:\d+)\s*(?:of)?\s*(?:experience|exp)(?:\s*(?:in)?\s*([a-z\s]+))?",  # e.g., 3-5 years of experience in project management
        r"(\d+)\s*\+\s*(?:year[s]?)?\s*(?:of)?\s*(?:experience|exp)(?:\s*(?:in)?\s*([a-z\s]+))?",  # e.g., 8+ years of experience in data analysis
        r"(\w+)\s*(?:\d{4})\s*(?:to|–|-)\s*(\w+)\s*(?:\d{4})\s*(?:in)?\s*([a-z\s]+)?",  # e.g., Feb 2021 to Sep 2021, April 2022 – July 2022
        r"(?:[a-z\s]*\b|\b)since\b(?:\s*\d{4})?(?:\s*(?:in)?\s*([a-z\s]+))?",  # e.g., since 2017, since January 2018 in software engineering
        r"(\d{4})\s*-\s*(?:[a-z\s]*\b|\b)(?:present|current)(?:\s*(?:in)?\s*([a-z\s]+))?",  # e.g., 2018 - present, 2020 - current in data science
        r"(\d{4})\s*(?:to|–|-)\s*(\d{4})\s*(?:in)?\s*([a-z\s]+)?",  # e.g., 2017 to 2019 in project management

    ]
    
    total_experience_years = 0
    experience_dict = {}
    for pattern in patterns:
        matches = re.findall(pattern, resume_text, re.IGNORECASE)
        
        for match in matches:
            if len(match) == 2:  # Handles the first and third patterns
                years = int(match[0])
                total_experience_years += years
                domain = match[1].strip() if match[1] else "General"
                
                for sent in doc.sents:
                    if match[0] in sent.text:
                        domain = extract_domain(sent, domain)
                
                if domain in experience_dict:
                    experience_dict[domain] += years
                else:
                    experience_dict[domain] = years
            elif len(match) == 3:  # Handles the second, fourth, and fifth patterns
                if match[1]:  # Handles date ranges
                    start_date = parser.parse(match[0])
                    end_date = parser.parse(match[1])
                    
                    experience_days = (end_date - start_date).days
                    years = round(experience_days / 365, 1)
                else:  # Handles present and since
                    start_date = parser.parse(match[0])
                    end_date = parser.parse("now")
                    
                    experience_days = (end_date - start_date).days
                    years = round(experience_days / 365, 1)
                
                total_experience_years += years
                domain = match[2].strip() if match[2] else "General"
                
                if domain in experience_dict:
                    experience_dict[domain] += years
                else:
                    experience_dict[domain] = years
    
    experience_dict["Total"] = total_experience_years
    return experience_dict

def extract_domain(sentence, default_domain):
    domain_keywords = ["in", "with", "of", "at", "on"]

    for token in sentence:
        if token.text.lower() in domain_keywords:
            domain = token.nbor().text.strip()
            return domain

    return default_domain



# Loop through each PDF file in the folder
for filename in os.listdir(folder_path):
    if filename.endswith('.pdf'):
        # Open the PDF file
        with open(os.path.join(folder_path, filename), 'rb') as f:
            # Read the PDF file
            text= ""
            with fitz.open(f) as doc:
                for page in doc:
                    text += str(page.get_text())
                    # print(text)
            resume_text = " ".join(text.split("\n"))

            # Process the resume using the spaCy NLP model
            doc_resume = nlp(resume_text)

            # Extract named entities, skills, and work experience from the resume
            resume_entities = [ent.text.lower() for ent in doc_resume.ents if ent.label_ in ['PERSON', 'ORG', 'GPE']]
            # print(resume_entities)
            resume_skills = set([ent.text.lower() for ent in doc_resume.ents if ent.label_ == 'SKILL'])
            # print(resume_skills)
            work_experience = [chunk.text.lower() for chunk in doc_resume.noun_chunks if 'work' in chunk.text.lower() and 'experience' in chunk.text.lower()]
            # print(work_experience)

            # Calculate a score for the resume based on the number of matching named entities, skills, and work experience
            entity_score = sum([2 for ent in doc_resume.ents if ent.label_ in ['PERSON', 'ORG', 'GPE'] and ent.text.lower() in job_description_tokens])
            skill_score = sum([1 for skill in resume_skills if skill in skill_tokens])
            # work_experience_score = 1 if not work_experience else 2
            work_experience_score = extract_experience_advanced(resume_text)
            resume_score = entity_score + skill_score + work_experience_score['Total']

            # Add the output data to the list
            output_data.append([filename, entity_score, skill_score, work_experience_score, resume_score])


# Sort the output data by the resume score in descending order
output_data_sorted = sorted(output_data, key=lambda x: x[4], reverse=True)


# Save the top 10 resume scores to a CSV file
output_file = os.path.join(output_dir, "resume_scores.csv")
with open(output_file, 'w', newline='') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(['Filename', 'Entity Score', 'Skill Score', 'Work Experience Score', 'Total Score'])
    for row in output_data_sorted[:10]:
        writer.writerow(row)




