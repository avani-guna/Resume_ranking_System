import os
import spacy
from sklearn.feature_extraction.text import TfidfVectorizer , CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import csv
import re
import fitz
from sklearn.metrics import jaccard_score
from dateutil import parser
from datetime import datetime
from exp_of_resume import calculate_duration

nlp = spacy.load("en_core_web_lg")
# json_file_
skills = "jz_skill_patterns.jsonl"
#Adding pipe to pretrianed model
ruler = nlp.add_pipe("entity_ruler", before="ner")
# For skills extraction
ruler.from_disk(skills) 

nlp_s = spacy.load("en_core_web_sm")
# add custom NER model
# cu_nlp = spacy.load("/home/indianic/Desktop/sentimate/resume_ranking/ResumePaser/model/output/model-best")

# Step 1: Data Preprocessing using Spacy
def preprocess_resume(text):
    doc = nlp(text)
    clean_text = [token.lemma_.lower() for token in doc if not token.is_stop and not token.is_punct and not token.is_space]
    return ' '.join(clean_text)

# Step 2: Feature Extraction
def extract_features(resumes, job_description):
    vectorizer = TfidfVectorizer()
    count_vectorizer = CountVectorizer()
    # Vectorize job description
    job_desc_tfidf = vectorizer.fit_transform([preprocess_resume(job_description)])
    job_desc_count = count_vectorizer.fit_transform([preprocess_resume(job_description)])
    # Vectorize resumes
    cosine_similarities = []
    jaccard_similarities = []
    for resume in resumes:
        resume_tfidf = vectorizer.transform([preprocess_resume(resume)])
        resume_count = count_vectorizer.transform([preprocess_resume(resume)])
        cosine_similarities.append(cosine_similarity(job_desc_tfidf, resume_tfidf)[0][0])
        jaccard_similarities.append((jaccard_score(job_desc_count.toarray()[0], resume_count.toarray()[0],average='weighted')))

    # # optionl 
    # jaccard_similarities = []
    # job_desc_tokens = set(preprocess_resume(job_description).split())
    # for resume in resumes:
    #     resume_tokens = set(preprocess_resume(resume).split())
    #     jaccard_similarities.append((len(job_desc_tokens.intersection(resume_tokens)) / len(job_desc_tokens.union(resume_tokens)) * 10))

    # Compute combined score
    final_scores = []
    for i in range(len(resumes)):
        final_scores.append(0.8 * cosine_similarities[i] + 0.2 * jaccard_similarities[i])

    # print(cosine_similarities)
    # print("################################################################################################")
    # print(jaccard_similarities)
    return final_scores

## find Skill score is similar to job_description
def find_skill_score(resume_text,job_description):
    #job description data
    doc_job = nlp(preprocess_resume(job_description))
    skill_tokens = set([ent.text.lower() for ent in doc_job.ents if ent.label_ == 'SKILL'])

    # resume data
    skill_scores = []
    for text in resume_text:
        doc_resume = nlp(preprocess_resume(text))
        resume_skills = set([ent.text.lower() for ent in doc_resume.ents if ent.label_ == 'SKILL'])
        # print(resume_skills)
        score = sum([1 for skill in resume_skills if skill in skill_tokens])
        skill_scores.append(score)

    return skill_scores

# load resume file
def load_resume(resume_folder):
    resumes = []
    resume_names = []
    for filename in os.listdir(resume_folder):
        if filename.endswith('.pdf'):
            # Open the PDF file
            with open(os.path.join(resume_folder, filename), 'rb') as f:
                # Read the PDF file
                text= ""
                with fitz.open(f) as doc:
                    for page in doc:
                        text += str(page.get_text())
                        # print(text)
                resumes.append(" ".join(text.split("\n")))
                # print(text)
                # print("------------------------------------------------------------------------------------------")
        resume_names.append(filename)
    return resumes , resume_names

# save output data
def save_output_file(ranked_resumes , output_path):
    # Write all resume scores to CSV file
    with open(os.path.join(output_dir, "resume_scores.csv") , 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Resume' ,'Skill score', 'Similarity Score %'])
        for resume,skill_s , score in ranked_resumes:
            writer.writerow([resume, skill_s,score])

    # set threshold 
    with open(os.path.join(output_dir, "best_resumes.csv"), 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Resume' ,'Skill score', 'Similarity Score %'])
        for resume,skill_s , score in ranked_resumes:
            if skill_s >=2 or score >= 50 :
                writer.writerow([resume, skill_s,score])

# find year of experience for resume
# def extract_experience(resume_text):
#     patterns = [
#         r"(\d+)\s*(?:year[s]?)?\s*(?:of)?\s*(?:experience|exp)(?:\s*(?:in)?\s*([a-z\s]+))?",  # e.g., 5 years of experience in software development
#         r"(\d+)\s*(?:years?)-(?:\d+)\s*(?:of)?\s*(?:experience|exp)(?:\s*(?:in)?\s*([a-z\s]+))?",  # e.g., 3-5 years of experience in project management
#         r"(\d+)\s*\+\s*(?:year[s]?)?\s*(?:of)?\s*(?:experience|exp)(?:\s*(?:in)?\s*([a-z\s]+))?",  # e.g., 8+ years of experience in data analysis
#         r"(\w+)\s*(?:\d{4})\s*(?:to|–|-)\s*(\w+)\s*(?:\d{4})\s*(?:in)?\s*([a-z\s]+)?",  # e.g., Feb 2021 to Sep 2021, April 2022 – July 2022
#         r"(?:[a-z\s]*\b|\b)since\b(?:\s*\d{4})?(?:\s*(?:in)?\s*([a-z\s]+))?",  # e.g., since 2017, since January 2018 in software engineering
#         r"(\d{4})\s*-\s*(?:[a-z\s]*\b|\b)(?:present|current)(?:\s*(?:in)?\s*([a-z\s]+))?",  # e.g., 2018 - present, 2020 - current in data science
#         # r"(\d{4})\s*(?:to|–|-)\s*(\d{4})\s*(?:in)?\s*([a-z\s]+)?",  # e.g., 2017 to 2019 in project management

#     ]
#     doc = nlp_s(resume_text)
#     total_experience_years = 0
#     experience_dict = {}
#     for pattern in patterns:
#         matches = re.findall(pattern, resume_text, re.IGNORECASE)
        
#         for match in matches:
#             if len(match) == 2:  # Handles the first and third patterns
#                 years = int(match[0])
#                 total_experience_years += years
#                 domain = match[1].strip() if match[1] else "General"
                
#                 for sent in doc.sents:
#                     if match[0] in sent.text:
#                         domain = extract_domain(sent, domain)
                
#                 if domain in experience_dict:
#                     experience_dict[domain] += years
#                 else:
#                     experience_dict[domain] = years
#             elif len(match) == 3:  # Handles the second, fourth, and fifth patterns
#                 if match[1]:  # Handles date ranges
#                     start_date = parser.parse(match[0])
#                     end_date = parser.parse(match[1])
                    
#                     experience_days = (end_date - start_date).days
#                     years = round(experience_days / 365, 1)
#                 else:  # Handles present and since
#                     start_date = parser.parse(match[0])
#                     end_date = parser.parse("now")
                    
#                     experience_days = (end_date - start_date).days
#                     years = round(experience_days / 365, 1)
                
#                 total_experience_years += years
#                 domain = match[2].strip() if match[2] else "General"
                
#                 if domain in experience_dict:
#                     experience_dict[domain] += years
#                 else:
#                     experience_dict[domain] = years
    
#     experience_dict["Total"] = total_experience_years
#     return experience_dict


def extract_experience(resume_text):
    patterns = [
        r"(\d+)\s*(?:year[s]?)?\s*(?:of)?\s*(?:experience|exp)(?:\s*(?:in)?\s*([a-z\s]+))?",  # e.g., 5 years of experience in software development
        r"(\d+)\s*(?:years?)-(?:\d+)\s*(?:of)?\s*(?:experience|exp)(?:\s*(?:in)?\s*([a-z\s]+))?",  # e.g., 3-5 years of experience in project management
        r"(\d+)\s*\+\s*(?:year[s]?)?\s*(?:of)?\s*(?:experience|exp)(?:\s*(?:in)?\s*([a-z\s]+))?",  # e.g., 8+ years of experience in data analysis
        r"(\w+)\s*(?:\d{4})\s*(?:to|–|-)\s*(\w+)\s*(?:\d{4})\s*(?:in)?\s*([a-z\s]+)?",  # e.g., Feb 2021 to Sep 2021, April 2022 – July 2022
        r"(?:[a-z\s]*\b|\b)since\b(?:\s*\d{4})?(?:\s*(?:in)?\s*([a-z\s]+))?",  # e.g., since 2017, since January 2018 in software engineering
        r"(\d{4})\s*-\s*(?:[a-z\s]*\b|\b)(?:present|current)(?:\s*(?:in)?\s*([a-z\s]+))?",  # e.g., 2018 - present, 2020 - current in data science
        r"(\w{3}\s\d{4})\s*(?:–|-)\s*(\w{3}\s\d{4})\s*(?:in)?\s*([a-z\s]+)"  # e.g., NOV 2022 – JAN 2023 in domain
    ]

    total_experience_months = 0
    experience_dict = {}
    for pattern in patterns:
        matches = re.findall(pattern, resume_text, re.IGNORECASE)

        for match in matches:
            print(match)
            if len(match) == 2:  # Handles the first and third patterns
                years = int(match[0])
                total_experience_months += years * 12
                domain = match[1].strip() if match[1] else "General"
                if domain in experience_dict:
                    experience_dict[domain] += years
                else:
                    experience_dict[domain] = years
            elif len(match) == 3:  # Handles the second, fourth, fifth, sixth, and seventh patterns
                if match[1]:  # Handles date ranges
                    start_date = parser.parse(match[0])
                    end_date = parser.parse(match[1])
                    experience_months = (end_date.year - start_date.year) * 12 + (end_date.month - start_date.month)
                    total_experience_months += experience_months
                else:  # Handles present and since
                    if match[0].lower() == "since":
                        start_date = parser.parse("January " + match[1])
                        end_date = parser.parse("now")
                        experience_months = (end_date.year - start_date.year) * 12 + (end_date.month - start_date.month)
                        total_experience_months += experience_months
                    elif match[0].lower() == "current" or match[0].lower() == "present":
                        start_date = parser.parse(match[1])
                        end_date = parser.parse("now")
                        experience_months = (end_date.year - start_date.year) * 12 + (end_date.month - start_date.month)
                        total_experience_months += experience_months

                domain = match[2].strip() if match[2] else "General"
                if domain in experience_dict:
                    experience_dict[domain] += experience_months / 12
                else:
                    experience_dict[domain] = experience_months / 12
         


    total_experience_years = total_experience_months / 12
    total_experience_years = round(total_experience_years, 1)
    total_experience_months = round(total_experience_months, 1)

    experience_dict["Total (Years)"] = total_experience_years
    experience_dict["Total (Months)"] = total_experience_months
    return experience_dict

def extract_domain(sentence, default_domain):
    domain_keywords = ["in", "with", "of", "at", "on"]

    for token in sentence:
        if token.text.lower() in domain_keywords:
            domain = token.nbor().text.strip()
            return domain

    return default_domain


# Find best matching resume
def find_best_resume(resume_data, job_description):
    # Read in resumes
  
    resumes , resume_names = resume_data # this is function 
    # Extract features
    similarity_scores = extract_features(resumes, job_description)

    skill_scores = find_skill_score(resumes,job_description)
    # print(skill_scores)
    
    total_skill = sum(skill_scores)
    for i in range(len(skill_scores)):
        skill_scores[i] = (skill_scores[i] / total_skill) * 100
    # print(skill_scores)    
    
    # don't uncomments this
    total_exp = []
    exp_yer = []
    for data in resumes:
        number_of_days = calculate_duration(data)
        years = number_of_days // 365
        months = (number_of_days - years *365) // 30
        exp = f"{years} year {months} months"
        exp_yer.append(exp)
        total_exp.append(number_of_days)
    # print(total_exp)
    
    # conert to per %
    similarity_scores = [round(i*100,1)for i in similarity_scores]
    # print(similarity_scores)
    # final score for skill and similarity score
    final_score = []
    for i in range(len(resumes)):
        final_score.append(0.6 * skill_scores[i] + 0.5 * similarity_scores[i])
    
    # ranked_resumes = sorted(list(zip(resume_names,skill_scores, similarity_scores)), key=lambda x: (x[2], x[1]), reverse=True)
    ranked_resumes = sorted(list(zip(resume_names,final_score,exp_yer)), key=lambda x: (x[1]), reverse=True)
    # print(ranked_resumes)
    # save data csv file
    # save_output_file(ranked_resumes,output_path)

    # Return best matching resume
    # best_resume = ranked_resumes[0]
    return ranked_resumes


if __name__ == "__main__":
    
    resume_folder = '/home/indianic/Desktop/sentimate/resume_ranking/AI_ML_CVs'
    # read job description
    with open("job_description.txt","r") as f:
        data = f.read()
        job_description = re.sub(r'\s+', ' ', data).strip()
    # Create a directory to store the output files
    output_dir = 'resume_scores'
    if not os.path.exists(output_dir):
        os.mkdir(output_dir)
        
    best_resume = find_best_resume(load_resume(resume_folder), job_description)
    # print('Best matching resume:', best_resume[0][0])
    # print('Skill score:', best_resume[0][1])
    # print('Similarity score:', best_resume[0][2])
    # for i,score in enumerate(best_resume[1:]):
    #     print(f'resume name: {best_resume[i][0]} --------- score : {best_resume[i][2]}, ---- Rank :  {i+2}')
    for i,score in enumerate(best_resume):
        print(f'resume name: {best_resume[i][0]} ------------- Rank :  {i+1}')
    
